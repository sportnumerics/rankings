import 'server-only';
import { createRequire } from 'module';

export type DataMode = 'json' | 'parquet';

export interface QueryDebug {
    label: string;
    queryMs: number;
    s3HeadRequests: number;
    s3GetRequests: number;
    s3RangeRequests: number;
    s3PartialBytes: number;
    note?: string;
}

let conn: any | null = null;
const nodeRequire = createRequire(import.meta.url);

function getDuckDbModule() {
    return nodeRequire('duckdb');
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

function all<T = any>(db: any, sql: string, params: any[] = []): Promise<T[]> {
    return new Promise((resolve, reject) => {
        db.all(sql, params, (err: Error | null, rows: T[]) => err ? reject(err) : resolve(rows));
    });
}

async function ensureConfigured(db: any) {
    // Lambda filesystem is mostly read-only; force duckdb home/extension dirs to /tmp.
    await run(db, "SET home_directory='/tmp'");
    await run(db, "SET extension_directory='/tmp/duckdb_extensions'");

    try {
        await run(db, 'LOAD httpfs');
    } catch {
        await run(db, 'INSTALL httpfs');
        await run(db, 'LOAD httpfs');
    }
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

    // More robust patterns for DuckDB HTTP log parsing
    // Accept both quoted and unquoted keys/values, flexible whitespace
    const headRe = /\bHEAD\b/i;
    const getRe = /\bGET\b/i;
    const rangeRe = /\b(Range|Content-Range)\b.*bytes/i;

    for (const row of rows) {
        const m = row.message || '';
        
        // Count HEAD requests
        if (headRe.test(m) && /\btype\b/i.test(m)) s3HeadRequests += 1;
        
        // Count GET requests
        if (getRe.test(m) && /\btype\b/i.test(m)) s3GetRequests += 1;
        
        // Count range requests (either Range header or Content-Range response)
        if (rangeRe.test(m)) s3RangeRequests += 1;

        // Parse partial content bytes (206 responses)
        if (/\b(206|PartialContent)\b/i.test(m) || /Content-Range.*bytes/i.test(m)) {
            const match = m.match(/Content-Length[=:\s]+(\d+)/i);
            if (match) s3PartialBytes += Number(match[1]);
        }
    }

    return { label, queryMs, s3HeadRequests, s3GetRequests, s3RangeRequests, s3PartialBytes };
}

export async function parquetQuery<T = any>(sql: string, label: string, params: any[] = []): Promise<{ rows: T[]; debug: QueryDebug }> {
    const db = getConnection();
    await ensureConfigured(db);

    const t0 = Date.now();
    const rows = await all<T>(db, sql, params);
    const queryMs = Date.now() - t0;
    let logs: Array<{ message: string }> = [];
    try {
        logs = await all<{ message: string }>(db, "select message from duckdb_logs order by timestamp desc limit 500");
    } catch {
        logs = [];
    }
    return { rows, debug: parseHttpDebug(logs, label, queryMs) };
}

export function dataModeFromSearch(searchParams?: Record<string, string | string[] | undefined>): DataMode {
    const raw = searchParams?.dataMode;
    const value = Array.isArray(raw) ? raw[0] : raw;
    return value === 'parquet' ? 'parquet' : 'json';
}
