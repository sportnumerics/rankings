import unittest
from . import ncaa
from . import fixtures

class TestScrape(unittest.TestCase):
  def test_ncaa_urls(self):
    n = ncaa.Ncaa(['MLA'], ['1','2'])
    urls = list(n.get_team_list_urls('2020'))
    self.assertEqual(urls[0]['url'], 'https://stats.ncaa.org/team/inst_team_list')
    self.assertEqual(urls[0]['params'], {'academic_year':'2020','division':'1','sport_code':'MLA'})
    self.assertEqual(urls[1]['url'], 'https://stats.ncaa.org/team/inst_team_list')
    self.assertEqual(urls[1]['params'], {'academic_year':'2020','division':'2','sport_code':'MLA'})

  def test_ncaa_team_list_html(self):
    html = fixtures.ncaa_team_list()
    n = ncaa.Ncaa()
    team_list = list(n.convert_team_list_html(html, next(n.get_team_list_urls('2020'))))
    self.assertEqual(len(team_list), 49)
    self.assertEqual(
      team_list[0],
      {
        'name': 'Air Force',
        'location': {
          'url': 'https://stats.ncaa.org/player/game_by_game',
          'params': {
            'game_sport_year_ctl_id': '15203',
            'org_id': '721',
            'stats_player_seq': -100
          }
        },
        'year': '2020',
        'id': 'ml-ncaa-721',
        'div':'1',
        'sport': 'ml'
      })