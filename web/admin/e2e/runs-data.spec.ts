import { captureRequest, expect, test } from "./fixtures";

const RUN = "run_01J9ZQ3F8W2N4K7T5B6C1D0E9F";

test.describe("runs, progress, costs, cancellation, reprocessing, materials, results @mock", () => {
  test("run: stage progress, LLM costs, cancel with reason", async ({ admin }) => {
    await admin.goto("/runs");
    await admin.getByRole("link", { name: RUN }).click();
    await expect(admin.getByRole("heading", { name: `Запуск ${RUN}` })).toBeVisible();
    await expect(admin.getByTestId("run-cost")).toHaveText("0.42 USD");
    const progress = admin.getByRole("table", { name: "Прогрес етапів" });
    await expect(progress).toContainText("extract-products");
    await expect(progress).toContainText("shop-example.product-extractor@1.2.0");
    await expect(progress.getByRole("columnheader", { name: "unrecognized" })).toBeVisible();

    await admin.getByRole("button", { name: "Скасувати запуск" }).click();
    await admin.getByLabel("Причина: Скасувати запуск").fill("wrong limits");
    const { body } = await captureRequest(admin, "POST", `/api/orchestrator/v1/runs/${RUN}/cancel`, () =>
      admin.getByRole("button", { name: "Скасувати", exact: true }).click(),
    );
    expect(body).toEqual({ reason: "wrong limits" });
  });

  test("run: failed items with trace links and collector errors", async ({ admin }) => {
    await admin.goto(`/runs/${RUN}`);
    await admin.getByRole("tab", { name: "Елементи й помилки" }).click();
    const items = admin.getByRole("table", { name: "Елементи запуску" });
    await expect(items).toContainText("unrecognized");
    await items.getByRole("link", { name: "web:9b1f0c1d2e3f40516273849a0b1c2d3e" }).click();
    await expect(admin.getByRole("heading", { name: /Простежуваність/ })).toBeVisible();
    await expect(admin.getByRole("table", { name: /Етапи obs_/ })).toContainText(
      "jane.storage-postgresql@1.0.0",
    );

    await admin.goto(`/runs/${RUN}`);
    await admin.getByRole("tab", { name: "Помилки колектора" }).click();
    const errors = admin.getByRole("table", { name: "Помилки колектора" });
    await expect(errors).toContainText("disallowed by robots.txt");
    await expect(errors).toContainText("source_unavailable");
  });

  test("reprocessing of stored RAW from a stage", async ({ admin }) => {
    await admin.goto(`/runs/${RUN}`);
    await admin.getByRole("tab", { name: "Повторна обробка" }).click();
    await admin.getByLabel("Сховище RAW (connection_id)").fill("raw-files");
    await admin.getByLabel("Почати з етапу").fill("extract-products");
    await admin.getByLabel("Збережені з (RFC 3339)").fill("2026-09-20T00:00:00Z");
    const { request, body } = await captureRequest(admin, "POST", "/api/orchestrator/v1/reprocessing", () =>
      admin.getByRole("button", { name: "Обробити повторно" }).click(),
    );
    expect(request.headers()["idempotency-key"]).toBeTruthy();
    expect(body).toEqual({
      task_id: "shop-catalog",
      stored_materials: { storage_connection_id: "raw-files", since: "2026-09-20T00:00:00Z" },
      from_stage: "extract-products",
    });
    await expect(admin).toHaveURL(/\/runs\/job_/);
  });

  test("materials: stored RAW shown as text (data, not markup), trace, reprocess one material", async ({
    admin,
  }) => {
    await admin.goto("/materials");
    await admin.getByLabel("Сховище (connection_id)").fill("raw-files");
    const table = admin.getByRole("table", { name: "Збережені матеріали" });
    await expect(table).toContainText("https://shop.example.test/product/a-100");
    await table.getByRole("button", { name: "Переглянути" }).click();
    const preview = admin.getByTestId("content-preview");
    await expect(preview).toContainText("<title>Kettle A-100</title>");
    expect(await admin.locator("title", { hasText: "Kettle A-100" }).count()).toBe(0);
    await table.getByRole("button", { name: "Повторно обробити" }).click();
    await admin.getByLabel("Завдання").fill("shop-catalog");
    const { body } = await captureRequest(admin, "POST", "/api/orchestrator/v1/reprocessing", () =>
      admin.getByRole("button", { name: "Обробити повторно" }).click(),
    );
    expect(body["stored_materials"]).toEqual({
      storage_connection_id: "raw-files",
      material_ids: ["web:9b1f0c1d2e3f40516273849a0b1c2d3e"],
    });
  });

  test("results: entity state and history with late (stale) fields", async ({ admin }) => {
    await admin.goto("/results?connection_id=results-pg&entity_type=product");
    const table = admin.getByRole("table", { name: "Сутності" });
    await expect(table).toContainText("Kettle A-100");
    await table.getByRole("button", { name: "Історія" }).click();
    const history = admin.getByRole("table", { name: "Історія сутності" });
    await expect(history).toContainText("price");
    await expect(history.locator(".badge-warn")).toHaveText("price");
  });

  test("dashboard: executors, recent runs, costs", async ({ admin }) => {
    await admin.goto("/");
    await expect(admin.getByRole("table", { name: "Виконавці" })).toContainText("handler-runtime");
    await expect(admin.getByRole("table", { name: "Виконавці" })).toContainText("degraded");
    await expect(admin.getByTestId("usage-total")).toHaveText("0.42 USD");
    await expect(admin.getByRole("table", { name: "Останні запуски" })).toContainText(RUN);
  });
});
