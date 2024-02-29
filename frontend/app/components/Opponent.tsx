import { RankedTeam } from "../server/types";
import Link from "./Link";
import Rank from "./Rank";

export default function Opponent({ opponent, link, year, home, divisional }: { opponent: RankedTeam, link: boolean, year: string, home?: boolean, divisional?: boolean }) {
    const nameElement = <span>{opponent.name}</span>;
    if (!link) {
        return nameElement
    }
    return <Link href={`/${year}/teams/${opponent.id}`} className="space-x-1">
        <Location home={home} />
        <Rank rank={opponent?.rank} />
        {nameElement}
        <Divisional divisional={divisional} />
    </Link>
}

function Location({ home }: { home?: boolean }) {
    if (home === undefined || home) {
        return null;
    }
    return <span className="pr-1">@</span>
}

function Divisional({ divisional }: { divisional?: boolean }) {
    if (divisional === undefined || divisional) {
        return null;
    }
    return <span className="pl-1"><sup>†</sup></span>
}