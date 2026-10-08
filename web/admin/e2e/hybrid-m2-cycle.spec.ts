import path from "node:path";
import { captureRequest, expect, realServiceUrl, test } from "./fixtures";
import {
  TESTSITE_URL as site,
  jsonRequest,
  publishExtractorPackage,
  approvePackage,
  htmlMaterial,
  publishTestsiteRules,
  runItems,
  storageInvoke,
  syncStorageConnections,
  uniqueId,
  waitRun,
} from "./seed";

const repo = path.resolve(import.meta.dirname, "..", "..", "..");

// One isolated end-to-end browser scenario: real Caddy, Registry, Collector, Orchestrator,
// Handler Runtime and Storage. The testsite and package fixtures are deterministic local inputs.
test("real M2 cycle: source, package, task, collection, materials, errors, fork activation and rollback @hybrid", async ({
  admin,
  request,
}) => {
  test.setTimeout(300_000);
  const registry = realServiceUrl("registry");
  const orchestrator = realServiceUrl("orchestrator");
  const storage = realServiceUrl("storage");
  const collector = realServiceUrl("collector");
  test.skip(!registry || !orchestrator || !storage || !collector, "Full real API stack is required");
  const registryUrl = registry as string;
  const orchestratorUrl = orchestrator as string;
  const sourceId = uniqueId("e2e-m2-source");
  const taskId = uniqueId("e2e-m2-task");
  const rules = await publishTestsiteRules(
    request,
    registryUrl,
    "e2e-m2-rules",
    "M2 deterministic local testsite rules",
  );
  const rulesId = rules.package_id;

  const extractorDir = path.join(repo, "libs", "extractor-sdk", "examples", "testsite-product-extractor");
  const extractor = await publishExtractorPackage(request, registryUrl, extractorDir);
  await jsonRequest(
    request,
    "post",
    `${registryUrl}/v1/packages/${extractor.package_id}/versions/1.0.0/status`,
    {
      status: "approved",
      reason: "M2 real browser acceptance fixture",
    },
  );
  const forkId = `${extractor.package_id}-fork`;
  await jsonRequest(
    request,
    "post",
    `${registryUrl}/v1/packages/${extractor.package_id}/forks`,
    {
      new_package_id: forkId,
      from_version: "1.0.0",
      auto_changes_allowed: false,
    },
    201,
  );
  const forkVersion = await jsonRequest(
    request,
    "get",
    `${registryUrl}/v1/packages/${forkId}/versions/1.0.0`,
  );
  if (forkVersion["status"] !== "approved")
    await jsonRequest(request, "post", `${registryUrl}/v1/packages/${forkId}/versions/1.0.0/status`, {
      status: "approved",
      reason: "M2 real browser fork activation fixture",
    });

  await admin.goto("/sources/new");
  await admin.getByLabel("Ідентифікатор (source_id)").fill(sourceId);
  await admin.getByLabel("Назва").fill(`M2 testsite ${sourceId}`);
  await admin.getByLabel("URL").fill(`${site}/`);
  await admin.getByLabel("Пакет правил (package_id)").fill(rulesId);
  await admin.getByLabel("Версія", { exact: true }).fill("1.0.0");
  const createdSource = await captureRequest(admin, "POST", "/api/orchestrator/v1/sources", () =>
    admin.getByRole("button", { name: "Створити джерело" }).click(),
  );
  expect(createdSource.body["collector_rules"]).toEqual({ package_id: rulesId, version: "1.0.0" });
  await expect(admin).toHaveURL(new RegExp(`/sources/${sourceId}$`));

  await syncStorageConnections(request, orchestratorUrl);

  const task = {
    task_id: taskId,
    title: `M2 real cycle ${taskId}`,
    input: { source_id: sourceId, urls: [`${site}/product/phone-alpha`, `${site}/missing-page`] },
    stages: [
      { stage_id: "collect", kind: "collect", collector: { collector: "web", mode: "full" } },
      {
        stage_id: "store-raw",
        kind: "handler",
        handler: { package_id: "jane.storage-files", version: "1.0.0" },
        connections: { target: "raw-files" },
        inputs: [{ from: "collect" }],
      },
      {
        stage_id: "extract-products",
        kind: "handler",
        handler: { package_id: extractor.package_id, version: extractor.version, digest: extractor.digest },
        inputs: [
          { from: "collect", when: { field: "material.format.media_type", op: "eq", value: "text/html" } },
        ],
        bindings: [{ url_patterns: [{ value: "*/product/*" }] }],
      },
      {
        stage_id: "store-products",
        kind: "handler",
        handler: { package_id: "jane.storage-postgresql", version: "1.0.0" },
        connections: { target: "results-pg" },
        inputs: [
          {
            from: "extract-products",
            select: "output",
            when: { field: "result.status", op: "eq", value: "success" },
          },
        ],
      },
    ],
  };
  await jsonRequest(request, "post", `${orchestratorUrl}/v1/tasks`, task, 201);
  await admin.goto(`/tasks/${taskId}`);
  await admin.getByRole("tab", { name: "Ланцюжок" }).click();
  for (const stage of task.stages)
    await expect(admin.getByTestId(`dag-node-${stage.stage_id}`)).toBeVisible();
  await admin.getByRole("tab", { name: "Запуски" }).click();
  await admin.getByLabel("Причина").fill("M2 real testsite collection");
  const started = await captureRequest(admin, "POST", `/api/orchestrator/v1/tasks/${taskId}/runs`, () =>
    admin.getByRole("button", { name: "Запустити" }).click(),
  );
  expect(started.request.headers()["idempotency-key"]).toBeTruthy();
  await expect(admin).toHaveURL(/\/runs\/run_/);
  const runId = admin.url().split("/").at(-1) as string;
  const run = await waitRun(request, orchestratorUrl, runId);
  expect(run["status"], JSON.stringify(run)).toBe("succeeded");
  const extracted = (await runItems(request, orchestratorUrl, runId)).filter(
    (i) => i.stage_id === "extract-products",
  );
  expect(extracted.map((i) => i.result_status)).toEqual(["success"]);
  const materialId = extracted[0]?.material_id as string;
  const observationId = extracted[0]?.observation_id as string;
  await admin.reload();
  await expect(admin.getByRole("table", { name: "Прогрес етапів" })).toContainText("store-raw");
  await admin.getByRole("tab", { name: "Елементи й помилки" }).click();
  await admin.getByLabel("Стан елемента").selectOption("");
  const runItemsTable = admin.getByRole("table", { name: "Елементи запуску" });
  await expect(runItemsTable).toContainText("extract-products");
  // trace link of a run item -> every stage of the material in this run, with package versions and outputs
  await runItemsTable
    .getByRole("row", { name: /extract-products/ })
    .getByRole("link", { name: materialId })
    .click();
  await expect(admin.getByRole("heading", { name: `Простежуваність ${materialId}` })).toBeVisible();
  const traced = admin.getByRole("table", { name: `Етапи ${observationId} (${runId})` });
  await expect(traced.getByRole("row", { name: /store-raw/ })).toContainText("jane.storage-files@1.0.0");
  await expect(traced.getByRole("row", { name: /store-raw/ })).toContainText("stored_object");
  await expect(traced.getByRole("row", { name: /extract-products/ })).toContainText(
    `${extractor.package_id}@${extractor.version}`,
  );
  await expect(traced.getByRole("row", { name: /store-products/ })).toContainText("results-pg");
  await admin.goto(`/runs/${runId}`);
  await admin.getByRole("tab", { name: "Помилки колектора" }).click();
  await expect(admin.getByRole("table", { name: "Помилки колектора" })).toContainText("404");

  // reprocessing of the stored RAW from a stage (run page): RAW stored since this run, from extract-products on
  await admin.getByRole("tab", { name: "Повторна обробка" }).click();
  const reprocessForm = admin.getByRole("form", { name: "Повторна обробка" });
  await expect(reprocessForm.getByLabel("Завдання")).toHaveValue(taskId);
  await reprocessForm.getByLabel("Сховище RAW (connection_id)").fill("raw-files");
  await reprocessForm.getByLabel("Почати з етапу").fill("extract-products");
  await reprocessForm.getByLabel("Збережені з (RFC 3339)").fill(run["created_at"] as string);
  await reprocessForm.getByLabel("Причина").fill("M2 reprocess stored RAW of the run");
  const [stageReprocess, stageAccepted] = await Promise.all([
    captureRequest(admin, "POST", "/api/orchestrator/v1/reprocessing", () =>
      reprocessForm.getByRole("button", { name: "Обробити повторно" }).click(),
    ),
    admin.waitForResponse(
      (r) => r.request().method() === "POST" && r.url().endsWith("/api/orchestrator/v1/reprocessing"),
    ),
  ]);
  expect(stageReprocess.request.headers()["idempotency-key"]).toBeTruthy();
  expect(stageReprocess.body).toEqual({
    task_id: taskId,
    stored_materials: { storage_connection_id: "raw-files", since: run["created_at"] },
    from_stage: "extract-products",
    reason: "M2 reprocess stored RAW of the run",
  });
  expect(stageAccepted.status()).toBe(202);
  const stageJob = (await stageAccepted.json()) as { job_id: string };
  await expect(admin).toHaveURL(new RegExp(`/runs/${stageJob.job_id}$`));
  const stageRun = await waitRun(request, orchestratorUrl, stageJob.job_id);
  expect(stageRun["status"], JSON.stringify(stageRun)).toBe("succeeded");
  expect(stageRun["trigger"]).toBe("reprocess");
  const stageRunItems = await runItems(request, orchestratorUrl, stageJob.job_id);
  expect(stageRunItems.filter((i) => i.stage_id === "store-raw")).toEqual([]); // starts at extract-products
  expect(
    stageRunItems
      .filter((i) => i.stage_id !== "collect")
      .map((i) => [i.stage_id, i.material_id, i.observation_id, i.result_status]),
  ).toEqual([
    ["extract-products", materialId, observationId, "success"],
    ["store-products", materialId, observationId, "success"],
  ]);
  await admin.reload();
  await expect(admin.getByText("reprocess", { exact: true })).toBeVisible();
  await expect(
    admin.getByRole("table", { name: "Прогрес етапів" }).getByRole("row", { name: /extract-products/ }),
  ).toContainText(`${extractor.package_id}@${extractor.version}`);

  // materials: the stored RAW as text, its trace (original run and the reprocessing), reprocessing of it alone
  await admin.goto(`/materials?connection_id=raw-files&source_id=${sourceId}`);
  const materials = admin.getByRole("table", { name: "Збережені матеріали" });
  await expect(materials).toContainText(`${site}/product/phone-alpha`);
  await expect(materials.getByRole("row")).toHaveCount(2);
  await materials.getByRole("button", { name: "Переглянути" }).click();
  await expect(admin.getByTestId("content-preview")).toContainText("<html");
  await materials.getByRole("link", { name: "Простежити" }).click();
  await expect(admin.getByRole("heading", { name: `Простежуваність ${materialId}` })).toBeVisible();
  await expect(admin.getByRole("table", { name: `Етапи ${observationId} (${runId})` })).toContainText(
    "store-raw",
  );
  await expect(
    admin.getByRole("table", { name: `Етапи ${observationId} (${stageJob.job_id})` }),
  ).toContainText("extract-products");
  await admin.goBack();

  await materials.getByRole("button", { name: "Повторно обробити" }).click();
  const oneForm = admin.getByRole("form", { name: "Повторна обробка" });
  await expect(oneForm).toContainText(materialId);
  await oneForm.getByLabel("Завдання").fill(taskId);
  await oneForm.getByLabel("Почати з етапу").fill("extract-products");
  await oneForm.getByLabel("Причина").fill("M2 reprocess one stored material from admin");
  const reprocessing = await captureRequest(admin, "POST", "/api/orchestrator/v1/reprocessing", () =>
    oneForm.getByRole("button", { name: "Обробити повторно" }).click(),
  );
  expect(reprocessing.request.headers()["idempotency-key"]).toBeTruthy();
  expect(reprocessing.body).toEqual({
    task_id: taskId,
    stored_materials: { storage_connection_id: "raw-files", material_ids: [materialId] },
    from_stage: "extract-products",
    reason: "M2 reprocess one stored material from admin",
  });
  await expect(admin).toHaveURL(/\/runs\/run_/);
  const reprocessRunId = admin.url().split("/").at(-1) as string;
  const oneRun = await waitRun(request, orchestratorUrl, reprocessRunId);
  expect(oneRun["status"], JSON.stringify(oneRun)).toBe("succeeded");
  // The selected material only, with its RAW of this source among the fed objects. The orchestrator does not
  // filter by the task's source, so RAW of the same URL stored by OTHER sources is fed too (WP-09 test below).
  const oneItems = (await runItems(request, orchestratorUrl, reprocessRunId)).filter(
    (i) => i.stage_id === "extract-products",
  );
  expect(oneItems.map((i) => i.observation_id)).toContain(observationId);
  for (const item of oneItems)
    expect([item.material_id, item.result_status]).toEqual([materialId, "success"]);
  await admin.reload();
  await expect(admin.getByRole("table", { name: "Прогрес етапів" })).toContainText("extract-products");

  await admin.goto(`/results?connection_id=results-pg&entity_type=product&scope=${sourceId}`);
  const products = admin.getByRole("table", { name: "Сутності" });
  await expect(products).toContainText("Phone Alpha");
  await expect(products).toContainText("299");

  await admin.goto(`/tasks/${taskId}`);
  await admin.getByRole("tab", { name: "Версії етапів" }).click();
  const stage = admin.getByRole("region", { name: "Етап extract-products" });
  await expect(stage.getByTestId("current-extract-products")).toContainText(extractor.package_id);
  await stage.getByLabel("Пакет для extract-products").selectOption(forkId);
  await stage.getByLabel("Версія для extract-products").selectOption("1.0.0");
  await stage.getByRole("button", { name: "Активувати" }).click();
  await stage.getByLabel("Причина: Активувати").fill("M2 switch to approved independent fork");
  const activation = await captureRequest(admin, "POST", /\/stages\/extract-products\/activations$/, () =>
    stage.getByRole("button", { name: "Активувати версію" }).click(),
  );
  expect(activation.body).toMatchObject({
    kind: "activate",
    package: { package_id: forkId, version: "1.0.0" },
  });
  await expect(stage.getByText(/Активація:/)).toContainText(forkId);
  await stage.getByRole("button", { name: "Відкотити" }).click();
  await stage.getByLabel("Причина: Відкотити").fill("M2 restore original package");
  const rollback = await captureRequest(admin, "POST", /\/stages\/extract-products\/activations$/, () =>
    stage.getByRole("button", { name: "Відкотити до попередньої" }).click(),
  );
  expect(rollback.body).toEqual({ kind: "rollback", reason: "M2 restore original package" });
  await expect(stage.getByText(/Відкат:/)).toContainText(extractor.package_id);
  await expect(stage.getByRole("table", { name: "Історія активацій extract-products" })).toContainText(
    forkId,
  );

  // both are in the audit log of the stage (who, what, which package)
  await admin.goto("/audit");
  await admin.getByLabel("Тип об'єкта").selectOption("stage");
  await admin.getByLabel("Об'єкт", { exact: true }).fill(`${taskId}/extract-products`);
  const audit = admin.getByRole("table", { name: "Події аудиту" });
  const activated = audit.getByRole("row", { name: /stage\.activate/ });
  await expect(activated).toContainText("M2 switch to approved independent fork");
  await expect(activated).toContainText(forkId);
  const rolledBack = audit.getByRole("row", { name: /stage\.rollback/ });
  await expect(rolledBack).toContainText("M2 restore original package");
  await expect(rolledBack).toContainText(extractor.package_id);
  await expect(audit.getByRole("row")).toHaveCount(3);
});

