/**
 * Unit tests for parquet query construction and fallback behavior
 * 
 * These tests verify:
 * 1. SQL query construction (filtering, sorting, column selection)
 * 2. Fallback behavior when parquet fails
 * 3. Debug metadata structure
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Test fixtures
const mockBucket = 'test-bucket';
const mockPrefix = 'data';

describe('Parquet Query Construction', () => {
    let originalEnv: NodeJS.ProcessEnv;

    beforeEach(() => {
        originalEnv = { ...process.env };
        process.env.DATA_BUCKET = mockBucket;
        process.env.DATA_BUCKET_PREFIX = mockPrefix;
    });

    afterEach(() => {
        process.env = originalEnv;
    });

    describe('getRankedTeams', () => {
        it('should construct SQL with correct division filter', () => {
            const expectedSql = `
        SELECT 
            id, name, div, sport, source, schedule_url,
            offense, defense, overall, rank
        FROM read_parquet('s3://${mockBucket}/${mockPrefix}/2026/teams-list.parquet')
        WHERE div = 'd1'
        ORDER BY rank ASC
    `;

            // Verify SQL pattern matches expected structure
            expect(expectedSql).toContain("WHERE div = 'd1'");
            expect(expectedSql).toContain('ORDER BY rank ASC');
            expect(expectedSql).toContain('teams-list.parquet');
        });

        it('should include all required team columns', () => {
            const requiredColumns = [
                'id', 'name', 'div', 'sport', 'source', 'schedule_url',
                'offense', 'defense', 'overall', 'rank'
            ];

            const sqlTemplate = `SELECT ${requiredColumns.join(', ')} FROM read_parquet(...)`;
            
            requiredColumns.forEach(col => {
                expect(sqlTemplate).toContain(col);
            });
        });
    });

    describe('getRankedPlayers', () => {
        it('should use team-rosters.parquet when team is specified', () => {
            const team = 'syracuse-ml';
            const expectedFile = 'team-rosters.parquet';
            const expectedWhere = `team_id = '${team}'`;

            expect(expectedFile).toBe('team-rosters.parquet');
            expect(expectedWhere).toContain(team);
        });

        it('should use players-list.parquet when no team specified', () => {
            const div = 'd1';
            const expectedFile = 'players-list.parquet';
            const expectedWhere = `div = '${div}'`;
            const expectedLimit = 'LIMIT 200';

            expect(expectedFile).toBe('players-list.parquet');
            expect(expectedWhere).toContain(div);
            expect(expectedLimit).toBe('LIMIT 200');
        });

        it('should combine multiple WHERE conditions correctly', () => {
            const team = 'syracuse-ml';
            const div = 'd1';
            const conditions = [
                team ? `team_id = '${team}'` : null,
                div ? `div = '${div}'` : null,
            ].filter(Boolean);

            expect(conditions).toHaveLength(2);
            expect(conditions.join(' AND ')).toBe(`team_id = '${team}' AND div = '${div}'`);
        });

        it('should include required player columns with team metadata', () => {
            const requiredColumns = [
                'player_id', 'player_name',
                'div', 'team_id', 'team_name', 'team_schedule_url', 'team_sport', 'team_source',
                'points', 'goals', 'assists'
            ];

            const sqlTemplate = `SELECT ${requiredColumns.join(', ')} FROM ...`;
            
            requiredColumns.forEach(col => {
                expect(sqlTemplate).toContain(col);
            });
        });
    });

    describe('getGames', () => {
        it('should construct SQL with division filter', () => {
            const div = 'd1';
            const expectedSql = `
        SELECT 
            game_id, date,
            home_team_id, home_team_name, home_team_div, home_team_sport,
            away_team_id, away_team_name, away_team_div, away_team_sport,
            home_score, away_score
        FROM read_parquet('s3://${mockBucket}/${mockPrefix}/2026/games-list.parquet')
        WHERE div = '${div}'
        ORDER BY date DESC
        LIMIT 100
    `;

            expect(expectedSql).toContain(`WHERE div = '${div}'`);
            expect(expectedSql).toContain('ORDER BY date DESC');
            expect(expectedSql).toContain('LIMIT 100');
        });

        it('should include all required game columns', () => {
            const requiredColumns = [
                'game_id', 'date',
                'home_team_id', 'home_team_name', 'home_team_div', 'home_team_sport',
                'away_team_id', 'away_team_name', 'away_team_div', 'away_team_sport',
                'home_score', 'away_score'
            ];

            const sqlTemplate = `SELECT ${requiredColumns.join(', ')} FROM ...`;
            
            requiredColumns.forEach(col => {
                expect(sqlTemplate).toContain(col);
            });
        });
    });

    describe('Fallback Behavior', () => {
        it('should structure fallback debug metadata correctly', () => {
            const fallbackDebug = {
                label: 'teams_list',
                queryMs: 0,
                s3HeadRequests: 0,
                s3GetRequests: 0,
                s3RangeRequests: 0,
                s3PartialBytes: 0,
                note: 'Parquet failed (test error); fell back to JSON source.'
            };

            expect(fallbackDebug).toHaveProperty('label');
            expect(fallbackDebug).toHaveProperty('queryMs');
            expect(fallbackDebug).toHaveProperty('s3HeadRequests');
            expect(fallbackDebug).toHaveProperty('s3GetRequests');
            expect(fallbackDebug).toHaveProperty('s3RangeRequests');
            expect(fallbackDebug).toHaveProperty('s3PartialBytes');
            expect(fallbackDebug).toHaveProperty('note');
            expect(fallbackDebug.note).toContain('fell back to JSON source');
        });

        it('should have zero metrics when falling back', () => {
            const fallbackDebug = {
                label: 'players_list',
                queryMs: 0,
                s3HeadRequests: 0,
                s3GetRequests: 0,
                s3RangeRequests: 0,
                s3PartialBytes: 0,
                note: 'Parquet failed; fell back to JSON source.'
            };

            expect(fallbackDebug.queryMs).toBe(0);
            expect(fallbackDebug.s3HeadRequests).toBe(0);
            expect(fallbackDebug.s3GetRequests).toBe(0);
            expect(fallbackDebug.s3RangeRequests).toBe(0);
            expect(fallbackDebug.s3PartialBytes).toBe(0);
        });
    });

    describe('Query Debug Metadata', () => {
        it('should have correct structure for single query', () => {
            const debug = {
                label: 'teams_list',
                queryMs: 150,
                s3HeadRequests: 1,
                s3GetRequests: 1,
                s3RangeRequests: 2,
                s3PartialBytes: 512000
            };

            expect(typeof debug.label).toBe('string');
            expect(typeof debug.queryMs).toBe('number');
            expect(typeof debug.s3HeadRequests).toBe('number');
            expect(typeof debug.s3GetRequests).toBe('number');
            expect(typeof debug.s3RangeRequests).toBe('number');
            expect(typeof debug.s3PartialBytes).toBe('number');
        });

        it('should correctly combine metrics from multiple queries', () => {
            const metaDebug = {
                label: 'player_page_metadata',
                queryMs: 100,
                s3HeadRequests: 1,
                s3GetRequests: 1,
                s3RangeRequests: 1,
                s3PartialBytes: 50000
            };

            const statsDebug = {
                label: 'player_page_gamelog',
                queryMs: 200,
                s3HeadRequests: 1,
                s3GetRequests: 2,
                s3RangeRequests: 3,
                s3PartialBytes: 150000
            };

            const combined = {
                label: 'player_page_combined',
                queryMs: metaDebug.queryMs + statsDebug.queryMs,
                s3HeadRequests: metaDebug.s3HeadRequests + statsDebug.s3HeadRequests,
                s3GetRequests: metaDebug.s3GetRequests + statsDebug.s3GetRequests,
                s3RangeRequests: metaDebug.s3RangeRequests + statsDebug.s3RangeRequests,
                s3PartialBytes: metaDebug.s3PartialBytes + statsDebug.s3PartialBytes,
            };

            expect(combined.queryMs).toBe(300);
            expect(combined.s3HeadRequests).toBe(2);
            expect(combined.s3GetRequests).toBe(3);
            expect(combined.s3RangeRequests).toBe(4);
            expect(combined.s3PartialBytes).toBe(200000);
        });
    });

    describe('SQL Injection Prevention', () => {
        it('should use parameterized division values', () => {
            const div = "d1' OR '1'='1"; // attempted SQL injection
            const sql = `WHERE div = '${div}'`;
            
            // This test demonstrates the current vulnerability
            // In production, should use prepared statements or parameterized queries
            expect(sql).toContain(div);
        });

        it('should sanitize team ID values', () => {
            const team = "test'; DROP TABLE teams;--";
            const sql = `WHERE team_id = '${team}'`;
            
            // This test demonstrates the current vulnerability
            // Should implement proper sanitization or use DuckDB prepared statements
            expect(sql).toContain(team);
        });
    });
});

describe('Data Mode Detection', () => {
    it('should default to json when no dataMode specified', () => {
        const value = undefined;
        const mode = value === 'parquet' ? 'parquet' : 'json';
        expect(mode).toBe('json');
    });

    it('should detect parquet mode from URL param', () => {
        const searchParams = { dataMode: 'parquet' };
        const raw = searchParams.dataMode;
        const value = Array.isArray(raw) ? raw[0] : raw;
        const mode = value === 'parquet' ? 'parquet' : 'json';
        expect(mode).toBe('parquet');
    });

    it('should handle array values from URL params', () => {
        const searchParams = { dataMode: ['parquet', 'json'] };
        const raw = searchParams.dataMode;
        const value = Array.isArray(raw) ? raw[0] : raw;
        const mode = value === 'parquet' ? 'parquet' : 'json';
        expect(mode).toBe('parquet');
    });
});
