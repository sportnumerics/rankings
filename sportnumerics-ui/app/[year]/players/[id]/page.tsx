import { date } from "@/app/formatting";
import { getPlayerStats } from "@/app/services/data";
import Link from "next/link";

interface Params {
    year: string;
    id: string;
}

export default async function Page({ params } : { params: Params}) {
    const player = await getPlayerStats(params);

    return <div>
        <h1>{player.name}</h1>
        <h2><Link href={`/${params.year}/teams/${player.team.id}`}>{player.team.name}</Link></h2>
        <table>
            <thead><tr><th>Date</th><th>Opponent</th><th>G</th><th>A</th><th>GB</th></tr></thead>
            <tbody>
                {player.stats.map(line => <tr>
                    <td>{date(line.date)}</td>
                    <td><Link href={`${params.year}/teams/${line.opponent.id}`}>{line.opponent.name}</Link></td>
                    <td>{line.g}</td>
                    <td>{line.a}</td>
                    <td>{line.gb}</td>
                    </tr>)}
            </tbody>
        </table>
    </div>
}