# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-03-07)

### PR
1) **#59 — Goals leaders page**
- Status: PR (CI green, awaiting merge approval)
- Owner: assistant
- Outcome: `/[year]/[div]/leaders/goals` page showing top 50 goal scorers
- First increment: single category (goals), reuse existing data/components
- Acceptance checks:
  - ✅ Page loads at `/[year]/[div]/leaders/goals` for all years/divs
  - ✅ Top 50 players sorted by goals (descending)
  - ✅ Displays: player name, team, goals, assists, points
  - ✅ CI green (all checks passed)
- Next action: **BLOCKED - needs manual merge (branch protection policy)**
- Link: https://github.com/sportnumerics/rankings/pull/59
- Last update: CI passed 2026-03-08 11:02 AM, awaiting merge

### Ready
1) **Assists leaders page**
- Status: Ready (next after #59 merges)
- Owner: assistant
- Outcome: `/[year]/[div]/leaders/assists` page showing top 50 assist leaders
- First increment: duplicate goals leaders pattern for assists
- Acceptance checks:
  - Page loads at `/[year]/[div]/leaders/assists`
  - Top 50 players sorted by assists (descending)
  - Consistent UI with goals leaders page
- Next action: start after #59 merges to avoid merge conflicts

2) **WIP/PR velocity automation**
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
- ✅ #54 Backtest CI + sticky PR comment + CLI backtest command (merged 2026-03-08)
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
