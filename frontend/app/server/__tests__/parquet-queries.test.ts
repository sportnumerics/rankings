/**
 * Tests for parquet query code paths
 * 
 * Validates:
 * - SQL query construction (div/team/game filtering, column selection, sorting, parameterization)
 * - Row mapping to structured objects
 * - Debug metadata structure
 */

import { parquetQuery } from '../parquet';

// Mock the parquetQuery function
jest.mock('../parquet', () => ({
  ...jest.requireActual('../parquet'),
  parquetQuery: jest.fn(),
}));

const mockParquetQuery = parquetQuery as jest.MockedFunction<typeof parquetQuery>;

describe('Parquet Query Functions', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    jest.clearAllMocks();
    process.env = {
      ...originalEnv,
      DATA_BUCKET: 'test-bucket',
      DATA_BUCKET_PREFIX: 'data',
    };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe('getRankedTeams SQL construction', () => {
    it('constructs parameterized SQL query with div filter', async () => {
      // Need to dynamically import to respect mock
      const { getRankedTeams } = await import('../teams');
      
      mockParquetQuery.mockResolvedValueOnce({
        rows: [],
        debug: {
          label: 'teams_list',
          queryMs: 100,
          s3HeadRequests: 1,
          s3GetRequests: 1,
          s3RangeRequests: 0,
          s3PartialBytes: 0,
        },
      });

      await getRankedTeams({ year: '2026', div: 'd1', mode: 'parquet' });

      const [sql, label, params] = mockParquetQuery.mock.calls[0];
      
      // Verify SQL uses placeholders (not direct interpolation)
      expect(sql).toContain('FROM read_parquet(?)');
      expect(sql).toContain('WHERE div = ?');
      expect(sql).toContain('ORDER BY rank ASC');
      expect(label).toBe('teams_list');
      
      // Verify parameters are passed separately
      expect(params).toEqual([
        's3://test-bucket/data/2026/teams-list.parquet',
        'd1'
      ]);
      
      // SQL should NOT contain direct string interpolation of user input
      expect(sql).not.toMatch(/WHERE div = ['"]d1['"]/);
      expect(sql).not.toMatch(/s3:\/\/test-bucket/);
    });

    it('maps parquet rows to RankedTeamMap structure', async () => {
      const { getRankedTeams } = await import('../teams');
      
      mockParquetQuery.mockResolvedValueOnce({
        rows: [
          {
            id: 'team1',
            name: 'Test Team',
            div: 'd1',
            sport: 'lacrosse',
            source: 'ncaa',
            schedule_url: 'https://example.com/schedule',
            offense: 1.5,
            defense: -0.5,
            overall: 1.0,
            rank: 1,
          },
        ],
        debug: {
          label: 'teams_list',
          queryMs: 100,
          s3HeadRequests: 1,
          s3GetRequests: 1,
          s3RangeRequests: 0,
          s3PartialBytes: 0,
        },
      });

      const result = await getRankedTeams({ year: '2026', div: 'd1', mode: 'parquet' });

      expect(result.body).toEqual({
        team1: {
          id: 'team1',
          name: 'Test Team',
          div: 'd1',
          sport: 'lacrosse',
          source: 'ncaa',
          schedule: { url: 'https://example.com/schedule' },
          offense: 1.5,
          defense: -0.5,
          overall: 1.0,
          rank: 1,
        },
      });
      expect(result.debug).toBeDefined();
      expect(result.debug?.label).toBe('teams_list');
    });

    it('includes correct columns in SQL', async () => {
      const { getRankedTeams } = await import('../teams');
      
      mockParquetQuery.mockResolvedValueOnce({
        rows: [],
        debug: {
          label: 'teams_list',
          queryMs: 100,
          s3HeadRequests: 1,
          s3GetRequests: 1,
          s3RangeRequests: 0,
          s3PartialBytes: 0,
        },
      });

      await getRankedTeams({ year: '2026', div: 'd1', mode: 'parquet' });

      const [sql] = mockParquetQuery.mock.calls[0];
      
      // Verify all required columns are selected
      const requiredColumns = ['id', 'name', 'div', 'sport', 'source', 'schedule_url', 'offense', 'defense', 'overall', 'rank'];
      requiredColumns.forEach(col => {
        expect(sql).toContain(col);
      });
    });
  });

  describe('getRankedPlayers SQL construction', () => {
    it('constructs parameterized SQL for division filter', async () => {
      const { getRankedPlayers } = await import('../players');
      
      mockParquetQuery.mockResolvedValueOnce({
        rows: [],
        debug: {
          label: 'players_list',
          queryMs: 100,
          s3HeadRequests: 1,
          s3GetRequests: 1,
          s3RangeRequests: 0,
          s3PartialBytes: 0,
        },
      });

      await getRankedPlayers({ year: '2026', div: 'd1', mode: 'parquet' });

      const [sql, label, params] = mockParquetQuery.mock.calls[0];
      
      expect(sql).toContain('FROM read_parquet(?)');
      expect(sql).toContain('WHERE div = ?');
      expect(sql).toContain('LIMIT 200');
      expect(label).toBe('players_list');
      expect(params).toEqual([
        's3://test-bucket/data/2026/players-list.parquet',
        'd1'
      ]);
      
      // No direct interpolation
      expect(sql).not.toMatch(/WHERE div = ['"]d1['"]/);
    });

    it('uses team-rosters.parquet for team-specific queries', async () => {
      const { getRankedPlayers } = await import('../players');
      
      mockParquetQuery.mockResolvedValueOnce({
        rows: [],
        debug: {
          label: 'team_page_roster',
          queryMs: 100,
          s3HeadRequests: 1,
          s3GetRequests: 1,
          s3RangeRequests: 0,
          s3PartialBytes: 0,
        },
      });

      await getRankedPlayers({ year: '2026', team: 'team1', mode: 'parquet' });

      const [sql, label, params] = mockParquetQuery.mock.calls[0];
      
      expect(sql).toContain('FROM read_parquet(?)');
      expect(sql).toContain('WHERE team_id = ?');
      expect(sql).not.toContain('LIMIT 200'); // No limit for team rosters
      expect(label).toBe('team_page_roster');
      expect(params).toEqual([
        's3://test-bucket/data/2026/team-rosters.parquet',
        'team1'
      ]);
      
      // No direct interpolation
      expect(sql).not.toMatch(/WHERE team_id = ['"]team1['"]/);
    });

    it('maps parquet rows to PlayerRating structure with team metadata', async () => {
      const { getRankedPlayers } = await import('../players');
      
      mockParquetQuery.mockResolvedValueOnce({
        rows: [
          {
            id: 'player1',
            name: 'John Doe',
            div: 'd1',
            team_id: 'team1',
            team_name: 'Test Team',
            team_schedule_url: 'https://example.com',
            team_sport: 'lacrosse',
            team_source: 'ncaa',
            points: 50,
            goals: 30,
            assists: 20,
          },
        ],
        debug: {
          label: 'players_list',
          queryMs: 100,
          s3HeadRequests: 1,
          s3GetRequests: 1,
          s3RangeRequests: 0,
          s3PartialBytes: 0,
        },
      });

      const result = await getRankedPlayers({ year: '2026', div: 'd1', mode: 'parquet' });

      const firstPlayer = Object.values(result.body)[0];
      expect(firstPlayer).toMatchObject({
        id: 'player1',
        name: 'John Doe',
        points: 50,
        goals: 30,
        assists: 20,
        team: {
          id: 'team1',
          name: 'Test Team',
          div: 'd1',
          schedule: { url: 'https://example.com' },
          sport: 'lacrosse',
          source: 'ncaa',
        },
      });
    });
  });

  describe('getGame SQL construction', () => {
    it('constructs parameterized SQL for metadata and boxscores', async () => {
      const { getGame } = await import('../games');
      
      mockParquetQuery
        .mockResolvedValueOnce({
          rows: [
            {
              game_id: 'game1',
              date: '2026-03-01',
              external_link: 'https://example.com',
              home_team_id: 'team1',
              home_team_name: 'Home Team',
              home_team_div: 'd1',
              home_team_schedule_url: 'https://example.com/home',
              home_team_sport: 'lacrosse',
              home_team_source: 'ncaa',
              away_team_id: 'team2',
              away_team_name: 'Away Team',
              away_team_div: 'd1',
              away_team_schedule_url: 'https://example.com/away',
              away_team_sport: 'lacrosse',
              away_team_source: 'ncaa',
              home_score: 15,
              away_score: 10,
            },
          ],
          debug: {
            label: 'game_page_metadata',
            queryMs: 50,
            s3HeadRequests: 1,
            s3GetRequests: 1,
            s3RangeRequests: 0,
            s3PartialBytes: 0,
          },
        })
        .mockResolvedValueOnce({
          rows: [],
          debug: {
            label: 'game_page_boxscore',
            queryMs: 30,
            s3HeadRequests: 1,
            s3GetRequests: 1,
            s3RangeRequests: 0,
            s3PartialBytes: 0,
          },
        });

      await getGame({ year: '2026', game: 'game1', mode: 'parquet' });

      // Verify metadata query parameterization
      const [metaSql, metaLabel, metaParams] = mockParquetQuery.mock.calls[0];
      expect(metaSql).toContain('FROM read_parquet(?)');
      expect(metaSql).toContain('WHERE game_id = ?');
      expect(metaSql).toContain('LIMIT 1');
      expect(metaLabel).toBe('game_page_metadata');
      expect(metaParams).toEqual([
        's3://test-bucket/data/2026/game-metadata.parquet',
        'game1'
      ]);
      expect(metaSql).not.toMatch(/WHERE game_id = ['"]game1['"]/);

      // Verify boxscore query parameterization
      const [boxSql, boxLabel, boxParams] = mockParquetQuery.mock.calls[1];
      expect(boxSql).toContain('FROM read_parquet(?)');
      expect(boxSql).toContain('WHERE game_id = ?');
      expect(boxSql).toContain('ORDER BY team_id ASC, points_desc ASC');
      expect(boxLabel).toBe('game_page_boxscore');
      expect(boxParams).toEqual([
        's3://test-bucket/data/2026/game-boxscores.parquet',
        'game1'
      ]);
      expect(boxSql).not.toMatch(/WHERE game_id = ['"]game1['"]/);
    });

    it('includes debug metadata in response', async () => {
      const { getGame } = await import('../games');
      
      mockParquetQuery
        .mockResolvedValueOnce({
          rows: [{
            game_id: 'game1',
            date: '2026-03-01',
            external_link: '',
            home_team_id: 'team1',
            home_team_name: 'Home',
            home_team_div: 'd1',
            home_team_schedule_url: '',
            home_team_sport: 'lacrosse',
            home_team_source: 'ncaa',
            away_team_id: 'team2',
            away_team_name: 'Away',
            away_team_div: 'd1',
            away_team_schedule_url: '',
            away_team_sport: 'lacrosse',
            away_team_source: 'ncaa',
            home_score: 15,
            away_score: 10,
          }],
          debug: {
            label: 'game_page_metadata',
            queryMs: 50,
            s3HeadRequests: 1,
            s3GetRequests: 1,
            s3RangeRequests: 2,
            s3PartialBytes: 1024,
          },
        })
        .mockResolvedValueOnce({
          rows: [],
          debug: {
            label: 'game_page_boxscore',
            queryMs: 30,
            s3HeadRequests: 1,
            s3GetRequests: 1,
            s3RangeRequests: 1,
            s3PartialBytes: 512,
          },
        });

      const result = await getGame({ year: '2026', game: 'game1', mode: 'parquet' });

      expect(result.debug).toBeDefined();
      expect(result.debug?.label).toBe('game_page_combined');
      expect(result.debug?.queryMs).toBeGreaterThan(0);
      expect(result.debug?.s3HeadRequests).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Debug metadata structure', () => {
    it('validates QueryDebug shape for successful queries', async () => {
      const { getRankedTeams } = await import('../teams');
      
      const expectedDebug = {
        label: 'teams_list',
        queryMs: 123,
        s3HeadRequests: 2,
        s3GetRequests: 1,
        s3RangeRequests: 3,
        s3PartialBytes: 2048,
      };

      mockParquetQuery.mockResolvedValueOnce({
        rows: [],
        debug: expectedDebug,
      });

      const result = await getRankedTeams({ year: '2026', div: 'd1', mode: 'parquet' });

      expect(result.debug).toMatchObject(expectedDebug);
      expect(typeof result.debug?.queryMs).toBe('number');
      expect(typeof result.debug?.s3HeadRequests).toBe('number');
      expect(typeof result.debug?.s3GetRequests).toBe('number');
      expect(typeof result.debug?.s3RangeRequests).toBe('number');
      expect(typeof result.debug?.s3PartialBytes).toBe('number');
    });
  });
});
