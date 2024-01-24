'use server';
import { getDiv } from '@/app/server/divs';
import { HasDivision, Player } from '../../../navigation';
import { twoPlaces } from '@/app/formatting';
import { Card, Error, H1, H2, Table, TableHeader } from '@/app/shared';
import { getRankedPlayers } from '@/app/server/players';
import Content from '@/app/components/Content';
import Link from '@/app/components/Link';

export default async function Page({ params } : { params: HasDivision}) {
    const playersPromise = getRankedPlayers(params);
    const divPromise = getDiv(params.div);
    const [players, div] = await Promise.all([playersPromise, divPromise]);
    if (!players || !div) {
        console.error(`No players or division for ${JSON.stringify(params)}`);
        return <Error />;
    }
    const playerRatings = Object.values(players);
    playerRatings.sort((a, b) => a.rank - b.rank);
    const top200 = playerRatings.slice(0, 200);
    return <>
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
        </>;
}