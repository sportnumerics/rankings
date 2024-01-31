import { RankedTeamMap } from "../server/types";
import Link from "./Link";
import Rank from "./Rank";

export default function Opponent({ id, name, teams, year }: { id: string, name: string, teams: RankedTeamMap, year: string }) {
    const opponent = teams[id];
    return <Link href={`/${year}/teams/${id}`} className="space-x-1">
        <Rank rank={opponent?.rank} threshold={25} />
        <span>{name}</span>
    </Link>
}