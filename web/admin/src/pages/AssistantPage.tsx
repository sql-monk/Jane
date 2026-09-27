// Assistant sessions: onboarding a source by name or URL, proposals with coverage/cost/risks (ТЗ §8, assistant.v1).
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useApi, useConfig } from "../app/context";
import { newIdempotencyKey, unwrap } from "../api/client";
import { pollDelay } from "../api/hooks";
import type {
  AcceptanceResult,
  Job,
  OnboardingRequest,
  OnboardingSession,
  Proposal,
  Source,
  TaskConfig,
} from "../api/types";
import { JobPanel, TestReportView } from "../components/JobPanel";
import { JsonEditor, checkJson } from "../components/JsonEditor";
import {
  ErrorBox,
  Field,
  JsonView,
  KeyValue,
  Loading,
  Notice,
  Page,
  Section,
  Status,
  Table,
} from "../components/ui";
import { formatDate, formatMoney, refLabel } from "../lib/format";
import { STRATEGY_LABELS } from "./RulesEditorPage";

const RECENT_ITEM = "jane.admin.recent_onboarding_sessions";
const ACTIVE_STATUSES = new Set(["resolving", "sampling", "analyzing", "applying"]);

// Per-viewer convenience only (the assistant has no list endpoint yet, see WP-12 report).
function readRecent(): string[] {
  try {
    const raw = window.localStorage.getItem(RECENT_ITEM);
    const parsed: unknown = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed.filter((x): x is string => typeof x === "string").slice(0, 20) : [];
  } catch {
    return [];
  }
}

function rememberSession(id: string): string[] {
  const next = [id, ...readRecent().filter((x) => x !== id)].slice(0, 20);
  try {
    window.localStorage.setItem(RECENT_ITEM, JSON.stringify(next));
  } catch {
    /* storage unavailable */
  }
  return next;
}

