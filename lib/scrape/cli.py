def run(args):
  print(f'stats with args {args}')

def add_parsers(parsers):
  parser = parsers.add_parser('scrape', help='scrape stats from league websites')
  parser.add_argument('--source', choices=['ncaa','mcla'], help='league source')
  parser.add_argument('--year', default='latest', help='year to fetch')
  parser.add_argument('--team', default='all', help='team to fetch')
  parser.set_defaults(func=run)
