import { date } from "@/app/formatting";
import { getPlayerStats } from "@/app/services/data";
import { Card, Content, Error, ExternalLink, H1, H2, Link, Table, TableHeader } from "@/app/shared";

interface Params {
    year: string;
    div: string;
    player: string;
}

export default async function Page({ params } : { params: Params}) {
    const player = await getPlayerStats(params);
    if (!player) {
        console.error(`No player for ${JSON.stringify(params)}`);
        return <Content><Error /></Content>
    }

    return <Content>
        <H1>{player.name}</H1>
        <H2><Link href={`/${params.year}/${params.div}/teams/${player.team.id}`}>{player.team.name}</Link></H2>
        {player.external_link && <ExternalLink href={player.external_link} /> }
        <Card title="Games Played">
        <Table>
            <TableHeader><tr><th>Date</th><th>Opponent</th><th>G</th><th>A</th><th>GB</th></tr></TableHeader>
            <tbody>
                {player.stats.map(line => <tr>
                    <td className="w-16">{date(line.date)}</td>
                    <td className="w-64"><Link href={`${params.year}/${params.div}/teams/${line.opponent.id}`}>{line.opponent.name}</Link></td>
                    <td className="w-8">{line.g}</td>
                    <td className="w-8">{line.a}</td>
                    <td className="w-8">{line.gb}</td>
                    </tr>)}
            </tbody>
        </Table>
        </Card>
    </Content>
}