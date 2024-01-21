import { NextRequest } from "next/server";
import { getTeamRatings, getTeams } from "../../teams";

export async function GET(request: NextRequest, { params: { year } }: { params: { year: string }}) {
    const div = request.nextUrl.searchParams.get('div');
    if (!div) {
        return new Response('query parameter `div` is required', { status: 400 });
    }
    const teamsPromise = getTeams({year, div});
    const ratingsPromise = getTeamRatings({year});
    const [teams, ratings] = await Promise.all([teamsPromise, ratingsPromise]);
    const teamRatings = Object.values(teams)
        .filter(team => team.div === div)
        .map(team => ({...team, ...ratings[team.id]}));
    teamRatings.sort((a, b) => (b.overall ?? -Infinity) - (a.overall ?? -Infinity));
    return Response.json(Object.fromEntries(teamRatings.map((team, i) => [team.id, {...team, rank: i + 1}])));
}
