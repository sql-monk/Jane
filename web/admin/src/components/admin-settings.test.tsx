import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppProvider } from "../app/context";
import { DEFAULT_CONFIG } from "../config";
import { LlmPage, validProvider } from "../pages/LlmPage";
import { ConnectionsPage } from "../pages/ConnectionsPage";
import { ErrorBox, ReasonAction, Table } from "./ui";
import { UnsavedChangesProvider } from "./UnsavedChanges";
import { openapiExample } from "../test/contracts";
import type { Connection, Source } from "../api/types";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

function mount(element: React.ReactNode, path: string) {
  return render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <AppProvider config={{ ...DEFAULT_CONFIG, auth: { mode: "none" } }}>
        <MemoryRouter initialEntries={[path]}>
          <UnsavedChangesProvider>{element}</UnsavedChangesProvider>
        </MemoryRouter>
      </AppProvider>
    </QueryClientProvider>,
  );
}
function dialogSupport() {
  Object.defineProperty(HTMLDialogElement.prototype, "showModal", {
    configurable: true,
    value: function (this: HTMLDialogElement) {
      this.open = true;
    },
  });
  Object.defineProperty(HTMLDialogElement.prototype, "close", {
    configurable: true,
    value: function (this: HTMLDialogElement) {
      this.open = false;
    },
  });
}

