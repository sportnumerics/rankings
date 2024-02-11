import 'server-only';
import { DIVS } from "./divs";
import source, { NotFoundError } from "./source";
import { RankedTeamMap, RatingMap, Team, TeamMap, TeamRating, TeamSchedule } from "./types";
import rank from './rank';
import Data from './Data';

export async function getRankedTeams({ year, div }: { year: string, div: string }): Promise<Data<RankedTeamMap>> {
    const teamsPromise = getTeams({ year, div });
    const ratingsPromise = getTeamRatings({ year });
    const [teams, ratings] = await Promise.all([teamsPromise, ratingsPromise]);
    const teamRatings = ratings.map(r => Object.values(teams.body)
        .filter(team => team.div === div)
        .map(team => ({ ...team, ...r[team.id] })));
    return teamRatings.map(r => rank(r, t => t.overall));
}

export async function getTeams({ year, div }: { year: string, div: string }): Promise<Data<TeamMap>> {
    const division = DIVS.find(division => division.id === div);
    if (!division) {
        throw new NotFoundError('division not found');
    }
    const teams: Data<Team[]> = await source.get(`${year}/${division.source}-teams.json`);
    return teams.map(t => Object.fromEntries(t.map(team => [team.id, team])));
}

export async function getTeamRatings({ year }: { year: string }): Promise<Data<RatingMap>> {
    const ratings: Data<TeamRating[]> = await source.get(`${year}/team-ratings.json`);
    return ratings.map(r => Object.fromEntries(r.map(rating => [rating.team, rating])));
}

export async function getTeam({ year, team }: { year: string, team: string }): Promise<Data<TeamSchedule>> {
    return await source.get(`${year}/schedules/${team}.json`);
}