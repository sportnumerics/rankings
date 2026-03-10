# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-03-10)

### PR
1) **#59 — Goals leaders page**
- Status: PR (green, awaiting review)
- Owner: assistant
- Outcome: `/[year]/[div]/leaders/goals` page showing top 50 goal scorers
- First increment: single category (goals), reuse existing data/components
- Acceptance checks:
  - ✅ Page loads at `/[year]/[div]/leaders/goals` for all years/divs
  - ✅ Top 50 players sorted by goals (descending)
  - ✅ Displays: player name, team, goals, assists, points
  - ✅ All CI checks passed
- Next action: needs Will's review + approval to merge
- Link: https://github.com/sportnumerics/rankings/pull/59
- Last update: CI green (2026-03-10 09:00)

2) **#TBD — Assists leaders page**
- Status: PR (opening now)
- Owner: assistant
- Outcome: `/[year]/[div]/leaders/assists` page showing top 50 assist leaders
- First increment: reuse goals leaders infrastructure, change sort field
- Acceptance checks:
  - Page loads at `/[year]/[div]/leaders/assists`
  - Top 50 players sorted by assists (descending)
  - Reuses PlayersCard component
  - CI passes
- Next action: push branch + open PR
- Branch: feature-assists-leaders-impl
- Last update: implemented (2026-03-10 09:00)

### Ready
3) **WIP/PR velocity automation**
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
- ✅ #56 Fix NCAA upcoming games date labeling off-by-one (merged 2026-03-07)
- ✅ #54 Backtest CI + sticky PR comment + CLI backtest command (merged 2026-03-07)
- ✅ Feature discovery sprint — top-5 candidates evaluated, promoted stats leaderboards (2026-03-08)

## Backlog Notes (assistant-facing)
- Prefer tasks that improve user-visible value or reduce prediction-quality risk.
- Keep PRs small and reviewable.
- Every status change must update `Next action`.
- **Saves leaders**: Not yet possible — `PlayerRating` type doesn't include saves field. Would require backend scraper extension + schema update.
