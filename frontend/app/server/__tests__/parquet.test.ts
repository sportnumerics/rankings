import { describe, it, expect, vi } from 'vitest';
import { dataModeFromSearch } from '../parquet';

// Mock server-only
vi.mock('server-only', () => ({}));

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
