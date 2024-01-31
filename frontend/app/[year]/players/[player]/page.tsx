'use server';
import { getPlayerStats } from "@/app/server/players";
import { date } from "@/app/formatting";
import { Card, ExternalLink, H1, H2, Table, TableHeader } from "@/app/shared";
import Link from "@/app/components/Link";
import Opponent from "@/app/components/Opponent";
import { getRankedTeams } from "@/app/server/teams";
import GameDate from "@/app/components/GameLink";

interface Params {
    year: string;
    player: string;
}

export default async function Page({ params }: { params: Params }) {
    const player = await getPlayerStats(params);
    const teams = await getRankedTeams({ div: player.team.div, ...params });

    return <>
        <H1>{player.name}</H1>
        <H2><Link href={`/${params.year}/teams/${player.team.id}`}>{player.team.name}</Link></H2>
        {player.external_link && <ExternalLink href={player.external_link} />}
        <Card title="Games Played">
            <Table>
                <TableHeader><tr><th>Date</th><th>Opponent</th><th>G</th><th>A</th><th>GB</th></tr></TableHeader>
                <tbody>
                    {player.stats.map(line => <tr key={line.game_id}>
                        <td className="w-16"><GameDate id={line.game_id} date={line.date} link={Boolean(line.g || line.a || line.gb)} year={params.year} hideTime /></td>
                        <td className="w-64"><Opponent id={line.opponent.id} name={line.opponent.name} teams={teams} year={params.year} /></td>
                        <td className="w-8">{line.g}</td>
                        <td className="w-8">{line.a}</td>
                        <td className="w-8">{line.gb}</td>
                    </tr>)}
                </tbody>
            </Table>
        </Card>
    </>
}