# Parquet Schema Design for Sportnumerics

## Design Principles

1. **Optimize for the common case**: List pages and leaderboards are 80%+ of queries
2. **Sort order = primary access pattern**: Row group skipping is the biggest win
3. **Accept minor inefficiency on detail pages**: Scanning 50-200 rows within a division is acceptable
4. **Denormalize to avoid joins**: Small data size makes duplication cheap
5. **Minimize file count**: Fewer files = simpler backend export, fewer S3 writes

---

## File 1: `{year}/teams.parquet`

**Primary use case**: Teams list page (filter by division, sorted by rank)

**Schema**:
```sql
CREATE TABLE teams (
    div VARCHAR,             -- SORT KEY 1: enables row group skipping
    rank INTEGER,            -- SORT KEY 2: within division
    id VARCHAR,              -- team identifier (e.g., "brigham-young-21")
    name VARCHAR,            -- display name
    sport VARCHAR,           -- "lacrosse"
    source VARCHAR,          -- "ncaa" or "mcla"
    schedule_url VARCHAR,    -- external schedule link
    offense DOUBLE,          -- offensive rating
    defense DOUBLE,          -- defensive rating
    overall DOUBLE           -- overall rating
)
```

**Sort order**: `(div ASC, rank ASC, id ASC)`

**Size**: ~30 KB compressed (~200 teams)

**Queries**:

| Page | Query | Read Size | Notes |
|------|-------|-----------|-------|
| Teams list | `WHERE div = ? ORDER BY rank` | ~5-10 KB | Row group skipping reads only target division |
| Team detail | `WHERE div = ? AND id = ?` | ~5-10 KB | Scans ~50-200 rows within division (acceptable) |

**Trade-off**: Team detail is not a pure point lookup, but we have `div` from the URL path (`/[year]/[division]/teams/[id]`), so we can skip to the right row group. Scanning 50-200 teams within a division is ~5-10 KB and negligible.

---

## File 2: `{year}/players.parquet`

**Primary use case**: Players list / leaderboards (filter by division, sorted by stat)

**Schema**:
```sql
CREATE TABLE players (
    team_div VARCHAR,        -- SORT KEY 1: enables row group skipping
    points DOUBLE,           -- SORT KEY 2: for default leaderboard (DESC)
    id VARCHAR,              -- player identifier
    name VARCHAR,            -- display name
    team_id VARCHAR,         -- FK to teams.id
    team_name VARCHAR,       -- denormalized for display
    team_schedule_url VARCHAR,
    team_sport VARCHAR,
    team_source VARCHAR,
    goals DOUBLE,            -- for goals leaderboard
    assists DOUBLE,          -- for assists leaderboard
    position VARCHAR,
    number INTEGER,
    class_year VARCHAR,      -- Fr, So, Jr, Sr
    eligibility VARCHAR,
    height VARCHAR,
    weight VARCHAR,
    high_school VARCHAR,
    hometown VARCHAR,
    external_link VARCHAR
)
```

**Sort order**: `(team_div ASC, points DESC, id ASC)`

**Size**: ~200 KB compressed (~2000 players)

**Queries**:

| Page | Query | Read Size | Notes |
|------|-------|-----------|-------|
| Players list | `WHERE team_div = ? ORDER BY points DESC LIMIT 200` | ~20-50 KB | Row group skipping + top-N |
| Goals leaders | `WHERE team_div = ? ORDER BY goals DESC LIMIT 50` | ~20-50 KB | Scans division, sorts by goals |
| Assists leaders | `WHERE team_div = ? ORDER BY assists DESC LIMIT 50` | ~20-50 KB | Scans division, sorts by assists |
| Player detail | `WHERE team_div = ? AND id = ?` | ~20-50 KB | Scans ~500-2000 players in division |
| Team roster | `WHERE team_id = ?` | ~20-50 KB | Scans division, filters by team_id |

