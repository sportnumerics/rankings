# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-03-21)

### PR
1) **#76 — Points leaders page**
- Status: PR (✅ all checks passing)
- Owner: assistant
- Outcome: /leaders/points page showing top 50 points leaders per division (completes goals/assists/points trio)
- First increment: ship MVP points leaders page
- Acceptance checks:
  - Page loads at /2026/d1/leaders/points ✅
  - Shows top 50 players sorted by points (goals + assists) descending ✅
  - Reuses existing PlayerRating data and PlayersCard UI ✅
  - All CI checks passing ✅
- Next action: awaiting Will's review/merge
- Link: https://github.com/sportnumerics/rankings/pull/76
- Last update: all checks passing (2026-03-21 09:10)

2) **#75 — PR velocity automation**
- Status: PR
- Owner: assistant
- Outcome: automated daily check for stale PRs (>24h, passing CI, awaiting review)
- First increment: Python script to identify review bottlenecks
- Acceptance checks:
  - Script lists PRs >24h with passing CI ✅
  - Provides velocity metrics (passing/stale/failing counts) ✅
  - Can be integrated into daily heartbeat checks ✅
- Next action: awaiting Will's review
- Link: https://github.com/sportnumerics/rankings/pull/75
- Last update: opened 2026-03-20

2) **#74 — Vitest infrastructure + SQL security tests**
- Status: PR
- Owner: assistant
- Outcome: unit testing infrastructure with Vitest, replaces standalone #69
- First increment: Vitest setup + parquet query tests + SQL injection detection
- Acceptance checks:
  - Vitest configured with Next.js compatibility ✅
  - Test scripts added (test, test:watch, test:ui) ✅
  - 6 tests for dataModeFromSearch function ✅
  - SQL security tests detect injection patterns ✅
  - All 9 tests passing ✅
- Next action: awaiting Will's review (supersedes #69)
- Link: https://github.com/sportnumerics/rankings/pull/74
- Last update: opened 2026-03-19
- Note: Once merged, can make SQL security tests fail on violations (currently warnings)

3) **#71 — Assists leaders page**
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
- Last update: all checks passing (2026-03-17 09:21), stale 4 days

4) **#70 — Per-game stat averages (PPG/GPG/APG)**
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
- Last update: all checks passing (2026-03-17 09:29), stale 4 days

5) **#68 — Parameterize parquet SQL inputs**
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
- Last update: all checks passing, stale 7 days (2026-03-15 09:00)

6) **#59 — Goals leaders page**
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
- Last update: review requested, all checks passing, stale 13 days (2026-03-09 09:15)

7) **#57 — DuckDB parquet benchmark harness + JSON vs parquet S3 comparison**
- Status: PR
- Owner: assistant
- Outcome: reproducible baseline for cold/warm local+S3 query performance
- First increment: keep as reference benchmark suite
- Acceptance checks:
  - Includes local page-shaped timings
  - Includes JSON vs parquet S3 timings
- Next action: decide if needed post-#58 merge (can archive or keep for docs)
- Link: https://github.com/sportnumerics/rankings/pull/57

### Ready
- (none - all Ready items now in PR)

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
