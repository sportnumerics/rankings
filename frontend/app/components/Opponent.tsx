import { RankedTeam } from "../server/types";
import Link from "./Link";
import Rank from "./Rank";

export default function Opponent({ opponent, link, year, home, divisional }: { opponent: RankedTeam, link: boolean, year: string, home?: boolean, divisional?: boolean }) {
    const content = <>
        <Location home={home} />
        <Rank rank={opponent?.rank} />
        <span>{opponent.name}</span><Divisional divisional={divisional} />
    </>;
    if (!link) {
        return content;
    }
    return <Link href={`/${year}/teams/${opponent.id}`} className="space-x-1">
        {content}
    </Link>
}

function Location({ home }: { home?: boolean }) {
    if (home === undefined || home === true) {
        return null;
    }
    return <span className="pr-1">@</span>;
}

function Divisional({ divisional }: { divisional?: boolean }) {
    if (divisional === undefined || divisional === true) {
        return null;
    }
    return <span className="pl-1"><sup>†</sup></span>;
}