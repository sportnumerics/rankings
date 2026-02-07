from typing import Any

from .tables import parse_table
from ..shared.types import Game, GameResult, GameStatLine, PlayerSummary, ScheduleGame, ScheduleGameResult, Scraper, Location, Team, TeamDetail, TeamSummary
from urllib.parse import urlparse, parse_qsl
from collections.abc import Iterator
from bs4 import BeautifulSoup
import datetime
import re

SPORT_MAP = {'MLA': 'ml', 'WLA': 'wl'}


class Ncaa(Scraper):
    base_url = 'https://stats.ncaa.org'

    def __init__(self, sports=['MLA', 'WLA'], divs=['1', '2', '3']):
        self.sports = sports
        self.divs = divs

    def get_team_list_urls(self, year: str) -> Iterator[Location]:
        for sport in self.sports:
            for div in self.divs:
                yield Location(
                    url=
                    f'{self.base_url}/team/inst_team_list?academic_year={year}&division={div}&sport_code={sport}'
                )

    def convert_team_list_html(self, html: str, year: str,
                               location: Location) -> Iterator[Team]:
        soup = BeautifulSoup(html, 'html.parser')
        team_links = soup.table.find_all('a')
        params = {k: v for (k, v) in parse_qsl(urlparse(location.url).query)}
        sport = SPORT_MAP[params['sport_code']]
        for link in team_links:
            link_parts = link['href'].split('/')
            name = link.string
            yield Team(name=name,
                       schedule=Location(
                           url=f'{self.base_url}/teams/{link_parts[2]}'),
                       id=f'{sport}-ncaa-{self._generate_slug(name)}',
                       div=sport + params['division'],
                       sport=sport,
                       year=params['academic_year'],
                       source='ncaa')

    OPPONENT_NAME_REGEX = re.compile(
        r'(?P<opponent_rank>#\d+)?\s*(?P<opponent_name>.+)')
    OPPONENT_COL_REGEX = re.compile(
        r'(?P<away>\@)?\s*(?P<opponent_name>[^\@]+)(\@(?P<neutral_site>.*))?')
    OPPONENT_ID_REGEX = re.compile(r'/team/(?P<id>\d+)/(?P<yearcode>\d+)')
    OPPONENT_ALT_ID_REGEX = re.compile(r'/teams/(?P<alt_id>\d+)')
    SCORE_REGEX = re.compile(
        r'(?P<outcome>[WL])?\s*(?P<points_for>\d+)\s*\-\s*(?P<points_against>\d+)'
    )
    DETAILS_URL_REGEX = re.compile(r'/contests/(?P<id>\d+)/box_score')

    def convert_schedule_html(self, html: str,
                              team: Team) -> Iterator[ScheduleGame]:
        soup = BeautifulSoup(html, 'html.parser')
        year_list = soup.find(id='year_list')
        if year_list:
            selected = year_list.find('option', attrs={'selected': 'selected'})
            if selected and selected.attrs.get('value'):
                team.alt_id = selected.attrs['value']
        schedule_header = soup.find('div',
                                    class_='card-header',
                                    string='Schedule/Results')
        if not schedule_header or not schedule_header.parent:
            return []
        schedule_div = schedule_header.parent
        if not schedule_div.table or not schedule_div.table.tbody:
            return []
        rows = schedule_div.table.tbody.find_all('tr')
        games = []
        for row in rows:
            cols = list(row.find_all('td'))
            if len(cols) < 4:
                continue
            date_col = cols[0]
            opp_col = cols[1]
            result_col = cols[2]

            date = self._to_iso_format(date_col.string)

            opp_link = opp_col.find('a')
            if not opp_link:
                continue
            name_string = ' '.join(opp_link.stripped_strings)
            name_match = self.OPPONENT_NAME_REGEX.match(name_string)
            opp_string = ' '.join(opp_col.stripped_strings)
            opp_match = self.OPPONENT_COL_REGEX.match(opp_string)
            if not name_match or not opp_match:
                continue

            opponent_name = name_match.group('opponent_name').strip()
            opponent = TeamSummary(name=opponent_name)
            home = opp_match.group('away') is None

            opponent.id = self._opponent_id(team.sport, team.source,
                                            opponent_name)

            result_str = ' '.join(result_col.stripped_strings)
            score_match = self.SCORE_REGEX.match(result_str)
            if score_match:
                result = ScheduleGameResult(
                    points_for=int(score_match.group('points_for')),
                    points_against=int(score_match.group('points_against')))
            else:
                result = None
            details = None
            id = None
            if hasattr(result_col, 'a') and hasattr(result_col.a, 'href'):
                game_details_url = result_col.a['href']
                url_match = self.DETAILS_URL_REGEX.match(game_details_url)
                if url_match:
                    details = Location(url=self.base_url +
                                       game_details_url.replace(
                                           'box_score', 'individual_stats'))
                    id = 'ml-ncaa-' + url_match.group('id')

            games.append(
                ScheduleGame(id=id,
                             date=date,
                             opponent=opponent,
                             sport=team.sport,
                             source=team.source,
                             result=result,
                             home=home,
                             details=details))
        return games

    TEAM_HREF_REGEX = re.compile(r'/teams/(?P<id>\d+)')
    TEAM_NAME_REGEX = re.compile(
        r'(#\d+ )?(?P<name>[a-zA-Z0-9\-_&\' .()]+) \(\d+-\d+\)')

    def cross_link_schedules(self, schedules: list[TeamDetail]):
        ids_by_alt_ids = {
            schedule.team.alt_id: schedule.team.id
            for schedule in schedules
        }
        for schedule in schedules:
            if not schedule.games:
                continue
            for game in schedule.games:
                if not game.opponent.id and game.opponent.alt_id in ids_by_alt_ids:
                    game.opponent.id = ids_by_alt_ids[game.opponent.alt_id]

    def convert_game_details_html(self, html: str, location: Location,
                                  game_id: str, sport: str, source: str,
                                  home_team: Team, away_team: Team) -> Game:
        soup = BeautifulSoup(html, 'html.parser')
        header = soup.find('div', class_='table-responsive')
        header_table_rows = list(header.table.table.find_all('tr'))
        date_row = header_table_rows[3]
        if not date_row:
            return None
        date = self._to_iso_format(next(date_row.stripped_strings))

        def is_team_href(tag):
            if tag.name != 'a' or tag.get('href') is None:
                return False
            m = self.TEAM_HREF_REGEX.match(tag['href'])
            if m:
                return tag.find('img') is None
            return False

        team_links = soup.find_all(is_team_href)

        def is_number(str):
            return str.strip().isnumeric()

        def get_total_score(link):
            link_cell = link.find_parent('td')
            score_cell = link_cell.find_next_sibling('td', string=is_number)
            return int(score_cell.string)

        stats_tables = list(soup.find_all('table', class_='dataTable'))

        away_score = get_total_score(team_links[0])
        home_score = get_total_score(team_links[1])
        result = GameResult(
            home_score=home_score,
            away_score=away_score) if home_score and away_score else None

        return Game(id=game_id,
                    date=date,
                    external_link=location.url,
                    home_team=home_team,
                    away_team=away_team,
                    result=result,
                    away_stats=parse_table(
                        stats_tables[0],
                        lambda col_name, cell: self._map_statistic(
                            sport, source, col_name, cell),
                        lambda **args: GameStatLine(**args)
                        if 'player' in args else None),
                    home_stats=parse_table(
                        stats_tables[1],
                        lambda col_name, cell: self._map_statistic(
                            sport, source, col_name, cell),
                        lambda **args: GameStatLine(**args)
                        if 'player' in args else None))

    def get_limiter_session_args(self):
        return {'per_minute': 30}

    def convert_roster(self, html, team):
        return None

    PLAYER_HREF_REGEX = re.compile(r'/players/(?P<player_id>\d+)')

    def _map_statistic(self, sport, source, key, tag) -> tuple[str, Any]:
        text = tag.get_text(strip=True)

        def get_num(t):
            return int(t.replace('/', '') if t else 0)

        try:
            match key:
                case '#':
                    return {'number': get_num(text)}
                case 'Name':
                    a = tag.find('a')
                    if not a:
                        return None
                    href = a['href']
                    href_match = self.PLAYER_HREF_REGEX.match(href)
                    if not href_match:
                        raise Exception(f'no match {href}')
                    return {
                        'player':
                        PlayerSummary(name=text,
                                      id=sport + '-' + source + '-' +
                                      href_match.group('player_id'),
                                      external_link=self.base_url + href)
                    }
                case 'P':
                    return {'position': text} if text else None
                case 'Goals':
                    return {'g': get_num(text)}
                case 'Assists':
                    return {'a': get_num(text)}
                case 'GB':
                    return {'gb': get_num(text)}
                case _:
                    return None
        except Exception as ex:
            raise Exception(f'error mapping statistic {tag}: {ex}')

    def _to_iso_format(self, date):
        return datetime.datetime.strptime(date, '%m/%d/%Y').date().isoformat()

    def _foreign_opponent_id(self, sport, source, name):
        return f'{sport}-{source}-nd-' + self._generate_slug(name)

    def _opponent_id(self, sport, source, name):
        return f'{sport}-{source}-{self._generate_slug(name)}'

    def _generate_slug(self, name):
        return re.sub(r'[^a-z-]', '', name.lower().replace(' ', '-'))
