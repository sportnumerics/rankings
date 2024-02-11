import 'server-only';
import source from "./source";
import { getTeams } from "./teams";
import { PlayerRating, PlayerRatingMap, PlayerStats, RankedPlayerMap, TeamMap } from "./types";
import rank from './rank';
import Data, { create } from './Data';

export async function getRankedPlayers({ year, team, div }: { year: string, team?: string | null, div?: string | null }): Promise<Data<RankedPlayerMap>> {
    const teamsPromise: Promise<Data<TeamMap>> = div ? getTeams({ year, div }) : Promise.resolve(create({}));
    const ratingsPromise = getPlayerRatings({ year });
    const [teams, ratings] = await Promise.all([teamsPromise, ratingsPromise]);
    const players = ratings.map(r => Object.values(r)
        .filter(player => !div || teams.body[player.team.id]?.div === div)
        .filter(player => !team || player.team.id === team));
    return players.map(p => rankPlayers(p));
}

export function rankPlayers(players: PlayerRating[]) {
    return rank(players, p => p.points);
}

export async function getPlayerRatings({ year }: { year: string }): Promise<Data<PlayerRatingMap>> {
    const ratings: Data<PlayerRating[]> = await source.get(`${year}/player-ratings.json`);
    return ratings.map(r => Object.fromEntries(r.map(rating => [rating.id, rating])));
}

export async function getPlayerStats({ year, player }: { year: string, player: string }): Promise<Data<PlayerStats>> {
    return await source.get(`${year}/players/${player}.json`);
}