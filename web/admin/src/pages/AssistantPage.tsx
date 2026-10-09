// Assistant: onboarding sessions (search, disambiguation, proposals with coverage/cost/risks, acceptance) and
// improvement runs (ТЗ §8, §9, assistant.v1). Sessions and runs come from the assistant's list endpoints
// (GET /v1/onboarding-sessions, GET /v1/improvement-runs), so the page restores its state after a reload; the
// open session / run is kept in the URL (`?session=`, `?tab=improvement&job=`), nothing in browser storage.
import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import { useApi, useConfig } from "../app/context";
import { newIdempotencyKey, unwrap } from "../api/client";
import { pollDelay, useCursorList } from "../api/hooks";
import { safeProblemCode } from "../api/problem";
import type {
  AcceptanceResult,
  Job,
  JobStatus,
  OnboardingRequest,
  OnboardingSession,
  OnboardingStatus,
  Proposal,
  Source,
  TaskConfig,
} from "../api/types";
import { ImprovementRunList } from "../components/ImprovementRuns";
import { ImprovementResultView } from "../components/ImprovementResultView";
import { JobPanel, TestReportView } from "../components/JobPanel";
import { JsonEditor, checkJson } from "../components/JsonEditor";
import {
  ErrorBox,
  Field,
  JsonView,
  KeyValue,
  Loading,
  LoadMore,
  Notice,
  Page,
  Section,
  Status,
  Table,
  Tabs,
} from "../components/ui";
import { formatDate, formatMoney, refLabel } from "../lib/format";
import { STRATEGY_LABELS } from "./RulesEditorPage";

const ACTIVE_STATUSES = new Set(["resolving", "sampling", "analyzing", "applying"]);
const ONBOARDING_STATUSES: OnboardingStatus[] = [
  "resolving",
  "needs_disambiguation",
  "sampling",
  "analyzing",
  "proposals_ready",
  "insufficient_sample",
  "applying",
  "completed",
  "failed",
  "cancelled",
];
const JOB_STATUSES: JobStatus[] = ["queued", "running", "cancelling", "succeeded", "failed", "cancelled"];

type AssistantTab = "onboarding" | "improvement";

