from datetime import datetime
from functools import reduce
import pathlib
import jinja2
import json
import math
import os
import re


def render(args):
  if args.year:
    year = args.year
  else:
    year = datetime.now().year
  out_dir = args.out_dir

  year_dir = os.path.join(args.input_dir, year)

  ratings = extract_ratings(year_dir)

  teams = extract_teams(year_dir)

  schedules = extract_schedules(year_dir)

  team_lists = create_team_lists(ratings, teams, schedules)

  env = jinja2.Environment(loader=jinja2.PackageLoader('lib.render'))
  template = env.get_template('teams.html')

  for uri, teams in team_lists.items():
    div_dir = os.path.join(out_dir, 'html', *uri.split('/'))
    pathlib.Path(div_dir).mkdir(parents=True, exist_ok=True)
    teams_html = template.render(teams)
    with open(os.path.join(div_dir, 'index.html'), 'w') as f:
      f.write(teams_html)

def extract_ratings(year_dir):
  with open(os.path.join(year_dir, 'team-ratings.json')) as f:
    return json.load(f)

def extract_teams(year_dir):
  _, _, filenames = next(os.walk(year_dir))
  for file in filenames:
    teams_match = re.match(r'(?P<source>\w+)\-teams\.json', file)
    if teams_match:
      source = teams_match.group('source')
      with open(os.path.join(year_dir, file)) as f:
        yield json.load(f)

def extract_schedules(year_dir):
  schedule_dir = os.path.join(year_dir, 'schedules')
  _, _, filenames = next(os.walk(schedule_dir))
  for file in filenames:
    with open(os.path.join(schedule_dir, file)) as f:
      yield json.load(f)

def create_team_lists(ratings, teams, schedules):
  ratings_dict = {r['team']: r for r in ratings}
  schedule_dict = {s['team']['id']: s for s in schedules}

  team_lists = {}
  for tl in teams:
    for t in tl:
      tid = t['id']
      year = t['year']
      source = t['source']
      sport = t['sport']
      div = t['div']
      uri = f'/{year}/{sport}/{source}/{div}'
      div = team_lists.setdefault(uri, {
        'div': div,
        'year': year,
        'teams': []
      })
      team = {
        'name': t['name'],
        'id': tid
      }

      ratings = ratings_dict.get(tid)
      if ratings:
        team['overall'] = ratings['overall']
        team['offense'] = ratings['offense']
        team['defense'] = ratings['defense']

      schedule = schedule_dict.get(tid)
      if schedule:
        team['wins'] = sum(map(is_win, schedule['games']))
        team['losses'] = sum(map(is_loss, schedule['games']))
        team['ties'] = sum(map(is_tie, schedule['games']))

      div['teams'].append(team)

  for div in team_lists.values():
    div['teams'].sort(key=lambda t: -t['overall'] if 'overall' in t else math.inf)

  return team_lists

def is_win(game):
  return 'result' in game and game['result']['points_for'] > game['result']['points_against']

def is_loss(game):
  return 'result' in game and game['result']['points_for'] < game['result']['points_against']

def is_tie(game):
  return 'result' in game and game['result']['points_for'] == game['result']['points_against']
