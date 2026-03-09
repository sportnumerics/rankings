# Parquet Schema Design for Sportnumerics

## Goals
- Minimal S3 writes (4-5 files per year)
- Optimal query performance via sort order and columnar storage
- Support all current pages with DuckDB range requests

---

## File 1: `{year}/teams.parquet`

**Purpose**: Teams list page, team lookups, division filtering

**Schema**:
```sql
CREATE TABLE teams (
    id VARCHAR,              -- team identifier (e.g., "brigham-young-21")
    name VARCHAR,            -- display name
    div VARCHAR,             -- division (d1, d2, d3, etc.)
    sport VARCHAR,           -- "lacrosse"
    source VARCHAR,          -- "ncaa" or "mcla"
    schedule_url VARCHAR,    -- external schedule link
    offense DOUBLE,          -- offensive rating
    defense DOUBLE,          -- defensive rating
    overall DOUBLE,          -- overall rating
    rank INTEGER             -- rank within division (computed from overall)
)
```

**Sort order**: `(div ASC, rank ASC)`
- Enables fast division filtering with row group skipping
- Teams list query reads only one row group (~5-10 KB)

**Size estimate**: ~200 teams × ~150 bytes = ~30 KB compressed

**Queries**:
- Teams list: `SELECT * FROM teams WHERE div = ? ORDER BY rank`
- Team lookup: `SELECT * FROM teams WHERE id = ?`

---

## File 2: `{year}/players.parquet`

**Purpose**: Players list, leaderboards, player lookups

**Schema**:
```sql
CREATE TABLE players (
    id VARCHAR,              -- player identifier
    name VARCHAR,            -- display name
    team_id VARCHAR,         -- FK to teams.id
    team_name VARCHAR,       -- denormalized for display
    team_div VARCHAR,        -- denormalized for filtering
    team_schedule_url VARCHAR, -- denormalized
    team_sport VARCHAR,      -- denormalized
    team_source VARCHAR,     -- denormalized
    points DOUBLE,           -- total rating (goals + assists)
    goals DOUBLE,            -- goals rating
    assists DOUBLE,          -- assists rating
    rank INTEGER,            -- rank by points within division (optional precompute)
    position VARCHAR,        -- player position
    number INTEGER,          -- jersey number
    class_year VARCHAR,      -- Fr, So, Jr, Sr
    eligibility VARCHAR,     -- eligibility status
    height VARCHAR,          -- height string
    weight VARCHAR,          -- weight string
    high_school VARCHAR,     -- high school
    hometown VARCHAR,        -- hometown
    external_link VARCHAR    -- link to source roster page
)
```

**Sort order**: `(team_div ASC, points DESC)`
- Division filtering + leaderboards read minimal row groups
- Players by team: secondary index on team_id (or partition by team_id)

**Size estimate**: ~2000 players × ~300 bytes = ~200 KB compressed

**Queries**:
- Players list: `SELECT * FROM players WHERE team_div = ? ORDER BY points DESC LIMIT 200`
- Goals leaders: `SELECT * FROM players WHERE team_div = ? ORDER BY goals DESC LIMIT 50`
- Assists leaders: `SELECT * FROM players WHERE team_div = ? ORDER BY assists DESC LIMIT 50`
- Player lookup: `SELECT * FROM players WHERE id = ?`
- Team roster: `SELECT * FROM players WHERE team_id = ? ORDER BY number`

---

## File 3: `{year}/schedules.parquet`

**Purpose**: Team detail pages (schedule + results)

**Schema**:
```sql
CREATE TABLE schedules (
    team_id VARCHAR,                -- FK to teams.id
    game_id VARCHAR,                -- unique game identifier
    date VARCHAR,                   -- ISO date string
    opponent_id VARCHAR,            -- opponent team id
    opponent_name VARCHAR,          -- denormalized
    opponent_div VARCHAR,           -- denormalized (for divisional flag)
    opponent_schedule_url VARCHAR,  -- denormalized
    opponent_sport VARCHAR,         -- denormalized
    opponent_source VARCHAR,        -- denormalized
    home BOOLEAN,                   -- true if home game
    points_for INTEGER,             -- team's score (null if not played)
    points_against INTEGER,         -- opponent's score (null if not played)
    details_url VARCHAR             -- link to game details page
)
```

**Sort order**: `(team_id ASC, date ASC)`
- Team schedule query reads one contiguous row group (~1-2 KB)

