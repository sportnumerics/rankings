# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-05-14)

### PR
1) **#97 — Restore prod division lookup and harden NCAA scraping**
- Status: PR (✅ all GitHub checks passing; review required; reverified 2026-05-14)
- Owner: assistant
- Outcome: prod-safe `/api/[year]/div` lookup plus NCAA scraper recovery when Playwright browser/page/context closes mid-run
- Acceptance checks:
  - Backend unit tests pass ✅ (`lib.scrape.test_playwright_fetcher`, `lib.scrape.test_ncaa` re-run locally 2026-05-09)
  - Frontend lint passes ✅ (re-run locally 2026-05-09)
  - GitHub PR Validation checks pass ✅ (backend/frontend, limited scrape, E2E, dev deploy)
- Next action: Will review/merge #97
- Link: https://github.com/sportnumerics/rankings/pull/97
- Last update: rechecked open PR status and GitHub checks; #97 remains mergeable with review as the only blocker (2026-05-14 09:00 CT)

2) **#95 — Backlog sync to current PR queue**
- Status: PR (stale; review required)
- Owner: assistant
- Outcome: backlog reflects current PR queue and merge order
- Next action: supersede or close if this file's #97 update is preferred
- Link: https://github.com/sportnumerics/rankings/pull/95

3) **#91 — Fix player page division error in parquet mode**
- Status: PR (stale; review required)
- Owner: assistant
- Outcome: player pages work in parquet mode without division lookup errors
- Next action: revisit after #97 merges; close if #97/main now covers the failure
- Link: https://github.com/sportnumerics/rankings/pull/91

4) **Feature PR queue**
- Status: PR (review required)
- Owner: assistant
- Items: #59 goals leaders, #76 points leaders, #86 assists leaders, #70 per-game stat averages
- Next action: merge/rebase in dependency order after prod fix #97 is resolved

5) **Parquet safety/test PR queue**
- Status: PR (review required)
- Owner: assistant
- Items: #68 parameterize parquet SQL inputs, #74 Vitest infrastructure + SQL security tests, #82 parquet query coverage
- Next action: prioritize #68/#74 before more parquet feature expansion

### Ready
1) **Post-#97 prod verification**
- Status: Ready
- Owner: assistant
- Outcome: confirm prod division lookup and NCAA scrape health after #97 merge/deploy
- Acceptance checks:
  - `/api/2026/div` returns JSON-backed division for representative team/player/game paths
  - prod backend logs show no repeated NCAA Playwright closed-browser failures
  - next limited scrape/export completes successfully
- Next action: run after Will merges #97

2) **Stale PR reduction pass**
- Status: Ready
- Owner: assistant
- Outcome: shrink the open PR queue to fewer, reviewable branches
- Acceptance checks:
  - identify PRs made obsolete by #97/main
  - close or rebase at least one stale PR with clear rationale
  - keep feature PRs ordered by user-visible value
- Next action: start with #91 and #95 after #97 merge

3) **Unit tests for parquet query code paths**
- Status: Ready
- Owner: assistant
- Outcome: systematic coverage for parquet query functions and server data loaders
- Acceptance checks:
  - tests verify SQL query construction (div filtering, sorting, column selection)
  - tests verify fallback behavior when parquet fails
  - tests verify debug metadata structure
  - all tests pass in CI
- Next action: reconcile with #74/#82 and rebase once #97 is merged

### In Progress
- (none)

### Blocked
- #97, #95, #91, #59, #68, #70, #74, #76, #82, #86: blocked on review/merge decision from Will

## Done
- ✅ #58 DuckDB parquet read mode merged (2026-03-13)
- ✅ #56 Fix NCAA upcoming games date labeling off-by-one (merged 2026-03-07)
- 🗄️ #57 DuckDB parquet benchmark harness closed as reference work

## Backlog Notes (assistant-facing)
- Prefer prod stability and PR-queue reduction before net-new feature branches.
- Keep PRs small and reviewable.
- Every status change must update `Next action`.
