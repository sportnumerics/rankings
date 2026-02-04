# Sportnumerics Product Ideas

This is a raw capture of ideas, research notes, and hypotheses. Not all ideas become backlog items.

## How to use
- Add ideas as you find them (with links + brief rationale).
- If an idea looks actionable, promote it to `PRODUCT-BACKLOG.md` with a small, reviewable first step.

## Ideas (newest first)

### 2026-02-04 — Goalie-specific rankings and statistics
- **Opportunity**: Goalies are underserved - current site shows general team rankings but no goalie-specific rankings
- **Data available**: 
  - NCAA tracks: Save Percentage, Goals Against Average, Saves Per Game ([example](https://www.ncaa.com/stats/lacrosse-men/d1/current/individual/224))
  - MCLA has goalie stat pages with similar metrics
- **Key metrics for goalies**:
  - Save Percentage (saves / (saves + goals allowed)) - primary metric
  - Goals Against Average (GAA)
  - Saves Per Game
  - Minutes Played
- **Value proposition**: Goalies, coaches, and scouts want to see goalie-specific performance comparisons
- **Current gap**: GameStatLine has `ga` (goals allowed) and `s` (shots), but doesn't distinguish goalie-specific stats vs team defensive stats
- **First step**: 
  - Extend data model to include goalie-specific stat line (saves, save %, GAA)
  - Scrape NCAA goalie leaderboard to validate data structure
  - Create /goalies rankings page (top N goalies by save % with min games played)
- **Similar for defenders**: Could extend to caused turnovers, ground balls for defenders

### 2026-02-04 — Prediction accuracy tracking and display
- **Opportunity**: Validate and improve the ranking algorithm by measuring prediction accuracy
- **What to track**:
  - Pre-game predictions (based on current rankings/ratings)
  - Actual game outcomes
  - Prediction accuracy over time (% correct, margin of error)
- **Value proposition**:
  - Users see how accurate the rankings are (builds trust)
  - Algorithm improvements can be measured objectively
  - Identify where model performs well/poorly (home vs away, rivalry games, etc.)
- **Implementation ideas**:
  - Store pre-game predictions when scraping schedules
  - Compare predictions to actual results after games
  - Display accuracy metrics on site ("/accuracy" page)
  - Show prediction confidence alongside game predictions
- **First step**:
  - Add prediction storage to database (predicted_winner, predicted_margin, confidence)
  - Write script to backfill predictions for already-played games (using ratings at that time)
  - Calculate accuracy metrics (correct picks, ATS accuracy, avg margin error)
  - Create simple accuracy dashboard page
- **Advanced**: Use accuracy data to tune algorithm parameters, display "upset alerts" for low-confidence predictions

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

