// LLM providers, model aliases, budgets and cost accounting (ТЗ §8, llm.v1). Credentials only via connection_id.
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useApi } from "../app/context";
import { unwrap, unwrapWithEtag, ifMatch } from "../api/client";
import type { BudgetDefinition, ModelAlias, Provider } from "../api/types";
import { JsonEditor, checkJson, toJsonText } from "../components/JsonEditor";
import {
  ErrorBox,
  Field,
  JsonView,
  Loading,
  Notice,
  Page,
  Section,
  Status,
  Table,
  Tabs,
} from "../components/ui";
import { formatDate, formatMoney } from "../lib/format";

type TabKey = "providers" | "aliases" | "budgets" | "usage";

export function LlmPage() {
  const [tab, setTab] = useState<TabKey>("providers");
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
  const open = async (id: string | null) => {
    if (!id) return setEditing({ text: toJsonText(NEW_PROVIDER), etag: null, isNew: true });
    const result = await unwrapWithEtag(
      api.llm.GET("/v1/providers/{provider_id}", { params: { path: { provider_id: id } } }),
    );
    setEditing({ text: toJsonText(result.data), etag: result.etag, isNew: false });
  };
  const check = editing ? checkJson(editing.text) : null;
  const provider = check?.value as Provider | undefined;
  const save = useMutation({
    mutationFn: (p: Provider) =>
      unwrap(
        api.llm.PUT("/v1/providers/{provider_id}", {
          params: { path: { provider_id: p.provider_id }, header: ifMatch(editing?.etag) },
          body: p,
        }),
      ),
    onSuccess: () => {
      setEditing(null);
      void queryClient.invalidateQueries({ queryKey: ["llm-providers"] });
    },
  });
  return (
    <Section
      title="Провайдери"
      actions={
        <button type="button" className="btn" onClick={() => void open(null)}>
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
        rows={providers.data?.items ?? []}
        rowKey={(p) => p.provider_id}
        columns={[
          {
            header: "Провайдер",
            cell: (p) => (
              <button type="button" className="link" onClick={() => void open(p.provider_id)}>
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
      {editing ? (
        <div className="card">
          <JsonEditor
            text={editing.text}
            onChange={(text) => setEditing({ ...editing, text })}
            label="Провайдер"
            minHeight="14rem"
          />
          <div className="button-row">
            <button
              type="button"
              className="btn btn-primary"
              disabled={!provider?.provider_id || save.isPending}
              onClick={() => provider && save.mutate(provider)}
            >
              Зберегти провайдера
            </button>
            <button type="button" className="btn" onClick={() => setEditing(null)}>
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
  const save = useMutation({
    mutationFn: (a: ModelAlias) =>
      unwrap(api.llm.PUT("/v1/model-aliases/{alias}", { params: { path: { alias: a.alias } }, body: a })),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["llm-aliases"] }),
  });
  return (
    <Section title="Псевдоніми моделей (на них посилаються пакети)">
      <ErrorBox error={aliases.error} />
      <Table
        label="Псевдоніми моделей"
        rows={aliases.data?.items ?? []}
        rowKey={(a) => a.alias}
        columns={[
          {
            header: "Псевдонім",
            cell: (a) => (
              <button type="button" className="link" onClick={() => setDraft(a)}>
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
          <input
            value={draft.provider_id}
            onChange={(e) => setDraft({ ...draft, provider_id: e.target.value })}
          />
        </Field>
        <Field label="Модель">
          <input value={draft.model_id} onChange={(e) => setDraft({ ...draft, model_id: e.target.value })} />
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
  const save = useMutation({
    mutationFn: () => {
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
      );
    },
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["llm-budgets"] }),
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
        rows={budgets.data?.items ?? []}
        rowKey={(b) => `${b.scope_type}/${b.scope_id}`}
        columns={[
          { header: "Рівень", cell: (b) => b.scope_type },
          { header: "Об'єкт", cell: (b) => b.scope_id },
          {
            header: "Бюджет",
            cell: (b) => (b.budget ? `${formatMoney(b.budget)} / ${b.budget.period}` : "успадковано"),
          },
          { header: "Запитів/хв", cell: (b) => b.max_requests_per_minute ?? "—" },
          {
            header: "",
            cell: (b) => (
              <button
                type="button"
                className="btn btn-small"
                onClick={() => remove.mutate(b)}
                disabled={remove.isPending}
              >
                Прибрати
              </button>
            ),
          },
        ]}
      />
      <div className="inline-form">
        <Field label="Рівень">
          <select
            value={draft.scope_type}
            onChange={(e) =>
              setDraft({ ...draft, scope_type: e.target.value as BudgetDefinition["scope_type"] })
            }
          >
            <option value="platform">платформа</option>
            <option value="source">джерело</option>
            <option value="task">завдання</option>
          </select>
        </Field>
        <Field label="Ідентифікатор">
          <input value={draft.scope_id} onChange={(e) => setDraft({ ...draft, scope_id: e.target.value })} />
        </Field>
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
                {p}
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
          disabled={!draft.scope_id || save.isPending}
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
  const usage = useQuery({
    queryKey: ["llm-usage", groupBy, since, scopeType, scopeId],
    queryFn: () =>
      unwrap(
        api.llm.GET("/v1/usage", {
          params: {
            query: {
              group_by: groupBy,
              ...(since ? { since } : {}),
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
        <Field label="З (RFC 3339)">
          <input value={since} onChange={(e) => setSince(e.target.value)} />
        </Field>
        <Field label="Рівень">
          <select
            value={scopeType}
            onChange={(e) => setScopeType(e.target.value as "" | "platform" | "source" | "task")}
          >
            <option value="">усі</option>
            <option value="platform">платформа</option>
            <option value="source">джерело</option>
            <option value="task">завдання</option>
          </select>
        </Field>
        <Field label="Ідентифікатор">
          <input value={scopeId} onChange={(e) => setScopeId(e.target.value)} />
        </Field>
      </div>
      <ErrorBox error={usage.error} />
      {usage.data?.totals ? (
        <p>
          Разом: <strong data-testid="usage-total">{formatMoney(usage.data.totals.cost)}</strong>, запитів{" "}
          {usage.data.totals.requests ?? 0}, токенів {usage.data.totals.input_tokens ?? 0} /{" "}
          {usage.data.totals.output_tokens ?? 0}
        </p>
      ) : null}
      <Table
        label="Витрати LLM"
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
          { header: "Запитів", cell: (r) => String(r["requests"] ?? 0) },
          { header: "Токени вх.", cell: (r) => String(r["input_tokens"] ?? 0) },
          { header: "Токени вих.", cell: (r) => String(r["output_tokens"] ?? 0) },
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
