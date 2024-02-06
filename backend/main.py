import os
import datetime
import argparse
import logging
import lib.scrape.cli
import lib.predict.cli
import lib.sync.cli
import lib.all.cli


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Sportnumerics core')
    parser.add_argument(
        '--year',
        default=get_default_year(),
        help='year(s) to fetch (defaults to environment variable YEAR or current year). Range expression e.g. 2008-2022 is possible'
    )
    subparsers = parser.add_subparsers()
    parser.set_defaults(func=lambda args: parser.print_help())
    lib.scrape.cli.add_parsers(subparsers)
    lib.predict.cli.add_parsers(subparsers)
    lib.sync.cli.add_parsers(subparsers)
    lib.all.cli.add_parsers(subparsers)
    args = parser.parse_args()
    args.func(args)


def get_default_year():
    return os.environ.get("YEAR") or str(datetime.datetime.now().year)


if __name__ == "__main__":
    main()
