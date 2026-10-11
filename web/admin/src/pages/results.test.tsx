import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, useNavigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppProvider } from "../app/context";
import { DEFAULT_CONFIG } from "../config";
import type { Connection, EntityHistoryEntry, EntityState, Source } from "../api/types";
import { openapiExample } from "../test/contracts";
import { ResultsPage } from "./ResultsPage";

const pg = openapiExample<Connection>("connection-pg");
const source = openapiExample<Source>("source-shop");
const entity = openapiExample<EntityState>("entity-state");
const extracted = openapiExample<{ output: { entities: EntityHistoryEntry["record"][] } }>(
  "result-extractor-success",
);
const historyEntry: EntityHistoryEntry = {
  record: extracted.output.entities[0]!,
  received_at: "2026-09-28T07:00:00Z",
  applied_fields: ["title"],
  stale_fields: ["price"],
};
const offer: EntityState = {
  ...entity,
  entity_type: "offer",
  fields: { ...entity.fields, title: "Laptop Alpha", shop: "Example shop", brand: "Example brand" },
};
const requests: URL[] = [];
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  requests.length = 0;
});
function RouteControls() {
  const navigate = useNavigate();
  return (
    <button onClick={() => navigate("/results?connection_id=other&entity_type=product&key=another")}>
      Змінити посилання
    </button>
  );
}
function mount(url = "/results") {
  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <AppProvider config={{ ...DEFAULT_CONFIG, auth: { mode: "none" } }}>
        <MemoryRouter initialEntries={[url]}>
          <ResultsPage />
          <RouteControls />
        </MemoryRouter>
      </AppProvider>
    </QueryClientProvider>,
  );
}
function mockApi(handle?: (url: URL) => Response | Promise<Response> | undefined) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (request: Request) => {
      const url = new URL(request.url);
      requests.push(url);
      const override = await handle?.(url);
      if (override) return override;
      if (url.pathname.endsWith("/connections")) return Response.json({ items: [pg], next_cursor: null });
      if (url.pathname.endsWith("/sources"))
        return Response.json({ items: [{ ...source, expected_entity_types: ["offer"] }], next_cursor: null });
      if (url.pathname.endsWith("/entity-history"))
        return Response.json({ items: [historyEntry], next_cursor: null });
      if (url.pathname.endsWith("/entities"))
        return Response.json({
          items: [{ ...offer, entity_type: url.searchParams.get("entity_type") }],
          next_cursor: null,
        });
      throw new Error(`Unexpected contract request: ${url.pathname}`);
    }),
  );
}
function entityRequests() {
  return requests.filter((url) => url.pathname.endsWith("/entities"));
}

