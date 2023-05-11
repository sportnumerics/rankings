import requests
import re
from bs4 import BeautifulSoup
import datetime


class Mcla():
  def get_team_list_urls(self, year):
    yield {'url': f'https://mcla.us/teams/{year}', 'year': year}

  def convert_team_list_html(self, html, location):
    soup = BeautifulSoup(html, 'html.parser')
    division_tables = soup.find_all('table', attrs={'class': 'team-roster'})
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
            'div': DIVISON_MAP[divison_text],
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
      opp_link_parts = opp_link.split('/')
      opp_id = self._normalize_slug(opp_link_parts[2])
      if len(opp_link_parts) > 2:
        game['opponent']['id'] = '-'.join(
            [team['sport'], team['source'], opp_id])

      date = ' '.join([team['year']] + list(date_col.stripped_strings))
      game['date'] = datetime.datetime.strptime(
          date, '%Y %a %b %d %I:%M%p').isoformat()
      game['details'] = {
        'url': date_col.a['href']
      }

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

  def _normalize_slug(self, slug):
    return re.sub(r'\_', '-', slug)


DIVISON_MAP = {'Division I': '1', 'Division II': '2', 'Division III': '3'}
