import requests
import datetime
import re
from bs4 import BeautifulSoup

SPORT_MAP = {'MLA': 'ml', 'WLA': 'wl'}


class Ncaa():
  def __init__(self, sports=['MLA', 'WLA'], divs=['1', '2', '3']):
    self.sports = sports
    self.divs = divs

  def get_team_list_urls(self, year):
    for sport in self.sports:
      for div in self.divs:
        yield {
            'url': 'https://stats.ncaa.org/team/inst_team_list',
            'params': {
                'academic_year': year,
                'division': div,
                'sport_code': sport
            }
        }

  def convert_team_list_html(self, html, location):
    soup = BeautifulSoup(html, 'html.parser')
    team_links = soup.table.table.find_all('a')
    for link in team_links:
      link_parts = link['href'].split('/')
      sport = SPORT_MAP[location['params']['sport_code']]
      yield {
          'name': link.string,
          'schedule': {
              'url': 'https://stats.ncaa.org/player/game_by_game',
              'params': {
                  'game_sport_year_ctl_id': link_parts[3],
                  'org_id': link_parts[2],
                  'stats_player_seq': -100
              }
          },
          'id': f'{sport}-ncaa-{link_parts[2]}',
          'div': location['params']['division'],
          'sport': sport,
          'year': location['params']['academic_year'],
          'source': 'ncaa'
      }

  def convert_schedule_html(self, html, team):
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find(id='game_breakdown_div').table.table.find_all('tr')
    games = []
    for row in rows:
      game = {}
      if 'class' in row.attrs or 'style' in row.attrs:
        continue
      cols = list(row.find_all('td'))
      date_col = cols[0]
      opp_col = cols[1]
      result_col = cols[2]

      date = datetime.datetime.strptime(date_col.string, '%m/%d/%Y').date()
      game['date'] = date.isoformat()

      def no_class(tag):
        return not tag.has_attr('class')

      opp_link = opp_col.find(
          lambda tag: tag.name == 'a' and not tag.has_attr('class'))
      opp_string = ' '.join(opp_col.stripped_strings)
      opp_match = re.match(
          r'(?P<away>\@)?\s*(?P<opponent_name>[^\@]+)(\@(?P<neutral_site>.*))?',
          opp_string)
      if not opp_match:
        continue

      game['opponent'] = {'name': opp_match.group('opponent_name').strip()}
      game['home'] = opp_match.group('away') is None

      opp_link_parts = opp_link['href'].split('/')
      if len(opp_link_parts) > 2:
        game['opponent']['id'] = '-'.join(
            [team['sport'], team['source'], opp_link_parts[2]])

      result_str = ' '.join(result_col.stripped_strings)
      score_match = re.match(
          r'(?P<outcome>[WL])\s*(?P<points_for>\d+)\s*\-\s*(?P<points_against>\d+)',
          result_str)
      if score_match:
        game['result'] = {
            'points_for': int(score_match.group('points_for')),
            'points_against': int(score_match.group('points_against'))
        }
      if hasattr(result_col, 'a') and hasattr(result_col.a, 'href'):
        game['details'] = {
          'url': result_col.a['href']
        }

      games.append(game)
    return {'team': team, 'games': games}
