import { twoPlaces } from '@/app/formatting';
import { Card, LoadingRows, Table, TableHeader } from '@/app/shared';
import Link from '@/app/components/Link';
import { HasDivision } from '../navigation';
import { RankedPlayer } from '../server/types';
import EmptyCard from './EmptyCard';

export default function PlayersCard({ players, showTeam, hideRank, params }: { players: RankedPlayer[], showTeam?: boolean, hideRank?: boolean, params: HasDivision }) {
    if (players.length === 0) {
        return <EmptyCard text='No player rankings yet...' />;
    }

    return <Card>
        <PlayersTable players={players} showTeam={showTeam} hideRank={hideRank} params={params} />
    </Card>;
}

export function PlayersTable({ players, showTeam = false, hideRank = false, params }: { players: RankedPlayer[], showTeam?: boolean, hideRank?: boolean, params: HasDivision }) {
    return <Table>
        <Header hideRank={hideRank} />
        <tbody>
        {players.map(player => <tr key={player.id}>
            {!hideRank && <td className="w-24">{player.rank}</td>}
            <td className={showTeam ? "w-96" : "w-64"}><Link href={`/${params.year}/players/${player.id}`}>{player.name}</Link>{showTeam && ` (${player.team.name})`}</td>
            <td className="w-24">{twoPlaces(player.points)}</td></tr>)}
        </tbody>
    </Table>
}

function Header({ hideRank }: { hideRank?: boolean }) {
    return <TableHeader><tr>{! hideRank && <th>Rank</th>}<th>Name</th><th>Rating</th></tr></TableHeader>
}

export function LoadingPlayersTable({ hideRank = false, showTeam = false }: { hideRank?: boolean, showTeam?: boolean }) {
    const start = hideRank ? 1 : 0;
    const cols = ["w-24", (showTeam ? "w-96" : "w-64"), "w-24"].slice(start);
    const skels = [["w-4", "w-48", "w-6"], ["w-3", "w-64", "w-5"], ["w-5", "w-52", "w-7"]].map(r => r.slice(start));
    return <Table>
        <Header />
        <LoadingRows cols={cols} skeletons={skels} />
    </Table>
}