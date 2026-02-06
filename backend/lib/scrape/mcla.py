from collections.abc import Iterator
import datetime
import re
from typing import Any, Generator
from bs4 import BeautifulSoup
import dateutil
import dateutil.parser as parser
from .tables import parse_table
from ..shared.types import FaceOffResults, Team, Location, ScheduleGame, TeamSummary, Game, ScheduleGameResult, GameResult, GameStatLine, Roster, RosterPlayer, Coach, Conference, PlayerSummary

TIMEZONES = {
    'PDT': -7 * 3600,
    'PST': -8 * 3600,
    'MDT': -6 * 3600,
    'MST': -7 * 3600,
    'CDT': -5 * 3600,
    'CST': -6 * 3600,
    'EDT': -4 * 3600,
    'EST': -5 * 3600
}

DIVISION_MAP = {
    'Division I': '1',
    'Division 1': '1',
    'Division II': '2',
    'Division 2': '2',
    'Division III': '3',
    'Division 3': '3',
    'Independent': '2'  # todo: handle independent teams correctly
}


class Mcla():

    def get_team_list_urls(self, year: str) -> Generator[Location, Any, Any]:
        yield Location(
            url=
            f'https://mcla.us/teams?current_season_year={year}&view_by=division'
        )

    def convert_team_list_html(self, html: str, year: str,
                               location: Location) -> Iterator[Team]:
        soup = BeautifulSoup(html, 'html.parser')
        
        box_titles = soup.find_all('h4', class_='box__title')
        for title in box_titles:
            # Extract division text (e.g., "Division 1")
            division_text = title.get_text(strip=True)
            
            # Find the table following this title
            table_wrapper = title.find_next('div', class_='table__wrapper--embedded')
            if not table_wrapper:
                continue
                
            table = table_wrapper.find('table')
            if not table or not table.tbody:
                continue
            
            for row in table.tbody.find_all('tr'):
                links = row.find_all('a')
                if len(links) < 2:
                    continue
                team = links[0]
                conf = links[1]
                
                if conf.string == 'NON-MCLA':
                    continue
                
                link_parts = team['href'].split('/')
                slug = link_parts[2]
                yield Team(
                    name=next(team.stripped_strings),
                    schedule=Location(
                        url=f'https://mcla.us/teams/{slug}/{year}/schedule'),
                    roster=Location(
                        url=f'https://mcla.us/teams/{slug}/{year}/roster'),
                    year=year,
                    id=f'ml-mcla-{self._normalize_slug(slug)}',
                    div='mcla' + DIVISION_MAP[division_text],
                    sport='ml',
                    source='mcla')

    def convert_schedule_html(self, html: str,
                              team: Team) -> Iterator[ScheduleGame]:
        soup = BeautifulSoup(html, 'html.parser')
        opponent_rows = soup.find_all('div', class_='game-opponent-tile')
        games = []
        for row in opponent_rows:
            opponent_div = row.find('div',
                                    class_='game-opponent-tile__opponent')
            date_div = row.find('div', class_='game-opponent-tile__date')
            time_string = next(
                row.find('p',
                         class_='game-opponent-tile__time').stripped_strings)
            time = time_string if _is_time(time_string) else ''
            score_div = row.find('div', class_='game-opponent-tile__result')

            opponent_p = opponent_div.find('p', class_='opponent__name')
            opponent_parts = list(opponent_p.stripped_strings)
            if len(opponent_parts) == 1:
                opponent = TeamSummary(name=opponent_parts[0])
                home = True
            else:
                opponent = TeamSummary(name=opponent_parts[1])
                home = False

            opp_link = opponent_p.a['href']
            opponent.id = self._parse_team_link_into_id(
                team.sport, team.source, opp_link)

            date = ' '.join(
                list(date_div.stripped_strings) + [time] + [team.year])
            date = parser.parse(date, tzinfos=TIMEZONES).isoformat()
            game_details_url = score_div.a['href']
            details = Location(
                url=self._convert_url_to_absolute(game_details_url))
            id = '-'.join(
                [team.sport, team.source,
                 game_details_url.split('/')[2]])

            score = ' '.join(
                score_div.find(
                    'p', class_='game-opponent-tile__score').stripped_strings)
            score_match = re.match(
                r'(?P<result>[WL])?\s?(?P<points_for>\d+)\s?-\s?(?P<points_against>\d+)',
                score)

            if score_match:
                points_for = int(score_match.group('points_for'))
                points_against = int(score_match.group('points_against'))
                d = dateutil.parser.isoparse(date).date()
                today = datetime.date.today()
                if d < today:
                    result = ScheduleGameResult(points_for=points_for,
                                                points_against=points_against)
                elif points_for > 0 or points_against > 0:
                    result = ScheduleGameResult(points_for=points_for,
                                                points_against=points_against)
                else:
                    result = None
            else:
                result = None

            games.append(
                ScheduleGame(id=id,
                             date=date,
                             details=details,
                             opponent=opponent,
                             sport=team.sport,
                             source=team.source,
                             result=result,
                             home=home))

        return games

    def cross_link_schedules(self, schedules):
        pass

    def convert_game_details_html(self, html: str, location: Location,
                                  game_id: str, sport: str, source: str,
                                  home_team: Team, away_team: Team) -> Game:
        soup = BeautifulSoup(html, 'html.parser')
        
        game_page_header = soup.find('div', class_='game-page-header')
        away_team_div = game_page_header.find('div', class_='game-page-header__team--away')
        home_team_div = game_page_header.find('div', class_='game-page-header__team--home')
        
        away_name = away_team_div.find('span', class_='team__name').get_text(strip=True)
        home_name = home_team_div.find('span', class_='team__name').get_text(strip=True)
        
        # Extract stable team IDs from scoring summary tables
        # These have div.team-info with links containing the team slug
        team_info_divs = soup.find_all('div', class_='team-info')
        if len(team_info_divs) >= 2:
            # First team-info is away, second is home (appears twice in different tables)
            away_link = team_info_divs[0].find('a')
            home_link = team_info_divs[1].find('a')
            away_id = self._parse_team_link_into_id(sport, source, away_link['href']) if away_link else None
            home_id = self._parse_team_link_into_id(sport, source, home_link['href']) if home_link else None
        else:
            # Fallback: no scoring data yet, use names (will be inconsistent but better than crashing)
            away_id = None
            home_id = None
        
        info_div = game_page_header.find('div', class_='game-page-header__info')
        date_str = info_div.find('span', class_='info__date').get_text(strip=True)
        # Game details don't include time or timezone, default to noon EST
        year = getattr(home_team, 'year', None) or getattr(away_team, 'year', None)
        if not year:
            year = str(datetime.date.today().year)
        date = parser.parse(date_str + ' ' + year + ' 12:00 EST', tzinfos=TIMEZONES).isoformat()
        
        home_team = TeamSummary(id=home_id, name=home_name)
        away_team = TeamSummary(id=away_id, name=away_name)
        
        # Parse scores
        try:
            info_div = game_page_header.find('div', class_='game-page-header__info')
            away_score_tag = info_div.find('span', class_='info__result--away')
            away_score = int(away_score_tag.get_text(strip=True)) if away_score_tag else None
        except:
            away_score = None
        try:
            home_score_tag = info_div.find('span', class_='info__result-home')
            home_score = int(home_score_tag.get_text(strip=True)) if home_score_tag else None
        except:
            home_score = None
        result = GameResult(
            home_score=home_score,
            away_score=away_score) if home_score is not None and away_score is not None else None

        roster_groups = soup.find('div', class_='roster-groups')
        (away_container,
         home_container) = roster_groups.find_all('div', recursive=False)

        if away_container:
            away_tables = away_container.find_all('table',
                                                  class_='stats-table')
            away_stats = self._parse_stats_tables(away_tables, sport, source)
        else:
            away_stats = None

        if home_container:
            home_tables = home_container.find_all('table',
                                                  class_='stats-table')
            home_stats = self._parse_stats_tables(home_tables, sport, source)
        else:
            home_stats = None

        return Game(id=game_id,
                    external_link=location.url,
                    date=date,
                    home_team=home_team,
                    away_team=away_team,
                    result=result,
                    home_stats=home_stats,
                    away_stats=away_stats)

    def convert_roster(self, html: str, team: Team) -> Roster:
        soup = BeautifulSoup(html, 'html.parser')
        head_coach_tag = soup.find('div', class_='coach-tile__info')
        if head_coach_tag:
            coach = Coach(
                name=next(head_coach_tag.stripped_strings),
                id=self._parse_coach_link_into_id(team.sport, team.source,
                                                  head_coach_tag.a['href']),
                external_link='https://mcla.us' + head_coach_tag.a['href'])
        else:
            coach = None

        def is_conference(href):
            return href.startswith('/conferences')

        header_tag = soup.find('div', class_='team-header-card__orgs')
        conference_tag = header_tag.find('a', href=is_conference)
        conference = Conference(
            name=conference_tag.string,
            id=self._parse_conference_link_into_id(team.sport, team.source,
                                                   conference_tag['href']),
            external_link='https://mcla.us' + conference_tag['href'])
        player_tiles = soup.find_all('div', class_='player-tile')
        players = [
            self._parse_player_tile(team.sport, team.source, tile)
            for tile in player_tiles
        ]
        return Roster(coach=coach, conference=conference, players=players)

    def get_limiter_session_args(self):
        return {'per_minute': 30}

    def _parse_stats_tables(self, tables, sport, source):
        stats = []

        def make_stats_line(**kwargs):
            face_offs = None
            if 'fow' in kwargs and 'fol' in kwargs:
                if kwargs['fow'] > 0 or kwargs['fol'] > 0:
                    face_offs = FaceOffResults(won=kwargs['fow'],
                                               lost=kwargs['fol'])
                del kwargs['fow']
                del kwargs['fol']
            return GameStatLine(face_offs=face_offs, **kwargs)

        for table in tables:
            rows = parse_table(
                table, lambda col, cell: self._parse_stats_table_row(
                    sport, source, col, cell), make_stats_line,
                table.select_one('thead tr:not(.pre-header)'))
            stats.extend(rows)
        return stats

    def _parse_roster_table_row(self, sport, source, col_name, cell):
        if col_name == '#':
            return {'number': int(cell.string)}
        if col_name == 'Player':
            last, first = ''.join(cell.a.stripped_strings).split(',')
            return {
                'player':
                PlayerSummary(id=self._parse_player_link_into_id(
                    sport, source, cell.a['href']),
                              name=f'{first.strip()} {last.strip()}',
                              external_link='https://mcla.us' + cell.a['href'])
            }
        if col_name == 'Yr':
            return {'class_year': cell.string}
        if col_name == 'El':
            return {'eligibility': cell.string}
        if col_name == 'Pos':
            return {'position': cell.string}
        if col_name == 'HT':
            return {'height': cell.string}
        if col_name == 'WT':
            return {'weight': cell.string}
        if col_name == 'High School':
            return {'high_school': cell.string}
        if col_name == 'Hometown':
            return {'hometown': cell.string}
        return None

    def _parse_player_tile(self, sport, source, tile) -> RosterPlayer:
        number_name = list(
            tile.find('div', class_='player-tile__name').stripped_strings)
        number = int(number_name[0]) if len(number_name) > 1 else None

        def is_name(href):
            return href.startswith('/players')

        name_tile = tile.find('div', class_='player-tile__name')
        name_tag = name_tile.find('a', href=is_name)
        name = name_tag.string
        external_link = 'https://mcla.us' + name_tag['href']
        id = self._parse_player_link_into_id(sport, source, name_tag['href'])
        info = list(
            tile.find('div', class_='player-tile__meta').stripped_strings)
        position = info[0] if len(info) > 0 else None
        class_year = info[1] if len(info) > 1 else None
        eligibility = info[2] if len(info) > 2 else None
        height = info[3] if len(info) > 3 else None
        weight = info[4] if len(info) > 4 else None
        locaton_tile = tile.find('div', class_='player-tile__location')
        (hometown, ) = locaton_tile.stripped_strings if locaton_tile else (
            None, )

        return RosterPlayer(player=PlayerSummary(id=id,
                                                 name=name,
                                                 external_link=external_link),
                            class_year=class_year,
                            eligibility=eligibility,
                            position=position,
                            number=number,
                            height=height,
                            weight=weight,
                            hometown=hometown)

    def _parse_stats_table_row(self, sport, source, col_name, cell):
        if col_name == '#':
            return {'number': int(cell.string) if cell.string else None}
        if col_name == 'Player':
            link = cell.find('a')
            if not link:
                return None
            name = link.get_text(strip=True)
            pos_tag = cell.find('span', class_='position')
            position = pos_tag.get_text(strip=True) if pos_tag else None
            return {
                'player':
                PlayerSummary(id=self._parse_player_link_into_id(
                    sport, source, link['href']),
                              name=name,
                              external_link=self._convert_url_to_absolute(
                                  link['href'])),
                'position': position
            }
        if col_name == 'FO-W':
            return {'fow': int(cell.string)}
        if col_name == 'FO-L':
            return {'fol': int(cell.string)}
        if col_name == 'GB':
            return {'gb': int(cell.string)}
        if col_name == 'G':
            return {'g': int(cell.string)}
        if col_name == 'A':
            return {'a': int(cell.string)}
        if col_name == 'SV':
            return {'s': int(cell.string)}
        if col_name == 'GA':
            return {'ga': int(cell.string)}

    def _normalize_slug(self, slug):
        return re.sub(r'\_', '-', slug)

    def _parse_team_link_into_id(self, sport, source, link):
        link_parts = link.split('/')
        id = self._normalize_slug(link_parts[2])
        if len(link_parts) > 2:
            return '-'.join([sport, source, id])
        else:
            return None

    PLAYER_REGEX = re.compile(
        r'^(https://mcla.us)?/players/(?P<id>[a-z0-9_\-]+)')

    def _parse_player_link_into_id(self, sport, source, link):
        link_match = self.PLAYER_REGEX.match(link)
        return '-'.join([sport, source, link_match.group('id')])

    def _parse_conference_link_into_id(self, sport, source, link):
        link_parts = link.split('/')
        id = link_parts[2]
        return '-'.join([sport, source, id])

    def _parse_coach_link_into_id(self, sport, source, link):
        link_parts = link.split('/')
        id = link_parts[2]
        return '-'.join([sport, source, id])

    def _convert_url_to_absolute(self, href):
        if href.startswith('https://'):
            return href
        else:
            return 'https://mcla.us' + href


def _is_time(time_string):
    try:
        parser.parse(time_string, tzinfos=TIMEZONES)
        return True
    except:
        return False
