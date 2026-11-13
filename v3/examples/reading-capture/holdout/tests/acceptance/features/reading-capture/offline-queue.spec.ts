// Holdout binding: drives the running product through the browser and the public API only.
import { test, expect } from '@playwright/test';

test('@SC-1 A reading saved offline syncs once', async ({ page, context, request }) => {
  await page.goto('/capture');
  await context.setOffline(true);
  await page.getByLabel('Asset tag').fill('PMP-0412');
  await page.getByLabel('Value').fill('7.25');
  await page.getByRole('button', { name: 'Save reading' }).click();
  await context.setOffline(false);
  await expect.poll(async () => {
    const res = await request.get('/v1/readings?asset_tag=PMP-0412');
    return (await res.json()).items.filter((r: { value: string }) => r.value === '7.25').length;
  }, { timeout: 60_000 }).toBe(1);
});

test('@SC-1 The same reading sent twice is stored once', async ({ request }) => {
  const body = { id: '0192f3a1-7c4e-7b2a-9d1e-3f5a6b7c8d9e', asset_tag: 'PMP-0412', value: '7.25',
    captured_at: '2026-11-11T08:42:10-03:00' };
  const first = await request.post('/v1/readings', { data: body });
  const second = await request.post('/v1/readings', { data: body });
  expect(await second.json()).toEqual(await first.json());
  const list = await (await request.get('/v1/readings?asset_tag=PMP-0412')).json();
  expect(list.items.filter((r: { id: string }) => r.id === body.id)).toHaveLength(1);
});
