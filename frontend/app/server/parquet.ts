import 'server-only';

export type DataMode = 'json' | 'parquet';

export interface QueryDebug {
    label: string;
    queryMs: number;
    s3HeadRequests: number;
    s3GetRequests: number;
    s3RangeRequests: number;
    s3PartialBytes: number;
}

let conn: any | null = null;

function getDuckDbModule() {
    return (0, eval)('require')('duckdb');
}

function getConnection() {
    if (conn) return conn;
    const duckdb = getDuckDbModule();
    conn = new duckdb.Database(':memory:');
    return conn;
}

function run(db: any, sql: string): Promise<void> {
    return new Promise((resolve, reject) => {
        db.run(sql, (err: Error | null) => err ? reject(err) : resolve());
    });
}

function all<T = any>(db: any, sql: string): Promise<T[]> {
    return new Promise((resolve, reject) => {
        db.all(sql, (err: Error | null, rows: T[]) => err ? reject(err) : resolve(rows));
    });
}

async function ensureConfigured(db: any) {
    await run(db, 'LOAD httpfs');
    await run(db, "SET enable_http_logging=true");
    await run(db, "SET s3_region='us-west-2'");

    const access = process.env.AWS_ACCESS_KEY_ID;
    const secret = process.env.AWS_SECRET_ACCESS_KEY;
    const token = process.env.AWS_SESSION_TOKEN;
    if (access && secret) {
        await run(db, `SET s3_access_key_id='${access}'`);
        await run(db, `SET s3_secret_access_key='${secret}'`);
        if (token) {
            await run(db, `SET s3_session_token='${token}'`);
        }
    }
}

function parseHttpDebug(rows: Array<{ message: string }>, label: string, queryMs: number): QueryDebug {
    let s3HeadRequests = 0;
    let s3GetRequests = 0;
    let s3RangeRequests = 0;
    let s3PartialBytes = 0;

    for (const row of rows) {
        const m = row.message || '';
        if (m.includes("'type': HEAD")) s3HeadRequests += 1;
        if (m.includes("'type': GET")) s3GetRequests += 1;
        if (m.includes("Range='bytes=")) s3RangeRequests += 1;
        if (m.includes('PartialContent_206')) {
            const match = m.match(/Content-Length=(\d+)/);
            if (match) s3PartialBytes += Number(match[1]);
        }
    }

    return { label, queryMs, s3HeadRequests, s3GetRequests, s3RangeRequests, s3PartialBytes };
}

export async function parquetQuery<T = any>(sql: string, label: string): Promise<{ rows: T[]; debug: QueryDebug }> {
    const db = getConnection();
    await ensureConfigured(db);

    const t0 = Date.now();
    const rows = await all<T>(db, sql);
    const queryMs = Date.now() - t0;
    const logs = await all<{ message: string }>(db, "select message from duckdb_logs where type='HTTP' order by timestamp desc limit 200");
    return { rows, debug: parseHttpDebug(logs, label, queryMs) };
}

export function dataModeFromSearch(searchParams?: Record<string, string | string[] | undefined>): DataMode {
    const raw = searchParams?.dataMode;
    const value = Array.isArray(raw) ? raw[0] : raw;
    return value === 'parquet' ? 'parquet' : 'json';
}
