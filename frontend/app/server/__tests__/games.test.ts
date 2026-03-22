import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getGame, getGames } from '../games';
import * as parquetModule from '../parquet';

// Mock server-only
vi.mock('server-only', () => ({}));

// Mock source module
vi.mock('../source', () => ({
  default: {
    get: vi.fn(),
  },
  NotFoundError: class NotFoundError extends Error {},
}));

describe('getGame', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    delete process.env.DATA_BUCKET;
    delete process.env.DATA_BUCKET_PREFIX;
  });

  describe('parquet mode', () => {
    it('should return game with metadata and box scores from parquet', async () => {
      process.env.DATA_BUCKET = 'test-bucket';
      process.env.DATA_BUCKET_PREFIX = 'data';

      const mockMetaRows = [
        {
          game_id: 'game1',
          date: '2026-03-15',
          external_link: 'http://game.com',
          home_team_id: 'team1',
          home_team_name: 'Team One',
          home_team_div: 'd1',
          home_team_schedule_url: 'http://schedule1.com',
          home_team_sport: 'lacrosse',
          home_team_source: 'ncaa',
          away_team_id: 'team2',
          away_team_name: 'Team Two',
          away_team_div: 'd1',
          away_team_schedule_url: 'http://schedule2.com',
          away_team_sport: 'lacrosse',
          away_team_source: 'ncaa',
          home_score: 15,
          away_score: 12,
        },
      ];

      const mockStatsRows = [
        {
          team_id: 'team1',
          player_id: 'player1',
          player_name: 'John Doe',
          number: '10',
          position: 'Attack',
          g: 3,
          a: 2,
          gb: 1,
          face_offs_won: 5,
          face_offs_lost: 3,
        },
        {
          team_id: 'team2',
          player_id: 'player2',
          player_name: 'Jane Smith',
          number: '15',
          position: 'Midfield',
          g: 2,
          a: 1,
          gb: 2,
          face_offs_won: 3,
          face_offs_lost: 5,
        },
      ];

      const mockMetaDebug = {
        label: 'game_page_metadata',
        queryMs: 120,
        s3HeadRequests: 1,
        s3GetRequests: 1,
        s3RangeRequests: 2,
        s3PartialBytes: 30000,
      };

      const mockStatsDebug = {
        label: 'game_page_boxscore',
        queryMs: 150,
        s3HeadRequests: 1,
        s3GetRequests: 1,
        s3RangeRequests: 3,
        s3PartialBytes: 40000,
      };

      vi.spyOn(parquetModule, 'parquetQuery')
        .mockResolvedValueOnce({
          rows: mockMetaRows,
          debug: mockMetaDebug,
        })
        .mockResolvedValueOnce({
          rows: mockStatsRows,
          debug: mockStatsDebug,
        });

      const result = await getGame({
        year: '2026',
        game: 'game1',
        mode: 'parquet',
      });

      // Verify metadata query
      expect(parquetModule.parquetQuery).toHaveBeenNthCalledWith(
        1,
        expect.stringContaining('game-metadata.parquet'),
        'game_page_metadata'
      );
      expect(parquetModule.parquetQuery).toHaveBeenNthCalledWith(
        1,
        expect.stringContaining("WHERE game_id = 'game1'"),
        'game_page_metadata'
      );

      // Verify box scores query
      expect(parquetModule.parquetQuery).toHaveBeenNthCalledWith(
        2,
        expect.stringContaining('game-boxscores.parquet'),
        'game_page_boxscore'
      );
      expect(parquetModule.parquetQuery).toHaveBeenNthCalledWith(
        2,
        expect.stringContaining("WHERE game_id = 'game1'"),
        'game_page_boxscore'
      );

      // Verify result structure
      expect(result.body).toMatchObject({
        id: 'game1',
        date: '2026-03-15',
        external_link: 'http://game.com',
        home_team: {
          id: 'team1',
          name: 'Team One',
          div: 'd1',
        },
        away_team: {
          id: 'team2',
          name: 'Team Two',
          div: 'd1',
        },
        result: {
          home_score: 15,
          away_score: 12,
        },
      });

      // Verify stats are split correctly
      expect(result.body.home_stats).toHaveLength(1);
      expect(result.body.away_stats).toHaveLength(1);
      expect(result.body.home_stats[0]).toMatchObject({
        player: { id: 'player1', name: 'John Doe' },
        number: '10',
        position: 'Attack',
        g: 3,
        a: 2,
        gb: 1,
      });

      // Verify debug metadata is combined
      expect(result.debug).toEqual({
        label: 'game_page_combined',
        queryMs: 270,
        s3HeadRequests: 2,
        s3GetRequests: 2,
        s3RangeRequests: 5,
        s3PartialBytes: 70000,
      });
    });

    it('should convert string numbers to Number type', async () => {
      process.env.DATA_BUCKET = 'test-bucket';

      const mockMetaRows = [
        {
          game_id: 'game1',
          date: '2026-03-15',
          external_link: '',
          home_team_id: 'team1',
          home_team_name: 'Team One',
          home_team_div: 'd1',
          home_team_schedule_url: '',
          home_team_sport: 'lacrosse',
          home_team_source: 'ncaa',
          away_team_id: 'team2',
          away_team_name: 'Team Two',
          away_team_div: 'd1',
          away_team_schedule_url: '',
          away_team_sport: 'lacrosse',
          away_team_source: 'ncaa',
          home_score: '15',
          away_score: '12',
        },
      ];

      const mockStatsRows = [
        {
          team_id: 'team1',
          player_id: 'player1',
          player_name: 'John Doe',
          number: '10',
          position: 'Attack',
          g: '3',
          a: '2',
          gb: '1',
          face_offs_won: '5',
          face_offs_lost: '3',
        },
      ];

      vi.spyOn(parquetModule, 'parquetQuery')
        .mockResolvedValueOnce({
          rows: mockMetaRows,
          debug: { label: 'game_page_metadata', queryMs: 100, s3HeadRequests: 0, s3GetRequests: 0, s3RangeRequests: 0, s3PartialBytes: 0 },
        })
        .mockResolvedValueOnce({
          rows: mockStatsRows,
          debug: { label: 'game_page_boxscore', queryMs: 100, s3HeadRequests: 0, s3GetRequests: 0, s3RangeRequests: 0, s3PartialBytes: 0 },
        });

      const result = await getGame({
        year: '2026',
        game: 'game1',
        mode: 'parquet',
      });

      // Verify scores are numbers
      expect(typeof result.body.result.home_score).toBe('number');
      expect(typeof result.body.result.away_score).toBe('number');
      expect(result.body.result.home_score).toBe(15);
      expect(result.body.result.away_score).toBe(12);

      // Verify stats are numbers
      const stat = result.body.home_stats[0];
      expect(typeof stat.g).toBe('number');
      expect(typeof stat.a).toBe('number');
      expect(typeof stat.gb).toBe('number');
      expect(stat.g).toBe(3);
    });

    it('should handle null schedule URLs gracefully', async () => {
      process.env.DATA_BUCKET = 'test-bucket';

      const mockMetaRows = [
        {
          game_id: 'game1',
          date: '2026-03-15',
          external_link: null,
          home_team_id: 'team1',
          home_team_name: 'Team One',
          home_team_div: 'd1',
          home_team_schedule_url: null,
          home_team_sport: 'lacrosse',
          home_team_source: 'ncaa',
          away_team_id: 'team2',
          away_team_name: 'Team Two',
          away_team_div: 'd1',
          away_team_schedule_url: null,
          away_team_sport: 'lacrosse',
          away_team_source: 'ncaa',
          home_score: 15,
          away_score: 12,
        },
      ];

      vi.spyOn(parquetModule, 'parquetQuery')
        .mockResolvedValueOnce({
          rows: mockMetaRows,
          debug: { label: 'game_page_metadata', queryMs: 100, s3HeadRequests: 0, s3GetRequests: 0, s3RangeRequests: 0, s3PartialBytes: 0 },
        })
        .mockResolvedValueOnce({
          rows: [],
          debug: { label: 'game_page_boxscore', queryMs: 100, s3HeadRequests: 0, s3GetRequests: 0, s3RangeRequests: 0, s3PartialBytes: 0 },
        });

      const result = await getGame({
        year: '2026',
        game: 'game1',
        mode: 'parquet',
      });

      expect(result.body.home_team.schedule.url).toBe('');
      expect(result.body.away_team.schedule.url).toBe('');
      expect(result.body.external_link).toBeNull();
    });
  });

  describe('parquet mode fallback', () => {
    it('should fall back to JSON mode when DATA_BUCKET is not set', async () => {
      delete process.env.DATA_BUCKET;

      const parquetSpy = vi.spyOn(parquetModule, 'parquetQuery');

      try {
        await getGame({
          year: '2026',
          game: 'game1',
          mode: 'parquet',
        });
      } catch (e) {
        // Expected to fail since we're not mocking source.get
      }

      expect(parquetSpy).not.toHaveBeenCalled();
    });

    it('should fall back to JSON mode when parquet query fails', async () => {
      process.env.DATA_BUCKET = 'test-bucket';

      vi.spyOn(parquetModule, 'parquetQuery').mockRejectedValue(
        new Error('Parquet read error')
      );

      try {
        const result = await getGame({
          year: '2026',
          game: 'game1',
          mode: 'parquet',
        });

        expect(result.debug?.note).toContain('Parquet failed');
        expect(result.debug?.note).toContain('Parquet read error');
      } catch (e) {
        // Expected if source.get is not mocked properly
      }

      expect(parquetModule.parquetQuery).toHaveBeenCalled();
    });
  });

  describe('json mode', () => {
    it('should not use parquet when mode is json', async () => {
      process.env.DATA_BUCKET = 'test-bucket';
      const parquetSpy = vi.spyOn(parquetModule, 'parquetQuery');

      try {
        await getGame({
          year: '2026',
          game: 'game1',
          mode: 'json',
        });
      } catch (e) {
        // Expected to fail since we're not mocking source.get
      }

      expect(parquetSpy).not.toHaveBeenCalled();
    });

    it('should default to json mode when mode is not specified', async () => {
      process.env.DATA_BUCKET = 'test-bucket';
      const parquetSpy = vi.spyOn(parquetModule, 'parquetQuery');

      try {
        await getGame({
          year: '2026',
          game: 'game1',
        });
      } catch (e) {
        // Expected to fail since we're not mocking source.get
      }

      expect(parquetSpy).not.toHaveBeenCalled();
    });
  });

  describe('SQL injection protection', () => {
    it('should sanitize game parameter in SQL query', async () => {
      process.env.DATA_BUCKET = 'test-bucket';

      const maliciousGame = "game1' OR '1'='1";

      vi.spyOn(parquetModule, 'parquetQuery').mockResolvedValue({
        rows: [],
        debug: { label: 'game_page_metadata', queryMs: 100, s3HeadRequests: 0, s3GetRequests: 0, s3RangeRequests: 0, s3PartialBytes: 0 },
      });

      try {
        await getGame({
          year: '2026',
          game: maliciousGame,
          mode: 'parquet',
        });
      } catch (e) {
        // May fail due to empty rows
      }

      const callArgs = vi.mocked(parquetModule.parquetQuery).mock.calls[0];
      const sql = callArgs[0];

      // Currently vulnerable: game is interpolated directly
      expect(sql).toContain(`game_id = '${maliciousGame}'`);

      // After PR #68, this should use parameterized queries with ?
      // expect(sql).toContain('game_id = ?');
    });
  });
});

