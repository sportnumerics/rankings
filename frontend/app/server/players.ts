import 'server-only';
import source from "./source";
import { getTeams } from "./teams";
import { HasId, HasRanking, PlayerRating, PlayerRatingMap, PlayerStats, PlayerSummary, RankedPlayerMap, TeamMap } from "./types";
import rank from './rank';

export async function getRankedPlayers({ year, team, div }: { year: string, team?: string | null, div?: string | null }): Promise<RankedPlayerMap> {
    const teamsPromise: Promise<TeamMap> = div ? getTeams({year, div}) : Promise.resolve({});
    const ratingsPromise = getPlayerRatings({ year });
    const [teams, ratings] = await Promise.all([teamsPromise, ratingsPromise]);
    const players = Object.values(ratings)
        .filter(player => !div || teams[player.team.id]?.div === div)
        .filter(player => !team || player.team.id === team);
    return rankPlayers(players);
}

export function rankPlayers(players: PlayerRating[]) {
    return rank(players, p => p.points);
}

export async function getPlayerRatings({ year }: {year: string}): Promise<PlayerRatingMap> {
    const response = await source.get(`${year}/player-ratings.json`);
    const ratings: PlayerRating[] = JSON.parse(response);
    return Object.fromEntries(ratings.map(rating => [rating.id, rating]));
}

export async function getPlayerStats({ year, player }: { year: string, player: string }): Promise<PlayerStats> {
    const response = await source.get(`${year}/players/${player}.json`);
    return JSON.parse(response);
}