describe("admin settings review regressions", () => {
  it("distinguishes initial loading, failed load and a genuinely empty table", () => {
    const props = {
      rows: [] as string[],
      columns: [{ header: "Об'єкт", cell: (value: string) => value }],
      rowKey: (value: string) => value,
    };
    const { rerender } = render(<Table {...props} loading />);
    expect(screen.getByRole("status")).toHaveTextContent("Завантаження");
    expect(screen.queryByText("Немає даних")).toBeNull();
    rerender(<Table {...props} error={new Error("offline")} />);
    expect(screen.queryByText("Немає даних")).toBeNull();
    rerender(<Table {...props} />);
    expect(screen.getByText("Немає даних")).toBeInTheDocument();
  });
  it("explains a persisted Problem safely without reflecting service prose", () => {
    const secret = ["credential", "private"].join("-");
    render(
      <ErrorBox
        error={{
          type: "urn:jane:problem:source_unavailable",
          title: secret,
          detail: secret,
          code: "source_unavailable",
          status: 503,
          retryable: true,
        }}
      />,
    );
    expect(screen.getByRole("alert")).toHaveTextContent("Джерело недоступне");
    expect(screen.getByRole("alert")).toHaveTextContent("HTTP 503");
    expect(screen.getByRole("alert")).toHaveTextContent("Можна повторити");
    expect(screen.getByRole("alert").textContent).not.toContain(secret);
  });
  it("does not submit a destructive action before its scoped confirmation", async () => {
    dialogSupport();
    const confirm = vi.fn();
    const user = userEvent.setup();
    render(
      <ReasonAction
        label="Прибрати"
        requireReason={false}
        impact="Бюджет джерела shop-catalog"
        onConfirm={confirm}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Прибрати" }));
    const dialog = screen.getByRole("dialog");
    expect(dialog).toHaveTextContent("Бюджет джерела shop-catalog");
    expect(confirm).not.toHaveBeenCalled();
    await user.click(within(dialog).getByRole("button", { name: "Підтвердити" }));
    expect(confirm).toHaveBeenCalledTimes(1);
  });
  it("clears the platform id when selecting a source budget and protects the draft across tabs", async () => {
    dialogSupport();
    const source = openapiExample<Source>("source-shop");
    vi.stubGlobal(
      "fetch",
      vi.fn(async (request: Request) => {
        const url = new URL(request.url);
        return Response.json({ items: url.pathname.endsWith("/sources") ? [source] : [], next_cursor: null });
      }),
    );
    const user = userEvent.setup();
    mount(<LlmPage />, "/llm?tab=budgets");
    await user.type(screen.getByLabelText("Сума"), "1.23");
    await user.selectOptions(screen.getByLabelText("Рівень"), "source");
    expect(screen.getByLabelText("Джерело")).toHaveValue("");
    await user.selectOptions(screen.getByLabelText("Джерело"), source.source_id);
    await user.click(screen.getByRole("tab", { name: "Псевдоніми моделей" }));
    const dialog = screen.getByRole("dialog", { name: "Незбережені зміни" });
    await user.click(within(dialog).getByRole("button", { name: "Залишитися" }));
    expect(screen.getByLabelText("Сума")).toHaveValue(1.23);
    expect(screen.getByLabelText("Джерело")).toHaveValue(source.source_id);
  });
  it("opens a connection directly, keeps a quiet pristine form and resets the dirty baseline after save", async () => {
    dialogSupport();
    const connection = openapiExample<Connection>("connection-pg");
    vi.stubGlobal(
      "fetch",
      vi.fn(async (request: Request) => {
        const url = new URL(request.url);
        if (url.pathname.endsWith(`/connections/${connection.connection_id}`))
          return Response.json(
            { connection: request.method === "PUT" ? await request.json() : connection, executors: [] },
            { headers: { ETag: '"revision-1"' } },
          );
        return Response.json({ items: [], next_cursor: null });
      }),
    );
    const user = userEvent.setup();
    mount(<ConnectionsPage />, `/connections?connection_id=${connection.connection_id}`);
    await waitFor(() => expect(screen.getByLabelText("Назва")).toHaveValue(connection.title));
    expect(screen.queryByRole("alert", { name: "Помилки підключення" })).toBeNull();
    await user.type(screen.getByLabelText("Назва"), " changed");
    await user.click(screen.getByRole("button", { name: "Зберегти й синхронізувати" }));
    await screen.findByText("Збережено; синхронізація з виконавцями — асинхронна.");
    await user.click(screen.getByRole("button", { name: "Закрити" }));
    expect(screen.queryByRole("dialog", { name: "Незбережені зміни" })).toBeNull();
  });
  it("rejects malformed nested model values and pricing before submission", () => {
    const base = {
      provider_id: "fake",
      kind: "fake",
      enabled: true,
      models: [{ model_id: "fake-deterministic-1" }],
    };
    expect(validProvider(base)).toBe(true);
    expect(validProvider({ ...base, models: [null] })).toBe(false);
    expect(
      validProvider({
        ...base,
        models: [
          {
            model_id: "fake-deterministic-1",
            pricing: { input_per_mtok: -1, output_per_mtok: 1, currency: "USD" },
          },
        ],
      }),
    ).toBe(false);
    expect(
      validProvider({ ...base, models: [{ model_id: "fake-deterministic-1", max_context_tokens: 1.5 }] }),
    ).toBe(false);
  });
  it("does not mark a newer connection draft saved when an earlier write completes", async () => {
    dialogSupport();
    const connection = openapiExample<Connection>("connection-pg");
    let complete: (() => void) | undefined;
    vi.stubGlobal(
      "fetch",
      vi.fn(async (request: Request) => {
        const url = new URL(request.url);
        if (url.pathname.endsWith(`/connections/${connection.connection_id}`)) {
          const body = request.method === "PUT" ? await request.json() : connection;
          if (request.method === "PUT")
            await new Promise<void>((resolve) => {
              complete = resolve;
            });
          return Response.json({ connection: body, executors: [] }, { headers: { ETag: '"revision-2"' } });
        }
        return Response.json({ items: [], next_cursor: null });
      }),
    );
    const user = userEvent.setup();
    mount(<ConnectionsPage />, `/connections?connection_id=${connection.connection_id}`);
    await waitFor(() => expect(screen.getByLabelText("Назва")).toHaveValue(connection.title));
    await user.type(screen.getByLabelText("Назва"), " submitted");
    await user.click(screen.getByRole("button", { name: "Зберегти й синхронізувати" }));
    await waitFor(() => expect(complete).toBeTypeOf("function"));
    await user.type(screen.getByLabelText("Назва"), " newer");
    complete?.();
    await screen.findByText("Збережено; синхронізація з виконавцями — асинхронна.");
    await user.click(screen.getByRole("button", { name: "Закрити" }));
    expect(screen.getByRole("dialog", { name: "Незбережені зміни" })).toBeVisible();
    expect(screen.getByLabelText("Назва")).toHaveValue(`${connection.title} submitted newer`);
  });
});
