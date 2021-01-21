import requests
import re
from bs4 import BeautifulSoup

class Mcla():
  def get_team_list_urls(self, year):
    yield {
      'url': f'https://mcla.us/teams/{year}',
      'year': year
    }

  def convert_team_list_html(self, html, location):
    soup = BeautifulSoup(html, 'html.parser')
    division_tables = soup.find_all('table', attrs={'class':'team-roster'})
    for table in division_tables:
      divison_text = next(table.parent.header.stripped_strings)
      for row in table.find_all('tr'):
        link = row.find('a')
        link_parts = link['href'].split('/')
        slug = link_parts[2]
        year = location['year']
        yield {
          'name': next(link.stripped_strings),
          'schedule_location': {
            'url': f'https://mcla.us/team/{slug}/{year}/schedule.html'
          },
          'year': location['year'],
          'id': f'ml-mcla-{self.normalize_slug(slug)}',
          'div': DIVISON_MAP[divison_text],
          'sport': 'ml'
        }

  def normalize_slug(self, slug):
    return re.sub(r'\_', '-', slug)

DIVISON_MAP = {
  'Division I': '1',
  'Division II': '2',
  'Division III': '3'
}


