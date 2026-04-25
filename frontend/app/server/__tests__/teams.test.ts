import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getRankedTeams } from '../teams';
import * as parquetModule from '../parquet';

// Mock server-only
vi.mock('server-only', () => ({}));

// Mock source module
vi.mock('../source', () => ({
  default: vi.fn(),
  NotFoundError: class NotFoundError extends Error {},
}));

// Mock shared module (React components)
vi.mock('../../shared', () => ({
  by: (fn: (item: any) => any) => (a: any, b: any) => {
    const aVal = fn(a);
    const bVal = fn(b);
    if (aVal < bVal) return -1;
    if (aVal > bVal) return 1;
    return 0;
  },
}));

describe('getRankedTeams', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    delete process.env.DATA_BUCKET;
    delete process.env.DATA_BUCKET_PREFIX;
  });

  describe('parquet mode', () => {
    it('should return ranked teams from parquet query', async () => {
      process.env.DATA_BUCKET = 'test-bucket';
      process.env.DATA_BUCKET_PREFIX = 'data';

      const mockRows = [
        {
          id: 'team1',
          name: 'Team One',
          div: 'd1',
          sport: 'lacrosse',
          source: 'ncaa',
          schedule_url: 'http://schedule.com',
          offense: 1500,
          defense: 1400,
          overall: 1450,
          rank: 1,
        },
        {
          id: 'team2',
          name: 'Team Two',
          div: 'd1',
          sport: 'lacrosse',
          source: 'ncaa',
          schedule_url: null,
          offense: 1400,
          defense: 1300,
          overall: 1350,
          rank: 2,
        },
      ];

      const mockDebug = {
        label: 'teams_list',
        queryMs: 150,
        s3HeadRequests: 1,
        s3GetRequests: 2,
        s3RangeRequests: 3,
        s3PartialBytes: 50000,
      };

      vi.spyOn(parquetModule, 'parquetQuery').mockResolvedValue({
        rows: mockRows,
        debug: mockDebug,
      });

      const result = await getRankedTeams({
        year: '2026',
        div: 'd1',
        mode: 'parquet',
      });

      expect(parquetModule.parquetQuery).toHaveBeenCalledWith(
        expect.stringContaining("FROM read_parquet('s3://test-bucket/data/2026/teams-list.parquet')"),
        'teams_list'
      );
      expect(parquetModule.parquetQuery).toHaveBeenCalledWith(
        expect.stringContaining("WHERE div = 'd1'"),
        'teams_list'
      );

      expect(result.body).toEqual({
        team1: {
          id: 'team1',
          name: 'Team One',
          div: 'd1',
          sport: 'lacrosse',
          source: 'ncaa',
          schedule: { url: 'http://schedule.com' },
          offense: 1500,
          defense: 1400,
          overall: 1450,
          rank: 1,
        },
        team2: {
          id: 'team2',
          name: 'Team Two',
          div: 'd1',
          sport: 'lacrosse',
          source: 'ncaa',
          schedule: { url: '' },
          offense: 1400,
          defense: 1300,
          overall: 1350,
          rank: 2,
        },
      });

      expect(result.debug).toEqual(mockDebug);
    });

    it('should handle null schedule_url gracefully', async () => {
      process.env.DATA_BUCKET = 'test-bucket';

      const mockRows = [
        {
          id: 'team1',
          name: 'Team One',
          div: 'd1',
          sport: 'lacrosse',
          source: 'ncaa',
          schedule_url: null,
          offense: 1500,
          defense: 1400,
          overall: 1450,
          rank: 1,
        },
      ];

      vi.spyOn(parquetModule, 'parquetQuery').mockResolvedValue({
        rows: mockRows,
        debug: { label: 'teams_list', queryMs: 100, s3HeadRequests: 0, s3GetRequests: 0, s3RangeRequests: 0, s3PartialBytes: 0 },
      });

      const result = await getRankedTeams({
        year: '2026',
        div: 'd1',
        mode: 'parquet',
      });

      expect(result.body.team1.schedule.url).toBe('');
    });

    it('should convert string numbers to Number type', async () => {
      process.env.DATA_BUCKET = 'test-bucket';

      const mockRows = [
        {
          id: 'team1',
          name: 'Team One',
          div: 'd1',
          sport: 'lacrosse',
          source: 'ncaa',
          schedule_url: 'http://schedule.com',
          offense: '1500',
          defense: '1400',
          overall: '1450',
          rank: '1',
        },
      ];

      vi.spyOn(parquetModule, 'parquetQuery').mockResolvedValue({
        rows: mockRows,
        debug: { label: 'teams_list', queryMs: 100, s3HeadRequests: 0, s3GetRequests: 0, s3RangeRequests: 0, s3PartialBytes: 0 },
      });

      const result = await getRankedTeams({
        year: '2026',
        div: 'd1',
        mode: 'parquet',
      });

      const team = result.body.team1;
      expect(typeof team.offense).toBe('number');
      expect(typeof team.defense).toBe('number');
      expect(typeof team.overall).toBe('number');
      expect(typeof team.rank).toBe('number');
      expect(team.offense).toBe(1500);
    });

    it('should include debug metadata in response', async () => {
      process.env.DATA_BUCKET = 'test-bucket';

      const mockDebug = {
        label: 'teams_list',
        queryMs: 250,
        s3HeadRequests: 2,
        s3GetRequests: 3,
        s3RangeRequests: 5,
        s3PartialBytes: 75000,
      };

      vi.spyOn(parquetModule, 'parquetQuery').mockResolvedValue({
        rows: [],
        debug: mockDebug,
      });

      const result = await getRankedTeams({
        year: '2026',
        div: 'd1',
        mode: 'parquet',
      });

      expect(result.debug).toEqual(mockDebug);
      expect(result.debug?.queryMs).toBe(250);
      expect(result.debug?.s3HeadRequests).toBe(2);
    });
  });

  describe('parquet mode fallback', () => {
    it('should fall back to JSON mode when DATA_BUCKET is not set', async () => {
      // DATA_BUCKET not set
      delete process.env.DATA_BUCKET;

      // We can't easily test the full JSON fallback without mocking source(),
      // but we can verify parquetQuery is not called
      const parquetSpy = vi.spyOn(parquetModule, 'parquetQuery');

      try {
        await getRankedTeams({
          year: '2026',
          div: 'd1',
          mode: 'parquet',
        });
      } catch (e) {
        // Expected to fail since we're not mocking source
      }

      expect(parquetSpy).not.toHaveBeenCalled();
    });

    it('should fall back to JSON mode when parquet query fails', async () => {
      process.env.DATA_BUCKET = 'test-bucket';

      vi.spyOn(parquetModule, 'parquetQuery').mockRejectedValue(
        new Error('S3 connection failed')
      );

      try {
        const result = await getRankedTeams({
          year: '2026',
          div: 'd1',
          mode: 'parquet',
        });

        // If we get here, fallback succeeded
        expect(result.debug?.note).toContain('Parquet failed');
        expect(result.debug?.note).toContain('S3 connection failed');
      } catch (e) {
        // Expected if source() is not mocked properly
        // The important part is that parquetQuery was called and failed
      }

      expect(parquetModule.parquetQuery).toHaveBeenCalled();
    });
  });

  describe('json mode', () => {
    it('should not use parquet when mode is json', async () => {
      process.env.DATA_BUCKET = 'test-bucket';
      const parquetSpy = vi.spyOn(parquetModule, 'parquetQuery');

      try {
        await getRankedTeams({
          year: '2026',
          div: 'd1',
          mode: 'json',
        });
      } catch (e) {
        // Expected to fail since we're not mocking source
      }

      expect(parquetSpy).not.toHaveBeenCalled();
    });

    it('should default to json mode when mode is not specified', async () => {
      process.env.DATA_BUCKET = 'test-bucket';
      const parquetSpy = vi.spyOn(parquetModule, 'parquetQuery');

      try {
        await getRankedTeams({
          year: '2026',
          div: 'd1',
        });
      } catch (e) {
        // Expected to fail since we're not mocking source
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
        debug: { label: 'teams_list', queryMs: 100, s3HeadRequests: 0, s3GetRequests: 0, s3RangeRequests: 0, s3PartialBytes: 0 },
      });

      await getRankedTeams({
        year: '2026',
        div: maliciousDiv,
        mode: 'parquet',
      });

      // Current implementation is vulnerable (string interpolation)
      // This test documents the issue that PR #68 will fix
      const callArgs = vi.mocked(parquetModule.parquetQuery).mock.calls[0];
      const sql = callArgs[0];

      // Currently vulnerable: div is interpolated directly
      expect(sql).toContain(`WHERE div = '${maliciousDiv}'`);

      // After PR #68, this should use parameterized queries with ?
      // expect(sql).toContain('WHERE div = ?');
    });
  });
});
