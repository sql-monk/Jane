import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppProvider } from "../app/context";
import { DEFAULT_CONFIG } from "../config";
import type { Connection, StoredObject } from "../api/types";
import { openapiExample } from "../test/contracts";
import { MaterialsPage, formatMaterialContent } from "./MaterialsPage";
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
      <AppProvider config={{ ...DEFAULT_CONFIG, auth: { mode: "none" } }}>
        <MemoryRouter initialEntries={[url]}>{page}</MemoryRouter>
      </AppProvider>
    </QueryClientProvider>,
  );
}
function mockObjects() {
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
        return new Response("<script>window.stolen=true</script>", {
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
  it("deep links preserve storage identity and render HTML as inert text", async () => {
    mockObjects();
    mount(<MaterialsPage />, `/materials?connection_id=raw-files&object_id=${raw.object.object_id}`);
    expect(await screen.findByTestId("content-preview")).toHaveTextContent(
      "<script>window.stolen=true</script>",
    );
    expect(document.querySelector("script")).toBeNull();
    expect(
      requests
        .filter((u) => u.pathname.includes("/objects/"))
        .every((u) => u.searchParams.get("connection_id") === "raw-files"),
    ).toBe(true);
  });
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
  it("shows unknown statistics, checks explicitly with idempotency, then refreshes snapshot", async () => {
    let checked = false;
    const keys: string[] = [];
    vi.stubGlobal(
      "fetch",
      vi.fn(async (request: Request) => {
        const url = new URL(request.url);
        if (url.pathname.endsWith("/connections")) return Response.json({ items: [pg], next_cursor: null });
        if (request.method === "POST") {
          checked = true;
          keys.push(request.headers.get("Idempotency-Key") ?? "");
          return Response.json({ ok: true, checked_at: "2026-10-11T08:00:00Z" });
        }
        return Response.json({
          connection_id: pg.connection_id,
          kind: pg.kind,
          availability: checked ? "available" : "unknown",
          checked_at: checked ? "2026-10-11T08:00:00Z" : null,
          message: null,
          statistics: {
            object_count: null,
            total_size_bytes: null,
            checked_at: null,
            scope: "connection_objects",
            unavailable_reason: "not supported",
          },
        });
      }),
    );
    mount(<StoragesPage />, "/storages");
    expect((await screen.findAllByText("Невідомо")).length).toBe(2);
    await userEvent.click(screen.getByRole("button", { name: "Перевірити зараз" }));
    await waitFor(() => expect(screen.getByText("Доступне")).toBeInTheDocument());
    expect(keys[0]).toBeTruthy();
    expect(screen.getByText("Статистика недоступна: not supported")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Матеріали" })).toHaveAttribute(
      "href",
      "/materials?connection_id=results-pg",
    );
    expect(screen.queryByText("JANE_SECRET_RESULTS_PG_PASSWORD")).not.toBeInTheDocument();
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
  it("formats nested JSON without changing types and preserves plain text", () => {
    const text = '{"items":[1,false,null,{"x":"<b>safe</b>"}]}';
    expect(JSON.parse(formatMaterialContent(text))).toEqual(JSON.parse(text));
    expect(formatMaterialContent("not json")).toBe("not json");
  });
});
