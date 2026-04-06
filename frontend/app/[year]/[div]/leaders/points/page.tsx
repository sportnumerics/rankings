'use server';
import PageHeading from '@/app/components/PageHeading';
import { HasDivision } from '../../../../navigation';
import PlayersCard from '@/app/components/PlayersCard';
import { getRankedPlayers } from '@/app/server/players';
import { getDiv } from '@/app/server/divs';
import { by } from '@/app/shared';
import LastUpdated from '@/app/components/LastModified';

export default async function Page({ params }: { params: HasDivision }) {
    const [{ body: players, lastModified }, div] = await Promise.all([getRankedPlayers(params), getDiv(params.div)]);
    const playerRatings = Object.values(players);
    // Sort by points (goals + assists, descending)
    playerRatings.sort(by(p => p.goals + p.assists));
    const topPointsLeaders = playerRatings.slice(0, 50);
    return <>
        <PageHeading heading='Points Leaders' subHeading={div.name} />
        <PlayersCard players={topPointsLeaders} showTeam params={params} />
        <LastUpdated lastModified={lastModified} />
    </>
}
