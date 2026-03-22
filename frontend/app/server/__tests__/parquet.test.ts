import { describe, it, expect } from 'vitest';
import { dataModeFromSearch } from '../parquet';

describe('parquet module', () => {
  describe('dataModeFromSearch', () => {
    it('returns "parquet" when dataMode param is "parquet"', () => {
      const result = dataModeFromSearch({ dataMode: 'parquet' });
      expect(result).toBe('parquet');
    });

    it('returns "json" when dataMode param is missing', () => {
      const result = dataModeFromSearch({});
      expect(result).toBe('json');
    });

    it('returns "json" when dataMode param is "json"', () => {
      const result = dataModeFromSearch({ dataMode: 'json' });
      expect(result).toBe('json');
    });

    it('returns "json" when dataMode param is invalid', () => {
      const result = dataModeFromSearch({ dataMode: 'invalid' });
      expect(result).toBe('json');
    });

    it('handles array values (takes first element)', () => {
      const result = dataModeFromSearch({ dataMode: ['parquet', 'json'] });
      expect(result).toBe('parquet');
    });

    it('returns "json" when searchParams is undefined', () => {
      const result = dataModeFromSearch(undefined);
      expect(result).toBe('json');
    });
  });
});
