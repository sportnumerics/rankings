# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-05-01)

### PR
1) **#97 — Restore prod division lookup and harden NCAA scraping**
- Status: PR
- Owner: assistant
- Outcome: production division lookup works again and NCAA scraping recovers cleanly from Playwright browser/page closure
- Current increment: prod hotfix + scraper hardening shipped to review with full validation green
- Acceptance checks:
  - `/api/[year]/div` resolves divisions without depending on parquet/DuckDB
  - NCAA scraping retries still handle queue-full / blocked responses
  - Scraper relaunches Firefox when Playwright page/context/browser closes mid-run
  - Backend/frontend validation listed in PR passes in CI
- Next action: merge first after Will review
- Link: https://github.com/sportnumerics/rankings/pull/97
- Last update: opened with all checks passing (2026-05-01 03:43 UTC)

2) **#95 — Sync backlog to current PR queue**
- Status: PR
- Owner: assistant
- Outcome: PRODUCT-BACKLOG.md matches the live queue and current merge order
- Current increment: refresh queue snapshot for the 2026-05-01 state
- Acceptance checks:
  - Open PR list matches `gh pr list`
  - Merge priority reflects incidents first, then oldest/highest-value reviewable work
  - `Next action` fields point at the real unblock step
- Next action: keep this PR current while review remains blocked elsewhere
- Link: https://github.com/sportnumerics/rankings/pull/95
- Last update: queue refreshed for #97 at the top (2026-05-01 09:00 CDT)

3) **#91 — Fix player page division error in parquet mode**
- Status: PR
- Owner: assistant
- Outcome: player pages resolve division correctly in parquet mode
- First increment: ship the parquet-mode division fix already in review
- Acceptance checks:
  - Player page no longer throws division lookup errors in parquet mode
  - Frontend unit tests and E2E stay green
- Next action: merge right after #97
- Link: https://github.com/sportnumerics/rankings/pull/91
- Last update: review required, checks passing (2026-04-03 11:15 UTC)

4) **#86 — Assists leaders page**
- Status: PR
- Owner: assistant
- Outcome: `/leaders/assists` page showing top 50 assist leaders per division
- First increment: MVP assists leaders page already built and in review
- Acceptance checks:
  - Page loads at `/2026/d1/leaders/assists`
  - Shows top 50 players sorted by assists descending
  - Reuses existing player leader UI patterns
- Next action: review after #97 / #95 / #91 merge sequence starts moving
- Link: https://github.com/sportnumerics/rankings/pull/86
- Last update: review required, checks passing (2026-03-30 18:10 UTC)

5) **#82 — Unit tests for parquet query code paths**
- Status: PR
- Owner: assistant
- Outcome: stronger automated coverage for parquet query construction and fallback paths
- First increment: tests for ranked teams/players/games query behavior
- Acceptance checks:
  - Tests verify division filtering, sorting, and selected columns
  - Tests verify fallback behavior when parquet fails
  - Tests verify debug metadata shape
  - CI passes
- Next action: review after higher-priority product/user-facing PRs
- Link: https://github.com/sportnumerics/rankings/pull/82
- Last update: review required, checks passing (2026-03-29 14:10 UTC)

6) **#76 — Points leaders page**
- Status: PR
- Owner: assistant
- Outcome: `/leaders/points` page showing top 50 point leaders per division
- First increment: MVP points leaders page already built and in review
- Acceptance checks:
  - Page loads at `/2026/d1/leaders/points`
  - Shows top 50 players sorted by points descending
  - Reuses existing player leader UI patterns
- Next action: revisit after assists/goals merge order is clearer
- Link: https://github.com/sportnumerics/rankings/pull/76
- Last update: review required, checks passing (2026-03-21 14:09 UTC)

7) **#74 — Vitest infrastructure and SQL security tests**
- Status: PR
- Owner: assistant
- Outcome: frontend Vitest coverage and SQL security tests in place
- First increment: infrastructure and parameterization test coverage already built
- Acceptance checks:
  - Vitest runs in CI
  - SQL security checks cover unsafe interpolation regressions
  - Existing frontend test workflows stay green
