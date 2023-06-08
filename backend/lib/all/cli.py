from . import all
from datetime import datetime

def add_parsers(parsers):
  all_parser = parsers.add_parser('all', help='scrape, predict and render')
  all_parser.add_argument('--year', default=str(datetime.now().year), help='Year to run')
  all_parser.add_argument('--out-dir', default='out', help='Output directory')
  all_parser.add_argument('--source', choices=['ncaa','mcla'], action='append', default=[], help='add a source (mcla or ncaa)')
  all_parser.set_defaults(func=all.run)
