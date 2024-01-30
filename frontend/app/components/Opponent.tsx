import { RankedTeamMap } from "../server/types";
import Link from "./Link";

export default function Opponent({ id, name, teams, year }: { id: string, name: string, teams: RankedTeamMap, year: string }) {
    const opponent = teams[id];
    return <Link href={`/${year}/teams/${id}`} className="space-x-1">
        <span className="text-xs">{opponent?.rank <= 25 ? opponent.rank : ""}</span>
        <span>{name}</span>
    </Link>
}