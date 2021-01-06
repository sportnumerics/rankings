import os

def ncaa_team_list():
  return load_fixture('ncaa_team_list.html')

def mcla_team_list():
  return load_fixture('mcla_team_list.html')

def load_fixture(filename):
  d = os.path.dirname(__file__)
  with open(os.path.join(d, filename)) as f:
    return f.read()