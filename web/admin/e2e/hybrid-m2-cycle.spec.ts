import { readFileSync } from "node:fs";
import path from "node:path";
import { captureRequest, expect, realServiceUrl, test } from "./fixtures";
import {
  TESTSITE_URL as site,
  jsonRequest,
  publishExtractorPackage,
  publishTestsiteRules,
  uniqueId,
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

  const connections = JSON.parse(
    readFileSync(path.join(repo, "infra", "config", "storage-connections.json"), "utf8"),
  ) as { connections: Array<Record<string, unknown> & { connection_id: string }> };
  for (const connection of connections.connections)
    await jsonRequest(
      request,
      "put",
      `${orchestratorUrl}/v1/connections/${connection.connection_id}`,
      connection,
      [200, 201],
    );

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
  await expect
    .poll(
      async () => {
        const run = await jsonRequest(request, "get", `${orchestratorUrl}/v1/runs/${runId}`);
        return run["status"];
      },
      { timeout: 180_000 },
    )
    .toBe("succeeded");
  await admin.reload();
  await expect(admin.getByRole("table", { name: "Прогрес етапів" })).toContainText("store-raw");
  await admin.getByRole("tab", { name: "Елементи й помилки" }).click();
  await admin.getByLabel("Стан елемента").selectOption("");
  await expect(admin.getByRole("table", { name: "Елементи запуску" })).toContainText("extract-products");
  await admin.getByRole("tab", { name: "Помилки колектора" }).click();
  await expect(admin.getByRole("table", { name: "Помилки колектора" })).toContainText("404");

  await admin.goto(`/materials?connection_id=raw-files&source_id=${sourceId}`);
  const materials = admin.getByRole("table", { name: "Збережені матеріали" });
  await expect(materials).toContainText("testsite:8080");
  await materials.getByRole("button", { name: "Переглянути" }).first().click();
  await expect(admin.getByTestId("content-preview")).toContainText("<html");

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
});
