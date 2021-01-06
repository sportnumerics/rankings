import unittest
from . import mcla
from . import fixtures

class TestMcla(unittest.TestCase):
  def test_ncaa_urls(self):
    n = mcla.Mcla()
    self.assertEqual(
      list(n.get_team_list_urls('2020')), [
        {
          'url':'https://mcla.us/teams/2020'
        }
      ])

  def test_ncaa_team_list_html(self):
    html = fixtures.mcla_team_list()
    n = mcla.Mcla()
    team_list = list(n.convert_team_list_html(html, {
      'url':'https://mcla.us/teams/2020'
    }))
    self.assertEqual(len(team_list), 163)
    self.assertEqual(
      team_list[0],
      {
        'name': 'Alabama',
        'location': {
          'id': 'alabama'
        },
        'div':'1'
      })
    print(team_list)