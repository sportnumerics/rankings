import subprocess
import os
import logging

LOGGER = logging.getLogger(__name__)


def sync(args):
    dry_run = ['--dryrun'] if args.dry_run else []
    input_path = os.path.join(args.input_dir, args.year)
    output_path = args.bucket_url + '/' + args.year
    LOGGER.info(f'Syncing {input_path} to {output_path}')
    subprocess.run([
        'aws', 's3', 'sync', input_path, output_path, '--delete', '--quiet',
        *dry_run
    ])
    LOGGER.info('Completed sync successfully.')
