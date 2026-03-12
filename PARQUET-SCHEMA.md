# Parquet Schema Design for Sportnumerics

## Design Approach

**One file per page component** - each file is optimized for exactly one query pattern.

**Trade-offs accepted:**
- More files (~12-13 vs monolithic design) - but still manageable
- Data duplication (player/team/game metadata repeated) - but small dataset makes this cheap
- More S3 writes per scrape - but cost is negligible (~$0.001/month)

**Benefits:**
- Every query is perfectly optimized (row group skipping + pre-sorted)
- Simple mapping: one file = one component = one query
- Independent evolution: add new pages without touching existing files
- Minimal reads: 1-50 KB per query

---

## File Inventory (12 files, ~4.5 MB total)

### Teams Pages (4 files)

1. **`teams-list.parquet`** (~30 KB) - Teams list page
2. **`team-metadata.parquet`** (~30 KB) - Team detail header
3. **`team-schedules.parquet`** (~150 KB) - Team schedule component
4. **`team-rosters.parquet`** (~200 KB) - Team roster component

### Players Pages (5 files)

5. **`players-list.parquet`** (~200 KB) - Players list page
6. **`player-metadata.parquet`** (~200 KB) - Player detail header
7. **`player-gamelogs.parquet`** (~1 MB) - Player game log component
8. **`goals-leaders.parquet`** (~200 KB) - Goals leaders page
9. **`assists-leaders.parquet`** (~200 KB) - Assists leaders page

### Games Pages (3 files)

10. **`games-list.parquet`** (~300 KB) - Games list page (rows duplicated for cross-division games)
11. **`game-metadata.parquet`** (~300 KB) - Game detail header (rows duplicated)
12. **`game-boxscores.parquet`** (~2 MB) - Game box score component

---

## Schema Definitions

### 1. teams-list.parquet

**Purpose**: Teams list page (`/[year]/[division]`)

**Schema**:
```sql
CREATE TABLE teams_list (
    div VARCHAR,             -- SORT KEY 1
    rank INTEGER,            -- SORT KEY 2
    id VARCHAR,
    name VARCHAR,
    sport VARCHAR,
    source VARCHAR,
    schedule_url VARCHAR,
    offense DOUBLE,
    defense DOUBLE,
    overall DOUBLE
)
```

**Sort**: `(div ASC, rank ASC)`

**Query**: `SELECT * FROM teams_list WHERE div = ? ORDER BY rank`

**Read size**: 5-10 KB (one row group for division)

---

### 2. team-metadata.parquet

**Purpose**: Team detail page header (`/[year]/[division]/teams/[teamId]`)

**Schema**:
```sql
CREATE TABLE team_metadata (
    div VARCHAR,             -- SORT KEY 1
    id VARCHAR,              -- SORT KEY 2
    name VARCHAR,
    sport VARCHAR,
    source VARCHAR,
    schedule_url VARCHAR,
    offense DOUBLE,
    defense DOUBLE,
    overall DOUBLE,
    rank INTEGER
)
```

**Sort**: `(div ASC, id ASC)`

**Query**: `SELECT * FROM team_metadata WHERE div = ? AND id = ?`

**Read size**: 1-2 KB (row group skip to division, scan ~50-200 teams)

**Note**: Could be pure O(1) lookup if we sort by `(id)` only, but that loses row group skipping. Current approach is acceptable (scan 50-200 rows = 1-2 KB).

---

### 3. team-schedules.parquet

**Purpose**: Team schedule component on team detail page

