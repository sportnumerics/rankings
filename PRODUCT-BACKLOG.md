# Sportnumerics Backlog (execution source of truth)

## North Star
Consistent weekly shipping velocity with small, high-confidence increments.

## Active Focus (updated 2026-04-28)

### PR
1) **#91 — Fix player page division error in parquet mode**
- Status: PR
- Owner: assistant
- Outcome: player pages resolve division correctly in parquet mode
- Current increment: fix complete and validated in CI/dev
- Acceptance checks:
  - player page no longer throws division resolution errors in parquet mode
  - frontend tests pass
  - deploy + E2E checks pass
- Next action: review/merge; #96 is already merged so this is now the clear top code PR in the queue
- Link: https://github.com/sportnumerics/rankings/pull/91
- Last update: checks green, review required (2026-04-03)

2) **#95 — Sync backlog to current PR queue**
- Status: PR
- Owner: assistant
- Outcome: backlog reflects the live queue and explicit priorities
- Current increment: refreshed for the live queue after #96 merged and stale PR keep decisions were recorded
- Acceptance checks:
  - PRODUCT-BACKLOG.md matches current open PR ordering
  - stale PRs have explicit keep/close recommendations
  - next implementation target is clear once merge queue moves
- Next action: review/merge after confirming queue ordering looks right
- Link: https://github.com/sportnumerics/rankings/pull/95
- Last update: backlog refreshed after #96 merged and the remaining stale March PRs were marked keep-for-now with explicit rationale (2026-04-28 09:00 AM CDT)

3) **#86 — Assists leaders page**
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

4) **#82 — Unit tests for parquet query code paths**
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

5) **#76 — Points leaders page**
- Status: PR
- Owner: assistant
- Outcome: `/leaders/points` page showing top combined scoring leaders per division
- First increment: ship MVP points leaders page
- Acceptance checks:
  - page loads at `/2026/d1/leaders/points`
  - shows top 50 players sorted by points descending
  - reuses existing leaders page patterns/UI
- Next action: awaiting Will's review
- Link: https://github.com/sportnumerics/rankings/pull/76
- Last update: checks green, review required (2026-03-21)

6) **#74 — Vitest infrastructure and SQL security tests**
- Status: PR
- Owner: assistant
- Outcome: frontend test harness covers SQL safety and future query regressions
- Current increment: baseline Vitest wiring plus SQL security coverage shipped in one PR
- Acceptance checks:
  - Vitest runs in CI for frontend unit tests
  - SQL-related tests guard against unsafe query construction regressions
  - CI passes
- Next action: awaiting Will's review
- Link: https://github.com/sportnumerics/rankings/pull/74
- Last update: checks green, review required (2026-03-19)

7) **#70 — Per-game stat averages**
- Status: PR
- Owner: assistant
- Outcome: player leader views can expose PPG/GPG/APG style averages
- First increment: ship computed per-game averages end-to-end
- Acceptance checks:
  - players/stat views expose per-game average fields
  - frontend renders the new averages without breaking existing stat pages
  - CI passes
- Next action: awaiting Will's review
- Link: https://github.com/sportnumerics/rankings/pull/70
- Last update: checks green, review required (2026-03-17)

8) **#68 — Parameterize parquet SQL inputs**
- Status: PR
- Owner: assistant
- Outcome: parquet query entry points avoid unsafe SQL string interpolation
- Current increment: parameterized query path and validation shipped
- Acceptance checks:
  - user-controlled query inputs are parameterized or validated
  - regression tests cover the protected path
  - CI passes
- Next action: awaiting Will's review
- Link: https://github.com/sportnumerics/rankings/pull/68
- Last update: checks green, review required (2026-03-14)

9) **#59 — Goals leaders page**
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
1) **Old PR queue cleanup pass**
- Status: Ready
- Owner: assistant
- Outcome: long-stale PR queue is intentionally reduced so review attention goes to the best work
- Current assessment after review:
  - **#68 keep** — still the only branch that hardens parquet query parameter handling across `teams.ts`, `players.ts`, `games.ts`, and `parquet.ts`; not superseded on `main`
  - **#70 keep** — still the only branch that adds `games_played` plus PPG/GPG/APG display; noisy docs can be trimmed later, but the product change remains unique
  - **#74 keep** — still the only branch that adds Vitest + parquet regression tests; especially useful because it can turn the SQL-hardening work in #68 into enforceable coverage
  - **#76 keep for now** — still the only points leaders implementation; lower priority than incident/security/test work, but not superseded by current open PRs
- Acceptance checks:
  - each long-stale PR has an explicit keep/close rationale
  - obviously superseded or low-value PRs are closed
  - remaining queue order is easier to understand at a glance
- Next action: ask Will to review/merge #68 first, then refresh/rebase #74 against it before revisiting #70 and #76

2) **Position-specific leaders pages**
- Status: Ready
- Owner: assistant
- Outcome: leaders filtered for attack, midfield, defense, goalie, and faceoff specialists
- First increment: ship one position-specific leaderboard using existing player stats/parquet data
- Acceptance checks:
  - at least one position-specific leaders page loads for 2026/d1
  - query/filter uses existing position data without ad hoc scraping changes
  - tests or focused validation cover the position filter path
- Next action: start after #91 / #95 merge queue moves

### Done
- ✅ #96 fix: harden division lookup and incomplete game rendering (merged 2026-04-24)
- ✅ #90 closed as superseded by newer backlog sync PR #95 (2026-04-25)
- ✅ #93 closed as superseded by shipped/active leaders work and current backlog ordering (2026-04-25)
- ✅ #92 closed as unused review surface; backlog driver already gets the same queue signal directly from `gh` (2026-04-25)
- ✅ #57 closed as stale research review surface; key benchmark findings preserved in the PR thread and can be revived later if needed (2026-04-27)
- ✅ #94 Fix NCAA player stats scrape regression coverage + CI timeout handling (merged 2026-04-22)
- ✅ #56 Fix NCAA upcoming games date labeling off-by-one (merged 2026-03-07)

## Backlog Notes (assistant-facing)
- Prioritize reviewable PR throughput before starting new feature work.
- Incident fixes beat roadmap work.
- Keep PRs small, user-visible when possible, and test-backed.
- Every status change must update `Next action`.
- When backlog docs go stale, refresh them against live `gh pr list`, not memory.
