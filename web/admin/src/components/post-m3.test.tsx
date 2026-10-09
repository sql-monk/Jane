import "@testing-library/jest-dom/vitest";
import type { ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppProvider } from "../app/context";
import { DEFAULT_CONFIG } from "../config";
import type { Job, PackageManifest, Source, TaskConfig, TestReport } from "../api/types";
import { AssistantPage, sessionIdFromJob } from "../pages/AssistantPage";
import { openapiExample } from "../test/contracts";
import { AttemptHistory } from "./AttemptHistory";
import { ImprovementResultView } from "./ImprovementResultView";
import { ReprocessForm } from "./ReprocessForm";
import { StageVersions } from "./StageVersions";

// Neighbour data: contract example files (contracts/examples/openapi) and values of the OpenAPI response examples
// of assistant.v1 / orchestrator.v1 / registry.v1 (listOnboardingSessions, getOnboardingSession, listRunItems).
const material = openapiExample<{ material_id: string; observation_id: string; fetched_at: string }>(
  "material-web",
);
const SESSION = "onb_01J9ZY0000000000000000001";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  localStorage.clear();
});

type Handler = (request: Request, url: URL) => Response | Promise<Response> | undefined;

function stubFetch(handler: Handler): Request[] {
  const requests: Request[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (request: Request) => {
      requests.push(request.clone());
      const url = new URL(request.url);
      return (await handler(request, url)) ?? Response.json({ items: [], next_cursor: null });
    }),
  );
  return requests;
}

function renderAt(path: string, element: ReactNode, route = "*") {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <AppProvider config={{ ...DEFAULT_CONFIG, auth: { mode: "none" } }}>
        <MemoryRouter initialEntries={[path]}>
          <Routes>
            <Route path={route} element={element} />
            <Route path="/runs/:runId" element={<p>run page</p>} />
          </Routes>
        </MemoryRouter>
      </AppProvider>
    </QueryClientProvider>,
  );
}

describe("assistant sessions (R24)", () => {
  it("finds the session of an onboarding job by labels.session_id or by links.session", () => {
    const base: Job = {
      job_id: "job_1",
      kind: "onboarding",
      status: "queued",
      created_at: material.fetched_at,
    };
    expect(sessionIdFromJob({ ...base, labels: { session_id: SESSION } })).toBe(SESSION);
    expect(sessionIdFromJob({ ...base, links: { session: `/v1/onboarding-sessions/${SESSION}` } })).toBe(
      SESSION,
    );
    expect(sessionIdFromJob(base)).toBeNull();
  });

  it("restores the open session from the URL and the list from the API, without browser storage", async () => {
    const requests = stubFetch((_request, url) => {
      if (url.pathname.endsWith("/v1/onboarding-sessions"))
        return Response.json({
          items: [
            {
              session_id: SESSION,
              status: "proposals_ready",
              query: "Shop Example kettles",
              proposal_count: 2,
              costs: { amount: 0.31, currency: "USD" },
              created_at: "2026-09-27T09:00:00Z",
            },
          ],
          next_cursor: null,
        });
      if (url.pathname.endsWith(`/v1/onboarding-sessions/${SESSION}`))
        return Response.json({
          session_id: SESSION,
          status: "completed",
          query: "Shop Example kettles",
          created_at: "2026-09-27T09:00:00Z",
        });
      if (url.pathname.endsWith("/v1/info"))
        return Response.json({ service: "assistant", version: "0.1.0", api_versions: ["v1"] });
      return undefined;
    });
    renderAt(`/assistant?session=${SESSION}`, <AssistantPage />);
    expect(await screen.findByRole("heading", { name: `Сесія ${SESSION}` })).toBeInTheDocument();
    const table = await screen.findByRole("table", { name: "Сесії підключення" });
    expect(within(table).getByRole("button", { name: SESSION })).toHaveClass("link-active");
    expect(within(table).getByText("0.31 USD")).toBeInTheDocument();
    expect(requests.some((r) => new URL(r.url).pathname.endsWith("/v1/onboarding-sessions"))).toBe(true);
    expect(localStorage.length).toBe(0);
  });
});

