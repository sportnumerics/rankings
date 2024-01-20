import {HasDivision} from '../../../navigation';
import { getDiv, getRankedTeamsByDiv } from '@/app/services/data';
import { twoPlaces } from '@/app/formatting';
import { Card, Content, Error, H1, H2, Link, Table, TableHeader } from '@/app/shared';

export default async function Page({ params } : { params: HasDivision}) {
    const teamsPromise = await getRankedTeamsByDiv(params);
    const divPromise = getDiv(params.div);
    const [teams, div] = await Promise.all([teamsPromise, divPromise]);
     if (!teams || !div) {
        console.error(`No teams or division for ${JSON.stringify(params)}`);
        return <Content><Error /></Content>
    }
    const sortedTeams = Object.values(teams);
    sortedTeams.sort((a, b) => a.rank - b.rank);
    return <Content>
        <div>
        <H1>Top Teams</H1>
        <H2>{div.name}</H2>
        </div>
        <Card>
            <Table>
                <TableHeader><tr><th>Rank</th><th>Team</th><th>Rating</th></tr></TableHeader>
                <tbody>{sortedTeams.map(team => <tr key={team.id}>
                        <td className="w-16">{team.rank}</td>
                        <td className="w-64"><Link href={`/${params.year}/${params.div}/teams/${team.id}`}>{team.name}</Link></td>
                        <td className="w-24">{twoPlaces(team.overall)}</td>
                    </tr>)}
                </tbody>
            </Table>
        </Card>
    </Content>;
}