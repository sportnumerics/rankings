# Sportnumerics Product Ideas

*Proactive improvements to make sportnumerics more useful for lacrosse fans.*

## Recent Findings (2026-01-26)

**🎯 Quick Wins Identified:**
1. **Display hidden stats**: Face-off %, Saves, Goals Against are already scraped but not shown
   - Low effort: Update frontend to display existing backend data
   - High impact: Better visibility for faceoff specialists and goalies
2. **CloudWatch retention**: Set 7-day (dev) and 30-day (prod) retention policies
   - Current cost: ~$0.20/month, but prevents unbounded growth
   - One-line terraform or AWS CLI change

**✅ Already Optimized:**
- Frontend bundle size: 96KB (good for Next.js app)
- No immediate optimization needed

## Legend
- 🎯 High Impact / Low Effort
- 💡 Idea / Needs Research
- 🚧 In Progress
- ✅ Done

---

## League Expansion

### High School Lacrosse 💡
- **Goal**: Add high school men's and women's lacrosse rankings
- **Research needed**:
  - Data sources? (MaxPreps? state associations?)
  - Licensing/terms of use
  - Data format (HTML scraping? API?)
- **Impact**: Massive user base (parents, players, recruiters)

### PLL (Premier Lacrosse League) 💡
- **Goal**: Add professional men's lacrosse
- **Research needed**:
  - Official stats API or scraping
  - Different stat categories for pro vs college
- **Impact**: Professional league fans

### Victoria Lacrosse (Australia) 💡
- **Goal**: International expansion
- **Research needed**:
  - Data availability from Lacrosse Victoria
  - Time zone handling
  - Season schedule differences
- **Impact**: International users

---

## Stats & Analytics

### Advanced Statistics 🎯
- **Already scraped but NOT displayed**:
  - **Face-offs** (FO-W, FO-L): Won/lost counts → could show win %
  - **Saves** (SV): For goalies
  - **Goals Against** (GA): For goalies
- **Quick wins**:
  1. Add face-off % to player pages (for faceoff specialists)
  2. Add SV and GA columns for goalies
  3. Calculate save % (SV / (SV + GA))
- **Future ideas** (need new data):
  - Shot accuracy % (goals / shots on goal) - not currently captured
  - Ground ball differential by team
  - Goals per possession
  - Time of possession

### Goalie Rankings 💡
- **Goal**: Dedicated goalie ranking system
- **Stats to track**:
  - Save percentage
  - Goals against average
  - Saves per game
  - Quality of opponents faced
- **Algorithm**: Adapt current ranking system for goalie-specific metrics

### Defender Rankings 💡
- **Goal**: Recognize defensive players
- **Stats to track**:
  - Caused turnovers
  - Ground balls
  - Goals allowed (when on field)
- **Challenge**: Defense is harder to quantify than offense

---

## Predictions

### Prediction Accuracy Dashboard 💡
- **Goal**: Show historical prediction accuracy
- **Features**:
  - Track predictions vs actual results
  - Show accuracy % over time
  - Break down by division, week, etc.
- **Impact**: Build trust, show model improvement

### Improved Prediction Algorithm 💡
- **Ideas**:
  - Factor in injuries/roster changes
  - Home field advantage
  - Recent form (last 3-5 games weighted more)
  - Head-to-head history
- **Research**: What additional signals can improve predictions?

---

## Cost Optimization

### CloudWatch Log Retention 🎯
- **Current**: No retention policy (logs kept indefinitely)
  - `/rankings/dev/backend`: 12 MB stored
  - `/rankings/prod/backend`: 411 MB stored (~$0.20/month currently)
- **Recommendation**: Set retention policies
  - Dev: 7 days (minimal cost, easier debugging of recent issues)
  - Prod: 30-90 days (balance cost vs audit trail)
- **Implementation**: Update terraform or use AWS CLI:
  ```bash
  aws logs put-retention-policy --log-group-name /rankings/dev/backend --retention-in-days 7
  aws logs put-retention-policy --log-group-name /rankings/prod/backend --retention-in-days 30
  ```
- **Savings**: Minimal now (~$0.20/month), but prevents unbounded growth
- **Risk**: Low - can always increase retention if needed

### Frontend Bundle Size ✅
- **Current**: ~96 KB First Load JS (good baseline)
  - Shared chunks: 87.3 KB
  - Page-specific: ~9 KB
- **Status**: Already well-optimized (Next.js default optimizations)
- **Future optimization ideas**:
  - Add `@next/bundle-analyzer` to monitor over time
  - Check for duplicate dependencies
  - Consider lazy-loading @heroicons/react (if not already tree-shaken)
- **Impact**: Current size is reasonable; focus on more impactful areas first

### Backend Optimization 💡
- **Ideas**:
  - Cache frequently-accessed data
  - Optimize scraping schedule (do we need to scrape daily in off-season?)
  - Use spot instances for non-critical backend tasks

### Migrate from JSON to Parquet + DuckDB 💡
- **Current state**: Write hundreds/thousands of JSON files to S3 multiple times per day
  - Expensive: Many small S3 writes
  - Manageable but not ideal
- **Goal**: Write fewer, larger Parquet files; query with DuckDB at request time
  - Fewer S3 writes = lower cost
  - Potentially better query performance with proper partitioning
  - More flexible querying (filter/aggregate without precomputing all combinations)
- **Challenge**: Initial testing showed latency issues with Parquet
  - Need to design schema/partitioning correctly
  - DuckDB might solve this with smart indexing/caching
- **Research needed**:
  - Optimal Parquet schema and partitioning strategy
  - DuckDB latency benchmarks on realistic queries
  - Cost comparison: many small JSON writes vs fewer large Parquet writes
  - Frontend integration: DuckDB WASM? Lambda with DuckDB?
- **Impact**: High - could significantly reduce S3 costs and improve query flexibility

---

## Performance

### Page Load Speed 💡
- **Measure**: Current load times
- **Optimize**:
  - Image optimization (already using Next.js Image?)
  - Preload critical resources
  - SSR/ISR tuning
- **Goal**: Sub-1s initial load

### API Response Times 💡
- **Measure**: Current API latency
- **Optimize**:
  - Add caching layer
  - Database query optimization
  - Reduce payload size

---

## User Experience

### Mobile Optimization 💡
- **Audit**: Test on various mobile devices
- **Improve**:
  - Touch targets
  - Responsive tables
  - Simplified navigation

### Accessibility 💡
- **Audit**: Run a11y checker
- **Fix**:
  - Keyboard navigation
  - Screen reader support
  - Color contrast

---

## Ideas to Explore

*(Capture raw ideas here, refine later)*

- Email/SMS alerts for game results
- Team comparison tool (side-by-side stats)
- Player search across all teams
- Historical trends (how has a team performed over multiple years?)
- Fantasy lacrosse integration?
- Export data (CSV/JSON API for researchers)

---

## Review Process

1. Rankline captures ideas here during downtime
2. Will reviews periodically
3. Promising ideas get promoted to GitHub issues/PRs
4. Track progress with emoji indicators
