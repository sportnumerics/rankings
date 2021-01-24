import os
import json
from scipy.sparse import coo_matrix
from scipy.sparse import linalg
import numpy as np
import pathlib
from datetime import datetime


def predict(args):
  out_dir = args.out_dir
  if args.year:
    year = args.year
  else:
    year = datetime.now().year

  schedules_dir = os.path.join(args.input_dir, year, 'schedules')
  _, _, filenames = next(os.walk(schedules_dir))

  schedules = load_schedules(map(lambda f: os.path.join(schedules_dir, f), filenames))

  ratings, hfa = calculate_ratings(schedules)

  sorted_ratings = sorted(ratings.values(), key=lambda r: -r['overall'])

  pathlib.Path(os.path.join(out_dir, year)).mkdir(parents=True, exist_ok=True)
  with open(os.path.join(out_dir, year, 'team-ratings.json'), 'w') as f:
    json.dump(sorted_ratings, f, indent=2)

def load_schedules(filenames):
  for file in filenames:
    with open(file) as f:
      yield json.load(f)

def calculate_ratings(schedules):
  game_map = {}
  for schedule in schedules:
    for game in schedule['games']:
      if 'result' not in game:
        continue
      team_id = schedule['team']['id']
      opponent_id = game['opponent']['id']
      gid = game_id(team_id, opponent_id, game['date'])
      g = {
        'team': team_id,
        'opponent': opponent_id,
        'home': game['home'],
        'points_for': game['result']['points_for'],
        'points_against': game['result']['points_against']
      }
      game_map[gid] = g

  games = game_map.values()

  team_map = build_team_map(games)
  n_teams = len(team_map['indicies_to_teams'])
  offset = len(team_map['ids_to_indicies'])

  coefficients = build_offensive_defensive_coefficient_matrix(games, team_map)

  constants = build_offensive_defensive_constants(games, team_map)

  raw_ratings, istop, itn, r1norm, r2norm, anorm, acond, arnorm, xnorm, var = linalg.lsqr(coefficients, constants, damp=0.2)

  overall = raw_ratings[0:n_teams] + raw_ratings[offset:n_teams+offset]
  hfa = raw_ratings[2*n_teams]

  results = {}
  for i in range(0, n_teams):
    team = team_map['indicies_to_teams'][i]
    results[team] = {
      'team': team,
      'offense': raw_ratings[i],
      'defense': raw_ratings[i+offset],
      'overall': overall[i],
    }

  return results, hfa

def build_team_map(games):
  ids_to_indicies = {}
  indicies_to_teams = {}

  def add_team_if_necessary(team_id):
    if (team_id not in ids_to_indicies):
      index = len(indicies_to_teams)
      ids_to_indicies[team_id] = index
      indicies_to_teams[index] = team_id

  for game in games:
    team_id = game['team']
    opponent_id = game['opponent']
    add_team_if_necessary(team_id)
    add_team_if_necessary(opponent_id)

  return {
    'ids_to_indicies': ids_to_indicies,
    'indicies_to_teams': indicies_to_teams
  }

def build_offensive_defensive_coefficient_matrix(games, team_map):
  ids_to_indicies = team_map['ids_to_indicies']

  hfa_factors = [hfa for g in games for hfa in ((1, -1) if g['home'] else (-1, 1))]
  hfa_i = [i for i in range(0, 2*len(games))]
  hfa_j = [2*len(ids_to_indicies)]*(2*len(games))

  data = [1, -1, 1, -1]*len(games)
  i = [i for g in range(0, 2*len(games)) for i in (g, g)]

  def offensive_offset(id):
    return ids_to_indicies[id]

  def defensive_offset(id):
    return len(ids_to_indicies) + ids_to_indicies[id]

  j = [k for game in games
    for k in (
      offensive_offset(game['team']),
      defensive_offset(game['opponent']),
      offensive_offset(game['opponent']),
      defensive_offset(game['team']))]

  return coo_matrix((data + hfa_factors, (i + hfa_i, j + hfa_j)), shape=(2*len(games), 2*len(ids_to_indicies)+1))

def build_offensive_defensive_constants(games, team_map):
  return np.array([
    p for g in games
    for p in (g['points_for'], g['points_against'])
  ])

def game_id(team_id, opponent_id, date):
  if team_id < opponent_id:
    return f'{team_id}_{opponent_id}_{date}'
  else:
    return f'{opponent_id}_{team_id}_{date}'
