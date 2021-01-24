import unittest
from . import predict

class TestPredict(unittest.TestCase):
  def test_calculate_ratings(self):
    schedules = [
      create_schedule('1', [
        home_game('2', result=(10, 5)),
        home_game('3', result=(10, 2)),
      ]),
      create_schedule('2', [
        away_game('1', result=(5, 10)),
        home_game('3', result=(6, 1))
      ]),
      create_schedule('3', [
        away_game('1', result=(2, 10)),
        away_game('3', result=(1, 6))
      ])
    ]

    ratings, year, hfa = predict.calculate_ratings(schedules)

    self.assertGreater(ratings['1']['overall'], ratings['2']['overall'])
    self.assertGreater(ratings['2']['overall'], ratings['3']['overall'])
    self.assertEqual(year, '2020')

def create_schedule(team_id, games):
  return {
    'team': {
      'id': team_id,
      'year': '2020'
    },
    'games': games
  }

def home_game(opponent_id, result):
  return create_game(opponent_id, result, home=True)

def away_game(opponent_id, result):
  return create_game(opponent_id, result, home=False)

def create_game(opponent_id, result=None, home=False):
  game = {
    'opponent': {
      'id': opponent_id,
    },
    'home': home,
    'date': 'today'
  }
  if result:
    game['result'] = {
      'points_for': result[0],
      'points_against': result[1]
    }
  return game
