from . import ncaa, mcla
import requests
import requests_cache
from datetime import datetime, timedelta
import json
import os
import pathlib

USER_AGENT='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'

def scrape(args):
  if args.source == 'ncaa':
    scraper = ncaa.Ncaa()
  elif args.source == 'mcla':
    scraper = mcla.Mcla()
  else:
    raise Exception(f'Unimplemented source {args.source}')
  source = args.source

  if args.year:
    year = str(args.year)
  else:
    year = str(datetime.now().year)

  out_dir = args.out_dir
  pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
  requests_cache.install_cache(cache_name=os.path.join(out_dir, 'cache'), expire_after=timedelta(days=1))

  teams = scrape_teams(scraper, year, out_dir)

  with open(os.path.join(out_dir, f'{source}-{year}-teams.json'), 'w') as f:
    json.dump(list(teams), f)


def scrape_teams(scraper, year, out_dir):
  for url in scraper.get_team_list_urls(year):
    html = requests.get(url['url'],params=url.get('params'),headers={'user-agent': USER_AGENT}).text
    try:
      yield from scraper.convert_team_list_html(html, url)
    except Exception as e:
      print(f'Unable to parse html from {url}: {e}')
      with open(os.path.join(out_dir, 'error.html'), 'w') as f:
        f.write(html)
