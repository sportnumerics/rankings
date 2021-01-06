import requests
from bs4 import BeautifulSoup

class Mcla():
  def get_team_list_urls(self, year):
    yield {
      'url': f'https://mcla.us/teams/{year}'
    }

  def convert_team_list_html(self, html, url):
    soup = BeautifulSoup(html, 'html.parser')
    division_tables = soup.find_all('table', attrs={'class':'team-roster'})
    for table in division_tables:
      divison_text = next(table.parent.header.stripped_strings)
      for row in table.find_all('tr'):
        link = row.find('a')
        link_parts = link['href'].split('/')
        yield {
          'name': next(link.stripped_strings),
          'location': {
            'id': link_parts[2]
          },
          'div': DIVISON_MAP[divison_text]
        }

DIVISON_MAP = {
  'Division I': '1',
  'Division II': '2',
  'Division III': '3'
}


