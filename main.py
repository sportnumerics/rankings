import argparse
import lib.scrape.cli
import lib.predict.cli
import lib.render.cli


def main():
  parser = argparse.ArgumentParser(description='Sportnumerics core')
  subparsers = parser.add_subparsers()
  parser.set_defaults(func=lambda args: parser.print_help())
  lib.scrape.cli.add_parsers(subparsers)
  lib.predict.cli.add_parsers(subparsers)
  lib.render.cli.add_parsers(subparsers)
  args = parser.parse_args()
  args.func(args)

if __name__ == "__main__":
  main()
