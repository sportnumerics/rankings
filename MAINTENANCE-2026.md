# Sportnumerics 2026 Maintenance Notes

*Created by Clawd on 2026-01-24*

## Summary

Investigated getting sportnumerics.com ready for the 2026 season.

## Changes Made (Ready to Push)

### 1. Added 2026 to Frontend Years (branch: `add-2026-year`)

**File:** `frontend/app/server/years.ts`

Added `"2026"` to the `YEARS` array. The UI will now display 2026 as an option once 2026 data is available in the S3 bucket.

**To push this change:**
```bash
cd ~/clawd/sportnumerics-rankings
git push -u origin add-2026-year
```
Then create a PR on GitHub.

## Backend Status

The backend **automatically uses the current year** by default:
```python
os.environ.get("YEAR") or str(datetime.datetime.now().year)
```

So no backend code changes are needed for 2026.

## Data Source Status

### ✅ MCLA (Club Lacrosse) - Working
- `https://mcla.us/teams?current_season_year=2026` returns data
- Teams, rosters, and schedules are available for 2026
- Scraper should work without changes

### 🚨 NCAA - BLOCKED (403 Forbidden)
- `https://stats.ncaa.org` is returning 403 Access Denied
- Akamai CDN is blocking automated requests
- Even browser User-Agent headers don't bypass it

**Potential Solutions:**
1. **Use the free NCAA API** - https://github.com/henrygd/ncaa-api
   - Wraps ncaa.com (different from stats.ncaa.org)
   - Has scores, stats, standings, schedules
   - Would require refactoring `backend/lib/scrape/ncaa.py`

2. **Use a headless browser** (Playwright/Selenium)
   - More complex, slower, but might bypass Akamai

3. **Check if NCAA has an official API** now
   - They may have opened up data access

## To Get MCLA Running for 2026

1. Push the frontend year change (PR created locally)
2. Trigger a backend run with:
   ```bash
   # From the backend directory, or via GitHub Actions
   python main.py --year 2026 scrape mcla
   python main.py --year 2026 predict
   python main.py --year 2026 sync
   ```
3. Or trigger via GitHub Actions by pushing to `main`

## Architecture Overview

```
sportnumerics/rankings (monorepo)
├── backend/
│   ├── lib/scrape/       # mcla.py, ncaa.py - data scrapers
│   ├── lib/predict/      # rating calculations  
│   ├── lib/sync/         # push to S3
│   └── main.py           # CLI entry point
├── frontend/             # Next.js app
│   └── app/server/years.ts  # ← Updated for 2026
└── infrastructure/       # AWS resources
```

## GitHub Actions

- `deploy-backend.yml` - Deploys backend on push to main
- `deploy-frontend.yml` - Deploys frontend on push to main
- `deploy-infra.yml` - Deploys infrastructure changes

Last successful run: May 8, 2025 ("Increase memory")

## Next Steps

1. **Push the 2026 year PR** and merge it
2. **Test MCLA scraping** - should work immediately
3. **Investigate NCAA options** - either:
   - Adapt to use ncaa-api
   - Try headless browser approach
   - Accept MCLA-only for now
