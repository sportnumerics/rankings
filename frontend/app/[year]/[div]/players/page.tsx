'use server';
import PageHeading from '@/app/components/PageHeading';
import { HasDivision } from '../../../navigation';
import PlayersCard from '@/app/components/PlayersCard';
import { getRankedPlayers } from '@/app/server/players';
import { getDiv } from '@/app/server/divs';
import { by } from '@/app/shared';
import LastUpdated from '@/app/components/LastModified';
import { dataModeFromSearch } from '@/app/server/parquet';
import DataModeFooter from '@/app/components/DataModeFooter';

export default async function Page({ params, searchParams }: { params: HasDivision, searchParams?: Record<string, string | string[] | undefined> }) {
    const mode = dataModeFromSearch(searchParams);
    const [{ body: players, lastModified, debug }, div] = await Promise.all([
        getRankedPlayers({ ...params, team: null, mode }),
        getDiv(params.div)
    ]);
    const playerRatings = Object.values(players);
    playerRatings.sort(by(p => p.rank));
    const topPlayers = playerRatings.slice(0, 200);
    return <>
        <PageHeading heading='Top Scoring Players' subHeading={div.name} />
        <PlayersCard players={topPlayers} showTeam params={params} />
        <DataModeFooter mode={mode} debugs={debug ? [debug] : []} />
        <LastUpdated lastModified={lastModified} />
    </>
}
