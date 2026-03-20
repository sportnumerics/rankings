# Feature Discovery Sprint — March 2026

**Research date:** 2026-03-16  
**Goal:** Identify highest-value near-term product improvement

## Methodology
- Analyzed competitor sites (NCAA.com, LaxNumbers.com)
- Reviewed current site structure and PR #59 (goals leaders)
- Identified feature gaps and user value opportunities

## Top 5 Candidates

### 1. Per-Game Stat Averages (Points/Goals/Assists PPG)
**Value:** ⭐⭐⭐⭐  
**Effort:** ⭐⭐  
**Risk:** Low

**Description:**  
Add per-game average columns alongside total stats for players. Show "PPG" (points per game), "GPG" (goals per game), "APG" (assists per game).

**User value:**
- Standard across all lacrosse stats sites (NCAA.com shows only per-game)
- More meaningful for comparing players with different games played
- Helps identify consistent performers vs volume scorers

**Implementation notes:**
- Backend: Add `games_played` count to player stats aggregation
- Frontend: Calculate averages (points/games_played) in player queries
- Display: Add columns to PlayerRatings table, sort options
- Data already exists in game boxscores - just needs aggregation

**Acceptance checks:**
- [ ] Players list shows PPG, GPG, APG columns
- [ ] Can sort by per-game stats
- [ ] Handles division-by-zero for players with 0 games
- [ ] Per-game stats match manual calculation from totals

---

### 2. Assists Leaders Page
**Value:** ⭐⭐⭐⭐  
**Effort:** ⭐  
**Risk:** Low

**Description:**  
Add `/leaders/assists` page (mirror of PR #59 goals leaders pattern).

**User value:**
- Natural companion to goals leaders
- Highlights playmakers (different player archetype than scorers)
- Completes the "big 3" stats (goals, assists, saves)

**Implementation notes:**
- Copy PR #59 pattern, change sort to `assists DESC`
- Update navigation to include assists link
- Reuse existing PlayersCard UI

**Acceptance checks:**
- [ ] Page loads at /2026/d1/leaders/assists
- [ ] Shows top 50 players sorted by assists descending
- [ ] Navigation includes "Assists Leaders" link

---

### 3. Goalie Stats & Saves Leaders
**Value:** ⭐⭐⭐⭐⭐  
**Effort:** ⭐⭐⭐⭐  
**Risk:** Medium

**Description:**  
Add goalie-specific stats (saves, save %, goals against avg) and `/leaders/saves` page.

**User value:**
- Goalies are currently invisible in rankings (offense-focused)
- Huge gap vs competitors (NCAA.com shows save leaders prominently)
- Completes position coverage (attackers, middies, goalies)

**Implementation notes:**
- Backend: Parse goalie stats from game boxscores (saves, GA)
- Backend: Calculate save % and GAA
- Frontend: New goalie leaderboard page
- Frontend: Update player pages to show goalie stats when applicable

**Blockers:**
- Need to verify goalie stats are in current scraped data
- May need to add goalie-specific parquet materialized view
- Save % calculation requires shots-against data (may not be in source)

**Acceptance checks:**
- [ ] Backend exports goalie stats to parquet
- [ ] /leaders/saves page shows top 50 goalies by saves
- [ ] Player pages show save % and GAA for goalies
- [ ] Stats validated against source data

**See also:** `PRODUCT-IDEAS.md` mentioned "product-research-goalies" branch exists

---

### 4. Quick Search (Team/Player Autocomplete)
**Value:** ⭐⭐⭐  
**Effort:** ⭐⭐⭐  
**Risk:** Low

**Description:**  
Add a search input in header that autocompletes team and player names, navigates on select.

**User value:**
- Reduces clicks to find specific team/player
- Standard UX on sports stats sites
- Especially valuable as data grows (more divisions, years)

**Implementation notes:**
- Frontend: Add search input to Navigation component
- Frontend: Client-side autocomplete using current page data (no backend needed initially)
- Use existing team/player name arrays from rankings
- Navigate to `/2026/teams/{teamId}` or `/2026/players/{playerId}` on select

**Acceptance checks:**
- [ ] Search input visible in header
- [ ] Autocomplete suggests teams and players as user types
- [ ] Selecting a result navigates to that entity's page
- [ ] Works on mobile (touch-friendly)

---

### 5. Historical Year Comparison Tool
**Value:** ⭐⭐⭐  
**Effort:** ⭐⭐⭐⭐⭐  
**Risk:** High

**Description:**  
Side-by-side comparison of team/player stats across years (e.g., "How did Syracuse perform in 2025 vs 2026?").

**User value:**
- Answers "trend" questions (improving/declining teams)
- Interesting for fans tracking program trajectory
- Differentiator from basic rankings sites

**Implementation notes:**
- Frontend: Add "Compare Years" toggle on team/player pages
- Backend: Query multiple years' data simultaneously
- UI: Table or chart showing key metrics by year
- Requires efficient cross-year data loading (parquet helps here)

**Blockers:**
- High complexity for first increment
- Unclear if multi-year data exists for all divisions
- UX design needed (how to display comparison clearly)

**Deferred rationale:**  
High effort, uncertain data availability. Better to ship smaller features first and validate user interest in historical data.

---

## Recommendation: Per-Game Stat Averages (#1)

**Why:**
- Highest value/effort ratio (⭐⭐⭐⭐ value, ⭐⭐ effort)
- Closes a major gap vs competitors (NCAA.com standard is per-game)
- Low risk - data already exists, just needs calculation
- Improves existing pages (no new navigation/routing)
- Foundation for future stat-based features

**First increment:**
Add `games_played` to backend player aggregation and `ppg`/`gpg`/`apg` columns to frontend player rankings display.

**Acceptance checks:**
- [ ] Backend: player stats JSON includes `games_played` field
- [ ] Frontend: Players table shows PPG, GPG, APG columns
- [ ] Frontend: Can sort by per-game stats
- [ ] Division-by-zero handled gracefully (show 0.00 or — for 0 games)
- [ ] Per-game calculations verified correct against sample data

**Estimated scope:** 1-2 days (backend aggregation + frontend display)

---

## Next Steps
1. Get Will's feedback on recommendation
2. Convert chosen feature to implementation-ready backlog task
3. Create first-increment PR

