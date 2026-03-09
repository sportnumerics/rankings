# JSON vs Parquet S3 Latency Benchmark

Bucket: `sportnumerics-rankings-bucket-prod` Year: `2026` Runs per mode: `5`

| Scenario | Format | Cold p50 (ms) | Cold p95 (ms) | Warm p50 (ms) | Warm p95 (ms) |
|---|---|---:|---:|---:|---:|
| rankings_ml1 | json | 764.4 | 810.9 | 206.3 | 250.1 |
| rankings_ml1 | parquet | 1598.5 | 1616.3 | 681.1 | 693.0 |
| upcoming_ml1 | json | 1022.5 | 1349.6 | 533.2 | 569.2 |
| upcoming_ml1 | parquet | 1556.2 | 1589.9 | 700.1 | 703.9 |
| team_schedule_penn | json | 285.6 | 301.4 | 100.5 | 101.4 |
| team_schedule_penn | parquet | 868.4 | 883.3 | 346.8 | 353.7 |

## Notes
- Cold: new client/connection per run (captures cold-start connection/setup + S3 access).
- Warm: reused client/connection in-process (captures steady-state request path).
- This benchmark is network-inclusive (S3), not local-file only.
