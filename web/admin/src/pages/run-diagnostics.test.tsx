import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppProvider } from "../app/context";
import { DEFAULT_CONFIG } from "../config";
import type { Run, TaskConfig } from "../api/types";
import { openapiExample } from "../test/contracts";
import { RunOutcome, RunPage, collectorAddress } from "./RunsPage";
import { TraceOutputs } from "./MaterialsPage";
import { ReprocessForm } from "../components/ReprocessForm";
import { StageVersions } from "../components/StageVersions";

const task = openapiExample<TaskConfig>("task-catalog");
const run: Run = {
  run_id: "run_review",
  task_id: task.task_id,
  status: "succeeded",
  trigger: "manual",
  created_at: "2026-10-11T01:00:00Z",
  counters: { materials: 2 },
  summary: {
    basis: "recorded_handler_outputs",
    complete: true,
    extracted_entities: 3,
    saved_records: 3,
    result_groups: [
      { connection_id: "results-pg", entity_type: "product", scope: "actual-business-scope", count: 3 },
    ],
  },
};

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

function mount(node: React.ReactNode, url = "/") {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <AppProvider config={{ ...DEFAULT_CONFIG, auth: { mode: "none" } }}>
        <MemoryRouter initialEntries={[url]}>{node}</MemoryRouter>
      </AppProvider>
    </QueryClientProvider>,
  );
}

