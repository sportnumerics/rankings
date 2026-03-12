# Feature Discovery Sprint - March 12, 2026

## Competitive Analysis Summary

**Laxnumbers.com** (primary competitor):
- High school + college rankings
- State-specific rankings
- Player leaders (points, goals, assists, faceoffs, saves)
- Recruiting commitments tracking
- Historical archives

**Laxmath.com/laxpower** (legacy player):
- Consensus ratings from 8 different systems
- Tournament predictions
- Historical data archives

**Sportnumerics.com** (current):
- NCAA D1/D2/D3 + MCLA team rankings ✅
- Player rankings ✅
- Game results ✅
- Individual team/player/game pages ✅
- **In progress**: Goals leaders (PR #59), Assists leaders (PR #61)

## Top 5 Feature Candidates

### 1. Multi-Category Player Leaders Hub
**Description**: Expand beyond goals/assists to a complete leaders dashboard with saves, faceoff %, ground balls, caused turnovers, etc.

**Value**: HIGH
- Natural extension of in-progress work (PRs #59, #61)
- Fills gap vs competitors (Laxnumbers has this)
- Appeals to specialized positions (goalies, FOGOs, defenders)
- SEO boost for long-tail searches ("best lacrosse goalies 2026")

**Effort**: LOW-MEDIUM
- Data already in database (GameStatLine)
- UI pattern established by PRs #59, #61
- ~3-5 new pages, reuse PlayersCard component
- Categories: saves, save %, faceoff wins, faceoff %, ground balls, caused turnovers, turnovers

**Risk**: LOW
- No new data pipeline needed
- Proven UI pattern
- No breaking changes

**First increment**: Add saves leaders page (goalies) - highest unserved niche

---

### 2. Tournament Bracket Predictions
**Description**: Generate and display predicted NCAA tournament brackets with confidence scores

**Value**: HIGH
- Spike traffic during tournament season (March-May)
- Differentiates from competitors (only Laxpower has this)
- Builds trust in ranking algorithm
- Viral potential (shareability)

**Effort**: MEDIUM
- Backend: bracket generation algorithm (seeding + predictions)
- Frontend: bracket visualization component
- Weekly updates during tournament
- Historical accuracy tracking

**Risk**: MEDIUM
- Algorithm accuracy will be public and scrutinized
- Requires solid confidence in ranking quality
- Maintenance burden during tournament season

**First increment**: Generate static bracket visualization for current top 16 teams

---

### 3. High School Lacrosse Rankings
**Description**: Add HS boys/girls rankings starting with top national teams

**Value**: VERY HIGH
- Massive untapped market (parents, players, coaches)
- Laxnumbers dominates this space
- High engagement potential
- Recruiting audience crossover

**Effort**: HIGH
- New data source required (MaxPreps scraper exists but needs validation)
- Separate database schema/pipeline
- New UI section
- State-specific breakdowns later
- Data quality/completeness risk

**Risk**: HIGH
- Scraping reliability (MaxPreps could block)
- Data quality for smaller schools
- Different ranking algorithm needed (fewer games, wider variance)
- Legal/ethical considerations (minors)
- Scope creep (50 states × 2 genders)

**First increment**: National top-25 boys HS rankings (proof of concept)

---

### 4. Head-to-Head Game Predictions
**Description**: Show predicted winner + margin for all upcoming games

**Value**: MEDIUM-HIGH
- Daily engagement driver (check before games)
- Validates ranking quality in real-time
- Fantasy/betting adjacent (traffic magnet)
- Builds trust through transparency

**Effort**: LOW-MEDIUM
- Backend: prediction algorithm (rating differential → expected margin)
- Frontend: add prediction to game cards on upcoming games page
- Post-game: track accuracy
- Calibration dashboard

**Risk**: MEDIUM
- Prediction accuracy must be decent (>60%) to build trust
- Could undermine confidence if poorly calibrated
- Needs statistical rigor

**First increment**: Add win probability to D1 upcoming games page

---

### 5. Recruiting Commitments Tracker
**Description**: Track and display player commitments to colleges

**Value**: MEDIUM
- Appeals to parents, coaches, prospects
- Laxnumbers has this, we don't
- Sticky content (repeat visits)

**Effort**: HIGH
- Requires new data source (user submissions? Twitter scraping?)
- Moderation/verification needed
- New database schema
- UI for browsing by player/school/year

**Risk**: HIGH
- Data sourcing challenge (manual curation doesn't scale)
- Accuracy/verification burden
- Potential legal issues (privacy, minors)
- High maintenance

**First increment**: Manual entry form + simple commitments list page

---

## Recommendation: #1 - Multi-Category Player Leaders Hub

**Rationale**:
1. **Natural extension** of active work (PRs #59, #61 establish pattern)
2. **Low risk, high value** - data exists, UI proven, no breaking changes
3. **Immediate differentiation** - competitors have this, we need it
4. **SEO benefit** - long-tail keywords for each category
5. **Quick wins** - can ship saves leaders in <1 day
6. **Foundation for #4** - player stats power predictions later

**First Increment**: Build `/leaders/saves` page (goalie-focused)
- Reuse PlayersCard component from PR #59
- Query GameStatLine for saves, save %
- Sort by saves descending (min games threshold)
- Deploy to dev, validate with real data

**Acceptance Criteria**:
- Page loads at `/2026/d1/leaders/saves`
- Shows top 50 goalies sorted by saves descending
- Includes save % column
- Min 5 games threshold to qualify
- Reuses existing UI components
- Query optimized for parquet mode (if PR #58 merged)

**Future increments**:
- Faceoff % leaders (FOGOs)
- Ground balls leaders
- Caused turnovers leaders
- Assists leaders (PR #61)
- Combined hub page linking all categories

---

## Next Steps

1. Update PRODUCT-BACKLOG.md with new "Multi-Category Player Leaders Hub" task
2. Convert first increment (saves leaders) into implementation-ready spec
3. Create branch + implement saves leaders page
4. Open PR with tests + docs