**Size estimate**: ~200 teams × ~15 games × ~200 bytes = ~150 KB compressed

**Queries**:
- Team schedule: `SELECT * FROM schedules WHERE team_id = ? ORDER BY date`
- Upcoming games: `SELECT * FROM schedules WHERE team_id = ? AND points_for IS NULL ORDER BY date`

---

## File 4: `{year}/games.parquet`

**Purpose**: Game detail pages (box scores), games list

**Schema**:
```sql
CREATE TABLE games (
    id VARCHAR,                    -- unique game identifier
    date VARCHAR,                  -- ISO datetime
    external_link VARCHAR,         -- link to source
    home_team_id VARCHAR,          -- FK to teams.id
    home_team_name VARCHAR,        -- denormalized
    home_team_div VARCHAR,         -- denormalized
    home_team_schedule_url VARCHAR, -- denormalized
    home_team_sport VARCHAR,       -- denormalized
    home_team_source VARCHAR,      -- denormalized
    away_team_id VARCHAR,          -- FK to teams.id
    away_team_name VARCHAR,        -- denormalized
    away_team_div VARCHAR,         -- denormalized
    away_team_schedule_url VARCHAR, -- denormalized
    away_team_sport VARCHAR,       -- denormalized
    away_team_source VARCHAR,      -- denormalized
    home_score INTEGER,            -- final score
    away_score INTEGER             -- final score
)
```

**Sort order**: `(date DESC)`
- Recent games list reads first row group only

**Size estimate**: ~1500 games × ~300 bytes = ~150 KB compressed

**Queries**:
- Games list: `SELECT * FROM games WHERE home_team_div = ? OR away_team_div = ? ORDER BY date DESC LIMIT 100`
- Game lookup: `SELECT * FROM games WHERE id = ?`

---

## File 5: `{year}/game_stats.parquet`

**Purpose**: Game detail pages (player box scores)

**Schema**:
```sql
CREATE TABLE game_stats (
    game_id VARCHAR,               -- FK to games.id
    team_id VARCHAR,               -- which team this stat line belongs to
    player_id VARCHAR,             -- FK to players.id
    player_name VARCHAR,           -- denormalized
    number INTEGER,                -- jersey number
    position VARCHAR,              -- player position
    g INTEGER,                     -- goals
    a INTEGER,                     -- assists
    gb INTEGER,                    -- ground balls
    face_offs_won INTEGER,         -- faceoffs won (nullable)
    face_offs_lost INTEGER         -- faceoffs lost (nullable)
)
```

**Sort order**: `(game_id ASC, team_id ASC, g + a DESC)`
- Game detail query reads one row group (~2-3 KB)
- Pre-sorted by points for display

**Size estimate**: ~1500 games × ~40 players × ~100 bytes = ~2 MB compressed

**Queries**:
- Game stats: `SELECT * FROM game_stats WHERE game_id = ? ORDER BY team_id, (g + a) DESC`

---

## File 6: `{year}/player_stats.parquet`

**Purpose**: Player detail pages (game log)

**Schema**:
```sql
CREATE TABLE player_stats (
    player_id VARCHAR,             -- FK to players.id
    game_id VARCHAR,               -- FK to games.id
    date VARCHAR,                  -- ISO date
    opponent_id VARCHAR,           -- opponent team id
    opponent_name VARCHAR,         -- denormalized
    opponent_div VARCHAR,          -- denormalized
    opponent_schedule_url VARCHAR, -- denormalized
    opponent_sport VARCHAR,        -- denormalized
    opponent_source VARCHAR,       -- denormalized
    g INTEGER,                     -- goals
    a INTEGER,                     -- assists
    gb INTEGER                     -- ground balls
)
```

**Sort order**: `(player_id ASC, date DESC)`
- Player game log query reads one row group (~1 KB)

**Size estimate**: ~2000 players × ~10 games × ~150 bytes = ~1 MB compressed

**Queries**:
- Player game log: `SELECT * FROM player_stats WHERE player_id = ? ORDER BY date DESC`

---

## Summary

