
import { NextRequest } from "next/server";
import source from "../../source";
import { PlayerRating, PlayerRatingMap, TeamMap } from "../../types";
import { getTeams } from "../../teams";

export async function GET(request: NextRequest, { params: { year } }: { params: { year: string }}) {
    const team = request.nextUrl.searchParams.get('team');
    const div = request.nextUrl.searchParams.get('div');
    const teamsPromise: Promise<TeamMap> = div ? getTeams({year, div}) : Promise.resolve({});
    const ratingsPromise = getPlayerRatings({ year });
    const [teams, ratings] = await Promise.all([teamsPromise, ratingsPromise]);
    const players = Object.values(ratings)
        .filter(player => !div || teams[player.team.id]?.div === div)
        .filter(player => !team || player.team.id === team);
    players.sort((a, b) => b.points - a.points);
    return Response.json(Object.fromEntries(players.map((player, i) => [player.id, {...player, rank: i + 1}])));
}

async function getPlayerRatings({ year }: {year: string}): Promise<PlayerRatingMap> {
    const response = await source.get(`${year}/player-ratings.json`);
    const ratings: PlayerRating[] = JSON.parse(response);
    return Object.fromEntries(ratings.map(rating => [rating.id, rating]));
}