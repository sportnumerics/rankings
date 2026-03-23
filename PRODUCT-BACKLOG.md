# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-03-23 09:00)

### PR (Ready for Review - All Checks Passing)
1) **#79 — Expand parquet query test coverage (players + games)**
- Status: PR (✅ all checks passing)
- Owner: assistant
- Outcome: comprehensive unit tests for players.ts and games.ts parquet queries
- First increment: increase test coverage for data layer
- Acceptance checks:
  - Tests cover dataModeFromSearch edge cases ✅
  - Tests validate query parameter handling ✅
  - All 9 tests passing ✅
- Next action: awaiting Will's review/merge
- Link: https://github.com/sportnumerics/rankings/pull/79
- Last update: all checks passing (2026-03-22 09:10)

2) **#76 — Points leaders page**
- Status: PR (✅ all checks passing)
- Owner: assistant
- Outcome: /leaders/points page showing top 50 point leaders per division
- First increment: ship MVP points leaders page
- Acceptance checks:
  - Page loads at /2026/d1/leaders/points ✅
  - Shows top 50 players sorted by points descending ✅
  - Reuses existing PlayerRating data and PlayersCard UI ✅
- Next action: awaiting Will's review/merge
- Link: https://github.com/sportnumerics/rankings/pull/76
- Last update: all checks passing (2026-03-21 09:09)

3) **#74 — Vitest infrastructure and SQL security tests**
- Status: PR (✅ all checks passing)
- Owner: assistant
- Outcome: Unit testing infrastructure with Vitest + SQL injection pattern detection
- First increment: establish test foundation with 9 passing tests
- Acceptance checks:
  - Vitest installed and configured ✅
  - Test scripts added to package.json (test, test:watch, test:ui) ✅
  - parquet.test.ts with 6 tests for dataModeFromSearch ✅
  - sql-security.test.ts detecting SQL injection patterns ✅
  - All tests passing (9/9) ✅
  - Tests detect current vulnerabilities in teams.ts, players.ts, games.ts ✅
- Next action: awaiting Will's review/merge
- Link: https://github.com/sportnumerics/rankings/pull/74
- Last update: all checks passing (2026-03-19 22:11)

4) **#71 — Assists leaders page**
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

5) **#70 — Per-game stat averages (PPG/GPG/APG)**
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

6) **#68 — Parameterize parquet SQL inputs**
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

7) **#59 — Goals leaders page**
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

### PR Velocity Status
**Current bottleneck:** 7 PRs awaiting review with all checks passing
- **High priority (features):** #76 (points leaders), #71 (assists leaders), #70 (per-game stats)
- **Medium priority (tests):** #79 (parquet tests), #74 (Vitest infrastructure)
- **Low priority (security):** #68 (SQL parameterization)
- **Low priority (features):** #59 (goals leaders)

**Stale >24h:** All feature PRs above are >24h old with passing checks
**Unblock action:** Will review + merge decision on top 3 feature PRs

**Note:** New docs PRs (#77, #78) and automation PR (#75) not included to avoid further queue buildup

### Ready
1) **WIP/PR velocity automation**
- Status: Ready → In Progress (PR #75 open)
- Owner: assistant
- Outcome: fewer stalls, faster PR throughput
- First increment: daily stale-PR check with concrete unblock actions
- Acceptance checks:
  - Daily update includes active PR state + next unblock step
  - blockers explicitly tagged with owner
- Next action: PR #75 awaiting review
- Link: https://github.com/sportnumerics/rankings/pull/75

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
