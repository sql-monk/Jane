import { captureRequest, expect, realServiceUrl, test } from "./fixtures";
import { ONBOARD_TESTSITE } from "./llm-scripts";
import { ASSISTANT_MODEL_ALIASES, TESTSITE_URL as site, jsonRequest, seedFakeLlm, uniqueId } from "./seed";

// R26: source onboarding through the admin UI against the REAL assistant, LLM gateway, Web Collector, registry,
// handler-runtime and orchestrator behind Caddy - the admin twin of S-M2-06 (tests/e2e/test_m2_assistant.py).
// Substitutes of EXTERNAL systems: the LLM is the deterministic provider `fake` of WP-10 configured through the LLM
// API (e2e/llm-scripts.ts ONBOARD_TESTSITE = the S-M2-06 answers); the web search is the `static` provider of WP-11
// with tests/e2e/config/assistant-search.json (`pnpm e2e:real:prepare` mounts it). Everything else is real: sampling
// of the testsite through the collector, analysis, extractor tests in the runtime, publication, activation.
const MIRROR_URL = "http://testsite-mirror.example.test/";
// The user's crawl hints (a CollectorRules fragment, ТЗ §8 «правила обходу»), as in S-M2-06.
const SECTION_PREFIXES = ["/catalog/", "/product/", "/news/", "/sitemap.xml", "/sitemaps/"];
const SECTION_PAGES = [
  "/catalog/phones/",
  "/product/phone-alpha",
  "/news/",
  "/news/2026/autumn-sale",
  "/catalog/laptops/",
  "/product/laptop-one",
  "/news/2026/holiday-hours",
];
const ACTIONS = ["створити новий", "прив'язати наявний", "адаптувати форк"];

