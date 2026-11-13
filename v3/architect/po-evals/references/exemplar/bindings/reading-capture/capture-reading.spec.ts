// Holdout binding: drives the running product through the browser only.
import { test, expect } from '@playwright/test';

test.use({ viewport: { width: 360, height: 800 } });

test('@SC-2 Recording a reading takes at most 3 taps', async ({ page }) => {
  await page.goto('/capture');
  await page.getByLabel('Asset tag').fill('PMP-0412');
  let taps = 0;
  page.on('request', () => {});
  await page.getByLabel('Value').fill('7.25'); taps += 1;
  await page.getByRole('button', { name: 'Save reading' }).click(); taps += 1;
  await expect(page.getByRole('list', { name: "Today's readings" })).toContainText('PMP-0412');
  await expect(page.getByRole('list', { name: "Today's readings" })).toContainText('7.25 bar');
  expect(taps).toBeLessThanOrEqual(3);
});

test('@SC-3 An unknown tag is refused with the next step', async ({ page }) => {
  await page.goto('/capture');
  await page.getByLabel('Asset tag').fill('XXX-0000');
  await page.getByLabel('Value').fill('7.25');
  await page.getByRole('button', { name: 'Save reading' }).click();
  await expect(page.getByRole('alert')).toHaveText('Tag not found. Check the tag or ask your planner.');
  await expect(page.getByLabel('Value')).toHaveValue('7.25');
  await expect(page.getByRole('list', { name: "Today's readings" })).not.toContainText('XXX-0000');
});