- Next action: refresh/rebase only after #68 lands, because the security work should merge first
- Link: https://github.com/sportnumerics/rankings/pull/74
- Last update: review required, checks passing (2026-03-19 22:11 UTC)

8) **#70 — Per-game stat averages (PPG/GPG/APG)**
- Status: PR
- Owner: assistant
- Outcome: per-game leader views and averages exposed in the product
- First increment: per-game stat averages implementation already built and in review
- Acceptance checks:
  - Per-game averages display correctly on leader pages
  - Validation suite passes
- Next action: revisit after the core leaders/security queue moves
- Link: https://github.com/sportnumerics/rankings/pull/70
- Last update: review required, checks passing (2026-03-17 14:29 UTC)

9) **#68 — Parameterize parquet SQL inputs**
- Status: PR
- Owner: assistant
- Outcome: parquet SQL input handling is parameterized instead of interpolated
- First increment: security hardening PR already built and in review
- Acceptance checks:
  - User-controlled SQL inputs are parameterized
  - Frontend tests and E2E stay green
- Next action: merge before refreshing/rebasing #74
- Link: https://github.com/sportnumerics/rankings/pull/68
- Last update: review required, checks passing (2026-03-14 02:23 UTC)

10) **#59 — Goals leaders page**
- Status: PR
- Owner: assistant
- Outcome: `/leaders/goals` page showing top 50 goal scorers per division
- First increment: MVP goals leaders page already built and in review
- Acceptance checks:
  - Page loads at `/2026/d1/leaders/goals`
  - Shows top 50 players sorted by goals descending
  - Reuses existing player leader UI patterns
- Next action: review after higher-priority queue items
- Link: https://github.com/sportnumerics/rankings/pull/59
- Last update: review required, checks passing (2026-03-28 14:07 UTC)

### In Progress
- (none)

### Ready
1) **Position-specific leaders pages (attack/midfield/defense/goalie/faceoff)**
- Status: Ready
- Owner: assistant
- Outcome: role-specific leader pages using existing position data already present in scraper/export paths
- First increment: ship one position-filtered leaders page end-to-end behind existing leader UI patterns
- Acceptance checks:
  - Position filter works off exported/player stat position data
  - One leaderboard route renders correctly in dev and test
  - Query path is covered by at least one focused automated test
- Next action: start once the incident/hotfix PRs above are merged or explicitly deprioritized
- Context: this remains the highest-value next net-new product feature after queue pressure drops

2) **Queue hygiene / stale-PR review notes**
- Status: Ready
- Owner: assistant
- Outcome: lower review overhead and less drift between docs and GitHub reality
- First increment: keep PRODUCT-BACKLOG.md aligned with live PR ordering and merge dependencies
- Acceptance checks:
  - Active PR order matches GitHub
  - stale PRs have explicit keep/refresh/close guidance
  - merge dependencies are documented
- Next action: continue through PR #95 whenever the queue is otherwise fully review-blocked

### Blocked
- (none)

## Done
- ✅ #96 merged
- ✅ #57 closed as superseded
- ✅ #58 no longer active in the open queue
- ✅ #90 closed as superseded
- ✅ #92 closed as unused review surface
- ✅ #93 closed as superseded
- ✅ #94 no longer active in the open queue
- ✅ #56 Fix NCAA upcoming games date labeling off-by-one (merged 2026-03-07)

## Backlog Notes (assistant-facing)
- Prioritize incidents and production-risk fixes first.
- When the queue is fully review-blocked, prefer tiny queue-health/doc-hygiene increments over speculative new code.
- Merge order currently: **#97 → #95 → #91 → #68 → refresh #74 → revisit #86 / #76 / #70 / #59 / #82**.
- Keep PRs small and reviewable.
- Every status change must update `Next action`.
