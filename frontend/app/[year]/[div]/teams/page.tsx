'use server';
import { getRankedTeams } from '@/app/server/teams';
import { HasDivision } from '../../../navigation';
import { TeamsCard } from '@/app/components/TeamList';
import { getDiv } from '@/app/server/divs';
import PageHeading from '@/app/components/PageHeading';
import { by } from '@/app/shared';
import LastUpdated from '@/app/components/LastModified';
import { dataModeFromSearch } from '@/app/server/parquet';
import DataModeFooter from '@/app/components/DataModeFooter';

export default async function Page({ params, searchParams }: { params: HasDivision, searchParams?: Record<string, string | string[] | undefined> }) {
    const mode = dataModeFromSearch(searchParams);
    const teamsData = await getRankedTeams({ ...params, mode });
    const divPromise = getDiv(params.div);
    const [{ body: teams, lastModified, debug }, div] = await Promise.all([teamsData, divPromise]);
    const sortedTeams = Object.values(teams);
    sortedTeams.sort(by(t => t.rank));
    return <>
        <PageHeading heading='Top Teams' subHeading={div.name} />
        <TeamsCard teams={sortedTeams} params={params} />
        <DataModeFooter mode={mode} debugs={debug ? [debug] : []} />
        <LastUpdated lastModified={lastModified} />
    </>;
}