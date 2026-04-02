# Feature Discovery Sprint — 2026-03-30

## Objective
Identify highest-value near-term product improvement with evidence-backed analysis (value/effort/risk).

## Current Site Strengths
- Team rankings (ELO-based)
- Schedule/results viewing
- Player stats (goals, assists, points)
- Fast parquet-based queries

## Current Site Gaps (vs NCAA.com)
- No saves/goalie stats
- No assists leaders page
- No points leaders page
- No per-game averages (PPG, GPG, APG)
- No save percentage leaderboards

---

## Top-5 Feature Candidates

### 1. **Assists Leaders Page** ⭐ RECOMMENDED
**Value**: High
- Assists are fundamental offensive stat (already collected)
- Users currently have no way to discover top playmakers
- NCAA.com has assists leaders prominently featured
- Directly comparable to goals leaders (#59)

**Effort**: Low
- Data already exists in `PlayerRating` parquet
- Copy implementation from PR #59 (goals leaders)
- Replace `goals` with `assists` in queries/UI
- Estimated: 2-3 hours

**Risk**: Very Low
- No new data dependencies
- No schema changes
- Proven UI pattern from #59

**Technical notes**:
- Route: `/[year]/[div]/leaders/assists`
- Query: `SELECT player_name, team, assists FROM player_ratings WHERE division = ? ORDER BY assists DESC LIMIT 50`
- UI: Reuse `PlayersCard` component

---

### 2. **Points Leaders Page**
**Value**: Medium-High
- Points (goals + assists) is standard aggregate metric
- Shows offensive versatility (goals-only can miss playmakers)
- NCAA.com includes points in leaderboards

**Effort**: Low
- Data: `points = goals + assists` (already in parquet)
- Implementation identical to #59/#1
- Estimated: 2-3 hours

**Risk**: Very Low
- Same low risk as assists leaders

**Note**: Less unique value than assists (users can mentally add goals+assists), but still standard.

---

### 3. **Per-Game Stat Averages (PPG, GPG, APG)**
**Value**: High
- Normalizes for games played (fairer comparison)
- NCAA.com shows "Per Game" prominently
- Currently site only shows raw totals

**Effort**: Medium
- Backend: Add `goals_per_game`, `assists_per_game`, `points_per_game` columns
- Compute: `goals / games_played` for each player
- Update parquet generation logic
- Update frontend queries/UI to display PPG
- Estimated: 4-6 hours

**Risk**: Medium
- Requires schema change (new columns)
- Need to handle division-by-zero (players with 0 games)
- Backend reprocessing required

**Blocker**: Need to confirm `games_played` data availability in current pipeline.

---

### 4. **Goalie Statistics (Saves, Save %, GAA)**
**Value**: Very High
- Large underserved audience (goalies, coaches, scouts)
- Zero competition in MCLA space
- NCAA.com has dedicated goalie leaderboards
- Completely new value proposition

**Effort**: High
- Scrape new data source (NCAA goalie stats page)
- Extend schema: `GoalieStatLine` model
- New parquet tables for goalie data
- New frontend pages: `/leaders/goalies`
- Estimated: 10-15 hours (multi-increment)

**Risk**: High
- New scraping target (may break)
- Schema expansion (backward compatibility)
- Data quality unknown (incomplete rosters?)
- Multi-week project

**Recommendation**: High value but requires multi-increment plan. Not suitable for single sprint.

---

### 5. **High School Lacrosse (MaxPreps)**
**Value**: Very High (huge audience)
- Massive market (parents, players, HS coaches)
- Proven scrapability (PR #29 POC worked)
- Low competition for MCLA-style rankings in HS space

**Effort**: Very High
- Separate league/season structure
- New scraping infrastructure
- New frontend routes (`/high-school/...`)
- Hosting/compute scaling
- Estimated: 40+ hours (multi-month project)

**Risk**: Very High
- Operational complexity (2x scraping targets)
- Cost scaling (more data, more traffic)
- Legal/ToS risk (MaxPreps may object)
- Requires explicit product pivot decision

**Recommendation**: Defer until MCLA product is mature and Will commits to multi-league expansion.

---

## Decision Matrix

| Feature                  | Value | Effort | Risk  | Time to Ship | Rec |
|--------------------------|-------|--------|-------|--------------|-----|
| Assists Leaders          | High  | Low    | V.Low | 2-3h         | ⭐   |
| Points Leaders           | Med   | Low    | V.Low | 2-3h         |     |
| Per-Game Averages        | High  | Med    | Med   | 4-6h         |     |
| Goalie Stats             | V.High| High   | High  | 10-15h       |     |
| High School (MaxPreps)   | V.High| V.High | V.High| 40+h         |     |

---

## Recommendation: **Assists Leaders Page**

**Why**:
1. **Low-hanging fruit**: Identical implementation to #59 (goals leaders)
2. **Immediate user value**: Discover top playmakers (currently impossible)
3. **Risk-free**: No schema changes, proven pattern, fast to ship
4. **Momentum**: Ship 2nd category in leaders suite, build toward complete stat coverage
5. **2-3 hour increment**: Can ship this week

**Next Steps**:
1. Create branch: `feature/assists-leaders`
2. Copy `/leaders/goals` implementation
3. Replace `goals` → `assists` in query/UI
4. Add route: `/[year]/[div]/leaders/assists`
5. Test with dev data
6. Open PR with CI

**After this ships**: Consider points leaders (same effort) or invest in per-game averages (higher value, more effort).

---

## Archive Notes
- **Goalie stats**: Revisit after leaders suite complete (goals/assists/points)
- **High school**: Requires explicit product expansion decision + multi-quarter roadmap
- **Per-game averages**: Strong candidate for next medium-effort increment

---

**Sprint completed**: 2026-03-30  
**Next action**: Implement assists leaders page