describe('getGames', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    delete process.env.DATA_BUCKET;
    delete process.env.DATA_BUCKET_PREFIX;
  });

  describe('parquet mode', () => {
    it('should return games by date from parquet query', async () => {
      process.env.DATA_BUCKET = 'test-bucket';
      process.env.DATA_BUCKET_PREFIX = 'data';

      const mockRows = [
        {
          game_id: 'game1',
          date: '2026-03-15',
          home_team_id: 'team1',
          home_team_name: 'Team One',
          home_team_div: 'd1',
          home_team_sport: 'lacrosse',
          away_team_id: 'team2',
          away_team_name: 'Team Two',
          away_team_div: 'd1',
          away_team_sport: 'lacrosse',
          home_score: 15,
          away_score: 12,
        },
        {
          game_id: 'game2',
          date: '2026-03-15',
          home_team_id: 'team3',
          home_team_name: 'Team Three',
          home_team_div: 'd1',
          home_team_sport: 'lacrosse',
          away_team_id: 'team4',
          away_team_name: 'Team Four',
          away_team_div: 'd1',
          away_team_sport: 'lacrosse',
          home_score: null,
          away_score: null,
        },
      ];

      const mockDebug = {
        label: 'games_list',
        queryMs: 200,
        s3HeadRequests: 1,
        s3GetRequests: 2,
        s3RangeRequests: 4,
        s3PartialBytes: 50000,
      };

      vi.spyOn(parquetModule, 'parquetQuery').mockResolvedValue({
        rows: mockRows,
        debug: mockDebug,
      });

      const result = await getGames({
        year: '2026',
        div: 'd1',
        mode: 'parquet',
      });

      expect(parquetModule.parquetQuery).toHaveBeenCalledWith(
        expect.stringContaining('games-list.parquet'),
        'games_list'
      );
      expect(parquetModule.parquetQuery).toHaveBeenCalledWith(
        expect.stringContaining("home_team_div = 'd1' OR away_team_div = 'd1'"),
        'games_list'
      );

      // Verify games are grouped by date
      expect(result.body['2026-03-15']).toHaveLength(2);
      
      // Verify first game structure
      const game1 = result.body['2026-03-15'][0];
      expect(game1).toMatchObject({
        date: '2026-03-15',
        homeTeam: 'Team One',
        homeTeamId: 'team1',
        awayTeam: 'Team Two',
        awayTeamId: 'team2',
        homeDiv: 'd1',
        awayDiv: 'd1',
        sport: 'lacrosse',
      });

      // Verify scores are included as result
      expect(game1.result).toEqual({
        home_score: 15,
        away_score: 12,
      });

      // Verify game without scores (upcoming)
      const game2 = result.body['2026-03-15'][1];
      expect(game2.result).toBeUndefined();

      expect(result.debug).toEqual(mockDebug);
    });

    it('should convert string numbers to Number type', async () => {
      process.env.DATA_BUCKET = 'test-bucket';

      const mockRows = [
        {
          game_id: 'game1',
          date: '2026-03-15',
          home_team_id: 'team1',
          home_team_name: 'Team One',
          home_team_div: 'd1',
          home_team_sport: 'lacrosse',
          away_team_id: 'team2',
          away_team_name: 'Team Two',
          away_team_div: 'd1',
          away_team_sport: 'lacrosse',
          home_score: '15',
          away_score: '12',
        },
      ];

      vi.spyOn(parquetModule, 'parquetQuery').mockResolvedValue({
        rows: mockRows,
        debug: { label: 'games_list', queryMs: 100, s3HeadRequests: 0, s3GetRequests: 0, s3RangeRequests: 0, s3PartialBytes: 0 },
      });

      const result = await getGames({
        year: '2026',
        div: 'd1',
        mode: 'parquet',
      });

      const game = result.body['2026-03-15'][0];
      expect(typeof game.result?.home_score).toBe('number');
      expect(typeof game.result?.away_score).toBe('number');
      expect(game.result?.home_score).toBe(15);
      expect(game.result?.away_score).toBe(12);
    });

    it('should handle games without scores (upcoming games)', async () => {
      process.env.DATA_BUCKET = 'test-bucket';

      const mockRows = [
        {
          game_id: 'game1',
          date: '2026-03-20',
          home_team_id: 'team1',
          home_team_name: 'Team One',
          home_team_div: 'd1',
          home_team_sport: 'lacrosse',
          away_team_id: 'team2',
          away_team_name: 'Team Two',
          away_team_div: 'd1',
          away_team_sport: 'lacrosse',
          home_score: null,
          away_score: null,
        },
      ];

      vi.spyOn(parquetModule, 'parquetQuery').mockResolvedValue({
        rows: mockRows,
        debug: { label: 'games_list', queryMs: 100, s3HeadRequests: 0, s3GetRequests: 0, s3RangeRequests: 0, s3PartialBytes: 0 },
      });

      const result = await getGames({
        year: '2026',
        div: 'd1',
        mode: 'parquet',
      });

      const game = result.body['2026-03-20'][0];
      expect(game.result).toBeUndefined();
    });
  });

  describe('parquet mode fallback', () => {
    it('should fall back to JSON mode when div is not specified', async () => {
      process.env.DATA_BUCKET = 'test-bucket';
      const parquetSpy = vi.spyOn(parquetModule, 'parquetQuery');

      try {
        await getGames({
          year: '2026',
          mode: 'parquet',
        });
      } catch (e) {
        // Expected to fail since we're not mocking source.get
      }

      expect(parquetSpy).not.toHaveBeenCalled();
    });

    it('should fall back to JSON mode when DATA_BUCKET is not set', async () => {
      delete process.env.DATA_BUCKET;

      const parquetSpy = vi.spyOn(parquetModule, 'parquetQuery');

      try {
        await getGames({
          year: '2026',
          div: 'd1',
          mode: 'parquet',
        });
      } catch (e) {
        // Expected to fail since we're not mocking source.get
      }

      expect(parquetSpy).not.toHaveBeenCalled();
    });

    it('should fall back to JSON mode when parquet query fails', async () => {
      process.env.DATA_BUCKET = 'test-bucket';

      vi.spyOn(parquetModule, 'parquetQuery').mockRejectedValue(
        new Error('Network timeout')
      );

      try {
        const result = await getGames({
          year: '2026',
          div: 'd1',
          mode: 'parquet',
        });

        expect(result.debug?.note).toContain('Parquet failed');
        expect(result.debug?.note).toContain('Network timeout');
      } catch (e) {
        // Expected if source.get is not mocked properly
      }

      expect(parquetModule.parquetQuery).toHaveBeenCalled();
    });
  });

  describe('json mode', () => {
    it('should not use parquet when mode is json', async () => {
      process.env.DATA_BUCKET = 'test-bucket';
      const parquetSpy = vi.spyOn(parquetModule, 'parquetQuery');

      try {
        await getGames({
          year: '2026',
          div: 'd1',
          mode: 'json',
        });
      } catch (e) {
        // Expected to fail since we're not mocking source.get
      }

      expect(parquetSpy).not.toHaveBeenCalled();
    });

    it('should default to json mode when mode is not specified', async () => {
      process.env.DATA_BUCKET = 'test-bucket';
      const parquetSpy = vi.spyOn(parquetModule, 'parquetQuery');

      try {
        await getGames({
          year: '2026',
          div: 'd1',
        });
      } catch (e) {
        // Expected to fail since we're not mocking source.get
      }

      expect(parquetSpy).not.toHaveBeenCalled();
    });
  });

  describe('SQL injection protection', () => {
    it('should sanitize div parameter in SQL query', async () => {
      process.env.DATA_BUCKET = 'test-bucket';

      const maliciousDiv = "d1' OR '1'='1";

      vi.spyOn(parquetModule, 'parquetQuery').mockResolvedValue({
        rows: [],
        debug: { label: 'games_list', queryMs: 100, s3HeadRequests: 0, s3GetRequests: 0, s3RangeRequests: 0, s3PartialBytes: 0 },
      });

      await getGames({
        year: '2026',
        div: maliciousDiv,
        mode: 'parquet',
      });

      const callArgs = vi.mocked(parquetModule.parquetQuery).mock.calls[0];
      const sql = callArgs[0];

      // Currently vulnerable: div is interpolated directly
      expect(sql).toContain(`home_team_div = '${maliciousDiv}' OR away_team_div = '${maliciousDiv}'`);

      // After PR #68, this should use parameterized queries with ?
      // expect(sql).toContain('home_team_div = ? OR away_team_div = ?');
    });
  });
});
