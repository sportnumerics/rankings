import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  esbuild: {
    jsx: 'automatic'
  },
  test: {
    globals: true,
    environment: 'node',
    include: ['app/**/*.{test,spec}.{ts,tsx}'],
    setupFiles: ['./vitest.setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './app'),
      'server-only': path.resolve(__dirname, './test/mocks/server-only.ts'),
    },
  },
});
