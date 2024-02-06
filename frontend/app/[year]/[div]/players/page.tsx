'use server';
import PageHeading from '@/app/components/PageHeading';
import { HasDivision } from '../../../navigation';
import PlayersCard from '@/app/components/PlayersCard';
import { getRankedPlayers } from '@/app/server/players';
import { getDiv } from '@/app/server/divs';
import { by } from '@/app/shared';

export default async function Page({ params }: { params: HasDivision }) {
    const [players, div] = await Promise.all([getRankedPlayers(params), getDiv(params.div)]);
    const playerRatings = Object.values(players);
    playerRatings.sort(by(p => p.rank));
    const topPlayers = playerRatings.slice(0, 200);
    return <>
        <PageHeading heading='Top Scoring Players' subHeading={div.name} />
        <PlayersCard players={topPlayers} showTeam params={params} />
    </>
}
