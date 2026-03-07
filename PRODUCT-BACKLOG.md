# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-03-07)

### PR
1) **#58 — DuckDB parquet mode toggle + team/player query optimizations**
- Status: PR
- Owner: assistant
- Outcome: dev-testable parquet path behind `?dataMode=parquet` with request-level range instrumentation
- First increment: ship top 3 optimizations for team/player pages and expose debug footer
- Acceptance checks:
  - Team page supports `?dataMode=parquet` via flat games parquet path
  - Player page supports `?dataMode=parquet` via optimized ratings path
  - Footer displays query ms + HEAD/GET/range/bytes stats
- Next action: wait for Frontend Unit Tests on #58, then request review
- Link: https://github.com/sportnumerics/rankings/pull/58
- Last update: PR opened with toggle + instrumentation (2026-03-07 16:06)

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
2) **Feature discovery sprint: highest-value near-term product improvement**
- Status: Ready
- Owner: assistant
- Outcome: one evidence-backed feature promoted to build
- First increment: produce top-5 candidate list with value/effort/risk and choose #1
- Acceptance checks:
  - Top-5 list captured in backlog notes
  - One candidate converted into implementation-ready task
- Next action: research 5 candidates from competitor + current site gaps

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

## Backlog Notes (assistant-facing)
- Prefer tasks that improve user-visible value or reduce prediction-quality risk.
- Keep PRs small and reviewable.
- Every status change must update `Next action`.
