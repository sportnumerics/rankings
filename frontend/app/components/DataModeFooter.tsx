import { QueryDebug } from "@/app/server/parquet";

export default function DataModeFooter({ mode, debugs }: { mode: string, debugs: QueryDebug[] }) {
    if (mode !== 'parquet') return null;

    return <div className="mt-4 text-xs text-slate-500 border-t pt-2">
        <div><strong>Data mode:</strong> parquet (DuckDB/S3 ranges)</div>
        {debugs.map((d, i) => (
            <div key={i}>
                {d.label}: {d.queryMs}ms · HEAD {d.s3HeadRequests} · GET {d.s3GetRequests} · ranges {d.s3RangeRequests} · bytes {d.s3PartialBytes.toLocaleString()}
            </div>
        ))}
    </div>;
}
