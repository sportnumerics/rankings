# MaxPreps High School Lacrosse Scraper

Proof-of-concept scraper for MaxPreps high school lacrosse rankings.

## Overview

MaxPreps provides comprehensive high school lacrosse rankings, stats, and schedules. This scraper extracts team ranking data from their Next.js-powered site by parsing the embedded `__NEXT_DATA__` JSON.

## Usage

```python
from lib.scrape.maxpreps import fetch_rankings

# Fetch national rankings for 23-24 season
teams = fetch_rankings('https://www.maxpreps.com/lacrosse/23-24/rankings/1/')

for team in teams:
    print(f"#{team.rank}: {team.school_name} ({team.city}, {team.state_code})")
```

## Demo Script

```bash
cd backend
uv run python scripts/demo_maxpreps.py
```

## Tests

```bash
cd backend
uv run python -m unittest lib.scrape.maxpreps.test_maxpreps_rankings
```

## Data Fields

Each `MaxPrepsRankingTeam` includes:
- `rank` - National ranking
- `school_name` - School name
- `city` - City (parsed from formatted name)
- `state_code` - Two-letter state code
- `record` - Win-loss-tie record (e.g., "21-1-0")
- `strength` - Strength rating
- `rating` - Overall rating
- `team_link` - Link to team schedule page
- `last_updated` - Last update timestamp

## Scrapability

✅ **HIGH** - MaxPreps uses Next.js with server-side rendering. All ranking data is embedded in `__NEXT_DATA__` JSON in the HTML, making it easy to parse without JavaScript execution.

## robots.txt

MaxPreps allows scraping of ranking pages (no disallow rules for `/lacrosse/rankings/`).

## Next Steps

- Parse additional ranking tiers (state, region, division)
- Extract player stats and team schedules
- Handle pagination for larger rankings
- Add support for girls lacrosse rankings
- Monitor for data structure changes
