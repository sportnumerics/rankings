from . import scrape

def add_parsers(parsers):
  parser = parsers.add_parser('scrape', help='scrape stats from league websites')
  parser.add_argument('--source', choices=['ncaa','mcla'], help='league source')
  parser.add_argument('--year', help='year to fetch (defaults to current year)')
  parser.add_argument('--out-dir', default='out', help='output directory')
  parser.set_defaults(func=scrape.scrape)
