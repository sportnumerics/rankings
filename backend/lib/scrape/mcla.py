from collections.abc import Iterator
import re
from bs4 import BeautifulSoup
import datetime
import dateutil.parser as parser
from .tables import parse_table
from ..shared.types import Team, Location, ScheduleGame, TeamSummary, Game, ScheduleGameResult, GameResult, GameStatLine, Roster, RosterPlayer, Coach, Conference, PlayerSummary

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

DIVISION_MAP = {'Division I': '1', 'Division II': '2', 'Division III': '3'}


class Mcla():

    def get_team_list_urls(self, year: str) -> Location:
        yield Location(url=f'https://mcla.us/teams/{year}')

    def convert_team_list_html(self, html: str, year: str,
                               location: Location) -> Iterator[Team]:
        soup = BeautifulSoup(html, 'html.parser')
        division_tables = soup.find_all('table', class_='team-roster')
        for table in division_tables:
            division_text = next(table.parent.header.stripped_strings)
            for row in table.find_all('tr'):
                link = row.find('a')
                link_parts = link['href'].split('/')
                slug = link_parts[2]
                yield Team(
                    name=next(link.stripped_strings),
                    schedule=Location(
                        url=f'https://mcla.us/team/{slug}/{year}/schedule.html'
                    ),
                    roster=Location(
                        url=f'https://mcla.us/team/{slug}/{year}/roster.html'),
                    year=year,
                    id=f'ml-mcla-{self._normalize_slug(slug)}',
                    div='mcla' + DIVISION_MAP[division_text],
                    sport='ml',
                    source='mcla')

    def convert_schedule_html(self, html: str,
                              team: Team) -> Iterator[ScheduleGame]:
        soup = BeautifulSoup(html, 'html.parser')
        team_schedule = soup.find('table', class_='team-schedule')
        rows = team_schedule.tbody.find_all('tr') if team_schedule else []
        games = []
        for row in rows:
            cols = list(row.find_all('td'))
            opponent_col = cols[0]
            date_col = cols[2]
            score_col = cols[3]

            opponent_parts = list(opponent_col.stripped_strings)
            if len(opponent_parts) == 1:
                opponent = TeamSummary(name=opponent_parts[0])
                home = True
            else:
                opponent = TeamSummary(name=opponent_parts[1])
                home = False

            opp_link = opponent_col.a['href']
            opponent.id = self._parse_team_link_into_id(
                team.sport, team.source, opp_link)

            date = ' '.join([team.year] + list(date_col.stripped_strings))
            date = datetime.datetime.strptime(
                date, '%Y %a %b %d %I:%M%p').isoformat()
            game_details_url = date_col.a['href']
            details = Location(url=game_details_url)
            id = '-'.join(
                [team.sport, team.source,
                 game_details_url.split('/')[4]])

            score = score_col.string
            score_match = re.match(
                r'(?P<result>Won|Lost)?\s+\((?P<points_for>\d+)-(?P<points_against>\d+)\)',
                score)

            result = ScheduleGameResult(
                points_for=int(score_match.group('points_for')),
                points_against=int(score_match.group(
                    'points_against'))) if score_match else None

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
        header = soup.find(class_='name-and-info').h1
        teams, date_tag = header.string.rsplit('on', maxsplit=1)
        away_name, home_name = map(lambda x: x.strip(), teams.split('vs'))
        time = header.next_sibling.replace('@', '')
        date = parser.parse(date_tag.strip() + ' ' + time.strip(),
                            tzinfos=TIMEZONES).isoformat()
        game_score = soup.find('div', class_='game-score')
        away_team_tag = game_score.find(class_='team-away')
        home_team_tag = game_score.find(class_='team-home')
        away_id = self._parse_team_link_into_id(sport, source,
                                                away_team_tag.a['href'])
        home_id = self._parse_team_link_into_id(sport, source,
                                                home_team_tag.a['href'])
        home_team = TeamSummary(id=home_id, name=home_name)
        away_team = TeamSummary(id=away_id, name=away_name)
        away_score = int(away_team_tag.find(class_='score').string)
        home_score = int(home_team_tag.find(class_='score').string)
        result = GameResult(home_score=home_score, away_score=away_score)
        away_header = soup.find('header', attrs={'title': 'Away Team'})
        if away_header:
            away_tables = away_header.find_next_siblings('table')
            away_stats = self._parse_stats_tables(away_tables, sport, source)
        else:
            away_stats = None

        home_header = soup.find('header', attrs={'title': 'Home Team'})
        if home_header:
            home_tables = home_header.find_next_siblings('table')
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
        head_coach_tag = soup.find(class_='head-coach')
        coach = Coach(
            name=next(head_coach_tag.stripped_strings),
            id=self._parse_coach_link_into_id(team.sport, team.source,
                                              head_coach_tag.a['href']),
            external_link='https://mcla.us' + head_coach_tag.a['href'])
        conference_tag = soup.find(class_='conference')
        conference = Conference(
            name=next(conference_tag.stripped_strings),
            id=self._parse_conference_link_into_id(team.sport, team.source,
                                                   conference_tag.a['href']),
            external_link='https://mcla.us' + conference_tag.a['href'])
        table = soup.find(class_='team-roster')
        players = parse_table(
            table, lambda col, cell: self._parse_roster_table_row(
                team.sport, team.source, col, cell), RosterPlayer)
        return Roster(coach=coach, conference=conference, players=players)

    def get_limiter_session_args(self):
        return {}

    def _parse_stats_tables(self, tables, sport, source):
        stats = []
        for table in tables:
            rows = parse_table(
                table, lambda col, cell: self._parse_stats_table_row(
                    sport, source, col, cell), GameStatLine)
            stats.extend(rows)
        return stats

    def _parse_roster_table_row(self, sport, source, col_name, cell):
        if col_name == '#':
            return ('number', int(cell.string))
        if col_name == 'Player':
            last, first = ''.join(cell.a.stripped_strings).split(',')
            return ('player',
                    PlayerSummary(id=self._parse_player_link_into_id(
                        sport, source, cell.a['href']),
                                  name=f'{first.strip()} {last.strip()}',
                                  external_link='https://mcla.us' +
                                  cell.a['href']))
        if col_name == 'Yr':
            return ('class_year', cell.string)
        if col_name == 'El':
            return ('eligibility', cell.string)
        if col_name == 'Pos':
            return ('position', cell.string)
        if col_name == 'HT':
            return ('height', cell.string)
        if col_name == 'WT':
            return ('weight', cell.string)
        if col_name == 'High School':
            return ('high_school', cell.string)
        if col_name == 'Hometown':
            return ('hometown', cell.string)
        return None

    def _parse_stats_table_row(self, sport, source, col_name, cell):
        if col_name == '#':
            return ['number', int(cell.string)]
        if col_name == 'Field Player' or col_name == 'Goalie':
            return [
                'player',
                PlayerSummary(id=self._parse_player_link_into_id(
                    sport, source, cell.a['href']),
                              name=cell.a.string,
                              external_link=cell.a['href'])
            ]
        if col_name == 'Pos':
            return ['position', cell.string]
        if col_name == 'FO':
            won, lost = cell.string.split('-')
            if won or lost:
                return ['face_offs', {'won': won or 0, 'lost': lost or 0}]
            else:
                return None
        if col_name == 'GB':
            return ['gb', int(cell.string)]
        if col_name == 'G':
            return ['g', int(cell.string)]
        if col_name == 'A':
            return ['a', int(cell.string)]
        if col_name == 'S':
            return ['s', int(cell.string)]
        if col_name == 'GA':
            return ['ga', int(cell.string)]

    def _normalize_slug(self, slug):
        return re.sub(r'\_', '-', slug)

    def _parse_team_link_into_id(self, sport, source, link):
        link_parts = link.split('/')
        id = self._normalize_slug(link_parts[2])
        if len(link_parts) > 2:
            return '-'.join([sport, source, id])
        else:
            return None

    PLAYER_REGEX = re.compile(r'^(https://mcla.us)?/player/(?P<id>\d+)/.*')

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
