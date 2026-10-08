import { captureRequest, expect, realServiceUrl, test } from "./fixtures";
import {
  TESTSITE_URL,
  jsonRequest,
  publishTestsiteRules,
  testsiteRecursivePageCount,
  uniqueId,
} from "./seed";

// The main admin API against the REAL orchestrator (WP-09, PostgreSQL). Every scenario creates its own objects
// with unique ids through the UI, so nothing depends on contract example data.
// Hybrid: JANE_ADMIN_TARGET_ORCHESTRATOR=http://127.0.0.1:<port>; whole stack: JANE_ADMIN_API_TARGET.
test.describe("real orchestrator: sources, tasks, schedules, limits, connections, audit @hybrid", () => {
  test.beforeEach(() => {
    test.skip(
      !realServiceUrl("orchestrator"),
      "JANE_ADMIN_TARGET_ORCHESTRATOR / JANE_ADMIN_API_TARGET is not set",
    );
  });

  test("source: create, toggle «Передавати в LLM невідомі сторінки» with If-Match, persisted", async ({
    admin,
  }) => {
    const sourceId = uniqueId("e2e-src");
    await admin.goto("/sources/new");
    await admin.getByLabel("Ідентифікатор (source_id)").fill(sourceId);
    await admin.getByLabel("Назва").fill(`E2E ${sourceId}`);
    await admin.getByLabel("URL").fill(`https://${sourceId}.example.test/`);
    await admin.getByLabel("Очікувані типи даних").fill("product");
    const created = await captureRequest(admin, "POST", "/api/orchestrator/v1/sources", () =>
      admin.getByRole("button", { name: "Створити джерело" }).click(),
    );
    expect(created.request.headers()["idempotency-key"]).toBeTruthy();
    await expect(admin).toHaveURL(new RegExp(`/sources/${sourceId}$`));
    await expect(admin.getByRole("heading", { name: `Джерело ${sourceId}` })).toBeVisible();

    await admin.getByLabel("Передавати в LLM невідомі сторінки").check();
    const saved = await captureRequest(admin, "PUT", `/api/orchestrator/v1/sources/${sourceId}`, () =>
      admin.getByRole("button", { name: "Зберегти" }).click(),
    );
    expect(saved.request.headers()["if-match"]).toBeTruthy();
    await expect(admin.getByText("Збережено")).toBeVisible();

    await admin.reload();
    await expect(admin.getByLabel("Передавати в LLM невідомі сторінки")).toBeChecked();
    await expect(admin.getByRole("table", { name: "Ефективні ліміти" })).toBeVisible();
    await admin.goto("/sources");
    await expect(admin.getByRole("table", { name: "Джерела" })).toContainText(sourceId);
    await expect(admin.getByRole("alert")).toHaveCount(0);
  });

  test("task: create, chain view, orchestrator validation, schedule change persisted, effective limits", async ({
    admin,
  }) => {
    const sourceId = uniqueId("e2e-src");
    const taskId = uniqueId("e2e-task");
    await admin.goto("/sources/new");
    await admin.getByLabel("Ідентифікатор (source_id)").fill(sourceId);
    await admin.getByLabel("Назва").fill(`E2E ${sourceId}`);
    await admin.getByLabel("URL").fill(`https://${sourceId}.example.test/`);
    await admin.getByRole("button", { name: "Створити джерело" }).click();
    await expect(admin).toHaveURL(new RegExp(`/sources/${sourceId}$`));

    await admin.goto("/tasks/new");
    await admin.getByLabel("Ідентифікатор (task_id)").fill(taskId);
    await admin.getByLabel("Назва").fill(`E2E ${taskId}`);
    await admin.getByLabel("Джерело (source_id)").fill(sourceId);
    await admin
      .getByLabel("Явний перелік URL (замість правил джерела; по одному в рядку)")
      .fill(`https://${sourceId}.example.test/a`);
    const validated = await captureRequest(admin, "POST", "/api/orchestrator/v1/task-validations", () =>
      admin.getByRole("button", { name: "Перевірити в оркестраторі" }).click(),
    );
    expect(validated.body["task_id"]).toBe(taskId);
    await expect(admin.getByLabel("Результат перевірки")).toBeVisible();

    const created = await captureRequest(admin, "POST", "/api/orchestrator/v1/tasks", () =>
      admin.getByRole("button", { name: "Створити завдання" }).click(),
    );
    expect(created.body).toMatchObject({ task_id: taskId, input: { source_id: sourceId } });
    await expect(admin).toHaveURL(new RegExp(`/tasks/${taskId}$`));

    await admin.getByRole("tab", { name: "Ланцюжок" }).click();
    await expect(admin.getByTestId("dag-node-collect")).toBeVisible();

    await admin.getByRole("tab", { name: "Конфігурація" }).click();
    await admin.getByLabel("Тип розкладу").selectOption("interval");
    await admin.getByLabel("Інтервал, секунд").fill("7200");
    const saved = await captureRequest(admin, "PUT", `/api/orchestrator/v1/tasks/${taskId}`, () =>
      admin.getByRole("button", { name: "Зберегти" }).click(),
    );
    expect(saved.request.headers()["if-match"]).toBeTruthy();
    await expect(admin.getByText(/Збережено/)).toBeVisible();
    await admin.reload();
    await expect(admin.getByLabel("Тип розкладу")).toHaveValue("interval");
    await expect(admin.getByLabel("Інтервал, секунд")).toHaveValue("7200");

    await admin.goto("/tasks");
    await expect(admin.getByRole("table", { name: "Завдання" })).toContainText("кожні 7200 с");

    await admin.goto(`/tasks/${taskId}`);
    await admin.getByRole("tab", { name: "Ефективні ліміти" }).click();
    await expect(admin.getByRole("table", { name: "Ефективні ліміти" })).toContainText(
      "queue.max_queue_depth",
    );
    await expect(admin.getByRole("alert")).toHaveCount(0);
    // This source has no collector rules and a non-resolvable host, so the run may end at once: here only the
    // start of a test-mode run is checked. Cancelling a run that is still collecting is the next scenario.
    await admin.getByRole("tab", { name: "Запуски" }).click();
    await admin.getByLabel("Причина").fill("e2e test-mode run");
    await admin.getByLabel("Тестовий режим (без запису в робочі дані)").check();
    const started = await captureRequest(admin, "POST", `/api/orchestrator/v1/tasks/${taskId}/runs`, () =>
      admin.getByRole("button", { name: "Запустити" }).click(),
    );
    expect(started.request.headers()["idempotency-key"]).toBeTruthy();
    expect(started.body).toEqual({ reason: "e2e test-mode run", test_mode: true });
    await expect(admin).toHaveURL(/\/runs\/run_/);
    await expect(admin.getByText("так (без запису в робочі дані)")).toBeVisible();
    await admin.getByRole("tab", { name: "Елементи й помилки" }).click();
    await expect(admin.getByRole("region", { name: "Елементи запуску" })).toBeVisible();
  });

  test("run cancel: a slow real testsite collection is cancelled from the UI while running; run and collection end cancelled", async ({
    admin,
    request,
  }) => {
    test.setTimeout(240_000);
    const registry = realServiceUrl("registry");
    const collector = realServiceUrl("collector");
    test.skip(!registry || !collector, "a real collection needs the real registry and web collector");
    const orchestratorUrl = realServiceUrl("orchestrator") as string;
    // Deterministic, not a race: the task limits (contract field rate.requests_per_second_per_host, set in the
    // task editor) slow the recursive crawl of the testsite to one page per 5 s, so a full crawl takes minutes
    // and the run is still collecting when the button is pressed.
    const limits = { rate: { requests_per_second_per_host: 0.2 } };
    const fullCrawl = testsiteRecursivePageCount();
    const rules = await publishTestsiteRules(
      request,
      registry as string,
      "e2e-cancel-rules",
      "slow testsite collection cancelled from the admin",
    );
    const sourceId = uniqueId("e2e-cancel-src");
    const taskId = uniqueId("e2e-cancel-task");

    await admin.goto("/sources/new");
    await admin.getByLabel("Ідентифікатор (source_id)").fill(sourceId);
    await admin.getByLabel("Назва").fill(`E2E cancel ${sourceId}`);
    await admin.getByLabel("URL").fill(`${TESTSITE_URL}/`);
    await admin.getByLabel("Пакет правил (package_id)").fill(rules.package_id);
    await admin.getByLabel("Версія", { exact: true }).fill(rules.version);
    await admin.getByRole("button", { name: "Створити джерело" }).click();
    await expect(admin).toHaveURL(new RegExp(`/sources/${sourceId}$`));

    await admin.goto("/tasks/new");
    await admin.getByLabel("Ідентифікатор (task_id)").fill(taskId);
    await admin.getByLabel("Назва").fill(`E2E cancel ${taskId}`);
    await admin.getByLabel("Джерело (source_id)").fill(sourceId);
    await admin.getByRole("textbox", { name: "Ліміти завдання" }).fill(JSON.stringify(limits));
    await expect(admin.getByText("Відповідає схемі контракту")).toBeVisible();
    const created = await captureRequest(admin, "POST", "/api/orchestrator/v1/tasks", () =>
      admin.getByRole("button", { name: "Створити завдання" }).click(),
    );
    expect(created.body).toMatchObject({ task_id: taskId, input: { source_id: sourceId }, limits });
    await expect(admin).toHaveURL(new RegExp(`/tasks/${taskId}$`));
    await admin.getByRole("tab", { name: "Ефективні ліміти" }).click();
    const rate = admin
      .getByRole("table", { name: "Ефективні ліміти" })
      .getByRole("row")
      .filter({ hasText: "rate.requests_per_second_per_host" })
      .getByRole("cell");
    await expect(rate.nth(1)).toHaveText("0.2");
    await expect(rate.nth(2)).toHaveText("task");

    await admin.getByRole("tab", { name: "Запуски" }).click();
    await admin.getByLabel("Причина").fill("e2e slow collection to cancel");
    await admin.getByLabel("Тестовий режим (без запису в робочі дані)").check();
    const started = await captureRequest(admin, "POST", `/api/orchestrator/v1/tasks/${taskId}/runs`, () =>
      admin.getByRole("button", { name: "Запустити" }).click(),
    );
    expect(started.body).toEqual({ reason: "e2e slow collection to cancel", test_mode: true });
    await expect(admin).toHaveURL(/\/runs\/run_/);
    const runId = admin.url().split("/").at(-1) as string;
    const runUrl = `${orchestratorUrl}/v1/runs/${runId}`;

    // In progress for real: the orchestrator started a collection and the collector fetches testsite pages.
    let collectionId = "";
    await expect
      .poll(
        async () => {
          const run = await jsonRequest(request, "get", runUrl);
          collectionId = typeof run["collection_id"] === "string" ? run["collection_id"] : "";
          return `${String(run["status"])}:${collectionId ? "collecting" : "-"}`;
        },
        { timeout: 60_000 },
      )
      .toBe("running:collecting");
    const collectionUrl = `${collector as string}/v1/collections/${collectionId}`;
    await expect
      .poll(
        async () => {
          const collection = await jsonRequest(request, "get", collectionUrl);
          const fetched = (collection["stats"] as { fetched?: number } | undefined)?.fetched ?? 0;
          return `${String(collection["status"])}:${fetched > 0 ? "fetching" : "-"}`;
        },
        { timeout: 60_000 },
      )
      .toBe("running:fetching");
    expect((await jsonRequest(request, "get", collectionUrl))["effective_limits"]).toMatchObject(limits);

    const status = admin
      .locator(".kv-row")
      .filter({ has: admin.locator("dt", { hasText: /^Стан$/ }) })
      .locator(".badge");
    await admin.getByRole("tab", { name: "Помилки колектора" }).click();
    await expect(admin.getByText(`Помилки й пропуски збору ${collectionId}`)).toBeVisible({
      timeout: 30_000,
    });
    await expect(status).toHaveText("running");
    await admin.getByRole("button", { name: "Скасувати запуск" }).click();
    await admin.getByLabel("Причина: Скасувати запуск").fill("e2e stop test run");
    const cancelled = await captureRequest(admin, "POST", `/api/orchestrator/v1/runs/${runId}/cancel`, () =>
      admin.getByRole("button", { name: "Скасувати", exact: true }).click(),
    );
    expect(cancelled.body).toEqual({ reason: "e2e stop test run" });
    // 202 = cancellation accepted for a run that is still in progress (200 would mean it had already ended).
    const response = await cancelled.request.response();
    expect(response?.status()).toBe(202);
    expect(((await response?.json()) as { status: string }).status).toBe("cancelling");
    await expect(admin.getByText(/Скасування:/)).toContainText("cancelling");

    await expect
      .poll(async () => (await jsonRequest(request, "get", runUrl))["status"], { timeout: 60_000 })
      .toBe("cancelled");
    await expect
      .poll(async () => (await jsonRequest(request, "get", collectionUrl))["status"], { timeout: 60_000 })
      .toBe("cancelled");
    const stopped = await jsonRequest(request, "get", collectionUrl);
    expect(stopped["finished_at"]).toBeTruthy();
    const fetched = (stopped["stats"] as { fetched: number }).fetched;
    expect(fetched).toBeGreaterThan(0);
    expect(fetched, "the collection stopped before a full crawl").toBeLessThan(fullCrawl);
    await expect(status).toHaveText("cancelled", { timeout: 30_000 });
    await expect(admin.getByRole("button", { name: "Скасувати запуск" })).toHaveCount(0);
    await expect(admin.getByRole("alert")).toHaveCount(0);
  });

  test("platform limits and connections: saved with If-Match; secrets only as references; audit trail", async ({
    admin,
  }) => {
    await admin.goto("/limits");
    await expect(admin.getByText("Відповідає схемі контракту")).toBeVisible();
    const limits = await captureRequest(admin, "PUT", "/api/orchestrator/v1/limits/platform", () =>
      admin.getByRole("button", { name: "Зберегти ліміти платформи" }).click(),
    );
    expect(limits.request.headers()["if-match"]).toBeTruthy();
    await expect(admin.getByText("Збережено")).toBeVisible();

    const connectionId = uniqueId("e2e-conn");
    await admin.goto("/connections");
    await admin.getByRole("button", { name: "Нове підключення" }).click();
    await admin.getByLabel("connection_id").fill(connectionId);
    await admin.getByLabel("Тип").last().fill("filesystem");
    await admin.getByRole("button", { name: "Додати посилання" }).click();
    await admin.getByLabel("Ім'я секрету 1").fill("token");
    // an open value instead of a reference is refused before anything is sent
    await admin.getByLabel("Посилання на секрет 1").fill("plain-token-value");
    await expect(admin.getByLabel("Помилки підключення")).toContainText(
      "очікується посилання env:, file: або vault:",
    );
    await expect(admin.getByRole("button", { name: "Зберегти й синхронізувати" })).toBeDisabled();
    await admin.getByLabel("Посилання на секрет 1").fill("env:JANE_SECRET_E2E_TOKEN");
    const savedConnection = await captureRequest(
      admin,
      "PUT",
      `/api/orchestrator/v1/connections/${connectionId}`,
      () => admin.getByRole("button", { name: "Зберегти й синхронізувати" }).click(),
    );
    expect(savedConnection.body["secret_refs"]).toEqual({ token: "env:JANE_SECRET_E2E_TOKEN" });
    await expect(admin.getByText("синхронізація з виконавцями — асинхронна")).toBeVisible();
    await admin.getByRole("button", { name: "Закрити" }).click();
    await admin.reload();
    const table = admin.getByRole("table", { name: "Підключення" });
    await expect(table).toContainText(connectionId);
    await expect(table).toContainText("env:JANE_SECRET_E2E_TOKEN");
    // the asynchronous sync reaches the storage executor (the list is polled by reloading)
    const connectionRow = table.getByRole("row", { name: new RegExp(connectionId) });
    await expect(async () => {
      await admin.reload();
      await expect(connectionRow).toContainText(/storage:\s*synced/, { timeout: 1_000 });
    }).toPass({ timeout: 30_000 });
    // the executor resolves the reference in ITS environment: not set there -> unresolved; no value is shown
    await connectionRow.getByRole("button", { name: connectionId }).click();
    const connectionExecutors = admin.getByRole("table", { name: "Виконавці підключення" });
    const storageExecutor = connectionExecutors.getByRole("row", { name: /^storage\b/ });
    await expect(storageExecutor).toContainText("synced");
    const [tested] = await Promise.all([
      admin.waitForResponse(
        (r) =>
          r.request().method() === "POST" &&
          r.url().endsWith(`/api/storage/v1/connections/${connectionId}/test`),
      ),
      storageExecutor.getByRole("button", { name: "Перевірити" }).click(),
    ]);
    expect(tested.status()).toBe(200);
    const testResult = admin.getByLabel("Результат перевірки підключення");
    await expect(testResult).toContainText("Перевірка підключення не вдалася");
    await expect(
      testResult.getByRole("table", { name: "Розв'язання секретів" }).getByRole("row", { name: /token/ }),
    ).toContainText("failed");
    await admin.getByRole("button", { name: "Закрити" }).click();

    await admin.goto("/audit");
    await expect(admin.getByRole("table", { name: "Події аудиту" })).toContainText(connectionId);
    await expect(admin.getByRole("alert")).toHaveCount(0);
  });

  test("dashboard shows the executors known to the orchestrator and their state", async ({ admin }) => {
    await admin.goto("/");
    const executors = admin.getByRole("table", { name: "Виконавці" });
    await expect(executors.getByRole("row")).not.toHaveCount(1);
    await expect(executors.locator(".badge").first()).toHaveText(/ok|degraded|down|unknown/);
  });
});
