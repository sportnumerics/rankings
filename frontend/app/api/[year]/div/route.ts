import { getGame } from "@/app/server/games";
import { getPlayerStats } from "@/app/server/players";
import { getTeam } from "@/app/server/teams";
import { NextRequest } from "next/server";

export async function GET(request: NextRequest, { params: { year } }: { params: { year: string } }) {
    const team = request.nextUrl.searchParams.get('team');
    const player = request.nextUrl.searchParams.get('player');
    const game = request.nextUrl.searchParams.get('game');

    if (team) {
        const { body: schedule } = await getTeam({ year, team });
        return Response.json(schedule.team.div);
    } else if (player) {
        const { body: stats } = await getPlayerStats({ year, player });
        const { body: schedule } = await getTeam({ year, team: stats.team.id });
        return Response.json(schedule.team.div)
    } else if (game) {
        const { body } = await getGame({ year, game });
        return Response.json(body.home_team.div);
    } else {
        return Response.json({ error: 'Must supply either a `team` or `player` search parameter.' }, { status: 400 });
    }
}