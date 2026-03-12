# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-03-07)

### PR
1) **#59 — Goals leaders page**
- Status: PR
- Owner: assistant
- Outcome: /leaders/goals page showing top 50 scorers per division
- First increment: ship MVP goals leaders page
- Acceptance checks:
  - Page loads at /2026/d1/leaders/goals
  - Shows top 50 players sorted by goals descending
  - Reuses existing PlayerRating data and PlayersCard UI
- Next action: awaiting Will's review
- Link: https://github.com/sportnumerics/rankings/pull/59
- Last update: review requested, all checks passing (2026-03-09 09:15)

2) **#58 — DuckDB parquet materialized views (12-file schema)**
- Status: PR
- Owner: assistant
- Outcome: 12 optimized parquet files (one per page component) with frontend DuckDB queries
- Current increment: Phase 1 + Phase 2 COMPLETE + schema + query + perf fixes
- Acceptance checks:
  - Backend: `python main.py export-parquet` generates all 12 files ✅
  - Backend: integrated into `all` workflow ✅
  - Frontend: all pages query correct file with optimal filters ✅
  - Footer displays query ms + file read stats ✅
  - Teams with 0 games appear in parquet mode ✅
  - Unrated teams rank below negative-rated teams (nulls last behavior) ✅
  - Team rosters parquet includes team metadata columns ✅
  - Game details page uses parquet mode and shows metrics ✅
  - game-metadata.parquet sorted by game_id for efficient single-game lookups ✅
- Next action: CI regenerating parquet files with correct schema + sort; then ready for Will's review
- Link: https://github.com/sportnumerics/rankings/pull/58
- Last update: Optimized game-metadata sort order for efficient game_id lookups (2026-03-12 08:49)

2) **#57 — DuckDB parquet benchmark harness + JSON vs parquet S3 comparison**
- Status: PR
- Owner: assistant
- Outcome: reproducible baseline for cold/warm local+S3 query performance
- First increment: keep as reference benchmark suite
- Acceptance checks:
  - Includes local page-shaped timings
  - Includes JSON vs parquet S3 timings
- Next action: decide merge order with #58 (can keep #57 for benchmarking docs)
- Link: https://github.com/sportnumerics/rankings/pull/57

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
- ✅ #56 Fix NCAA upcoming games date labeling off-by-one (merged 2026-03-07)

## Backlog Notes (assistant-facing)
- Prefer tasks that improve user-visible value or reduce prediction-quality risk.
- Keep PRs small and reviewable.
- Every status change must update `Next action`.
