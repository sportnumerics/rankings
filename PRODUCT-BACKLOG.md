# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-04-10 09:00)

### PR
1) **#91 — Fix player page division error in parquet mode** ⭐ PROD BUG FIX
- Status: PR (✅ frontend tests, dev deploy, and E2E passing)
- Owner: assistant
- Outcome: parquet-mode player pages no longer fail when division must be discovered from JSON first
- Acceptance checks:
  - ✅ Frontend unit tests passing
  - ✅ Preview deployed to dev
  - ✅ E2E smoke tests passing
- Next action: Will review/merge for prod deploy
- Link: https://github.com/sportnumerics/rankings/pull/91
- Last update: CI green, ready for review (2026-04-03 11:15)

2) **#82 — Unit tests for parquet query code paths**
- Status: PR (✅ tests/dev deploy/E2E passing)
- Owner: assistant
- Outcome: Vitest coverage for parquet query path behavior
- Acceptance checks:
  - ✅ Frontend unit tests pass in CI
  - ✅ Preview deployed to dev
  - ✅ E2E smoke tests passing
- Next action: Will review/merge
- Link: https://github.com/sportnumerics/rankings/pull/82
- Last update: CI green, ready for review (2026-03-29 14:10)

3) **#86 — Assists leaders page**
- Status: PR (✅ all checks passing)
- Owner: assistant
- Outcome: /leaders/assists page showing top 50 assist leaders per division
- Acceptance checks:
  - ✅ Page loads at /2026/d1/leaders/assists
  - ✅ Shows top 50 players sorted by assists descending
  - ✅ Reuses existing PlayerRating data and PlayersCard UI
  - ✅ Frontend tests + dev deploy + E2E passing
- Next action: Will review/merge
- Link: https://github.com/sportnumerics/rankings/pull/86
- Last update: CI green, ready for review (2026-03-30 18:10)

4) **#59 — Goals leaders page**
- Status: PR (✅ all checks passing)
- Owner: assistant
- Outcome: /leaders/goals page showing top 50 scorers per division
- Acceptance checks:
  - ✅ Page loads at /2026/d1/leaders/goals
  - ✅ Shows top 50 players sorted by goals descending
  - ✅ Reuses existing PlayerRating data and PlayersCard UI
  - ✅ Frontend tests + dev deploy + E2E passing
- Next action: Will review/merge
- Link: https://github.com/sportnumerics/rankings/pull/59
- Last update: CI green, ready for review (2026-03-28 14:07)

5) **#76 — Points leaders page**
- Status: PR (✅ all checks passing)
- Owner: assistant
- Outcome: /leaders/points page showing top 50 points leaders per division
- Acceptance checks:
  - ✅ Page loads at /2026/d1/leaders/points
  - ✅ Shows top 50 players sorted by points descending
  - ✅ Reuses existing PlayerRating data and PlayersCard UI
  - ✅ Frontend tests + dev deploy + E2E passing
- Next action: Will review/merge
- Link: https://github.com/sportnumerics/rankings/pull/76
- Last update: CI green, ready for review (2026-03-21 14:09)

6) **#92 — PR health dashboard script**
- Status: PR (docs/tooling; ✅ checks passing)
- Owner: assistant
- Outcome: script to summarize stale/open PR state and unblock actions
- Acceptance checks:
  - ✅ PR validation checks passing
  - ✅ Produces actionable PR-health summary
- Next action: Will review/merge
- Link: https://github.com/sportnumerics/rankings/pull/92
- Last update: CI green, ready for review (2026-04-03 14:07)

7) **#90 — Backlog sync docs**
- Status: PR (docs only)
- Owner: assistant
- Outcome: PRODUCT-BACKLOG.md reflects current queue and priorities
- Acceptance checks:
  - Backlog matches active PR set
  - Next actions are explicit
- Next action: keep current while review queue is open
- Link: https://github.com/sportnumerics/rankings/pull/90
- Last update: refreshed for 2026-04-10 queue

8) **#93 — Feature discovery: position leaders recommendation**
- Status: PR (docs only)
- Owner: assistant
- Outcome: evidence-backed recommendation to build position-specific leaders next
- Acceptance checks:
  - ✅ Candidate list captured
  - ✅ Position leaders promoted as next build recommendation
- Next action: review/merge or fold into backlog notes
- Link: https://github.com/sportnumerics/rankings/pull/93
- Last update: created with recommendation (2026-04-04 11:13)

9) **Open PR review queue snapshot (2026-04-10 09:00 CT)**
- Status: PR hygiene update
- Open PRs still awaiting review: #93, #92, #91, #90, #86, #82, #76, #74, #70, #68, #59, #57
- Review decision state: all currently show `REVIEW_REQUIRED`
- Checks: no failing checks surfaced in the current open PR list snapshot; #91 remains the most production-relevant ready PR with frontend tests, dev deploy, and E2E green
- Queue note: review backlog remains the limiting factor; avoid opening another feature branch until at least one ready PR lands
- Next action: review/merge #91 first, then #82 or #86 to reopen build capacity

### Ready
1) **Position-specific leader boards** ⭐ next build after review queue moves
- Status: Ready
- Owner: assistant
- Outcome: attack/midfield/defense/goalie/faceoff filtered leader pages using existing position data
- First increment: ship one position-filtered leaders page end-to-end
- Acceptance checks:
  - Page renders with correct position filter
  - Uses existing player/parquet query pipeline
  - Tests cover position filter behavior
- Next action: start after at least one of #91 / #82 / #86 merges
- Context: recommended by PR #93; position data already exists in scraper + parquet export

2) **WIP/PR velocity automation**
- Status: Ready
- Owner: assistant
- Outcome: fewer stalls, faster PR throughput
- First increment: daily stale-PR check with concrete unblock actions
- Acceptance checks:
  - Daily update includes active PR state + next unblock step
  - blockers explicitly tagged with owner
- Next action: merge #92, then use it daily

### In Progress
- (none)

### Blocked
- **New feature work is intentionally blocked on review bandwidth.**
- Current unblock owner: Will
- Unblock condition: review/merge highest-priority ready PRs (#91 first, then #82/#86)
- 2026-04-10 check: queue still fully review-blocked; no new in-progress feature branch should be opened until at least one ready PR lands

## Done (recent)
- ✅ #89 HOTFIX: Firefox + Playwright bypasses Akamai on stats.ncaa.org (merged 2026-04-01)
- ✅ #58 DuckDB parquet materialized views (merged 2026-03-13)
- ✅ #56 Fix NCAA upcoming games date labeling off-by-one (merged 2026-03-07)

## Backlog Notes (assistant-facing)
- Prefer tasks that improve user-visible value or reduce prediction-quality risk.
- Keep PRs small and reviewable.
- Every status change must update `Next action`.
- Feature discovery sprint completed 2026-03-30 (see docs/feature-discovery-2026-03-30.md)
- Current focus: ship leader pages (#86, #76, #59) then goalie stats
