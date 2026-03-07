#!/usr/bin/env python3
import argparse
import json
import statistics
import time
from dataclasses import dataclass
from pathlib import Path

import duckdb


@dataclass
class QueryCase:
    name: str
    sql: str
    notes: str


def build_cases(base: Path):
    return [
        QueryCase(
            name="rankings_ml1_targeted",
            notes="Rankings page shape: top 25 teams for NCAA ML1 (targeted NCAA teams parquet)",
            sql=f"""
                SELECT tr.team, t.name, tr.overall
                FROM read_parquet('{(base / 'team_ratings/data.parquet').as_posix()}') tr
                JOIN read_parquet('{(base / 'teams/ncaa.parquet').as_posix()}') t ON tr.team = t.id
                WHERE t.div = 'ml1'
                ORDER BY tr.overall DESC
                LIMIT 25
            """,
        ),
        QueryCase(
            name="rankings_ml1_glob",
            notes="Same query but globbing all teams parquet files (tests partition/path pruning impact)",
            sql=f"""
                SELECT tr.team, t.name, tr.overall
                FROM read_parquet('{(base / 'team_ratings/data.parquet').as_posix()}') tr
                JOIN read_parquet('{(base / 'teams/*.parquet').as_posix()}') t ON tr.team = t.id
                WHERE t.div = 'ml1' AND t.source = 'ncaa'
                ORDER BY tr.overall DESC
                LIMIT 25
            """,
        ),
        QueryCase(
            name="upcoming_games_ml1_targeted",
            notes="Upcoming games page shape: next 14 days, NCAA ML1",
            sql=f"""
                SELECT g.date, g.away_team.name AS away_team, g.home_team.name AS home_team
                FROM read_parquet('{(base / 'games/ncaa.parquet').as_posix()}') g
                JOIN read_parquet('{(base / 'teams/ncaa.parquet').as_posix()}') h ON g.home_team.id = h.id
                WHERE h.div = 'ml1'
                  AND CAST(g.date AS DATE) BETWEEN DATE '2026-03-07' AND DATE '2026-03-21'
                ORDER BY g.date
                LIMIT 200
            """,
        ),
        QueryCase(
            name="team_schedule_flatten",
            notes="Team page shape: one team schedule unnest",
            sql=f"""
                SELECT s.team.id AS team_id, s.team.name AS team_name, g.date, g.opponent.name AS opponent,
                       g.result.points_for AS points_for, g.result.points_against AS points_against
                FROM read_parquet('{(base / 'schedules/ncaa.parquet').as_posix()}') s,
                     UNNEST(s.games) AS t(g)
                WHERE s.team.id = 'ml-ncaa-penn'
                ORDER BY g.date
            """,
        ),
        QueryCase(
            name="team_schedule_from_games",
            notes="Alternative team-page shape from flat games parquet (same team)",
            sql=f"""
                SELECT date,
                       CASE WHEN home_team.id='ml-ncaa-penn' THEN away_team.name ELSE home_team.name END as opponent,
                       CASE WHEN home_team.id='ml-ncaa-penn' THEN result.home_score ELSE result.away_score END as points_for,
                       CASE WHEN home_team.id='ml-ncaa-penn' THEN result.away_score ELSE result.home_score END as points_against
                FROM read_parquet('{(base / 'games/ncaa.parquet').as_posix()}')
                WHERE home_team.id='ml-ncaa-penn' OR away_team.id='ml-ncaa-penn'
                ORDER BY date
            """,
        ),
        QueryCase(
            name="player_leaderboard_team",
            notes="Player leaderboard shape: join ratings + players",
            sql=f"""
                SELECT p.id, p.name, pr.points, pr.goals, pr.assists
                FROM read_parquet('{(base / 'player_ratings/data.parquet').as_posix()}') pr
                JOIN read_parquet('{(base / 'players/data.parquet').as_posix()}') p ON pr.id = p.id
                WHERE pr.team.id = 'ml-ncaa-penn'
                ORDER BY pr.points DESC
                LIMIT 50
            """,
        ),
        QueryCase(
            name="player_leaderboard_ratings_only",
            notes="Alternative leaderboard from player_ratings only (name already present)",
            sql=f"""
                SELECT id, name, points, goals, assists
                FROM read_parquet('{(base / 'player_ratings/data.parquet').as_posix()}')
                WHERE team.id = 'ml-ncaa-penn'
                ORDER BY points DESC
                LIMIT 50
            """,
        ),
    ]


