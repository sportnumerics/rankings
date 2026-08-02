import unittest
from unittest.mock import patch

from .sync import sync


class TestSync(unittest.TestCase):

    @patch('lib.sync.sync.subprocess.run')
    @patch('lib.sync.sync.shared.years', return_value=['2026'])
    def test_sync_checks_aws_exit_status(self, _years, run):
        sync(type('Args', (), {
            'input_dir': 'out',
            'year': '2026',
            'bucket_url': 's3://rankings',
            'dry_run': False,
        })())

        self.assertEqual(run.call_args.kwargs, {'check': True})


if __name__ == '__main__':
    unittest.main()