| File | Size (compressed) | Sort Order | Use Case |
|------|------------------|------------|----------|
| `teams.parquet` | ~30 KB | `(div, rank)` | Teams list, lookups |
| `players.parquet` | ~200 KB | `(team_div, points DESC)` | Players list, leaderboards |
| `schedules.parquet` | ~150 KB | `(team_id, date)` | Team schedules |
| `games.parquet` | ~150 KB | `(date DESC)` | Games list, lookups |
| `game_stats.parquet` | ~2 MB | `(game_id, team_id)` | Game box scores |
| `player_stats.parquet` | ~1 MB | `(player_id, date DESC)` | Player game logs |

**Total: 6 files, ~3.5 MB, 6 writes per scrape**

**Performance gains:**
- Division-filtered queries: read ~5-50 KB instead of 200-500 KB (10-50x bandwidth reduction)
- Detail page queries: read ~1-3 KB via range requests (100x+ bandwidth reduction)
- No client-side sorting/filtering (faster initial render)
- Better CloudFront caching (fewer files to invalidate)

---

## Page-to-Query Mapping

### Teams Page (`/[year]/[division]`)
**Components:**
- Teams list ranked by overall rating

**Queries:**
1. `SELECT * FROM teams.parquet WHERE div = ? ORDER BY rank ASC`
   - Reads: ~5-10 KB (one row group for division)
   - Returns: ~50-200 teams depending on division

---

### Team Page (`/[year]/[division]/teams/[teamId]`)
**Components:**
- Team metadata (name, ratings, rank)
- Schedule (upcoming and past games)
- Roster (players list)

**Queries:**
1. `SELECT * FROM teams.parquet WHERE id = ?`
   - Reads: ~1-2 KB (single team via range request)
   - Returns: 1 team
2. `SELECT * FROM schedules.parquet WHERE team_id = ? ORDER BY date ASC`
   - Reads: ~1-2 KB (contiguous block for team)
   - Returns: ~15 games
3. `SELECT * FROM players.parquet WHERE team_id = ? ORDER BY number ASC`
   - Reads: ~2-5 KB (all players for team)
   - Returns: ~20-40 players

**Total: ~4-9 KB**

---

### Players Page (`/[year]/[division]/players`)
**Components:**
- Top 200 players ranked by points

**Queries:**
1. `SELECT * FROM players.parquet WHERE team_div = ? ORDER BY points DESC LIMIT 200`
   - Reads: ~20-50 KB (division-filtered row groups)
   - Returns: 200 players

---

### Player Page (`/[year]/[division]/players/[playerId]`)
**Components:**
- Player metadata (name, team, position, stats)
- Game log (stats per game)

**Queries:**
1. `SELECT * FROM players.parquet WHERE id = ?`
   - Reads: ~1-2 KB (single player via range request)
   - Returns: 1 player
2. `SELECT * FROM player_stats.parquet WHERE player_id = ? ORDER BY date DESC`
   - Reads: ~1-2 KB (contiguous block for player)
   - Returns: ~10-15 games

**Total: ~2-4 KB**

---

### Goals Leaders Page (`/[year]/[division]/leaders/goals`)
**Components:**
- Top 50 players ranked by goals

**Queries:**
1. `SELECT * FROM players.parquet WHERE team_div = ? ORDER BY goals DESC LIMIT 50`
   - Reads: ~10-30 KB (division-filtered row groups)
   - Returns: 50 players

---

### Games Page (`/[year]/[division]/games`)
**Components:**
- Recent 100 games for division

**Queries:**
1. `SELECT * FROM games.parquet WHERE home_team_div = ? OR away_team_div = ? ORDER BY date DESC LIMIT 100`
   - Reads: ~20-50 KB (recent games from top row groups)
   - Returns: 100 games

---

### Game Page (`/[year]/[division]/games/[gameId]`)
**Components:**
- Game metadata (date, teams, score)
- Box score (player stats for both teams)

**Queries:**
1. `SELECT * FROM games.parquet WHERE id = ?`
   - Reads: ~1-2 KB (single game via range request)
   - Returns: 1 game
2. `SELECT * FROM game_stats.parquet WHERE game_id = ? ORDER BY team_id ASC, (g + a) DESC`
   - Reads: ~2-3 KB (all player stats for game)
   - Returns: ~40 stat lines (both teams)

**Total: ~3-5 KB**

---

## Migration Path

1. Update backend export to write parquet with these schemas + sort orders
2. Add server-side DuckDB query functions for each page type
3. Add `?dataMode=parquet` support to all pages (reuse existing pattern from #58)
4. Test in dev, compare performance
5. Flip default to parquet once validated
6. Remove legacy JSON generation