/** The session of an onboarding Job: `labels.session_id`, or its `links.session` (/v1/onboarding-sessions/{id}). */
export function sessionIdFromJob(job: Job): string | null {
  const label = job.labels?.["session_id"];
  if (label) return label;
  for (const link of Object.values(job.links ?? {})) {
    const match = /\/v1\/onboarding-sessions\/([^/?#]+)/.exec(link);
    if (match?.[1]) return decodeURIComponent(match[1]);
  }
  return null;
}

function percent(value: number | undefined): string {
  return value === undefined ? "—" : `${Math.round(value * 100)}%`;
}

export function AssistantPage() {
  const [params, setParams] = useSearchParams();
  const tab: AssistantTab = params.get("tab") === "improvement" ? "improvement" : "onboarding";
  const update = (changes: Record<string, string | null>) => {
    const next = new URLSearchParams(params);
    for (const [key, value] of Object.entries(changes)) {
      if (value) next.set(key, value);
      else next.delete(key);
    }
    setParams(next);
  };
  return (
    <Page title="Асистент">
      <Tabs<AssistantTab>
        tabs={[
          ["onboarding", "Підключення джерел"],
          ["improvement", "Запуски вдосконалення"],
        ]}
        active={tab}
        onChange={(t) => update({ tab: t === "onboarding" ? null : t })}
      />
      {tab === "onboarding" ? (
        <Onboarding sessionId={params.get("session")} onOpen={(id) => update({ session: id })} />
      ) : (
        <ImprovementRuns jobId={params.get("job")} onOpen={(id) => update({ job: id })} />
      )}
    </Page>
  );
}

/** Research limits of the assistant (GET /v1/info -> limits, PlatformLimits): the ТЗ §8 sampling threshold. */
function OnboardingLimits() {
  const api = useApi();
  const info = useQuery({
    queryKey: ["info", "assistant"],
    queryFn: () => unwrap(api.assistant.GET("/v1/info")),
  });
  const defaults = info.data?.limits?.defaults.llm;
  const caps = info.data?.limits?.hard_caps?.llm;
  const budget = defaults?.budget;
  return (
    <Section title="Ліміти дослідження">
      {info.isLoading ? <Loading /> : null}
      <ErrorBox error={info.error} title="Ліміти асистента недоступні" />
      {info.data ? (
        <KeyValue
          rows={[
            [
              "Поріг достатності вибірки (min_onboarding_confidence)",
              <span data-testid="min-onboarding-confidence">
                {percent(defaults?.min_onboarding_confidence)}
                {caps?.min_onboarding_confidence !== undefined
                  ? ` (стеля ${percent(caps.min_onboarding_confidence)})`
                  : ""}
              </span>,
            ],
            [
              "Макс. сторінок вибірки (max_onboarding_samples)",
              String(defaults?.max_onboarding_samples ?? "—"),
            ],
            ["Бюджет LLM асистента", budget ? `${formatMoney(budget)} / ${budget.period}` : "—"],
            ["Профіль лімітів", info.data.limits?.profile ?? "—"],
          ]}
        />
      ) : null}
      <p className="muted">
        Асистент добирає вибірку, доки впевненість не досягне порога; не досягнуто в межах бюджету й
        max_onboarding_samples — сесія insufficient_sample. Поріг можна змінити для одного підключення нижче
        (hard_caps обмежують його зверху).
      </p>
    </Section>
  );
}

function Onboarding({ sessionId, onOpen }: { sessionId: string | null; onOpen: (id: string) => void }) {
  const api = useApi();
  const queryClient = useQueryClient();
  const [startJob, setStartJob] = useState<string | null>(null);
  const [form, setForm] = useState({
    query: "",
    source_kind: "",
    expected: "",
    amount: "",
    currency: "USD",
    samples: "",
    confidence: "",
    auto_activation: false,
    hints: "",
  });
  const hints = checkJson(form.hints);

  const start = useMutation({
    mutationFn: () => {
      const limits: NonNullable<OnboardingRequest["limits"]> = {
        ...(form.amount
          ? { budget: { amount: Number(form.amount), currency: form.currency, period: "total" as const } }
          : {}),
        ...(form.samples ? { max_onboarding_samples: Number.parseInt(form.samples, 10) } : {}),
        ...(form.confidence ? { min_onboarding_confidence: Number(form.confidence) } : {}),
      };
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
        ...(Object.keys(limits).length ? { limits } : {}),
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
      void queryClient.invalidateQueries({ queryKey: ["onboarding-sessions"] });
      const id = sessionIdFromJob(job);
      if (id) onOpen(id);
    },
  });

  return (
    <>
      <OnboardingLimits />
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
          <Field
            label="Поріг впевненості вибірки"
            hint="0–1; порожньо — поріг асистента (min_onboarding_confidence)"
          >
            <input
              type="number"
              min={0.01}
              max={1}
              step="0.05"
              value={form.confidence}
              onChange={(e) => setForm({ ...form, confidence: e.target.value })}
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
      <SessionList selected={sessionId} onOpen={onOpen} />
      {sessionId ? <SessionView key={sessionId} sessionId={sessionId} shownJob={startJob} /> : null}
    </>
  );
}

/** Sessions of the assistant, newest first (GET /v1/onboarding-sessions, cursor pagination). */
function SessionList({ selected, onOpen }: { selected: string | null; onOpen: (id: string) => void }) {
  const api = useApi();
  const [status, setStatus] = useState<OnboardingStatus | "">("");
  const [manualId, setManualId] = useState("");
  const list = useCursorList(["onboarding-sessions", status], (cursor, limit) =>
    unwrap(
      api.assistant.GET("/v1/onboarding-sessions", {
        params: {
          query: { limit, ...(cursor ? { cursor } : {}), ...(status ? { status: [status] } : {}) },
        },
      }),
    ),
  );
  return (
    <Section
      title="Сесії"
      actions={
        <button type="button" className="btn btn-small" onClick={list.refetch}>
          Оновити список
        </button>
      }
    >
      <div className="filters">
        <Field label="Стан сесії">
          <select value={status} onChange={(e) => setStatus(e.target.value as OnboardingStatus | "")}>
            <option value="">усі</option>
            {ONBOARDING_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </Field>
        <div className="inline-form">
          <Field label="Відкрити сесію за ідентифікатором">
            <input value={manualId} onChange={(e) => setManualId(e.target.value)} placeholder="onb_…" />
          </Field>
          <button
            type="button"
            className="btn"
            disabled={!manualId.trim()}
            onClick={() => {
              onOpen(manualId.trim());
              setManualId("");
            }}
          >
            Відкрити
          </button>
        </div>
      </div>
      {list.isLoading ? <Loading /> : null}
      <ErrorBox error={list.error} title="Список сесій недоступний" />
      <Table
        label="Сесії підключення"
        rows={list.items}
        rowKey={(s) => s.session_id}
        empty="Сесій ще немає"
        columns={[
          {
            header: "Сесія",
            cell: (s) => (
              <button
                type="button"
                className={s.session_id === selected ? "link link-active" : "link"}
                onClick={() => onOpen(s.session_id)}
              >
                {s.session_id}
              </button>
            ),
          },
          { header: "Запит", cell: (s) => s.query },
          { header: "Стан", cell: (s) => <Status value={s.status} /> },
          { header: "Варіантів", cell: (s) => String(s.proposal_count ?? "—") },
          { header: "Витрати LLM", cell: (s) => formatMoney(s.costs) },
          { header: "Створено", cell: (s) => formatDate(s.created_at) },
          {
            header: "Помилка",
            cell: (s) => (s.error ? <code>{safeProblemCode(s.error.code)}</code> : "—"),
          },
        ]}
      />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
    </Section>
  );
}

/** Improvement runs of the assistant with filters; the chosen run's result (ImprovementResult, proposal). */
function ImprovementRuns({ jobId, onOpen }: { jobId: string | null; onOpen: (id: string) => void }) {
  const api = useApi();
  const [filter, setFilter] = useState({ package_id: "", source_id: "", problem_group_id: "", status: "" });
  return (
    <>
      <Section title="Запуски вдосконалення екстракторів">
        <p className="muted">
          Job вдосконалення на проблемних прикладах (запускаються з розділу «Проблеми»), новіші першими.
        </p>
        <div className="filters">
          <Field label="Пакет (package_id)">
            <input
              value={filter.package_id}
              onChange={(e) => setFilter({ ...filter, package_id: e.target.value.trim() })}
            />
          </Field>
          <Field label="Джерело (source_id)">
            <input
              value={filter.source_id}
              onChange={(e) => setFilter({ ...filter, source_id: e.target.value.trim() })}
            />
          </Field>
          <Field label="Група проблем (problem_group_id)">
            <input
              value={filter.problem_group_id}
              onChange={(e) => setFilter({ ...filter, problem_group_id: e.target.value.trim() })}
            />
          </Field>
          <Field label="Стан job">
            <select value={filter.status} onChange={(e) => setFilter({ ...filter, status: e.target.value })}>
              <option value="">усі</option>
              {JOB_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </Field>
        </div>
        <ImprovementRunList
          filter={{
            ...(filter.package_id ? { package_id: filter.package_id } : {}),
            ...(filter.source_id ? { source_id: filter.source_id } : {}),
            ...(filter.problem_group_id ? { problem_group_id: filter.problem_group_id } : {}),
            ...(filter.status ? { status: filter.status as JobStatus } : {}),
          }}
          label="Запуски вдосконалення"
          selected={jobId}
          onOpen={onOpen}
        />
      </Section>
      {jobId ? (
        <JobPanel
          key={jobId}
          service="assistant"
          client={api.assistant}
          jobId={jobId}
          title="Вдосконалення"
          renderResult={(result) => <ImprovementResultView result={result} />}
        />
      ) : null}
    </>
  );
}

/** Job.result of acceptProposal (AcceptanceResult); the other jobs of a session return the session itself. */
function isAcceptance(result: Record<string, unknown>): boolean {
  return Array.isArray(result["extractors"]) && typeof result["collector_rules"] === "object";
}

function SessionView({ sessionId, shownJob }: { sessionId: string; shownJob: string | null }) {
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
    onSuccess: (job) => {
      setAcceptJob(job.job_id);
      void queryClient.invalidateQueries({ queryKey: ["onboarding", sessionId] });
    },
  });
  const s: OnboardingSession | undefined = session.data;
  const status = s?.status;
  // The list shows the stored state of every session: refresh it whenever this session changes its state.
  useEffect(() => {
    if (status) void queryClient.invalidateQueries({ queryKey: ["onboarding-sessions"] });
  }, [status, queryClient]);
  const lastJob = s?.job_id && s.job_id !== shownJob && s.job_id !== acceptJob ? s.job_id : null;
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
          {s.error ? <ErrorBox error={s.error} title="Помилка сесії" /> : null}
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
              {s.sample.message ? `. ${s.sample.message}` : ""}
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
          {lastJob ? (
            // After a reload: the latest job of the session (continuation after the choice, or the acceptance).
            <JobPanel
              key={lastJob}
              service="assistant"
              client={api.assistant}
              jobId={lastJob}
              title="Останній job сесії"
              renderResult={(result) =>
                isAcceptance(result) ? (
                  <AcceptanceView result={result as unknown as AcceptanceResult} />
                ) : (
                  <p className="muted">Результат job — стан сесії вище.</p>
                )
              }
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
      {result.activated && result.source_draft ? (
        <p>
          Джерело:{" "}
          <Link to={`/sources/${encodeURIComponent(result.source_draft.source_id)}`}>
            {result.source_draft.source_id}
          </Link>
          {(result.task_drafts ?? []).map((t) => (
            <span key={t.task_id}>
              , завдання <Link to={`/tasks/${encodeURIComponent(t.task_id)}`}>{t.task_id}</Link>
            </span>
          ))}
        </p>
      ) : null}
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
      {createTask.data ? (
        <Link to={`/tasks/${encodeURIComponent(createTask.data.task_id)}`}> Завдання створено</Link>
      ) : null}
      <ErrorBox error={createTask.error} />
    </div>
  );
}
