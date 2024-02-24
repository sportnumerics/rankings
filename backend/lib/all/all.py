from dataclasses import dataclass

from ..shared.types import PredictArgs, ScrapeArgs, SyncArgs
from ..scrape import scrape
from ..predict import predict
from ..sync import sync
from ..shared import shared
import logging

ALL_SOURCES = ['mcla', 'ncaa']
LOGGER = logging.getLogger(__name__)


def run(args):
    sources = ALL_SOURCES if args.all_sources else args.source

    for year in shared.years(args.year):
        for source in sources:
            scrape.scrape_schedules(
                ScrapeArgs(source=source, year=year, out_dir=args.out_dir))

        predict.predict(
            PredictArgs(input_dir=args.out_dir,
                        year=year,
                        out_dir=args.out_dir))

        if args.bucket_url:
            sync.sync(
                SyncArgs(input_dir=args.out_dir,
                         year=year,
                         bucket_url=args.bucket_url,
                         dry_run=False))
        else:
            LOGGER.info(
                "Skipping sync with S3 since no bucket url was specified")
