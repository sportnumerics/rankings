# Feature Discovery Sprint - 2026-04-04

## Research Summary

**Competitors analyzed:**
- NCAA.com (official D1 stats)
- LaxNumbers (high school focus, recruits, state rankings)
- MaxPreps (high school team rankings)
- Inside Lacrosse (recruiting/player rankings)
- National Lacrosse Federation (team/player rankings)

**Current sportnumerics pages:**
- Team rankings (by division)
- Player rankings (by division)
- Games (by division)
- Team detail pages
- Player detail pages
- Game detail pages
- About page

## Top 5 Feature Candidates (Value/Effort/Risk)

### 1. **Position-Specific Leader Boards** 🏆
**Value:** HIGH - Users want to compare players by position (attack, midfield, defense, goalie, faceoff)
**Effort:** MEDIUM - Requires:
- Position data extraction from NCAA scraper
- New leader pages `/[year]/[div]/leaders/[position]`
- Reuse existing PlayersCard + RankedPlayers components
**Risk:** LOW - Position data is stable in NCAA HTML, similar to existing goals leaders work
**Gaps filled:**
- NCAA.com has goals/assists leaders but not by position
- LaxNumbers has high school position leaders
- We have overall player ratings but no position breakdowns
**First increment:** Attack leaders page (goals + assists focus)
**User impact:** Fans can find top attackers, best faceoff specialists, elite goalies

---

### 2. **Team Stats Pages (Offense/Defense Efficiency)** 📊
**Value:** HIGH - Team stats are core to understanding rankings
**Effort:** MEDIUM - Requires:
- Aggregate team offense/defense stats (goals for/against per game, shot %, etc.)
- New team stats page `/[year]/[div]/teams/stats`
- Table component with sortable columns
**Risk:** LOW - Data already in game results, just needs aggregation
**Gaps filled:**
- NCAA.com has team stats but not broken down by division
- LaxNumbers focuses on individuals
- Our rankings show rating but not underlying performance metrics
**First increment:** Basic team offense/defense table (goals/game, goals against/game)
**User impact:** Users understand *why* teams are ranked where they are

---

### 3. **Head-to-Head Records** 🤝
**Value:** MEDIUM-HIGH - Fans want to see team matchup history
**Effort:** LOW-MEDIUM - Requires:
- Query games for team A vs team B
- Display win/loss record + recent games
- Add "vs [opponent]" section to team detail pages
**Risk:** LOW - Data already exists in games table
**Gaps filled:**
- NCAA.com doesn't show historical H2H
- Competitors focus on current season only
- Our team pages show games but not opponent-specific history
**First increment:** Add H2H record section to team detail page
**User impact:** Quick answer to "How have these teams done against each other?"

---

### 4. **Game Predictions** 🔮
**Value:** MEDIUM-HIGH - Engaging for fans, validates ranking quality
**Effort:** MEDIUM - Requires:
- Prediction algorithm (simple: rating diff → win probability)
- Upcoming games page with predictions
- Post-game: show prediction accuracy
**Risk:** MEDIUM - Predictions can be wrong and hurt credibility if not framed carefully
**Gaps filled:**
- NCAA.com has no predictions
- Competitors don't show algorithmic predictions
- Our ratings imply strength but don't forecast outcomes
**First increment:** Simple rating-based win probability on upcoming games page
**User impact:** Users can see "Who's favored?" before games

---

### 5. **Recruiting/Commits Tracker** 🎓
**Value:** MEDIUM - High engagement in HS/college recruiting community
**Effort:** HIGH - Requires:
- New data source (Inside Lacrosse? LaxNumbers? Manual?)
- Player profile enrichment
- Commits page + team/player links
**Risk:** HIGH - Data quality, scraping legality, ongoing maintenance
**Gaps filled:**
- LaxNumbers, Inside Lacrosse dominate this space
- We have zero recruiting content
- MCLA is post-college so less relevant
**First increment:** Manual commit list for top teams (proof of concept)
**User impact:** Fans track where players are going

---

## Recommendation

**Build #1: Position-Specific Leader Boards** (attack/midfield/defense/goalie/faceoff)

**Why:**
- **High value:** Fans naturally think in positions ("Who's the best attackman?")
- **Medium effort:** Similar to existing goals leaders PR (#59)
- **Low risk:** Position data is stable, UI patterns established
- **Differentiation:** NCAA.com doesn't break down by position + division
- **Foundation for more:** Once positions exist, can use for team composition analysis, recruiting, etc.

**Implementation plan:**
1. Extract position from NCAA player pages (already in scraper output?)
2. Add position column to player parquet file
3. Create `/[year]/[div]/leaders/attack`, `/[year]/[div]/leaders/midfield`, etc.
4. Reuse PlayersCard component with position filter
5. Add navigation to existing leaders section

**Estimated effort:** 2-4 hours
**Acceptance criteria:**
- 5 leader pages (attack, midfield, defense, goalie, faceoff)
- Top 50 players per position per division
- Sorted by rating (or position-specific stat like saves for goalies)
- Links to player detail pages

---

## Next Steps

1. Confirm #1 with Will
2. Check if position data already exists in scraper
3. If yes → start implementation
4. If no → add position extraction as first increment
