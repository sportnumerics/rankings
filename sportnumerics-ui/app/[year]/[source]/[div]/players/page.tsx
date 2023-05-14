import Params from '../params';
import { getRankedPlayersByDiv } from '@/app/services/data';
import { twoPlaces } from '@/app/formatting';
import Link from 'next/link';

export default async function Page({ params } : { params: Params}) {
    const players = await getRankedPlayersByDiv(params);
    const playerRatings = Object.values(players);
    playerRatings.sort((a, b) => a.rank - b.rank);
    const top200 = playerRatings.slice(0, 200);
    return <div>
            <h1>Top Players ({params.source} {params.div})</h1>
            <table>
                <thead><tr><th>Rank</th><th>Name</th><th>Rating</th></tr></thead>
                <tbody>
                {top200.map((player) => <tr>
                    <td>{player.rank}</td>
                    <td><Link href={`/${params.year}/players/${player.id}`}>{player.name}</Link> ({player.team.name})</td>
                    <td>{twoPlaces(player.points)}</td></tr>)}
                </tbody>
            </table>
        </div>;
}