import { captureRequest, expect, fulfillJson, mockUrl, preferExample, test } from "./fixtures";

test.describe("problem groups, improvement, unknown materials, assistant sessions @mock", () => {
  test("problem groups: filter unresolved, improve on problem samples across all bindings", async ({
    admin,
    request,
  }) => {
    // Contract example of a group, with a stored sample (stored_object_id is a documented ProblemGroup field).
    const groups = await (await request.get(`${mockUrl("orchestrator")}/v1/problem-groups`)).json();
    groups.items[0].samples[0].stored_object_id = "obj_01J9ZQ4C00000000000000D9";
    await fulfillJson(admin, "/api/orchestrator/v1/problem-groups", groups);
    await preferExample(admin, "/api/orchestrator/v1/tasks", "byPackage");

    await admin.goto("/problems");
    await expect(admin.getByRole("table", { name: "Групи проблем" })).toBeVisible();
    const [listed] = await Promise.all([
      admin.waitForRequest(
        (r) =>
          new URL(r.url()).pathname === "/api/orchestrator/v1/problem-groups" &&
          new URL(r.url()).searchParams.get("status") === "unresolved",
      ),
      admin.getByLabel("Стан групи").selectOption("unresolved"),
    ]);
    expect(new URL(listed.url()).searchParams.get("status")).toBe("unresolved");
    const table = admin.getByRole("table", { name: "Групи проблем" });
    await expect(table).toContainText("missing-selector:.price");
    await table.getByRole("button", { name: "Відкрити" }).click();

    await admin.getByLabel("Сховище RAW прикладів").fill("raw-files");
    const [improve, patch] = await Promise.all([
      admin.waitForRequest(
        (r) => r.method() === "POST" && r.url().includes("/api/assistant/v1/improvement-runs"),
      ),
      admin.waitForRequest(
        (r) => r.method() === "PATCH" && r.url().includes("/api/orchestrator/v1/problem-groups/pg_"),
      ),
      admin.getByRole("button", { name: "Запустити вдосконалення" }).click(),
    ]);
    expect(JSON.parse(improve.postData() ?? "{}")).toEqual({
      package: { package_id: "shop-example.product-extractor", version: "1.2.0" },
      source_id: "shop-example",
      problem_group_id: "pg_01J9ZW0000000000000000001",
      problem_samples: [
        { material_ref: { storage_connection_id: "raw-files", object_id: "obj_01J9ZQ4C00000000000000D9" } },
      ],
      bindings: [{ task_id: "shop-catalog", stage_id: "extract-products" }],
      policy: { approval: "manual", allow_fork: true },
    });
    expect(patch.headers()["content-type"]).toContain("application/merge-patch+json");
    expect(JSON.parse(patch.postData() ?? "{}")).toEqual({
      status: "in_progress",
      assistant_job_id: "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
    });
    await expect(admin.getByLabel("Вдосконалення")).toBeVisible();

    const ignore = await captureRequest(admin, "PATCH", "/api/orchestrator/v1/problem-groups/pg_", () =>
      admin.getByRole("button", { name: "Ігнорувати" }).click(),
    );
    expect(ignore.body).toEqual({ status: "ignored" });
  });

  test("improvement result: unresolved outcome and suggestion to extend expected data types", async ({
    admin,
    request,
  }) => {
    const groups = await (await request.get(`${mockUrl("orchestrator")}/v1/problem-groups`)).json();
    groups.items[0].status = "unresolved";
    groups.items[0].assistant_job_id = "job_imp_unresolved";
    await fulfillJson(admin, "/api/orchestrator/v1/problem-groups", groups);
    await fulfillJson(admin, "/api/assistant/v1/jobs/job_imp_unresolved", {
      job_id: "job_imp_unresolved",
      kind: "improvement",
      status: "succeeded",
      created_at: "2026-09-27T10:00:00Z",
      finished_at: "2026-09-27T10:05:00Z",
      result: {
        outcome: "unresolved",
        attempts: 3,
        unresolved_reason: "price is rendered by JavaScript",
        suggested_entity_types: ["offer"],
        costs: { amount: 0.31, currency: "USD" },
      },
    });
    await admin.goto("/problems");
    await admin
      .getByRole("table", { name: "Групи проблем" })
      .getByRole("button", { name: "Відкрити" })
      .click();
    await expect(admin.getByText("потрібне рішення людини")).toBeVisible();
    const result = admin.getByLabel("Результат вдосконалення");
    await expect(result).toContainText("price is rendered by JavaScript");
    await expect(result).toContainText("offer");
  });

  test("unknown materials are listed with the LLM forwarding state", async ({ admin }) => {
    await admin.goto("/problems?tab=unknown");
    const table = admin.getByRole("table", { name: "Невідомі матеріали" });
    await expect(table).toContainText("https://shop.example.test/gift-cards");
    await expect(table).toContainText("forward_unknown_to_llm=false");
  });

  test("assistant: onboarding by name, disambiguation, proposals with coverage, cost and risks, acceptance", async ({
    admin,
  }) => {
    await admin.goto("/assistant");
    await admin.getByLabel("Назва або посилання").fill("Shop Example kettles");
    await admin.getByLabel("Очікувані типи даних").fill("product");
    await admin.getByLabel("Бюджет дослідження").fill("2");
    const start = await captureRequest(admin, "POST", "/api/assistant/v1/onboarding-sessions", () =>
      admin.getByRole("button", { name: "Почати підключення" }).click(),
    );
    expect(start.request.headers()["idempotency-key"]).toBeTruthy();
    expect(start.body).toEqual({
      query: "Shop Example kettles",
      expected_entity_types: ["product"],
      limits: { budget: { amount: 2, currency: "USD", period: "total" } },
      auto_activation: false,
    });

    await admin.getByLabel("Відкрити сесію за ідентифікатором").fill("onb_01J9ZY0000000000000000001");
    await admin.getByRole("button", { name: "Відкрити", exact: true }).click();
    const candidates = admin.getByRole("table", { name: "Кандидати джерела" });
    await expect(candidates).toContainText("Shop Example Outlet");
    const select = await captureRequest(admin, "POST", "/candidate-selection", () =>
      candidates.getByRole("button", { name: "Обрати" }).first().click(),
    );
    expect(select.body).toEqual({ candidate_id: "cand_1" });

    await preferExample(
      admin,
      "/api/assistant/v1/onboarding-sessions/onb_01J9ZY0000000000000000001",
      "proposals",
    );
    await admin.reload();
    await admin.getByRole("button", { name: "onb_01J9ZY0000000000000000001" }).click();
    const proposal = admin.getByTestId("proposal-p1");
    await expect(proposal).toContainText("рекомендовано");
    await expect(proposal).toContainText("Sitemap / Sitemap Index");
    await expect(proposal).toContainText("~18000 матеріалів");
    await expect(proposal).toContainText("0.31 USD");
    await expect(proposal.getByLabel("Ризики")).toContainText("sitemap may omit discontinued products");
    await expect(proposal.getByRole("table", { name: "Екстрактори варіанта" })).toContainText(
      "прив'язати наявний",
    );

    await admin.getByLabel("source_id для джерела").fill("shop-example");
    const accept = await captureRequest(admin, "POST", "/proposals/p1/acceptance", () =>
      proposal.getByRole("button", { name: "Прийняти варіант" }).click(),
    );
    expect(accept.body).toEqual({ activate: false, source_id: "shop-example" });
    await expect(admin.getByLabel("Застосування варіанта")).toBeVisible();
  });
});
