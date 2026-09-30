import { API_KEY, expect, expectNoSecretLeak, login, test } from "./fixtures";

// Runs on mocks and on the real API: login, navigation over every section, no secret leaks.
test.describe("auth and navigation", () => {
  test("unauthenticated users are sent to the login page", async ({ page }) => {
    await page.goto("/sources");
    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByLabel("Ключ API")).toHaveAttribute("type", "password");
  });

  test("the API key stays in sessionStorage, is sent as Bearer and is never displayed", async ({ page }) => {
    const auth: string[] = [];
    page.on("request", (r) => {
      if (new URL(r.url()).pathname.startsWith("/api/")) auth.push(r.headers()["authorization"] ?? "");
    });
    await login(page);
    await expect(page.getByRole("heading", { name: "Огляд" })).toBeVisible();
    expect(await page.evaluate(() => sessionStorage.getItem("jane.admin.api_key"))).toBe(API_KEY);
    await expectNoSecretLeak(page);
    expect(auth.length).toBeGreaterThan(0);
    expect(new Set(auth)).toEqual(new Set([`Bearer ${API_KEY}`]));

    for (const section of [
      "Джерела",
      "Завдання",
      "Запуски",
      "Матеріали",
      "Результати",
      "Проблеми",
      "Пакети",
      "Асистент",
      "Підключення",
      "LLM",
      "Ліміти",
      "Аудит",
    ]) {
      await page
        .getByRole("navigation", { name: "Розділи" })
        .getByRole("link", { name: section, exact: true })
        .click();
      await expect(page.locator("h1")).toBeVisible();
      await expectNoSecretLeak(page);
    }

    await page.getByRole("button", { name: "Вийти" }).click();
    await expect(page).toHaveURL(/\/login$/);
    expect(await page.evaluate(() => sessionStorage.getItem("jane.admin.api_key"))).toBeNull();
  });
});
