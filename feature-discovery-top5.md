# Feature Discovery Sprint: Top 5 Candidates
*Generated: 2026-03-10 05:48 AM*

## Current State
Sportnumerics offers:
- Team rankings by division
- Player stats (goals, assists, etc.)
- Game schedules/results
- Individual team/player detail pages

**PR #59** adds `/leaders/goals` page (top 50 scorers).

## Competitor Analysis (NCAA.com)
NCAA.com provides:
- Individual stat leaders (goals, saves per game)
- Team stat leaders (goals/game, goals allowed/game)
- Multiple stat categories accessible from main stats page

## Top 5 Candidates (Ranked by Value/Effort)

### 1. **Multi-Category Leaders Pages** 
**Value:** High — Users want to see best performers across multiple dimensions (assists, faceoffs, saves, groundballs)  
**Effort:** Low — Reuse PR #59 infrastructure, just filter by different stat columns  
**Risk:** Low — Same data source, proven UI pattern  
**First increment:** Add `/leaders/assists` and `/leaders/saves` pages using existing PlayersCard component  
**Why #1:** Lowest-hanging fruit with clear user value. Natural extension of work-in-progress.

---

### 2. **Team Stats Leaders**
**Value:** Medium-High — Coaches/fans want to compare team offensive/defensive efficiency  
**Effort:** Medium — Need to aggregate team-level stats (goals/game, goals allowed/game, win %)  
**Risk:** Low — Data already exists in team records  
**First increment:** Add `/leaders/teams` showing top 20 by points/game, sorted descending  
**Why #2:** Complements player leaders. Moderate effort but fills obvious gap vs NCAA.com.

---

### 3. **Historical Stat Archives (Multi-Year Leaders)**
**Value:** Medium — Power users want to track season-over-season performance, all-time records  
**Effort:** Medium — Need to query across multiple years, handle data schema changes  
**Risk:** Medium — Data availability/consistency varies by year  
**First increment:** Add year selector to `/leaders/goals` showing top 50 for any past season  
**Why #3:** Differentiation opportunity. Adds depth without new page types.

---

### 4. **Game-Level Advanced Stats (Possession, Shot Charts)**
**Value:** High — Deep insights for serious analysts  
**Effort:** High — Requires new data sources (NCAA doesn't provide play-by-play publicly)  
**Risk:** High — Data acquisition unclear, scraping play-by-play may be fragile  
**First increment:** Research data availability (check if any MCLA sites publish PBP)  
**Why #4:** High value but significant unknowns. Park until easier wins ship.

---

### 5. **Mobile-Optimized Quick Stats Dashboard**
**Value:** Medium — Better mobile UX for checking rankings on-the-go  
**Effort:** Medium — Responsive design improvements, simplified layouts  
**Risk:** Low — Pure frontend work, no new data needed  
**First increment:** Add responsive breakpoints to team rankings page, test on mobile devices  
**Why #5:** Solid incremental improvement. Defer until core content features ship.

---

## Recommendation: Build Candidate #1 (Multi-Category Leaders)

**Rationale:**
- Directly builds on PR #59 (goals leaders)
- Smallest possible increment: 2-4 hours to add assists + saves pages
- Clear user value with zero data acquisition risk
- Sets foundation for more leader categories later (groundballs, faceoffs, etc.)

**Next action:** Convert to backlog task and implement first increment (assists + saves pages).
