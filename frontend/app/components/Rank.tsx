export default function Rank({ rank, threshold }: { rank: number, threshold?: number }) {
    if (!rank || (threshold && rank > threshold)) {
        return null;
    }
    return <span className="text-xs pr-1">{rank}</span>
}