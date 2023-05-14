import { datetime } from "@/app/formatting";
import { GameStatLine, getGame } from "@/app/services/data";
import Link from "next/link";

interface Params {
    year: string;
    id: string;
}

export default async function Page({ params } : { params: Params}) {
    const game = await getGame(params);

    function StatLines({ stats }: {stats: GameStatLine[]}) {
        const sortedStats = stats.slice();
        sortedStats.sort((a, b) => (b.a + b.g - a.a - a.g));

        return <table>
            <thead><tr><th>Number</th><th>Name</th><th>Position</th><th>G</th><th>A</th><th>GB</th></tr></thead>
            <tbody>
                {sortedStats.map(line => <tr>
                    <td>{line.number}</td>
                    <td><Link href={`/${params.year}/players/${line.player.id}`}>{line.player.name}</Link></td>
                    <td>{line.position}</td>
                    <td>{line.g}</td>
                    <td>{line.a}</td>
                    <td>{line.gb}</td>
                </tr>)}
            </tbody>
        </table>
    }

    return <div>
        <h1>{game.away_team.name} at {game.home_team.name}</h1>
        <h2>{datetime(game.date)}</h2>
        <h3>{game.away_team.name} {game.result.away_score} - {game.home_team.name} {game.result.home_score}</h3>
        {game.external_link && <div><Link href={game.external_link}>External Link</Link></div>}
        <div>
            <h2>{game.away_team.name}</h2>
            <StatLines stats={game.away_stats} />
        </div>
        <div>
            <h2>{game.home_team.name}</h2>
            <StatLines stats={game.home_stats} />
        </div>
    </div>
}
