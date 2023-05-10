from watchdog.events import FileSystemEventHandler, LoggingEventHandler
from watchdog.observers import Observer
from datetime import datetime
from functools import partial
from shutil import copyfile
import http.server
import pathlib
import signal
import jinja2
import json
import time
import math
import os
import re


def render(args):
  year = args.year
  out_dir = args.out_dir

  year_dir = os.path.join(args.input_dir, year)

  ratings = extract_ratings(year_dir)

  teams = extract_teams(year_dir)

  schedules = extract_schedules(year_dir)

  team_lists = create_team_lists(ratings, teams, schedules)

  env = jinja2.Environment(loader=jinja2.PackageLoader('lib.render'))

  rebuild_all(team_lists, out_dir, env)
  if hasattr(args, 'serve') and args.serve:
    server_pid = os.fork()
    if server_pid == 0:
      start_server(args.port, out_dir)
    else:
      watch_templates_and_rebuild_on_changes(team_lists, out_dir, env)
    os.kill(server_pid, signal.SIGINT)
    os.waitpid(server_pid, 0)


def start_server(port, out_dir):
  httpd = http.server.HTTPServer(
          ('', port),
          partial(http.server.SimpleHTTPRequestHandler,
                  directory=os.path.join(out_dir, 'html')))
  print(f'listening on {port}')
  httpd.serve_forever()


def watch_templates_and_rebuild_on_changes(team_lists, out_dir, env):
  class Watcher(FileSystemEventHandler):
    def on_any_event(self, event):
      rebuild_all(team_lists, out_dir, env)

  observer = Observer()
  script_dir = os.path.dirname(__file__)
  templates_dir = os.path.join(script_dir, 'templates')
  static_dir = os.path.join(script_dir, 'static')
  watcher = Watcher()
  observer.schedule(watcher, templates_dir, recursive=True)
  observer.schedule(watcher, static_dir, recursive=True)
  observer.start()
  print(f'waiting on file changes in {templates_dir}')
  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    observer.stop()
  observer.join()


def rebuild_all(team_lists, out_dir, env):
  render_team_lists(team_lists, out_dir, env)
  render_teams(team_lists, out_dir, env)
  render_styles(out_dir, env)
  render_static(out_dir)


def extract_ratings(year_dir):
  with open(os.path.join(year_dir, 'team-ratings.json')) as f:
    return json.load(f)


def extract_teams(year_dir):
  _, _, filenames = next(os.walk(year_dir))
  for file in filenames:
    teams_match = re.match(r'(?P<source>\w+)\-teams\.json', file)
    if teams_match:
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
    for team in tl:
      year = team['year']
      source = team['source']
      sport = team['sport']
      div_id = team['div']
      uri = uri_for_div(year=year, source=source, sport=sport, div=div_id)
      uri_for_year = partial(uri_for_div, source=source, sport=sport, div=div_id)
      div = team_lists.setdefault(uri, dict(div=div_id, year=year, uri_for_div=uri_for_div, uri_for_year=uri_for_year, teams=[]))

      add_team_to_div(team, div, ratings_dict, schedule_dict)

  for div in team_lists.values():
    div['teams'].sort(
        key=lambda t: -t['overall'] if 'overall' in t else math.inf)

  return team_lists


def add_team_to_div(team, div, ratings_dict, schedule_dict):
  tid = team['id']
  name = team['name']
  year = team['year']
  source = team['source']
  sport = team['sport']
  div_id = team['div']
  team = dict(name=name, id=tid, year=year)

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
    team['games'] = list(map(partial(enrich_game, tid=tid, ratings=ratings_dict, schedules=schedule_dict), schedule['games']))

  team['uri_for_year'] = partial(uri_for_team, sport=sport, source=source, div=div_id, team_id=tid)
  team['uri_for_div'] = uri_for_div

  div['teams'].append(team)


def enrich_game(game, tid, ratings, schedules):
  enriched_game = {
    **game,
    'date': datetime.fromisoformat(game['date']) if isinstance(game['date'], str) else game['date'],
  }
  opp_id = game['opponent']['id']
  opp_ratings = ratings.get(opp_id)
  team_ratings = ratings.get(tid)
  if opp_ratings and team_ratings:
    enriched_game['predicted_points_for'] = team_ratings['offense'] - opp_ratings['defense']
    enriched_game['predicted_points_against'] = opp_ratings['offense'] - team_ratings['defense']
  opp_schedule = schedules.get(opp_id)
  if opp_schedule:
    opp_team = opp_schedule['team']
    year = opp_team['year']
    sport = opp_team['sport']
    source = opp_team['source']
    div = opp_team['div']
    enriched_game['opponent']['uri'] = uri_for_team(year=year, sport=sport, source=source, div=div, team_id=opp_id)
  return enriched_game


def render_team_lists(team_lists, out_dir, env):
  template = env.get_template('teams.html.jinja')

  for uri, teams in team_lists.items():
    div_dir = division_directory(out_dir, uri)
    pathlib.Path(div_dir).mkdir(parents=True, exist_ok=True)
    teams_html = template.render(teams)
    with open(os.path.join(div_dir, 'index.html'), 'w') as f:
      f.write(teams_html)


def render_teams(team_lists, out_dir, env):
  template = env.get_template('team.html.jinja')

  for uri, teams in team_lists.items():
    div_dir = division_directory(out_dir, uri)
    pathlib.Path(div_dir).mkdir(parents=True, exist_ok=True)
    for team in teams['teams']:
      tid = team['id']
      team_html = template.render(team)
      with open(os.path.join(div_dir, f'{tid}.html'), 'w') as f:
        f.write(team_html)


def render_styles(out_dir, env):
  template = env.get_template('style.css.jinja')
  css = template.render()
  with open(os.path.join(content_directory(out_dir), 'style.css'), 'w') as f:
    f.write(css)


def render_static(out_dir):
  static_dir = os.path.join(os.path.dirname(__file__), 'static')
  for dirpath, _, files in os.walk(static_dir):
    for file in files:
      rel_dir = os.path.relpath(dirpath, static_dir)
      target_dir = os.path.join(content_directory(out_dir), rel_dir)
      pathlib.Path(target_dir).mkdir(parents=True, exist_ok=True)
      copyfile(os.path.join(dirpath, file), os.path.join(target_dir, file))


def content_directory(out_dir):
  return os.path.join(out_dir, 'html')


def division_directory(out_dir, div_uri):
  return os.path.join(content_directory(out_dir), *div_uri.split('/'))


def is_win(game):
  return 'result' in game and game['result']['points_for'] > game['result'][
      'points_against']


def is_loss(game):
  return 'result' in game and game['result']['points_for'] < game['result'][
      'points_against']


def is_tie(game):
  return 'result' in game and game['result']['points_for'] == game['result'][
      'points_against']

def uri_for_team(year, sport, source, div, team_id):
  return f'/{year}/{sport}/{source}/{div}/{team_id}.html'

def uri_for_div(year, sport, source, div):
  return f'/{year}/{sport}/{source}/{div}/'
