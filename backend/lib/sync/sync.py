import subprocess
import os


def sync(args):
  dry_run = ['--dryrun'] if args.dry_run else []
  input_path = os.path.join(args.input_dir, args.year)
  output_path = args.bucket_url + '/' + args.year
  subprocess.run([
      'aws', 's3', 'sync', input_path, output_path, '--delete', '--quiet',
      *dry_run
  ])