test.describe("real source onboarding in the admin @hybrid", () => {
  const services = ["assistant", "llm", "registry", "orchestrator", "collector", "handler"] as const;
  const url = (api: (typeof services)[number]) => realServiceUrl(api) as string;
  test.beforeEach(() => {
    test.skip(
      services.some((s) => !realServiceUrl(s)),
      "Full real API stack is required (JANE_ADMIN_API_TARGET)",
    );
  });

  test("by name: candidates, choice, sample, proposals with coverage, cost and risks, acceptance with activation; restored after a reload", async ({
    admin,
    request,
  }) => {
    test.setTimeout(900_000);
    const [assistant, llm, registry, orchestrator] = [
      url("assistant"),
      url("llm"),
      url("registry"),
      url("orchestrator"),
    ];
    // Cheap prices: one onboarding makes a classification call per sampled page within the assistant's run budget.
    await seedFakeLlm(request, llm, "e2e-admin-onboarding", ONBOARD_TESTSITE, ASSISTANT_MODEL_ALIASES, {
      input_per_mtok: 1,
      output_per_mtok: 4,
    });
    const sourceId = uniqueId("e2e-onb");

    // ---- the sampling threshold of the assistant (GET /v1/info, contract llm.min_onboarding_confidence)
    const info = (await jsonRequest(request, "get", `${assistant}/v1/info`)) as {
      limits: { defaults: { llm: { min_onboarding_confidence: number } } };
    };
    const threshold = info.limits.defaults.llm.min_onboarding_confidence;
    await admin.goto("/assistant");
    await expect(admin.getByTestId("min-onboarding-confidence")).toHaveText(
      new RegExp(`^${Math.round(threshold * 100)}%`),
    );

    // ---- 1. only the name of the site plus the entry pages of its sections
    await admin.getByLabel("Назва або посилання").fill("testsite");
    await admin.getByLabel("Тип джерела (необов'язково)").fill("web");
    await admin.getByLabel("Бюджет дослідження").fill("1");
    const hints = {
      scope: { path_prefixes: SECTION_PREFIXES },
      strategies: [{ type: "seed_list", urls: SECTION_PAGES.map((p) => site + p) }],
    };
    await admin.getByRole("textbox", { name: "Підказки обходу" }).fill(JSON.stringify(hints));
    const [started, response] = await Promise.all([
      captureRequest(admin, "POST", "/api/assistant/v1/onboarding-sessions", () =>
        admin.getByRole("button", { name: "Почати підключення" }).click(),
      ),
      admin.waitForResponse(
        (r) => r.request().method() === "POST" && r.url().endsWith("/api/assistant/v1/onboarding-sessions"),
      ),
    ]);
    expect(started.request.headers()["idempotency-key"]).toBeTruthy();
    expect(started.body).toEqual({
      query: "testsite",
      source_kind: "web",
      limits: { budget: { amount: 1, currency: "USD", period: "total" } },
      crawl_hints: hints,
      auto_activation: false,
    });
    expect(response.status()).toBe(202);
    const job = (await response.json()) as { labels: { session_id: string } };
    const sessionId = job.labels.session_id;
    await expect(admin).toHaveURL(new RegExp(`[?&]session=${sessionId}`));
    const view = admin.getByRole("region", { name: `Сесія ${sessionId}` });

    // ---- 2. two search candidates for the same name: the user picks the test site
    const candidates = view.getByRole("table", { name: "Кандидати джерела" });
    await expect(candidates).toBeVisible({ timeout: 120_000 });
    await expect(candidates.getByRole("row")).toHaveCount(3); // header + 2 candidates
    await expect(candidates).toContainText(MIRROR_URL);
    const testsiteRow = candidates.getByRole("row", { name: new RegExp(`${site}/`) });
    await expect(testsiteRow).toContainText("Jane test site");
    const chosen = (
      (await jsonRequest(request, "get", `${assistant}/v1/onboarding-sessions/${sessionId}`)) as {
        candidates: Array<{ candidate_id: string; url?: string }>;
      }
    ).candidates.find((c) => c.url === `${site}/`)?.candidate_id;
    const selected = await captureRequest(admin, "POST", "/candidate-selection", () =>
      testsiteRow.getByRole("button", { name: "Обрати" }).click(),
    );
    expect(selected.body).toEqual({ candidate_id: chosen });

    // ---- 3. adaptive sample through the real collector, analysis, proposals (the session polls with backoff)
    const status = view.locator(".kv-row", { hasText: "Стан" }).locator(".badge");
    await expect(status).toHaveText("proposals_ready", { timeout: 600_000 });
    const session = (await jsonRequest(
      request,
      "get",
      `${assistant}/v1/onboarding-sessions/${sessionId}`,
    )) as {
      sample: { materials: number; distinct_types: number; confidence: number; sufficient: boolean };
      proposals: Array<{
        proposal_id: string;
        recommended?: boolean;
        coverage: { estimated_materials: number };
        cost: { requests_per_run_estimate: number; llm_setup_cost: { amount: number } };
        risks: string[];
      }>;
      costs: { amount: number };
    };
    expect(session.sample.sufficient).toBe(true);
    expect(session.sample.confidence).toBeGreaterThanOrEqual(threshold);
    await expect(view.getByText(/^Вибірка:/)).toContainText(
      `Вибірка: ${session.sample.materials} матеріалів, ${session.sample.distinct_types} типів, впевненість ${Math.round(session.sample.confidence * 100)}%`,
    );
    const analysis = view.getByLabel("Аналіз джерела");
    await expect(analysis).toContainText("sitemap");
    await expect(analysis).toContainText("product (");
    await expect(analysis.getByRole("table", { name: "Поля product" })).toContainText("sku");
    expect(session.proposals.length).toBeGreaterThanOrEqual(2);
    expect(session.proposals.filter((p) => p.recommended)).toHaveLength(1);
    expect(session.costs.amount).toBeGreaterThan(0);
    for (const p of session.proposals) {
      const card = view.getByTestId(`proposal-${p.proposal_id}`);
      await expect(card).toContainText(`~${p.coverage.estimated_materials} матеріалів; product`);
      await expect(card.locator(".kv-row", { hasText: "Запитів за запуск" })).toContainText(
        String(p.cost.requests_per_run_estimate),
      );
      expect(p.cost.llm_setup_cost.amount).toBeGreaterThan(0);
      await expect(card.getByLabel("Ризики").getByRole("listitem")).toHaveCount(p.risks.length);
      const extractor = card.getByRole("table", { name: "Екстрактори варіанта" }).getByRole("row").nth(1);
      await expect(extractor).toContainText("product");
      await expect(extractor).toContainText(new RegExp(ACTIONS.join("|")));
      await expect(extractor).toContainText(/[1-9]\d* ✓ \/ 0 ✗/);
    }
    const recommended = session.proposals.find((p) => p.recommended) as (typeof session.proposals)[number];
    const recommendedCard = view.getByTestId(`proposal-${recommended.proposal_id}`);
    await expect(recommendedCard).toContainText("рекомендовано");
    await expect(recommendedCard).toContainText("Sitemap");

    // ---- 4. the user accepts the recommended plan under its own source id, with activation
    await view.getByLabel("source_id для джерела").fill(sourceId);
    await view.getByRole("checkbox", { name: /Активувати одразу/ }).check();
    const accepted = await captureRequest(
      admin,
      "POST",
      `/proposals/${recommended.proposal_id}/acceptance`,
      () => recommendedCard.getByRole("button", { name: "Прийняти варіант" }).click(),
    );
    expect(accepted.request.headers()["idempotency-key"]).toBeTruthy();
    expect(accepted.body).toEqual({ activate: true, source_id: sourceId });
    const panel = view.getByLabel("Застосування варіанта");
    await expect(panel.locator(".job-head .badge")).toHaveText("succeeded", { timeout: 600_000 });
    const result = panel.getByLabel("Результат застосування");
    await expect(result.locator(".kv-row", { hasText: "Активовано" })).toContainText("так");
    await expect(result.getByRole("link", { name: sourceId, exact: true })).toBeVisible();
    await expect(result.getByRole("link", { name: `${sourceId}-collect` })).toBeVisible();
    await expect(result.getByLabel("Звіт тестів").first()).toContainText(/не пройдено\s*0/);

    // the orchestrator has the source and the task the assistant created; the registry has the approved versions
    const source = (await jsonRequest(request, "get", `${orchestrator}/v1/sources/${sourceId}`)) as {
      collector_rules: { package_id: string; version: string };
      locator: { url: string };
    };
    expect(source.locator.url).toBe(`${site}/`);
    await expect(result).toContainText(
      `${source.collector_rules.package_id}@${source.collector_rules.version}`,
    );
    const task = (await jsonRequest(request, "get", `${orchestrator}/v1/tasks/${sourceId}-collect`)) as {
      stages: Array<{ stage_id: string; kind: string; collector?: { rules?: unknown } }>;
    };
    expect(task.stages.find((s) => s.kind === "collect")?.collector?.rules).toMatchObject(
      source.collector_rules,
    );
    const rules = (await jsonRequest(
      request,
      "get",
      `${registry}/v1/packages/${source.collector_rules.package_id}/versions/${source.collector_rules.version}`,
    )) as { status: string; manifest: { kind: string; provenance: { created_by: string } } };
    expect([rules.status, rules.manifest.kind, rules.manifest.provenance.created_by]).toEqual([
      "approved",
      "collector-rules",
      "llm",
    ]);

    // ---- 5. after a reload the session, its state and the acceptance result come back from the assistant API
    await admin.reload();
    await expect(status).toHaveText("completed");
    const sessions = admin.getByRole("table", { name: "Сесії підключення" });
    await expect(sessions.getByRole("row", { name: new RegExp(sessionId) })).toContainText("completed");
    const last = view.getByLabel("Останній job сесії");
    await expect(last.locator(".job-head .badge")).toHaveText("succeeded");
    await expect(last.getByLabel("Результат застосування")).toContainText(source.collector_rules.package_id);
    await admin.getByLabel("Стан сесії").selectOption("completed");
    await expect(sessions.getByRole("row", { name: new RegExp(sessionId) })).toBeVisible();
    expect(await admin.evaluate(() => window.localStorage.length)).toBe(0);

    // ---- 6. the created task: its collect stage runs the accepted rules; they can be re-activated and rolled back
    await last.getByRole("link", { name: `${sourceId}-collect` }).click();
    await admin.getByRole("tab", { name: "Версії етапів" }).click();
    const collect = admin.getByRole("region", { name: "Етап collect" });
    await expect(collect.getByTestId("current-collect")).toHaveText(
      `${source.collector_rules.package_id}@${source.collector_rules.version}`,
    );
    await collect.getByLabel("Версія для collect").selectOption(source.collector_rules.version);
    await collect.getByRole("button", { name: "Активувати" }).click();
    await collect.getByLabel("Причина: Активувати").fill("R26 accepted rules confirmed by a human");
    const activation = await captureRequest(admin, "POST", /\/stages\/collect\/activations$/, () =>
      collect.getByRole("button", { name: "Активувати версію" }).click(),
    );
    expect(activation.body).toMatchObject({
      kind: "activate",
      package: { package_id: source.collector_rules.package_id, version: source.collector_rules.version },
    });
    await expect(collect.getByText(/Активація:/)).toContainText(source.collector_rules.package_id);
    await collect.getByRole("button", { name: "Відкотити" }).click();
    await collect.getByLabel("Причина: Відкотити").fill("R26 rollback of the collector rules");
    await captureRequest(admin, "POST", /\/stages\/collect\/activations$/, () =>
      collect.getByRole("button", { name: "Відкотити до попередньої" }).click(),
    );
    await expect(collect.getByText(/Відкат:/)).toContainText(source.collector_rules.package_id);
    const history = collect.getByRole("table", { name: "Історія активацій collect" });
    await expect(history.getByRole("row")).toHaveCount(3);
    await expect(history).toContainText("R26 accepted rules confirmed by a human");
    await expect(admin.getByRole("alert")).toHaveCount(0);
  });
});
