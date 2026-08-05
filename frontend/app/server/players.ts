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

        // Use optimized materialized view
        const file = team ? 'team-rosters.parquet' : 'players-list.parquet';
        const parquetPath = `s3://${bucket}/${prefix}/${year}/${file}`;
        let whereClause = '';
        const params: any[] = [parquetPath];

        if (team && div) {
            whereClause = 'WHERE team_id = ? AND div = ?';
            params.push(team, div);
        } else if (team) {
            whereClause = 'WHERE team_id = ?';
            params.push(team);
        } else if (div) {
            whereClause = 'WHERE div = ?';
            params.push(div);
        }

        const sql = `
          SELECT 
            player_id as id, player_name as name,
            div, team_id, team_name, team_schedule_url, team_sport, team_source,
            points, goals, assists, position, number, class_year
          FROM read_parquet(?)
          ${whereClause}
          ORDER BY points DESC
          ${!team && div ? 'LIMIT 200' : ''}
        `;

        try {
            const { rows, debug } = await parquetQuery<any>(sql, team ? 'team_page_roster' : 'players_list', params);
            const players: PlayerRating[] = rows.map(r => ({
                id: r.id,
                name: r.name,
                team: {
                    id: r.team_id,
                    name: r.team_name,
                    div: r.div,
                    schedule: { url: r.team_schedule_url || '' },
                    sport: r.team_sport,
                    source: r.team_source,
                },
                points: Number(r.points),
                goals: Number(r.goals),
                assists: Number(r.assists),
            }));
            const ranked = rankPlayers(players);
            const data = create(ranked) as Data<RankedPlayerMap> & { debug?: QueryDebug };
            data.debug = debug;
            return data;
        } catch (error: any) {
            console.error(`parquet ${team ? 'team_page_roster' : 'players_list'} failed`, error);
            const fallback = await getRankedPlayers({ year, team, div, mode: 'json' }) as Data<RankedPlayerMap> & { debug?: QueryDebug };
            fallback.debug = {
                label: team ? 'team_page_roster' : 'players_list',
                queryMs: 0,
                s3HeadRequests: 0,
                s3GetRequests: 0,
                s3RangeRequests: 0,
                s3PartialBytes: 0,
                note: `Parquet failed (${error?.message || 'unknown error'}); fell back to JSON source.`
            };
            return fallback;
        }
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

export async function getPlayerStats({ year, player, div, mode = 'json' }: { year: string, player: string, div?: string, mode?: DataMode }): Promise<Data<PlayerStats> & { debug?: QueryDebug }> {
    if (mode === 'parquet') {
        const bucket = process.env.DATA_BUCKET;
        const prefix = process.env.DATA_BUCKET_PREFIX || 'data';
        if (!bucket || !div) {
            return await source.get(`${year}/players/${player}.json`);
        }

        // Query both player metadata and game log from materialized views
        const metaSql = `
          SELECT 
            player_id as id, player_name as name,
            div as team_div,
            team_id, team_name, team_schedule_url, team_sport, team_source,
            points, goals, assists,
            position, number, class_year, eligibility, height, weight,
            high_school, hometown, external_link
          FROM read_parquet(?)
          WHERE div = ? AND player_id = ?
          LIMIT 1
        `;

        const statsSql = `
          SELECT 
            date, game_id,
            opponent_id, opponent_name, opponent_div,
            opponent_schedule_url, opponent_sport, opponent_source,
            g, a, gb
          FROM read_parquet(?)
          WHERE div = ? AND player_id = ?
          ORDER BY date DESC
        `;

        try {
            const [metaResult, statsResult] = await Promise.all([
                parquetQuery<any>(
                    metaSql,
                    'player_page_metadata',
                    [`s3://${bucket}/${prefix}/${year}/player-metadata.parquet`, div, player]
                ),
                parquetQuery<any>(
                    statsSql,
                    'player_page_gamelog',
                    [`s3://${bucket}/${prefix}/${year}/player-gamelogs.parquet`, div, player]
                )
            ]);

            if (!metaResult.rows.length) {
                throw new NotFoundError('player not found');
            }

            const meta = metaResult.rows[0];
            const stats: PlayerStats = {
                id: meta.id,
                name: meta.name,
                team: {
                    id: meta.team_id,
                    name: meta.team_name,
                    div: meta.team_div,
                    schedule: { url: meta.team_schedule_url || '' },
                    sport: meta.team_sport,
                    source: meta.team_source,
                },
                external_link: meta.external_link,
                stats: statsResult.rows.map(s => ({
                    game_id: s.game_id,
                    date: s.date,
                    opponent: {
                        id: s.opponent_id,
                        name: s.opponent_name,
                        div: s.opponent_div,
                        schedule: { url: s.opponent_schedule_url || '' },
                        sport: s.opponent_sport,
                        source: s.opponent_source,
                    },
                    g: Number(s.g),
                    a: Number(s.a),
                    gb: Number(s.gb),
                })),
                position: meta.position,
                number: meta.number,
                class_year: meta.class_year,
                eligibility: meta.eligibility,
                height: meta.height,
                weight: meta.weight,
                high_school: meta.high_school,
                hometown: meta.hometown,
            };

            const data = create(stats) as Data<PlayerStats> & { debug?: QueryDebug };
            data.debug = {
                label: 'player_page_combined',
                queryMs: metaResult.debug.queryMs + statsResult.debug.queryMs,
                s3HeadRequests: metaResult.debug.s3HeadRequests + statsResult.debug.s3HeadRequests,
                s3GetRequests: metaResult.debug.s3GetRequests + statsResult.debug.s3GetRequests,
                s3RangeRequests: metaResult.debug.s3RangeRequests + statsResult.debug.s3RangeRequests,
                s3PartialBytes: metaResult.debug.s3PartialBytes + statsResult.debug.s3PartialBytes,
            };
            return data;
        } catch (error: any) {
            console.error('parquet player_page failed', error);
            const fallback = await source.get(`${year}/players/${player}.json`) as Data<PlayerStats> & { debug?: QueryDebug };
            fallback.debug = {
                label: 'player_page_combined',
                queryMs: 0,
                s3HeadRequests: 0,
                s3GetRequests: 0,
                s3RangeRequests: 0,
                s3PartialBytes: 0,
                note: `Parquet failed (${error?.message || 'unknown error'}); fell back to JSON source.`
            };
            return fallback;
        }
    }

    return await source.get(`${year}/players/${player}.json`);
}