**Trade-off**: 
- Goals/assists leaderboards require re-sorting after division filter (not sorted by those columns)
- Player detail and team roster require scanning the division
- Alternative would be 3+ separate files (players-by-points, players-by-goals, players-by-id, roster-by-team)
- Current approach: single file, accept ~20-50 KB reads for all queries (still 5-10x better than JSON)

---

## File 3: `{year}/schedules.parquet`

**Primary use case**: Team detail page schedule section

**Schema**:
```sql
CREATE TABLE schedules (
    team_id VARCHAR,                -- SORT KEY 1
    date VARCHAR,                   -- SORT KEY 2 (ISO format for lexical sort)
    game_id VARCHAR,
    opponent_id VARCHAR,
    opponent_name VARCHAR,          -- denormalized
    opponent_div VARCHAR,
    opponent_schedule_url VARCHAR,
    opponent_sport VARCHAR,
    opponent_source VARCHAR,
    home BOOLEAN,
    points_for INTEGER,             -- null if not played
    points_against INTEGER,
    details_url VARCHAR
)
```

**Sort order**: `(team_id ASC, date ASC)`

**Size**: ~150 KB compressed (~200 teams × ~15 games)

**Queries**:

| Page | Query | Read Size | Notes |
|------|-------|-----------|-------|
| Team schedule | `WHERE team_id = ? ORDER BY date` | ~1-2 KB | Perfect: contiguous row group per team |

**Trade-off**: None. This is optimal for the only use case.

---

## File 4: `{year}/games.parquet`

**Primary use case**: Games list (recent games in division)

**Schema**:
```sql
CREATE TABLE games (
    date VARCHAR,                  -- SORT KEY 1 (DESC, ISO format)
    id VARCHAR,                    -- SORT KEY 2
    external_link VARCHAR,
    home_team_id VARCHAR,
    home_team_name VARCHAR,
    home_team_div VARCHAR,
    home_team_schedule_url VARCHAR,
    home_team_sport VARCHAR,
    home_team_source VARCHAR,
    away_team_id VARCHAR,
    away_team_name VARCHAR,
    away_team_div VARCHAR,
    away_team_schedule_url VARCHAR,
    away_team_sport VARCHAR,
    away_team_source VARCHAR,
    home_score INTEGER,
    away_score INTEGER
)
```

**Sort order**: `(date DESC, id ASC)`

**Size**: ~150 KB compressed (~1500 games)

**Queries**:

| Page | Query | Read Size | Notes |
|------|-------|-----------|-------|
| Games list | `WHERE home_team_div = ? OR away_team_div = ? ORDER BY date DESC LIMIT 100` | ~50-150 KB | Must scan to filter by division; date sort is free |
| Game detail | `WHERE id = ?` | ~50-150 KB | Must scan whole file (no ID index) |

**Trade-off**: 
- Games list can't use row group skipping (division filter is OR condition on two columns)
- Game detail is a full scan
- Alternative: separate `games-by-id.parquet` sorted by ID (~150 KB duplicate)
- Current approach: accept ~50-150 KB read for both queries (still better than JSON ~200-500 KB)
- **Recommendation**: If game detail becomes common, add `games-by-id.parquet`

---

## File 5: `{year}/game_stats.parquet`

**Primary use case**: Game detail page box score

**Schema**:
```sql
CREATE TABLE game_stats (
    game_id VARCHAR,               -- SORT KEY 1
    team_id VARCHAR,               -- SORT KEY 2
    points_desc DOUBLE,            -- SORT KEY 3 (g + a, DESC for display order)
    player_id VARCHAR,
    player_name VARCHAR,
    number INTEGER,
    position VARCHAR,
    g INTEGER,
    a INTEGER,
    gb INTEGER,
    face_offs_won INTEGER,
    face_offs_lost INTEGER
)
```

**Sort order**: `(game_id ASC, team_id ASC, points_desc DESC)`
- Note: `points_desc` = `-(g + a)` to achieve DESC sort in ASC-sorted parquet

**Size**: ~2 MB compressed (~1500 games × ~40 players)

**Queries**:

