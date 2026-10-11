import { test, expect, mockUrl } from "./fixtures";

test.describe("settings and responsive navigation @mock", () => {
  test("tablets and phones get a closable menu and labeled table cards without page overflow", async ({
    admin,
  }) => {
    await admin.goto("/connections");
    await expect(admin.getByRole("table", { name: "Підключення" })).toBeVisible();
    for (const width of [768, 390]) {
      await admin.setViewportSize({ width, height: 844 });
      await expect(admin.getByRole("navigation", { name: "Розділи" })).toBeHidden();
      const button = admin.getByRole("button", { name: "Відкрити меню" });
      await button.click();
      await expect(admin.getByRole("navigation", { name: "Розділи" })).toBeVisible();
      await admin.keyboard.press("Escape");
      await expect(admin.getByRole("navigation", { name: "Розділи" })).toBeHidden();
      await expect(button).toBeFocused();
      expect(await admin.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
        true,
      );
      if (width === 390) {
        await expect(
          admin.locator('table[aria-label="Підключення"] td[data-label="Підключення"]').first(),
        ).toBeVisible();
        expect(
          await admin
            .locator('table[aria-label="Підключення"] tbody tr')
            .first()
            .evaluate((row) => getComputedStyle(row).display),
        ).toBe("block");
      }
    }
  });

  test("usage shows loading before the accounting response and displays the returned total", async ({
    admin,
    request,
  }) => {
    const sample = await (await request.get(`${mockUrl("llm")}/v1/usage`)).json();
    let release: (() => void) | undefined;
    const gate = new Promise<void>((resolve) => {
      release = resolve;
    });
    await admin.route("**/api/llm/v1/usage?**", async (route) => {
      await gate;
      await route.fulfill({ json: sample });
    });
    await admin.goto("/llm?tab=usage");
    await expect(admin.getByRole("status")).toContainText("Завантаження");
    await expect(admin.getByText("Немає даних", { exact: true })).toHaveCount(0);
    release?.();
    await expect(admin.getByTestId("usage-total")).toContainText(sample.totals.cost.currency);
    await expect(admin.getByRole("table", { name: "Витрати LLM" })).toBeVisible();
  });

  test("budget levels clear stale ids and tab changes keep the unsaved amount until a decision", async ({
    admin,
  }) => {
    await admin.goto("/llm?tab=budgets");
    await admin.getByLabel("Сума", { exact: true }).fill("1.23");
    await admin.getByLabel("Рівень", { exact: true }).selectOption("source");
    await expect(admin.getByLabel("Джерело", { exact: true })).toHaveValue("");
    await expect(admin.getByRole("button", { name: "Зберегти бюджет" })).toBeDisabled();
    await admin.getByRole("tab", { name: "Псевдоніми моделей" }).click();
    const confirmation = admin.getByRole("dialog", { name: "Незбережені зміни" });
    await expect(confirmation).toBeVisible();
    await confirmation.getByRole("button", { name: "Залишитися" }).click();
    await expect(admin.getByLabel("Сума", { exact: true })).toHaveValue("1.23");
    await admin.getByRole("tab", { name: "Псевдоніми моделей" }).click();
    await confirmation.getByRole("button", { name: "Відкинути й перейти" }).click();
    await expect(admin).toHaveURL(/tab=aliases/);
  });
});
