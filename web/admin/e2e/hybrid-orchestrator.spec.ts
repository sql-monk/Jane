import { API_KEY, captureRequest, expect, realServiceUrl, test } from "./fixtures";
import { uniqueId } from "./seed";

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
    await admin.getByRole("button", { name: "Скасувати запуск" }).click();
    await admin.getByLabel("Причина: Скасувати запуск").fill("e2e stop test run");
    const cancelled = await captureRequest(
      admin,
      "POST",
      /\/api\/orchestrator\/v1\/runs\/run_[^/]+\/cancel/,
      () => admin.getByRole("button", { name: "Скасувати", exact: true }).click(),
    );
    expect(cancelled.body).toEqual({ reason: "e2e stop test run" });
    await expect(admin.getByText(/Скасування:/)).toBeVisible();
    await expect
      .poll(
        async () => {
          const response = await admin.request.get(
            `${realServiceUrl("orchestrator")}/v1/runs/${admin.url().split("/").at(-1)}`,
            {
              headers: { Authorization: `Bearer ${API_KEY}` },
            },
          );
          expect(response.ok(), await response.text()).toBeTruthy();
          return ((await response.json()) as { status: string }).status;
        },
        { timeout: 60_000 },
      )
      .toBe("cancelled");
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
    await admin.getByLabel("Посилання на секрет 1").fill("env:JANE_SECRET_E2E_TOKEN");
    await admin.getByRole("button", { name: "Зберегти й синхронізувати" }).click();
    await expect(admin.getByText("синхронізація з виконавцями — асинхронна")).toBeVisible();
    await admin.getByRole("button", { name: "Закрити" }).click();
    await admin.reload();
    const table = admin.getByRole("table", { name: "Підключення" });
    await expect(table).toContainText(connectionId);
    await expect(table).toContainText("env:JANE_SECRET_E2E_TOKEN");

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
