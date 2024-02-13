import re
from bs4 import BeautifulSoup
import datetime
import dateutil.parser as parser
from .tables import parse_table

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


class Mcla():

    def get_team_list_urls(self, year):
        yield {'url': f'https://mcla.us/teams/{year}', 'year': year}

    def convert_team_list_html(self, html, location):
        soup = BeautifulSoup(html, 'html.parser')
        division_tables = soup.find_all('table', class_='team-roster')
        for table in division_tables:
            divison_text = next(table.parent.header.stripped_strings)
            for row in table.find_all('tr'):
                link = row.find('a')
                link_parts = link['href'].split('/')
                slug = link_parts[2]
                year = location['year']
                yield {
                    'name': next(link.stripped_strings),
                    'schedule': {
                        'url':
                        f'https://mcla.us/team/{slug}/{year}/schedule.html'
                    },
                    'roster': {
                        'url': f'https://mcla.us/team/{slug}/{year}/roster.html'
                    },
                    'year': location['year'],
                    'id': f'ml-mcla-{self._normalize_slug(slug)}',
                    'div': 'mcla' + DIVISON_MAP[divison_text],
                    'sport': 'ml',
                    'source': 'mcla'
                }

    def convert_schedule_html(self, html, team):
        soup = BeautifulSoup(html, 'html.parser')
        team_schedule = soup.find('table', class_='team-schedule')
        rows = team_schedule.tbody.find_all('tr') if team_schedule else []
        games = []
        for row in rows:
            game = {}
            cols = list(row.find_all('td'))
            opponent_col = cols[0]
            date_col = cols[2]
            score_col = cols[3]

            opponent_parts = list(opponent_col.stripped_strings)
            if len(opponent_parts) == 1:
                game['opponent'] = {'name': opponent_parts[0]}
                game['home'] = True
            else:
                game['opponent'] = {'name': opponent_parts[1]}
                game['home'] = False

            game['sport'] = team['sport']
            game['source'] = team['source']

            opp_link = opponent_col.a['href']
            opp_id = self._parse_team_link_into_id(team['sport'],
                                                   team['source'], opp_link)
            if opp_id:
                game['opponent']['id'] = opp_id

            date = ' '.join([team['year']] + list(date_col.stripped_strings))
            game['date'] = datetime.datetime.strptime(
                date, '%Y %a %b %d %I:%M%p').isoformat()
            game_details_url = date_col.a['href']
            game['details'] = {'url': game_details_url}
            game['id'] = '-'.join([
                team['sport'], team['source'],
                game_details_url.split('/')[4]
            ])

            score = score_col.string
            score_match = re.match(
                r'(?P<result>Won|Lost)?\s+\((?P<points_for>\d+)-(?P<points_against>\d+)\)',
                score)

            if score_match:
                game['result'] = {
                    'points_for': int(score_match.group('points_for')),
                    'points_against': int(score_match.group('points_against'))
                }

            games.append(game)

        return games

    def cross_link_schedules(self, schedules):
        pass

    def convert_game_details_html(self, html, location, game_id, sport, source,
                                  home_team, away_team):
        soup = BeautifulSoup(html, 'html.parser')
        result = {'id': game_id, 'external_link': location['url']}
        header = soup.find(class_='name-and-info').h1
        teams, date = header.string.rsplit('on', maxsplit=1)
        away_name, home_name = map(lambda x: x.strip(), teams.split('vs'))
        time = header.next_sibling.replace('@', '')
        date_time = parser.parse(date.strip() + ' ' + time.strip(),
                                 tzinfos=TIMEZONES).isoformat()
        result['date'] = date_time
        game_score = soup.find('div', class_='game-score')
        away_team = game_score.find(class_='team-away')
        home_team = game_score.find(class_='team-home')
        away_id = self._parse_team_link_into_id(sport, source,
                                                away_team.a['href'])
        home_id = self._parse_team_link_into_id(sport, source,
                                                home_team.a['href'])
        result['home_team'] = {'id': home_id, 'name': home_name}
        result['away_team'] = {'id': away_id, 'name': away_name}
        away_score = int(away_team.find(class_='score').string)
        home_score = int(home_team.find(class_='score').string)
        result['result'] = {'home_score': home_score, 'away_score': away_score}
        away_header = soup.find('header', attrs={'title': 'Away Team'})
        if away_header:
            away_tables = away_header.find_next_siblings('table')
            result['away_stats'] = self._parse_stats_tables(
                away_tables, sport, source)

        home_header = soup.find('header', attrs={'title': 'Home Team'})
        if home_header:
            home_tables = home_header.find_next_siblings('table')
            result['home_stats'] = self._parse_stats_tables(
                home_tables, sport, source)

        return result

    def _parse_stats_tables(self, tables, sport, source):
        stats = []
        for table in tables:
            rows = parse_table(table, lambda col, cell: self._parse_stats_table_row(
                sport, source, col, cell))
            stats.extend(rows)
        return stats

    def get_limiter_session_args(self):
        return {}

    def convert_roster(self, html, team):
        soup = BeautifulSoup(html, 'html.parser')
        result = {
            'team': team
        }
        head_coach = soup.find(class_='head-coach')
        result['coach'] = {
            'name': next(head_coach.stripped_strings),
            'id': self._parse_coach_link_into_id(team['sport'], team['source'], head_coach.a['href']),
            'external_link': 'https://mcla.us' + head_coach.a['href']
        }
        conference = soup.find(class_='conference')
        result['conference'] = {
            'name': next(conference.stripped_strings),
            'id': self._parse_conference_link_into_id(team['sport'], team['source'], conference.a['href']),
            'external_link': 'https://mcla.us' + conference.a['href']
        }
        table = soup.find(class_='team-roster')
        result['players'] = parse_table(table, lambda col, cell: self._parse_roster_table_row(
            team['sport'], team['source'], col, cell))
        return result

    def _parse_roster_table_row(self, sport, source, col_name, cell):
        if col_name == '#':
            return ['number', int(cell.string)]
        if col_name == 'Player':
            last, first = ''.join(cell.a.stripped_strings).split(',')
            return ['player', {
                'id':
                self._parse_player_link_into_id(
                    sport, source, cell.a['href']),
                'name': f'{first.strip()} {last.strip()}',
                'external_link':
                'https://mcla.us' + cell.a['href']
            }]
        if col_name == 'Yr':
            return ['class', cell.string]
        if col_name == 'El':
            return ['eligibility', cell.string]
        if col_name == 'Pos':
            return ['position', cell.string]
        if col_name == 'HT':
            return ['height', cell.string]
        if col_name == 'WT':
            return ['weight', cell.string]
        if col_name == 'High School':
            return ['high_school', cell.string]
        if col_name == 'Hometown':
            return ['hometown', cell.string]

    def _parse_stats_table_row(self, sport, source, col_name, cell):
        if col_name == '#':
            return ['number', int(cell.string)]
        if col_name == 'Field Player' or col_name == 'Goalie':
            return ['player', {
                'id':
                self._parse_player_link_into_id(
                    sport, source, cell.a['href']),
                'name':
                cell.a.string,
                'external_link':
                cell.a['href']
            }]
        if col_name == 'Pos':
            return ['position', cell.string]
        if col_name == 'FO':
            won, lost = cell.string.split('-')
            if won or lost:
                return ['face_offs', {
                    'won': won or 0,
                    'lost': lost or 0
                }]
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


DIVISON_MAP = {'Division I': '1', 'Division II': '2', 'Division III': '3'}
