"""
MaxPreps high school lacrosse rankings scraper.

Extracts team ranking data from MaxPreps Next.js pages via embedded __NEXT_DATA__ JSON.
"""

import json
import re
from typing import List, Dict, Optional
from urllib.request import Request, urlopen


class MaxPrepsRankingTeam:
    """Represents a single team in the MaxPreps rankings."""
    
    def __init__(self, data: Dict):
        self.rank = data.get('rank')
        self.school_id = data.get('schoolId')
        self.school_name = data.get('schoolName')
        self.school_formatted_name = data.get('schoolFormattedName')
        self.state_code = data.get('stateCode')
        self.record = data.get('overall')
        self.strength = data.get('strength')
        self.rating = data.get('rating')
        self.team_link = data.get('teamLink')
        self.last_updated = data.get('lastUpdated')
        
        # Parse city from formatted name (e.g., "Benjamin (Palm Beach Gardens, FL)")
        self.city = self._parse_city(self.school_formatted_name)
    
    def _parse_city(self, formatted_name: Optional[str]) -> Optional[str]:
        """Extract city from school formatted name."""
        if not formatted_name:
            return None
        
        # Pattern: "School Name (City, ST)"
        match = re.search(r'\(([^,]+),', formatted_name)
        return match.group(1).strip() if match else None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            'rank': self.rank,
            'school_id': self.school_id,
            'school_name': self.school_name,
            'city': self.city,
            'state': self.state_code,
            'record': self.record,
            'strength': self.strength,
            'rating': self.rating,
            'team_link': self.team_link,
            'last_updated': self.last_updated,
        }


def fetch_rankings(url: str, timeout: int = 15) -> List[MaxPrepsRankingTeam]:
    """
    Fetch rankings from a MaxPreps rankings page.
    
    Args:
        url: MaxPreps rankings page URL (e.g., https://www.maxpreps.com/lacrosse/23-24/rankings/1/)
        timeout: Request timeout in seconds
    
    Returns:
        List of MaxPrepsRankingTeam objects
    
    Raises:
        ValueError: If __NEXT_DATA__ JSON cannot be found or parsed
        urllib.error.URLError: If request fails
    """
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urlopen(req, timeout=timeout) as resp:
        html = resp.read().decode('utf-8')
    
    # Extract __NEXT_DATA__ JSON
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html)
    if not match:
        raise ValueError("Could not find __NEXT_DATA__ in HTML")
    
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse __NEXT_DATA__ JSON: {e}")
    
    # Navigate to rankings data
    try:
        rankings_list = data['props']['pageProps']['rankingsListData']['rankings']
    except KeyError as e:
        raise ValueError(f"Unexpected __NEXT_DATA__ structure (missing key: {e})")
    
    return [MaxPrepsRankingTeam(team_data) for team_data in rankings_list]


def fetch_rankings_from_json(json_data: Dict) -> List[MaxPrepsRankingTeam]:
    """
    Parse rankings from already-extracted rankingsListData JSON.
    
    Useful for testing with fixtures.
    
    Args:
        json_data: The rankingsListData object from __NEXT_DATA__
    
    Returns:
        List of MaxPrepsRankingTeam objects
    """
    rankings_list = json_data.get('rankings', [])
    return [MaxPrepsRankingTeam(team_data) for team_data in rankings_list]
