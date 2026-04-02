# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-04-02 09:00)

### PR
1) **#86 — Assists leaders page** ⭐ HIGH-VALUE
- Status: PR (✅ all checks passing, awaiting review)
- Owner: assistant
- Outcome: /leaders/assists page showing top 50 assist leaders per division
- First increment: MVP assists leaders page (recommended from feature discovery sprint)
- Acceptance checks:
  - ✅ Page loads at /2026/d1/leaders/assists
  - ✅ Shows top 50 players sorted by assists descending
  - ✅ Reuses existing PlayerRating data and PlayersCard UI
  - ✅ All CI checks passing
- Next action: awaiting Will's code review for merge
- Link: https://github.com/sportnumerics/rankings/pull/86
- Last update: CI green, ready for review (2026-03-30 18:10)
- **Value**: Fills current gap (assists are fundamental stat, NCAA.com has prominent assists leaders)

2) **#76 — Points leaders page**
- Status: PR (✅ all checks passing)
- Owner: assistant
- Outcome: /leaders/points page showing top 50 points leaders per division
- First increment: MVP points leaders page
- Acceptance checks:
  - ✅ Page loads at /2026/d1/leaders/points
  - ✅ Shows top 50 players sorted by points (goals + assists) descending
  - ✅ Reuses existing PlayerRating data and PlayersCard UI
- Next action: awaiting Will's review
- Link: https://github.com/sportnumerics/rankings/pull/76
- Last update: CI green

3) **#59 — Goals leaders page**
- Status: PR (✅ all checks passing)
- Owner: assistant
- Outcome: /leaders/goals page showing top 50 scorers per division
- First increment: ship MVP goals leaders page
- Acceptance checks:
  - Page loads at /2026/d1/leaders/goals
  - Shows top 50 players sorted by goals descending
  - Reuses existing PlayerRating data and PlayersCard UI
- Next action: awaiting Will's review
- Link: https://github.com/sportnumerics/rankings/pull/59
- Last update: CI green

4) **#82 — Unit tests for parquet query code paths**
- Status: PR (✅ CI passing, INCOMPLETE)
- Owner: assistant
- Outcome: test coverage for parquet.ts query functions to catch bugs reactively
- First increment: add vitest + 13 tests for utility functions
- Acceptance checks:
  - ✅ All tests pass in CI
  - ⚠️ INCOMPLETE: Only covers utility functions (dataModeFromSearch, QueryDebug type)
  - ❌ Missing: SQL query construction tests (getRankedTeams, getRankedPlayers, getGames)
  - ❌ Missing: Fallback behavior tests when parquet fails
- Next action: Expand tests to cover actual query paths OR close PR and revisit when needed
- Link: https://github.com/sportnumerics/rankings/pull/82
- Last update: PR created with 13 passing tests (2026-03-29 09:05)
- **Note**: Current tests provide minimal value; recommend closing until more comprehensive coverage is scoped

### Ready
5) **Saves leaders page** (next high-value feature)
- Status: Ready
- Owner: assistant
- Outcome: /leaders/saves page showing top 50 goalie save leaders per division
- First increment: implement saves leaders using existing pattern from #86/#76/#59
- Acceptance checks:
  - Page loads at /2026/d1/leaders/saves
  - Shows top 50 players sorted by saves descending
  - Reuses existing PlayerRating data and PlayersCard UI
- Next action: Create PR after reviewing #86 merge
- Estimated effort: 1-2 hours (identical pattern)
- **Context**: From feature discovery sprint - goalies are underrepresented, saves are already collected

6) **WIP/PR velocity automation**
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

## Done (recent)
- ✅ #89 HOTFIX: Firefox + Playwright bypasses Akamai on stats.ncaa.org (merged 2026-04-01)
- ✅ #58 DuckDB parquet materialized views (merged 2026-03-13)
- ✅ #56 Fix NCAA upcoming games date labeling off-by-one (merged 2026-03-07)

## Backlog Notes (assistant-facing)
- Prefer tasks that improve user-visible value or reduce prediction-quality risk.
- Keep PRs small and reviewable.
- Every status change must update `Next action`.
- Feature discovery sprint completed 2026-03-30 (see docs/feature-discovery-2026-03-30.md)
- Current focus: ship leader pages (#86, #76, #59) then goalie stats