describe("improvement result with a proposal (R08/R24)", () => {
  it("shows the unpublished version, changed files, omitted files, diff and manifest", async () => {
    const manifest = openapiExample<PackageManifest>("manifest-extractor");
    const based_on = { package_id: manifest.package_id, version: manifest.version };
    renderAt(
      "/",
      <ImprovementResultView
        result={{
          outcome: "proposal_only",
          version: { package_id: manifest.package_id, version: "9.9.9" },
          activated: false,
          proposal: {
            based_on,
            version: "9.9.9",
            schema_change: "none",
            change_summary: "Support the .price-new selector.",
            manifest: { ...manifest, version: "9.9.9" },
            files: {
              "src/main.py": { encoding: "utf-8", data: "PRICE = 'price-new'\n" },
              "tests/sample.bin": { encoding: "base64", data: "AAEC" },
            },
            omitted_files: ["tests/problem-p1/material.json"],
            diff: "--- a/src/main.py\n+++ b/src/main.py\n@@ -1 +1 @@\n-PRICE = 'price'\n+PRICE = 'price-new'\n",
          },
        }}
      />,
    );
    const result = screen.getByLabelText("Результат вдосконалення");
    expect(result).toHaveTextContent(`${manifest.package_id}@9.9.9 (не опубліковано)`);
    expect(within(result).queryByRole("link", { name: `${manifest.package_id}@9.9.9` })).toBeNull();
    const files = screen.getByRole("table", { name: "Змінені файли пропозиції" });
    expect(within(files).getByText("src/main.py")).toBeInTheDocument();
    expect(within(files).getByText("двійковий файл")).toBeInTheDocument();
    expect(within(files).getByText("3 B")).toBeInTheDocument();
    expect(screen.getByText("tests/problem-p1/material.json")).toBeInTheDocument();
    const diff = screen.getByLabelText("Diff пропозиції");
    expect(diff.querySelector(".diff-add")).toHaveTextContent("price-new");
    expect(
      screen.getByRole("link", { name: `${based_on.package_id}@${based_on.version}` }),
    ).toBeInTheDocument();
  });

  it("links a published version and shows test reports of every context", () => {
    const report = openapiExample<TestReport>("test-report");
    renderAt(
      "/",
      <ImprovementResultView
        result={{
          outcome: "new_version",
          version: report.package,
          test_reports: [{ context: "bindings:shop-catalog/extract-products", report }],
        }}
      />,
    );
    expect(
      screen.getByRole("link", { name: `${report.package.package_id}@${report.package.version}` }),
    ).toBeVisible();
    expect(screen.getByText("bindings:shop-catalog/extract-products")).toBeInTheDocument();
    expect(screen.queryByLabelText("Пропозиція асистента")).toBeNull();
  });
});

describe("attempt history (R25)", () => {
  it("keeps milliseconds of the backoff and never reflects an unknown error code", async () => {
    renderAt(
      "/",
      <AttemptHistory
        label="Історія спроб itm_1"
        history={[
          { event: "claimed", at: "2026-09-27T10:00:06.011Z", attempt: 1 },
          {
            event: "retry_scheduled",
            at: "2026-09-27T10:00:06.512Z",
            attempt: 1,
            available_at: "2026-09-27T10:00:09.512Z",
            delay_ms: 3000,
            code: "upstream_unavailable",
          },
          { event: "failed", at: "2026-09-27T10:00:09.600Z", attempt: 2, code: "leaked-secret-value" },
        ]}
      />,
    );
    await userEvent.click(screen.getByText("3 подій"));
    const items = within(screen.getByLabelText("Історія спроб itm_1")).getAllByRole("listitem");
    expect(items[1]).toHaveTextContent(
      "retry_scheduled 2026-09-27 10:00:06.512Z, спроба 1, доступний з 2026-09-27 10:00:09.512Z, затримка 3000 мс, код upstream_unavailable",
    );
    expect(items[2]).toHaveTextContent("unknown_error");
    expect(document.body.textContent).not.toContain("leaked-secret-value");
  });
});

