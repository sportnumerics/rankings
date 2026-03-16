import { twoPlaces } from '@/app/formatting';
import { Card, LoadingRows, Table, TableHeader } from '@/app/shared';
import Link from '@/app/components/Link';
import { HasDivision } from '../navigation';
import { RankedPlayer } from '../server/types';
import EmptyCard from './EmptyCard';

export default function PlayersCard({ title, players, showTeam, hideRank, params, cardClassName }: { title?: string, players: RankedPlayer[], showTeam?: boolean, hideRank?: boolean, params: HasDivision, cardClassName?: string }) {
    if (players.length === 0) {
        return <EmptyCard text='No player rankings yet...' />;
    }

    return <Card title={title} className={cardClassName}>
        <PlayersTable players={players} showTeam={showTeam} hideRank={hideRank} params={params} />
    </Card>;
}

export function PlayersTable({ players, showTeam = false, hideRank = false, params }: { players: RankedPlayer[], showTeam?: boolean, hideRank?: boolean, params: HasDivision }) {
    const hasGamesPlayed = players.some(p => p.games_played && p.games_played > 0);
    
    return <Table>
        <Header hideRank={hideRank} showPerGame={hasGamesPlayed} />
        <tbody>
            {players.map(player => {
                const gp = player.games_played || 0;
                const ppg = gp > 0 ? player.points / gp : 0;
                const gpg = gp > 0 ? player.goals / gp : 0;
                const apg = gp > 0 ? player.assists / gp : 0;
                
                return <tr key={player.id}>
                    {!hideRank && player.rank && <td className="w-32">{player.rank}</td>}
                    <td className={showTeam ? "w-96" : "w-64"}><Link href={`/${params.year}/players/${player.id}`}>{player.name}</Link>{showTeam && ` (${player.team.name})`}</td>
                    <td className="w-24">{twoPlaces(player.points)}</td>
                    <td className="w-24">{twoPlaces(player.goals)}</td>
                    <td className="w-24">{twoPlaces(player.assists)}</td>
                    {hasGamesPlayed && <td className="w-16">{gp}</td>}
                    {hasGamesPlayed && <td className="w-20">{twoPlaces(ppg)}</td>}
                    {hasGamesPlayed && <td className="w-20">{twoPlaces(gpg)}</td>}
                    {hasGamesPlayed && <td className="w-20">{twoPlaces(apg)}</td>}
                </tr>
            })}
        </tbody>
    </Table>
}

function Header({ hideRank, showPerGame }: { hideRank?: boolean, showPerGame?: boolean }) {
    return <TableHeader><tr>
        {!hideRank && <th>Rank</th>}
        <th>Name</th>
        <th>Pts</th>
        <th>G</th>
        <th>A</th>
        {showPerGame && <th>GP</th>}
        {showPerGame && <th>PPG</th>}
        {showPerGame && <th>GPG</th>}
        {showPerGame && <th>APG</th>}
    </tr></TableHeader>
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