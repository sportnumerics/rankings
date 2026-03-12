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
- Current increment: Phase 1 + Phase 2 COMPLETE
- Acceptance checks:
  - Backend: `python main.py export-parquet` generates all 12 files ✅
  - Backend: integrated into `all` workflow ✅
  - Frontend: all pages query correct file with optimal filters ✅
  - Footer displays query ms + file read stats ✅
- Next action: awaiting Will's review to merge and proceed to Phase 3 (flip default)
- Link: https://github.com/sportnumerics/rankings/pull/58
- Last update: Phase 1+2 complete - all pages support ?dataMode=parquet (2026-03-09 19:30)

3) **#57 — DuckDB parquet benchmark harness + JSON vs parquet S3 comparison**
- Status: PR
- Owner: assistant
- Outcome: reproducible baseline for cold/warm local+S3 query performance
- First increment: keep as reference benchmark suite
- Acceptance checks:
  - Includes local page-shaped timings
  - Includes JSON vs parquet S3 timings
- Next action: decide merge order with #58 (can keep #57 for benchmarking docs)
- Link: https://github.com/sportnumerics/rankings/pull/57

4) **#62 — Unit test coverage for parquet query code paths**
- Status: PR
- Owner: assistant
- Outcome: Vitest coverage for parquet.ts and teams loader parquet/fallback logic
- Current increment: fixed Data.map chaining in teams fallback/json tests after CI failure
- Acceptance checks:
  - Tests verify SQL query construction (div filtering, sorting, column selection) ✅
  - Tests verify fallback behavior when parquet fails ✅
  - Tests verify debug metadata structure ✅
  - Frontend Unit Tests check in PR Validation passes (rerun pending)
- Next action: rerun/observe CI for PR #62 and request merge once green
- Link: https://github.com/sportnumerics/rankings/pull/62
- Last update: pushed fix commit 1b87dae (2026-03-11 09:04)

### Ready
2) **Multi-Category Player Leaders Hub (Saves/Faceoffs/Ground Balls)**
- Status: Ready
- Owner: assistant
- Outcome: Expand player leaders beyond goals/assists to saves, faceoff %, ground balls, caused turnovers
- Context: Natural extension of PRs #59 (goals) and #61 (assists); fills gap vs Laxnumbers
- Blocker: Requires backend PlayerRating extension (saves, faceoffs, gb, ct fields) + aggregation logic
- First increment: Add saves/ga fields to PlayerRating + export-parquet saves-leaders file + frontend page
- Acceptance checks (Phase 1 - Saves):
  - Backend: PlayerRating includes `saves` and `ga` (goals against) fields
  - Backend: player_ratings computation aggregates saves from Player.stats
  - Backend: export_saves_leaders() generates saves-leaders.parquet
  - Frontend: /leaders/saves page shows top 50 goalies sorted by saves descending
  - Minimum games threshold applied (5+ games)
- Next action: Phase 1 backend work (extend PlayerRating + aggregation)
- Link to discovery: FEATURE-DISCOVERY-2026-03-12.md (top-5 analysis)

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
- ✅ Feature discovery sprint (2026-03-12): Top-5 candidates analyzed, #1 (Multi-Category Leaders Hub) promoted to Ready
  - See: FEATURE-DISCOVERY-2026-03-12.md for full analysis
  - Recommendation: Saves leaders → Faceoff leaders → Ground balls → Caused turnovers

## Backlog Notes (assistant-facing)
- Prefer tasks that improve user-visible value or reduce prediction-quality risk.
- Keep PRs small and reviewable.
- Every status change must update `Next action`.
