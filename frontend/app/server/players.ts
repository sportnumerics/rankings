import 'server-only';
import source, { NotFoundError } from "./source";
import { getTeams } from "./teams";
import { PlayerRating, PlayerRatingMap, PlayerStats, RankedPlayerMap, TeamMap } from "./types";
import rank from './rank';
import Data, { create } from './Data';
import { DataMode, parquetQuery, QueryDebug } from './parquet';

export async function getRankedPlayers({ year, team, div, mode = 'json' }: { year: string, team?: string | null, div?: string | null, mode?: DataMode }): Promise<Data<RankedPlayerMap> & { debug?: QueryDebug }> {
    if (mode === 'parquet') {
        const bucket = process.env.DATA_BUCKET;
        const prefix = process.env.DATA_BUCKET_PREFIX || 'data';
        if (!bucket) {
            return getRankedPlayers({ year, team, div, mode: 'json' });
        }

        const where = [
            team ? `pr.team.id = '${team}'` : null,
            div ? `t.div = '${div}'` : null,
        ].filter(Boolean).join(' AND ');

        const sql = `
          SELECT pr.id, pr.name, pr.team, pr.points, pr.goals, pr.assists
          FROM read_parquet('s3://${bucket}/${prefix}/${year}/v2/player_ratings/data.parquet') pr
          LEFT JOIN read_parquet('s3://${bucket}/${prefix}/${year}/v2/teams/*.parquet') t ON pr.team.id = t.id
          ${where ? `WHERE ${where}` : ''}
          ORDER BY pr.points DESC
        `;

        const { rows, debug } = await parquetQuery<any>(sql, 'player_page_rankings');
        const ranked = rankPlayers(rows as PlayerRating[]);
        const data = create(ranked) as Data<RankedPlayerMap> & { debug?: QueryDebug };
        data.debug = debug;
        return data;
    }

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

export async function getPlayerStats({ year, player, mode = 'json' }: { year: string, player: string, mode?: DataMode }): Promise<Data<PlayerStats> & { debug?: QueryDebug }> {
    if (mode === 'parquet') {
        const bucket = process.env.DATA_BUCKET;
        const prefix = process.env.DATA_BUCKET_PREFIX || 'data';
        if (!bucket) {
            return await source.get(`${year}/players/${player}.json`);
        }

        const sql = `
          SELECT *
          FROM read_parquet('s3://${bucket}/${prefix}/${year}/v2/players/data.parquet')
          WHERE id = '${player}'
          LIMIT 1
        `;

        const { rows, debug } = await parquetQuery<any>(sql, 'player_page_profile');
        if (!rows.length) {
            throw new NotFoundError('player not found');
        }
        const data = create(rows[0] as PlayerStats) as Data<PlayerStats> & { debug?: QueryDebug };
        data.debug = debug;
        return data;
    }

    return await source.get(`${year}/players/${player}.json`);
}
