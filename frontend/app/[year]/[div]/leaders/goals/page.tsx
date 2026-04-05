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
    // Sort by goals (descending)
    playerRatings.sort(by(p => p.goals));
    const topGoalScorers = playerRatings.slice(0, 50);
    return <>
        <PageHeading heading='Goals Leaders' subHeading={div.name} />
        <PlayersCard players={topGoalScorers} showTeam params={params} />
        <LastUpdated lastModified={lastModified} />
    </>
}
