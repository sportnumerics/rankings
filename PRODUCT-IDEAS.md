# Sportnumerics Product Ideas

This is a raw capture of ideas, research notes, and hypotheses. Not all ideas become backlog items.

## How to use
- Add ideas as you find them (with links + brief rationale).
- If an idea looks actionable, promote it to `PRODUCT-BACKLOG.md` with a small, reviewable first step.

## Ideas (newest first)

### 2026-02-04 — High school lacrosse data source: MaxPreps
- **Site**: https://www.maxpreps.com/lacrosse/
- **Coverage**: Comprehensive national boys/girls high school lacrosse rankings, stats, schedules, scores
- **Scrapability**: ✅ HIGH - Next.js app with `__NEXT_DATA__` JSON embedded in pages
- **robots.txt**: Allows rankings pages (no disallow for `/lacrosse/rankings/`)
- **Data structure**: Ranking data embedded in page as JSON (easy parsing)
- **Opportunity**: Massive user base (high school parents/players/coaches), currently underserved
- **First step**: Parse one rankings page to extract team data (name, rank, location, record)

### 2026-02-04 — PLL data source reconnaissance
- The PLL runs a public stats site: https://stats.premierlacrosseleague.com/ (player/team/game stats). Potentially scrapeable endpoints for league expansion.
- Official stats provider: Champion Data (may imply structured feeds behind the site).

### 2026-01-27 — Speed up CI + reduce noise
- Add Next.js build caching in GitHub Actions (`actions/cache` for `.next/cache` + npm cache). Speeds deploy runs and reduces “No build cache found” warnings.

### 2026-01-27 — Infra: stop Terraform tag schema drift from breaking deploys
- Some AWS resources don’t support `tags` depending on provider version (seen with `aws_cloudfront_origin_access_control` and `aws_cloudfront_cache_policy`). Idea: standardize tagging via provider `default_tags` and/or remove per-resource tags where unsupported, to keep deploys green.

### 2026-01-27 — Add a lightweight “site health” endpoint/page
- Provide a simple `/api/health` (or `/health`) that checks backend connectivity and returns build/version + data bucket status. Useful for debugging and uptime checks.

