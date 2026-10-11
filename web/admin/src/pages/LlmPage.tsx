// LLM providers, model aliases, budgets and cost accounting (ТЗ §8, llm.v1). Credentials only via connection_id.
import { useCallback, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useApi } from "../app/context";
import { unwrap, unwrapWithEtag, ifMatch } from "../api/client";
import type { BudgetDefinition, ModelAlias, Provider } from "../api/types";
import { JsonEditor, checkJson, toJsonText } from "../components/JsonEditor";
import {
  PropertyGrid,
  PropertyIssuesContext,
  PropertyDraftsBlockedContext,
} from "../components/PropertyGrid";
import type { JsonValue } from "../lib/property";
import { ConnectionPicker } from "../components/ConnectionPicker";
import { useUnsavedChanges } from "../components/UnsavedChanges";
import { useSourceOptions, useTaskOptions } from "../lib/pickers";
import {
  ErrorBox,
  Field,
  JsonView,
  Loading,
  Notice,
  LoadMore,
  ReasonAction,
  Page,
  Section,
  Status,
  Table,
  Tabs,
} from "../components/ui";
import {
  formatDate,
  formatMoney,
  inputInstant,
  PERIOD_LABELS,
  SCOPE_LABELS,
  SLUG_PATTERN,
} from "../lib/format";

type TabKey = "providers" | "aliases" | "budgets" | "usage";

export function LlmPage() {
  const [params, setParams] = useSearchParams();
  const requested = params.get("tab");
  const tab: TabKey =
    requested === "aliases" || requested === "budgets" || requested === "usage" ? requested : "providers";
  const setTab = (value: TabKey) => setParams({ tab: value });
  return (
    <Page title="LLM">
      <Tabs<TabKey>
        tabs={[
          ["providers", "Провайдери й моделі"],
          ["aliases", "Псевдоніми моделей"],
          ["budgets", "Бюджети"],
          ["usage", "Витрати"],
        ]}
        active={tab}
        onChange={setTab}
      />
      {tab === "providers" ? <Providers /> : null}
      {tab === "aliases" ? <Aliases /> : null}
      {tab === "budgets" ? <Budgets /> : null}
      {tab === "usage" ? <Usage /> : null}
    </Page>
  );
}

const NEW_PROVIDER: Provider = {
  provider_id: "",
  kind: "openai_compatible",
  connection_id: "",
  enabled: true,
  models: [],
};

