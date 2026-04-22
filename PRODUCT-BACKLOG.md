# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-04-22)

### PR
1) **#94 — Fix NCAA player stats scraping**
- Status: PR
- Owner: assistant
- Outcome: keep NCAA player stat ingestion reliable enough for rankings + leaders pages
- Current increment: regression coverage for live `individual_stats` fetches plus CI timeout hardening for ECS task completion detection
- Acceptance checks:
  - `lib.scrape.test_playwright_fetcher` and `lib.scrape.test_ncaa` pass
  - PR validation passes, including `Run Backend (Limited Scrape)`
  - Limited NCAA scrape produces game details with player stat payloads
- Next action: ask Will to review/merge now that all checks are green
- Link: https://github.com/sportnumerics/rankings/pull/94
- Last update: CI rerun fully green after ECS-missing handling fix (2026-04-22 08:21 CDT)

2) **#91 — Fix player page division error in parquet mode**
- Status: PR
- Owner: assistant
- Outcome: player pages resolve the correct division in parquet mode without runtime errors
- Current increment: hotfix shipped to dev and validated in CI
- Acceptance checks:
  - Player page loads in parquet mode for valid players/divisions
  - Frontend unit tests pass
  - E2E tests pass
- Next action: review/merge after #94 incident work is cleared
- Link: https://github.com/sportnumerics/rankings/pull/91
- Last update: all checks passing on open PR (2026-04-03 06:15 CDT)

3) **#86 — Assists leaders page**
- Status: PR
- Owner: assistant
- Outcome: /leaders/assists page showing top assist leaders per division
- Current increment: MVP page implemented and validated in CI/dev
- Acceptance checks:
  - Page loads at `/2026/d1/leaders/assists`
  - Shows top 50 players sorted by assists descending
  - Reuses existing leader page/UI patterns
- Next action: review/merge after higher-priority bugfix PRs
- Link: https://github.com/sportnumerics/rankings/pull/86
- Last update: all checks passing on open PR (2026-03-30 01:10 PM CDT)

4) **#82 — Unit tests for parquet query code paths**
- Status: PR
- Owner: assistant
- Outcome: systematic test coverage for parquet.ts query functions and server data loaders
- Current increment: first coverage slice landed and CI/dev passed
- Acceptance checks:
  - Tests cover parquet query construction + fallback behavior
  - Frontend unit tests pass
  - E2E tests pass
- Next action: review/merge before adding more parquet-mode surface area
- Link: https://github.com/sportnumerics/rankings/pull/82
- Last update: all checks passing on open PR (2026-03-29 09:10 AM CDT)

5) **#59 — Goals leaders page**
- Status: PR
- Owner: assistant
- Outcome: /leaders/goals page showing top 50 scorers per division
- Current increment: MVP page implemented and validated in CI/dev
- Acceptance checks:
  - Page loads at `/2026/d1/leaders/goals`
  - Shows top 50 players sorted by goals descending
  - Reuses existing `PlayersCard` UI
- Next action: review/merge after more urgent PRs above
- Link: https://github.com/sportnumerics/rankings/pull/59
- Last update: all checks passing on open PR (2026-03-28 09:07 AM CDT)

### Ready
1) **PR review + merge queue cleanup**
- Status: Ready
- Owner: Will
- Outcome: reduce WIP and unblock the next feature branch by merging the highest-value green PRs
- First increment: review `#94`, then `#91`, then `#82/#86` depending on product priority
- Acceptance checks:
  - At least one green PR merged
  - Merge order is explicit in this file / daily update
  - Next build target is chosen after queue shrinks
- Next action: merge or comment on the highest-priority green PR

2) **Position-specific leaders pages**
- Status: Ready
- Owner: assistant
- Outcome: attack/midfield/defense/goalie/faceoff leader views using already-exported position data
- First increment: ship one position-filtered leaders page behind the existing leaders patterns
- Acceptance checks:
  - One leaders page can filter by position using parquet-backed data
  - Position filter behavior is covered by tests or existing query coverage
  - Backlog includes follow-up slices for remaining positions
- Next action: start only after current merge queue moves

3) **WIP/PR velocity automation**
- Status: Ready
- Owner: assistant
- Outcome: fewer stale PRs and faster review throughput
- First increment: daily stale-PR check with concrete unblock actions
- Acceptance checks:
  - Daily update includes active PR state + next unblock step
  - blockers explicitly tagged with owner
  - stale PRs are summarized in priority order
- Next action: keep this file synced to actual PR state during backlog-driver runs

### In Progress
- (none — prefer merge queue reduction before opening new implementation work)

### Blocked
- (none)

## Done
- ✅ #56 Fix NCAA upcoming games date labeling off-by-one (merged 2026-03-07)

## Backlog Notes (assistant-facing)
- Prefer tasks that improve user-visible value or reduce prediction-quality risk.
- Keep PRs small and reviewable.
- Every status change must update `Next action`.
