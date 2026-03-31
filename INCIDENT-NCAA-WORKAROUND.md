# NCAA.com Workaround Plan

**Problem:** stats.ncaa.org blocked by Akamai (Access Denied)  
**Solution:** Scrape from NCAA.com instead

## Data Availability on NCAA.com

✅ **Working endpoints:**
- Main stats page: `https://www.ncaa.com/stats/lacrosse-men/d1`
- Goals leaders: `https://www.ncaa.com/stats/lacrosse-men/d1/current/individual/222`
- Assists leaders: `https://www.ncaa.com/stats/lacrosse-men/d1/current/individual/223`
- Saves leaders: `https://www.ncaa.com/stats/lacrosse-men/d1/current/individual/586`
- Team scoring offense: `https://www.ncaa.com/stats/lacrosse-men/d1/current/team/228`

All accessible via curl with basic User-Agent header.

## URL Pattern

```
https://www.ncaa.com/stats/{sport}/{division}/current/{type}/{stat_id}

sport: lacrosse-men, lacrosse-women
division: d1, d2, d3
type: individual, team
stat_id: numeric ID (see below)
```

## Stat IDs (from dropdown on ncaa.com)

### Individual Stats
- 222: Goals Per Game ⭐
- 223: Assists Per Game ⭐
- 586: Saves Per Game ⭐
- 224: Save Percentage
- 225: Goals-Against Average
- 227: Ground Balls Per Game
- 221: Points Per Game
- 410: Face-Off Winning Pct
- 560: Caused Turnovers Per Game
- 562: Shot Percentage
- 960: Individual Man-up Goals

### Team Stats
- 228: Scoring Offense ⭐
- 229: Scoring Defense ⭐
- 535: Assists Per Game
- 536: Saves Per Game
- 537: Points Per Game
- 538: Ground Balls Per Game
- 230: Face-Off Winning Percentage
- 231: Man-Up Offense
- 232: Man-Down Defense
- 238: Scoring Margin
- 233: Winning Percentage
- 561: Caused Turnovers Per Game
- 563: Shot Percentage
- 559: Turnovers Per Game
- 838: Clearing Percentage
- 1213: Opponent Clear Percentage

## Implementation Plan

### Phase 1: Quick Fix (New Scraper)
1. Create `backend/lib/scrape/ncaa_dot_com.py` (parallel to existing ncaa.py)
2. Parse HTML tables from NCAA.com (BeautifulSoup)
3. Extract player/team stats with rankings
4. Map to existing data schema

### Phase 2: Integration
1. Add NCAA.com scraper to backend pipeline
2. Update data merge logic to combine stats.ncaa.org (schedules) + NCAA.com (stats)
3. Add fallback: try stats.ncaa.org first, fall back to NCAA.com on 403

### Phase 3: Long-term
1. Monitor if Akamai eventually blocks NCAA.com too
2. Consider Playwright if needed
3. Cache aggressively to reduce request volume

## Data Mapping

NCAA.com provides:
- Rank
- Player Name
- School (with logo)
- Class (Fr/So/Jr/Sr)
- Position
- Games Played
- Total Stat
- Per Game Average

We can extract:
- Player name → `PlayerSummary.name`
- School → `TeamSummary.name` (need to map to existing team IDs)
- Stats → goals, assists, saves per game

## Testing

```bash
# Test goals leaders page
curl -s -A "Mozilla/5.0" "https://www.ncaa.com/stats/lacrosse-men/d1/current/individual/222" | \
  grep -E "<td>" | head -20

# Should show Luke McNamara, Rory Connor, etc.
```

## Next Steps
1. ✅ Confirmed NCAA.com accessible
2. ⏭️ Create ncaa_dot_com.py scraper
3. ⏭️ Parse HTML tables
4. ⏭️ Add unit tests
5. ⏭️ Integrate into pipeline
6. ⏭️ Deploy to prod