function Providers() {
  const api = useApi();
  const queryClient = useQueryClient();
  const providers = useQuery({
    queryKey: ["llm-providers"],
    queryFn: () => unwrap(api.llm.GET("/v1/providers")),
  });
  const [editing, setEditing] = useState<{ text: string; etag: string | null; isNew: boolean } | null>(null);
  const [baseline, setBaseline] = useState("");
  const [openError, setOpenError] = useState<unknown>(null);
  const loadEpoch = useRef(0);
  const [propertyIssues, setPropertyIssues] = useState<Record<string, string>>({});
  const reportPropertyIssue = useCallback(
    (key: string, message: string) =>
      setPropertyIssues((previous) => {
        if ((previous[key] ?? "") === message) return previous;
        const next = { ...previous };
        if (message) next[key] = message;
        else delete next[key];
        return next;
      }),
    [],
  );
  const load = async (id: string | null) => {
    const epoch = ++loadEpoch.current;
    setOpenError(null);
    setPropertyIssues({});
    if (!id) {
      const text = toJsonText(NEW_PROVIDER);
      setBaseline(text);
      return setEditing({ text, etag: null, isNew: true });
    }
    try {
      const result = await unwrapWithEtag(
        api.llm.GET("/v1/providers/{provider_id}", { params: { path: { provider_id: id } } }),
      );
      if (epoch !== loadEpoch.current) return;
      const text = toJsonText(result.data);
      setBaseline(text);
      setEditing({ text, etag: result.etag, isNew: false });
    } catch (error) {
      if (epoch === loadEpoch.current) setOpenError(error);
    }
  };
  const check = editing ? checkJson(editing.text) : null;
  const provider = check?.value as Provider | undefined;
  const save = useMutation({
    mutationFn: (p: Provider) =>
      unwrapWithEtag(
        api.llm.PUT("/v1/providers/{provider_id}", {
          params: { path: { provider_id: p.provider_id }, header: ifMatch(editing?.etag) },
          body: p,
        }),
      ),
    onSuccess: (result, saved) => {
      const text = toJsonText(saved);
      setBaseline(text);
      if (toJsonText(provider) === text) {
        guard.markSaved();
        setEditing(null);
      } else setEditing((current) => (current ? { ...current, etag: result.etag } : current));
      void queryClient.invalidateQueries({ queryKey: ["llm-providers"] });
    },
  });
  const valid = validProvider(provider) && Object.keys(propertyIssues).length === 0;
  const guard = useUnsavedChanges({
    dirty: Boolean(editing && (editing.text !== baseline || Object.keys(propertyIssues).length > 0)),
    label: "Провайдер LLM",
    onSave: async () => {
      if (!valid || !provider) return false;
      await save.mutateAsync(provider);
      return true;
    },
  });
  const open = (id: string | null) => {
    if (!save.isPending) guard.confirmChange(() => void load(id));
  };
  const update = (patch: Partial<Provider>) => {
    if (editing && provider) {
      const next = { ...provider, ...patch };
      if (patch.connection_id === "") delete next.connection_id;
      setEditing({ ...editing, text: toJsonText(next) });
    }
  };
  return (
    <Section
      title="Провайдери"
      actions={
        <button type="button" className="btn" disabled={save.isPending} onClick={() => void open(null)}>
          Новий провайдер
        </button>
      }
    >
      <Notice>
        Облікові дані провайдера задаються керованим підключенням (connection_id), а не в налаштуваннях
        провайдера.
      </Notice>
      {providers.isLoading ? <Loading /> : null}
      <ErrorBox error={providers.error} />
      <Table
        label="Провайдери LLM"
        loading={providers.isLoading}
        error={providers.error}
        rows={providers.data?.items ?? []}
        rowKey={(p) => p.provider_id}
        columns={[
          {
            header: "Провайдер",
            cell: (p) => (
              <button
                type="button"
                className="link"
                disabled={save.isPending}
                onClick={() => void open(p.provider_id)}
              >
                {p.provider_id}
              </button>
            ),
          },
          { header: "Тип", cell: (p) => p.kind },
          { header: "Підключення", cell: (p) => p.connection_id ?? "—" },
          { header: "Увімкнено", cell: (p) => <Status value={p.enabled ? "ok" : "cancelled"} /> },
          {
            header: "Моделі",
            cell: (p) =>
              p.models
                .map(
                  (m) =>
                    `${m.model_id}${m.pricing ? ` (${m.pricing.input_per_mtok}/${m.pricing.output_per_mtok} ${m.pricing.currency} за 1M)` : ""}`,
                )
                .join(", "),
          },
          { header: "Ліміти", cell: (p) => (p.limits ? <JsonView value={p.limits} compact /> : "—") },
        ]}
      />
      <ErrorBox error={openError} title="Провайдера не відкрито" />
      {editing ? (
        <div className="card">
          {provider && check?.ok && Array.isArray(provider.models) ? (
            <>
              <div className="grid-3">
                <Field label="Ідентифікатор провайдера">
                  <input
                    value={provider.provider_id}
                    disabled={!editing.isNew}
                    onChange={(e) => update({ provider_id: e.target.value })}
                  />
                </Field>
                <Field label="Тип провайдера">
                  <input
                    value={provider.kind}
                    list="provider-kinds"
                    onChange={(e) => update({ kind: e.target.value })}
                  />
                  <datalist id="provider-kinds">
                    <option value="openai_compatible" />
                    <option value="anthropic" />
                    <option value="fake" />
                  </datalist>
                </Field>
                <ConnectionPicker
                  label="Підключення провайдера"
                  value={provider.connection_id ?? ""}
                  onChange={(connection_id) => update({ connection_id })}
                />
                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={provider.enabled}
                    onChange={(e) => update({ enabled: e.target.checked })}
                  />
                  Увімкнено
                </label>
              </div>
              <h3>Моделі</h3>
              <p className="muted">
                model_id — ідентифікатор моделі у провайдера; pricing задає ціну за мільйон вхідних і вихідних
                токенів.
              </p>
              <PropertyIssuesContext.Provider value={reportPropertyIssue}>
                <PropertyDraftsBlockedContext.Provider value={save.isPending}>
                  <PropertyGrid
                    value={provider.models as unknown as JsonValue}
                    label="Моделі провайдера"
                    onChange={(models) => {
                      if (Array.isArray(models)) update({ models: models as unknown as Provider["models"] });
                    }}
                  />
                </PropertyDraftsBlockedContext.Provider>
              </PropertyIssuesContext.Provider>
            </>
          ) : null}
          {editing.text !== baseline && !valid ? (
            <p className="error-inline" role="alert">
              Заповніть ідентифікатор і тип провайдера. Кожна модель має містити model_id; ціни — невід'ємні
              числа, валюта — три великі літери, розмір контексту — додатне ціле число.
            </p>
          ) : null}
          <details>
            <summary>Додаткові параметри JSON</summary>
            <JsonEditor
              text={editing.text}
              onChange={(text) => setEditing({ ...editing, text })}
              label="Провайдер"
              readOnly={save.isPending}
              minHeight="14rem"
            />
          </details>
          <div className="button-row sticky-actions">
            <button
              type="button"
              className="btn btn-primary"
              disabled={!valid || !check?.ok || save.isPending}
              onClick={() => provider && save.mutate(provider)}
            >
              Зберегти провайдера
            </button>
            <button
              type="button"
              className="btn"
              onClick={() =>
                guard.confirmChange(() => {
                  loadEpoch.current += 1;
                  setEditing(null);
                })
              }
            >
              Скасувати
            </button>
          </div>
          <ErrorBox error={save.error} title="Провайдера не збережено" />
        </div>
      ) : null}
    </Section>
  );
}

