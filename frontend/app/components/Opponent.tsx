import { RankedTeam } from "../server/types";
import Link from "./Link";
import Rank from "./Rank";

export default function Opponent({ opponent, link, year }: { opponent: RankedTeam, link: boolean, year: string }) {
    const nameElement = <span>{opponent.name}</span>;
    if (!link) {
        return nameElement
    }
    return <Link href={`/${year}/teams/${opponent.id}`} className="space-x-1">
        <Rank rank={opponent?.rank} />
        {nameElement}
    </Link>
}