import { test, expect, mockUrl, fulfillJson } from "./fixtures";
import type { Run } from "../src/api/types";

test.describe("run diagnostics and honest result context @mock", () => {
  test("shows distinct business counts, includes successful items and links only confirmed storage scope", async ({
    admin,
    request,
    apiRequests,
  }) => {
    const sample = (await (await request.get(`${mockUrl("orchestrator")}/v1/runs/run_review`)).json()) as Run;
    const run: Run = {
      ...sample,
      run_id: "run_review",
      status: "succeeded",
      counters: { materials: 6 },
      summary: {
        basis: "recorded_handler_outputs",
        complete: true,
        extracted_entities: 3,
        saved_records: 3,
        result_groups: [
          { connection_id: "results-pg", entity_type: "product", scope: "shop-example", count: 3 },
        ],
      },
    };
    await fulfillJson(admin, "/api/orchestrator/v1/runs/run_review", run);
    await admin.goto("/runs/run_review");
    await expect(admin.getByRole("heading", { name: "Результат ланцюжка" })).toBeVisible();
    await expect(admin.getByText("Зібрано матеріалів", { exact: true })).toBeVisible();
    await expect(admin.getByText("Розібрано унікальних сутностей", { exact: true })).toBeVisible();
    await expect(admin.getByText(/Там можуть бути результати інших запусків/)).toBeVisible();
    const result = admin.getByRole("link", { name: "Товари · shop-example · results-pg", exact: true });
    await expect(result).toHaveAttribute(
      "href",
      "/results?connection_id=results-pg&entity_type=product&scope=shop-example",
    );
    await admin.getByRole("tab", { name: "Елементи й помилки" }).click();
    await expect(admin.getByLabel("Стан елемента", { exact: true })).toHaveValue("");
    await expect(admin.getByRole("table", { name: "Елементи запуску" })).toBeVisible();
    const itemRequests = apiRequests.filter((call) => new URL(call.url()).pathname.endsWith("/items"));
    expect(itemRequests.length).toBeGreaterThan(0);
    expect(itemRequests.every((call) => !new URL(call.url()).searchParams.has("status"))).toBe(true);
    await result.click();
    await expect(admin).toHaveURL(
      /\/results\?connection_id=results-pg&entity_type=product&scope=shop-example$/,
    );
  });

  test("historical incomplete traces show unavailable business counts", async ({ admin, request }) => {
    const sample = await (await request.get(`${mockUrl("orchestrator")}/v1/runs/run_review`)).json();
    await fulfillJson(admin, "/api/orchestrator/v1/runs/run_review", {
      ...sample,
      run_id: "run_review",
      counters: { materials: 6 },
      summary: { basis: "recorded_handler_outputs", complete: false, legacy_trace: true, result_groups: [] },
    });
    await admin.goto("/runs/run_review");
    await expect(
      admin.getByRole("region", { name: "Результат ланцюжка" }).getByText("Недоступно", { exact: true }),
    ).toHaveCount(2);
    await expect(admin.getByText(/історичне трасування було обрізане/)).toBeVisible();
  });
});
