import unittest
from . import mcla
from . import fixtures

class TestMcla(unittest.TestCase):
  def test_mcla_urls(self):
    m = mcla.Mcla()
    self.assertEqual(next(m.get_team_list_urls('2020'))['url'], 'https://mcla.us/teams/2020')

  def test_mcla_team_list_html(self):
    html = fixtures.mcla_team_list()
    m = mcla.Mcla()
    team_list = list(m.convert_team_list_html(html, next(m.get_team_list_urls('2020'))))
    self.assertEqual(len(team_list), 163)
    self.assertEqual(
      team_list[0],
      {
        'name': 'Alabama',
        'location': {
          'id': 'alabama'
        },
        'year': '2020',
        'div':'1',
        'id': 'ml-mcla-alabama',
        'sport': 'ml'
      })

  def test_mcla_converts_slugs_correctly(self):
    html = fixtures.mcla_team_list()
    m = mcla.Mcla()
    team_list = list(m.convert_team_list_html(html, next(m.get_team_list_urls('2020'))))
    self.assertEqual(
      team_list[2],
      {
        'name': 'Arizona State',
        'location': {
          'id': 'arizona_state'
        },
        'year': '2020',
        'div': '1',
        'id': 'ml-mcla-arizona-state',
        'sport': 'ml'
      }
    )