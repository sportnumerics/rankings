# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-03-07)

### PR
1) **#54 — Backtest CI + sticky PR comment + CLI backtest command**
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
2) **Multi-category leaders pages (assists + saves)**
- Status: Ready
- Owner: assistant
- Outcome: `/leaders/assists` and `/leaders/saves` pages showing top 50 performers
- First increment: implement assists leaders page reusing goals leaders infrastructure
- Acceptance checks:
  - `/2026/d1/leaders/assists` loads with top 50 by assists descending
  - `/2026/d1/leaders/saves` loads with top 50 by saves descending
  - Reuses PlayersCard component from goals leaders
  - All E2E tests pass
- Next action: implement assists page on new branch (feature-assists-leaders)
- Research: see `feature-discovery-top5.md` for full analysis

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
