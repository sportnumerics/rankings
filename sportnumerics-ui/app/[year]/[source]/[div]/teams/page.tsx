import Params from '../params';
import { getRankedTeamsByDiv } from '@/app/services/data';
import { twoPlaces } from '@/app/formatting';
import Link from 'next/link';

export default async function Page({ params } : { params: Params}) {
    const teams = await getRankedTeamsByDiv(params);

    const sortedTeams = Object.values(teams);
    sortedTeams.sort((a, b) => a.rank - b.rank);

    return <table>
        <thead><tr><th>Rank</th><th>Team</th><th>Rating</th></tr></thead>
        <tbody>{sortedTeams.map((team) => <tr><td>{team.rank}</td><td><Link href={`/${params.year}/teams/${team.id}`}>{team.name}</Link></td><td>{twoPlaces(team.overall)}</td></tr>)}</tbody>
        </table>;
}