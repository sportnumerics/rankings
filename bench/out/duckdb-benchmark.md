# DuckDB Parquet Benchmark

Dataset: `bench/data/2026/v2`

## Query timings (ms)

| Query | Warm p50 | Warm p95 | Cold p50 | Cold p95 | Notes |
|---|---:|---:|---:|---:|---|
| rankings_ml1_targeted | 2.6 | 2.8 | 3.2 | 3.3 | Rankings page shape: top 25 teams for NCAA ML1 (targeted NCAA teams parquet) |
| rankings_ml1_glob | 2.8 | 3.1 | 3.5 | 3.7 | Same query but globbing all teams parquet files (tests partition/path pruning impact) |
| upcoming_games_ml1_targeted | 3.1 | 3.4 | 3.8 | 3.8 | Upcoming games page shape: next 14 days, NCAA ML1 |
| team_schedule_flatten | 48.2 | 55.4 | 48.2 | 62.4 | Team page shape: one team schedule unnest |
| team_schedule_from_games | 2.5 | 4.0 | 3.2 | 3.4 | Alternative team-page shape from flat games parquet (same team) |
| player_leaderboard_team | 11.0 | 15.3 | 12.8 | 13.2 | Player leaderboard shape: join ratings + players |
| player_leaderboard_ratings_only | 8.7 | 14.2 | 9.5 | 11.8 | Alternative leaderboard from player_ratings only (name already present) |

## Row group structure

| File | Row groups | Compressed bytes |
|---|---:|---:|
| `bench/data/2026/v2/games/ncaa.parquet` | 1 | 1766114 |
| `bench/data/2026/v2/games/mcla.parquet` | 1 | 733896 |
| `bench/data/2026/v2/schedules/ncaa.parquet` | 1 | 153349 |
| `bench/data/2026/v2/schedules/mcla.parquet` | 1 | 439141 |
| `bench/data/2026/v2/players/data.parquet` | 1 | 2019747 |
| `bench/data/2026/v2/player_ratings/data.parquet` | 1 | 1277335 |
