import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppProvider } from "../app/context";
import { DEFAULT_CONFIG } from "../config";
import type { Connection, StoredObject } from "../api/types";
import { openapiExample } from "../test/contracts";
import { MaterialsPage } from "./MaterialsPage";
import { StoragesPage } from "./StoragesPage";

const pg = openapiExample<Connection>("connection-pg");
const rawResult = openapiExample<{
  output: { writes: { object: StoredObject["object"] }[] };
  finished_at: string;
}>("result-storage-raw");
const raw: StoredObject = { object: rawResult.output.writes[0]!.object, stored_at: rawResult.finished_at };
const requests: URL[] = [];

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  requests.length = 0;
});
function mount(page: React.ReactNode, url = "/materials") {
  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <AppProvider
        config={{
          ...DEFAULT_CONFIG,
          auth: { mode: "none" },
          polling: { initial_ms: 10, max_ms: 20, multiplier: 1 },
        }}
      >
        <MemoryRouter initialEntries={[url]}>{page}</MemoryRouter>
      </AppProvider>
    </QueryClientProvider>,
  );
}
function mockObjects(contentText = "<script>window.stolen=true</script>") {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (request: Request) => {
      const url = new URL(request.url);
      requests.push(url);
      if (url.pathname.endsWith("/connections"))
        return Response.json({
          items: [pg, { connection_id: "raw-files", kind: "filesystem" }],
          next_cursor: null,
        });
      if (url.pathname.endsWith("/objects")) {
        if (url.searchParams.get("connection_id") === pg.connection_id)
          return Response.json(
            {
              type: "urn:jane:problem:upstream_unavailable",
              title: "Storage offline",
              status: 503,
              code: "upstream_unavailable",
            },
            { status: 503 },
          );
        return Response.json({
          items: [
            {
              ...raw,
              object: {
                ...raw.object,
                object_id: url.searchParams.has("cursor") ? "obj_second" : raw.object.object_id,
              },
            },
          ],
          next_cursor: url.searchParams.has("cursor") ? null : "next-raw",
        });
      }
      if (url.pathname.endsWith("/content"))
        return new Response(contentText, {
          headers: { "Content-Type": "text/html" },
        });
      return Response.json(raw);
    }),
  );
}

