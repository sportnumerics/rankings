"""
Unit tests for Playwright fetcher.
"""

import asyncio
import unittest
import os
from unittest.mock import MagicMock, patch
from .playwright_fetcher import NcaaRateLimitCircuitOpen, PlaywrightFetcher


class TestPlaywrightFetcher(unittest.TestCase):
    
    @unittest.skipIf(os.environ.get('CI') == 'true', "Skip browser tests in CI (no Playwright browsers installed)")
    def test_fetch_stats_ncaa_org(self):
        """Test that Firefox can fetch from stats.ncaa.org"""
        url = 'https://stats.ncaa.org/team/inst_team_list?academic_year=2026&division=1&sport_code=MLA'
        
        with PlaywrightFetcher() as fetcher:
            html = fetcher.fetch(url)
            
            self.assertIsNotNone(html)
            self.assertIn('Air Force', html)  # First team alphabetically
            self.assertNotIn('Access Denied', html)

    @unittest.skipIf(os.environ.get('CI') == 'true', "Skip browser tests in CI (no Playwright browsers installed)")
    def test_fetch_ncaa_individual_stats_page(self):
        """Test that live NCAA individual stats pages fetch successfully."""
        url = 'https://stats.ncaa.org/contests/6520729/individual_stats'

        with PlaywrightFetcher() as fetcher:
            html = fetcher.fetch(url)

            self.assertIsNotNone(html)
            self.assertIn('dataTable', html)
            self.assertNotIn('Access Denied', html)
    
    def test_detects_queue_full_html_as_retryable(self):
        fetcher = PlaywrightFetcher()
        self.assertTrue(fetcher._is_blocked_or_busy_html(
            "<html><body><h2>This website is under heavy load (queue full)</h2></body></html>"
        ))
        self.assertTrue(fetcher._is_blocked_or_busy_html(
            "<html><body>Access Denied</body></html>"
        ))
        self.assertFalse(fetcher._is_blocked_or_busy_html(
            "<html><body><table class='dataTable'></table></body></html>"
        ))

    @patch('lib.scrape.playwright_fetcher.random.uniform', return_value=0.25)
    @patch('lib.scrape.playwright_fetcher.time.sleep')
    @patch('lib.scrape.playwright_fetcher.time.monotonic')
    def test_wait_before_fetch_respects_min_delay(self, monotonic, sleep,
                                                  _uniform):
        fetcher = PlaywrightFetcher(min_delay_seconds=4.0)
        fetcher._last_fetch_at = 10.0
        monotonic.return_value = 12.5

        fetcher._wait_before_fetch()

        sleep.assert_called_once_with(1.75)

    @patch.dict(os.environ, {'NCAA_FETCH_DELAY_SECONDS': '7.5'})
    def test_default_delay_comes_from_environment(self):
        fetcher = PlaywrightFetcher()
        self.assertEqual(fetcher.min_delay_seconds, 7.5)

    @patch.dict(os.environ, {'NCAA_FETCH_DELAY_SECONDS': '-1'})
    def test_negative_default_delay_is_rejected(self):
        with self.assertRaisesRegex(ValueError,
                                    'NCAA_FETCH_DELAY_SECONDS must be non-negative'):
            PlaywrightFetcher()

    @patch.dict(os.environ, {'NCAA_FETCH_DELAY_SECONDS': 'nan'})
    def test_non_finite_default_delay_is_rejected(self):
        with self.assertRaisesRegex(ValueError,
                                    'NCAA_FETCH_DELAY_SECONDS must be finite'):
            PlaywrightFetcher()

    def test_non_finite_direct_delay_is_rejected(self):
        for delay in (float('nan'), float('inf')):
            with self.subTest(delay=delay):
                with self.assertRaisesRegex(ValueError,
                                            'NCAA_FETCH_DELAY_SECONDS must be finite'):
                    PlaywrightFetcher(min_delay_seconds=delay)

    @patch.dict(os.environ, {'NCAA_MAX_CONSECUTIVE_BLOCKS': '0'})
    def test_non_positive_block_limit_is_rejected(self):
        with self.assertRaisesRegex(ValueError,
                                    'NCAA_MAX_CONSECUTIVE_BLOCKS must be positive'):
            PlaywrightFetcher()

    @patch('lib.scrape.playwright_fetcher.time.monotonic', return_value=10.0)
    def test_repeated_blocks_open_circuit_and_extend_cooldown(self, _monotonic):
        fetcher = PlaywrightFetcher(max_consecutive_blocked_fetches=2)

        fetcher._record_blocked_fetch_failure()
        self.assertEqual(fetcher._blocked_until, 30.0)

        with self.assertRaises(NcaaRateLimitCircuitOpen):
            fetcher._record_blocked_fetch_failure()

        self.assertEqual(fetcher._blocked_until, 50.0)

    @patch('lib.scrape.playwright_fetcher.time.monotonic', return_value=10.0)
    def test_non_blocked_failure_resets_block_streak(self, _monotonic):
        fetcher = PlaywrightFetcher(max_consecutive_blocked_fetches=2)

        fetcher._record_blocked_fetch_failure()
        fetcher._record_non_blocked_fetch_failure()
        fetcher._record_blocked_fetch_failure()

        self.assertEqual(fetcher._consecutive_blocked_fetches, 1)
        self.assertEqual(fetcher._blocked_until, 30.0)

    def test_fetch_multiple_propagates_circuit_open(self):
        fetcher = PlaywrightFetcher()
        fetcher.fetch = MagicMock(side_effect=NcaaRateLimitCircuitOpen(
            'NCAA rate-limit circuit opened'))

        with self.assertRaises(NcaaRateLimitCircuitOpen):
            fetcher.fetch_multiple(['https://stats.ncaa.org/teams/594020'])

    def test_navigation_timeout_resets_block_streak(self):
        class FakePage:
            def __init__(self):
                self.outcomes = [
                    (200, '<html>Access Denied</html>'),
                    TimeoutError('navigation timed out'),
                    (200, '<html>Access Denied</html>'),
                ]

            async def goto(self, *_args, **_kwargs):
                outcome = self.outcomes.pop(0)
                if isinstance(outcome, Exception):
                    raise outcome
                self.html = outcome[1]
                return type('Response', (), {'status': outcome[0]})()

            async def content(self):
                return self.html

        fetcher = PlaywrightFetcher(min_delay_seconds=0,
                                    max_attempts=1,
                                    max_consecutive_blocked_fetches=2)
        fetcher.page = FakePage()
        fetcher._loop = asyncio.new_event_loop()
        fetcher._wait_before_fetch = MagicMock()
        try:
            with self.assertRaisesRegex(Exception, 'blocked or queue-full html'):
                fetcher.fetch('https://stats.ncaa.org/first')
            with self.assertRaises(TimeoutError):
                fetcher.fetch('https://stats.ncaa.org/second')
            with self.assertRaisesRegex(Exception, 'blocked or queue-full html'):
                fetcher.fetch('https://stats.ncaa.org/third')
        finally:
            fetcher._loop.close()

        self.assertEqual(fetcher._consecutive_blocked_fetches, 1)

    @unittest.skipIf(os.environ.get('CI') == 'true', "Skip browser tests in CI (no Playwright browsers installed)")
    def test_context_manager(self):
        """Test context manager properly initializes and cleans up"""
        with PlaywrightFetcher() as fetcher:
            self.assertIsNotNone(fetcher.page)
            self.assertIsNotNone(fetcher.browser)
        
        # After exit, browser should be closed
        # (Can't easily assert this without accessing internals)


if __name__ == '__main__':
    unittest.main()