function Aliases() {
  const api = useApi();
  const queryClient = useQueryClient();
  const aliases = useQuery({
    queryKey: ["llm-aliases"],
    queryFn: () => unwrap(api.llm.GET("/v1/model-aliases")),
  });
  const [draft, setDraft] = useState<ModelAlias>({ alias: "", provider_id: "", model_id: "" });
  const [baseline, setBaseline] = useState(JSON.stringify(draft));
  const providers = useQuery({
    queryKey: ["llm-providers"],
    queryFn: () => unwrap(api.llm.GET("/v1/providers")),
  });
  const save = useMutation({
    mutationFn: (a: ModelAlias) =>
      unwrap(api.llm.PUT("/v1/model-aliases/{alias}", { params: { path: { alias: a.alias } }, body: a })),
    onSuccess: (_result, saved) => {
      if (JSON.stringify(draft) === JSON.stringify(saved)) guard.markSaved();
      setBaseline(JSON.stringify(saved));
      void queryClient.invalidateQueries({ queryKey: ["llm-aliases"] });
    },
  });
  const guard = useUnsavedChanges({
    dirty: JSON.stringify(draft) !== baseline,
    label: "Псевдонім моделі",
    onSave: async () => {
      if (!/^[a-z][a-z0-9_-]{0,31}$/.test(draft.alias) || !draft.provider_id || !draft.model_id) return false;
      await save.mutateAsync(draft);
      return true;
    },
  });
  const models = providers.data?.items.find((p) => p.provider_id === draft.provider_id)?.models ?? [];
  return (
    <Section title="Псевдоніми моделей (на них посилаються пакети)">
      <ErrorBox error={aliases.error} />
      <Table
        label="Псевдоніми моделей"
        loading={aliases.isLoading}
        error={aliases.error}
        rows={aliases.data?.items ?? []}
        rowKey={(a) => a.alias}
        columns={[
          {
            header: "Псевдонім",
            cell: (a) => (
              <button
                type="button"
                className="link"
                onClick={() =>
                  guard.confirmChange(() => {
                    setDraft(a);
                    setBaseline(JSON.stringify(a));
                  })
                }
              >
                {a.alias}
              </button>
            ),
          },
          { header: "Провайдер", cell: (a) => a.provider_id },
          { header: "Модель", cell: (a) => a.model_id },
        ]}
      />
      <div className="inline-form">
        <Field label="Псевдонім">
          <input value={draft.alias} onChange={(e) => setDraft({ ...draft, alias: e.target.value })} />
        </Field>
        <Field label="Провайдер">
          <select
            value={draft.provider_id}
            onChange={(e) => setDraft({ ...draft, provider_id: e.target.value, model_id: "" })}
          >
            <option value="">Оберіть провайдера</option>
            {providers.data?.items.map((p) => (
              <option key={p.provider_id} value={p.provider_id}>
                {p.provider_id}
              </option>
            ))}
            {draft.provider_id && !providers.data?.items.some((p) => p.provider_id === draft.provider_id) ? (
              <option value={draft.provider_id}>{draft.provider_id} (поза каталогом)</option>
            ) : null}
          </select>
        </Field>
        <Field label="Модель">
          <select value={draft.model_id} onChange={(e) => setDraft({ ...draft, model_id: e.target.value })}>
            <option value="">Оберіть модель</option>
            {models.map((m) => (
              <option key={m.model_id} value={m.model_id}>
                {m.model_id}
              </option>
            ))}
            {draft.model_id && !models.some((m) => m.model_id === draft.model_id) ? (
              <option value={draft.model_id}>{draft.model_id} (поза каталогом)</option>
            ) : null}
          </select>
        </Field>
        <button
          type="button"
          className="btn btn-primary"
          disabled={
            !/^[a-z][a-z0-9_-]{0,31}$/.test(draft.alias) ||
            !draft.provider_id ||
            !draft.model_id ||
            save.isPending
          }
          onClick={() => save.mutate(draft)}
        >
          Призначити
        </button>
      </div>
      <ErrorBox error={save.error} />
      <ErrorBox error={providers.error} title="Каталог провайдерів недоступний" />
    </Section>
  );
}

