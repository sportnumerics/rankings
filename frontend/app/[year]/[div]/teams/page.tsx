import { HasDivision } from '../../../navigation';
import { twoPlaces } from '@/app/formatting';
import { Card, Error, H1, H2, Table, TableHeader } from '@/app/shared';
import { getRankedTeams } from '@/app/server/teams';
import { getDiv } from '@/app/server/divs';
import Content from '@/app/components/Content';
import Link from '@/app/components/Link';

export default async function Page({ params } : { params: HasDivision}) {
    const teamsPromise = await getRankedTeams(params);
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