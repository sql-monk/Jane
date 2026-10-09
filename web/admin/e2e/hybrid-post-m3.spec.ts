import path from "node:path";
import type { APIRequestContext, Page } from "@playwright/test";
import { captureRequest, expect, realServiceUrl, test } from "./fixtures";
import { formatInstant } from "../src/lib/format";
import {
  E2E_PACKAGES_DIR,
  TESTSITE_URL,
  approvePackage,
  jsonRequest,
  publishPackage,
  publishTestsiteRules,
  runItems,
  seedFakeLlm,
  syncStorageConnections,
  uniqueId,
  waitRun,
} from "./seed";

const services = ["registry", "orchestrator", "storage", "collector", "llm", "assistant"] as const;
const url = (api: (typeof services)[number]) => realServiceUrl(api) as string;
interface RawObject {
  object: { object_id: string };
  material: { material_id: string; observation_id: string };
}

/** Real collector -> RAW -> extractor creates a problem sample and a successful control sample. */
async function problemRun(request: APIRequestContext) {
  const registry = url("registry");
  const orchestrator = url("orchestrator");
  await syncStorageConnections(request, orchestrator);
  const extractor = await publishPackage(
    request,
    registry,
    path.join(E2E_PACKAGES_DIR, "e2e.improvable-product-extractor"),
    "e2e-post-m3",
  );
  await approvePackage(request, registry, extractor, "post-M3 admin: human baseline");
  const rules = await publishTestsiteRules(request, registry, "e2e-post-m3-rules", "post-M3 admin rules");
  const sourceId = uniqueId("e2e-post-m3-source");
  const taskId = uniqueId("e2e-post-m3-task");
  await jsonRequest(
    request,
    "post",
    orchestrator + "/v1/sources",
    {
      source_id: sourceId,
      kind: "web",
      title: sourceId,
      locator: { url: TESTSITE_URL + "/" },
      collector_rules: rules,
    },
    201,
  );
  await jsonRequest(
    request,
    "post",
    orchestrator + "/v1/tasks",
    {
      task_id: taskId,
      title: taskId,
      input: {
        source_id: sourceId,
        urls: [TESTSITE_URL + "/product/phone-alpha", TESTSITE_URL + "/product/phone-gamma"],
      },
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
          inputs: [{ from: "collect" }],
        },
      ],
    },
    201,
  );
  const job = await jsonRequest(request, "post", orchestrator + "/v1/tasks/" + taskId + "/runs", {}, 202);
  const runId = job["job_id"] as string;
  expect((await waitRun(request, orchestrator, runId))["status"]).toBe("succeeded");
  const extracted = (await runItems(request, orchestrator, runId)).filter(
    (i) => i.stage_id === "extract-products",
  );
  expect(extracted.map((i) => i.result_status).sort()).toEqual(["success", "unrecognized"]);
  const problem = extracted.find((i) => i.result_status === "unrecognized")!;
  const objects = (
    await jsonRequest(
      request,
      "get",
      url("storage") + "/v1/objects?connection_id=raw-files&source_id=" + sourceId,
    )
  )["items"] as RawObject[];
  expect(objects).toHaveLength(2);
  const raw = objects.find((o) => o.material.observation_id === problem.observation_id)!;
  expect(raw.object.object_id).toBeTruthy();
  const groups = (
    await jsonRequest(request, "get", orchestrator + "/v1/problem-groups?source_id=" + sourceId)
  )["items"] as Array<{ group_id: string }>;
  expect(groups).toHaveLength(1);
  return { extractor, sourceId, taskId, runId, raw, groupId: groups[0]!.group_id };
}

async function openGroup(admin: Page, sourceId: string) {
  await admin.goto("/problems");
  await admin.getByLabel("Джерело").fill(sourceId);
  await admin
    .getByRole("table", { name: "Групи проблем" })
    .getByRole("row", { name: new RegExp(sourceId) })
    .getByRole("button", { name: "Відкрити" })
    .click();
}

