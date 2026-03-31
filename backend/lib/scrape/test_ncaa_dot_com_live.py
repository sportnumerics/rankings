"""
Live integration test for NCAA.com scraper.
Fetches real data from NCAA.com to verify scraper works.

Run with: uv run python -m lib.scrape.test_ncaa_dot_com_live
"""

import unittest
from .ncaa_dot_com import NcaaDotCom
import requests


class TestNcaaDotComLive(unittest.TestCase):
    """Live tests against real NCAA.com - may be slow"""
    
    def setUp(self):
        self.scraper = NcaaDotCom()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def test_fetch_goals_leaders(self):
        """Fetch real goals per game leaders from NCAA.com"""
        url = self.scraper.get_stat_leaders_url('lacrosse-men', 'd1', 'individual', 'goals_per_game')
        print(f"\nFetching: {url}")
        
        resp = self.session.get(url, timeout=10)
        self.assertEqual(resp.status_code, 200)
        
        results = self.scraper.parse_individual_stats_html(resp.text, 'lacrosse-men', 'd1', 'goals_per_game')
        
        print(f"Found {len(results)} players")
        self.assertGreater(len(results), 0, "Should have at least one player")
        
        # Print top 5
        for i, player in enumerate(results[:5]):
            print(f"  {player['rank']}. {player['player_name']} ({player['school']}) - {player['per_game']} GPG")
        
        # Validate structure
        first = results[0]
        self.assertIn('player_name', first)
        self.assertIn('school', first)
        self.assertIn('per_game', first)
        self.assertIsInstance(first['per_game'], float)
        self.assertGreater(first['per_game'], 0)
    
    def test_fetch_assists_leaders(self):
        """Fetch assists per game leaders"""
        url = self.scraper.get_stat_leaders_url('lacrosse-men', 'd1', 'individual', 'assists_per_game')
        print(f"\nFetching: {url}")
        
        resp = self.session.get(url, timeout=10)
        self.assertEqual(resp.status_code, 200)
        
        results = self.scraper.parse_individual_stats_html(resp.text, 'lacrosse-men', 'd1', 'assists_per_game')
        
        print(f"Found {len(results)} players")
        self.assertGreater(len(results), 0)
        
        for i, player in enumerate(results[:5]):
            print(f"  {player['rank']}. {player['player_name']} ({player['school']}) - {player['per_game']} APG")
    
    def test_fetch_saves_leaders(self):
        """Fetch saves per game leaders"""
        url = self.scraper.get_stat_leaders_url('lacrosse-men', 'd1', 'individual', 'saves_per_game')
        print(f"\nFetching: {url}")
        
        resp = self.session.get(url, timeout=10)
        self.assertEqual(resp.status_code, 200)
        
        results = self.scraper.parse_individual_stats_html(resp.text, 'lacrosse-men', 'd1', 'saves_per_game')
        
        print(f"Found {len(results)} players")
        self.assertGreater(len(results), 0)
        
        for i, player in enumerate(results[:5]):
            print(f"  {player['rank']}. {player['player_name']} ({player['school']}) - {player['per_game']} SPG")
    
    def test_fetch_team_scoring_offense(self):
        """Fetch team scoring offense stats"""
        url = self.scraper.get_stat_leaders_url('lacrosse-men', 'd1', 'team', 'scoring_offense')
        print(f"\nFetching: {url}")
        
        resp = self.session.get(url, timeout=10)
        self.assertEqual(resp.status_code, 200)
        
        results = self.scraper.parse_team_stats_html(resp.text, 'lacrosse-men', 'd1', 'scoring_offense')
        
        print(f"Found {len(results)} teams")
        self.assertGreater(len(results), 0)
        
        for i, team in enumerate(results[:5]):
            print(f"  {team['rank']}. {team['team_name']} - {team['per_game']} GPG")
    
    def test_verify_stats_ncaa_org_blocked(self):
        """Verify that stats.ncaa.org is still blocked"""
        print("\nVerifying stats.ncaa.org is blocked...")
        
        try:
            resp = self.session.get('https://stats.ncaa.org/teams/1', timeout=10)
            content = resp.text.lower()
            
            if 'access denied' in content or resp.status_code == 403:
                print("  ✓ Confirmed: stats.ncaa.org is blocked (Access Denied)")
            else:
                print(f"  ⚠ stats.ncaa.org returned status {resp.status_code}")
                print(f"    (May have been unblocked or our workaround is unnecessary)")
        except Exception as e:
            print(f"  ✗ Error checking stats.ncaa.org: {e}")


if __name__ == '__main__':
    print("=" * 70)
    print("NCAA.com Live Integration Test")
    print("Testing real data fetching from NCAA.com")
    print("=" * 70)
    unittest.main(verbosity=2)
