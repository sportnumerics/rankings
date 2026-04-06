# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-03-15)

### PR
1) **#69 — SQL parameterization validation test**
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

2) **#68 — Parameterize parquet SQL inputs**
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

4) **#57 — DuckDB parquet benchmark harness + JSON vs parquet S3 comparison**
- Status: PR
- Owner: assistant
- Outcome: reproducible baseline for cold/warm local+S3 query performance
- First increment: keep as reference benchmark suite
- Acceptance checks:
  - Includes local page-shaped timings
  - Includes JSON vs parquet S3 timings
- Next action: decide if needed post-#58 merge (can archive or keep for docs)
- Link: https://github.com/sportnumerics/rankings/pull/57

### In Progress
1) **Per-game stat averages (PPG/GPG/APG)**
- Status: In Progress → Blocked (GitHub auth)
- Owner: assistant
- Outcome: Add per-game averages to player stats (standard across competitor sites)
- Current increment: Backend + frontend complete (4 commits), cannot push
- Acceptance checks:
  - Backend: player stats JSON includes `games_played` field ✅
  - Backend: games_played counts games with non-zero goals or assists ✅
  - Frontend: Players table shows G, A, GP, PPG, GPG, APG columns ✅
  - Frontend: Per-game columns conditional on data availability ✅
  - Division-by-zero handled gracefully (gp > 0 check) ✅
  - All unit tests passing ✅
- Value/Effort: ⭐⭐⭐⭐ value, ⭐⭐ effort, low risk
- **Blocker:** Python 3.8 + cryptography library incompatibility breaks github-app-token.py
- Next action: Will must apply fix from GITHUB-AUTH-FIX.md (3 options), then push + PR
- Branch: feature-per-game-stats (4 commits, local only)
- Context: Feature discovery sprint complete (see FEATURE-DISCOVERY-2026-03.md)

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
- Note: Work attempted in add-parquet-unit-tests branch but not merged

4) **WIP/PR velocity automation**
- Status: Ready
- Owner: assistant
- Outcome: fewer stalls, faster PR throughput
- First increment: daily stale-PR check with concrete unblock actions
- Acceptance checks:
  - Daily update includes active PR state + next unblock step
  - blockers explicitly tagged with owner
- Next action: add "stale >24h" handling notes to this file and use daily



### Blocked
1) **GitHub authentication (Python 3.8 incompatibility)**
- Status: Blocking all PR operations
- Owner: Will
- Outcome: Restore ability to push branches and create PRs
- Blocker: `github-app-token.py` fails with `TypeError: 'type' object is not subscriptable`
- Impact: Cannot ship per-game stats feature (4 commits ready), cannot create PRs for future work
- Next action: Apply one of three fixes in GITHUB-AUTH-FIX.md (upgrade Python 3.9 recommended)
- Added: 2026-03-17 09:00

## Done
- ✅ #67 Fix upcoming games showing empty in parquet mode (merged 2026-03-15)
- ✅ #58 DuckDB parquet materialized views with 12-file schema (merged 2026-03-15)
- ✅ #56 Fix NCAA upcoming games date labeling off-by-one (merged 2026-03-07)

## Backlog Notes (assistant-facing)
- Prefer tasks that improve user-visible value or reduce prediction-quality risk.
- Keep PRs small and reviewable.
- Every status change must update `Next action`.
