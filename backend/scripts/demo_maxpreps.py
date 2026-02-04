#!/usr/bin/env python3
"""
Demo script for MaxPreps rankings scraper.

Fetches and displays high school lacrosse rankings.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.scrape.maxpreps import fetch_rankings


def main():
    # Fetch 23-24 national boys lacrosse rankings
    url = 'https://www.maxpreps.com/lacrosse/23-24/rankings/1/'
    
    print(f"Fetching rankings from {url}...")
    teams = fetch_rankings(url)
    
    print(f"\n✅ Found {len(teams)} ranked teams\n")
    print(f"{'Rank':<6} {'School':<30} {'Location':<35} {'Record':<10}")
    print("=" * 85)
    
    for team in teams[:10]:  # Show top 10
        location = f"{team.city or 'N/A'}, {team.state_code or 'N/A'}"
        print(f"#{team.rank:<5} {team.school_name:<30} {location:<35} {team.record or 'N/A':<10}")
    
    if len(teams) > 10:
        print(f"\n... and {len(teams) - 10} more teams")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
