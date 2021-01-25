from . import scrape


def add_parsers(parsers):
  scrape_parser = parsers.add_parser('scrape',
                                     help='scrape stats from league websites')
  scrape_parser.add_argument('--source',
                             choices=['ncaa', 'mcla'],
                             help='league source')
  scrape_parser.add_argument('--year',
                             help='year to fetch (defaults to current year)')
  scrape_parser.add_argument('--out-dir',
                             default='out',
                             help='output directory')

  scrape_subparsers = scrape_parser.add_subparsers()

  team_parser = scrape_subparsers.add_parser('teams', help='scrape team lists')
  team_parser.set_defaults(func=scrape.scrape_team_list)

  schedule_parser = scrape_subparsers.add_parser('schedules',
                                                 help='scrape team schedules')
  schedule_parser.add_argument(
      '--team-list-file',
      help='File to read team list from (will scrape them by default)')
  schedule_parser.set_defaults(func=scrape.scrape_schedules)
