'use server';
import { getRankedTeams } from '@/app/server/teams';
import { HasDivision } from '../../../navigation';
import { TeamsCard } from '@/app/components/TeamList';
import { getDiv } from '@/app/server/divs';
import PageHeading from '@/app/components/PageHeading';
import { by } from '@/app/shared';

export default async function Page({ params }: { params: HasDivision }) {
    const teamsPromise = await getRankedTeams(params);
    const divPromise = getDiv(params.div);
    const [teams, div] = await Promise.all([teamsPromise, divPromise]);
    const sortedTeams = Object.values(teams);
    sortedTeams.sort(by(t => t.rank));
    return <>
        <PageHeading heading='Top Teams' subHeading={div.name} />
        <TeamsCard teams={sortedTeams} params={params} />
    </>;
}