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
