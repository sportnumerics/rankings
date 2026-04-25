# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-04-24)

### PR
1) **#96 — Harden division lookup and incomplete game rendering**
- Status: PR
- Owner: assistant
- Outcome: shared division resolution and game detail pages fail safely instead of crashing on malformed or partial data
- Current increment: frontend hardening shipped to PR and dev
- Acceptance checks:
  - `/api/[year]/div` returns a stable JSON object shape for success and error paths
  - client division lookup handles non-OK responses explicitly
  - incomplete game payloads do not crash the game detail page
  - `cd frontend && npm run build` passes
- Next action: Will review/merge incident fix
- Link: https://github.com/sportnumerics/rankings/pull/96
- Last update: PR opened, checks green (2026-04-23 10:25 PM CDT)

2) **#91 — Fix player page division error in parquet mode**
- Status: PR
- Owner: assistant
- Outcome: player pages resolve division correctly in parquet mode
- Current increment: fix complete and validated in CI/dev
- Acceptance checks:
  - player page no longer throws division resolution errors in parquet mode
  - frontend tests pass
  - deploy + E2E checks pass
- Next action: merge after reviewing overlap with #96
- Link: https://github.com/sportnumerics/rankings/pull/91
- Last update: checks green, review required (2026-04-03)

3) **#95 — Sync backlog to current PR queue**
- Status: PR
- Owner: assistant
- Outcome: backlog reflects the live queue and explicit priorities
- Current increment: refresh to current 2026-04-24 queue and stale-PR decisions
- Acceptance checks:
  - PRODUCT-BACKLOG.md matches current open PR ordering
  - stale PRs have explicit keep/close recommendations
  - next implementation target is clear once merge queue moves
- Next action: review/merge after confirming queue ordering looks right
- Link: https://github.com/sportnumerics/rankings/pull/95
- Last update: backlog refreshed for #96 + stale PR cleanup recommendations (2026-04-24 09:00 AM CDT)

4) **#86 — Assists leaders page**
- Status: PR
- Owner: assistant
- Outcome: `/leaders/assists` page showing top assist leaders per division
- First increment: ship MVP assists leaders page
- Acceptance checks:
  - page loads at `/2026/d1/leaders/assists`
  - shows top 50 players sorted by assists descending
  - reuses existing leaders page patterns/UI
- Next action: awaiting Will's review
- Link: https://github.com/sportnumerics/rankings/pull/86
- Last update: checks green, review required (2026-03-30)

5) **#82 — Unit tests for parquet query code paths**
- Status: PR
- Owner: assistant
- Outcome: frontend parquet query paths have regression coverage
- Current increment: baseline parquet query tests merged into one PR
- Acceptance checks:
  - tests cover ranked teams / players / games parquet mode
  - tests verify fallback behavior and debug metadata
  - CI passes
- Next action: awaiting Will's review
- Link: https://github.com/sportnumerics/rankings/pull/82
- Last update: checks green, review required (2026-03-29)

6) **#59 — Goals leaders page**
- Status: PR
- Owner: assistant
- Outcome: `/leaders/goals` page showing top scorers per division
- First increment: ship MVP goals leaders page
- Acceptance checks:
  - page loads at `/2026/d1/leaders/goals`
  - shows top 50 players sorted by goals descending
  - reuses existing PlayerRating data and PlayersCard UI
- Next action: awaiting Will's review
- Link: https://github.com/sportnumerics/rankings/pull/59
- Last update: checks green, review required (2026-03-28)

### In Progress
- (none)

### Ready
1) **Position-specific leaders pages**
- Status: Ready
- Owner: assistant
- Outcome: leaders filtered for attack, midfield, defense, goalie, and faceoff specialists
- First increment: ship one position-specific leaderboard using existing player stats/parquet data
- Acceptance checks:
  - at least one position-specific leaders page loads for 2026/d1
  - query/filter uses existing position data without ad hoc scraping changes
  - tests or focused validation cover the position filter path
- Next action: start after #96 / #91 / #95 merge queue moves

### Done
- ✅ #90 closed as superseded by newer backlog sync PR #95 (2026-04-25)
- ✅ #93 closed as superseded by shipped/active leaders work and current backlog ordering (2026-04-25)
- ✅ #92 closed as unused review surface; backlog driver already gets the same queue signal directly from `gh` (2026-04-25)
- ✅ #94 Fix NCAA player stats scrape regression coverage + CI timeout handling (merged 2026-04-22)
- ✅ #56 Fix NCAA upcoming games date labeling off-by-one (merged 2026-03-07)

## Backlog Notes (assistant-facing)
- Prioritize reviewable PR throughput before starting new feature work.
- Incident fixes beat roadmap work.
- Keep PRs small, user-visible when possible, and test-backed.
- Every status change must update `Next action`.
- When backlog docs go stale, refresh them against live `gh pr list`, not memory.
