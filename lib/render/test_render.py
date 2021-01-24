import unittest
from . import render
from .. import testing


class TestRender(unittest.TestCase):
  def test_extract_data(self):
    team1 = testing.create_team('team-1')
    team2 = testing.create_team('team-2')
    team3 = testing.create_team('team-3')
    ratings = [
      testing.create_rating('team-1', (27, 20, 7)),
      testing.create_rating('team-2', (25, 20, 5)),
      testing.create_rating('team-3', (11, 9, 2))
    ]
    teams = [[team2, team1, team3]]
    schedules = [
      testing.create_schedule(team1, [
        testing.create_game('team-2', result=(15,13)),
        testing.create_game('team-3', result=(18, 3))
      ]),
      testing.create_schedule(team2, [
        testing.create_game('team-1', result=(13,15)),
        testing.create_game('team-3')
      ]),
      testing.create_schedule(team3, [
        testing.create_game('team-1', result=(3, 18)),
        testing.create_game('team-2')
      ])
    ]

    team_lists = render.create_team_lists(ratings, teams, schedules)

    self.assertEqual(team_lists['/2020/mcla/1'],
      {
        'div': '1',
        'year': 2020,
        'teams': [
          {
            'name': 'team-1',
            'id': 'team-1',
            'wins': 2,
            'losses': 0,
            'ties': 0,
            'overall': 27,
            'offense': 20,
            'defense': 7
          },
          {
            'name': 'team-2',
            'id': 'team-2',
            'wins': 0,
            'losses': 1,
            'ties': 0,
            'overall': 25,
            'offense': 20,
            'defense': 5
          },
          {
            'name': 'team-3',
            'id': 'team-3',
            'wins': 0,
            'losses': 1,
            'ties': 0,
            'overall': 11,
            'offense': 9,
            'defense': 2
          }
        ]
      })