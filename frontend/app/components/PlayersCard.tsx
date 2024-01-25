import { twoPlaces } from '@/app/formatting';
import { Card, Table, TableHeader } from '@/app/shared';
import Link from '@/app/components/Link';
import { HasDivision } from '../navigation';
import { RankedPlayer } from '../server/types';
import EmptyCard from './EmptyCard';

export default function PlayersCard({ players, params }: { players: RankedPlayer[], params: HasDivision }) {
    if (players.length === 0) {
        return <EmptyCard text='No player rankings yet...' />;
    }

    return <Card>
        <PlayersTable players={players} params={params} />
    </Card>;
}

export function PlayersTable({ players, params }: { players: RankedPlayer[], params: HasDivision }) {
    return <Table>
        <TableHeader><tr><th>Rank</th><th>Name</th><th>Rating</th></tr></TableHeader>
        <tbody>
        {players.map(player => <tr key={player.id}>
            <td className="w-16">{player.rank}</td>
            <td className="w-96"><Link href={`/${params.year}/${params.div}/players/${player.id}`}>{player.name}</Link> ({player.team.name})</td>
            <td className="w-24">{twoPlaces(player.points)}</td></tr>)}
        </tbody>
    </Table>
}