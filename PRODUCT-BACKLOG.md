# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-03-14)

### PR
1) **#68 — Security: parameterize parquet SQL inputs**
- Status: PR (✅ all checks passing - ready to merge)
- Owner: assistant
- Outcome: Prevent SQL injection in parquet queries by using ? placeholders
- First increment: Replace template literals with parameterized queries
- Acceptance checks:
  - All parquet queries use ? placeholders ✅
  - parquetQuery accepts params array ✅
  - All CI checks passing ✅
  - Frontend deployed to dev ✅
- Next action: Ready for Will's review/merge
- Link: https://github.com/sportnumerics/rankings/pull/68
- Last update: Security fix complete, all checks passing (2026-03-14 09:00)

2) **#69 — Test: SQL parameterization validation**
- Status: PR (CI running)
- Owner: assistant
- Outcome: Automated test to prevent SQL injection regressions
- First increment: Add npm test script that validates parameterized queries
- Acceptance checks:
  - Test detects template literal vulnerabilities ✅
  - Test confirms ? placeholder usage ✅
  - Runs in CI via npm test --if-present ✅
  - Prevents regression to string concatenation ✅
- Next action: CI validation, then ready for review
- Link: https://github.com/sportnumerics/rankings/pull/69
- Last update: Test script created and pushed (2026-03-14 09:04)

3) **#59 — Goals leaders page**
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

4) **#58 — DuckDB parquet materialized views (12-file schema)**
- Status: PR (✅ all checks passing - ready to merge)
- Owner: assistant
- Outcome: 12 optimized parquet files (one per page component) with frontend DuckDB queries
- Current increment: Phase 1 + Phase 2 COMPLETE + all schema/query/perf fixes
- Acceptance checks:
  - Backend: `python main.py export-parquet` generates all 12 files ✅
  - Backend: integrated into `all` workflow ✅
  - Frontend: all pages query correct file with optimal filters ✅
  - Footer displays query ms + file read stats ✅
  - Teams with 0 games appear in parquet mode ✅
  - Unrated teams rank below negative-rated teams (nulls last) ✅
  - Team rosters include team metadata columns ✅
  - Game details page uses parquet mode ✅
  - game-metadata sorted by game_id for efficient lookups ✅
  - Fresh parquet files deployed to dev with correct schema ✅
- Next action: Ready for Will's review/merge
- Link: https://github.com/sportnumerics/rankings/pull/58
- Last update: All fixes complete, CI passing, dev deployed (2026-03-12 09:05)

5) **#57 — DuckDB parquet benchmark harness + JSON vs parquet S3 comparison**
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
1) **Feature discovery sprint: highest-value near-term product improvement**
- Status: Ready
- Owner: assistant
- Outcome: one evidence-backed feature promoted to build
- First increment: produce top-5 candidate list with value/effort/risk and choose #1
- Acceptance checks:
  - Top-5 list captured in backlog notes
  - One candidate converted into implementation-ready task
- Next action: research 5 candidates from competitor + current site gaps

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
- ✅ #56 Fix NCAA upcoming games date labeling off-by-one (merged 2026-03-07)
- ✅ Unit tests backlog item → converted to #69 SQL parameterization validation test (2026-03-14)

## Backlog Notes (assistant-facing)
- Prefer tasks that improve user-visible value or reduce prediction-quality risk.
- Keep PRs small and reviewable.
- Every status change must update `Next action`.
