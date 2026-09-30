import { captureRequest, expect, openapiExample, preferExample, test } from "./fixtures";

const RULES_MANIFEST = openapiExample<Record<string, unknown>>("manifest-rules");
const RULES_WEB_SHOP = openapiExample<Record<string, unknown>>("rules-web-shop");

test.describe("sources, crawl strategies, tasks, schedules, chains @mock", () => {
  test.beforeEach(async ({ admin }) => {
    // The collector-rules package of shop-example: manifest and rules.json from the contract examples.
    await admin.route("**/api/registry/v1/packages/shop-example.web-rules/versions/1.0.0", (route) =>
      route.fulfill({
        json: {
          package_id: "shop-example.web-rules",
          version: "1.0.0",
          digest: "sha256:bd33d6b0fb860947abb60fbf898610d7ad28e279daf21106399995dcd911674a",
          status: "approved",
          test_status: "passed",
          created_at: "2026-09-27T09:00:00Z",
          manifest: RULES_MANIFEST,
          files: [
            { path: "jane-package.json", size_bytes: 400, sha256: "1".repeat(64) },
            { path: "rules.json", size_bytes: 900, sha256: "2".repeat(64) },
          ],
        },
      }),
    );
    await admin.route(
      "**/api/registry/v1/packages/shop-example.web-rules/versions/1.0.0/file?path=rules.json",
      (route) => route.fulfill({ contentType: "text/plain", body: JSON.stringify(RULES_WEB_SHOP) }),
    );
  });

  test("source: combined strategies, «Передавати в LLM невідомі сторінки», save with PUT", async ({
    admin,
  }) => {
    await admin.goto("/sources");
    await admin.getByRole("link", { name: "shop-example" }).click();
    await expect(admin.getByRole("heading", { name: "Джерело shop-example" })).toBeVisible();
    const strategies = admin.getByRole("table", { name: "Стратегії обходу" });
    await expect(strategies).toContainText("Sitemap / Sitemap Index");
    await expect(strategies).toContainText("Рекурсивний обхід посилань");
    await expect(strategies).toContainText("Категорії, пагінація, пошук");

    const flag = admin.getByLabel("Передавати в LLM невідомі сторінки");
    await expect(flag).not.toBeChecked();
    await flag.check();
    const { body } = await captureRequest(admin, "PUT", "/api/orchestrator/v1/sources/shop-example", () =>
      admin.getByRole("button", { name: "Зберегти" }).click(),
    );
    expect(body["forward_unknown_to_llm"]).toBe(true);
    expect(body["collector_rules"]).toMatchObject({ package_id: "shop-example.web-rules", version: "1.0.0" });
    expect(body).not.toHaveProperty("created_at");
    await expect(admin.getByText("Збережено")).toBeVisible();
    await expect(admin.getByRole("table", { name: "Ефективні ліміти" })).toContainText(
      "rate.requests_per_second_per_host",
    );
  });

  test("new source is created with an Idempotency-Key", async ({ admin }) => {
    await admin.goto("/sources/new");
    await admin.getByLabel("Ідентифікатор (source_id)").fill("news-example");
    await admin.getByLabel("Назва").fill("News Example");
    await admin.getByLabel("URL").fill("https://news.example.test/");
    const { request, body } = await captureRequest(admin, "POST", "/api/orchestrator/v1/sources", () =>
      admin.getByRole("button", { name: "Створити джерело" }).click(),
    );
    expect(request.headers()["idempotency-key"]).toMatch(/^[0-9a-f-]{36}$/);
    expect(body).toMatchObject({
      source_id: "news-example",
      kind: "web",
      locator: { url: "https://news.example.test/" },
    });
  });

  test("rules editor: add a feed strategy to sitemap+recursive+listing and publish a new version", async ({
    admin,
  }) => {
    await admin.goto("/packages/shop-example.web-rules/versions/1.0.0/rules");
    await expect(admin.getByRole("heading", { name: /Стратегії обходу \(3\)/ })).toBeVisible();
    await admin.getByLabel("Тип нової стратегії").selectOption("feed");
    await admin.getByRole("button", { name: "Додати стратегію" }).click();
    await expect(admin.getByRole("heading", { name: /Стратегії обходу \(4\)/ })).toBeVisible();
    await expect(admin.getByText("Правила відповідають collector-rules.schema.json")).toBeVisible();
    await admin.getByLabel("Опис змін").fill("add RSS feed");
    const { body } = await captureRequest(
      admin,
      "POST",
      "/api/registry/v1/packages/shop-example.web-rules/versions",
      () => admin.getByRole("button", { name: "Опублікувати версію правил" }).click(),
    );
    const manifest = body["manifest"] as Record<string, unknown>;
    expect(manifest["version"]).toBe("1.1.0");
    expect(manifest["provenance"]).toMatchObject({
      created_by: "human",
      based_on: { package_id: "shop-example.web-rules", version: "1.0.0" },
      change_summary: "add RSS feed",
    });
    const files = body["files"] as Record<string, { data: string }>;
    const rules = JSON.parse(files["rules.json"]?.data ?? "{}") as { strategies: Array<{ type: string }> };
    expect(rules.strategies.map((s) => s.type)).toEqual(["sitemap", "recursive", "listing", "feed"]);
    expect(files).not.toHaveProperty("jane-package.json");
  });

  test("tasks: schedules, chain with branching, validation, test-mode run", async ({ admin }) => {
    await preferExample(admin, "/api/orchestrator/v1/tasks", "list");
    await admin.goto("/tasks");
    const table = admin.getByRole("table", { name: "Завдання" });
    await expect(table).toContainText("cron 0 2 * * 0 Europe/Kyiv");
    await expect(table).toContainText("кожні 86400 с");
    await table.getByRole("link", { name: "shop-catalog" }).click();

    await expect(admin.getByLabel("Тип розкладу")).toHaveValue("cron");
    await expect(admin.getByLabel("Cron (5 полів)")).toHaveValue("0 2 * * 0");

    await admin.getByRole("tab", { name: "Ланцюжок" }).click();
    for (const stage of [
      "collect",
      "store-raw",
      "extract-products",
      "store-products",
      "analyze-problems",
      "unknown-pages",
    ]) {
      await expect(admin.getByTestId(`dag-node-${stage}`)).toBeVisible();
    }
    await expect(admin.getByTestId("dag-edge-extract-products-analyze-problems")).toContainText("problems");
    await expect(admin.getByTestId("dag-edge-collect-unknown-pages")).toContainText("unmatched_materials");

    const { body } = await captureRequest(admin, "POST", "/api/orchestrator/v1/task-validations", () =>
      admin.getByRole("button", { name: "Перевірити в оркестраторі" }).click(),
    );
    expect(body["task_id"]).toBe("shop-catalog");
    await expect(admin.getByLabel("Результат перевірки")).toContainText("Перевірте конфігурацію завдання");
    await expect(admin.getByLabel("Результат перевірки")).toContainText(
      "Ефективне «Передавати в LLM невідомі сторінки»: ні",
    );

    await admin.getByRole("tab", { name: "Запуски" }).click();
    await admin.getByLabel("Причина").fill("dry run of new extractor");
    await admin.getByLabel("Тестовий режим (без запису в робочі дані)").check();
    const run = await captureRequest(admin, "POST", "/api/orchestrator/v1/tasks/shop-catalog/runs", () =>
      admin.getByRole("button", { name: "Запустити" }).click(),
    );
    expect(run.body).toEqual({ reason: "dry run of new extractor", test_mode: true });
    await expect(admin).toHaveURL(/\/runs\/job_/);
  });

  test("task schedule change is saved without code changes", async ({ admin }) => {
    await admin.goto("/tasks/shop-catalog");
    await admin.getByLabel("Тип розкладу").selectOption("interval");
    await admin.getByLabel("Інтервал, секунд").fill("3600");
    const { body } = await captureRequest(admin, "PUT", "/api/orchestrator/v1/tasks/shop-catalog", () =>
      admin.getByRole("button", { name: "Зберегти" }).click(),
    );
    expect(body["schedule"]).toMatchObject({
      type: "interval",
      interval_seconds: 3600,
      timezone: "Europe/Kyiv",
    });
    expect((body["stages"] as unknown[]).length).toBe(6);
  });
});
