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
            yield Team(
                name=link.string,
                schedule=Location(
                    url=
                    f'{self.base_url}/player/game_by_game?game_sport_year_ctl_id={link_parts[3]}&org_id={link_parts[2]}&stats_player_seq=-100'
                ),
                id=f'{sport}-ncaa-{link_parts[2]}',
                div=sport + params['division'],
                sport=sport,
                year=params['academic_year'],
                source='ncaa')

    OPPONENT_NAME_REGEX = re.compile(
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
        alt_id = soup.find(id='year_list').find('option',
                                                attrs={
                                                    'selected': 'selected'
                                                }).attrs['value']
        if alt_id:
            team.alt_id = alt_id
        game_breakdown_div = soup.find(id='game_breakdown_div')
        rows = game_breakdown_div.table.table.find_all(
            'tr') if game_breakdown_div else []
        games = []
        for row in rows:
            if 'class' in row.attrs or 'style' in row.attrs:
                continue
            cols = list(row.find_all('td'))
            date_col = cols[0]
            opp_col = cols[1]
            result_col = cols[2]

            date = self._to_iso_format(date_col.string)

            opp_link = opp_col.find(
                lambda tag: tag.name == 'a' and not tag.has_attr('class'))
            opp_string = ' '.join(opp_col.stripped_strings)
            opp_match = self.OPPONENT_NAME_REGEX.match(opp_string)
            if not opp_match:
                continue

            opponent = TeamSummary(
                name=opp_match.group('opponent_name').strip())
            home = opp_match.group('away') is None

            if opp_link:
                id_match = self.OPPONENT_ID_REGEX.match(opp_link['href'])
                if id_match:
                    opponent.id = '-'.join(
                        [team.sport, team.source,
                         id_match.group('id')])
                alt_id_match = self.OPPONENT_ALT_ID_REGEX.match(
                    opp_link['href'])
                if alt_id_match:
                    opponent.alt_id = alt_id_match.group('alt_id')
            else:
                opponent.id = self._foreign_opponent_id(
                    team.sport, team.source, opponent.name)

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
                    details = Location(url=self.base_url + game_details_url)
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
        game_date = soup.find('td', string='Game Date:')
        if not game_date:
            return None
        date = self._to_iso_format(
            next(game_date.find_next_sibling('td').stripped_strings))

        def is_team_href(href):
            m = self.TEAM_HREF_REGEX.match(href)
            return m

        team_links = soup.find_all('a', href=is_team_href)

        def get_total_score(link):
            row = link.find_parent('tr')
            cells = row.find_all('td')
            return int(cells[-1].get_text(strip=True))

        stats_tables = list(
            map(lambda t: t.find_parent('table'),
                soup.find_all('th', string='Player')))

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

    PLAYER_HREF_REGEX = re.compile(
        r'/player/index\?game_sport_year_ctl_id=(?P<gsycid>\d+)&(amp;)?org_id=(?P<org_id>\d+)&(amp;)?stats_player_seq=(?P<spseq>\d+)'
    )

    def _map_statistic(self, sport, source, key, tag) -> tuple[str, Any]:
        text = tag.get_text(strip=True)

        def get_num(t):
            return int(t.replace('/', '') if t else 0)

        try:
            match key:
                case 'Player':
                    a = tag.find('a')
                    if not a:
                        return None
                    href = a['href']
                    href_match = self.PLAYER_HREF_REGEX.match(href)
                    if not href_match:
                        raise Exception(f'no match {href}')
                    last, first = text.rsplit(', ', 1)
                    return {'player':
                            PlayerSummary(name=f'{first} {last}',
                                          id=sport + '-' + source + '-' +
                                          href_match.group('spseq'),
                                          external_link=self.base_url +
                                          href.replace('&amp;', '&'))}
                case 'Pos':
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
        return f'{sport}-{source}-nd-' + re.sub(r'[^a-z-]', '',
                                                name.lower().replace(' ', '-'))
