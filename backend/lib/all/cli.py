from . import all
from datetime import datetime


def add_parsers(parsers):
  all_parser = parsers.add_parser('all', help='scrape and predict')
  all_parser.add_argument('--out-dir', default='out', help='Output directory')
  all_parser.add_argument('--bucket-url', help='S3 Bucket url')
  all_parser.add_argument(
      '--source',
      choices=all.ALL_SOURCES,
      action='append',
      default=[],
      help='add a source (mcla or ncaa) - or specify --all-sources to scrape')
  all_parser.add_argument('--all-sources',
                          action='store_true',
                          help='Scrape all available sources')
  all_parser.set_defaults(func=all.run)
