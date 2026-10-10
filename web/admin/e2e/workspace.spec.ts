import path from "node:path";
import { captureRequest, expect, fulfillJson, login, mockUrl, openapiExample, test } from "./fixtures";
import type { Run, Source, TaskSummary } from "../src/api/types";

const evidence = path.resolve(import.meta.dirname, "../../../.jane");

test.describe("admin workspace", () => {
  test("list rows and action buttons stay compact while dialogs are open @mock", async ({ admin }) => {
    await admin.setViewportSize({ width: 1600, height: 900 });
    await admin.getByLabel("Тема оформлення").selectOption("dark");
    const response = await admin.request.get(`${mockUrl("orchestrator")}/v1/tasks`);
    const list = (await response.json()) as { items: TaskSummary[]; next_cursor: string | null };
    const title = "Повний збір каталогу з довгою назвою джерела та детальним описом призначення завдання";
    await fulfillJson(admin, "/api/orchestrator/v1/tasks", {
      ...list,
      items: list.items.map((task) => ({ ...task, title })),
    });
    await admin.goto("/tasks");
    const row = admin.getByRole("table", { name: "Завдання" }).locator("tbody tr").first();
    const actions = row.locator(".row-actions .btn");
    await expect(actions).toHaveCount(2);
    const sizes = await actions.evaluateAll((buttons) =>
      buttons.map((button) => {
        const rect = button.getBoundingClientRect();
        return { height: rect.height, width: rect.width, top: rect.top };
      }),
    );
    expect(sizes[0]).toEqual(sizes[1]);
    await expect(row.getByTitle(title)).toHaveText(title);
    expect(
      await row
        .getByTitle(title)
        .evaluate(
          (cell) =>
            cell.getBoundingClientRect().height <= Number.parseFloat(getComputedStyle(cell).lineHeight) + 1,
        ),
    ).toBe(true);
    await row
      .locator("xpath=ancestor::div[contains(@class, 'table-wrap')]")
      .screenshot({ path: path.join(evidence, "wp12-admin-compact-tasks.png") });
    const height = (await row.boundingBox())!.height;
    const trigger = row.getByRole("button", { name: /^Запустити / });
    await trigger.click();
    await expect(admin.getByRole("dialog", { name: /^Запуск / })).toBeVisible();
    expect((await row.boundingBox())!.height).toBe(height);
    await admin.keyboard.press("Escape");
    await expect(admin.getByRole("dialog")).toHaveCount(0);
    await expect(trigger).toBeFocused();
    await admin.goto("/runs");
    const runRow = admin.getByRole("table", { name: "Запуски" }).locator("tbody tr").first();
    await runRow
      .locator("xpath=ancestor::div[contains(@class, 'table-wrap')]")
      .screenshot({ path: path.join(evidence, "wp12-admin-compact-runs.png") });
    const runHeight = (await runRow.boundingBox())!.height;
    await runRow.getByRole("button", { name: "Зупинити", exact: true }).click();
    await expect(admin.getByRole("dialog", { name: "Зупинити", exact: true })).toBeVisible();
    expect((await runRow.boundingBox())!.height).toBe(runHeight);
    await admin.keyboard.press("Escape");
    await expect(admin.getByRole("dialog")).toHaveCount(0);
    const cancelUrl = /\/api\/orchestrator\/v1\/runs\/[^/]+\/cancel$/;
    await admin.route(cancelUrl, (route) =>
      route.fulfill({
        status: 503,
        json: {
          type: "urn:jane:problem:unavailable",
          title: "Unavailable",
          status: 503,
          code: "unavailable",
        },
      }),
    );
    await runRow.getByRole("button", { name: "Зупинити", exact: true }).click();
    await admin.getByRole("button", { name: "Підтвердити зупинку" }).click();
    await expect(admin.getByRole("alert")).toContainText("Не вдалося зупинити");
    expect((await runRow.boundingBox())!.height).toBe(runHeight);
    await expect(runRow.getByRole("alert")).toHaveCount(0);
    await admin.unroute(cancelUrl);
    await runRow.getByRole("button", { name: "Зупинити", exact: true }).click();
    await admin.getByLabel("Причина: Зупинити").fill("Перевірка компактності після зупинки");
    await admin.getByRole("button", { name: "Підтвердити зупинку" }).click();
    await expect(
      admin.getByText("Скасування прийнято. Уже збережені дані залишаються у сховищах."),
    ).toBeVisible();
    expect((await runRow.boundingBox())!.height).toBe(runHeight);
    await expect(runRow).not.toContainText("Скасування прийнято");
  });
  test("active metric keeps queued runs visible after following its link @mock", async ({ admin }) => {
    const response = await admin.request.get(`${mockUrl("orchestrator")}/v1/runs`);
    const list = (await response.json()) as { items: Run[]; next_cursor: string | null };
    expect(list.items.length).toBeGreaterThan(0);
    await fulfillJson(admin, "/api/orchestrator/v1/runs", {
      ...list,
      items: list.items.map((run) => ({ ...run, status: "queued" })),
    });
    await admin.goto("/");
    const metric = admin.locator(".metric").filter({ hasText: "Серед останніх запусків" });
    await expect(metric.locator(".metric-value")).toHaveText(String(list.items.length));
    await expect(metric).toHaveAttribute("href", "/runs");
    await metric.click();
    await expect(admin).toHaveURL(/\/runs$/);
    await expect(admin.getByRole("table", { name: "Запуски" })).toContainText("queued");
  });
  test("LLM reporting requests a rolling window and refreshes its upper bound @mock", async ({ admin }) => {
    await admin.goto("/");
    await expect(admin.getByTestId("usage-total")).not.toHaveText("—");
    const selected = await captureRequest(admin, "GET", "/api/llm/v1/usage", () =>
      admin.getByLabel("Період витрат LLM").selectOption("7"),
    );
    const selectedUrl = new URL(selected.request.url());
    expect(
      Date.parse(selectedUrl.searchParams.get("until")!) - Date.parse(selectedUrl.searchParams.get("since")!),
    ).toBe(7 * 86400000);
    await expect(admin.getByRole("button", { name: "Оновити", exact: true })).toBeEnabled();
    const updated = await captureRequest(admin, "GET", "/api/llm/v1/usage", () =>
      admin.getByRole("button", { name: "Оновити", exact: true }).click(),
    );
    expect(Date.parse(new URL(updated.request.url()).searchParams.get("until")!)).toBeGreaterThanOrEqual(
      Date.parse(selectedUrl.searchParams.get("until")!),
    );
  });

  test("run list cancels with an explicit confirmation and audit reason @mock", async ({ admin }) => {
    await admin.goto("/runs");
    await admin.getByRole("button", { name: "Зупинити", exact: true }).first().click();
    await admin.getByLabel("Причина: Зупинити").fill("Перевірка зупинки зі списку");
    const { body } = await captureRequest(admin, "POST", /\/v1\/runs\/[^/]+\/cancel$/, () =>
      admin.getByRole("button", { name: "Підтвердити зупинку" }).click(),
    );
    expect(body).toEqual({ reason: "Перевірка зупинки зі списку" });
    await expect(
      admin.getByText("Скасування прийнято. Уже збережені дані залишаються у сховищах."),
    ).toBeVisible();
  });

  test("changing themes preserves unsaved code and undo history @mock", async ({ admin }) => {
    await admin.goto("/packages/shop-example.product-extractor/versions/1.2.0/edit");
    const editor = admin.getByRole("textbox", { name: "Код src/product_extractor/main.py" });
    await editor.click();
    await admin.keyboard.press("Control+End");
    await admin.keyboard.insertText("\n# theme-draft\n");
    await admin.getByLabel("Тема оформлення").selectOption("dark");
    await expect(editor).toContainText("# theme-draft");
    await expect(admin.getByLabel("Локальні зміни")).toContainText("+# theme-draft");
    await admin.screenshot({ path: path.join(evidence, "wp12-admin-editor-dark.png"), fullPage: true });
    await admin.getByLabel("Тема оформлення").selectOption("light");
    await expect(editor).toContainText("# theme-draft");
    await editor.click();
    await admin.keyboard.press("Control+z");
    await expect(editor).not.toContainText("# theme-draft");
  });
  test("dark and light themes persist across reload and cover all screens", async ({ admin }) => {
    await admin.getByLabel("Тема оформлення").selectOption("dark");
    await expect(admin.locator("html")).toHaveAttribute("data-theme", "dark");
    await expect(admin.getByRole("heading", { name: "Потребує уваги" })).toBeVisible();
    await expect(admin.getByRole("button", { name: "Оновити", exact: true })).toBeEnabled();
    await expect(admin.getByRole("alert")).toHaveCount(0);
    await admin.screenshot({ path: path.join(evidence, "wp12-admin-dark.png"), fullPage: true });
    await admin.reload();
    await expect(admin.getByLabel("Тема оформлення")).toHaveValue("dark");
    await admin
      .getByRole("navigation", { name: "Розділи" })
      .getByRole("link", { name: "Джерела", exact: true })
      .click();
    await expect(admin.locator("html")).toHaveAttribute("data-theme", "dark");
    await admin.getByLabel("Тема оформлення").selectOption("light");
    await admin.goto("/");
    await expect(admin.getByLabel("Тема оформлення")).toHaveValue("light");
    await expect(admin.getByTestId("usage-total")).not.toHaveText("—");
    await expect(admin.getByRole("button", { name: "Оновити", exact: true })).toBeEnabled();
    await expect(admin.getByRole("alert")).toHaveCount(0);
    await admin.screenshot({ path: path.join(evidence, "wp12-admin-light.png"), fullPage: true });
  });

  test("system preference responds to OS changes and explicit dark overrides it", async ({ admin }) => {
    await admin.getByLabel("Тема оформлення").selectOption("system");
    await admin.emulateMedia({ colorScheme: "dark" });
    await expect(admin.locator("html")).toHaveAttribute("data-theme", "dark");
    await admin.emulateMedia({ colorScheme: "light" });
    await expect(admin.locator("html")).toHaveAttribute("data-theme", "light");
    await admin.getByLabel("Тема оформлення").selectOption("dark");
    await admin.emulateMedia({ colorScheme: "light" });
    await expect(admin.locator("html")).toHaveAttribute("data-theme", "dark");
  });

  test("theme works with unavailable local storage", async ({ page }) => {
    await page.addInitScript(() => {
      Object.defineProperty(window, "localStorage", {
        get() {
          throw new DOMException("unavailable", "SecurityError");
        },
      });
    });
    await login(page);
    await page.getByLabel("Тема оформлення").selectOption("dark");
    await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
    await expect(page.getByRole("heading", { name: "Огляд", exact: true })).toBeVisible();
  });

  test("mobile navigation opens, closes on selection and keeps content within viewport", async ({
    admin,
  }) => {
    await admin.setViewportSize({ width: 390, height: 844 });
    await admin.getByLabel("Тема оформлення").selectOption("dark");
    await expect(admin.getByRole("navigation", { name: "Розділи" })).not.toBeVisible();
    await admin.getByRole("button", { name: "Відкрити меню" }).click();
    await expect(admin.getByRole("navigation", { name: "Розділи" })).toBeVisible();
    await admin
      .getByRole("navigation", { name: "Розділи" })
      .getByRole("link", { name: "Завдання", exact: true })
      .click();
    await expect(admin.getByRole("heading", { name: "Завдання", exact: true })).toBeVisible();
    await expect(admin.getByRole("navigation", { name: "Розділи" })).not.toBeVisible();
    await admin.goto("/");
    await expect(admin.getByTestId("usage-total")).not.toHaveText("—");
    await expect(admin.getByRole("button", { name: "Оновити", exact: true })).toBeEnabled();
    await expect(admin.getByRole("alert")).toHaveCount(0);
    expect(await admin.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    await admin.screenshot({ path: path.join(evidence, "wp12-admin-mobile.png"), fullPage: true });
  });

  test("dashboard distinguishes paginated samples from unavailable services @mock", async ({ admin }) => {
    const source = openapiExample<Source>("source-shop");
    await fulfillJson(admin, "/api/orchestrator/v1/sources", { items: [source], next_cursor: "next-page" });
    await fulfillJson(
      admin,
      "/api/llm/v1/usage",
      { type: "urn:jane:problem:unavailable", title: "Unavailable", status: 503, code: "unavailable" },
      "GET",
      503,
    );
    await admin.reload();
    await expect(admin.locator(".metric").filter({ hasText: "Джерела" }).locator(".metric-value")).toHaveText(
      "1+",
    );
    await expect(admin.getByTestId("usage-total")).toHaveText("—");
    await expect(admin.getByText("У цій вибірці проблем немає")).not.toBeVisible();
    await expect(admin.getByRole("alert")).toBeVisible();
  });

  test("quick run defaults to test mode and submits the selected mode with idempotency @mock", async ({
    admin,
  }) => {
    await admin.goto("/tasks");
    const open = admin.getByRole("button", { name: /^Запустити / }).first();
    await open.click();
    const form = admin.getByRole("form", { name: /^Запуск / });
    await expect(form.getByLabel("Режим запуску")).toHaveValue("test");
    await form.getByLabel("Причина запуску").fill("Перевірка інтерфейсу");
    const { request, body } = await captureRequest(admin, "POST", /\/v1\/tasks\/[^/]+\/runs$/, () =>
      form.getByRole("button", { name: "Підтвердити запуск" }).click(),
    );
    expect(body).toEqual({ test_mode: true, reason: "Перевірка інтерфейсу" });
    expect(request.headers()["idempotency-key"]).toBeTruthy();
    await expect(admin).toHaveURL(/\/runs\//);
    await admin.goto("/tasks");
    await admin
      .getByRole("button", { name: /^Запустити / })
      .first()
      .click();
    await admin.getByLabel("Режим запуску").selectOption("live");
    await expect(admin.getByText("Етапи збереження запишуть результати в робочі сховища.")).toBeVisible();
    const live = await captureRequest(admin, "POST", /\/v1\/tasks\/[^/]+\/runs$/, () =>
      admin.getByRole("button", { name: "Підтвердити запуск" }).click(),
    );
    expect(live.body["test_mode"]).toBe(false);
    expect(live.request.headers()["idempotency-key"]).not.toBe(request.headers()["idempotency-key"]);
  });

  test("problem links preserve source and status through filters and reload @mock", async ({ admin }) => {
    const requests: URL[] = [];
    admin.on("request", (request) => {
      if (new URL(request.url()).pathname.endsWith("/v1/problem-groups"))
        requests.push(new URL(request.url()));
    });
    await admin.goto("/problems?status=open&source_id=shop-example");
    await expect(admin.getByLabel("Стан групи")).toHaveValue("open");
    await expect(admin.getByLabel("Джерело", { exact: true })).toHaveValue("shop-example");
    await expect
      .poll(() =>
        requests.some(
          (url) =>
            url.searchParams.get("source_id") === "shop-example" && url.searchParams.get("status") === "open",
        ),
      )
      .toBe(true);
    await admin.getByLabel("Стан групи").selectOption("unresolved");
    await expect(admin).toHaveURL(/source_id=shop-example/);
    await admin.reload();
    await expect(admin.getByLabel("Стан групи")).toHaveValue("unresolved");
  });

  test("source search and task shortcuts work without hiding pagination @mock", async ({ admin }) => {
    await admin.goto("/sources");
    await expect(admin.getByRole("table", { name: "Джерела" })).toBeVisible();
    await admin.getByLabel("Пошук у завантажених джерелах").fill("no-match-in-loaded-page");
    await expect(admin.getByText(/Збігів у завантажених джерелах немає/)).toBeVisible();
    await admin.getByLabel("Пошук у завантажених джерелах").clear();
    await admin.getByRole("link", { name: "Завдання джерела" }).first().click();
    await expect(admin).toHaveURL(/\/tasks\?source_id=/);
    await expect(admin.getByLabel("Джерело", { exact: true })).not.toHaveValue("");
  });
});
