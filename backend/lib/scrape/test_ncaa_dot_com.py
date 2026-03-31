"""
Unit tests for NCAA.com scraper.
"""

import unittest
from .ncaa_dot_com import NcaaDotCom


class TestNcaaDotCom(unittest.TestCase):
    
    def setUp(self):
        self.scraper = NcaaDotCom()
    
    def test_stat_url_construction(self):
        """Test URL building for different stats"""
        url = self.scraper.get_stat_leaders_url('lacrosse-men', 'd1', 'individual', 'goals_per_game')
        self.assertEqual(url, 'https://www.ncaa.com/stats/lacrosse-men/d1/current/individual/222')
        
        url = self.scraper.get_stat_leaders_url('lacrosse-men', 'd1', 'individual', 'assists_per_game')
        self.assertEqual(url, 'https://www.ncaa.com/stats/lacrosse-men/d1/current/individual/223')
        
        url = self.scraper.get_stat_leaders_url('lacrosse-men', 'd1', 'team', 'scoring_offense')
        self.assertEqual(url, 'https://www.ncaa.com/stats/lacrosse-men/d1/current/team/228')
    
    def test_parse_goals_leaders_html(self):
        """Test parsing goals per game leaderboard"""
        # Sample HTML from NCAA.com (simplified)
        html = '''
        <div class="block-stats">
            <table>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td>Luke McNamara</td>
                        <td><a href="/schools/utah">Utah</a></td>
                        <td>So.</td>
                        <td>ATT</td>
                        <td>8</td>
                        <td>34</td>
                        <td>4.25</td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td>Rory Connor</td>
                        <td><a href="/schools/georgetown">Georgetown</a></td>
                        <td>Sr.</td>
                        <td>ATT</td>
                        <td>7</td>
                        <td>29</td>
                        <td>4.14</td>
                    </tr>
                </tbody>
            </table>
        </div>
        '''
        
        results = self.scraper.parse_individual_stats_html(html, 'lacrosse-men', 'd1', 'goals_per_game')
        
        self.assertEqual(len(results), 2)
        
        # Check first player
        self.assertEqual(results[0]['rank'], '1')
        self.assertEqual(results[0]['player_name'], 'Luke McNamara')
        self.assertEqual(results[0]['school'], 'Utah')
        self.assertEqual(results[0]['class'], 'So.')
        self.assertEqual(results[0]['position'], 'ATT')
        self.assertEqual(results[0]['games'], 8)
        self.assertEqual(results[0]['total'], 34.0)
        self.assertEqual(results[0]['per_game'], 4.25)
        
        # Check second player
        self.assertEqual(results[1]['rank'], '2')
        self.assertEqual(results[1]['player_name'], 'Rory Connor')
        self.assertEqual(results[1]['school'], 'Georgetown')
        self.assertEqual(results[1]['per_game'], 4.14)
    
    def test_parse_team_stats_html(self):
        """Test parsing team stats (e.g., scoring offense)"""
        html = '''
        <div class="block-stats">
            <table>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td><a href="/schools/duke">Duke</a></td>
                        <td>16.89</td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td><a href="/schools/utah">Utah</a></td>
                        <td>15.89</td>
                    </tr>
                </tbody>
            </table>
        </div>
        '''
        
        results = self.scraper.parse_team_stats_html(html, 'lacrosse-men', 'd1', 'scoring_offense')
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['rank'], '1')
        self.assertEqual(results[0]['team_name'], 'Duke')
        self.assertEqual(results[0]['per_game'], 16.89)
        
        self.assertEqual(results[1]['rank'], '2')
        self.assertEqual(results[1]['team_name'], 'Utah')
        self.assertEqual(results[1]['per_game'], 15.89)
    
    def test_parse_empty_html(self):
        """Test handling of empty/invalid HTML"""
        html = '<div>No stats here</div>'
        results = self.scraper.parse_individual_stats_html(html, 'lacrosse-men', 'd1', 'goals_per_game')
        self.assertEqual(len(results), 0)
        
        results = self.scraper.parse_team_stats_html(html, 'lacrosse-men', 'd1', 'scoring_offense')
        self.assertEqual(len(results), 0)
    
    def test_malformed_row_handling(self):
        """Test that malformed rows don't crash parser"""
        html = '''
        <div class="block-stats">
            <table>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td>Good Player</td>
                        <td>Utah</td>
                        <td>So.</td>
                        <td>ATT</td>
                        <td>8</td>
                        <td>34</td>
                        <td>4.25</td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <!-- Missing columns -->
                    </tr>
                    <tr>
                        <td>3</td>
                        <td>Another Player</td>
                        <td>Duke</td>
                        <td>Jr.</td>
                        <td>MID</td>
                        <td>9</td>
                        <td>30</td>
                        <td>3.33</td>
                    </tr>
                </tbody>
            </table>
        </div>
        '''
        
        results = self.scraper.parse_individual_stats_html(html, 'lacrosse-men', 'd1', 'goals_per_game')
        
        # Should skip malformed row but parse valid ones
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['player_name'], 'Good Player')
        self.assertEqual(results[1]['player_name'], 'Another Player')


if __name__ == '__main__':
    unittest.main()
