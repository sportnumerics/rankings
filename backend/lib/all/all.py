
from ..shared.types import PredictArgs, ScrapeArgs, SyncArgs
from ..scrape import scrape
from ..predict import predict
from ..games import games
from ..sync import sync
from ..shared import shared
import logging

ALL_SOURCES = ['mcla', 'ncaa']
LOGGER = logging.getLogger(__name__)


def run(args):
    sources = ALL_SOURCES if args.all_sources else args.source

    for year in shared.years(args.year):
        for source in sources:
            scrape_args = ScrapeArgs(source=source, year=year, out_dir=args.out_dir)
            if args.limit:
                scrape_args.limit = args.limit
                LOGGER.info(f"Limiting scrape to {args.limit} teams per source")
            
            scrape.scrape_schedules(scrape_args)

        predict.predict(
            PredictArgs(input_dir=args.out_dir,
                        year=year,
                        out_dir=args.out_dir))

        # Generate consolidated games file
        games.generate_games_file(
            type('GamesArgs', (), {'year': year, 'input_dir': args.out_dir})())

        if args.bucket_url:
            sync.sync(
                SyncArgs(input_dir=args.out_dir,
                         year=year,
                         bucket_url=args.bucket_url,
                         dry_run=False))
        else:
            LOGGER.info(
                "Skipping sync with S3 since no bucket url was specified")
