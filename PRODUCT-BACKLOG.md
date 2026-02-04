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
1) **MaxPreps high school lacrosse scraper (proof of concept)**
   - Outcome: Validate feasibility of scraping MaxPreps rankings + basic team data
   - First increment: Write parser to extract team data from one rankings page (rank, name, location, record) from `__NEXT_DATA__` JSON
   - Acceptance checks:
     - Script successfully extracts ≥10 teams from https://www.maxpreps.com/lacrosse/rankings/1/
     - Unit test with fixture (saved `__NEXT_DATA__` JSON)
     - Output includes: rank, team name, school, city, state, record

### In Progress
- (none)

### PR
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
