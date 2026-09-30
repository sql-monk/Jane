import { captureRequest, expect, expectNoSecretLeak, fulfillJson, mockUrl, test } from "./fixtures";

// Values that must never reach the screen even if a service returned them by mistake.
const LEAKED = ["pg-password-LEAK-1", "tg-bot-token-LEAK-2", "Bearer eyLEAKLEAKLEAK3"];

test.describe("connections, LLM, limits and secrets @mock", () => {
  test("connections show only secret references and sync state", async ({ admin }) => {
    await admin.goto("/connections");
    const table = admin.getByRole("table", { name: "Підключення" });
    await expect(table).toContainText("env:RESULTS_PG_PASSWORD");
    await expect(table).toContainText("synced");
  });

  test("secret values returned by a faulty service are never displayed", async ({ admin, request }) => {
    const list = await (await request.get(`${mockUrl("orchestrator")}/v1/connections`)).json();
    const connection = list.items[0].connection;
    connection.params.password = LEAKED[0];
    connection.params.headers = { Authorization: LEAKED[2] };
    connection.secret_refs.bot_token = LEAKED[1];
    await fulfillJson(admin, "/api/orchestrator/v1/connections", list);
    await fulfillJson(admin, "/api/orchestrator/v1/connections/results-pg", list.items[0]);
    await admin.goto("/connections");
    await expect(admin.getByRole("table", { name: "Підключення" })).toContainText("env:RESULTS_PG_PASSWORD");
    await expectNoSecretLeak(admin, LEAKED);
    await admin.getByRole("button", { name: "results-pg" }).click();
    await expect(admin.getByLabel("connection_id")).toHaveValue("results-pg");
    await expectNoSecretLeak(admin, LEAKED);
    for (const input of await admin.locator("input").all()) {
      const value = await input.inputValue();
      for (const secret of LEAKED) expect(value).not.toContain(secret);
    }
  });

  test("connection editor accepts only secret references; test shows resolution state without values", async ({
    admin,
  }) => {
    await admin.goto("/connections");
    await admin.getByRole("button", { name: "Нове підключення" }).click();
    await admin.getByLabel("connection_id").fill("results-pg");
    await admin.getByRole("button", { name: "Додати посилання" }).click();
    await admin.getByLabel("Ім'я секрету 1").fill("password");
    await admin.getByLabel("Посилання на секрет 1").fill("hunter2-plain-value");
    await expect(admin.getByLabel("Помилки підключення")).toContainText(
      "очікується посилання env:, file: або vault:",
    );
    await expect(admin.getByRole("button", { name: "Зберегти й синхронізувати" })).toBeDisabled();

    await admin.getByLabel("Посилання на секрет 1").fill("env:RESULTS_PG_PASSWORD");
    const { body } = await captureRequest(admin, "PUT", "/api/orchestrator/v1/connections/results-pg", () =>
      admin.getByRole("button", { name: "Зберегти й синхронізувати" }).click(),
    );
    expect(body).toEqual({
      connection_id: "results-pg",
      kind: "postgresql",
      params: {},
      secret_refs: { password: "env:RESULTS_PG_PASSWORD" },
    });
    await expect(admin.getByText("синхронізація з виконавцями — асинхронна")).toBeVisible();

    await fulfillJson(
      admin,
      "/api/storage/v1/connections/results-pg/test",
      {
        ok: false,
        checked_at: "2026-09-27T10:00:00Z",
        secrets_resolved: { username: true, password: false },
        message: "environment variable RESULTS_PG_PASSWORD is not set",
      },
      "POST",
    );
    await admin
      .getByRole("table", { name: "Виконавці підключення" })
      .getByRole("button", { name: "Перевірити" })
      .click();
    const result = admin.getByLabel("Результат перевірки підключення");
    await expect(result).toContainText("Перевірка підключення не вдалася");
    await expect(result.getByRole("table", { name: "Розв'язання секретів" })).toContainText("password");
  });

  test("LLM: providers via connections, budgets, usage", async ({ admin }) => {
    await admin.goto("/llm");
    await expect(admin.getByRole("table", { name: "Провайдери LLM" })).toContainText("fake-deterministic-1");
    await admin.getByRole("tab", { name: "Бюджети" }).click();
    await expect(admin.getByRole("table", { name: "Бюджети LLM" })).toContainText("news-tg-events");
    await admin.getByLabel("Рівень").selectOption("task");
    await admin.getByLabel("Ідентифікатор").fill("shop-price-check");
    await admin.getByLabel("Сума").fill("3");
    const { body } = await captureRequest(admin, "PUT", "/api/llm/v1/budgets/task/shop-price-check", () =>
      admin.getByRole("button", { name: "Зберегти бюджет" }).click(),
    );
    expect(body).toEqual({
      scope_type: "task",
      scope_id: "shop-price-check",
      budget: { amount: 3, currency: "USD", period: "day" },
    });
    await admin.getByRole("tab", { name: "Витрати" }).click();
    await expect(admin.getByTestId("usage-total")).toHaveText("0.42 USD");
  });

  test("limits: platform defaults and hard caps are edited without code; effective limits show provenance", async ({
    admin,
  }) => {
    await admin.goto("/limits");
    await expect(admin.getByRole("heading", { name: /профіль dev-laptop/ })).toBeVisible();
    await expect(admin.getByText("Відповідає схемі контракту")).toBeVisible();
    const { body } = await captureRequest(admin, "PUT", "/api/orchestrator/v1/limits/platform", () =>
      admin.getByRole("button", { name: "Зберегти ліміти платформи" }).click(),
    );
    expect(body["profile"]).toBe("dev-laptop");
    await admin.getByLabel("Завдання").fill("shop-catalog");
    await admin.getByLabel("Етап").fill("extract-products");
    await admin.getByRole("button", { name: "Показати" }).click();
    const effective = admin.getByRole("table", { name: "Ефективні ліміти" });
    await expect(effective).toContainText("sandbox.memory_mb");
    await expect(effective).toContainText("stage");
  });
});
