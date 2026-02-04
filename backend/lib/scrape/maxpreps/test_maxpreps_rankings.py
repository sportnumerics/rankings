"""
Tests for MaxPreps rankings scraper.
"""

import json
import os
import unittest
from pathlib import Path

from lib.scrape.maxpreps.maxpreps_rankings import (
    MaxPrepsRankingTeam,
    fetch_rankings_from_json,
)


class TestMaxPrepsRankingTeam(unittest.TestCase):
    """Test MaxPrepsRankingTeam data model."""
    
    def test_parse_team_with_all_fields(self):
        """Test parsing team with complete data."""
        data = {
            'rank': 1,
            'schoolId': 'cd85d44b-8d6c-4ed2-873e-e3b3cbc1f0f7',
            'schoolName': 'Benjamin',
            'schoolFormattedName': 'Benjamin (Palm Beach Gardens, FL)',
            'stateCode': 'FL',
            'overall': '21-1-0',
            'strength': 21.4905,
            'rating': 47.36,
            'teamLink': 'https://www.maxpreps.com/fl/palm-beach-gardens/benjamin-buccaneers/lacrosse/23-24/schedule/',
            'lastUpdated': '2024-06-17T04:37:42',
        }
        
        team = MaxPrepsRankingTeam(data)
        
        self.assertEqual(team.rank, 1)
        self.assertEqual(team.school_name, 'Benjamin')
        self.assertEqual(team.city, 'Palm Beach Gardens')
        self.assertEqual(team.state_code, 'FL')
        self.assertEqual(team.record, '21-1-0')
        self.assertEqual(team.strength, 21.4905)
        self.assertEqual(team.rating, 47.36)
    
    def test_parse_city_from_formatted_name(self):
        """Test city extraction from various formatted names."""
        test_cases = [
            ('Benjamin (Palm Beach Gardens, FL)', 'Palm Beach Gardens'),
            ('Lake Mary (Lake Mary, FL)', 'Lake Mary'),
            ('La Salle College (Wyndmoor, PA)', 'Wyndmoor'),
            (None, None),
            ('No Parentheses School', None),
        ]
        
        for formatted_name, expected_city in test_cases:
            team = MaxPrepsRankingTeam({'schoolFormattedName': formatted_name})
            self.assertEqual(team.city, expected_city, f"Failed for: {formatted_name}")
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        data = {
            'rank': 5,
            'schoolId': 'test-id',
            'schoolName': 'Test School',
            'schoolFormattedName': 'Test School (Test City, TS)',
            'stateCode': 'TS',
            'overall': '15-3-0',
            'strength': 18.5,
            'rating': 42.1,
            'teamLink': 'https://example.com/team',
            'lastUpdated': '2024-06-01T00:00:00',
        }
        
        team = MaxPrepsRankingTeam(data)
        result = team.to_dict()
        
        self.assertEqual(result['rank'], 5)
        self.assertEqual(result['school_name'], 'Test School')
        self.assertEqual(result['city'], 'Test City')
        self.assertEqual(result['state'], 'TS')
        self.assertEqual(result['record'], '15-3-0')


class TestFetchRankingsFromJson(unittest.TestCase):
    """Test parsing rankings from JSON fixture."""
    
    def setUp(self):
        """Load fixture data."""
        fixture_path = Path(__file__).parent / 'fixtures' / 'rankings_23-24_national.json'
        with open(fixture_path) as f:
            self.fixture_data = json.load(f)
    
    def test_parses_all_teams(self):
        """Test that all teams in fixture are parsed."""
        teams = fetch_rankings_from_json(self.fixture_data)
        
        # Fixture has 25 teams
        self.assertEqual(len(teams), 25)
    
    def test_top_ranked_team(self):
        """Test that #1 ranked team is parsed correctly."""
        teams = fetch_rankings_from_json(self.fixture_data)
        
        top_team = teams[0]
        self.assertEqual(top_team.rank, 1)
        self.assertEqual(top_team.school_name, 'Benjamin')
        self.assertEqual(top_team.city, 'Palm Beach Gardens')
        self.assertEqual(top_team.state_code, 'FL')
        self.assertEqual(top_team.record, '21-1-0')
        self.assertIsNotNone(top_team.strength)
        self.assertIsNotNone(top_team.rating)
    
    def test_all_teams_have_required_fields(self):
        """Test that all teams have rank, school name, and state."""
        teams = fetch_rankings_from_json(self.fixture_data)
        
        for team in teams:
            self.assertIsNotNone(team.rank, f"Team {team.school_name} missing rank")
            self.assertIsNotNone(team.school_name, f"Rank {team.rank} missing school name")
            self.assertIsNotNone(team.state_code, f"Team {team.school_name} missing state")
    
    def test_output_format(self):
        """Test that to_dict produces expected output format."""
        teams = fetch_rankings_from_json(self.fixture_data)
        
        result = [team.to_dict() for team in teams[:3]]
        
        # Verify structure
        for team_dict in result:
            self.assertIn('rank', team_dict)
            self.assertIn('school_name', team_dict)
            self.assertIn('city', team_dict)
            self.assertIn('state', team_dict)
            self.assertIn('record', team_dict)
            self.assertIn('strength', team_dict)
            self.assertIn('rating', team_dict)


if __name__ == '__main__':
    unittest.main()