describe("exact reprocessing selection (R06)", () => {
  function submitted(requests: Request[]) {
    return Promise.all(
      requests
        .filter((r) => r.method === "POST")
        .map(async (r) => (await r.json()) as Record<string, unknown>),
    );
  }
  const accepted = () =>
    Response.json(
      { job_id: "run_1", kind: "run", status: "queued", created_at: material.fetched_at },
      { status: 202 },
    );

  it.each([
    ["material", { material_ids: [material.material_id] }],
    ["object", { object_ids: ["obj_01J9ZQ4C00000000000000D1"] }],
    ["observation", { material_ids: [material.material_id], observation_ids: [material.observation_id] }],
  ])("a stored object: %s", async (mode, selection) => {
    const requests = stubFetch((request) => (request.method === "POST" ? accepted() : undefined));
    renderAt(
      "/",
      <ReprocessForm
        storageConnectionId="raw-files"
        stored={{
          object_id: "obj_01J9ZQ4C00000000000000D1",
          material_id: material.material_id,
          observation_id: material.observation_id,
        }}
      />,
    );
    await userEvent.type(screen.getByLabelText("Завдання"), "shop-catalog");
    await userEvent.selectOptions(screen.getByLabelText("Що обробити"), mode);
    await userEvent.click(screen.getByRole("button", { name: "Обробити повторно" }));
    expect(await screen.findByText("run page")).toBeInTheDocument();
    expect(await submitted(requests)).toEqual([
      { task_id: "shop-catalog", stored_materials: { storage_connection_id: "raw-files", ...selection } },
    ]);
  });

  it("an object without a material can be reprocessed only as that RAW", () => {
    stubFetch(() => undefined);
    renderAt("/", <ReprocessForm stored={{ object_id: "obj_1" }} />);
    const options = within(screen.getByLabelText("Що обробити")).getAllByRole("option");
    expect(options.map((o) => o.getAttribute("value"))).toEqual(["object"]);
  });
});

describe("collect stage versions (R05: collector.rules activations)", () => {
  it("activates a rules version on a collect stage that inherits the rules of its source", async () => {
    const task = openapiExample<TaskConfig>("task-catalog");
    const source = openapiExample<Source>("source-shop");
    const rules = source.collector_rules as { package_id: string; version: string; digest?: string };
    const withoutRules: TaskConfig = {
      ...task,
      stages: task.stages.map((s) =>
        s.kind === "collect" ? { ...s, collector: { collector: s.collector?.collector ?? "web" } } : s,
      ),
    };
    const requests = stubFetch((request, url) => {
      if (url.pathname.endsWith(`/v1/sources/${source.source_id}`)) return Response.json(source);
      if (url.pathname.endsWith(`/v1/packages/${rules.package_id}/versions`))
        return Response.json({
          items: [
            {
              package_id: rules.package_id,
              version: rules.version,
              digest: rules.digest,
              status: "approved",
              test_status: "unknown",
              created_at: material.fetched_at,
            },
          ],
          next_cursor: null,
        });
      if (request.method === "POST")
        return Response.json({
          activation_id: "act_1",
          task_id: task.task_id,
          stage_id: "collect",
          kind: "activate",
          package: rules,
          activated_at: material.fetched_at,
        });
      return undefined;
    });
    renderAt("/", <StageVersions task={withoutRules} />);
    const card = screen.getByRole("region", { name: "Етап collect" });
    expect(await within(card).findByText(`${rules.package_id}@${rules.version}`)).toBeInTheDocument();
    expect(within(card).getByText("(правила джерела)")).toBeInTheDocument();
    await within(card).findByRole("option", { name: `${rules.version} (unknown)` });
    await userEvent.selectOptions(within(card).getByLabelText("Версія для collect"), rules.version);
    await userEvent.click(within(card).getByRole("button", { name: "Активувати" }));
    await userEvent.type(within(card).getByLabelText("Причина: Активувати"), "new rules");
    await userEvent.click(within(card).getByRole("button", { name: "Активувати версію" }));
    expect(await within(card).findByText(/Активація:/)).toBeInTheDocument();
    const post = requests.find((r) => r.method === "POST");
    expect(new URL(post?.url ?? "").pathname).toMatch(
      /\/v1\/tasks\/shop-catalog\/stages\/collect\/activations$/,
    );
    expect(await post?.json()).toEqual({
      kind: "activate",
      package: { package_id: rules.package_id, version: rules.version, digest: rules.digest },
      reason: "new rules",
    });
  });
});
