# Sportnumerics Backlog

A lightweight, assistant-run task management system.

## Status meanings
- **Idea**: worth considering, not yet scoped
- **Ready**: scoped into a small first increment that can be done in <= 1-3 hours
- **In Progress**: being implemented on a branch
- **PR**: PR open, awaiting review/CI
- **Done**: merged
- **Blocked**: needs Will input or external dependency

## Rules
- Prefer *small* increments that ship value or reduce risk.
- Each backlog item must have: **Outcome**, **First increment**, **Acceptance checks**.
- When possible: add/adjust tests with the change.

---

## Now (top priority)

### Ready
1) **Goalie statistics data model extension**
   - Outcome: Enable tracking goalie-specific stats (saves, save %, GAA) for future goalie rankings
   - First increment: Extend GameStatLine/PlayerStatLine data model to include goalie stats; scrape NCAA goalie leaderboard as validation
   - Acceptance checks:
     - Data model includes: saves (int), save_percentage (float), goals_against_average (float), minutes_played (int)
     - Script successfully scrapes top 25 goalies from NCAA leaderboard
     - Unit test with fixture validates goalie stat parsing
     - No breaking changes to existing team scraping/ranking pipeline

### In Progress
- (none)

### PR
- **MaxPreps high school lacrosse scraper (POC)** (PR #29) - validates scrapability, extracts 25 teams with tests
- **Product research: MaxPreps high school lacrosse** (PR #28) - documents findings and feasibility
- **PLL data source reconnaissance (stats site)** (PR #27) - documents GraphQL endpoints, auth requirements, and scraping feasibility
- **Document "how deploy works" (1-page ops doc)** (PR #26)
- **Add backend end-to-end smoke test in CI** (PR #20) - validates scrape→predict→sync pipeline on PRs, syncs to dev
- **Add Next.js build caching** (PR #13) - caches npm + .next/cache for faster deploys

---

## Next (candidate work)

### Idea
- (seed ideas live in PRODUCT-IDEAS.md; promote the best ones here)

### Blocked
- (none)

---

## Done
- ✅ Fix Terraform deploy failure (PR #9, merged 2026-01-28)
- ✅ Make health_check.sh token-proof (already implemented in scripts/health_check.sh)
