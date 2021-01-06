import requests
from bs4 import BeautifulSoup

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
          'id': link_parts[2],
          'game_sport_year_ctl_id': link_parts[3]
        },
        'id': f'{sport}-ncaa-{link_parts[2]}',
        'div': location['params']['division'],
        'sport': sport,
        'year': location['params']['academic_year']
      }

SPORT_MAP = {
  'MLA': 'ml',
  'WLA': 'wl'
}


