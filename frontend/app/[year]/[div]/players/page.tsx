import { HasDivision } from '../../../navigation';
import { getDiv, getRankedPlayersByDiv } from '@/app/services/data';
import { twoPlaces } from '@/app/formatting';
import { Card, Content, Error, H1, H2, Link, Table, TableHeader } from '@/app/shared';

export default async function Page({ params } : { params: HasDivision}) {
    const playersPromise = getRankedPlayersByDiv(params);
    const divPromise = getDiv(params.div);
    const [players, div] = await Promise.all([playersPromise, divPromise]);
    if (!players || !div) {
        console.error(`No players or division for ${JSON.stringify(params)}`);
        return <Content><Error /></Content>
    }
    const playerRatings = Object.values(players);
    playerRatings.sort((a, b) => a.rank - b.rank);
    const top200 = playerRatings.slice(0, 200);
    return <Content>
            <div>
            <H1>Top Players</H1>
            <H2>{div.name}</H2>
            </div>
            <Card>
                <Table>
                    <TableHeader><tr><th>Rank</th><th>Name</th><th>Rating</th></tr></TableHeader>
                    <tbody>
                    {top200.map(player => <tr key={player.id}>
                        <td className="w-16">{player.rank}</td>
                        <td className="w-96"><Link href={`/${params.year}/${params.div}/players/${player.id}`}>{player.name}</Link> ({player.team.name})</td>
                        <td className="w-24">{twoPlaces(player.points)}</td></tr>)}
                    </tbody>
                </Table>
            </Card>
        </Content>;
}