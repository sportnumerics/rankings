import { NextRequest } from "next/server";
import { DIVS } from "../../divs/route";
import source, { NotFoundError } from "../../source";
import { RatingMap, Team, TeamMap, TeamRating } from "../../types";

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

export async function getTeams({ year, div }: { year: string, div: string }): Promise<TeamMap> {
    const division = DIVS.find(division => division.id === div);
    if (!division) {
        throw new NotFoundError('division not found');
    }
    const response = await source.get(`${year}/${division.source}-teams.json`);
    const teams: Team[] = JSON.parse(response)
    return Object.fromEntries(teams.map(team => [team.id, team]));
}


export async function getTeamRatings({ year }: { year: string}): Promise<RatingMap> {
    const response = await source.get(`${year}/team-ratings.json`);
    const ratings: TeamRating[] = JSON.parse(response);
    return Object.fromEntries(ratings.map(rating => [rating.team, rating]));
}