type Period = NonNullable<BudgetDefinition["budget"]>["period"];

function Budgets() {
  const api = useApi();
  const queryClient = useQueryClient();
  const budgets = useQuery({ queryKey: ["llm-budgets"], queryFn: () => unwrap(api.llm.GET("/v1/budgets")) });
  const [draft, setDraft] = useState({
    scope_type: "platform" as BudgetDefinition["scope_type"],
    scope_id: "platform",
    amount: "",
    currency: "USD",
    period: "day" as Period,
    rpm: "",
  });
  const [baseline, setBaseline] = useState(JSON.stringify(draft));
  const save = useMutation({
    mutationFn: () => {
      const submitted = JSON.stringify(draft);
      const body: BudgetDefinition = {
        scope_type: draft.scope_type,
        scope_id: draft.scope_id,
        ...(draft.amount
          ? { budget: { amount: Number(draft.amount), currency: draft.currency, period: draft.period } }
          : {}),
        ...(draft.rpm ? { max_requests_per_minute: Number.parseInt(draft.rpm, 10) } : {}),
      };
      return unwrap(
        api.llm.PUT("/v1/budgets/{scope_type}/{scope_id}", {
          params: { path: { scope_type: draft.scope_type, scope_id: draft.scope_id } },
          body,
        }),
      ).then((result) => ({ result, submitted }));
    },
    onSuccess: (saved) => {
      if (JSON.stringify(draft) === saved.submitted) guard.markSaved();
      setBaseline(saved.submitted);
      void queryClient.invalidateQueries({ queryKey: ["llm-budgets"] });
    },
  });
  const valid = Boolean(
    draft.scope_id &&
    (draft.amount || draft.rpm) &&
    (!draft.amount ||
      (Number.isFinite(Number(draft.amount)) &&
        Number(draft.amount) >= 0 &&
        /^[A-Z]{3}$/.test(draft.currency))) &&
    (!draft.rpm || (Number.isInteger(Number(draft.rpm)) && Number(draft.rpm) >= 1)),
  );
  const guard = useUnsavedChanges({
    dirty: JSON.stringify(draft) !== baseline,
    label: "Бюджет LLM",
    onSave: async () => {
      if (!valid) return false;
      await save.mutateAsync();
      return true;
    },
  });
  const remove = useMutation({
    mutationFn: (b: BudgetDefinition) =>
      unwrap(
        api.llm.DELETE("/v1/budgets/{scope_type}/{scope_id}", {
          params: { path: { scope_type: b.scope_type, scope_id: b.scope_id } },
        }),
      ),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["llm-budgets"] }),
  });
  return (
    <Section title="Бюджети за рівнями (платформа → джерело → завдання)">
      <ErrorBox error={budgets.error} />
      <Table
        label="Бюджети LLM"
        loading={budgets.isLoading}
        error={budgets.error}
        rows={budgets.data?.items ?? []}
        rowKey={(b) => `${b.scope_type}/${b.scope_id}`}
        columns={[
          { header: "Рівень", cell: (b) => SCOPE_LABELS[b.scope_type] },
          { header: "Об'єкт", cell: (b) => b.scope_id },
          {
            header: "Бюджет",
            cell: (b) =>
              b.budget ? `${formatMoney(b.budget)} ${PERIOD_LABELS[b.budget.period]}` : "успадковано",
          },
          { header: "Запитів/хв", cell: (b) => b.max_requests_per_minute ?? "—" },
          {
            header: "",
            cell: (b) => (
              <ReasonAction
                label="Прибрати"
                danger
                requireReason={false}
                busy={remove.isPending}
                impact={`Прибрати бюджет: ${SCOPE_LABELS[b.scope_type]} ${b.scope_id}. Для цього рівня діятиме успадкований бюджет.`}
                onConfirm={() => remove.mutate(b)}
              />
            ),
          },
        ]}
      />
      <div className="inline-form">
        <Field label="Рівень">
          <select
            value={draft.scope_type}
            onChange={(e) =>
              setDraft({
                ...draft,
                scope_type: e.target.value as BudgetDefinition["scope_type"],
                scope_id: e.target.value === "platform" ? "platform" : "",
              })
            }
          >
            <option value="platform">платформа</option>
            <option value="source">джерело</option>
            <option value="task">завдання</option>
          </select>
        </Field>
        <ScopePicker
          scope={draft.scope_type}
          value={draft.scope_id}
          onChange={(scope_id) => setDraft({ ...draft, scope_id })}
        />
        <Field label="Сума">
          <input
            type="number"
            min={0}
            step="0.01"
            value={draft.amount}
            onChange={(e) => setDraft({ ...draft, amount: e.target.value })}
          />
        </Field>
        <Field label="Валюта">
          <input
            value={draft.currency}
            onChange={(e) => setDraft({ ...draft, currency: e.target.value.toUpperCase() })}
            maxLength={3}
          />
        </Field>
        <Field label="Період">
          <select
            value={draft.period}
            onChange={(e) => setDraft({ ...draft, period: e.target.value as Period })}
          >
            {(["run", "day", "week", "month", "total"] as Period[]).map((p) => (
              <option key={p} value={p}>
                {PERIOD_LABELS[p]}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Запитів/хв">
          <input
            type="number"
            min={1}
            value={draft.rpm}
            onChange={(e) => setDraft({ ...draft, rpm: e.target.value })}
          />
        </Field>
        <button
          type="button"
          className="btn btn-primary"
          disabled={!valid || save.isPending}
          onClick={() => save.mutate()}
        >
          Зберегти бюджет
        </button>
      </div>
      <ErrorBox error={save.error ?? remove.error} />
    </Section>
  );
}

type GroupBy = "day" | "model" | "purpose" | "scope";

function Usage() {
  const api = useApi();
  const [groupBy, setGroupBy] = useState<GroupBy>("day");
  const [since, setSince] = useState("");
  const [scopeType, setScopeType] = useState<"" | "platform" | "source" | "task">("");
  const [scopeId, setScopeId] = useState("");
  const sinceInstant = inputInstant(since);
  const usage = useQuery({
    queryKey: ["llm-usage", groupBy, since, scopeType, scopeId],
    queryFn: () =>
      unwrap(
        api.llm.GET("/v1/usage", {
          params: {
            query: {
              group_by: groupBy,
              ...(sinceInstant ? { since: sinceInstant } : {}),
              ...(scopeType ? { scope_type: scopeType } : {}),
              ...(scopeId ? { scope_id: scopeId } : {}),
            },
          },
        }),
      ),
  });
  const items = (usage.data?.items ?? []) as Array<Record<string, unknown>>;
  return (
    <Section title="Облік витрат LLM">
      <div className="filters">
        <Field label="Групувати за">
          <select value={groupBy} onChange={(e) => setGroupBy(e.target.value as GroupBy)}>
            <option value="day">днями</option>
            <option value="model">моделями</option>
            <option value="purpose">призначенням</option>
            <option value="scope">рівнями</option>
          </select>
        </Field>
        <Field label="З дати" hint="Часовий пояс вашого браузера; у результатах — час Києва.">
          <input type="datetime-local" value={since} onChange={(e) => setSince(e.target.value)} />
        </Field>
        <Field label="Рівень">
          <select
            value={scopeType}
            onChange={(e) => {
              setScopeType(e.target.value as "" | "platform" | "source" | "task");
              setScopeId(e.target.value === "platform" ? "platform" : "");
            }}
          >
            <option value="">усі</option>
            <option value="platform">платформа</option>
            <option value="source">джерело</option>
            <option value="task">завдання</option>
          </select>
        </Field>
        {scopeType ? <ScopePicker scope={scopeType} value={scopeId} onChange={setScopeId} /> : null}
      </div>
      <ErrorBox error={usage.error} />
      {usage.data?.totals ? (
        <p>
          Разом: <strong data-testid="usage-total">{formatMoney(usage.data.totals.cost)}</strong>, запитів{" "}
          {usage.data.totals.requests ?? "—"}, токенів {usage.data.totals.input_tokens ?? "—"} /{" "}
          {usage.data.totals.output_tokens ?? "—"}
        </p>
      ) : null}
      <Table
        label="Витрати LLM"
        loading={usage.isLoading}
        error={usage.error}
        rows={items}
        rowKey={(r, i) => String(r["period_start"] ?? r["model"] ?? r["purpose"] ?? i)}
        columns={[
          {
            header: "Група",
            cell: (r) =>
              r["period_start"]
                ? formatDate(String(r["period_start"]))
                : String(r["model"] ?? r["purpose"] ?? r["scope_id"] ?? "—"),
          },
          { header: "Запитів", cell: (r) => String(r["requests"] ?? "—") },
          { header: "Токени вх.", cell: (r) => String(r["input_tokens"] ?? "—") },
          { header: "Токени вих.", cell: (r) => String(r["output_tokens"] ?? "—") },
          {
            header: "Вартість",
            cell: (r) => formatMoney(r["cost"] as { amount: number; currency: string } | undefined),
          },
          { header: "Тестовий режим", cell: (r) => (r["test_mode"] ? "так" : "") },
        ]}
      />
    </Section>
  );
}

function ScopePicker({
  scope,
  value,
  onChange,
}: {
  scope: "platform" | "source" | "task";
  value: string;
  onChange: (value: string) => void;
}) {
  const sources = useSourceOptions();
  const tasks = useTaskOptions();
  if (scope === "platform")
    return (
      <Field label="Об'єкт">
        <input value="Платформа" readOnly />
      </Field>
    );
  const list = scope === "source" ? sources : tasks;
  return (
    <div>
      <Field label={SCOPE_LABELS[scope] ?? "Об'єкт"}>
        <select value={value} onChange={(e) => onChange(e.target.value)}>
          <option value="">Оберіть об'єкт</option>
          {list.options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label} · {option.value}
            </option>
          ))}
          {value && !list.options.some((option) => option.value === value) ? (
            <option value={value}>{value} (поза завантаженим каталогом)</option>
          ) : null}
        </select>
      </Field>
      <ErrorBox error={list.error} />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
    </div>
  );
}

