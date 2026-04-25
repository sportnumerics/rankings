import { getGame } from "@/app/server/games";
import { getPlayerStats } from "@/app/server/players";
import { getTeam } from "@/app/server/teams";
import { NextRequest } from "next/server";

function ok(div: string) {
    return Response.json({ div });
}

function bad(message: string, status = 400) {
    return Response.json({ error: message }, { status });
}

export async function GET(request: NextRequest, { params: { year } }: { params: { year: string } }) {
    const team = request.nextUrl.searchParams.get('team');
    const player = request.nextUrl.searchParams.get('player');
    const game = request.nextUrl.searchParams.get('game');

    try {
        if (team) {
            const { body: schedule } = await getTeam({ year, team });
            if (!schedule.team?.div) {
                return bad('team division unavailable', 404);
            }
            return ok(schedule.team.div);
        } else if (player) {
            const { body: stats } = await getPlayerStats({ year, player });
            const div = stats.team?.div;
            if (div) {
                return ok(div);
            }

            const teamId = stats.team?.id;
            if (!teamId) {
                return bad('player team unavailable', 404);
            }

            const { body: schedule } = await getTeam({ year, team: teamId });
            if (!schedule.team?.div) {
                return bad('player division unavailable', 404);
            }
            return ok(schedule.team.div);
        } else if (game) {
            const { body } = await getGame({ year, game });
            const div = body.home_team?.div ?? body.away_team?.div;
            if (!div) {
                return bad('game division unavailable', 404);
            }
            return ok(div);
        }

        return bad('Must supply either a `team`, `player`, or `game` search parameter.');
    } catch (error) {
        console.error('division lookup failed', { year, team, player, game, error });
        return bad('division lookup failed', 500);
    }
}
