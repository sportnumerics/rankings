# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-03-07)

### PR
1) **#62 — Unit test coverage for parquet query code paths**
- Status: PR
- Owner: assistant
- Outcome: Vitest framework + tests for parquet.ts and teams.ts query logic
- Current increment: Basic test coverage for SQL construction and debug metadata
- Acceptance checks:
  - Vitest configured with node environment ✅
  - Tests verify SQL query construction (div filtering, sorting, column selection) ✅
  - Tests verify debug metadata structure ✅
  - All tests pass in CI (pending)
- Next action: awaiting Will's review
- Link: https://github.com/sportnumerics/rankings/pull/62
- Last update: created with Vitest setup + initial tests (2026-03-11 06:23)

2) **#54 — Backtest CI + sticky PR comment + CLI backtest command**
- Status: PR
- Owner: assistant
- Outcome: one canonical backtest path (local + CI) and visible PR quality signal
- First increment: finish review fixes and get green checks
- Acceptance checks:
  - CI backtest job passes
  - PR comment updates with summary table
  - command `python main.py --year 2024-2025 backtest --data-dir ... --out-dir ...` works
- Next action: verify CI passes after lazy-import fix (c067b33), then request merge
- Link: https://github.com/sportnumerics/rankings/pull/54
- Last update: Fixed ModuleNotFoundError in backend by lazy-loading backtest_baseline (2026-03-07 09:00)

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
