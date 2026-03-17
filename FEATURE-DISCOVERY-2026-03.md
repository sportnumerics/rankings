# Feature Discovery Sprint — March 2026

**Goal**: Identify highest-value near-term product improvement  
**Method**: Evidence-based value/effort/risk scoring  
**Outcome**: One feature promoted to implementation-ready task

---

## Top 5 Candidates

### 1. **Assists Leaders Page** 📊
**Value**: High (completes leader stats trilogy)  
**Effort**: Low (reuse goals leaders page pattern)  
**Risk**: Low (proven pattern)

**Evidence**:
- Goals leaders page (#59) already built - same pattern works
- Data already available in player stats
- Natural user expectation: "if goals leaders exist, assists should too"
- SEO benefit: more entry points for player searches

**Implementation Path**:
- Clone `/leaders/goals` → `/leaders/assists`
- Sort by `assists DESC` instead of `goals DESC`
- ~2 hours work, no new data pipeline needed

**User Value**:
- Midfielders/playmakers get recognition (not just scorers)
- Coaches scouting for passers
- Complete statistical picture

**Score**: 9/10 (low-hanging fruit with clear user demand)

---

### 2. **High School Lacrosse (MaxPreps)** 🏫
**Value**: Very High (massive new audience)  
**Effort**: Medium (scraper POC done, needs pipeline integration)  
**Risk**: Medium (external dependency, maintenance)

**Evidence**:
- Working POC built (PR #29 archived code)
- MaxPreps allows scraping per robots.txt
- Stable JSON structure in `__NEXT_DATA__`
- Market: parents, HS players, coaches (underserved segment)

**Implementation Path**:
1. Restore MaxPreps scraper from archived PR
2. Integrate into pipeline (`scrapers/maxpreps/`)
3. Add `/high-school` division selector
4. Deploy behind feature flag initially

**User Value**:
- Expand beyond college-only
- 10x potential audience (every HS player has parents/coaches)
- Differentiation from competitors

**Risks**:
- MaxPreps could change structure
- Legal/ToS considerations (currently allowed)
- Extra scraping maintenance burden

**Score**: 8/10 (high impact but needs careful execution)

---

### 3. **Goalie-Specific Rankings** 🥅
**Value**: Medium-High (underserved niche)  
**Effort**: Medium (needs data model extension)  
**Risk**: Low (additive, doesn't break existing)

**Evidence**:
- No existing goalie-only rankings anywhere
- NCAA publishes goalie stats (saves %, GAA)
- Goalies/coaches actively search for this data
- Natural extension of current player stats

**Implementation Path**:
1. Extend `GameStatLine` with goalie fields (saves, save %, GAA)
2. Scrape NCAA goalie leaderboards for validation
3. Add `/leaders/goalies` page
4. Future: rating algorithm specific to goalies

**User Value**:
- Goalies get recognition
- Scouts can find top goalies by division
- Fills a gap in lacrosse analytics

**Score**: 7/10 (niche but valuable)

---

### 4. **Prediction Accuracy Dashboard** 📈
**Value**: Medium (builds trust, algorithm validation)  
**Effort**: High (requires prediction storage + backfill)  
**Risk**: Medium (exposes algorithm weaknesses publicly)

**Evidence**:
- Users want to know "how accurate are these rankings?"
- Competitor rankings often lack validation
- Objective measure of algorithm quality

**Implementation Path**:
1. Store pre-game predictions (winner, margin, confidence)
2. Backfill predictions for historical games
3. Calculate accuracy metrics (% correct, avg error)
4. Build `/accuracy` page showing validation stats

**User Value**:
- Trust through transparency
- See where model excels/struggles
- Marketing differentiator ("80% accurate predictions")

**Risks**:
- Low accuracy could hurt credibility
- Adds complexity to pipeline
- Prediction storage overhead

**Score**: 6/10 (good long-term but not urgent)

---

### 5. **PLL (Pro League) Rankings** 🏆
**Value**: High (professional league coverage)  
**Effort**: Very High (API authentication + Cloudflare)  
**Risk**: High (blocked access, no official API)

**Evidence**:
- PLL has GraphQL API but requires auth
- Cloudflare blocks scraping attempts (error 1010)
- No public documentation
- Premium/pro audience interest

**Implementation Path**:
1. ~~Browser automation (Playwright)~~ - fragile
2. **Request official API partnership** - ideal but uncertain
3. Wait for public API release

**User Value**:
- Pro-level analysis
- Bridge gap between college and pro
- High-profile teams/players

**Risks**:
- No guaranteed access path
- High maintenance (anti-scraping measures)
- Legal risk without official approval

**Score**: 4/10 (high value but blocked by access issues)

---

## Recommendation: **Assists Leaders Page**

**Why**:
1. **Proven pattern**: Goals leaders (#59) works, just clone it
2. **Low effort**: ~2 hours, no new infrastructure
3. **Clear user demand**: Natural expectation alongside goals
4. **Zero risk**: Additive feature, existing data
5. **Ship momentum**: Quick win to keep velocity up

**Acceptance Criteria**:
- Page loads at `/2026/d1/leaders/assists`
- Top 50 players sorted by `assists DESC`
- Reuses `PlayersCard` component from goals leaders
- Navigation link added to leaders menu
- SEO: meta tags for assists leaders

**Next Steps**:
1. Create implementation task in backlog
2. Build MVP on feature branch
3. Deploy to dev for validation
4. Ship to prod

---

## Deferred (but valuable)

**High School Lacrosse** (#2): Worth doing Q2 2026 after assists leaders ships. Needs product planning session with Will to scope phasing.

**Goalie Rankings** (#3): Good Q2/Q3 feature when pipeline can handle additional stat types.

**Prediction Accuracy** (#4): Q3 2026 after prediction storage is architected.

**PLL** (#5): Monitor for official API announcement. Don't pursue until access is guaranteed.

---

**Decision Date**: 2026-03-15  
**Owner**: assistant  
**Status**: Assists Leaders promoted to Ready → In Progress
