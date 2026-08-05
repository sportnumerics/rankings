import assert from 'node:assert/strict';
import test from 'node:test';

import { parquetQuery } from './parquet.ts';

test('parquetQuery executes an unparameterized query', async () => {
    const { rows } = await parquetQuery<{ value: number }>(
        'SELECT 1 AS value', 'unit_test');

    assert.deepEqual(rows, [{ value: 1 }]);
});

test('parquetQuery binds parameter values as literals', async () => {
    const value = "x' OR 1=1 --";
    const { rows } = await parquetQuery<{ value: string }>(
        'SELECT ? AS value', 'unit_test', [value]);

    assert.deepEqual(rows, [{ value }]);
});
