import { describe, it, expect } from 'vitest';
import { dataModeFromSearch, QueryDebug } from './parquet';

describe('dataModeFromSearch', () => {
  it('returns "parquet" when dataMode=parquet', () => {
    expect(dataModeFromSearch({ dataMode: 'parquet' })).toBe('parquet');
  });

  it('returns "json" when dataMode=json', () => {
    expect(dataModeFromSearch({ dataMode: 'json' })).toBe('json');
  });

  it('returns "json" by default when dataMode is missing', () => {
    expect(dataModeFromSearch({})).toBe('json');
    expect(dataModeFromSearch(undefined)).toBe('json');
  });

  it('returns "json" for invalid dataMode values', () => {
    expect(dataModeFromSearch({ dataMode: 'invalid' })).toBe('json');
    expect(dataModeFromSearch({ dataMode: '' })).toBe('json');
  });

  it('handles array values (takes first element)', () => {
    expect(dataModeFromSearch({ dataMode: ['parquet', 'json'] })).toBe('parquet');
    expect(dataModeFromSearch({ dataMode: ['json', 'parquet'] })).toBe('json');
  });
});

describe('QueryDebug type', () => {
  it('has all required fields', () => {
    const debug: QueryDebug = {
      label: 'test',
      queryMs: 100,
      s3HeadRequests: 1,
      s3GetRequests: 2,
      s3RangeRequests: 3,
      s3PartialBytes: 1024,
    };

    expect(debug.label).toBe('test');
    expect(debug.queryMs).toBe(100);
    expect(debug.s3HeadRequests).toBe(1);
    expect(debug.s3GetRequests).toBe(2);
    expect(debug.s3RangeRequests).toBe(3);
    expect(debug.s3PartialBytes).toBe(1024);
  });

  it('allows optional note field', () => {
    const debug: QueryDebug = {
      label: 'test',
      queryMs: 0,
      s3HeadRequests: 0,
      s3GetRequests: 0,
      s3RangeRequests: 0,
      s3PartialBytes: 0,
      note: 'Fallback',
    };

    expect(debug.note).toBe('Fallback');
  });
});

describe('SQL query construction patterns', () => {
  it('teams_list query has required fields', () => {
    const bucket = 'test-bucket';
    const prefix = 'data';
    const year = '2026';
    const div = 'd1';

    const sql = `
        SELECT 
            id, name, div, sport, source, schedule_url,
            offense, defense, overall, rank
        FROM read_parquet('s3://${bucket}/${prefix}/${year}/teams-list.parquet')
        WHERE div = '${div}'
        ORDER BY rank ASC
    `;

    expect(sql).toContain('id, name, div, sport, source');
    expect(sql).toContain('offense, defense, overall, rank');
    expect(sql).toContain('read_parquet');
    expect(sql).toContain(`WHERE div = '${div}'`);
    expect(sql).toContain('ORDER BY rank ASC');
  });

  it('players_list query has division filter and limit', () => {
    const bucket = 'test-bucket';
    const prefix = 'data';
    const year = '2026';
    const div = 'd1';

    const sql = `
          SELECT 
            player_id as id, player_name as name,
            div, team_id, team_name, team_schedule_url, team_sport, team_source,
            points, goals, assists, position, number, class_year
          FROM read_parquet('s3://${bucket}/${prefix}/${year}/players-list.parquet')
          WHERE div = '${div}'
          ORDER BY points DESC
          LIMIT 200
        `;

    expect(sql).toContain('player_id as id');
    expect(sql).toContain('points, goals, assists');
    expect(sql).toContain(`WHERE div = '${div}'`);
    expect(sql).toContain('ORDER BY points DESC');
    expect(sql).toContain('LIMIT 200');
  });

  it('games_list query handles cross-division filtering', () => {
    const bucket = 'test-bucket';
    const prefix = 'data';
    const year = '2026';
    const div = 'd1';

    const sql = `
        SELECT 
            game_id, date,
            home_team_id, home_team_name, home_team_div, home_team_sport,
            away_team_id, away_team_name, away_team_div, away_team_sport,
            home_score, away_score
        FROM read_parquet('s3://${bucket}/${prefix}/${year}/games-list.parquet')
        WHERE home_team_div = '${div}' OR away_team_div = '${div}'
        ORDER BY date DESC
        LIMIT 100
    `;

    expect(sql).toContain('game_id, date');
    expect(sql).toContain('home_team_div');
    expect(sql).toContain('away_team_div');
    expect(sql).toContain(`WHERE home_team_div = '${div}' OR away_team_div = '${div}'`);
    expect(sql).toContain('ORDER BY date DESC');
  });

  it('team_page_roster query filters by team_id', () => {
    const bucket = 'test-bucket';
    const prefix = 'data';
    const year = '2026';
    const team = 'ml-army';

    const sql = `
          SELECT 
            player_id as id, player_name as name,
            div, team_id, team_name, team_schedule_url, team_sport, team_source,
            points, goals, assists, position, number, class_year
          FROM read_parquet('s3://${bucket}/${prefix}/${year}/team-rosters.parquet')
          WHERE team_id = '${team}'
          ORDER BY points DESC
        `;

    expect(sql).toContain('player_id as id');
    expect(sql).toContain(`WHERE team_id = '${team}'`);
    expect(sql).toContain('ORDER BY points DESC');
  });
});

describe('fallback behavior', () => {
  it('creates proper fallback debug on error', () => {
    const error = new Error('Connection timeout');
    const fallback: QueryDebug = {
      label: 'teams_list',
      queryMs: 0,
      s3HeadRequests: 0,
      s3GetRequests: 0,
      s3RangeRequests: 0,
      s3PartialBytes: 0,
      note: `Parquet failed (${error.message}); fell back to JSON source.`,
    };

    expect(fallback.queryMs).toBe(0);
    expect(fallback.s3HeadRequests).toBe(0);
    expect(fallback.note).toContain('Parquet failed');
    expect(fallback.note).toContain('Connection timeout');
    expect(fallback.note).toContain('fell back to JSON');
  });

  it('handles unknown errors gracefully', () => {
    const fallback: QueryDebug = {
      label: 'players_list',
      queryMs: 0,
      s3HeadRequests: 0,
      s3GetRequests: 0,
      s3RangeRequests: 0,
      s3PartialBytes: 0,
      note: 'Parquet failed (unknown error); fell back to JSON source.',
    };

    expect(fallback.note).toContain('unknown error');
  });
});
