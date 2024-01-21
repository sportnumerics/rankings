import { DIVS } from "./divs";
import source, { NotFoundError } from "./source";
import { RatingMap, Team, TeamMap, TeamRating } from "./types";

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