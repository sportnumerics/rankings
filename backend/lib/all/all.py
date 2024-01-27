from dataclasses import dataclass

from ..scrape import scrape
from ..predict import predict
from ..sync import sync

ALL_SOURCES = ['mcla', 'ncaa']


def run(args):
  sources = ALL_SOURCES if args.all_sources else args.source

  for source in sources:
    scrape.scrape_schedules(
        ScrapeArgs(source=source, year=args.year, out_dir=args.out_dir))

  predict.predict(
      PredictArgs(input_dir=args.out_dir, year=args.year,
                  out_dir=args.out_dir))

  if args.bucket_url:
    sync.sync(
        SyncArgs(input_dir=args.out_dir,
                 year=args.year,
                 bucket_url=args.bucket_url,
                 dry_run=False))
  else:
    print("Skipping sync with S3 since no bucket url was specified")


@dataclass
class ScrapeArgs:
  source: str
  year: str
  out_dir: str


@dataclass
class PredictArgs:
  input_dir: str
  year: str
  out_dir: str


@dataclass
class SyncArgs:
  input_dir: str
  year: str
  bucket_url: str
  dry_run: str
