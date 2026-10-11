import { captureRequest, expect, realServiceUrl, selectCatalogOption, test } from "./fixtures";
import { jsonRequest, uniqueId } from "./seed";

// Screens against REAL services (WP-10 llm, WP-11 assistant) while the other neighbours stay contract mocks.
// Run: JANE_ADMIN_TARGET_LLM=http://127.0.0.1:<port> [JANE_ADMIN_TARGET_ASSISTANT=...] pnpm e2e --grep @hybrid
// The LLM budget uses a real task when Orchestrator is real, or the contract-mock task catalog otherwise.
test.describe("real llm and assistant services @hybrid", () => {
  test("LLM: providers, aliases, budget round-trip, usage", async ({ admin, request }) => {
    test.skip(!realServiceUrl("llm"), "JANE_ADMIN_TARGET_LLM / JANE_ADMIN_API_TARGET is not set");
    const orchestrator = realServiceUrl("orchestrator");
    const scope = orchestrator ? uniqueId("e2e-budget-task") : "shop-catalog";
    if (orchestrator) {
      const sourceId = uniqueId("e2e-budget-source");
      await jsonRequest(
        request,
        "post",
        `${orchestrator}/v1/sources`,
        {
          source_id: sourceId,
          kind: "web",
          title: sourceId,
          locator: { url: "https://example.test/" },
        },
        201,
      );
      await jsonRequest(
        request,
        "post",
        `${orchestrator}/v1/tasks`,
        {
          task_id: scope,
          title: scope,
          input: { source_id: sourceId },
          stages: [{ stage_id: "collect", kind: "collect", collector: { collector: "web" } }],
        },
        201,
      );
    }
    await admin.goto("/llm");
    const providers = admin.getByRole("table", { name: "Провайдери LLM" });
    await expect(providers).toBeVisible();
    await expect(admin.getByRole("alert")).toHaveCount(0);

    await admin.getByRole("tab", { name: "Псевдоніми моделей" }).click();
    await expect(
      admin.getByRole("table", { name: "Псевдоніми моделей" }).or(admin.getByText("Немає даних")),
    ).toBeVisible();

    await admin.getByRole("tab", { name: "Бюджети" }).click();
    await admin.getByLabel("Рівень").selectOption("task");
    await selectCatalogOption(admin, admin.getByLabel("Завдання", { exact: true }), scope);
    await admin.getByLabel("Сума").fill("1.5");
    const saved = await captureRequest(admin, "PUT", `/api/llm/v1/budgets/task/${scope}`, () =>
      admin.getByRole("button", { name: "Зберегти бюджет" }).click(),
    );
    expect(saved.body).toMatchObject({
      scope_type: "task",
      scope_id: scope,
      budget: { amount: 1.5, currency: "USD" },
    });
    const budgets = admin.getByRole("table", { name: "Бюджети LLM" });
    await expect(budgets).toContainText(scope);
    await budgets
      .getByRole("row", { name: new RegExp(scope) })
      .getByRole("button", { name: "Прибрати" })
      .click();
    await admin
      .getByRole("dialog", { name: "Прибрати", exact: true })
      .getByRole("button", { name: "Підтвердити", exact: true })
      .click();
    await expect(budgets.or(admin.getByText("Немає даних"))).not.toContainText(scope);

    await admin.getByRole("tab", { name: "Витрати" }).click();
    await expect(
      admin.getByRole("table", { name: "Витрати LLM" }).or(admin.getByText("Немає даних")),
    ).toBeVisible();
    await expect(admin.getByRole("alert")).toHaveCount(0);
  });

  test("assistant: onboarding job is accepted and its state is shown", async ({ admin }) => {
    test.skip(!realServiceUrl("assistant"), "JANE_ADMIN_TARGET_ASSISTANT / JANE_ADMIN_API_TARGET is not set");
    await admin.goto("/assistant");
    await admin.getByLabel("Назва або посилання").fill("https://shop.example.test/");
    await admin.getByLabel("Тип джерела (необов'язково)").fill("web");
    await admin.getByLabel("Бюджет дослідження").fill("0.5");
    const [response] = await Promise.all([
      admin.waitForResponse(
        (r) => r.request().method() === "POST" && r.url().endsWith("/api/assistant/v1/onboarding-sessions"),
      ),
      admin.getByRole("button", { name: "Почати підключення" }).click(),
    ]);
    expect(response.status()).toBe(202);
    const panel = admin.getByLabel("Підключення джерела");
    await expect(panel).toBeVisible();
    await expect(panel.locator(".badge")).toHaveText(/У черзі|Виконується|Успішно|Помилка|Скасовано/);
    // The real job links to its session (links.session): the session view opens with a live status.
    await expect(admin.getByRole("heading", { name: /^Сесія onb_/ })).toBeVisible();
    await expect(
      admin
        .getByRole("region", { name: /^Сесія onb_/ })
        .locator(".badge")
        .first(),
    ).toBeVisible();
  });
});
