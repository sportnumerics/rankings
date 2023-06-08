from datetime import datetime

def create_team(team_id,
                name=None,
                sport='ml',
                source='mcla',
                div='1',
                year=2020):
  if not name:
    name = team_id
  return {
      'name': name,
      'year': year,
      'id': team_id,
      'div': div,
      'sport': sport,
      'source': source
  }


def create_schedule(team, games):
  return {'team': team, 'games': games}


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
      'date': '2020-01-31T13:00:00'
  }
  if result:
    game['result'] = {'points_for': result[0], 'points_against': result[1]}
  return game


def create_rating(team_id, ratings):
  overall, offense, defense = ratings
  return {
      'team': team_id,
      'overall': overall,
      'offense': offense,
      'defense': defense
  }
