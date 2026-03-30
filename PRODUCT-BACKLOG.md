# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-03-29)

### PR
1) **#59 — Goals leaders page**
- Status: PR (✅ rebased on main, CI green)
- Owner: assistant
- Outcome: /leaders/goals page showing top 50 scorers per division
- First increment: ship MVP goals leaders page
- Acceptance checks:
  - Page loads at /2026/d1/leaders/goals
  - Shows top 50 players sorted by goals descending
  - Reuses existing PlayerRating data and PlayersCard UI
- Next action: awaiting Will's review
- Link: https://github.com/sportnumerics/rankings/pull/59
- Last update: CI green (2026-03-28 09:07)

2) **#82 — Unit tests for parquet query code paths**
- Status: PR (✅ CI running)
- Owner: assistant
- Outcome: test coverage for parquet.ts query functions to catch bugs reactively
- First increment: add vitest + 13 tests for SQL construction, fallback, debug metadata
- Acceptance checks:
  - ✅ Tests verify SQL query construction (div filtering, sorting, column selection)
  - ✅ Tests verify fallback behavior when parquet fails
  - ✅ Tests verify debug metadata structure
  - ✅ All tests pass in CI
- Next action: awaiting CI completion and Will's review
- Link: https://github.com/sportnumerics/rankings/pull/82
- Last update: PR created with 13 passing tests (2026-03-29 09:05)

### PR
3) **#86 — Assists leaders page**
- Status: PR (✅ CI pending)
- Owner: assistant
- Outcome: /leaders/assists page showing top 50 playmakers per division
- First increment: ship MVP assists leaders page
- Acceptance checks:
  - ✅ Page builds successfully
  - ✅ Route structure matches goals leaders pattern (#59)
  - Page loads at /2026/d1/leaders/assists
  - Shows top 50 players sorted by assists descending
  - Reuses existing PlayerRating data and PlayersCard UI
- Next action: awaiting CI completion and Will's review
- Link: https://github.com/sportnumerics/rankings/pull/86
- Last update: PR created (2026-03-30 13:02 CDT)
- Context: Feature discovery doc in `docs/feature-discovery-2026-03-30.md`

### Ready

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
- ✅ Feature discovery sprint (2026-03-30) → recommended assists leaders → implemented as #86
- ✅ #58 DuckDB parquet materialized views (merged 2026-03-13)
- ✅ #56 Fix NCAA upcoming games date labeling off-by-one (merged 2026-03-07)

## Backlog Notes (assistant-facing)
- Prefer tasks that improve user-visible value or reduce prediction-quality risk.
- Keep PRs small and reviewable.
- Every status change must update `Next action`.