| Page | Query | Read Size | Notes |
|------|-------|-----------|-------|
| Game box score | `WHERE game_id = ? ORDER BY team_id, (g + a) DESC` | ~2-3 KB | Perfect: contiguous row group per game, pre-sorted |

**Trade-off**: None. This is optimal for the only use case.

---

## File 6: `{year}/player_stats.parquet`

**Primary use case**: Player detail page game log

**Schema**:
```sql
CREATE TABLE player_stats (
    player_id VARCHAR,             -- SORT KEY 1
    date VARCHAR,                  -- SORT KEY 2 (ISO format, DESC via negative timestamp)
    game_id VARCHAR,
    opponent_id VARCHAR,
    opponent_name VARCHAR,
    opponent_div VARCHAR,
    opponent_schedule_url VARCHAR,
    opponent_sport VARCHAR,
    opponent_source VARCHAR,
    g INTEGER,
    a INTEGER,
    gb INTEGER
)
```

**Sort order**: `(player_id ASC, date DESC)`

**Size**: ~1 MB compressed (~2000 players × ~10 games)

**Queries**:

| Page | Query | Read Size | Notes |
|------|-------|-----------|-------|
| Player game log | `WHERE player_id = ? ORDER BY date DESC` | ~1-2 KB | Perfect: contiguous row group per player, pre-sorted |

**Trade-off**: None. This is optimal for the only use case.

---

## Summary Table

| File | Size | Sort Order | Primary Use Case | Read Size |
|------|------|------------|------------------|-----------|
| `teams.parquet` | 30 KB | `(div, rank, id)` | Teams list | 5-10 KB |
| `players.parquet` | 200 KB | `(team_div, points DESC, id)` | Players list | 20-50 KB |
| `schedules.parquet` | 150 KB | `(team_id, date)` | Team schedule | 1-2 KB |
| `games.parquet` | 150 KB | `(date DESC, id)` | Games list | 50-150 KB |
| `game_stats.parquet` | 2 MB | `(game_id, team_id, points DESC)` | Game box score | 2-3 KB |
| `player_stats.parquet` | 1 MB | `(player_id, date DESC)` | Player game log | 1-2 KB |

**Total: 6 files, ~3.5 MB**

---

## Page-to-Query Mapping

### Teams List (`/[year]/[division]`)
```sql
SELECT * FROM teams.parquet WHERE div = ? ORDER BY rank
```
- Read: 5-10 KB (one row group)
- Row group skipping: ✅
- Optimal: ✅

---

### Team Detail (`/[year]/[division]/teams/[teamId]`)
**Metadata:**
```sql
SELECT * FROM teams.parquet WHERE div = ? AND id = ?
```
- Read: 5-10 KB (scans ~50-200 teams in division)
- Row group skipping: ✅ (on div)
- Optimal: ⚠️ (acceptable trade-off)

**Schedule:**
```sql
SELECT * FROM schedules.parquet WHERE team_id = ? ORDER BY date
```
- Read: 1-2 KB
- Row group skipping: ✅
- Optimal: ✅

**Roster:**
```sql
SELECT * FROM players.parquet WHERE team_div = ? AND team_id = ? ORDER BY number
```
- Read: 20-50 KB (scans division, filters by team_id)
- Row group skipping: ✅ (on team_div)
- Optimal: ⚠️ (acceptable trade-off)

**Total: ~26-62 KB** (vs ~200-500 KB JSON)

---

### Players List (`/[year]/[division]/players`)
```sql
SELECT * FROM players.parquet WHERE team_div = ? ORDER BY points DESC LIMIT 200
```
- Read: 20-50 KB
- Row group skipping: ✅
- Optimal: ✅

---

### Player Detail (`/[year]/[division]/players/[playerId]`)
**Metadata:**
```sql
SELECT * FROM players.parquet WHERE team_div = ? AND id = ?
```
- Read: 20-50 KB (scans ~500-2000 players in division)
- Row group skipping: ✅ (on team_div)
- Optimal: ⚠️ (acceptable trade-off)

