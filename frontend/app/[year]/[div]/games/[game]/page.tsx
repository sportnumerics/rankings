'use server';
import { getGame } from "@/app/server/games";
import { GameStatLine } from "@/app/server/types";
import { longDatetime } from "@/app/formatting";
import { Card, ExternalLink, H1, H2, Table, TableHeader } from "@/app/shared";
import Link from "next/link";

interface Params {
    year: string;
    div: string;
    game: string;
}

export default async function Page({ params } : { params: Params}) {
    const game = await getGame(params);

    function StatLines({ stats }: {stats: GameStatLine[]}) {
        const sortedStats = stats.slice();
        sortedStats.sort((a, b) => (b.a + b.g - a.a - a.g));

        return <Table>
            <TableHeader><tr><th>#</th><th>Name</th><th>Position</th><th>G</th><th>A</th><th>GB</th></tr></TableHeader>
            <tbody>
                {sortedStats.map(line => <tr key={line.player.id}>
                    <td className="w-16">{line.number}</td>
                    <td className="w-64"><Link href={`/${params.year}/${params.div}/players/${line.player.id}`}>{line.player.name}</Link></td>
                    <td className="w-24">{line.position}</td>
                    <td className="w-8">{line.g}</td>
                    <td className="w-8">{line.a}</td>
                    <td className="w-8">{line.gb}</td>
                </tr>)}
            </tbody>
        </Table>
    }

    return <>
        <div>
        <H1>{game.away_team.name} at {game.home_team.name}</H1>
        <H2>{longDatetime(game.date)}</H2>
        {game.external_link && <ExternalLink href={game.external_link} />}
        </div>
        <Card>
        <H2>{game.away_team.name} <span className="text-xl">{game.result.away_score}</span> - {game.home_team.name} <span className="text-xl">{game.result.home_score}</span></H2>
        </Card>
        <Card title={game.away_team.name}>
            <StatLines stats={game.away_stats} />
        </Card>
        <Card title={game.home_team.name}>
            <StatLines stats={game.home_stats} />
        </Card>
    </>
}
