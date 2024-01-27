from . import sync
from datetime import datetime


def add_parsers(parsers):
  sync_parser = parsers.add_parser('sync', help='sync to s3')
  sync_parser.add_argument('--input-dir',
                           default='out',
                           help='Local directory to sync')
  sync_parser.add_argument(
      '--bucket-url',
      help='Output bucket path (e.g. s3://<bucket-name>/<path>)')
  sync_parser.add_argument('--dry-run',
                           action='store_true',
                           help='Performs a dry-run of the sync')
  sync_parser.set_defaults(func=sync.sync)
