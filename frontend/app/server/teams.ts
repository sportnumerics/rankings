import 'server-only';
import { DIVS } from "./divs";
import source, { NotFoundError } from "./source";
import { RankedTeamMap, RatingMap, Team, TeamMap, TeamRating, TeamSchedule } from "./types";
import rank from './rank';

export async function getRankedTeams({ year, div }: { year: string, div: string }): Promise<RankedTeamMap> {
    const teamsPromise = getTeams({year, div});
    const ratingsPromise = getTeamRatings({ year });
    const [teams, ratings] = await Promise.all([teamsPromise, ratingsPromise]);
    const teamRatings = Object.values(teams)
        .filter(team => team.div === div)
        .map(team => ({...team, ...ratings[team.id]}));
    return rank(teamRatings, t => t.overall ?? -Infinity);
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

export async function getTeam({ year, team }: { year: string, team: string }): Promise<TeamSchedule> {
    const response = await source.get(`${year}/schedules/${team}.json`);
    return JSON.parse(response);
}