**Schema**:
```sql
CREATE TABLE team_schedules (
    div VARCHAR,                    -- SORT KEY 1 (team's division)
    team_id VARCHAR,                -- SORT KEY 2
    date VARCHAR,                   -- SORT KEY 3 (ISO format)
    game_id VARCHAR,
    opponent_id VARCHAR,
    opponent_name VARCHAR,
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

**Sort**: `(div ASC, team_id ASC, date ASC)`

**Query**: `SELECT * FROM team_schedules WHERE div = ? AND team_id = ? ORDER BY date`

**Read size**: 1-2 KB (perfect: row group skip to division → team → read contiguous block)

---

### 4. team-rosters.parquet

**Purpose**: Team roster component on team detail page

**Schema**:
```sql
CREATE TABLE team_rosters (
    div VARCHAR,                    -- SORT KEY 1 (team's division)
    team_id VARCHAR,                -- SORT KEY 2
    number INTEGER,                 -- SORT KEY 3 (jersey number)
    player_id VARCHAR,
    player_name VARCHAR,
    position VARCHAR,
    class_year VARCHAR,
    eligibility VARCHAR,
    height VARCHAR,
    weight VARCHAR,
    high_school VARCHAR,
    hometown VARCHAR,
    external_link VARCHAR,
    points DOUBLE,                  -- for display
    goals DOUBLE,
    assists DOUBLE
)
```

**Sort**: `(div ASC, team_id ASC, number ASC)`

**Query**: `SELECT * FROM team_rosters WHERE div = ? AND team_id = ? ORDER BY number`

**Read size**: 2-5 KB (perfect: row group skip to division → team → read contiguous block)

---

### 5. players-list.parquet

**Purpose**: Players list page (`/[year]/[division]/players`)

**Schema**:
```sql
CREATE TABLE players_list (
    div VARCHAR,                    -- SORT KEY 1
    points DOUBLE,                  -- SORT KEY 2 (DESC)
    player_id VARCHAR,
    player_name VARCHAR,
    team_id VARCHAR,
    team_name VARCHAR,
    team_schedule_url VARCHAR,
    team_sport VARCHAR,
    team_source VARCHAR,
    goals DOUBLE,
    assists DOUBLE,
    position VARCHAR,
    number INTEGER,
    class_year VARCHAR
)
```

**Sort**: `(div ASC, points DESC)`

**Query**: `SELECT * FROM players_list WHERE div = ? ORDER BY points DESC LIMIT 200`

**Read size**: 20-50 KB (row group skip to division, read top-N)

---

### 6. player-metadata.parquet

**Purpose**: Player detail page header (`/[year]/[division]/players/[playerId]`)

**Schema**:
```sql
CREATE TABLE player_metadata (
    div VARCHAR,                    -- SORT KEY 1
    player_id VARCHAR,              -- SORT KEY 2
    player_name VARCHAR,
    team_id VARCHAR,
    team_name VARCHAR,
    team_schedule_url VARCHAR,
    team_sport VARCHAR,
    team_source VARCHAR,
    points DOUBLE,
    goals DOUBLE,
    assists DOUBLE,
    position VARCHAR,
    number INTEGER,
    class_year VARCHAR,
    eligibility VARCHAR,
    height VARCHAR,
    weight VARCHAR,
    high_school VARCHAR,
    hometown VARCHAR,
    external_link VARCHAR
)
```

**Sort**: `(div ASC, player_id ASC)`

**Query**: `SELECT * FROM player_metadata WHERE div = ? AND player_id = ?`

**Read size**: 5-20 KB (row group skip to division, scan ~500-2000 players)

**Note**: Could be O(1) with sort by `(player_id)` only, but loses row group skipping. Current approach acceptable.

---

### 7. player-gamelogs.parquet

**Purpose**: Player game log component on player detail page

**Schema**:
```sql
CREATE TABLE player_gamelogs (
    div VARCHAR,                    -- SORT KEY 1 (player's team division)
    player_id VARCHAR,              -- SORT KEY 2
    date VARCHAR,                   -- SORT KEY 3 (ISO format, DESC via negative)
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

**Sort**: `(div ASC, player_id ASC, date DESC)`

**Query**: `SELECT * FROM player_gamelogs WHERE div = ? AND player_id = ? ORDER BY date DESC`

**Read size**: 1-2 KB (perfect: row group skip to division → player → read contiguous block)

---

### 8. goals-leaders.parquet

**Purpose**: Goals leaders page (`/[year]/[division]/leaders/goals`)

**Schema**:
```sql
CREATE TABLE goals_leaders (
    div VARCHAR,                    -- SORT KEY 1
    goals DOUBLE,                   -- SORT KEY 2 (DESC)
    player_id VARCHAR,
    player_name VARCHAR,
    team_id VARCHAR,
    team_name VARCHAR,
    team_schedule_url VARCHAR,
    team_sport VARCHAR,
    team_source VARCHAR,
    points DOUBLE,
    assists DOUBLE,
    position VARCHAR,
    number INTEGER,
    class_year VARCHAR
)
```

**Sort**: `(div ASC, goals DESC)`

**Query**: `SELECT * FROM goals_leaders WHERE div = ? ORDER BY goals DESC LIMIT 50`

**Read size**: 10-30 KB (row group skip to division, read top-N)

---

### 9. assists-leaders.parquet

**Purpose**: Assists leaders page (`/[year]/[division]/leaders/assists`)

**Schema**:
```sql
CREATE TABLE assists_leaders (
    div VARCHAR,                    -- SORT KEY 1
    assists DOUBLE,                 -- SORT KEY 2 (DESC)
    player_id VARCHAR,
    player_name VARCHAR,
    team_id VARCHAR,
    team_name VARCHAR,
    team_schedule_url VARCHAR,
    team_sport VARCHAR,
    team_source VARCHAR,
    points DOUBLE,
    goals DOUBLE,
    position VARCHAR,
    number INTEGER,
    class_year VARCHAR
)
```

**Sort**: `(div ASC, assists DESC)`

**Query**: `SELECT * FROM assists_leaders WHERE div = ? ORDER BY assists DESC LIMIT 50`

**Read size**: 10-30 KB (row group skip to division, read top-N)

---

### 10. games-list.parquet

**Purpose**: Games list page (`/[year]/[division]/games`)

**Schema**:
```sql
CREATE TABLE games_list (
    div VARCHAR,                    -- SORT KEY 1 (DUPLICATED: home_team_div OR away_team_div)
    date VARCHAR,                   -- SORT KEY 2 (ISO format, DESC)
    game_id VARCHAR,
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

**Sort**: `(div ASC, date DESC)`

**Duplication**: Each game appears **twice** (once for home team's div, once for away team's div)
- Cross-division games are rare (~5-10% of games)
- Dedup on read: `SELECT DISTINCT ON (game_id) ...` or client-side dedup

**Query**: `SELECT * FROM games_list WHERE div = ? ORDER BY date DESC LIMIT 100`

**Read size**: 20-50 KB (row group skip to division, read top-N)

**Size impact**: ~150 KB → ~300 KB due to duplication (acceptable trade-off for perfect queries)

---

### 11. game-metadata.parquet

**Purpose**: Game detail page header (`/[year]/[division]/games/[gameId]`)

**Schema**:
```sql
CREATE TABLE game_metadata (
    div VARCHAR,                    -- SORT KEY 1 (DUPLICATED: home_team_div OR away_team_div)
    game_id VARCHAR,                -- SORT KEY 2
    date VARCHAR,
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

**Sort**: `(div ASC, game_id ASC)`

**Duplication**: Each game appears **twice** (once for home team's div, once for away team's div)

**Query**: `SELECT * FROM game_metadata WHERE div = ? AND game_id = ? LIMIT 1`

**Read size**: 1-2 KB (row group skip to division, scan ~500-1500 games, return first match)

**Note**: We have `div` from URL path, so we can skip to right row group. Scan is acceptable (1-2 KB).

**Alternative**: Sort by `(game_id)` only for O(1) lookup, but loses row group skipping benefits.

---

### 12. game-boxscores.parquet

**Purpose**: Game box score component on game detail page

**Schema**:
```sql
CREATE TABLE game_boxscores (
    game_id VARCHAR,                -- SORT KEY 1
    team_id VARCHAR,                -- SORT KEY 2
    points_desc DOUBLE,             -- SORT KEY 3 (negative of g+a for DESC display)
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

**Sort**: `(game_id ASC, team_id ASC, points_desc DESC)`

**Query**: `SELECT * FROM game_boxscores WHERE game_id = ? ORDER BY team_id, (g + a) DESC`

**Read size**: 2-3 KB (perfect: row group skip to game → read contiguous block, pre-sorted)

---

## Summary Table

| File | Size | Sort Order | Query Read | Row Group Skip |
|------|------|------------|------------|----------------|
| `teams-list.parquet` | 30 KB | `(div, rank)` | 5-10 KB | ✅ div |
| `team-metadata.parquet` | 30 KB | `(div, id)` | 1-2 KB | ✅ div |
| `team-schedules.parquet` | 150 KB | `(div, team_id, date)` | 1-2 KB | ✅ div, team_id |
| `team-rosters.parquet` | 200 KB | `(div, team_id, number)` | 2-5 KB | ✅ div, team_id |
| `players-list.parquet` | 200 KB | `(div, points DESC)` | 20-50 KB | ✅ div |
| `player-metadata.parquet` | 200 KB | `(div, player_id)` | 5-20 KB | ✅ div |
| `player-gamelogs.parquet` | 1 MB | `(div, player_id, date DESC)` | 1-2 KB | ✅ div, player_id |
| `goals-leaders.parquet` | 200 KB | `(div, goals DESC)` | 10-30 KB | ✅ div |
| `assists-leaders.parquet` | 200 KB | `(div, assists DESC)` | 10-30 KB | ✅ div |
| `games-list.parquet` | 300 KB | `(div, date DESC)` | 20-50 KB | ✅ div |
| `game-metadata.parquet` | 300 KB | `(div, game_id)` | 1-2 KB | ✅ div |
| `game-boxscores.parquet` | 2 MB | `(game_id, team_id, pts DESC)` | 2-3 KB | ✅ game_id |

**Total: 12 files, ~4.5 MB**

---

## Performance Comparison

| Page | JSON (current) | Parquet (proposed) | Improvement |
|------|----------------|-------------------|-------------|
| Teams list | 200-500 KB | 5-10 KB | **20-50x** |
| Team detail | 200-500 KB | 4-9 KB | **22-125x** |
| Players list | 200-500 KB | 20-50 KB | **4-10x** |
| Player detail | 200-500 KB | 6-22 KB | **9-83x** |
| Goals leaders | 200-500 KB | 10-30 KB | **7-50x** |
| Games list | 200-500 KB | 20-50 KB | **4-10x** |
| Game detail | 200-500 KB | 3-5 KB | **40-167x** |

---

## Data Consistency

**Challenge**: 12 files written sequentially means brief inconsistency window.

**Solution**: Sentinel file pattern
1. Write all 12 parquet files to S3
2. Write `{year}/_ready` sentinel file last
3. Readers check for sentinel before querying
4. If sentinel missing, fall back to JSON or show stale data

**Alternative**: Atomic batch upload
- Generate all 12 files locally
- Upload via S3 batch API (single operation)
- Trade-off: requires temp disk space (~4.5 MB), more complex orchestration

---

## Migration Path

### Phase 1: Backend Export
1. Update backend to generate 12 parquet files with specified schemas
2. Implement duplication logic for games (write each cross-division game twice)
3. Write sentinel file after all exports complete
4. Keep JSON generation for now (fallback)

### Phase 2: Frontend Queries
1. Add DuckDB loader that checks for sentinel file
2. Implement 12 query functions (one per file)
3. Add `?dataMode=parquet` flag to all pages
4. Test in dev environment

### Phase 3: Rollout
1. Deploy to prod with parquet disabled by default
2. Enable for internal testing
3. Monitor performance and errors
4. Flip default to parquet
5. Remove JSON generation after 1-2 weeks

---

## Implementation Notes

### Duplication Logic (games)

```python
def export_games_list(games, output_path):
    rows = []
    for game in games:
        # Add row for home team's division
        rows.append({
            'div': game.home_team_div,
            'date': game.date,
            'game_id': game.id,
            # ... all other fields
        })
        # Add row for away team's division (if different)
        if game.away_team_div != game.home_team_div:
            rows.append({
                'div': game.away_team_div,
                'date': game.date,
                'game_id': game.id,
                # ... all other fields
            })
    
    df = pd.DataFrame(rows)
    df = df.sort_values(['div', 'date'], ascending=[True, False])
    df.to_parquet(output_path, compression='gzip', index=False)
```

### Deduplication on Read

```typescript
// Client-side dedup
const games = await query(`SELECT * FROM games_list WHERE div = ? ORDER BY date DESC LIMIT 100`, [div]);
const uniqueGames = Array.from(new Map(games.map(g => [g.game_id, g])).values());

// OR server-side dedup
SELECT DISTINCT ON (game_id) * FROM games_list WHERE div = ? ORDER BY date DESC LIMIT 100
```

### Sort Order for DESC columns

For columns that need DESC sort (date, points, goals, assists):
- **Date**: Use ISO format `YYYY-MM-DD`, then negate or reverse in sort
- **Numeric**: Store as negative value (e.g., `points_desc = -points`) for ASC parquet sort that displays DESC

---

## Open Questions

1. **Should game-metadata use (game_id) sort instead of (div, game_id)?**
   - Pro: True O(1) lookup (1-2 KB always)
   - Con: Loses row group skipping benefits for games list
   - Current: Scan ~500-1500 games within division = 1-2 KB (acceptable)

2. **Compression: gzip vs zstd?**
   - gzip: better compatibility, slower
   - zstd: better compression ratio, faster, requires DuckDB zstd extension
   - Recommendation: start with gzip, test zstd later

3. **Row group size tuning?**
   - Default: ~122 MB uncompressed (often too large for our use case)
   - Recommendation: 1-10 MB row groups for better granularity
   - Configure via: `row_group_size` parameter in parquet writer
