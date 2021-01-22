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
        'schedule_location': {
          'url': 'https://mcla.us/team/alabama/2020/schedule.html'
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
        'schedule_location': {
          'url': 'https://mcla.us/team/arizona_state/2020/schedule.html'
        },
        'year': '2020',
        'div': '1',
        'id': 'ml-mcla-arizona-state',
        'sport': 'ml'
      }
    )

  def test_mcla_team_schedule_html(self):
    html = fixtures.mcla_schedule()
    m = mcla.Mcla()
    team = {
      'name': 'Arizona State',
      'year': '2020'
    }
    schedule = m.convert_schedule_html(html, team)
    self.assertEqual(schedule['team'], team)
    self.assertEqual(schedule['games'][0], {
      'date': '2020-02-09',
      'opponent': {
        'name': 'Dominican'
      },
      'home': True,
      'result': {
        'points_for': 11,
        'points_against': 16
      }
    })