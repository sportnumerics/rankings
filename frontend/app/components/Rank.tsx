export default function Rank({ rank }: { rank?: number }) {
    if (!rank || rank > 25) {
        return null;
    }
    return <span className="text-xs pr-1">{rank}</span>
}