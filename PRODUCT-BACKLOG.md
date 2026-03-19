# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-03-19)

### PR
1) **#71 — Assists leaders page**
- Status: PR (✅ all checks passing)
- Owner: assistant
- Outcome: /leaders/assists page showing top 50 assist leaders per division
- First increment: ship MVP assists leaders page
- Acceptance checks:
  - Page loads at /2026/d1/leaders/assists ✅
  - Shows top 50 players sorted by assists descending ✅
  - Reuses existing PlayerRating data and PlayersCard UI ✅
- Next action: awaiting Will's review/merge
- Link: https://github.com/sportnumerics/rankings/pull/71
- Last update: all checks passing (2026-03-17 09:21)

2) **#70 — Per-game stat averages (PPG/GPG/APG)**
- Status: PR (✅ all checks passing)
- Owner: assistant
- Outcome: Add per-game averages to player stats (standard across competitor sites)
- First increment: Backend + frontend complete
- Acceptance checks:
  - Backend: player stats include `games_played` field ✅
  - Backend: games_played counts games with non-zero goals or assists ✅
  - Frontend: Players table shows G, A, GP, PPG, GPG, APG columns ✅
  - Frontend: Per-game columns conditional on data availability ✅
  - Division-by-zero handled gracefully ✅
  - All unit tests passing ✅
- Next action: awaiting Will's review/merge
- Link: https://github.com/sportnumerics/rankings/pull/70
- Last update: all checks passing (2026-03-17 09:29)

3) **#69 — SQL parameterization validation test**
- Status: PR (✅ all checks passing)
- Owner: assistant
- Outcome: npm test script that validates parquet queries use ? placeholders (prevents SQL injection)
- First increment: ship regression guard for SQL parameterization
- Acceptance checks:
  - Test detects vulnerable patterns (template literals in WHERE clauses) ✅
  - Test confirms safe patterns (parquetQuery with params array) ✅
  - Runs in CI via 'npm test --if-present' ✅
  - Currently passing with 1 warning (parquet.ts has no SQL queries) ✅
- Next action: awaiting Will's review/merge (low risk, high value security guard)
- Link: https://github.com/sportnumerics/rankings/pull/69
- Last update: test passing, depends on #68 (2026-03-15 09:00)

4) **#68 — Parameterize parquet SQL inputs**
- Status: PR (✅ all checks passing)
- Owner: assistant
- Outcome: replace string interpolation with bound parameters in all parquet queries
- First increment: security hardening for frontend DuckDB queries
- Acceptance checks:
  - All parquet.ts helper functions accept params array ✅
  - All query callsites use ? placeholders (teams.ts, players.ts, games.ts) ✅
  - Frontend lint passes ✅
  - Functionally identical behavior (mechanical refactor) ✅
- Next action: awaiting Will's review/merge (security best practice, low risk)
- Link: https://github.com/sportnumerics/rankings/pull/68
- Last update: all checks passing, awaiting review (2026-03-15 09:00)

5) **#59 — Goals leaders page**
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

6) **#57 — DuckDB parquet benchmark harness + JSON vs parquet S3 comparison**
- Status: PR
- Owner: assistant
- Outcome: reproducible baseline for cold/warm local+S3 query performance
- First increment: keep as reference benchmark suite
- Acceptance checks:
  - Includes local page-shaped timings
  - Includes JSON vs parquet S3 timings
- Next action: decide if needed post-#58 merge (can archive or keep for docs)
- Link: https://github.com/sportnumerics/rankings/pull/57

7) **#73 — docs: update CI status for PRs #70 and #71**
- Status: PR (✅ all checks passing)
- Owner: assistant
- Outcome: backlog documentation update
- Next action: awaiting Will's merge (docs-only, low priority)
- Link: https://github.com/sportnumerics/rankings/pull/73

8) **#72 — docs: sync backlog with CI status**
- Status: PR (✅ all checks passing)
- Owner: assistant
- Outcome: backlog documentation update
- Next action: awaiting Will's merge (docs-only, low priority)
- Link: https://github.com/sportnumerics/rankings/pull/72

9) **#74 — Vitest infrastructure and SQL security tests**
- Status: PR (🟡 CI running)
- Owner: assistant
- Outcome: Unit testing infrastructure with Vitest + SQL injection pattern detection
- First increment: establish test foundation with 9 passing tests
- Acceptance checks:
  - Vitest installed and configured ✅
  - Test scripts added to package.json (test, test:watch, test:ui) ✅
  - parquet.test.ts with 6 tests for dataModeFromSearch ✅
  - sql-security.test.ts detecting SQL injection patterns ✅
  - All tests passing locally (9/9) ✅
  - Tests detect current vulnerabilities in teams.ts, players.ts, games.ts ✅
- Next action: awaiting CI completion + Will's review
- Link: https://github.com/sportnumerics/rankings/pull/74
- Last update: PR created, CI running (2026-03-19 09:05)
- Note: Addresses backlog item "Unit tests for parquet query code paths"

### Ready
1) **WIP/PR velocity automation**
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
- ✅ GitHub auth fixed: replaced Python script with Node.js (2026-03-17)
- ✅ #67 Fix upcoming games showing empty in parquet mode (merged 2026-03-15)
- ✅ #58 DuckDB parquet materialized views with 12-file schema (merged 2026-03-15)
- ✅ #56 Fix NCAA upcoming games date labeling off-by-one (merged 2026-03-07)

## Backlog Notes (assistant-facing)
- Prefer tasks that improve user-visible value or reduce prediction-quality risk.
- Keep PRs small and reviewable.
- Every status change must update `Next action`.
