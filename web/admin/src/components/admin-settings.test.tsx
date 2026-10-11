import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppProvider } from "../app/context";
import { DEFAULT_CONFIG } from "../config";
import { LlmPage, validProvider } from "../pages/LlmPage";
import { ConnectionsPage } from "../pages/ConnectionsPage";
import { PackagePage, PackagesPage } from "../pages/PackagesPage";
import { AssistantPage } from "../pages/AssistantPage";
import { ErrorBox, Field, ReasonAction, Table } from "./ui";
import { UnsavedChangesProvider } from "./UnsavedChanges";
import { openapiExample } from "../test/contracts";
import type { Connection, Package, PackageManifest, Source } from "../api/types";

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
  it("labels a search control inside a native form without including the submit button", () => {
    render(
      <Field label="Пошук у сховищі" hint="До розбиття на сторінки">
        <form>
          <input />
          <button>Знайти</button>
        </form>
      </Field>,
    );
    const control = screen.getByRole("textbox", { name: "Пошук у сховищі" });
    expect(control).toHaveAccessibleDescription("До розбиття на сторінки");
    expect((control as HTMLInputElement).labels).toHaveLength(1);
  });
  it("ignores an older provider open response after a new editor is opened", async () => {
    dialogSupport();
    // Provider identity and fields from the llm.v1 listProviders example.
    const existing = {
      provider_id: "fake",
      kind: "fake",
      enabled: true,
      models: [{ model_id: "fake-deterministic-1" }],
    };
    let complete: (() => void) | undefined;
    vi.stubGlobal(
      "fetch",
      vi.fn(async (request: Request) => {
        const url = new URL(request.url);
        if (url.pathname.endsWith("/providers/fake")) {
          await new Promise<void>((resolve) => {
            complete = resolve;
          });
          return Response.json(existing, { headers: { ETag: '"existing"' } });
        }
        return Response.json({
          items: url.pathname.endsWith("/providers") ? [existing] : [],
          next_cursor: null,
        });
      }),
    );
    const user = userEvent.setup();
    mount(<LlmPage />, "/llm");
    await user.click(await screen.findByRole("button", { name: "fake" }));
    await waitFor(() => expect(complete).toBeTypeOf("function"));
    await user.click(screen.getByRole("button", { name: "Новий провайдер" }));
    await user.type(screen.getByLabelText("Ідентифікатор провайдера"), "newer-provider-draft");
    complete?.();
    await waitFor(() =>
      expect(screen.getByLabelText("Ідентифікатор провайдера")).toHaveValue("newer-provider-draft"),
    );
    await user.click(screen.getByRole("tab", { name: "Бюджети" }));
    expect(screen.getByRole("dialog", { name: "Незбережені зміни" })).toBeVisible();
  });
  it.each(["create", "fork", "onboarding"] as const)(
    "keeps %s inputs fixed while its request is pending",
    async (mode) => {
      dialogSupport();
      const manifest = openapiExample<PackageManifest>("manifest-extractor");
      const fetchedAt = openapiExample<{ fetched_at: string }>("material-web").fetched_at;
      // Package view derived from the extractor manifest and the registry.v1 Package response fields.
      const pkg: Package = {
        package_id: manifest.package_id,
        kind: manifest.kind,
        title: manifest.title,
        latest_version: manifest.version,
        auto_changes_allowed: true,
        deprecated: false,
        created_at: fetchedAt,
        updated_at: fetchedAt,
      };
      let complete: (() => void) | undefined;
      let sent: Record<string, unknown> | undefined;
      vi.stubGlobal(
        "fetch",
        vi.fn(async (request: Request) => {
          const url = new URL(request.url);
          if (request.method === "POST") {
            sent = (await request.json()) as Record<string, unknown>;
            await new Promise<void>((resolve) => {
              complete = resolve;
            });
            return mode === "onboarding"
              ? Response.json(
                  { job_id: "job_review", kind: "onboarding", status: "queued", created_at: fetchedAt },
                  { status: 202 },
                )
              : Response.json(
                  { ...pkg, package_id: sent!["new_package_id"] ?? sent!["package_id"] },
                  { status: 201 },
                );
          }
          if (url.pathname.endsWith(`/packages/${pkg.package_id}`)) return Response.json(pkg);
          if (url.pathname.endsWith("/versions"))
            return Response.json({
              items: [{ package_id: pkg.package_id, version: manifest.version, status: "approved" }],
              next_cursor: null,
            });
          if (url.pathname.endsWith("/v1/info"))
            return Response.json({ service: "assistant", version: "0.1.0", api_versions: ["v1"] });
          if (url.pathname.endsWith("/jobs/job_review"))
            return Response.json({
              job_id: "job_review",
              kind: "onboarding",
              status: "queued",
              created_at: fetchedAt,
            });
          return Response.json({ items: [], next_cursor: null });
        }),
      );
      const user = userEvent.setup();
      if (mode === "create") {
        mount(<PackagesPage />, "/packages");
        await user.click(screen.getByRole("button", { name: "Новий пакет" }));
        await user.type(screen.getByLabelText("package_id"), "review-created");
      } else if (mode === "fork") {
        mount(
          <Routes>
            <Route path="/packages/:packageId" element={<PackagePage />} />
          </Routes>,
          `/packages/${pkg.package_id}`,
        );
        await user.click(await screen.findByRole("tab", { name: "Створити форк" }));
        const version = screen.getByRole("combobox", { name: "Від версії" });
        expect((version as HTMLSelectElement).labels).toHaveLength(1);
        await user.type(screen.getByLabelText("Новий package_id"), "review-fork");
      } else mount(<AssistantPage />, "/assistant");
      const field = screen.getByLabelText(mode === "onboarding" ? "Назва або посилання" : "Назва");
      await user.type(field, "Submitted title");
      await user.click(
        screen.getByRole("button", {
          name: mode === "create" ? "Створити" : mode === "fork" ? "Створити форк" : "Почати підключення",
        }),
      );
      await waitFor(() => expect(complete).toBeTypeOf("function"));
      expect(field).toBeDisabled();
      await user.type(field, " newer draft");
      expect(field).toHaveValue("Submitted title");
      expect(sent?.[mode === "onboarding" ? "query" : "title"]).toBe("Submitted title");
      complete?.();
      if (mode === "onboarding") {
        await waitFor(() => expect(field).toBeEnabled());
        await user.type(field, " next draft");
        await user.click(screen.getByRole("tab", { name: "Запуски вдосконалення" }));
        expect(screen.getByRole("dialog", { name: "Незбережені зміни" })).toBeVisible();
      }
    },
  );
  it("gives selects an exact field name and associates hints and field errors separately", () => {
    render(
      <Field label="Рівень" hint="Область дії бюджету" error="Виберіть джерело">
        <select defaultValue="source">
          <option value="platform">Платформа</option>
          <option value="source">Джерело</option>
        </select>
      </Field>,
    );
    const control = screen.getByRole("combobox", { name: "Рівень" });
    expect(control).toHaveAttribute("aria-invalid", "true");
    expect(control).toHaveAccessibleDescription("Область дії бюджету Виберіть джерело");
  });
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