describe("parsed results browser", () => {
  it("infers the sole type from all source pages and discovers all configured stores", async () => {
    mockApi((url) => {
      if (url.pathname.endsWith("/sources")) {
        expect(entityRequests()).toHaveLength(0);
        return Response.json({
          items: [{ ...source, expected_entity_types: ["offer"] }],
          next_cursor: url.searchParams.has("cursor") ? null : "source-next",
        });
      }
      if (url.pathname.endsWith("/connections"))
        return Response.json({
          items: [
            { ...pg, connection_id: url.searchParams.has("cursor") ? "second-store" : pg.connection_id },
          ],
          next_cursor: url.searchParams.has("cursor") ? null : "store-next",
        });
      return undefined;
    });
    mount();
    expect(await screen.findByRole("table", { name: "Сутності results-pg" })).toHaveTextContent(
      "Laptop Alpha",
    );
    expect(await screen.findByRole("table", { name: "Сутності second-store" })).toHaveTextContent(
      "Example shop",
    );
    expect(screen.getByLabelText(/^Тип результату/)).toHaveValue("offer");
    expect(screen.getByLabelText("Сховище результатів")).toHaveValue("");
    expect(entityRequests().every((url) => url.searchParams.get("entity_type") === "offer")).toBe(true);
    expect(entityRequests().every((url) => !url.searchParams.has("scope"))).toBe(true);
  });
  it("does not guess among multiple types and permits a custom type", async () => {
    mockApi((url) =>
      url.pathname.endsWith("/sources")
        ? Response.json({
            items: [{ ...source, expected_entity_types: ["offer", "product"] }],
            next_cursor: null,
          })
        : undefined,
    );
    mount();
    await screen.findByText("Виберіть або введіть тип сутності, щоб переглянути розібрані дані.");
    expect(entityRequests()).toHaveLength(0);
    expect(
      [...document.querySelectorAll("#result-entity-types option")].map((option) =>
        option.getAttribute("value"),
      ),
    ).toEqual(["offer", "product"]);
    await userEvent.type(screen.getByLabelText(/^Тип результату/), "event");
    await screen.findByRole("table", { name: "Сутності results-pg" });
    await waitFor(() => expect(entityRequests().at(-1)?.searchParams.get("entity_type")).toBe("event"));
  });
  it("preserves explicit alternate type, key and scope deep links without using source_id as scope", async () => {
    mockApi();
    mount(
      "/results?connection_id=legacy-store&entity_type=product&scope=explicit-space&key=exact-key&source_id=other-source",
    );
    const table = await screen.findByRole("table", { name: "Сутності" });
    expect(table).toHaveTextContent("Laptop Alpha");
    expect(table).toHaveTextContent("Версія");
    const query = entityRequests()[0]!.searchParams;
    expect(query.get("connection_id")).toBe("legacy-store");
    expect(query.get("entity_type")).toBe("product");
    expect(query.get("scope")).toBe("explicit-space");
    expect(query.get("key")).toBe("exact-key");
    expect(query.has("source_id")).toBe(false);
    await userEvent.clear(screen.getByLabelText(/^Тип результату/));
    expect(
      await screen.findByText("Виберіть або введіть тип сутності, щоб переглянути розібрані дані."),
    ).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });
  it("isolates storage errors and cursors, labels local searching, and refreshes loaded data", async () => {
    let refreshCount = 0;
    mockApi((url) => {
      if (url.pathname.endsWith("/connections"))
        return Response.json({ items: [pg, { ...pg, connection_id: "offline" }], next_cursor: null });
      if (!url.pathname.endsWith("/entities")) return undefined;
      if (url.searchParams.get("connection_id") === "offline")
        return Response.json(
          {
            type: "urn:jane:problem:upstream_unavailable",
            title: "Storage offline",
            status: 503,
            code: "upstream_unavailable",
          },
          { status: 503 },
        );
      refreshCount++;
      return Response.json({
        items: [
          {
            ...offer,
            canonical_key: url.searchParams.has("cursor") ? "second-key" : offer.canonical_key,
            fields: {
              ...offer.fields,
              title: url.searchParams.has("cursor") ? "Laptop Beta" : "Laptop Alpha",
            },
          },
        ],
        next_cursor: url.searchParams.has("cursor") ? null : "entities-next",
      });
    });
    mount();
    const section = await screen.findByRole("region", { name: /results-pg/ });
    expect(
      await within(section).findByText(/Завантажено: 1. Показано: 1. Є наступна сторінка./),
    ).toBeInTheDocument();
    expect(await screen.findByRole("alert")).toHaveTextContent("upstream_unavailable, HTTP 503");
    await userEvent.click(within(section).getByRole("button", { name: "Показати ще" }));
    await within(section).findByText("Laptop Beta");
    expect(
      entityRequests()
        .filter((url) => url.searchParams.has("cursor"))
        .every((url) => url.searchParams.get("connection_id") === "results-pg"),
    ).toBe(true);
    await userEvent.type(screen.getByLabelText(/^Пошук у завантажених результатах/), "Beta");
    expect(
      within(section).getByText(/Завантажено: 2. Показано: 1. Усі сторінки завантажено./),
    ).toBeInTheDocument();
    expect(within(section).queryByText("Laptop Alpha")).not.toBeInTheDocument();
    const beforeRefresh = refreshCount;
    await userEvent.click(within(section).getByRole("button", { name: "Оновити" }));
    await waitFor(() => expect(refreshCount).toBeGreaterThan(beforeRefresh));
    expect(
      screen.getByText("Шукає лише серед уже завантажених рядків. Натисніть «Показати ще», щоб додати дані."),
    ).toBeInTheDocument();
  });
  it("renders zero prices, preserves unknown values and full metadata, and keeps unsafe URLs inert", async () => {
    mockApi((url) =>
      url.pathname.endsWith("/entities")
        ? Response.json({
            items: [
              {
                ...offer,
                fields: {
                  ...offer.fields,
                  title: "<script>unsafe</script>",
                  price: { amount: 0, currency: "UAH" },
                  availability: "future_state",
                  url: "javascript:alert(1)",
                  extra: { nested: ["retained"] },
                },
              },
              {
                ...offer,
                canonical_key: "missing-price",
                fields: { title: "Unknown price", price: { currency: "UAH" } },
              },
            ],
            next_cursor: null,
          })
        : undefined,
    );
    mount("/results?connection_id=results-pg&entity_type=offer");
    const table = await screen.findByRole("table", { name: "Сутності" });
    const row = within(table).getByText("<script>unsafe</script>").closest("tr")!;
    expect(within(row).getByText("0 UAH")).toBeInTheDocument();
    expect(within(row).getByText("future_state")).toBeInTheDocument();
    expect(within(row).getByText("javascript:alert(1)")).toBeInTheDocument();
    expect(row.querySelector("a[href^='javascript:']")).toBeNull();
    expect(document.querySelector("script")).toBeNull();
    expect(document.querySelector("img")).toBeNull();
    const details = row.querySelector("details")!;
    await userEvent.click(within(details).getByText("Усі поля та метадані"));
    expect(within(details).getByTestId("json-view")).toHaveTextContent('"nested"');
    expect(within(details).getByTestId("json-view")).toHaveTextContent('"field_orders"');
    expect(within(details).getByRole("link")).toHaveAttribute(
      "href",
      `/materials/${encodeURIComponent(entity.field_orders!.title!.material_id!)}/trace`,
    );
    const missing = within(table).getByText("Unknown price").closest("tr")!;
    expect(within(missing).getAllByRole("cell")[3]).toHaveTextContent(/^—$/);
    expect(within(missing).queryByText("0 UAH")).not.toBeInTheDocument();
  });
  it("paginates history, keeps record provenance, and closes history when URL context changes", async () => {
    mockApi((url) =>
      url.pathname.endsWith("/entity-history")
        ? Response.json({
            items: [
              {
                ...historyEntry,
                delivery_key: url.searchParams.has("cursor") ? "second-update" : "first-update",
              },
            ],
            next_cursor: url.searchParams.has("cursor") ? null : "history-next",
          })
        : undefined,
    );
    mount("/results?connection_id=results-pg&entity_type=offer");
    await userEvent.click(await screen.findByRole("button", { name: "Історія" }));
    const table = await screen.findByRole("table", { name: "Історія сутності" });
    expect(table.querySelector(".badge-warn")).toHaveTextContent("price");
    const details = table.querySelector("details")!;
    await userEvent.click(within(details).getByText("Повний запис і походження"));
    expect(within(details).getByRole("link", { name: /^Запуск/ })).toHaveAttribute(
      "href",
      `/runs/${historyEntry.record.provenance!.run_id}`,
    );
    expect(within(details).getByRole("link", { name: /^Матеріал/ })).toHaveAttribute(
      "href",
      `/materials/${encodeURIComponent(historyEntry.record.observation.material_id!)}/trace`,
    );
    expect(within(details).getByTestId("json-view")).toHaveTextContent('"provenance"');
    const section = table.closest("section")!;
    await userEvent.click(within(section).getByRole("button", { name: "Показати ще" }));
    await waitFor(() => expect(within(table).getAllByRole("row")).toHaveLength(3));
    expect(
      requests
        .find((url) => url.pathname.endsWith("/entity-history") && url.searchParams.has("cursor"))
        ?.searchParams.get("cursor"),
    ).toBe("history-next");
    await userEvent.click(screen.getByRole("button", { name: "Змінити посилання" }));
    expect(screen.queryByRole("table", { name: "Історія сутності" })).not.toBeInTheDocument();
  });
  it.each(["Область даних", "Канонічний ключ", "Пошук у завантажених результатах"])(
    "closes selected history when changing %s",
    async (label) => {
      mockApi();
      mount("/results?connection_id=results-pg&entity_type=offer");
      await userEvent.click(await screen.findByRole("button", { name: "Історія" }));
      await screen.findByRole("table", { name: "Історія сутності" });
      await userEvent.type(
        screen.getByLabelText((content) => content.startsWith(label)),
        "changed",
      );
      expect(screen.queryByRole("table", { name: "Історія сутності" })).not.toBeInTheDocument();
    },
  );
});