**Game log:**
```sql
SELECT * FROM player_stats.parquet WHERE player_id = ? ORDER BY date DESC
```
- Read: 1-2 KB
- Row group skipping: ✅
- Optimal: ✅

**Total: ~21-52 KB** (vs ~200-500 KB JSON)

---

### Goals Leaders (`/[year]/[division]/leaders/goals`)
```sql
SELECT * FROM players.parquet WHERE team_div = ? ORDER BY goals DESC LIMIT 50
```
- Read: 20-50 KB (scans division, re-sorts by goals)
- Row group skipping: ✅ (on team_div)
- Optimal: ⚠️ (sorted by points, not goals)

---

### Games List (`/[year]/[division]/games`)
```sql
SELECT * FROM games.parquet 
WHERE home_team_div = ? OR away_team_div = ? 
ORDER BY date DESC LIMIT 100
```
- Read: 50-150 KB (full scan, can't skip on OR condition)
- Row group skipping: ❌
- Optimal: ⚠️ (acceptable, still faster than JSON)

---

### Game Detail (`/[year]/[division]/games/[gameId]`)
**Metadata:**
```sql
SELECT * FROM games.parquet WHERE id = ?
```
- Read: 50-150 KB (full scan, no ID index)
- Row group skipping: ❌
- Optimal: ❌ (could add `games-by-id.parquet` if needed)

**Box score:**
```sql
SELECT * FROM game_stats.parquet WHERE game_id = ? ORDER BY team_id, (g + a) DESC
```
- Read: 2-3 KB
- Row group skipping: ✅
- Optimal: ✅

**Total: ~52-153 KB** (vs ~200-500 KB JSON)

---

## Performance vs JSON

| Query Type | JSON | Parquet | Improvement |
|------------|------|---------|-------------|
| Teams list | 200-500 KB | 5-10 KB | **20-50x** |
| Team detail | 200-500 KB | 26-62 KB | **3-8x** |
| Players list | 200-500 KB | 20-50 KB | **4-10x** |
| Player detail | 200-500 KB | 21-52 KB | **4-10x** |
| Game detail | 200-500 KB | 52-153 KB | **1.3-4x** |

---

## Future Optimizations

If profiling shows these queries are bottlenecks:

1. **Add `games-by-id.parquet`** (~150 KB)
   - Sorted by `(id)` for O(1) game detail lookup
   - Reduces game detail from 50-150 KB → 1-2 KB

2. **Add `players-by-id.parquet`** (~200 KB)
   - Sorted by `(id)` for O(1) player detail lookup
   - Reduces player detail from 20-50 KB → 1-2 KB

3. **Add `roster-by-team.parquet`** (~200 KB)
   - Sorted by `(team_id, number)` for O(1) team roster lookup
   - Reduces team roster from 20-50 KB → 2-5 KB

**Cost**: 3 extra files, ~550 KB total, 3 more S3 writes per scrape

**Benefit**: All detail pages become 1-5 KB point lookups

**Recommendation**: Start with 6-file schema, profile in production, add optimization files if needed.

---

## Migration Path

1. **Backend**: Update export to write 6 parquet files with specified schemas and sort orders
2. **Frontend**: Add DuckDB query functions for each page type
3. **Feature flag**: Add `?dataMode=parquet` support to all pages
4. **Test**: Validate queries in dev, compare performance
5. **Rollout**: Flip default to parquet
6. **Cleanup**: Remove legacy JSON generation

---

## Open Questions

1. **Do we need immediate consistency?** If yes, how do we handle mid-scrape state with 6 files?
   - Option A: Write to temp prefix, atomic rename (S3 doesn't support this)
   - Option B: Write sentinel file last, readers check for it
   - Option C: Accept brief inconsistency (probably fine)

2. **Should we compress game_stats differently?** It's 2 MB (57% of total size)
   - Current: gzip compression
   - Option: zstd for better compression ratio
   - Trade-off: compression vs decompression speed

3. **Do we need year-over-year queries?** (e.g., player stats across multiple seasons)
   - Current: separate files per year
   - Option: append to multi-year files
   - Trade-off: file size vs query complexity
