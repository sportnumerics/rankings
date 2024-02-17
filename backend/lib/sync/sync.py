import subprocess
import os
import logging
from ..shared import shared

LOGGER = logging.getLogger(__name__)


def sync(args):
    dry_run = ['--dryrun'] if args.dry_run else []
    for year in shared.years(args.year):
        input_path = os.path.join(args.input_dir, year)
        output_path = args.bucket_url + '/' + year
        LOGGER.info(f'Syncing {input_path} to {output_path}')
        subprocess.run([
            'aws', 's3', 'sync', input_path, output_path, '--delete',
            '--quiet', *dry_run
        ])
        LOGGER.info('Completed sync successfully.')