/** Submit the UI form and prove that only the selected stored observation reached the extractor. */
async function reprocess(
  admin: Page,
  request: APIRequestContext,
  taskId: string,
  raw: RawObject,
  selection: Record<string, unknown>,
) {
  const form = admin.getByRole("form", { name: "Повторна обробка" });
  await form.getByLabel("Почати з етапу").fill("extract-products");
  const [sent, response] = await Promise.all([
    captureRequest(admin, "POST", "/api/orchestrator/v1/reprocessing", () =>
      form.getByRole("button", { name: "Обробити повторно" }).click(),
    ),
    admin.waitForResponse(
      (r) =>
        r.request().method() === "POST" && new URL(r.url()).pathname === "/api/orchestrator/v1/reprocessing",
    ),
  ]);
  expect(sent.request.headers()["idempotency-key"]).toBeTruthy();
  expect(sent.body).toEqual({
    task_id: taskId,
    from_stage: "extract-products",
    stored_materials: { storage_connection_id: "raw-files", ...selection },
  });
  expect(response.status()).toBe(202);
  const runId = ((await response.json()) as { job_id: string }).job_id;
  await expect(admin).toHaveURL(new RegExp("/runs/" + runId + "$"));
  expect((await waitRun(request, url("orchestrator"), runId))["status"]).toBe("succeeded");
  const items = await runItems(request, url("orchestrator"), runId);
  expect(items.filter((i) => i.stage_id === "store-raw")).toHaveLength(0);
  expect(
    items
      .filter((i) => i.stage_id === "extract-products")
      .map((i) => [i.material_id, i.observation_id, i.result_status]),
  ).toEqual([[raw.material.material_id, raw.material.observation_id, "unrecognized"]]);
}

