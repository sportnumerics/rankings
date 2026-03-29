# Feature Discovery Sprint — 2026-03-29

## Research Summary

### Competitor Analysis
**LaxNumbers.com (high school focus):**
- State rankings with movement tracking
- Performance leaders: points, goals, assists, face-offs, **saves**
- Recruit commitment tracking
- Coach milestone tracking

**NCAA.com (D1):**
- Individual stat leaders (goals/assists per game)
- Team stat leaders (scoring offense/defense per game)
- Clean, simple leaderboards

**Current sportnumerics.com:**
- Team rankings (overall/offense/defense)
- Player stats (points, goals, assists)
- Game schedules
- **NEW:** Goals leaders page (PR #59 pending)

### Existing branch work (not yet merged):
- `feature-goals-leaders` → PR #59 (CI green, awaiting review)
- `feat/points-leaders`
- `feature-assists-leaders` (multiple versions)
- `feature-saves-leaders`
- `feature-per-game-stats`

---

## Top 5 Feature Candidates

### 1. **Assists Leaders Page** ⭐ RECOMMENDED
**Value:** High — completes the "big 3" offensive stats trio (goals ✅, points, assists)
**Effort:** Low — identical structure to goals leaders (copy PR #59, change sort field)
**Risk:** Very Low — proven pattern, no new data needed
**User Impact:** High — assists are a core stat fans track
**Implementation:** 2-3 hours (copy goals leaders, swap to assists sort)

**Why #1:** Goals leaders proved the pattern works. Assists is the natural next step and requires minimal new code.

---

### 2. **Points Leaders Page**
**Value:** Medium-High — most comprehensive offensive stat
**Effort:** Low — same pattern as goals/assists
**Risk:** Very Low
**User Impact:** Medium — users can already infer from goals+assists
**Implementation:** 2-3 hours

**Why #2:** Completes the offensive stat trinity, but less urgent than assists since points = goals + assists.

---

### 3. **Saves Leaders / Goalkeeper Rankings**
**Value:** High — completely missing position category
**Effort:** Medium — need to verify data availability, might need scraper updates
**Risk:** Medium — depends on data source having goalie stats
**User Impact:** High — goalies are a major position with dedicated fans
**Implementation:** 6-8 hours (data investigation + UI)

**Why #3:** High value but requires data validation first. Could be quick if data exists, slow if scraping needed.

---

### 4. **Per-Game Stats** (points/goals/assists per game)
**Value:** Medium — more fair comparison across teams with different # games
**Effort:** Medium — need to calculate games played, update UI
**Risk:** Low — math is straightforward
**User Impact:** Medium — purists prefer per-game, but total stats are standard
**Implementation:** 4-6 hours

**Why #4:** Nice refinement but not critical. Total stats are industry standard for season leaders.

---

### 5. **Team Stat Leaders** (scoring offense/defense per game)
**Value:** Medium — adds team-level comparison beyond rankings
**Effort:** Low-Medium — data exists, need new page/UI
**Risk:** Low
**User Impact:** Low-Medium — team rankings already show relative strength
**Implementation:** 3-5 hours

**Why #5:** Interesting but overlaps with existing team rankings. Lower differentiation value.

---

## Recommendation: **Assists Leaders** (#1)

**Rationale:**
- Proven pattern from PR #59 (goals leaders)
- Minimal risk and effort
- Completes the core offensive stat coverage
- Fast shipping velocity (could ship in <3 hours)

**Next Steps:**
1. Wait for PR #59 (goals) to merge
2. Copy implementation, change to assists sort
3. Ship within 1 day

**Alternative:** If data validation for saves is quick, **Saves Leaders** (#3) could leapfrog to #1 as it fills a major gap.
