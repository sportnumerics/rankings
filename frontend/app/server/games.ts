import 'server-only';
import source, { NotFoundError } from "./source";
import { Game } from "./types";
import Data, { create } from './Data';
import { DataMode, parquetQuery, QueryDebug } from './parquet';

export interface GameScore {
    // camelCase (frontend-normalized)
    homeScore?: number;
    awayScore?: number;
    // snake_case (raw backend JSON)
    home_score?: number;
    away_score?: number;
    // team schedule style
    points_for?: number;
    points_against?: number;
}

export interface ScheduledGame {
    date: string;
    homeTeam: string;
    homeTeamId: string;
    awayTeam: string;
    awayTeamId: string;
    homeDiv?: string;
    sport?: string;
    source?: string;
    result?: GameScore;
    prediction?: GameScore;
}

export type GamesByDate = Record<string, ScheduledGame[]>;

export async function getGame({ year, game, div, mode = 'json' }: { year: string, game: string, div?: string, mode?: DataMode }): Promise<Data<Game> & { debug?: QueryDebug }> {
    if (mode !== 'parquet' || !div) {
        return await source.get(`${year}/games/${game}.json`);
    }

    const bucket = process.env.DATA_BUCKET;
    const prefix = process.env.DATA_BUCKET_PREFIX || 'data';
    if (!bucket) {
        return await source.get(`${year}/games/${game}.json`);
    }

    // Query game metadata and box scores
    const metaSql = `
        SELECT 
            game_id, date, external_link,
            home_team_id, home_team_name, home_team_div, 
            home_team_schedule_url, home_team_sport, home_team_source,
            away_team_id, away_team_name, away_team_div,
            away_team_schedule_url, away_team_sport, away_team_source,
            home_score, away_score
        FROM read_parquet('s3://${bucket}/${prefix}/${year}/game-metadata.parquet')
        WHERE div = '${div}' AND game_id = '${game}'
        LIMIT 1
    `;

    const statsSql = `
        SELECT 
            team_id, player_id, player_name, number, position,
            g, a, gb, face_offs_won, face_offs_lost
        FROM read_parquet('s3://${bucket}/${prefix}/${year}/game-boxscores.parquet')
        WHERE game_id = '${game}'
        ORDER BY team_id ASC, points_desc ASC
    `;

    try {
        const [metaResult, statsResult] = await Promise.all([
            parquetQuery<any>(metaSql, 'game_page_metadata'),
            parquetQuery<any>(statsSql, 'game_page_boxscore')
        ]);

        if (!metaResult.rows.length) {
            throw new NotFoundError('game not found');
        }

        const meta = metaResult.rows[0];
        const homeStats = statsResult.rows.filter(s => s.team_id === meta.home_team_id);
        const awayStats = statsResult.rows.filter(s => s.team_id === meta.away_team_id);

        const gameData: Game = {
            id: meta.game_id,
            external_link: meta.external_link,
            date: meta.date,
            home_team: {
                id: meta.home_team_id,
                name: meta.home_team_name,
                div: meta.home_team_div,
                schedule: { url: meta.home_team_schedule_url || '' },
                sport: meta.home_team_sport,
                source: meta.home_team_source,
            },
            away_team: {
                id: meta.away_team_id,
                name: meta.away_team_name,
                div: meta.away_team_div,
                schedule: { url: meta.away_team_schedule_url || '' },
                sport: meta.away_team_sport,
                source: meta.away_team_source,
            },
            result: {
                home_score: Number(meta.home_score),
                away_score: Number(meta.away_score),
            },
            home_stats: homeStats.map(s => ({
                player: { id: s.player_id, name: s.player_name, external_link: '' },
                number: s.number,
                position: s.position,
                g: Number(s.g),
                a: Number(s.a),
                gb: Number(s.gb),
                face_offs: {
                    won: Number(s.face_offs_won || 0),
                    lost: Number(s.face_offs_lost || 0),
                },
            })),
            away_stats: awayStats.map(s => ({
                player: { id: s.player_id, name: s.player_name, external_link: '' },
                number: s.number,
                position: s.position,
                g: Number(s.g),
                a: Number(s.a),
                gb: Number(s.gb),
                face_offs: {
                    won: Number(s.face_offs_won || 0),
                    lost: Number(s.face_offs_lost || 0),
                },
            })),
        };

        const data = create(gameData) as Data<Game> & { debug?: QueryDebug };
        data.debug = {
            label: 'game_page_combined',
            queryMs: metaResult.debug.queryMs + statsResult.debug.queryMs,
            s3HeadRequests: metaResult.debug.s3HeadRequests + statsResult.debug.s3HeadRequests,
            s3GetRequests: metaResult.debug.s3GetRequests + statsResult.debug.s3GetRequests,
            s3RangeRequests: metaResult.debug.s3RangeRequests + statsResult.debug.s3RangeRequests,
            s3PartialBytes: metaResult.debug.s3PartialBytes + statsResult.debug.s3PartialBytes,
        };
        return data;
    } catch (error: any) {
        console.error('parquet game_page failed', error);
        const fallback = await source.get(`${year}/games/${game}.json`) as Data<Game> & { debug?: QueryDebug };
        fallback.debug = {
            label: 'game_page_combined',
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

export async function getGames({ year, div, mode = 'json' }: { year: string, div?: string, mode?: DataMode }): Promise<Data<GamesByDate> & { debug?: QueryDebug }> {
    if (mode !== 'parquet' || !div) {
        return await source.get(`${year}/games.json`);
    }

    const bucket = process.env.DATA_BUCKET;
    const prefix = process.env.DATA_BUCKET_PREFIX || 'data';
    if (!bucket) {
        return await source.get(`${year}/games.json`);
    }

    const sql = `
        SELECT 
            game_id, date,
            home_team_id, home_team_name, home_team_div, home_team_sport,
            away_team_id, away_team_name, away_team_div, away_team_sport,
            home_score, away_score
        FROM read_parquet('s3://${bucket}/${prefix}/${year}/games-list.parquet')
        WHERE div = '${div}'
        ORDER BY date DESC
        LIMIT 100
    `;

    try {
        const { rows, debug } = await parquetQuery<any>(sql, 'games_list');
        
        // Deduplicate games (each appears twice for cross-division games)
        const uniqueGames = new Map<string, any>();
        for (const row of rows) {
            if (!uniqueGames.has(row.game_id)) {
                uniqueGames.set(row.game_id, row);
            }
        }

        // Group by date
        const gamesByDate: GamesByDate = {};
        for (const row of Array.from(uniqueGames.values())) {
            const date = row.date.split('T')[0]; // Extract date portion
            if (!gamesByDate[date]) {
                gamesByDate[date] = [];
            }
            gamesByDate[date].push({
                date: row.date,
                homeTeam: row.home_team_name,
                homeTeamId: row.home_team_id,
                awayTeam: row.away_team_name,
                awayTeamId: row.away_team_id,
                homeDiv: row.home_team_div,
                sport: row.home_team_sport,
                result: row.home_score !== null ? {
                    home_score: Number(row.home_score),
                    away_score: Number(row.away_score),
                } : undefined,
            });
        }

        const data = create(gamesByDate) as Data<GamesByDate> & { debug?: QueryDebug };
        data.debug = debug;
        return data;
    } catch (error: any) {
        console.error('parquet games_list failed', error);
        const fallback = await source.get(`${year}/games.json`) as Data<GamesByDate> & { debug?: QueryDebug };
        fallback.debug = {
            label: 'games_list',
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
