import unittest
from . import predict
from .. import testing


class TestPredict(unittest.TestCase):
  def test_calculate_ratings(self):
    schedules = [
        testing.create_schedule(testing.create_team('1'), [
            testing.home_game('2', result=(10, 5)),
            testing.home_game('3', result=(10, 2)),
        ]),
        testing.create_schedule(testing.create_team('2'), [
            testing.away_game('1', result=(5, 10)),
            testing.home_game('3', result=(6, 1))
        ]),
        testing.create_schedule(testing.create_team('3'), [
            testing.away_game('1', result=(2, 10)),
            testing.away_game('3', result=(1, 6))
        ])
    ]

    ratings, hfa = predict.calculate_ratings(schedules)

    self.assertGreater(ratings['1']['overall'], ratings['2']['overall'])
    self.assertGreater(ratings['2']['overall'], ratings['3']['overall'])
