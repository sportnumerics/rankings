import unittest
from . import ncaa
from . import fixtures

class TestScrape(unittest.TestCase):
  def test_ncaa_urls(self):
    n = ncaa.Ncaa(['MLA'], ['1','2'])
    self.assertEqual(
      list(n.get_team_list_urls('2020')), [
        {
          'url':'https://stats.ncaa.org/team/inst_team_list',
          'params':{'academic_year':'2020','division':'1','sport_code':'MLA'}
        },
        {
          'url':'https://stats.ncaa.org/team/inst_team_list',
          'params':{'academic_year':'2020','division':'2','sport_code':'MLA'}
        }
      ])

  def test_ncaa_team_list_html(self):
    html = fixtures.ncaa_team_list()
    n = ncaa.Ncaa()
    team_list = list(n.convert_team_list_html(html, {
      'url':'https://stats.ncaa.org/team/inst_team_list',
      'params':{'academic_year':'2020','division':'1','sport_code':'MLA'}
    }))
    self.assertEqual(len(team_list), 49)
    self.assertEqual(
      team_list[0],
      {
        'name': 'Air Force',
        'location': {
          'game_sport_year_ctl_id': '15203',
          'id': '721'
        },
        'div':'1',
        'sport_code':'MLA'
      })