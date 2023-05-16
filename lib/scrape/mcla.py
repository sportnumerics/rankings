import requests
import re
from bs4 import BeautifulSoup
import datetime
import dateutil.parser as parser

TIMEZONES = {
  'PDT': -7*3600,
  'PST': -8*3600,
  'MDT': -6*3600,
  'MST': -7*3600,
  'CDT': -5*3600,
  'CST': -6*3600,
  'EDT': -4*3600,
  'EST': -5*3600
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
                'url': f'https://mcla.us/team/{slug}/{year}/schedule.html'
            },
            'year': location['year'],
            'id': f'ml-mcla-{self._normalize_slug(slug)}',
            'div': 'mcla' + DIVISON_MAP[divison_text],
            'sport': 'ml',
            'source': 'mcla'
        }

  def convert_schedule_html(self, html, team):
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find('table', class_='team-schedule').tbody.find_all('tr')
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
      opp_link = opponent_col.a['href']
      opp_id = self._parse_team_link_into_id(team['sport'], team['source'], opp_link)
      if opp_id:
        game['opponent']['id'] = opp_id

      date = ' '.join([team['year']] + list(date_col.stripped_strings))
      game['date'] = datetime.datetime.strptime(
          date, '%Y %a %b %d %I:%M%p').isoformat()
      game_details_url = date_col.a['href']
      game['details'] = {
        'url': game_details_url
      }
      game['id'] = '-'.join([team['sport'], team['source'], game_details_url.split('/')[4]])

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

    return {'team': team, 'games': games}

  def convert_game_details_html(self, html, location, game_id, sport, source):
    soup = BeautifulSoup(html, 'html.parser')
    result = {
      'id': game_id,
      'external_link': location['url']
    }
    header = soup.find(class_='name-and-info').h1
    teams, date = header.string.rsplit('on', maxsplit=1)
    away_name, home_name = map(lambda x: x.strip(), teams.split('vs'))
    time = header.next_sibling.replace('@', '')
    date_time = parser.parse(date.strip() + ' ' + time.strip(), tzinfos=TIMEZONES).isoformat()
    result['date'] = date_time
    game_score = soup.find('div', class_='game-score')
    away_team = game_score.find(class_='team-away')
    home_team = game_score.find(class_='team-home')
    away_id = self._parse_team_link_into_id(sport, source, away_team.a['href'])
    home_id = self._parse_team_link_into_id(sport, source, home_team.a['href'])
    result['home_team'] = {
      'id': home_id,
      'name': home_name
    }
    result['away_team'] = {
      'id': away_id,
      'name': away_name
    }
    away_score = int(away_team.find(class_='score').string)
    home_score = int(home_team.find(class_='score').string)
    result['result'] = {
      'home_score': home_score,
      'away_score': away_score
    }
    away_header = soup.find('header', attrs={'title': 'Away Team'})
    if away_header:
      away_tables = away_header.find_next_siblings('table')
      result['away_stats'] = self._parse_stats_tables(away_tables, sport, source)

    home_header = soup.find('header', attrs={'title': 'Home Team'})
    if home_header:
      home_tables = home_header.find_next_siblings('table')
      result['home_stats'] = self._parse_stats_tables(home_tables, sport, source)

    return result

  def _parse_stats_tables(self, tables, sport, source):
    stats = []
    for table in tables:
      col_mapping = {}
      for i, heading in enumerate(table.thead.find_all('th')):
        col_mapping[i] = ''.join(heading.stripped_strings)
      for raw_row in table.tbody.find_all('tr'):
        row = {}
        for i, cell in enumerate(raw_row.find_all('td')):
          if cell.string == "No recorded player stats":
            break
          col_name = col_mapping[i]
          if col_name == '#':
            row['number'] = int(cell.string)
          if col_name == 'Field Player' or col_name == 'Goalie':
            row['player'] = {
              'id': self._parse_player_link_into_id(sport, source, cell.a['href']),
              'name': cell.a.string,
              'external_link': cell.a['href']
            }
          if col_name == 'Pos':
            row['position'] = cell.string
          if col_name == 'FO':
            won, lost = cell.string.split('-')
            if won or lost:
              row['face_offs'] = {
                'won': won or 0,
                'lost': lost or 0
              }
          if col_name == 'GB':
            row['gb'] = int(cell.string)
          if col_name == 'G':
            row['g'] = int(cell.string)
          if col_name == 'A':
            row['a'] = int(cell.string)
          if col_name == 'S':
            row['s'] = int(cell.string)
          if col_name == 'GA':
            row['ga'] = int(cell.string)
        if row:
          stats.append(row)
    return stats


  def _normalize_slug(self, slug):
    return re.sub(r'\_', '-', slug)


  def _parse_team_link_into_id(self, sport, source, link):
    link_parts = link.split('/')
    id = self._normalize_slug(link_parts[2])
    if len(link_parts) > 2:
      return '-'.join([sport, source, id])
    else:
      return None

  def _parse_player_link_into_id(self, sport, source, link):
    link_parts = link.split('/')
    id = link_parts[4]
    return '-'.join([sport, source, id])

DIVISON_MAP = {'Division I': '1', 'Division II': '2', 'Division III': '3'}
