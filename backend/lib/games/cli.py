from . import games


def add_parsers(parsers):
    games_parser = parsers.add_parser('games', help='generate games.json from schedules')
    games_parser.add_argument('--input-dir',
                             default='out',
                             help='Directory containing schedule files')
    games_parser.set_defaults(func=games.generate_games_file)
