import { test, expect, API_KEY } from "./fixtures";
import { apiTarget } from "../dev-proxy";

test.describe("module operations on a real stack", () => {
  test.skip(!apiTarget(), "Requires real module telemetry and persistent configuration");

  test("all eight module forms load, diagnostics and monitoring show real responses", async ({ admin }) => {
    test.setTimeout(180_000);
    await admin.goto("/modules");
    await expect(admin.locator("article.module-card")).toHaveCount(8);
    const cards = await admin
      .locator("article.module-card h2 a")
      .evaluateAll((links) =>
        links.map((link) => ({ name: link.textContent!, path: link.getAttribute("href")! })),
      );
    for (const module of cards) {
      await admin.goto(`${module.path}?tab=settings`);
      await expect(admin.getByRole("heading", { level: 1, name: module.name })).toBeVisible();
      await expect(admin.getByLabel("Знайти налаштування")).toBeVisible({ timeout: 30_000 });
      await admin.getByLabel("Знайти налаштування").fill("Максимум точок");
      await expect(admin.getByRole("spinbutton", { name: "Максимум точок графіка" })).toBeVisible();
      await expect(admin.getByRole("button", { name: "Зберегти налаштування" })).toBeDisabled();
      await admin.getByRole("tab", { name: "Діагностика" }).click();
      await expect(admin.getByRole("heading", { name: "Можливості модуля" })).toBeVisible();
      await admin.getByRole("tab", { name: "Моніторинг", exact: true }).click();
      await expect(admin.locator(".telemetry-chart").first()).toBeVisible();
      await expect(admin.getByText(/Останнє вимірювання:/)).toBeVisible();
    }
  });

  test("saves a draft with ETag, rejects stale writes and restores the original overrides", async ({
    admin,
    request,
  }) => {
    const endpoint = `${apiTarget()}/api/assistant/v1/configuration`;
    const headers = { Authorization: `Bearer ${API_KEY}` };
    const before = await request.get(endpoint, { headers });
    expect(before.ok()).toBeTruthy();
    const initial = await before.json();
    const field = initial.fields.find(
      (item: { path: string }) => item.path === "settings.operations_max_points",
    );
    const value = initial.overrides[field.path] ?? field.inherited_value;
    const changed = value === field.maximum ? value - 1 : value + 1;
    try {
      await admin.goto("/modules/assistant?tab=settings");
      await admin.getByLabel("Знайти налаштування").fill("Максимум точок");
      await admin.getByRole("spinbutton", { name: "Максимум точок графіка" }).fill(String(changed));
      await admin.getByRole("button", { name: "Зберегти налаштування" }).click();
      await expect(admin.getByText("Є збережені зміни, що очікують перезапуску.")).toBeVisible();
      const saved = await request.get(endpoint, { headers });
      expect((await saved.json()).overrides[field.path]).toBe(changed);
      const stale = await request.put(endpoint, {
        headers: { ...headers, "If-Match": before.headers()["etag"]! },
        data: { values: initial.overrides },
      });
      expect(stale.status()).toBe(412);
    } finally {
      const current = await request.get(endpoint, { headers });
      const restored = await request.put(endpoint, {
        headers: { ...headers, "If-Match": current.headers()["etag"]! },
        data: { values: initial.overrides },
      });
      expect(restored.ok()).toBeTruthy();
      expect((await restored.json()).pending_restart).toBe(initial.pending_restart);
    }
  });

  test("period controls, refresh, basic/advanced forms and narrow screens work", async ({ admin }) => {
    await admin.goto("/monitoring");
    await expect(admin.getByRole("img").first()).toBeVisible();
    await admin.getByLabel("Період моніторингу").selectOption("1440");
    await expect(admin.getByLabel("Період моніторингу")).toHaveValue("1440");
    await admin.getByLabel("Автооновлення").uncheck();
    await expect(admin.getByLabel("Автооновлення")).not.toBeChecked();
    const refresh = admin.waitForResponse(
      (response) => response.url().includes("/v1/telemetry") && response.ok(),
    );
    await admin.getByRole("button", { name: "Оновити", exact: true }).click();
    await refresh;
    await admin.goto("/modules/assistant?tab=settings");
    const basic = await admin.locator(".module-setting-row").count();
    await admin.getByLabel("Показати розширені налаштування").check();
    expect(await admin.locator(".module-setting-row").count()).toBeGreaterThan(basic);
    await admin.setViewportSize({ width: 390, height: 844 });
    const fits = await admin.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth);
    expect(fits).toBeTruthy();
    await admin.goto("/monitoring");
    await expect(admin.getByRole("img").first()).toBeVisible();
    expect(
      await admin.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
    ).toBeTruthy();
  });
});
