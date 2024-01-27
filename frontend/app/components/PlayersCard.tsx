import { twoPlaces } from '@/app/formatting';
import { Card, Table, TableHeader } from '@/app/shared';
import Link from '@/app/components/Link';
import { HasDivision } from '../navigation';
import { RankedPlayer } from '../server/types';
import EmptyCard from './EmptyCard';

export default function PlayersCard({ players, showTeam = false, params }: { players: RankedPlayer[], showTeam?: boolean, params: HasDivision }) {
    if (players.length === 0) {
        return <EmptyCard text='No player rankings yet...' />;
    }

    return <Card>
        <PlayersTable players={players} showTeam={showTeam} params={params} />
    </Card>;
}

export function PlayersTable({ players, showTeam, params }: { players: RankedPlayer[], showTeam: boolean, params: HasDivision }) {
    return <Table>
        <TableHeader><tr><th>Rank</th><th>Name</th><th>Rating</th></tr></TableHeader>
        <tbody>
        {players.map(player => <tr key={player.id}>
            <td className="w-24">{player.rank}</td>
            <td className={showTeam ? "w-96" : "w-64"}><Link href={`/${params.year}/players/${player.id}`}>{player.name}</Link>{showTeam && ` (${player.team.name})`}</td>
            <td className="w-24">{twoPlaces(player.points)}</td></tr>)}
        </tbody>
    </Table>
}