// «Повторно обробити» on ONE stored object must reprocess the RAW of the task's source only. The orchestrator
// used to filter the connection by `material_ids` alone (WP-09 `_feed_stored`, reported by WP-13 in
// docs/delivery/WP-13.md), feeding RAW of the same URL from another source into this task as well.
// The accepted WP-09 fix also filters by the task's source (storage.v1 listObjects accepts `source_id`).
test("reprocessing one stored material takes only RAW of the task's source (WP-09 defect) @hybrid", async ({
  admin,
  request,
}) => {
  test.setTimeout(180_000);
  const registry = realServiceUrl("registry");
  const orchestrator = realServiceUrl("orchestrator");
  const storage = realServiceUrl("storage");
  test.skip(!registry || !orchestrator || !storage, "Full real API stack is required");
  const [registryUrl, orchestratorUrl, storageUrl] = [registry, orchestrator, storage] as [
    string,
    string,
    string,
  ];
  await syncStorageConnections(request, orchestratorUrl);
  const extractor = await publishExtractorPackage(
    request,
    registryUrl,
    path.join(repo, "libs", "extractor-sdk", "examples", "testsite-product-extractor"),
  );
  await approvePackage(request, registryUrl, extractor, "WP-09 reprocessing filter fixture");
  // The same page (one material_id) stored as RAW by two sources.
  const ownSource = uniqueId("e2e-wp09-own");
  const otherSource = uniqueId("e2e-wp09-other");
  const url = `${site}/product/phone-alpha?wp09=${ownSource}`;
  const html = "<html><body><h1>Phone Alpha</h1></body></html>";
  for (const sourceId of [ownSource, otherSource])
    await storageInvoke(request, storageUrl, "raw-files", `${sourceId}-raw`, {
      kind: "material",
      material: htmlMaterial(sourceId, url, html, `obs_${sourceId}`, new Date().toISOString()),
    });
  await jsonRequest(
    request,
    "post",
    `${orchestratorUrl}/v1/sources`,
    { source_id: ownSource, kind: "web", title: `WP-09 ${ownSource}`, locator: { url: `${site}/` } },
    [200, 201],
  );
  const taskId = uniqueId("e2e-wp09-task");
  await jsonRequest(
    request,
    "post",
    `${orchestratorUrl}/v1/tasks`,
    {
      task_id: taskId,
      title: `WP-09 ${taskId}`,
      input: { source_id: ownSource, urls: [url] },
      stages: [
        { stage_id: "collect", kind: "collect", collector: { collector: "web", mode: "full" } },
        {
          stage_id: "extract-products",
          kind: "handler",
          handler: { package_id: extractor.package_id, version: extractor.version, digest: extractor.digest },
          inputs: [{ from: "collect" }],
        },
      ],
    },
    201,
  );

  await admin.goto(`/materials?connection_id=raw-files&source_id=${ownSource}`);
  const materials = admin.getByRole("table", { name: "Збережені матеріали" });
  await expect(materials.getByRole("row")).toHaveCount(2);
  await materials.getByRole("button", { name: "Повторно обробити" }).click();
  const form = admin.getByRole("form", { name: "Повторна обробка" });
  await form.getByLabel("Завдання").fill(taskId);
  await form.getByLabel("Почати з етапу").fill("extract-products");
  await form.getByRole("button", { name: "Обробити повторно" }).click();
  await expect(admin).toHaveURL(/\/runs\/run_/);
  const runId = admin.url().split("/").at(-1) as string;
  const run = await waitRun(request, orchestratorUrl, runId);
  expect(run["status"], JSON.stringify(run)).toBe("succeeded");
  const fed = (await runItems(request, orchestratorUrl, runId)).filter(
    (i) => i.stage_id === "extract-products",
  );
  // the set-up worked: the RAW of the task's own source was fed
  expect(fed.map((i) => i.observation_id)).toContain(`obs_${ownSource}`);
  expect(fed.map((i) => i.observation_id)).toEqual([`obs_${ownSource}`]);
});
