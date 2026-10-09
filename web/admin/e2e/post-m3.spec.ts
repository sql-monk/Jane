import {
  captureRequest,
  expect,
  fulfillJson,
  mockUrl,
  openapiExample,
  preferExample,
  test,
} from "./fixtures";

// WP-20 (post-M3) screens on the contract mocks: every neighbour answer is a contract example (served by
// contracts/tools/mock.py, `Prefer: example=<name>` selects a named one) or a contract example file.
const SESSION = "onb_01J9ZY0000000000000000001";
const SESSION_JOB = "job_01J9ZY0000000000000000JOB";
const IMPROVEMENT_JOB = "job_01J9ZW00000000000000IMPROV";
const RUN = "run_01J9ZQ3F8W2N4K7T5B6C1D0E9F";

test.describe("post-M3 admin (WP-20) @mock", () => {
  test("assistant: sessions come from the list API and survive a reload; nothing is kept in localStorage", async ({
    admin,
  }) => {
    const [listed] = await Promise.all([
      admin.waitForRequest(
        (r) => r.method() === "GET" && new URL(r.url()).pathname === "/api/assistant/v1/onboarding-sessions",
      ),
      admin.goto("/assistant"),
    ]);
    expect(new URL(listed.url()).searchParams.get("limit")).toBe("50");
    const sessions = admin.getByRole("table", { name: "Сесії підключення" });
    await expect(sessions).toContainText("https://tiny.example.test/");
    await expect(sessions.getByRole("row", { name: /tiny\.example\.test/ })).toContainText(
      "insufficient_sample",
    );
    await expect(sessions.getByRole("row", { name: /Shop Example kettles/ })).toContainText("0.31 USD");

    const [filtered] = await Promise.all([
      admin.waitForRequest(
        (r) =>
          new URL(r.url()).pathname === "/api/assistant/v1/onboarding-sessions" &&
          new URL(r.url()).searchParams.getAll("status").join() === "proposals_ready",
      ),
      admin.getByLabel("Стан сесії").selectOption("proposals_ready"),
    ]);
    expect(new URL(filtered.url()).searchParams.getAll("status")).toEqual(["proposals_ready"]);

    // the latest job of the session is the acceptance; after a reload its result (drafts) is shown again
    await preferExample(admin, `/api/assistant/v1/onboarding-sessions/${SESSION}`, "proposals");
    await preferExample(admin, `/api/assistant/v1/jobs/${SESSION_JOB}`, "acceptanceSucceeded");
    await sessions.getByRole("button", { name: SESSION }).click();
    await expect(admin).toHaveURL(new RegExp(`[?&]session=${SESSION}`));
    await expect(admin.getByRole("heading", { name: `Сесія ${SESSION}` })).toBeVisible();
    await admin.reload();
    const view = admin.getByRole("region", { name: `Сесія ${SESSION}` });
    await expect(view.getByTestId("proposal-p1")).toContainText("рекомендовано");
    const last = view.getByLabel("Останній job сесії");
    await expect(last).toContainText(SESSION_JOB);
    await expect(last.getByLabel("Результат застосування")).toContainText("shop-example.rules@1.0.0");
    await expect(last.getByRole("button", { name: "Створити джерело з чернетки" })).toBeVisible();
    const stored = await admin.evaluate(() => JSON.stringify({ ...window.localStorage }));
    expect(stored).toBe("{}");
  });

  test("assistant: min_onboarding_confidence of the assistant is shown and can be set for one onboarding", async ({
    admin,
  }) => {
    await preferExample(admin, "/api/assistant/v1/info", "assistantCi");
    await preferExample(admin, "/api/assistant/v1/onboarding-sessions", "onboarding", "POST");
    const [info] = await Promise.all([
      admin.waitForResponse((r) => new URL(r.url()).pathname === "/api/assistant/v1/info"),
      admin.goto("/assistant"),
    ]);
    expect(await info.json()).toEqual(openapiExample("assistant-info-ci"));
    await expect(admin.getByTestId("min-onboarding-confidence")).toHaveText("80%");
    await expect(admin.getByRole("region", { name: "Ліміти дослідження" })).toContainText("0.01 USD / day");

    await admin.getByLabel("Назва або посилання").fill("Shop Example kettles");
    await admin.getByLabel("Поріг впевненості вибірки").fill("0.9");
    const start = await captureRequest(admin, "POST", "/api/assistant/v1/onboarding-sessions", () =>
      admin.getByRole("button", { name: "Почати підключення" }).click(),
    );
    expect(start.body).toEqual({
      query: "Shop Example kettles",
      limits: { min_onboarding_confidence: 0.9 },
      auto_activation: false,
    });
    // Job.labels.session_id of the 202 opens the session and puts it into the URL
    await expect(admin).toHaveURL(new RegExp(`[?&]session=${SESSION}`));
    await expect(admin.getByRole("heading", { name: `Сесія ${SESSION}` })).toBeVisible();
  });

  test("improvement runs: list with filters, result with the proposal (files, manifest, diff)", async ({
    admin,
  }) => {
    await admin.goto("/assistant");
    await admin.getByRole("tab", { name: "Запуски вдосконалення" }).click();
    const runs = admin.getByRole("table", { name: "Запуски вдосконалення" });
    const row = runs.getByRole("row", { name: new RegExp(IMPROVEMENT_JOB) });
    await expect(row).toContainText("new_version");
    await expect(row).toContainText("shop-example.product-extractor@1.2.1");
    await expect(row).toContainText("pg_01J9ZW0000000000000000001");
    const [filtered] = await Promise.all([
      admin.waitForRequest(
        (r) =>
          new URL(r.url()).pathname === "/api/assistant/v1/improvement-runs" &&
          new URL(r.url()).searchParams.get("package_id") === "shop-example.product-extractor",
      ),
      admin.getByLabel("Пакет (package_id)").fill("shop-example.product-extractor"),
    ]);
    expect(new URL(filtered.url()).searchParams.get("package_id")).toBe("shop-example.product-extractor");
    const [byStatus] = await Promise.all([
      admin.waitForRequest(
        (r) =>
          new URL(r.url()).pathname === "/api/assistant/v1/improvement-runs" &&
          new URL(r.url()).searchParams.getAll("status").join() === "succeeded",
      ),
      admin.getByLabel("Стан job").selectOption("succeeded"),
    ]);
    expect(new URL(byStatus.url()).searchParams.get("package_id")).toBe("shop-example.product-extractor");

    // the run's job: the package forbids automatic changes -> proposal only (assistant.v1 example)
    await preferExample(admin, `/api/assistant/v1/jobs/${IMPROVEMENT_JOB}`, "improvementProposalOnly");
    await row.getByRole("button", { name: IMPROVEMENT_JOB }).click();
    await expect(admin).toHaveURL(new RegExp(`[?&]job=${IMPROVEMENT_JOB}`));
    const result = admin.getByLabel("Вдосконалення", { exact: true }).getByLabel("Результат вдосконалення");
    await expect(result).toContainText("proposal_only");
    await expect(result).toContainText("shop-example.product-extractor@1.2.1 (не опубліковано)");
    await expect(result.getByRole("link", { name: "shop-example.product-extractor@1.2.1" })).toHaveCount(0);
    const proposal = result.getByLabel("Пропозиція асистента");
    await expect(proposal).toContainText("shop-example.product-extractor@1.2.0");
    await expect(proposal).toContainText("Support the .price-new selector.");
    const files = proposal.getByRole("table", { name: "Змінені файли пропозиції" });
    await expect(files).toContainText("src/product_extractor/main.py");
    await expect(files).toContainText("tests/problem-p1/expected.json");
    await files
      .getByRole("row", { name: /main\.py/ })
      .getByText("показати")
      .click();
    await expect(proposal.getByLabel("Вміст src/product_extractor/main.py")).toContainText("price(?:-new)?");
    await expect(proposal).toContainText("tests/problem-p1/material.json");
    const diff = proposal.getByLabel("Diff пропозиції");
    await expect(diff.locator(".diff-add")).toContainText("price(?:-new)?");
    await expect(diff.locator(".diff-del")).toContainText('class="price"');
    await proposal.getByText("Маніфест запропонованої версії").click();
    await expect(proposal.getByTestId("json-view")).toContainText('"origin": "problem_sample"');

    // after a reload the chosen run is open again (URL), its result is read from the assistant
    await admin.reload();
    await expect(
      admin.getByLabel("Вдосконалення", { exact: true }).getByLabel("Пропозиція асистента"),
    ).toBeVisible();
  });

  test("problem group: the note is saved with merge-patch and shown", async ({ admin }) => {
    await admin.goto("/problems");
    await admin
      .getByRole("table", { name: "Групи проблем" })
      .getByRole("button", { name: "Відкрити" })
      .click();

    // note (PATCH merge-patch; the contract answer is the group with its note)
    await admin.getByLabel("Примітка до групи").fill("waits for the new price selector");
    const saved = await captureRequest(admin, "PATCH", "/api/orchestrator/v1/problem-groups/pg_", () =>
      admin.getByRole("button", { name: "Зберегти примітку" }).click(),
    );
    expect(saved.request.headers()["content-type"]).toContain("application/merge-patch+json");
    expect(saved.body).toEqual({ note: "waits for the new price selector" });
    await expect(admin.getByTestId("group-note")).toHaveText(
      "version shop-example.product-extractor@1.2.1 awaits manual approval",
    );
    await expect(
      admin.getByRole("table", { name: "Групи проблем" }).getByRole("columnheader", { name: "Примітка" }),
    ).toBeVisible();
  });

  test("problem group: assistant runs of the group, reprocessing of exactly the sample RAW", async ({
    admin,
    request,
  }) => {
    const groups = await (await request.get(`${mockUrl("orchestrator")}/v1/problem-groups`)).json();
    groups.items[0].samples[0].stored_object_id = "obj_01J9ZQ4C00000000000000D9";
    await fulfillJson(admin, "/api/orchestrator/v1/problem-groups", groups);
    await preferExample(admin, "/api/orchestrator/v1/tasks", "byPackage");
    await admin.goto("/problems");
    await admin
      .getByRole("table", { name: "Групи проблем" })
      .getByRole("button", { name: "Відкрити" })
      .click();

    // assistant runs of this group (GET /v1/improvement-runs?problem_group_id=...)
    const runs = admin.getByRole("table", { name: "Запуски асистента для групи" });
    await expect(runs).toContainText(IMPROVEMENT_JOB);
    await runs.getByRole("button", { name: IMPROVEMENT_JOB }).click();
    await expect(admin.getByLabel("Вдосконалення", { exact: true })).toContainText(IMPROVEMENT_JOB);

    // reprocessing of exactly the stored RAW of the samples (stored_materials.object_ids)
    await admin.getByLabel("Сховище RAW прикладів").fill("raw-files");
    await admin.getByRole("button", { name: "Підготувати повторну обробку прикладів" }).click();
    const form = admin.getByRole("form", { name: "Повторна обробка" });
    await expect(form).toContainText("obj_01J9ZQ4C00000000000000D9");
    await expect(form.getByLabel("Завдання")).toHaveValue("shop-catalog");
    await form.getByLabel("Почати з етапу").fill("extract-products");
    await form.getByRole("checkbox", { name: /Тестовий режим/ }).check();
    const reprocess = await captureRequest(admin, "POST", "/api/orchestrator/v1/reprocessing", () =>
      form.getByRole("button", { name: "Обробити повторно" }).click(),
    );
    expect(reprocess.request.headers()["idempotency-key"]).toBeTruthy();
    expect(reprocess.body).toEqual({
      task_id: "shop-catalog",
      stored_materials: { storage_connection_id: "raw-files", object_ids: ["obj_01J9ZQ4C00000000000000D9"] },
      from_stage: "extract-products",
      test_mode: true,
    });
    await expect(admin).toHaveURL(/\/runs\/job_/);
  });

  test("run items and trace: attempt history and available_at (R25 diagnostics)", async ({ admin }) => {
    await admin.goto(`/runs/${RUN}`);
    await admin.getByRole("tab", { name: "Елементи й помилки" }).click();
    const items = admin.getByRole("table", { name: "Елементи запуску" });
    const retrying = items.getByRole("row", { name: /web:0a1b2c3d4e5f60718293a4b5c6d7e8f9/ });
    await expect(retrying).toContainText("retrying");
    await expect(retrying).toContainText("2026-09-27 10:00:09.512Z");
    await expect(retrying).toContainText("Помилка елемента (upstream_unavailable)");
    await retrying.getByText("2 подій").click();
    const history = retrying.getByLabel("Історія спроб itm_01J9ZQ4B0000000000000002");
    await expect(history.getByRole("listitem")).toHaveCount(2);
    await expect(history.getByRole("listitem").nth(1)).toContainText(
      "retry_scheduled 2026-09-27 10:00:06.512Z, спроба 1, доступний з 2026-09-27 10:00:09.512Z, затримка 3000 мс, код upstream_unavailable",
    );

    await items.getByRole("link", { name: "web:9b1f0c1d2e3f40516273849a0b1c2d3e" }).click();
    const stages = admin.getByRole("table", { name: /Етапи obs_/ });
    const extract = stages.getByRole("row", { name: /extract-products/ });
    await expect(extract).toContainText("completed");
    await extract.getByText("4 подій").click();
    const traced = extract.getByLabel("Історія спроб itm_01J9ZQ4B0000000000000001");
    await expect(traced.getByRole("listitem")).toHaveCount(4);
    await expect(traced.getByRole("listitem").nth(2)).toContainText(
      "claimed 2026-09-27 10:00:09.530Z, спроба 2",
    );
  });

  test("reprocessing: exact stored RAW or observation from the materials page, exact ids on the run page", async ({
    admin,
    request,
  }) => {
    // the first stored object of the storage.v1 listObjects contract example
    const listed = await (
      await request.get(`${mockUrl("storage")}/v1/objects?connection_id=raw-files`)
    ).json();
    const first = listed.items[0] as {
      object: { object_id: string };
      material: { material_id: string; observation_id: string };
    };
    await admin.goto("/materials?connection_id=raw-files");
    const table = admin.getByRole("table", { name: "Збережені матеріали" });
    await table.getByRole("button", { name: "Повторно обробити" }).first().click();
    const form = admin.getByRole("form", { name: "Повторна обробка" });
    await expect(form.getByLabel("Що обробити").locator("option")).toHaveText([
      "усі збережені спостереження матеріалу (material_ids)",
      "лише цей збережений RAW (object_ids)",
      "лише це спостереження матеріалу (observation_ids)",
    ]);
    await form.getByLabel("Завдання").fill("shop-catalog");
    await form.getByLabel("Що обробити").selectOption("object");
    const exact = await captureRequest(admin, "POST", "/api/orchestrator/v1/reprocessing", () =>
      form.getByRole("button", { name: "Обробити повторно" }).click(),
    );
    expect(exact.body).toEqual({
      task_id: "shop-catalog",
      stored_materials: { storage_connection_id: "raw-files", object_ids: [first.object.object_id] },
    });

    await admin.goto("/materials?connection_id=raw-files");
    await table.getByRole("button", { name: "Повторно обробити" }).first().click();
    await form.getByLabel("Завдання").fill("shop-catalog");
    await form.getByLabel("Що обробити").selectOption("observation");
    const observation = await captureRequest(admin, "POST", "/api/orchestrator/v1/reprocessing", () =>
      form.getByRole("button", { name: "Обробити повторно" }).click(),
    );
    expect(observation.body).toEqual({
      task_id: "shop-catalog",
      stored_materials: {
        storage_connection_id: "raw-files",
        material_ids: [first.material.material_id],
        observation_ids: [first.material.observation_id],
      },
    });

    await admin.goto(`/runs/${RUN}`);
    await admin.getByRole("tab", { name: "Повторна обробка" }).click();
    await admin.getByLabel("Сховище RAW (connection_id)").fill("raw-files");
    await admin.getByLabel("Точний вибір: RAW object_ids").fill("obj_01J9ZQ4C00000000000000D1, obj_2");
    await admin.getByLabel("Точний вибір: observation_ids").fill("obs_01J9ZQ4A0000000000000001");
    const ids = await captureRequest(admin, "POST", "/api/orchestrator/v1/reprocessing", () =>
      admin.getByRole("button", { name: "Обробити повторно" }).click(),
    );
    expect(ids.body).toEqual({
      task_id: "shop-catalog",
      stored_materials: {
        storage_connection_id: "raw-files",
        object_ids: ["obj_01J9ZQ4C00000000000000D1", "obj_2"],
        observation_ids: ["obs_01J9ZQ4A0000000000000001"],
      },
    });
  });

  test("package version: test summary of every context (registry test_summary)", async ({ admin }) => {
    await admin.goto("/packages/shop-example.product-extractor?version=1.2.0");
    await expect(admin.getByTestId("test-summary-status")).toHaveText("passed");
    const contexts = admin.getByRole("table", { name: "Тести за контекстами" });
    const binding = contexts.getByRole("row", { name: /bindings:shop-catalog\/extract-products/ });
    await expect(binding).toContainText("passed");
    await expect(binding).toContainText("assistant");
    await expect(contexts.getByRole("row", { name: /^tests/ })).toContainText("handler-runtime@0.1.0");
  });

  test("stage versions: collector rules of a collect stage are activated and rolled back with audit", async ({
    admin,
    request,
  }) => {
    // Approved versions of the rules package: the registry list example with the identity of the rules manifest.
    const rules = openapiExample<{ package_id: string; version: string }>("manifest-rules");
    const versions = await (
      await request.get(`${mockUrl("registry")}/v1/packages/${rules.package_id}/versions?status=approved`)
    ).json();
    versions.items = versions.items
      .slice(0, 1)
      .map((v: Record<string, unknown>) => ({ ...v, package_id: rules.package_id, version: rules.version }));
    await fulfillJson(admin, `/api/registry/v1/packages/${rules.package_id}/versions`, versions);

    await admin.goto("/tasks/shop-catalog");
    await admin.getByRole("tab", { name: "Версії етапів" }).click();
    const card = admin.getByRole("region", { name: "Етап collect" });
    await expect(card.getByTestId("current-collect")).toHaveText(`${rules.package_id}@${rules.version}`);
    await expect(card.getByLabel("Пакет для collect").locator("option").first()).toHaveText(
      `${rules.package_id} (поточний)`,
    );
    await card.getByLabel("Версія для collect").selectOption(rules.version);
    await card.getByRole("button", { name: "Активувати" }).click();
    await card.getByLabel("Причина: Активувати").fill("rules with the feed strategy");
    const activate = await captureRequest(
      admin,
      "POST",
      "/api/orchestrator/v1/tasks/shop-catalog/stages/collect/activations",
      () => card.getByRole("button", { name: "Активувати версію" }).click(),
    );
    expect(activate.request.headers()["idempotency-key"]).toBeTruthy();
    expect(activate.body).toMatchObject({
      kind: "activate",
      package: { package_id: rules.package_id, version: rules.version },
      reason: "rules with the feed strategy",
    });
    await card.getByRole("button", { name: "Відкотити" }).click();
    await card.getByLabel("Причина: Відкотити").fill("back to the previous rules");
    const rollback = await captureRequest(
      admin,
      "POST",
      "/api/orchestrator/v1/tasks/shop-catalog/stages/collect/activations",
      () => card.getByRole("button", { name: "Відкотити до попередньої" }).click(),
    );
    expect(rollback.body).toEqual({ kind: "rollback", reason: "back to the previous rules" });
    await expect(card.getByRole("table", { name: "Історія активацій collect" })).toBeVisible();
  });
});
