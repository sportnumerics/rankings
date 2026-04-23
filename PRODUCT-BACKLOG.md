# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-04-23)

### PR
1) **#91 — Fix player page division error in parquet mode**
- Status: PR
- Owner: assistant
- Outcome: player pages resolve the correct division in parquet mode without runtime errors
- Current increment: hotfix shipped to dev and validated in CI
- Acceptance checks:
  - Player page loads in parquet mode for valid players/divisions
  - Frontend unit tests pass
  - E2E tests pass
- Next action: ask Will to review/merge now that #94 is already merged
- Link: https://github.com/sportnumerics/rankings/pull/91
- Last update: promoted to top merge target after #94 merged (2026-04-22 06:30 PM CDT)

2) **#95 — Sync backlog to current PR queue**
- Status: PR
- Owner: assistant
- Outcome: keep PRODUCT-BACKLOG.md aligned with the actual open/merged queue
- Current increment: follow-up refresh after #94 merged so this file stops pointing at already-finished work
- Acceptance checks:
  - Active PR list matches `gh pr list`
  - Recently merged work is moved to Done
  - Merge priorities are explicit
- Next action: merge after confirming this file reflects the live queue
- Link: https://github.com/sportnumerics/rankings/pull/95
- Last update: backlog corrected for #94 merge + current open PR ordering (2026-04-23 09:00 AM CDT)

3) **#86 — Assists leaders page**
- Status: PR
- Owner: assistant
- Outcome: /leaders/assists page showing top assist leaders per division
- Current increment: MVP page implemented and validated in CI/dev
- Acceptance checks:
  - Page loads at `/2026/d1/leaders/assists`
  - Shows top 50 players sorted by assists descending
  - Reuses existing leader page/UI patterns
- Next action: review/merge after #91 and backlog cleanup
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
- First increment: review `#91`, then `#95`, then `#82/#86` depending on product priority
- Acceptance checks:
  - At least one green PR merged
  - Merge order is explicit in this file / daily update
  - Next build target is chosen after queue shrinks
- Next action: merge or comment on #91 first

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

3) **Stale PR cleanup decisions (`#90`, `#93`, `#92`)**
- Status: Ready
- Owner: assistant
- Outcome: reduce duplicate docs/workflow noise in the queue so active implementation PRs are obvious
- First increment: decide whether each PR should merge, supersede, or close based on overlap with #95 and current priorities
- Acceptance checks:
  - each stale PR has an explicit keep/close decision
  - backlog references only still-actionable PRs as active priorities
  - next review request is unambiguous
- Next action: make cleanup recommendations in the daily update; avoid opening new feature work until this is settled

### In Progress
- (none — prefer merge queue reduction before opening new implementation work)

### Blocked
- (none)

## Done
- ✅ #94 Fix NCAA player stats scraping (merged 2026-04-22)
- ✅ #56 Fix NCAA upcoming games date labeling off-by-one (merged 2026-03-07)

## Backlog Notes (assistant-facing)
- Prefer tasks that improve user-visible value or reduce prediction-quality risk.
- Keep PRs small and reviewable.
- Every status change must update `Next action`.
