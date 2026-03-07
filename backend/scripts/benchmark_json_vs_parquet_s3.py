#!/usr/bin/env python3
import argparse
import json
import os
import statistics
import time
from datetime import date

import boto3
import duckdb

BUCKET = 'sportnumerics-rankings-bucket-prod'
YEAR = '2026'
REGION = 'us-west-2'
TEAM_ID = 'ml-ncaa-penn'
START = date(2026, 3, 7)
END = date(2026, 3, 21)


def p95(xs):
    xs = sorted(xs)
    return xs[max(0, int(0.95 * len(xs)) - 1)]


def bench_json_rankings(client):
    tr = json.loads(client.get_object(Bucket=BUCKET, Key=f'data/{YEAR}/team-ratings.json')['Body'].read())
    teams = json.loads(client.get_object(Bucket=BUCKET, Key=f'data/{YEAR}/ncaa-teams.json')['Body'].read())
    teams_by_id = {t['id']: t for t in teams}
    rows = [r for r in tr if teams_by_id.get(r['team'], {}).get('div') == 'ml1']
    rows.sort(key=lambda r: r['overall'], reverse=True)
    return rows[:25]


def bench_json_upcoming(client):
    games_by_date = json.loads(client.get_object(Bucket=BUCKET, Key=f'data/{YEAR}/games.json')['Body'].read())
    rows = []
    for _, games in games_by_date.items():
        for g in games:
            if g.get('homeDiv') != 'ml1':
                continue
            d = date.fromisoformat(g['date'][:10])
            if START <= d <= END:
                rows.append(g)
    rows.sort(key=lambda g: g['date'])
    return rows[:200]


def bench_json_team_schedule(client):
    schedule = json.loads(client.get_object(Bucket=BUCKET, Key=f'data/{YEAR}/schedules/{TEAM_ID}.json')['Body'].read())
    games = schedule.get('games', [])
    games.sort(key=lambda g: g['date'])
    return games


def duck_conn():
    c = duckdb.connect(database=':memory:')
    c.execute('LOAD httpfs;')
    c.execute(f"SET s3_region='{REGION}';")
    c.execute(f"SET s3_access_key_id='{os.environ['AWS_ACCESS_KEY_ID']}';")
    c.execute(f"SET s3_secret_access_key='{os.environ['AWS_SECRET_ACCESS_KEY']}';")
    tok = os.environ.get('AWS_SESSION_TOKEN')
    if tok:
        c.execute(f"SET s3_session_token='{tok}';")
    return c


PARQUET_SQL = {
    'rankings': f"""
        SELECT tr.team, t.name, tr.overall
        FROM read_parquet('s3://{BUCKET}/data/{YEAR}/v2/team_ratings/data.parquet') tr
        JOIN read_parquet('s3://{BUCKET}/data/{YEAR}/v2/teams/ncaa.parquet') t ON tr.team=t.id
        WHERE t.div='ml1'
        ORDER BY tr.overall DESC
        LIMIT 25
    """,
    'upcoming': f"""
        SELECT g.date, g.away_team.name, g.home_team.name
        FROM read_parquet('s3://{BUCKET}/data/{YEAR}/v2/games/ncaa.parquet') g
        JOIN read_parquet('s3://{BUCKET}/data/{YEAR}/v2/teams/ncaa.parquet') h ON g.home_team.id=h.id
        WHERE h.div='ml1' AND CAST(g.date AS DATE) BETWEEN DATE '{START.isoformat()}' AND DATE '{END.isoformat()}'
        ORDER BY g.date
        LIMIT 200
    """,
    'team_schedule': f"""
        SELECT date,
               CASE WHEN home_team.id='{TEAM_ID}' THEN away_team.name ELSE home_team.name END AS opponent,
               CASE WHEN home_team.id='{TEAM_ID}' THEN result.home_score ELSE result.away_score END AS points_for,
               CASE WHEN home_team.id='{TEAM_ID}' THEN result.away_score ELSE result.home_score END AS points_against
        FROM read_parquet('s3://{BUCKET}/data/{YEAR}/v2/games/ncaa.parquet')
        WHERE home_team.id='{TEAM_ID}' OR away_team.id='{TEAM_ID}'
        ORDER BY date
    """,
}


def measure_json(fn, runs):
    cold = []
    warm = []

    for _ in range(runs):
        c = boto3.client('s3', region_name=REGION)
        t = time.perf_counter(); fn(c); cold.append((time.perf_counter() - t) * 1000)

    c = boto3.client('s3', region_name=REGION)
    for _ in range(runs):
        t = time.perf_counter(); fn(c); warm.append((time.perf_counter() - t) * 1000)

    return {
        'cold_p50_ms': statistics.median(cold),
        'cold_p95_ms': p95(cold),
        'warm_p50_ms': statistics.median(warm),
        'warm_p95_ms': p95(warm),
    }


def measure_parquet(sql, runs):
    cold = []
    warm = []

    for _ in range(runs):
        c = duck_conn()
        t = time.perf_counter(); c.execute(sql).fetchall(); cold.append((time.perf_counter() - t) * 1000)
        c.close()

    c = duck_conn()
    c.execute(sql).fetchall()
    for _ in range(runs):
        t = time.perf_counter(); c.execute(sql).fetchall(); warm.append((time.perf_counter() - t) * 1000)
    c.close()

    return {
        'cold_p50_ms': statistics.median(cold),
        'cold_p95_ms': p95(cold),
        'warm_p50_ms': statistics.median(warm),
        'warm_p95_ms': p95(warm),
    }


def main():
    ap = argparse.ArgumentParser(description='Benchmark JSON vs Parquet query latency over S3')
    ap.add_argument('--runs', type=int, default=5)
    ap.add_argument('--out', default='bench/out/json-vs-parquet-s3-benchmark.md')
    args = ap.parse_args()

    results = {
        'rankings_ml1': {
            'json': measure_json(bench_json_rankings, args.runs),
            'parquet': measure_parquet(PARQUET_SQL['rankings'], args.runs),
        },
        'upcoming_ml1': {
            'json': measure_json(bench_json_upcoming, args.runs),
            'parquet': measure_parquet(PARQUET_SQL['upcoming'], args.runs),
        },
        'team_schedule_penn': {
            'json': measure_json(bench_json_team_schedule, args.runs),
            'parquet': measure_parquet(PARQUET_SQL['team_schedule'], args.runs),
        },
    }

    lines = [
        '# JSON vs Parquet S3 Latency Benchmark',
        '',
        f'Bucket: `{BUCKET}` Year: `{YEAR}` Runs per mode: `{args.runs}`',
        '',
        '| Scenario | Format | Cold p50 (ms) | Cold p95 (ms) | Warm p50 (ms) | Warm p95 (ms) |',
        '|---|---|---:|---:|---:|---:|',
    ]

    for scenario, vals in results.items():
        for fmt in ['json', 'parquet']:
            r = vals[fmt]
            lines.append(
                f"| {scenario} | {fmt} | {r['cold_p50_ms']:.1f} | {r['cold_p95_ms']:.1f} | {r['warm_p50_ms']:.1f} | {r['warm_p95_ms']:.1f} |"
            )

    lines += [
        '',
        '## Notes',
        '- Cold: new client/connection per run (captures cold-start connection/setup + S3 access).',
        '- Warm: reused client/connection in-process (captures steady-state request path).',
        '- This benchmark is network-inclusive (S3), not local-file only.',
        '',
    ]

    out_path = args.out
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        f.write('\n'.join(lines))

    print('\n'.join(lines))


if __name__ == '__main__':
    main()