def measure(case: QueryCase, runs: int = 20, warmup: int = 2):
    con = duckdb.connect(database=':memory:')
    con.execute("PRAGMA enable_object_cache=true")
    for _ in range(warmup):
        con.execute(case.sql).fetchall()

    warm_times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        con.execute(case.sql).fetchall()
        warm_times.append((time.perf_counter() - t0) * 1000)

    cold_times = []
    for _ in range(min(8, runs)):
        cold = duckdb.connect(database=':memory:')
        cold.execute("PRAGMA enable_object_cache=false")
        t0 = time.perf_counter()
        cold.execute(case.sql).fetchall()
        cold_times.append((time.perf_counter() - t0) * 1000)
        cold.close()

    out = {
        "name": case.name,
        "notes": case.notes,
        "warm_ms": {
            "p50": statistics.median(warm_times),
            "p95": sorted(warm_times)[max(0, int(0.95 * len(warm_times)) - 1)],
            "avg": statistics.mean(warm_times),
        },
        "cold_ms": {
            "p50": statistics.median(cold_times),
            "p95": sorted(cold_times)[max(0, int(0.95 * len(cold_times)) - 1)],
            "avg": statistics.mean(cold_times),
        },
    }
    con.close()
    return out


def parquet_row_group_summary(base: Path):
    con = duckdb.connect(database=':memory:')
    files = [
        base / 'games/ncaa.parquet',
        base / 'games/mcla.parquet',
        base / 'schedules/ncaa.parquet',
        base / 'schedules/mcla.parquet',
        base / 'players/data.parquet',
        base / 'player_ratings/data.parquet',
    ]
    rows = []
    for f in files:
        groups = con.execute(
            f"""
            SELECT row_group_id, SUM(total_compressed_size) AS compressed_bytes
            FROM parquet_metadata('{f.as_posix()}')
            GROUP BY 1
            ORDER BY 1
            """
        ).fetchall()
        rows.append({
            "file": f.as_posix(),
            "row_groups": len(groups),
            "compressed_bytes": sum(g[1] for g in groups),
        })
    con.close()
    return rows


def main():
    parser = argparse.ArgumentParser(description='Benchmark current parquet layout with DuckDB query shapes')
    parser.add_argument('--data-root', required=True, help='Path to .../data/<year>/v2')
    parser.add_argument('--out-dir', default='bench/out', help='Output directory for report JSON/MD')
    parser.add_argument('--runs', type=int, default=20, help='Warm run count per query')
    args = parser.parse_args()

    base = Path(args.data_root)
    cases = build_cases(base)

    results = [measure(c, runs=args.runs) for c in cases]
    rg = parquet_row_group_summary(base)

    out = {
        'dataset': str(base),
        'results': results,
        'row_group_summary': rg,
    }

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'duckdb-benchmark.json').write_text(json.dumps(out, indent=2) + '\n')

    lines = [
        '# DuckDB Parquet Benchmark',
        '',
        f'Dataset: `{base}`',
        '',
        '## Query timings (ms)',
        '',
        '| Query | Warm p50 | Warm p95 | Cold p50 | Cold p95 | Notes |',
        '|---|---:|---:|---:|---:|---|',
    ]

    for r in results:
        lines.append(
            f"| {r['name']} | {r['warm_ms']['p50']:.1f} | {r['warm_ms']['p95']:.1f} | {r['cold_ms']['p50']:.1f} | {r['cold_ms']['p95']:.1f} | {r['notes']} |"
        )

    lines += [
        '',
        '## Row group structure',
        '',
        '| File | Row groups | Compressed bytes |',
        '|---|---:|---:|',
    ]
    for row in rg:
        lines.append(f"| `{row['file']}` | {row['row_groups']} | {row['compressed_bytes']} |")

    (out_dir / 'duckdb-benchmark.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
