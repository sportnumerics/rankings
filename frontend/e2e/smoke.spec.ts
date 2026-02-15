import { test, expect } from '@playwright/test';

// These are intentionally simple “journey” checks.
// They should catch obvious regressions (blank pages, crashes, routing breakage)
// without being too brittle.

test('home page loads', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/Sportnumerics/i);
  // Ensure the app renders some meaningful navigation/content.
  await expect(page.getByRole('link', { name: /about/i })).toBeVisible();
});

test('about page loads', async ({ page }) => {
  await page.goto('/about');
  await expect(page).toHaveTitle(/Sportnumerics/i);
});

test('missing player shows friendly message', async ({ page }) => {
  await page.goto('/2024/players/definitely-not-a-player');
  await expect(page.getByRole('heading', { name: /player not found/i })).toBeVisible();
});

test('missing team schedule shows friendly message', async ({ page }) => {
  await page.goto('/2024/teams/definitely-not-a-team');
  await expect(page.getByRole('heading', { name: /team schedule not found/i })).toBeVisible();
});

test('games page loads', async ({ page }) => {
  await page.goto('/2026/games');
  await expect(page).toHaveTitle(/Sportnumerics/i);
  await expect(page.getByRole('heading', { name: /upcoming games/i })).toBeVisible();
});
