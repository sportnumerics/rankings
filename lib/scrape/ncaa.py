import requests
from bs4 import BeautifulSoup


SPORT_MAP = {
  'MLA': 'ml',
  'WLA': 'wl'
}

class Ncaa():
  def __init__(self, sports = ['MLA', 'WLA'], divs = ['1','2','3']):
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
        'location': {
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
        'year': location['params']['academic_year']
      }
