import { RankedTeam } from "../server/types";
import Link from "./Link";
import Rank from "./Rank";

export default function Opponent({ opponent, link, year, home }: { opponent: RankedTeam, link: boolean, year: string, home?: boolean }) {
    const nameElement = <span>{opponent.name}</span>;
    if (!link) {
        return nameElement
    }
    return <Link href={`/${year}/teams/${opponent.id}`} className="space-x-1">
        <Location home={home} />
        <Rank rank={opponent?.rank} />
        {nameElement}
    </Link>
}

function Location({ home }: { home?: boolean }) {
    if (home === undefined || home) {
        return null;
    }
    return <span className="pr-1">@</span>
}