/** The onboarding Job points at its session through `links` (any link to /v1/onboarding-sessions/{id}). */
export function sessionIdFromJob(job: Job): string | null {
  for (const link of Object.values(job.links ?? {})) {
    const match = /\/v1\/onboarding-sessions\/([^/?#]+)/.exec(link);
    if (match?.[1]) return decodeURIComponent(match[1]);
  }
  return null;
}

export function AssistantPage() {
  const api = useApi();
  const [recent, setRecent] = useState<string[]>(readRecent);
  const [sessionId, setSessionId] = useState<string | null>(recent[0] ?? null);
  const [manualId, setManualId] = useState("");
  const [startJob, setStartJob] = useState<string | null>(null);
  const [form, setForm] = useState({
    query: "",
    source_kind: "",
    expected: "",
    amount: "",
    currency: "USD",
    samples: "",
    auto_activation: false,
    hints: "",
  });
  const hints = checkJson(form.hints);

  const start = useMutation({
    mutationFn: () => {
      const body: OnboardingRequest = {
        query: form.query,
        ...(form.source_kind ? { source_kind: form.source_kind } : {}),
        ...(form.expected
          ? {
              expected_entity_types: form.expected
                .split(",")
                .map((t) => t.trim())
                .filter(Boolean),
            }
          : {}),
        ...(form.amount || form.samples
          ? {
              limits: {
                ...(form.amount
                  ? {
                      budget: {
                        amount: Number(form.amount),
                        currency: form.currency,
                        period: "total" as const,
                      },
                    }
                  : {}),
                ...(form.samples ? { max_onboarding_samples: Number.parseInt(form.samples, 10) } : {}),
              },
            }
          : {}),
        ...(hints.value && typeof hints.value === "object"
          ? { crawl_hints: hints.value as Record<string, unknown> }
          : {}),
        auto_activation: form.auto_activation,
      };
      return unwrap(
        api.assistant.POST("/v1/onboarding-sessions", {
          params: { header: { "Idempotency-Key": newIdempotencyKey() } },
          body,
        }),
      ) as Promise<Job>;
    },
    onSuccess: (job) => {
      setStartJob(job.job_id);
      const id = sessionIdFromJob(job);
      if (id) {
        setRecent(rememberSession(id));
        setSessionId(id);
      }
    },
  });

  return (
    <Page title="Асистент: підключення джерела">
      <Section title="Нове підключення">
        <p className="muted">
          Достатньо назви сайту чи Telegram-каналу або точного посилання. Асистент збирає різноманітну вибірку
          в межах бюджету, визначає типи матеріалів і сутностей та пропонує кілька варіантів збору з
          поясненням охоплення, вартості й ризиків.
        </p>
        <div className="grid-3">
          <Field label="Назва або посилання">
            <input
              value={form.query}
              onChange={(e) => setForm({ ...form, query: e.target.value })}
              maxLength={2000}
            />
          </Field>
          <Field label="Тип джерела (необов'язково)">
            <input
              list="onb-kinds"
              value={form.source_kind}
              onChange={(e) => setForm({ ...form, source_kind: e.target.value })}
            />
            <datalist id="onb-kinds">
              <option value="web" />
              <option value="telegram" />
            </datalist>
          </Field>
          <Field label="Очікувані типи даних">
            <input
              value={form.expected}
              onChange={(e) => setForm({ ...form, expected: e.target.value })}
              placeholder="product, event"
            />
          </Field>
          <Field label="Бюджет дослідження">
            <input
              type="number"
              min={0}
              step="0.01"
              value={form.amount}
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
            />
          </Field>
          <Field label="Валюта">
            <input
              value={form.currency}
              onChange={(e) => setForm({ ...form, currency: e.target.value.toUpperCase() })}
              maxLength={3}
            />
          </Field>
          <Field label="Макс. сторінок вибірки">
            <input
              type="number"
              min={1}
              value={form.samples}
              onChange={(e) => setForm({ ...form, samples: e.target.value })}
            />
          </Field>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={form.auto_activation}
              onChange={(e) => setForm({ ...form, auto_activation: e.target.checked })}
            />
            Дозволити автоматичну активацію
          </label>
        </div>
        <Field label="Правила обходу від користувача (фрагмент CollectorRules, необов'язково)">
          <JsonEditor
            text={form.hints}
            onChange={(t) => setForm({ ...form, hints: t })}
            label="Підказки обходу"
            minHeight="5rem"
          />
        </Field>
        <button
          type="button"
          className="btn btn-primary"
          disabled={!form.query.trim() || Boolean(hints.parseError) || start.isPending}
          onClick={() => start.mutate()}
        >
          Почати підключення
        </button>
        <ErrorBox error={start.error} title="Не вдалося почати" />
        {startJob ? (
          <JobPanel service="assistant" client={api.assistant} jobId={startJob} title="Підключення джерела" />
        ) : null}
      </Section>
      <Section title="Сесії">
        <div className="inline-form">
          <Field label="Відкрити сесію за ідентифікатором">
            <input value={manualId} onChange={(e) => setManualId(e.target.value)} placeholder="onb_…" />
          </Field>
          <button
            type="button"
            className="btn"
            disabled={!manualId.trim()}
            onClick={() => {
              setRecent(rememberSession(manualId.trim()));
              setSessionId(manualId.trim());
              setManualId("");
            }}
          >
            Відкрити
          </button>
        </div>
        {recent.length ? (
          <p>
            Нещодавні:{" "}
            {recent.map((id) => (
              <button
                key={id}
                type="button"
                className={id === sessionId ? "link link-active" : "link"}
                onClick={() => setSessionId(id)}
              >
                {id}
              </button>
            ))}
          </p>
        ) : null}
      </Section>
      {sessionId ? <SessionView key={sessionId} sessionId={sessionId} /> : null}
    </Page>
  );
}

function SessionView({ sessionId }: { sessionId: string }) {
  const api = useApi();
  const { polling } = useConfig();
  const queryClient = useQueryClient();
  const [acceptJob, setAcceptJob] = useState<string | null>(null);
  const [activate, setActivate] = useState(false);
  const [sourceId, setSourceId] = useState("");
  const session = useQuery({
    queryKey: ["onboarding", sessionId],
    queryFn: () =>
      unwrap(
        api.assistant.GET("/v1/onboarding-sessions/{session_id}", {
          params: { path: { session_id: sessionId } },
        }),
      ),
    refetchInterval: (query) =>
      query.state.data && ACTIVE_STATUSES.has(query.state.data.status) && !query.state.error
        ? pollDelay(query.state.dataUpdateCount, polling)
        : false,
  });
  const select = useMutation({
    mutationFn: (candidateId: string) =>
      unwrap(
        api.assistant.POST("/v1/onboarding-sessions/{session_id}/candidate-selection", {
          params: { path: { session_id: sessionId } },
          body: { candidate_id: candidateId },
        }),
      ),
    onSuccess: (updated) => queryClient.setQueryData(["onboarding", sessionId], updated),
  });
  const accept = useMutation({
    mutationFn: (proposal: Proposal) =>
      unwrap(
        api.assistant.POST("/v1/onboarding-sessions/{session_id}/proposals/{proposal_id}/acceptance", {
          params: {
            path: { session_id: sessionId, proposal_id: proposal.proposal_id },
            header: { "Idempotency-Key": newIdempotencyKey() },
          },
          body: { activate, ...(sourceId ? { source_id: sourceId } : {}) },
        }),
      ) as Promise<Job>,
    onSuccess: (job) => setAcceptJob(job.job_id),
  });
  const s: OnboardingSession | undefined = session.data;
  return (
    <Section title={`Сесія ${sessionId}`}>
      {session.isLoading ? <Loading /> : null}
      <ErrorBox error={session.error} />
      {s ? (
        <>
          <KeyValue
            rows={[
              ["Запит", s.query],
              ["Стан", <Status value={s.status} />],
              ["Витрати LLM", formatMoney(s.costs)],
              ["Створено", formatDate(s.created_at)],
            ]}
          />
          {s.error ? (
            <ErrorBox error={new Error(`${s.error.title} (${s.error.code})`)} title="Помилка сесії" />
          ) : null}
          {s.status === "needs_disambiguation" && s.candidates?.length ? (
            <div aria-label="Кандидати">
              <h3>Уточніть джерело</h3>
              <Table
                label="Кандидати джерела"
                rows={s.candidates}
                rowKey={(c) => c.candidate_id}
                columns={[
                  { header: "Кандидат", cell: (c) => c.title },
                  { header: "Адреса", cell: (c) => c.url ?? c.telegram_username ?? "—" },
                  {
                    header: "Впевненість",
                    cell: (c) => (c.confidence !== undefined ? `${Math.round(c.confidence * 100)}%` : "—"),
                  },
                  {
                    header: "",
                    cell: (c) => (
                      <button
                        type="button"
                        className="btn btn-small"
                        onClick={() => select.mutate(c.candidate_id)}
                        disabled={select.isPending}
                      >
                        Обрати
                      </button>
                    ),
                  },
                ]}
              />
              <ErrorBox error={select.error} />
            </div>
          ) : null}
          {s.sample ? (
            <Notice tone={s.sample.sufficient === false ? "warn" : "info"}>
              Вибірка: {s.sample.materials ?? 0} матеріалів, {s.sample.distinct_types ?? 0} типів, впевненість{" "}
              {s.sample.confidence !== undefined ? `${Math.round(s.sample.confidence * 100)}%` : "—"}
              {s.sample.sufficient === false ? " — вибірки недостатньо" : ""}
              {s.sample.message ? `: ${s.sample.message}` : ""}
            </Notice>
          ) : null}
          {s.analysis ? (
            <div aria-label="Аналіз джерела">
              <h3>Аналіз</h3>
              <KeyValue
                rows={[
                  ["Тип джерела", s.analysis.source_kind ?? "—"],
                  ["Способи обходу", (s.analysis.discovery_methods ?? []).join(", ") || "—"],
                  [
                    "Типи матеріалів",
                    (s.analysis.material_types ?? []).map((m) => `${m.type} (${m.count})`).join(", ") || "—",
                  ],
                ]}
              />
              {(s.analysis.entities ?? []).map((e) => (
                <Table
                  key={e.entity_type}
                  label={`Поля ${e.entity_type}`}
                  rows={e.fields}
                  rowKey={(f) => f.name}
                  columns={[
                    { header: `Сутність ${e.entity_type}: поле`, cell: (f) => f.name },
                    { header: "Тип", cell: (f) => f.type ?? "—" },
                    {
                      header: "Покриття",
                      cell: (f) => (f.coverage !== undefined ? `${Math.round(f.coverage * 100)}%` : "—"),
                    },
                  ]}
                />
              ))}
            </div>
          ) : null}
          {(s.proposals ?? []).map((p) => (
            <ProposalCard
              key={p.proposal_id}
              proposal={p}
              canAccept={s.status === "proposals_ready"}
              busy={accept.isPending}
              onAccept={() => accept.mutate(p)}
            />
          ))}
          {s.status === "proposals_ready" ? (
            <div className="inline-form">
              <Field label="source_id для джерела">
                <input value={sourceId} onChange={(e) => setSourceId(e.target.value)} />
              </Field>
              <label className="checkbox">
                <input type="checkbox" checked={activate} onChange={(e) => setActivate(e.target.checked)} />
                Активувати одразу (якщо дозволяє політика)
              </label>
            </div>
          ) : null}
          <ErrorBox error={accept.error} title="Варіант не прийнято" />
          {acceptJob ? (
            <JobPanel
              service="assistant"
              client={api.assistant}
              jobId={acceptJob}
              title="Застосування варіанта"
              renderResult={(result) => <AcceptanceView result={result as unknown as AcceptanceResult} />}
            />
          ) : null}
        </>
      ) : null}
    </Section>
  );
}

function ProposalCard({
  proposal,
  canAccept,
  busy,
  onAccept,
}: {
  proposal: Proposal;
  canAccept: boolean;
  busy: boolean;
  onAccept: () => void;
}) {
  const rules = proposal.collector_rules as { strategies?: Array<{ type?: string }> };
  return (
    <div className="card" data-testid={`proposal-${proposal.proposal_id}`}>
      <div className="card-head">
        <strong>
          {proposal.title}{" "}
          {proposal.recommended ? <span className="badge badge-ok">рекомендовано</span> : null}
        </strong>
        {canAccept ? (
          <button type="button" className="btn btn-primary" onClick={onAccept} disabled={busy}>
            Прийняти варіант
          </button>
        ) : null}
      </div>
      {proposal.summary ? <p>{proposal.summary}</p> : null}
      <KeyValue
        rows={[
          [
            "Стратегії",
            (rules.strategies ?? []).map((st) => STRATEGY_LABELS[st.type ?? ""] ?? st.type).join(" + ") ||
              "—",
          ],
          [
            "Охоплення",
            proposal.coverage
              ? `~${proposal.coverage.estimated_materials ?? "?"} матеріалів; ${(proposal.coverage.entity_types ?? []).join(", ")}`
              : "—",
          ],
          ["Запитів за запуск", String(proposal.cost?.requests_per_run_estimate ?? "—")],
          ["LLM на налаштування", formatMoney(proposal.cost?.llm_setup_cost)],
          ["LLM за запуск", formatMoney(proposal.cost?.llm_cost_per_run)],
        ]}
      />
      {proposal.risks?.length ? (
        <div aria-label="Ризики">
          <strong>Ризики:</strong>
          <ul>
            {proposal.risks.map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
        </div>
      ) : null}
      <Table
        label="Екстрактори варіанта"
        rows={proposal.extractors}
        rowKey={(e, i) => `${e.entity_type}-${i}`}
        columns={[
          { header: "Сутність", cell: (e) => e.entity_type },
          {
            header: "Дія",
            cell: (e) =>
              ({ bind_existing: "прив'язати наявний", fork: "адаптувати форк", create: "створити новий" })[
                e.action
              ],
          },
          { header: "Пакет", cell: (e) => refLabel(e.package) },
          {
            header: "Збіг",
            cell: (e) => (e.match_score !== undefined ? `${Math.round(e.match_score * 100)}%` : "—"),
          },
          {
            header: "Перевірка на прикладах",
            cell: (e) =>
              e.tested_on_samples
                ? `${e.tested_on_samples.passed ?? 0} ✓ / ${e.tested_on_samples.failed ?? 0} ✗`
                : "—",
          },
        ]}
      />
      <details>
        <summary>Правила колектора варіанта</summary>
        <JsonView value={proposal.collector_rules} />
      </details>
    </div>
  );
}

function AcceptanceView({ result }: { result: AcceptanceResult }) {
  const api = useApi();
  const createSource = useMutation({
    mutationFn: (source: Source) =>
      unwrap(
        api.orchestrator.POST("/v1/sources", {
          params: { header: { "Idempotency-Key": newIdempotencyKey() } },
          body: source,
        }),
      ),
  });
  const createTask = useMutation({
    mutationFn: (task: TaskConfig) =>
      unwrap(
        api.orchestrator.POST("/v1/tasks", {
          params: { header: { "Idempotency-Key": newIdempotencyKey() } },
          body: task,
        }),
      ),
  });
  return (
    <div aria-label="Результат застосування">
      <KeyValue
        rows={[
          ["Правила колектора", refLabel(result.collector_rules)],
          ["Активовано", result.activated ? "так" : "ні — створіть джерело й завдання з чернеток"],
        ]}
      />
      {result.extractors.map((e, i) => (
        <div key={i}>
          <p>
            {e.action}:{" "}
            <Link to={`/packages/${encodeURIComponent(e.package.package_id)}`}>{refLabel(e.package)}</Link>
          </p>
          {e.test_report ? <TestReportView report={e.test_report} /> : null}
        </div>
      ))}
      {result.source_draft && !result.activated ? (
        <div>
          <button
            type="button"
            className="btn"
            onClick={() => result.source_draft && createSource.mutate(result.source_draft)}
            disabled={createSource.isPending}
          >
            Створити джерело з чернетки
          </button>
          {createSource.data ? (
            <Link to={`/sources/${encodeURIComponent(createSource.data.source_id)}`}> Джерело створено</Link>
          ) : null}
          <ErrorBox error={createSource.error} />
        </div>
      ) : null}
      {!result.activated
        ? (result.task_drafts ?? []).map((t) => (
            <div key={t.task_id}>
              <button
                type="button"
                className="btn"
                onClick={() => createTask.mutate(t)}
                disabled={createTask.isPending}
              >
                Створити завдання «{t.title}»
              </button>
            </div>
          ))
        : null}
      <ErrorBox error={createTask.error} />
    </div>
  );
}