export function validProvider(value: unknown): value is Provider {
  if (!value || typeof value !== "object") return false;
  const provider = value as Record<string, unknown>;
  if (
    typeof provider.provider_id !== "string" ||
    !SLUG_PATTERN.test(provider.provider_id) ||
    typeof provider.kind !== "string" ||
    !provider.kind ||
    typeof provider.enabled !== "boolean" ||
    !Array.isArray(provider.models)
  )
    return false;
  if (
    provider.connection_id !== undefined &&
    (typeof provider.connection_id !== "string" || !SLUG_PATTERN.test(provider.connection_id))
  )
    return false;
  return provider.models.every((value: unknown) => {
    if (!value || typeof value !== "object" || Array.isArray(value)) return false;
    const model = value as Record<string, unknown>;
    if (typeof model.model_id !== "string" || !model.model_id) return false;
    if (
      model.max_context_tokens !== undefined &&
      (typeof model.max_context_tokens !== "number" ||
        !Number.isInteger(model.max_context_tokens) ||
        model.max_context_tokens < 1)
    )
      return false;
    if (
      model.supports_structured_output !== undefined &&
      typeof model.supports_structured_output !== "boolean"
    )
      return false;
    if (model.pricing !== undefined) {
      if (!model.pricing || typeof model.pricing !== "object" || Array.isArray(model.pricing)) return false;
      const price = model.pricing as Record<string, unknown>;
      if (
        typeof price.input_per_mtok !== "number" ||
        !Number.isFinite(price.input_per_mtok) ||
        price.input_per_mtok < 0 ||
        typeof price.output_per_mtok !== "number" ||
        !Number.isFinite(price.output_per_mtok) ||
        price.output_per_mtok < 0 ||
        typeof price.currency !== "string" ||
        !/^[A-Z]{3}$/.test(price.currency)
      )
        return false;
    }
    return true;
  });
}
