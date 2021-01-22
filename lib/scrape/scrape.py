from . import ncaa, mcla
import requests
import requests_cache
from datetime import datetime, timedelta
import json
import os
import pathlib
import fileinput

USER_AGENT='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'

def scrape_team_list(args):
  runner = ScrapeRunner(args)

  runner.scrape_and_write_team_lists()

def scrape_schedules(args):
  runner = ScrapeRunner(args)

  if not args.team_list_file:
    runner.scrape_and_write_team_lists()
    team_list_file = runner.get_team_list_filename()
  else:
    team_list_file = args.team_list_file

  runner.scrape_and_write_schedules(team_list_file)

class ScrapeRunner():
  def __init__(self, args):
    if args.source == 'ncaa':
      self.scraper = ncaa.Ncaa()
    elif args.source == 'mcla':
      self.scraper = mcla.Mcla()
    else:
      raise Exception(f'Unimplemented source {args.source}')
    self.source = args.source

    if args.year:
      self.year = str(args.year)
    else:
      self.year = str(datetime.now().year)

    self.out_dir = args.out_dir

    self.cache = requests_cache.CachedSession(cache_name=os.path.join(self.out_dir, 'cache'), expire_after=timedelta(days=1))

  def scrape_and_write_team_lists(self):
    teams = self.scrape_teams()

    pathlib.Path(self.out_dir).mkdir(parents=True, exist_ok=True)
    with open(self.get_team_list_filename(), 'w') as f:
      json.dump(list(teams), f, indent=2)

  def scrape_and_write_schedules(self, team_list_file):
    with open(team_list_file) as f:
      teams = json.load(f)

    schedule_dir = os.path.join(self.out_dir, self.year, 'schedules')
    pathlib.Path(schedule_dir).mkdir(parents=True, exist_ok=True)
    for team in teams:
      schedule = self.scrape_schedule(team)
      with open(os.path.join(schedule_dir, team['id'] + '.json'), 'w') as f:
        json.dump(schedule, f, indent=2)

  def scrape_teams(self):
    for url in self.scraper.get_team_list_urls(self.year):
      html = self.fetch(url)
      try:
        yield from self.scraper.convert_team_list_html(html, url)
      except Exception as e:
        print(f'Unable to convert team list html from {url}: {e}')
        with open(os.path.join(self.out_dir, 'error.html'), 'w') as f:
          f.write(html)

  def scrape_schedule(self, team):
    location = team['schedule_location']
    html = self.fetch(location)
    try:
      return self.scraper.convert_schedule_html(html, team)
    except Exception as e:
      print(f'Unable to convert schedule html from {location}: {e}')

  def fetch(self, location):
    return self.cache.get(location['url'],params=location.get('params'),headers={'user-agent': USER_AGENT}).text

  def get_team_list_filename(self):
    return os.path.join(self.out_dir, f'{self.source}-{self.year}-teams.json')