# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-03-07)

### PR
1) **#59 — Goals leaders page**
- Status: PR (has merge conflicts - rebasing)
- Owner: assistant
- Outcome: /leaders/goals page showing top 50 scorers per division
- First increment: ship MVP goals leaders page
- Acceptance checks:
  - Page loads at /2026/d1/leaders/goals
  - Shows top 50 players sorted by goals descending
  - Reuses existing PlayerRating data and PlayersCard UI
- Next action: resolve merge conflicts and force-push updated branch
- Link: https://github.com/sportnumerics/rankings/pull/59
- Last update: rebasing on main (2026-03-28 09:00)

### Ready
2) **Unit tests for parquet query code paths**
- Status: Ready
- Owner: assistant
- Outcome: test coverage for parquet.ts query functions and server data loaders
- First increment: add tests for getRankedTeams/getRankedPlayers/getGames parquet mode
- Acceptance checks:
  - Tests verify SQL query construction (div filtering, sorting, column selection)
  - Tests verify fallback behavior when parquet fails
  - Tests verify debug metadata structure
  - All tests pass in CI
- Next action: create test file with fixture data and basic query validation
- Context: Multiple parquet bugs found reactively (div mapping, Promise.all pattern, etc.) - need systematic coverage

3) **Feature discovery sprint: highest-value near-term product improvement**
- Status: Ready
- Owner: assistant
- Outcome: one evidence-backed feature promoted to build
- First increment: produce top-5 candidate list with value/effort/risk and choose #1
- Acceptance checks:
  - Top-5 list captured in backlog notes
  - One candidate converted into implementation-ready task
- Next action: research 5 candidates from competitor + current site gaps

4) **WIP/PR velocity automation**
- Status: Ready
- Owner: assistant
- Outcome: fewer stalls, faster PR throughput
- First increment: daily stale-PR check with concrete unblock actions
- Acceptance checks:
  - Daily update includes active PR state + next unblock step
  - blockers explicitly tagged with owner
- Next action: add "stale >24h" handling notes to this file and use daily

### In Progress
- (none)

### Blocked
- (none)

## Done
- ✅ #58 DuckDB parquet materialized views (merged 2026-03-13)
- ✅ #56 Fix NCAA upcoming games date labeling off-by-one (merged 2026-03-07)
- ✅ Feature discovery sprint (2026-03-08) — top-5 list complete, promoted Stats Leaderboards

## Backlog Notes (assistant-facing)
- Prefer tasks that improve user-visible value or reduce prediction-quality risk.
- Keep PRs small and reviewable.
- Every status change must update `Next action`.

### Feature Discovery Sprint — Top 5 Candidates (2026-03-08)

**Evaluation criteria**: Value (user engagement + differentiation) / Effort (dev complexity) / Risk (data availability + maintenance)

**1. Stats leaderboards by category** ⭐ PROMOTED
- **Value**: HIGH — Core feature gap vs competitors (ESPN, NCAA.com have this)
- **Effort**: LOW — We already collect goals/assists, just need new views/sorts
- **Risk**: LOW — Existing data, no new scraping
- **Win**: Quick value add, easy to test, clear user benefit
- **First increment**: Goals leaders page (top 50, sortable)

**2. Prediction accuracy dashboard**
- **Value**: HIGH — Builds trust, validates ranking quality, differentiator
- **Effort**: MEDIUM — Need to store predictions pre-game, track outcomes, calculate metrics
- **Risk**: MEDIUM — Needs schema changes, backfill logic
- **Win**: Transparency = credibility, helps tune algorithm over time

**3. Conference/division standings**
- **Value**: MEDIUM-HIGH — Standard feature, users expect it
- **Effort**: LOW-MEDIUM — Data exists (games/results), just aggregate by conference
- **Risk**: LOW — No new data sources
- **Win**: Completes the "rankings + standings" package

**4. Goalie-specific rankings**
- **Value**: HIGH — Totally underserved niche, clear gap
- **Effort**: MEDIUM — New scraper (NCAA goalie stats), schema extension
- **Risk**: MEDIUM — New scraping target, need to extend PlayerRating model
- **Win**: Unique differentiator, dedicated audience (goalies/coaches)
- **Research**: PR #31 notes (see memory/sportnumerics-product-research.md)

**5. High school lacrosse (MaxPreps)**
- **Value**: VERY HIGH — Massive untapped market (parents/players/coaches)
- **Effort**: MEDIUM-HIGH — POC exists, but needs full integration + UI
- **Risk**: MEDIUM-HIGH — New sport tier, scraping stability unknown long-term
- **Win**: 10x user base potential, strong differentiation
- **Research**: POC already built (PR #29), see memory/sportnumerics-product-research.md

**Decision**: Promote #1 (Stats leaderboards) to Ready — quickest win with clear value.