// Real API and UI through Caddy; data are created through public APIs, no page.route or response fixtures.
// The external model used by the retry scenario is explicitly the deterministic fake provider of the real LLM gateway.
test.describe("remaining post-M3 admin coverage @hybrid", () => {
  test.beforeEach(() =>
    test.skip(
      services.some((s) => !realServiceUrl(s)),
      "Full real API stack is required",
    ),
  );

  test("human group note persists; group sample reprocessing sends exact object_ids", async ({
    admin,
    request,
  }) => {
    test.setTimeout(240_000);
    const data = await problemRun(request);
    await openGroup(admin, data.sourceId);
    const note = "Human decision: check the saved out-of-stock sample";
    await admin.getByLabel("Примітка до групи").fill(note);
    const saved = await captureRequest(
      admin,
      "PATCH",
      "/api/orchestrator/v1/problem-groups/" + data.groupId,
      () => admin.getByRole("button", { name: "Зберегти примітку" }).click(),
    );
    expect(saved.body).toEqual({ note });
    await expect(admin.getByTestId("group-note")).toHaveText(note);
    const group = await jsonRequest(
      request,
      "get",
      url("orchestrator") + "/v1/problem-groups?source_id=" + data.sourceId,
    );
    expect((group["items"] as Array<{ note: string }>)[0]?.note).toBe(note);
    await admin.reload();
    await openGroup(admin, data.sourceId);
    await expect(admin.getByLabel("Примітка до групи")).toHaveValue(note);
    await admin.getByLabel("Сховище RAW прикладів").fill("raw-files");
    await admin.getByRole("button", { name: "Підготувати повторну обробку прикладів" }).click();
    await expect(admin.getByRole("form", { name: "Повторна обробка" })).toContainText(
      data.raw.object.object_id,
    );
    await reprocess(admin, request, data.taskId, data.raw, { object_ids: [data.raw.object.object_id] });
  });

  test("run-page manual object_ids and observation_ids select one RAW, excluding the control sample", async ({
    admin,
    request,
  }) => {
    test.setTimeout(240_000);
    const data = await problemRun(request);
    for (const mode of ["object", "observation"] as const) {
      await admin.goto("/runs/" + data.runId);
      await admin.getByRole("tab", { name: "Повторна обробка" }).click();
      const form = admin.getByRole("form", { name: "Повторна обробка" });
      await expect(form.getByLabel("Завдання")).toHaveValue(data.taskId);
      await form.getByLabel("Сховище RAW (connection_id)").fill("raw-files");
      await form
        .getByLabel("Точний вибір: " + (mode === "object" ? "RAW object_ids" : "observation_ids"))
        .fill(mode === "object" ? data.raw.object.object_id : data.raw.material.observation_id);
      await reprocess(
        admin,
        request,
        data.taskId,
        data.raw,
        mode === "object"
          ? { object_ids: [data.raw.object.object_id] }
          : { observation_ids: [data.raw.material.observation_id] },
      );
    }
  });

  test("improvement runs are filtered by package_id and job status against the real assistant", async ({
    admin,
    request,
  }) => {
    test.setTimeout(240_000);
    const data = await problemRun(request);
    const decoy = await publishPackage(
      request,
      url("registry"),
      path.join(E2E_PACKAGES_DIR, "e2e.improvable-product-extractor"),
      "e2e-filter-control",
    );
    await approvePackage(request, url("registry"), decoy, "post-M3 admin filters control");
    const jobs: string[] = [];
    for (const pkg of [data.extractor, decoy]) {
      const job = await jsonRequest(
        request,
        "post",
        url("assistant") + "/v1/improvement-runs",
        {
          package: { package_id: pkg.package_id, version: pkg.version, digest: pkg.digest },
          source_id: data.sourceId,
          problem_samples: [
            { material_ref: { storage_connection_id: "raw-files", object_id: data.raw.object.object_id } },
          ],
          policy: { approval: "manual", allow_fork: true },
          limits: { max_improvement_attempts: 0 },
        },
        202,
      );
      jobs.push(job["job_id"] as string);
      await expect
        .poll(
          async () =>
            (await jsonRequest(request, "get", url("assistant") + "/v1/jobs/" + job["job_id"]))["status"],
          { timeout: 60_000 },
        )
        .toBe("succeeded");
    }
    // A zero-attempt run needs no external LLM call; both jobs have real, completed assistant results.
    await admin.goto("/assistant?tab=improvement");
    await admin.getByLabel("Джерело (source_id)").fill(data.sourceId);
    const table = admin.getByRole("table", { name: "Запуски вдосконалення" });
    await expect(table.getByRole("row")).toHaveCount(3);
    const [packageQuery] = await Promise.all([
      admin.waitForRequest(
        (r) =>
          new URL(r.url()).pathname === "/api/assistant/v1/improvement-runs" &&
          new URL(r.url()).searchParams.get("package_id") === data.extractor.package_id,
      ),
      admin.getByLabel("Пакет (package_id)").fill(data.extractor.package_id),
    ]);
    expect(new URL(packageQuery.url()).searchParams.get("package_id")).toBe(data.extractor.package_id);
    await expect(table.getByRole("row")).toHaveCount(2);
    await expect(table).toContainText(jobs[0]!);
    await expect(table).not.toContainText(jobs[1]!);
    const [statusQuery] = await Promise.all([
      admin.waitForRequest(
        (r) =>
          new URL(r.url()).pathname === "/api/assistant/v1/improvement-runs" &&
          new URL(r.url()).searchParams.get("status") === "failed",
      ),
      admin.getByLabel("Стан job").selectOption("failed"),
    ]);
    expect(new URL(statusQuery.url()).searchParams.get("package_id")).toBe(data.extractor.package_id);
    await expect(table.getByRole("row", { name: new RegExp(jobs[0]!) })).toHaveCount(0);
    await admin.getByLabel("Стан job").selectOption("succeeded");
    await expect(table).toContainText(jobs[0]!);
    await expect(table).not.toContainText(jobs[1]!);
  });

  test("run items show retry_scheduled and its real available_at after an unavailable fake provider", async ({
    admin,
    request,
  }) => {
    test.setTimeout(180_000);
    const alias = uniqueId("e2e-admin-retry");
    await seedFakeLlm(request, url("llm"), alias, [{ error: "unavailable" }], [alias]);
    const triage = await publishPackage(
      request,
      url("registry"),
      path.join(E2E_PACKAGES_DIR, "e2e.llm-page-triage"),
      "e2e-retry-triage",
      (manifest) => {
        (manifest["entry"] as Record<string, unknown>)["model"] = alias;
      },
    );
    await approvePackage(request, url("registry"), triage, "post-M3 admin retry diagnostics");
    const rules = await publishTestsiteRules(
      request,
      url("registry"),
      "e2e-retry-rules",
      "post-M3 retry rules",
    );
    const sourceId = uniqueId("e2e-retry-source");
    const taskId = uniqueId("e2e-retry-task");
    await jsonRequest(
      request,
      "post",
      url("orchestrator") + "/v1/sources",
      {
        source_id: sourceId,
        kind: "web",
        title: sourceId,
        locator: { url: TESTSITE_URL + "/" },
        collector_rules: rules,
      },
      201,
    );
    await jsonRequest(
      request,
      "post",
      url("orchestrator") + "/v1/tasks",
      {
        task_id: taskId,
        title: taskId,
        input: { source_id: sourceId, urls: [TESTSITE_URL + "/product/phone-gamma"] },
        retries: {
          max_attempts: 2,
          initial_backoff_ms: 1000,
          max_backoff_ms: 1000,
          backoff_multiplier: 1,
          jitter: false,
        },
        stages: [
          { stage_id: "collect", kind: "collect", collector: { collector: "web", mode: "full" } },
          {
            stage_id: "triage",
            kind: "handler",
            handler: { package_id: triage.package_id, version: triage.version, digest: triage.digest },
            inputs: [{ from: "collect" }],
          },
        ],
      },
      201,
    );
    const job = await jsonRequest(
      request,
      "post",
      url("orchestrator") + "/v1/tasks/" + taskId + "/runs",
      {},
      202,
    );
    const runId = job["job_id"] as string;
    await waitRun(request, url("orchestrator"), runId);
    const items = (
      await jsonRequest(request, "get", url("orchestrator") + "/v1/runs/" + runId + "/items?stage_id=triage")
    )["items"] as Array<{
      item_id: string;
      attempts: number;
      status: string;
      available_at: string;
      attempt_history: Array<{
        event: string;
        at: string;
        attempt?: number;
        available_at?: string;
        delay_ms?: number;
        code?: string;
      }>;
    }>;
    expect(items).toHaveLength(1);
    const item = items[0]!;
    expect(item.status).toBe("failed");
    expect(item.attempts).toBe(2);
    const retry = item.attempt_history.find((e) => e.event === "retry_scheduled")!;
    expect(retry).toMatchObject({ attempt: 1, delay_ms: 1000, code: "upstream_unavailable" });
    expect(retry.available_at).toBeTruthy();
    const laterClaim = item.attempt_history.find((e) => e.event === "claimed" && e.attempt === 2)!;
    expect(Date.parse(laterClaim.at)).toBeGreaterThanOrEqual(Date.parse(retry.available_at!));
    await admin.goto("/runs/" + runId);
    await admin.getByRole("tab", { name: "Елементи й помилки" }).click();
    const row = admin.getByRole("table", { name: "Елементи запуску" }).getByRole("row", { name: /triage/ });
    await expect(row).toContainText(formatInstant(item.available_at));
    await row.getByText(/^\d+ подій$/).click();
    const history = row.getByLabel("Історія спроб " + item.item_id);
    await expect(history.getByRole("listitem").filter({ hasText: "retry_scheduled" })).toContainText(
      "доступний з " + formatInstant(retry.available_at),
    );
    await expect(history).toContainText("затримка 1000 мс, код upstream_unavailable");
    await expect(admin.getByRole("alert")).toHaveCount(0);
  });
});
