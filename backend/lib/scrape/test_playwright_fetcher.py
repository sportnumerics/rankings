"""
Unit tests for Playwright fetcher.
"""

import unittest
import os
from .playwright_fetcher import PlaywrightFetcher


class TestPlaywrightFetcher(unittest.TestCase):
    
    def test_fetch_stats_ncaa_org(self):
        """Test that Firefox can fetch from stats.ncaa.org"""
        # Skip in CI environments that may have asyncio issues or no browser
        if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
            self.skipTest('Skipping Playwright test in CI environment')
        
        url = 'https://stats.ncaa.org/team/inst_team_list?academic_year=2026&division=1&sport_code=MLA'
        
        with PlaywrightFetcher() as fetcher:
            html = fetcher.fetch(url)
            
            self.assertIsNotNone(html)
            self.assertIn('Air Force', html)  # First team alphabetically
            self.assertNotIn('Access Denied', html)
    
    def test_context_manager(self):
        """Test context manager properly initializes and cleans up"""
        # Skip in CI environments
        if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
            self.skipTest('Skipping Playwright test in CI environment')
        
        with PlaywrightFetcher() as fetcher:
            self.assertIsNotNone(fetcher.page)
            self.assertIsNotNone(fetcher.browser)
        
        # After exit, browser should be closed
        # (Can't easily assert this without accessing internals)


if __name__ == '__main__':
    unittest.main()
