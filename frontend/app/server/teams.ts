import 'server-only';
import { DIVS } from "./divs";
import source, { NotFoundError } from "./source";
import { RankedTeamMap, RatingMap, Team, TeamMap, TeamRating, TeamSchedule } from "./types";
import rank from './rank';
import Data, { create } from './Data';
import { DataMode, parquetQuery, QueryDebug } from './parquet';

export async function getRankedTeams({ year, div, mode = 'json' }: { year: string, div: string, mode?: DataMode }): Promise<Data<RankedTeamMap> & { debug?: QueryDebug }> {
    if (mode !== 'parquet') {
        const teamsPromise = getTeams({ year, div });
        const ratingsPromise = getTeamRatings({ year });
        const [teams, ratings] = await Promise.all([teamsPromise, ratingsPromise]);
        const teamRatings = ratings.map(r => Object.values(teams.body)
            .filter(team => team.div === div)
            .map(team => ({ ...team, ...r[team.id] })));
        return teamRatings.map(r => rank(r, t => t.overall));
    }

    const bucket = process.env.DATA_BUCKET;
    const prefix = process.env.DATA_BUCKET_PREFIX || 'data';
    if (!bucket) {
        const teamsPromise = getTeams({ year, div });
        const ratingsPromise = getTeamRatings({ year });
        const [teams, ratings] = await Promise.all([teamsPromise, ratingsPromise]);
        const teamRatings = ratings.map(r => Object.values(teams.body)
            .filter(team => team.div === div)
            .map(team => ({ ...team, ...r[team.id] })));
        return teamRatings.map(r => rank(r, t => t.overall));
    }

    const sql = `
        SELECT 
            id, name, div, sport, source, schedule_url,
            offense, defense, overall, rank
        FROM read_parquet(?)
        WHERE div = ?
        ORDER BY rank ASC
    `;

    try {
        const { rows, debug } = await parquetQuery<any>(
            sql,
            'teams_list',
            [`s3://${bucket}/${prefix}/${year}/teams-list.parquet`, div]
        );
        const teamMap: RankedTeamMap = Object.fromEntries(
            rows.map(r => [r.id, {
                id: r.id,
                name: r.name,
                div: r.div,
                sport: r.sport,
                source: r.source,
                schedule: { url: r.schedule_url || '' },
                offense: Number(r.offense),
                defense: Number(r.defense),
                overall: Number(r.overall),
                rank: Number(r.rank),
            }])
        );
        const data = create(teamMap) as Data<RankedTeamMap> & { debug?: QueryDebug };
        data.debug = debug;
        return data;
    } catch (error: any) {
        console.error('parquet teams_list failed', error);
        const teamsPromise = getTeams({ year, div });
        const ratingsPromise = getTeamRatings({ year });
        const [teams, ratings] = await Promise.all([teamsPromise, ratingsPromise]);
        const teamRatings = ratings.map(r => Object.values(teams.body)
            .filter(team => team.div === div)
            .map(team => ({ ...team, ...r[team.id] })));
        const fallback = teamRatings.map(r => rank(r, t => t.overall)) as Data<RankedTeamMap> & { debug?: QueryDebug };
        fallback.debug = {
            label: 'teams_list',
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

export async function getTeam({ year, team, mode = 'json' }: { year: string, team: string, mode?: DataMode }): Promise<Data<TeamSchedule> & { debug?: QueryDebug }> {
    if (mode !== 'parquet') {
        return await source.get(`${year}/schedules/${team}.json`);
    }

    const bucket = process.env.DATA_BUCKET;
    const prefix = process.env.DATA_BUCKET_PREFIX || 'data';
    if (!bucket) {
        return await source.get(`${year}/schedules/${team}.json`);
    }

    const sql = `
      WITH target_team AS (
        SELECT id, name, div, source
        FROM read_parquet(?)
        WHERE id = ?
      )
      SELECT
        g.id,
        g.date,
        g.home_team.id AS home_id,
        g.home_team.name AS home_name,
        g.away_team.id AS away_id,
        g.away_team.name AS away_name,
        g.result.home_score AS home_score,
        g.result.away_score AS away_score,
        t.id AS team_id,
        t.name AS team_name,
        t.div AS team_div,
        t.source AS team_source
      FROM read_parquet(?) g
      JOIN target_team t ON (g.home_team.id = t.id OR g.away_team.id = t.id)
      ORDER BY g.date
    `;

    try {
        const { rows, debug } = await parquetQuery<any>(
            sql,
            'team_page_schedule',
            [
                `s3://${bucket}/${prefix}/${year}/v2/teams/*.parquet`,
                team,
                `s3://${bucket}/${prefix}/${year}/v2/games/*.parquet`,
            ]
        );
        if (!rows.length) {
            throw new NotFoundError('team not found');
        }

        const first = rows[0];
        const sport = String(first.team_id || 'ml').split('-')[0] || 'ml';
        const body: TeamSchedule = {
            team: {
                id: first.team_id,
                name: first.team_name,
                div: first.team_div,
                source: first.team_source,
                sport,
                schedule: { url: '' },
            },
            games: rows.map(r => {
                const home = r.home_id === first.team_id;
                return {
                    id: r.id,
                    date: r.date,
                    sport,
                    source: first.team_source,
                    home,
                    opponent: {
                        id: home ? r.away_id : r.home_id,
                        name: home ? r.away_name : r.home_name,
                        div: first.team_div,
                        schedule: { url: '' },
                        sport,
                        source: first.team_source,
                    },
                    details: { url: '' },
                    result: (r.home_score === null || r.away_score === null)
                        ? undefined
                        : {
                            points_for: home ? r.home_score : r.away_score,
                            points_against: home ? r.away_score : r.home_score,
                        }
                };
            })
        };

        const data = create(body) as Data<TeamSchedule> & { debug?: QueryDebug };
        data.debug = debug;
        return data;
    } catch (error: any) {
        console.error('parquet team_page_schedule failed', error);
        const fallback = await source.get(`${year}/schedules/${team}.json`) as Data<TeamSchedule> & { debug?: QueryDebug };
        fallback.debug = {
            label: 'team_page_schedule',
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
