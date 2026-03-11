import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock modules before imports
vi.mock('../parquet', () => ({
  parquetQuery: vi.fn(),
}));

vi.mock('../source', () => ({
  default: {
    get: vi.fn(),
  },
  NotFoundError: class NotFoundError extends Error {},
}));

vi.mock('server-only', () => ({}));

vi.mock('../Data', () => ({
  default: {},
  create: vi.fn((body) => ({
    body,
    map: (fn: any) => vi.mocked(create)(fn(body)),
  })),
}));

vi.mock('../rank', () => ({
  default: vi.fn((items) => {
    const sorted = [...items].sort((a: any, b: any) => b.overall - a.overall);
    return Object.fromEntries(sorted.map((item: any, i: number) => [item.id, { ...item, rank: i + 1 }]));
  }),
}));

vi.mock('../divs', () => ({
  DIVS: [
    { id: 'd1', source: 'ncaa', name: 'D1' },
    { id: 'd2', source: 'ncaa', name: 'D2' },
    { id: 'd3', source: 'ncaa', name: 'D3' },
  ],
}));

import { getRankedTeams } from '../teams';
import { parquetQuery } from '../parquet';
import source from '../source';
import { create } from '../Data';

describe('getRankedTeams', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    delete process.env.DATA_BUCKET;
    delete process.env.DATA_BUCKET_PREFIX;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('parquet mode', () => {
    beforeEach(() => {
      process.env.DATA_BUCKET = 'test-bucket';
      process.env.DATA_BUCKET_PREFIX = 'data';
    });

    it('constructs correct SQL query with div filtering and sorting', async () => {
      vi.mocked(parquetQuery).mockResolvedValue({
        rows: [
          {
            id: 'ml-team1',
            name: 'Team 1',
            div: 'd1',
            sport: 'ml',
            source: 'ncaa',
            schedule_url: 'http://example.com',
            offense: 100,
            defense: 90,
            overall: 95,
            rank: 1,
          },
        ],
        debug: {
          label: 'teams_list',
          queryMs: 100,
          s3HeadRequests: 1,
          s3GetRequests: 1,
          s3RangeRequests: 0,
          s3PartialBytes: 1024,
        },
      });

      await getRankedTeams({ year: '2026', div: 'd1', mode: 'parquet' });

      expect(parquetQuery).toHaveBeenCalledWith(
        expect.stringContaining("WHERE div = 'd1'"),
        'teams_list'
      );
      expect(parquetQuery).toHaveBeenCalledWith(
        expect.stringContaining('ORDER BY rank ASC'),
        'teams_list'
      );
      expect(parquetQuery).toHaveBeenCalledWith(
        expect.stringContaining('FROM read_parquet(\'s3://test-bucket/data/2026/teams-list.parquet\')'),
        'teams_list'
      );
    });

    it('selects correct columns for teams list', async () => {
      vi.mocked(parquetQuery).mockResolvedValue({
        rows: [],
        debug: {
          label: 'teams_list',
          queryMs: 100,
          s3HeadRequests: 0,
          s3GetRequests: 0,
          s3RangeRequests: 0,
          s3PartialBytes: 0,
        },
      });

      await getRankedTeams({ year: '2026', div: 'd1', mode: 'parquet' });

      const call = vi.mocked(parquetQuery).mock.calls[0][0];
      expect(call).toContain('id,');
      expect(call).toContain('name,');
      expect(call).toContain('div,');
      expect(call).toContain('sport,');
      expect(call).toContain('source,');
      expect(call).toContain('schedule_url,');
      expect(call).toContain('offense,');
      expect(call).toContain('defense,');
      expect(call).toContain('overall,');
      expect(call).toContain('rank');
    });

    it('returns debug metadata with query stats', async () => {
      const mockDebug = {
        label: 'teams_list',
        queryMs: 250,
        s3HeadRequests: 2,
        s3GetRequests: 3,
        s3RangeRequests: 1,
        s3PartialBytes: 4096,
      };
      vi.mocked(parquetQuery).mockResolvedValue({
        rows: [
          {
            id: 'ml-team1',
            name: 'Team 1',
            div: 'd1',
            sport: 'ml',
            source: 'ncaa',
            schedule_url: 'http://example.com',
            offense: 100,
            defense: 90,
            overall: 95,
            rank: 1,
          },
        ],
        debug: mockDebug,
      });

      const result = await getRankedTeams({ year: '2026', div: 'd1', mode: 'parquet' });

      expect(result.debug).toEqual(mockDebug);
    });

    it('falls back to JSON on parquet error and includes error note', async () => {
      vi.mocked(parquetQuery).mockRejectedValue(new Error('Connection failed'));
      
      // Mock getTeams result - source.get returns Data<Team[]>
      const teamsList = [{ id: 'ml-team1', name: 'Team 1', div: 'd1', sport: 'ml', source: 'ncaa', schedule: { url: '' } }];
      const teamsData = {
        body: teamsList,
        map: (fn: any) => ({ body: fn(teamsList) }),
      };
      
      // Mock getTeamRatings result
      const ratingsList = [{ team: 'ml-team1', offense: 100, defense: 90, overall: 95 }];
      const ratingsData = {
        body: ratingsList,
        map: (fn: any) => ({ body: fn(ratingsList) }),
      };
      
      vi.mocked(source.get)
        .mockResolvedValueOnce(teamsData as any)
        .mockResolvedValueOnce(ratingsData as any);

      const result = await getRankedTeams({ year: '2026', div: 'd1', mode: 'parquet' });

      expect(source.get).toHaveBeenCalled();
      expect(result.debug).toBeDefined();
      expect(result.debug?.note).toContain('Parquet failed');
      expect(result.debug?.note).toContain('Connection failed');
      expect(result.debug?.queryMs).toBe(0);
    });

    it('falls back to JSON when DATA_BUCKET is not set', async () => {
      delete process.env.DATA_BUCKET;
      
      // Mock getTeams result - source.get returns Data<Team[]>
      const teamsList = [{ id: 'ml-team1', name: 'Team 1', div: 'd1', sport: 'ml', source: 'ncaa', schedule: { url: '' } }];
      const teamsData = {
        body: teamsList,
        map: (fn: any) => ({ body: fn(teamsList) }),
      };
      
      // Mock getTeamRatings result
      const ratingsList = [{ team: 'ml-team1', offense: 100, defense: 90, overall: 95 }];
      const ratingsData = {
        body: ratingsList,
        map: (fn: any) => ({ body: fn(ratingsList) }),
      };
      
      vi.mocked(source.get)
        .mockResolvedValueOnce(teamsData as any)
        .mockResolvedValueOnce(ratingsData as any);

      await getRankedTeams({ year: '2026', div: 'd1', mode: 'parquet' });

      expect(source.get).toHaveBeenCalled();
      expect(parquetQuery).not.toHaveBeenCalled();
    });
  });

  describe('json mode', () => {
    it('uses JSON source when mode is not parquet', async () => {
      // Mock getTeams result - source.get returns Data<Team[]>
      const teamsList = [{ id: 'ml-team1', name: 'Team 1', div: 'd1', sport: 'ml', source: 'ncaa', schedule: { url: '' } }];
      const teamsData = {
        body: teamsList,
        map: (fn: any) => ({ body: fn(teamsList) }),
      };
      
      // Mock getTeamRatings result
      const ratingsList = [{ team: 'ml-team1', offense: 100, defense: 90, overall: 95 }];
      const ratingsData = {
        body: ratingsList,
        map: (fn: any) => ({ body: fn(ratingsList) }),
      };
      
      vi.mocked(source.get)
        .mockResolvedValueOnce(teamsData as any)
        .mockResolvedValueOnce(ratingsData as any);

      await getRankedTeams({ year: '2026', div: 'd1', mode: 'json' });

      expect(source.get).toHaveBeenCalled();
      expect(parquetQuery).not.toHaveBeenCalled();
    });
  });
});
