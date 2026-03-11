import { describe, it, expect, vi, beforeEach } from 'vitest';
import { parquetQuery, parseHttpDebug, dataModeFromSearch } from '../parquet';

// Mock duckdb module
vi.mock('duckdb', () => {
  return {
    default: {
      Database: vi.fn().mockImplementation(() => ({
        run: vi.fn((sql: string, callback: (err: Error | null) => void) => callback(null)),
        all: vi.fn((sql: string, callback: (err: Error | null, rows: any[]) => void) => callback(null, [])),
      })),
    },
  };
});

vi.mock('server-only', () => ({}));

describe('parquetQuery', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    process.env.AWS_ACCESS_KEY_ID = 'test-key';
    process.env.AWS_SECRET_ACCESS_KEY = 'test-secret';
  });

  it('returns query results with debug metadata', async () => {
    const mockRows = [
      { id: 1, name: 'Test 1' },
      { id: 2, name: 'Test 2' },
    ];

    const { parquetQuery: pq } = await import('../parquet');
    
    // Test that the function returns the expected structure
    const result = await pq('SELECT * FROM test', 'test_label');
    expect(result).toHaveProperty('rows');
    expect(result).toHaveProperty('debug');
    expect(result.debug).toHaveProperty('label', 'test_label');
    expect(result.debug).toHaveProperty('queryMs');
    expect(result.debug).toHaveProperty('s3HeadRequests');
    expect(result.debug).toHaveProperty('s3GetRequests');
    expect(result.debug).toHaveProperty('s3RangeRequests');
    expect(result.debug).toHaveProperty('s3PartialBytes');
  });
});

describe('dataModeFromSearch', () => {
  it('returns parquet when dataMode is parquet', () => {
    expect(dataModeFromSearch({ dataMode: 'parquet' })).toBe('parquet');
  });

  it('returns json when dataMode is not parquet', () => {
    expect(dataModeFromSearch({ dataMode: 'json' })).toBe('json');
    expect(dataModeFromSearch({ dataMode: 'invalid' })).toBe('json');
    expect(dataModeFromSearch({})).toBe('json');
    expect(dataModeFromSearch(undefined)).toBe('json');
  });

  it('handles array values', () => {
    expect(dataModeFromSearch({ dataMode: ['parquet'] })).toBe('parquet');
    expect(dataModeFromSearch({ dataMode: ['json', 'parquet'] })).toBe('json');
  });
});
