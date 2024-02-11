export default function LastUpdated({ lastModified }: { lastModified?: Date }) {
    if (!lastModified) {
        return null;
    }
    return <div className="text-xs text-slate-300">Last updated: {lastModified.toLocaleString('en-US')}</div>
}