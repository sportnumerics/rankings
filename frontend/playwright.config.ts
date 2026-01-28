import { defineConfig, devices } from '@playwright/test';

// Default to prod; can override via BASE_URL.
const baseURL = process.env.BASE_URL ?? 'https://sportnumerics.com';

export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  expect: {
    timeout: 10_000,
  },
  retries: 0,
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
