import { captureRequest, expect, fulfillJson, mockUrl, openapiExample, test } from "./fixtures";

const PKG = "shop-example.product-extractor";
const JOB = "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F";

test.describe("packages, versions, tests without writes, diff, forks, upstream, code editor @mock", () => {
  test("version: run tests (test_mode, no writes) and see the report; approve with an audit reason", async ({
    admin,
  }) => {
    // The mock job never finishes; a finished job carries the TestReport from contracts/examples.
    await fulfillJson(admin, `/api/handler-runtime/v1/jobs/${JOB}`, {
      job_id: JOB,
      kind: "test_run",
      status: "succeeded",
      created_at: "2026-09-27T10:10:00Z",
      finished_at: "2026-09-27T10:10:03Z",
      result: openapiExample("test-report"),
    });
    await admin.goto("/packages");
    await admin.getByRole("link", { name: PKG }).click();
    await admin.getByRole("tab", { name: "Версії й тести" }).click();
    await admin.getByRole("button", { name: "1.2.0" }).click();
    await expect(admin.getByRole("table", { name: "Файли версії" })).toContainText(
      "src/product_extractor/main.py",
    );

    const run = await captureRequest(admin, "POST", "/api/handler-runtime/v1/test-runs", () =>
      admin.getByRole("button", { name: "Запустити тести (без запису)" }).click(),
    );
    expect(run.body).toMatchObject({ handler: { package_id: PKG, version: "1.2.0" }, tests: "all" });
    const report = admin.getByTestId("job-panel").getByLabel("Звіт тестів");
    await expect(report).toContainText("problem-sample-2026-09-26");
    await expect(report).toContainText("/entities/0/fields/price");

    await admin.getByRole("button", { name: "Погодити", exact: true }).click();
    await admin.getByLabel("Причина: Погодити").fill("tests passed on all bindings");
    const approve = await captureRequest(
      admin,
      "POST",
      `/api/registry/v1/packages/${PKG}/versions/1.2.0/status`,
      () => admin.getByRole("button", { name: "Погодити версію" }).click(),
    );
    expect(approve.body).toEqual({ status: "approved", reason: "tests passed on all bindings" });
  });

  test("diff between versions", async ({ admin }) => {
    await admin.goto(`/packages/${PKG}`);
    await admin.getByRole("tab", { name: "Відмінності" }).click();
    await admin.getByLabel("Від (версія або parent:<версія>)").fill("1.1.0");
    const { request } = await captureRequest(admin, "GET", `/api/registry/v1/packages/${PKG}/diff`, () =>
      admin.getByRole("button", { name: "Порівняти" }).click(),
    );
    expect(new URL(request.url()).searchParams.get("from")).toBe("1.1.0");
    await expect(admin.locator(".diff-add")).toContainText("og_title(tree)");
    await expect(admin.locator(".diff-del")).toContainText("title = h1.text()");
    await expect(admin.getByRole("table", { name: "Зміни маніфесту" })).toContainText(
      "/provenance/change_summary",
    );
  });

  test("fork: independent copy; parent updates are visible and ported only on explicit command", async ({
    admin,
    request,
  }) => {
    await admin.goto(`/packages/${PKG}`);
    await admin.getByRole("tab", { name: "Створити форк" }).click();
    await admin.getByLabel("Новий package_id").fill("acme.product-extractor");
    const fork = await captureRequest(admin, "POST", `/api/registry/v1/packages/${PKG}/forks`, () =>
      admin.getByRole("button", { name: "Створити форк" }).click(),
    );
    expect(fork.body).toEqual({
      new_package_id: "acme.product-extractor",
      from_version: "1.2.0",
      auto_changes_allowed: false,
    });
    await expect(admin).toHaveURL(/\/packages\/acme\.product-extractor$/);

    // The fork as the registry describes it (forkPackage 201 example of the contract).
    const forked = await (
      await request.post(`${mockUrl("registry")}/v1/packages/${PKG}/forks`, {
        headers: { "Idempotency-Key": "e2e-fork" },
        data: { new_package_id: "acme.product-extractor", from_version: "1.2.0" },
      })
    ).json();
    await fulfillJson(admin, "/api/registry/v1/packages/acme.product-extractor", forked);
    const polled: string[] = [];
    admin.on("request", (r) => {
      if (r.method() !== "GET") polled.push(`${r.method()} ${new URL(r.url()).pathname}`);
    });
    await admin.reload();
    await admin.getByRole("tab", { name: "Оновлення батька" }).click();
    await expect(admin.getByTestId("newer-parent-versions")).toHaveText("1.3.0");
    // Nothing is ported automatically: only reads so far.
    expect(polled).toEqual([]);

    await admin.getByRole("button", { name: "Порівняти з батьком 1.3.0" }).click();
    await expect(admin.getByLabel("Відмінності версій")).toContainText("src/product_extractor/main.py");

    await admin.getByLabel("Версія батька").selectOption("1.3.0");
    await admin.getByLabel("Нова версія форку").fill("1.3.0");
    await admin.getByRole("button", { name: "Перенести зміни" }).click();
    const port = await captureRequest(
      admin,
      "POST",
      "/api/registry/v1/packages/acme.product-extractor/upstream-ports",
      () => admin.getByRole("button", { name: "Так, перенести в нову версію" }).click(),
    );
    expect(port.body).toEqual({ parent_version: "1.3.0", new_version: "1.3.0", base_version: "1.2.0" });
    await expect(admin.getByLabel("Перенесення змін батька")).toBeVisible();
  });

  test("code editor: edit, local diff, publish as a new draft version", async ({ admin }) => {
    await admin.goto(`/packages/${PKG}/versions/1.2.0/edit`);
    await expect(admin.getByRole("button", { name: "src/product_extractor/main.py" })).toBeVisible();
    const editor = admin.getByRole("textbox", { name: "Код src/product_extractor/main.py" });
    await editor.click();
    await admin.keyboard.press("Control+End");
    await admin.keyboard.type("\n# handle .price-new\n");
    await expect(admin.getByLabel("Локальні зміни")).toContainText("+# handle .price-new");
    await admin.getByLabel("Опис змін").fill("Support .price-new selector.");
    const { body } = await captureRequest(admin, "POST", `/api/registry/v1/packages/${PKG}/versions`, () =>
      admin.getByRole("button", { name: "Опублікувати як нову версію" }).click(),
    );
    const manifest = body["manifest"] as Record<string, unknown>;
    expect(manifest["version"]).toBe("1.2.1");
    expect(manifest["provenance"]).toEqual({
      created_by: "human",
      based_on: { package_id: PKG, version: "1.2.0" },
      change_summary: "Support .price-new selector.",
    });
    const files = body["files"] as Record<string, { encoding: string; data: string }>;
    expect(files["src/product_extractor/main.py"]?.data).toContain("# handle .price-new");
    expect(Object.keys(files)).not.toContain("jane-package.json");
    await expect(admin).toHaveURL(new RegExp(`/packages/${PKG}\\?version=`));
  });

  test("stage versions: activate an approved version and roll back, both audited", async ({ admin }) => {
    await admin.goto("/tasks/shop-catalog");
    await admin.getByRole("tab", { name: "Версії етапів" }).click();
    await expect(admin.getByTestId("current-extract-products")).toHaveText(`${PKG}@1.2.0`);
    await expect(admin.getByRole("table", { name: "Історія активацій extract-products" })).toContainText(
      "regression on category pages",
    );

    const card = admin.getByRole("region", { name: "Етап extract-products" });
    await card.getByLabel("Версія для extract-products").selectOption("1.2.0");
    await card.getByRole("button", { name: "Активувати" }).click();
    await card.getByLabel("Причина: Активувати").fill("tests passed on all bindings");
    const activate = await captureRequest(
      admin,
      "POST",
      "/api/orchestrator/v1/tasks/shop-catalog/stages/extract-products/activations",
      () => card.getByRole("button", { name: "Активувати версію" }).click(),
    );
    expect(activate.request.headers()["idempotency-key"]).toBeTruthy();
    expect(activate.body).toMatchObject({
      kind: "activate",
      package: { package_id: PKG, version: "1.2.0" },
      reason: "tests passed on all bindings",
    });
    await expect(card.getByText(/Активація: .*1\.1\.0.*→/)).toBeVisible();

    await card.getByRole("button", { name: "Відкотити" }).click();
    await card.getByLabel("Причина: Відкотити").fill("regression on category pages");
    const rollback = await captureRequest(
      admin,
      "POST",
      "/api/orchestrator/v1/tasks/shop-catalog/stages/extract-products/activations",
      () => card.getByRole("button", { name: "Відкотити до попередньої" }).click(),
    );
    expect(rollback.body).toEqual({ kind: "rollback", reason: "regression on category pages" });

    await admin.goto("/audit");
    await expect(admin.getByRole("table", { name: "Події аудиту" })).toContainText("stage.activate");
  });
});
