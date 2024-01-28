import { twoPlaces } from '@/app/formatting';
import { Card, LoadingRows, Table, TableHeader } from '@/app/shared';
import Link from '@/app/components/Link';
import { HasDivision } from '../navigation';
import { RankedTeam } from '../server/types';
import EmptyCard from './EmptyCard';
import classNames from 'classnames';

export function TeamsCard({ teams, params }: { teams: RankedTeam[], params: HasDivision }) {
    if (teams.length === 0) {
        return <EmptyCard text='No team rankings yet...'/>
    }

    return <Card>
        <TeamsTable teams={teams} params={params} />
    </Card>
}

export function TeamsTable({ teams, params }: { teams: RankedTeam[], params: HasDivision }) {
    return <Table>
        <Header />
        <tbody>{teams.map(team => <tr key={team.id}>
                <td className="w-16">{team.rank}</td>
                <td className="w-64"><Link href={`/${params.year}/teams/${team.id}`}>{team.name}</Link></td>
                <td className="w-24">{twoPlaces(team.overall)}</td>
            </tr>)}
        </tbody>
    </Table>
}

function Header() {
    return <TableHeader><tr><th>Rank</th><th>Team</th><th>Rating</th></tr></TableHeader>;
}

export function LoadingTeamsTable() {
    return <Table>
        <Header />
        <LoadingRows cols={["w-16", "w-64", "w-24"]} skeletons={[["w-4", "w-48", "w-6"], ["w-5", "w-52", "w-5"], ["w-4", "w-36", "w-7"]]} />
    </Table>
}