describe("material and storage browser", () => {
  it("discovers storages, isolates errors, and paginates each storage independently", async () => {
    mockObjects();
    mount(<MaterialsPage />);
    const table = await screen.findByRole("table", { name: "Матеріали raw-files" });
    expect(await within(table).findByText(raw.object.object_id)).toBeInTheDocument();
    expect(await screen.findByRole("alert")).toHaveTextContent("upstream_unavailable, HTTP 503");
    const section = screen.getByRole("region", { name: "raw-files" });
    await userEvent.click(within(section).getByRole("button", { name: "Показати ще" }));
    expect(await within(table).findByText("obj_second")).toBeInTheDocument();
    expect(
      requests.some(
        (u) =>
          u.searchParams.get("cursor") === "next-raw" && u.searchParams.get("connection_id") === "raw-files",
      ),
    ).toBe(true);
    expect(
      requests.some(
        (u) =>
          u.searchParams.get("cursor") === "next-raw" &&
          u.searchParams.get("connection_id") === pg.connection_id,
      ),
    ).toBe(false);
  });
  it.each(["<script>window.stolen=true</script>", '{ "large":9007199254740993, "exponent":1e400 }'])(
    "deep links preserve storage identity and exact source content: %s",
    async (contentText) => {
      mockObjects(contentText);
      mount(<MaterialsPage />, `/materials?connection_id=raw-files&object_id=${raw.object.object_id}`);
      expect((await screen.findByTestId("content-preview")).textContent).toBe(contentText);
      expect(document.querySelector("script")).toBeNull();
      expect(
        requests
          .filter((u) => u.pathname.includes("/objects/"))
          .every((u) => u.searchParams.get("connection_id") === "raw-files"),
      ).toBe(true);
    },
  );
  it("forwards source and storage-date filters to the API, without claiming local type filtering covers unloaded pages", async () => {
    mockObjects();
    mount(
      <MaterialsPage />,
      "/materials?connection_id=raw-files&source_id=shop-example&since=2026-10-01T12%3A00&until=2026-10-02T12%3A00",
    );
    await screen.findByText(raw.object.object_id);
    const query = requests.find((u) => u.pathname.endsWith("/objects"))!.searchParams;
    expect(query.get("source_id")).toBe("shop-example");
    expect(query.get("since")).toBe(new Date("2026-10-01T12:00").toISOString());
    expect(query.get("until")).toBe(new Date("2026-10-02T12:00").toISOString());
    expect(screen.getByLabelText("Медіатип у завантажених матеріалах")).toBeInTheDocument();
  });
  it("polls an async check without duplicate submission or premature snapshot refresh", async () => {
    let completed = false;
    let snapshots = 0;
    const keys: string[] = [];
    const requestBodies: unknown[] = [];
    const job = {
      job_id: "job_status_check",
      kind: "storage_status_check",
      status: "queued",
      created_at: "2026-10-11T08:00:00Z",
    };
    const snapshot = () => ({
      connection_id: pg.connection_id,
      kind: pg.kind,
      availability: completed ? "available" : "unknown",
      checked_at: completed ? "2026-10-11T08:00:00Z" : null,
      message: null,
      statistics: {
        object_count: null,
        total_size_bytes: null,
        checked_at: null,
        scope: "connection_objects",
        unavailable_reason: "adapter_statistics_not_supported",
      },
    });
    vi.stubGlobal(
      "fetch",
      vi.fn(async (request: Request) => {
        const url = new URL(request.url);
        if (url.pathname.endsWith("/connections")) return Response.json({ items: [pg], next_cursor: null });
        if (request.method === "POST") {
          expect(url.pathname.endsWith("/storage-status/checks")).toBe(true);
          keys.push(request.headers.get("Idempotency-Key") ?? "");
          requestBodies.push(await request.json());
          return Response.json(job, { status: 202, headers: { Location: "/v1/jobs/job_status_check" } });
        }
        if (url.pathname.includes("/jobs/"))
          return Response.json({
            ...job,
            status: completed ? "succeeded" : "running",
            progress: { completed: completed ? 1 : 0, total: 1, unit: "connections" },
            ...(completed ? { result: snapshot(), finished_at: "2026-10-11T08:00:01Z" } : {}),
          });
        snapshots++;
        return Response.json(snapshot());
      }),
    );
    mount(<StoragesPage />, "/storages");
    expect((await screen.findAllByText("Невідомо")).length).toBe(2);
    await userEvent.click(screen.getByRole("button", { name: "Перевірити зараз" }));
    expect(await screen.findByText("Перевіряємо доступність і статистику…")).toBeInTheDocument();
    const button = screen.getByRole("button", { name: "Перевіряємо…" });
    expect(button).toBeDisabled();
    await userEvent.click(button);
    expect(keys).toHaveLength(1);
    expect(snapshots).toBe(1);
    expect(requestBodies).toEqual([{ connection_id: "results-pg" }]);
    completed = true;
    await waitFor(() => expect(screen.getByText("Доступне")).toBeInTheDocument());
    expect(screen.getByRole("button", { name: "Перевірити зараз" })).toBeEnabled();
    expect(keys[0]).toBeTruthy();
    expect(snapshots).toBe(2);
    expect(
      screen.getByText("Статистика недоступна: Цей тип сховища не надає статистику."),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Матеріали" })).toHaveAttribute(
      "href",
      "/materials?connection_id=results-pg",
    );
    expect(screen.queryByText("JANE_SECRET_RESULTS_PG_PASSWORD")).not.toBeInTheDocument();
  });
  it("displays RAW and entity counts separately and links actual entity types", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (request: Request) => {
        const url = new URL(request.url);
        if (url.pathname.endsWith("/connections")) return Response.json({ items: [pg], next_cursor: null });
        return Response.json({
          connection_id: pg.connection_id,
          kind: pg.kind,
          availability: "available",
          checked_at: "2026-10-11T08:00:00Z",
          message: null,
          statistics: {
            object_count: 2,
            total_size_bytes: 151,
            scope: "connection_objects",
            checked_at: "2026-10-11T08:00:00Z",
            unavailable_reason: null,
          },
          entity_statistics: {
            entity_count: 1172,
            total_size_bytes: 65536,
            size_basis: "postgresql_relation_with_indexes",
            types: [{ entity_type: "offer", entity_count: 1172 }],
            checked_at: "2026-10-11T08:00:00Z",
            unavailable_reason: null,
          },
        });
      }),
    );
    mount(<StoragesPage />, "/storages");
    const link = await screen.findByRole("link", { name: /Пропозиції магазинів/ });
    expect(link).toHaveAttribute("href", "/results?connection_id=results-pg&entity_type=offer");
    expect(screen.getByText("Таблиця актуальних станів з індексами")).toBeInTheDocument();
    expect(screen.getByText("RAW і документи результатів").nextElementSibling).toHaveTextContent("2");
    expect(screen.getByText("Кількість сутностей").nextElementSibling).toHaveTextContent(/1.?172/);
  });
  it("shows a failed check and releases the button after its terminal outcome", async () => {
    const job = {
      job_id: "job_status_check",
      kind: "storage_status_check",
      status: "queued",
      created_at: "2026-10-11T08:00:00Z",
    };
    vi.stubGlobal(
      "fetch",
      vi.fn(async (request: Request) => {
        const url = new URL(request.url);
        if (url.pathname.endsWith("/connections")) return Response.json({ items: [pg], next_cursor: null });
        if (request.method === "POST") return Response.json(job, { status: 202 });
        if (url.pathname.includes("/jobs/"))
          return Response.json({
            ...job,
            status: "failed",
            error: {
              type: "urn:jane:problem:upstream_unavailable",
              title: "Storage unavailable",
              status: 503,
              code: "upstream_unavailable",
            },
          });
        return Response.json({
          connection_id: pg.connection_id,
          kind: pg.kind,
          availability: "unknown",
          checked_at: null,
          message: null,
          statistics: {
            object_count: null,
            total_size_bytes: null,
            checked_at: null,
            scope: "connection_objects",
            unavailable_reason: "not_checked",
          },
        });
      }),
    );
    mount(<StoragesPage />, "/storages");
    await userEvent.click(await screen.findByRole("button", { name: "Перевірити зараз" }));
    expect(await screen.findByText("Перевірка завершилася з помилкою.")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveTextContent("upstream_unavailable");
    expect(screen.getByRole("button", { name: "Перевірити зараз" })).toBeEnabled();
  });
  it.each(["since=invalid-date", "since=2026-10-02T12%3A00&until=2026-10-01T12%3A00"])(
    "blocks invalid date filters before storage requests: %s",
    async (query) => {
      mockObjects();
      mount(<MaterialsPage />, `/materials?connection_id=raw-files&${query}`);
      expect(await screen.findByRole("alert")).toHaveTextContent(/дата|Початок періоду/);
      expect(requests.some((u) => u.pathname.endsWith("/objects"))).toBe(false);
    },
  );
});
