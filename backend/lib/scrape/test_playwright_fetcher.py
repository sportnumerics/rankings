"""
Unit tests for Playwright fetcher.
"""

import unittest
import os
from unittest.mock import patch
from .playwright_fetcher import PlaywrightFetcher


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
