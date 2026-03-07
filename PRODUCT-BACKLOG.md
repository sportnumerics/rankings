# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-03-07)

### PR
1) **#57 — DuckDB parquet benchmark harness + low-hanging perf paths**
- Status: PR
- Owner: assistant
- Outcome: quantified local + S3 parquet query latency and identified fastest query shapes
- First increment: benchmark page-shaped queries and publish actionable optimizations
- Acceptance checks:
  - Bench script runs against current prod parquet layout
  - Warm/cold timings captured for rankings/upcoming/team/player shapes
  - At least 3 concrete optimization recommendations documented
- Next action: incorporate S3-cold benchmark notes into PR description and request review
- Link: https://github.com/sportnumerics/rankings/pull/57
- Last update: Added S3 cold-start timings; biggest delta is schedule unnest vs flat games path (2026-03-07 12:49)

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
- ✅ #54 Backtest CI + sticky PR comment + CLI backtest command (merged 2026-03-07)

## Backlog Notes (assistant-facing)
- Prefer tasks that improve user-visible value or reduce prediction-quality risk.
- Keep PRs small and reviewable.
- Every status change must update `Next action`.