describe("run outcome and provenance", () => {
  it("separates approval from unknown tests and disables rollback without a prior activation", async () => {
    const stage = task.stages.find((candidate) => candidate.kind === "handler")!;
    const ref = stage.handler!;
    vi.stubGlobal(
      "fetch",
      vi.fn(async (request: Request) => {
        const url = new URL(request.url);
        if (url.pathname.endsWith("/versions")) {
          expect(url.searchParams.get("status")).toBe("approved");
          const packageId = url.pathname.split("/").at(-2);
          const packageRef = task.stages
            .map((candidate) => candidate.handler ?? candidate.collector?.rules)
            .find((candidate) => candidate?.package_id === packageId)!;
          return Response.json({
            items: [
              { ...packageRef, status: "approved", test_status: "unknown", created_at: run.created_at },
            ],
            next_cursor: null,
          });
        }
        if (url.pathname.endsWith("/packages") || url.pathname.endsWith("/activations"))
          return Response.json({ items: [], next_cursor: null });
        throw new Error("Unexpected request");
      }),
    );
    mount(<StageVersions task={task} />);
    const card = within(screen.getByRole("region", { name: `Етап ${stage.stage_id}` }));
    const option = await card.findByRole("option", { name: `${ref.version} — погоджено` });
    expect(option).toBeInTheDocument();
    await userEvent.selectOptions(card.getByLabelText(`Версія для ${stage.stage_id}`), ref.version);
    expect(card.getByText(/Тести: результати невідомі або тести ще не запускали/)).toBeInTheDocument();
    expect(card.getByRole("button", { name: "Активувати" })).toBeEnabled();
    expect(card.getByRole("button", { name: "Відкотити" })).toBeDisabled();
    expect(card.getByText(/Відкат недоступний: попередньої активації немає/)).toBeInTheDocument();
  });

  it("excludes credentials and query tokens from collector addresses", () => {
    expect(collectorAddress("https://user:password@example.test/path?token=secret")).toBe(
      "https://example.test/path",
    );
    expect(collectorAddress("javascript:alert(1)")).toBeNull();
  });

  it("shows a collection startup failure honestly and starts item filters with all states", async () => {
    const requests: URL[] = [];
    vi.stubGlobal(
      "fetch",
      vi.fn(async (request: Request) => {
        const url = new URL(request.url);
        requests.push(url);
        if (url.pathname.endsWith("/runs/run_review"))
          return Response.json({
            ...run,
            status: "failed",
            collector_kind: "web",
            error: {
              type: "urn:jane:problem:validation_failed",
              code: "validation_failed",
              title: "raw-secret",
              detail: "raw-secret",
              status: 422,
              retryable: false,
            },
          });
        if (url.pathname.endsWith("/items") || url.pathname.endsWith("/executors"))
          return Response.json({ items: [], next_cursor: null });
        throw new Error("Unexpected request");
      }),
    );
    mount(
      <Routes>
        <Route path="/runs/:runId" element={<RunPage />} />
      </Routes>,
      "/runs/run_review",
    );
    await screen.findByRole("heading", { name: "Результат ланцюжка" });
    expect(document.body.textContent).not.toContain("raw-secret");
    await userEvent.click(screen.getByRole("tab", { name: "Помилки колектора" }));
    expect(screen.getByText(/Збір не вдалося почати/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("tab", { name: "Елементи й помилки" }));
    expect(screen.getByLabelText("Стан елемента")).toHaveValue("");
    await waitFor(() =>
      expect(requests.some((url) => url.pathname.endsWith("/items") && !url.searchParams.has("status"))).toBe(
        true,
      ),
    );
  });
  it("shows business counts apart from material count and links only actual storage scope", () => {
    mount(<RunOutcome run={run} />);
    expect(screen.getByText("Розібрано унікальних сутностей")).toBeInTheDocument();
    const link = screen.getByRole("link", { name: /actual-business-scope/ });
    expect(link.getAttribute("href")).toBe(
      "/results?connection_id=results-pg&entity_type=product&scope=actual-business-scope",
    );
    expect(link.getAttribute("href")).not.toContain("run_review");
    expect(screen.getByText(/Там можуть бути результати інших запусків/)).toBeInTheDocument();
  });

  it("marks missing historical business counts as unavailable", () => {
    mount(<RunOutcome run={{ ...run, summary: { complete: false, legacy_trace: true } }} />);
    expect(screen.getAllByText("Недоступно")).toHaveLength(2);
    expect(screen.getByText(/історичне трасування було обрізане/)).toBeInTheDocument();
  });

  it("keeps technical output JSON collapsed and links exact entity and RAW objects", async () => {
    mount(
      <TraceOutputs
        outputs={[
          {
            kind: "entity",
            entity_type: "product",
            canonical_key: 'actual-business-scope|{"sku":"a"}',
            connection_id: "results-pg",
          },
          {
            kind: "stored_object",
            object_id: "obj_exact",
            connection_id: "raw-files",
            write_status: "written",
          },
        ]}
      />,
    );
    expect(screen.getByTestId("json-view").closest("details")).not.toHaveAttribute("open");
    await userEvent.click(screen.getByText("Відкрити результати й об'єкти"));
    const entity = screen.getByRole("link", { name: /Товари/ });
    expect(new URL(entity.getAttribute("href")!, "http://localhost").searchParams.get("key")).toBe(
      'actual-business-scope|{"sku":"a"}',
    );
    expect(screen.getByRole("link", { name: /RAW obj_exact/ })).toHaveAttribute(
      "href",
      "/materials?connection_id=raw-files&object_id=obj_exact",
    );
  });

  it("a RAW row starts with exactly one object; broad material selection needs confirmation", async () => {
    const requests: Record<string, unknown>[] = [];
    vi.stubGlobal(
      "fetch",
      vi.fn(async (request: Request) => {
        const path = new URL(request.url).pathname;
        if (path.endsWith("/tasks"))
          return Response.json({
            items: [
              { task_id: task.task_id, title: task.title, source_id: task.input.source_id, enabled: true },
            ],
            next_cursor: null,
          });
        if (path.endsWith(`/tasks/${task.task_id}`)) return Response.json(task);
        if (path.endsWith("/connections"))
          return Response.json({
            items: [{ connection: { connection_id: "raw-files", kind: "filesystem" } }],
            next_cursor: null,
          });
        if (path.endsWith("/reprocessing")) {
          requests.push(await request.json());
          return Response.json({
            job_id: "run_exact",
            kind: "run",
            status: "queued",
            created_at: run.created_at,
          });
        }
        throw new Error(`Unexpected request ${path}`);
      }),
    );
    mount(
      <ReprocessForm
        taskId={task.task_id}
        storageConnectionId="raw-files"
        stored={{ object_id: "obj_exact", material_id: "mat", observation_id: "obs" }}
      />,
    );
    const selection = screen.getByLabelText("Що обробити");
    expect(selection).toHaveValue("object");
    const start = screen.getByRole("button", { name: "Обробити повторно" });
    await waitFor(() => expect(start).toBeEnabled());
    await userEvent.selectOptions(selection, "material");
    expect(start).toBeDisabled();
    await userEvent.selectOptions(selection, "object");
    await userEvent.click(start);
    await waitFor(() => expect(requests).toHaveLength(1));
    expect(requests[0]).toMatchObject({
      task_id: task.task_id,
      stored_materials: { storage_connection_id: "raw-files", object_ids: ["obj_exact"] },
    });
    expect(JSON.stringify(requests[0])).not.toContain("material_ids");
  });
});
