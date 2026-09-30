import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useApi } from "../app/context";
import { ifMatch, newIdempotencyKey, unwrap, unwrapWithEtag } from "../api/client";
import { useCursorList } from "../api/hooks";
import type { Job, RunRequest, Stage, TaskConfig, TaskValidation } from "../api/types";
import { DagView } from "../components/DagView";
import { EffectiveLimitsView } from "../components/EffectiveLimitsView";
import { JsonEditor, checkJson, toJsonText } from "../components/JsonEditor";
import { ScheduleEditor } from "../components/ScheduleEditor";
import { StageVersions } from "../components/StageVersions";
import {
  ErrorBox,
  Field,
  Loading,
  LoadMore,
  Notice,
  Page,
  ReasonAction,
  Section,
  Status,
  Table,
  Tabs,
} from "../components/ui";
import { SCHEMAS, validateAgainst } from "../lib/schema";
import { formatDate, refLabel } from "../lib/format";

function scheduleLabel(schedule: TaskConfig["schedule"]): string {
  if (!schedule || schedule.type === "manual") return "вручну";
  if (schedule.type === "cron") return `cron ${schedule.cron ?? ""} ${schedule.timezone ?? ""}`.trim();
  if (schedule.type === "interval") return `кожні ${schedule.interval_seconds ?? "?"} с`;
  return `одноразово ${schedule.at ?? ""}`;
}

export function TasksPage() {
  const api = useApi();
  const [params, setParams] = useSearchParams();
  const sourceId = params.get("source_id") ?? "";
  const packageId = params.get("package_id") ?? "";
  const list = useCursorList(["tasks", sourceId, packageId], (cursor, limit) =>
    unwrap(
      api.orchestrator.GET("/v1/tasks", {
        params: {
          query: {
            limit,
            ...(cursor ? { cursor } : {}),
            ...(sourceId ? { source_id: sourceId } : {}),
            ...(packageId ? { package_id: packageId } : {}),
          },
        },
      }),
    ),
  );
  return (
    <Page
      title="Завдання"
      actions={
        <Link className="btn btn-primary" to="/tasks/new">
          Нове завдання
        </Link>
      }
    >
      <div className="filters">
        <Field label="Джерело">
          <input
            value={sourceId}
            onChange={(e) => setParams(e.target.value ? { source_id: e.target.value } : {})}
          />
        </Field>
        {packageId ? (
          <span>
            Прив'язки пакета <code>{packageId}</code>{" "}
            <button type="button" className="btn btn-small" onClick={() => setParams({})}>
              скинути
            </button>
          </span>
        ) : null}
      </div>
      {list.isLoading ? <Loading /> : null}
      <ErrorBox error={list.error} />
      <Table
        label="Завдання"
        rows={list.items}
        rowKey={(t) => t.task_id}
        columns={[
          {
            header: "Завдання",
            cell: (t) => <Link to={`/tasks/${encodeURIComponent(t.task_id)}`}>{t.task_id}</Link>,
          },
          { header: "Назва", cell: (t) => t.title },
          {
            header: "Джерело",
            cell: (t) => <Link to={`/sources/${encodeURIComponent(t.source_id)}`}>{t.source_id}</Link>,
          },
          { header: "Розклад", cell: (t) => scheduleLabel(t.schedule) },
          { header: "Наступний запуск", cell: (t) => formatDate(t.next_run_at) },
          {
            header: "Останній запуск",
            cell: (t) => (t.last_run ? <Status value={t.last_run.status ?? null} /> : "—"),
          },
          { header: "Увімкнено", cell: (t) => (t.enabled ? "так" : "ні") },
          ...(packageId
            ? [
                {
                  header: "Етапи з пакетом",
                  cell: (t: (typeof list.items)[number]) =>
                    (t.package_stages ?? []).map((s) => `${s.stage_id} (${refLabel(s.package)})`).join(", "),
                },
              ]
            : []),
        ]}
      />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
    </Page>
  );
}

const NEW_TASK: TaskConfig = {
  task_id: "",
  title: "",
  enabled: true,
  input: { source_id: "" },
  stages: [{ stage_id: "collect", kind: "collect", collector: { collector: "web", mode: "full" } }],
};

type TabKey = "config" | "chain" | "runs" | "versions" | "limits";

export function TaskPage() {
  const { taskId } = useParams();
  const isNew = !taskId;
  const api = useApi();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<TabKey>("config");

  const loaded = useQuery({
    queryKey: ["task", taskId],
    enabled: !isNew,
    queryFn: () =>
      unwrapWithEtag(
        api.orchestrator.GET("/v1/tasks/{task_id}", { params: { path: { task_id: taskId as string } } }),
      ),
  });

  const [draft, setDraft] = useState<TaskConfig>(NEW_TASK);
  const [stagesText, setStagesText] = useState(toJsonText(NEW_TASK.stages));
  const [limitsText, setLimitsText] = useState("");
  const [retriesText, setRetriesText] = useState("");
  const [urlsText, setUrlsText] = useState("");
  const [validation, setValidation] = useState<TaskValidation | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const task = loaded.data?.data;
    if (!task) return;
    setDraft(task);
    setStagesText(toJsonText(task.stages));
    setLimitsText(toJsonText(task.limits));
    setRetriesText(toJsonText(task.retries));
    setUrlsText((task.input.urls ?? []).join("\n"));
  }, [loaded.data]);

  const assembled = useMemo(() => {
    const stages = checkJson(stagesText);
    const limits = checkJson(limitsText, SCHEMAS.limits);
    const retries = checkJson(retriesText);
    const errors = [stages, limits, retries].filter((c) => c.parseError).map((c) => c.parseError as string);
    if (errors.length) return { task: null as TaskConfig | null, issues: errors.map((e) => `JSON: ${e}`) };
    const urls = urlsText
      .split(/\s+/)
      .map((u) => u.trim())
      .filter(Boolean);
    const task: TaskConfig = {
      ...draft,
      input: { ...draft.input, ...(urls.length ? { urls } : {}) },
      stages: (stages.value as Stage[] | undefined) ?? [],
    };
    if (!urls.length) delete task.input.urls;
    if (limits.value !== undefined) task.limits = limits.value as NonNullable<TaskConfig["limits"]>;
    else delete task.limits;
    if (retries.value !== undefined) task.retries = retries.value as NonNullable<TaskConfig["retries"]>;
    else delete task.retries;
    const issues = validateAgainst(SCHEMAS.task, task).map((i) => `${i.pointer} ${i.message}`);
    return { task, issues };
  }, [draft, stagesText, limitsText, retriesText, urlsText]);

  const validate = useMutation({
    mutationFn: (task: TaskConfig) => unwrap(api.orchestrator.POST("/v1/task-validations", { body: task })),
    onSuccess: setValidation,
  });

  const save = useMutation({
    mutationFn: (task: TaskConfig) =>
      isNew
        ? unwrapWithEtag(
            api.orchestrator.POST("/v1/tasks", {
              params: { header: { "Idempotency-Key": newIdempotencyKey() } },
              body: task,
            }),
          )
        : unwrapWithEtag(
            api.orchestrator.PUT("/v1/tasks/{task_id}", {
              params: { path: { task_id: taskId as string }, header: ifMatch(loaded.data?.etag) },
              body: task,
            }),
          ),
    onSuccess: (result) => {
      setSaved(true);
      void queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.setQueryData(["task", result.data.task_id], result);
      if (isNew) navigate(`/tasks/${encodeURIComponent(result.data.task_id)}`, { replace: true });
    },
  });

  const remove = useMutation({
    mutationFn: () =>
      unwrap(
        api.orchestrator.DELETE("/v1/tasks/{task_id}", { params: { path: { task_id: taskId as string } } }),
      ),
    onSuccess: () => navigate("/tasks"),
  });

  const set = (patch: Partial<TaskConfig>) => {
    setSaved(false);
    setDraft((d) => ({ ...d, ...patch }));
  };

  if (!isNew && loaded.isLoading) return <Loading />;
  const currentStages = (checkJson(stagesText).value as Stage[] | undefined) ?? draft.stages;

  return (
    <Page
      title={isNew ? "Нове завдання" : `Завдання ${taskId}`}
      actions={
        !isNew ? (
          <ReasonAction
            label="Видалити"
            confirmLabel="Видалити завдання"
            danger
            requireReason={false}
            onConfirm={() => remove.mutate()}
          />
        ) : null
      }
    >
      <ErrorBox error={loaded.error} />
      <ErrorBox error={remove.error} title="Не вдалося видалити" />
      <Tabs<TabKey>
        tabs={
          isNew
            ? [
                ["config", "Конфігурація"],
                ["chain", "Ланцюжок"],
              ]
            : [
                ["config", "Конфігурація"],
                ["chain", "Ланцюжок"],
                ["runs", "Запуски"],
                ["versions", "Версії етапів"],
                ["limits", "Ефективні ліміти"],
              ]
        }
        active={tab}
        onChange={setTab}
      />
      {tab === "config" || tab === "chain" ? (
        <form
          className="form"
          onSubmit={(e) => {
            e.preventDefault();
            if (assembled.task && !assembled.issues.length) save.mutate(assembled.task);
          }}
        >
          {tab === "config" ? (
            <>
              <div className="grid-2">
                <Field label="Ідентифікатор (task_id)">
                  <input
                    value={draft.task_id}
                    disabled={!isNew}
                    onChange={(e) => set({ task_id: e.target.value })}
                    required
                  />
                </Field>
                <Field label="Назва">
                  <input
                    value={draft.title}
                    onChange={(e) => set({ title: e.target.value })}
                    required
                    maxLength={200}
                  />
                </Field>
                <Field label="Джерело (source_id)">
                  <input
                    value={draft.input.source_id}
                    onChange={(e) => set({ input: { ...draft.input, source_id: e.target.value } })}
                    required
                  />
                </Field>
                <Field label="Передавати в LLM невідомі сторінки">
                  <select
                    value={
                      draft.forward_unknown_to_llm === undefined
                        ? "inherit"
                        : draft.forward_unknown_to_llm
                          ? "on"
                          : "off"
                    }
                    onChange={(e) => {
                      const next = { ...draft };
                      if (e.target.value === "inherit") delete next.forward_unknown_to_llm;
                      else next.forward_unknown_to_llm = e.target.value === "on";
                      setSaved(false);
                      setDraft(next);
                    }}
                  >
                    <option value="inherit">як у джерела</option>
                    <option value="on">увімкнено</option>
                    <option value="off">вимкнено</option>
                  </select>
                </Field>
                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={draft.enabled !== false}
                    onChange={(e) => set({ enabled: e.target.checked })}
                  />
                  Завдання увімкнено
                </label>
              </div>
              <Field label="Явний перелік URL (замість правил джерела; по одному в рядку)">
                <textarea
                  rows={3}
                  value={urlsText}
                  onChange={(e) => (setSaved(false), setUrlsText(e.target.value))}
                />
              </Field>
              <Section title="Розклад">
                <ScheduleEditor
                  value={draft.schedule}
                  onChange={(schedule) => {
                    const next = { ...draft };
                    if (schedule) next.schedule = schedule;
                    else delete next.schedule;
                    setSaved(false);
                    setDraft(next);
                  }}
                />
              </Section>
              <div className="grid-2">
                <Section title="Ліміти рівня завдання">
                  <JsonEditor
                    text={limitsText}
                    onChange={(t) => (setSaved(false), setLimitsText(t))}
                    schema={SCHEMAS.limits}
                    label="Ліміти завдання"
                    minHeight="8rem"
                  />
                </Section>
                <Section title="Повторні спроби">
                  <JsonEditor
                    text={retriesText}
                    onChange={(t) => (setSaved(false), setRetriesText(t))}
                    label="Повторні спроби"
                    minHeight="8rem"
                  />
                </Section>
              </div>
            </>
          ) : null}
          {tab === "chain" ? (
            <>
              <Section title="Ланцюжок обробки (етапи й переходи)">
                <DagView stages={currentStages} />
              </Section>
              <Section
                title="Етапи (TaskConfig.stages)"
                actions={
                  <button
                    type="button"
                    className="btn"
                    onClick={() => {
                      const stages = (checkJson(stagesText).value as Stage[] | undefined) ?? [];
                      const from = stages[stages.length - 1]?.stage_id ?? "collect";
                      const stage: Stage = {
                        stage_id: `stage-${stages.length + 1}`,
                        kind: "handler",
                        handler: { package_id: "", version: "" },
                        inputs: [{ from }],
                      };
                      setSaved(false);
                      setStagesText(toJsonText([...stages, stage]));
                    }}
                  >
                    Додати етап-обробник
                  </button>
                }
              >
                <p className="muted">
                  Кожен етап посилається на точну версію пакета. Розгалуження — кілька етапів з тим самим{" "}
                  <code>inputs[].from</code>; умови — <code>when</code>; вибірка — <code>select</code>{" "}
                  (output, input_material, problems, unmatched_materials).
                </p>
                <JsonEditor
                  text={stagesText}
                  onChange={(t) => (setSaved(false), setStagesText(t))}
                  label="Етапи завдання"
                  minHeight="20rem"
                />
              </Section>
            </>
          ) : null}
          {assembled.issues.length ? (
            <ul className="error-inline" role="alert" aria-label="Помилки конфігурації">
              {assembled.issues.map((i) => (
                <li key={i}>{i}</li>
              ))}
            </ul>
          ) : null}
          <div className="button-row">
            <button
              type="button"
              className="btn"
              disabled={!assembled.task || validate.isPending}
              onClick={() => assembled.task && validate.mutate(assembled.task)}
            >
              Перевірити в оркестраторі
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={save.isPending || !assembled.task || assembled.issues.length > 0}
            >
              {isNew ? "Створити завдання" : "Зберегти"}
            </button>
          </div>
          <ErrorBox error={validate.error} title="Перевірка не вдалася" />
          <ErrorBox error={save.error} title="Не вдалося зберегти" />
          {saved ? (
            <Notice tone="ok">Збережено. Поточні запуски продовжуються зі старою конфігурацією.</Notice>
          ) : null}
          {validation ? <ValidationView validation={validation} /> : null}
        </form>
      ) : null}
      {tab === "runs" && taskId ? <TaskRuns taskId={taskId} /> : null}
      {tab === "versions" && loaded.data ? <StageVersions task={loaded.data.data} /> : null}
      {tab === "limits" && taskId ? <EffectiveLimitsView query={{ task_id: taskId }} /> : null}
    </Page>
  );
}

function ValidationView({ validation }: { validation: TaskValidation }) {
  return (
    <div className="validation" aria-label="Результат перевірки">
      <p>
        Конфігурація: <Status value={validation.valid ? "ok" : "failed"} />{" "}
        {validation.effective_forward_unknown_to_llm !== undefined ? (
          <span>
            Ефективне «Передавати в LLM невідомі сторінки»:{" "}
            <strong>{validation.effective_forward_unknown_to_llm ? "так" : "ні"}</strong>
          </span>
        ) : null}
      </p>
      {[
        ...validation.errors.map((e) => ["error", e] as const),
        ...(validation.warnings ?? []).map((w) => ["warning", w] as const),
      ].map(([level], i) => (
        <p key={i} className={level === "error" ? "error-inline" : "warn-inline"}>
          {level === "error" ? "Помилка" : "Попередження"}: Перевірте конфігурацію завдання.
        </p>
      ))}
    </div>
  );
}

function TaskRuns({ taskId }: { taskId: string }) {
  const api = useApi();
  const navigate = useNavigate();
  const [reason, setReason] = useState("");
  const [testMode, setTestMode] = useState(false);
  const [urls, setUrls] = useState("");
  const list = useCursorList(["runs", taskId], (cursor, limit) =>
    unwrap(
      api.orchestrator.GET("/v1/runs", {
        params: { query: { task_id: taskId, limit, ...(cursor ? { cursor } : {}) } },
      }),
    ),
  );
  const start = useMutation({
    mutationFn: (body: RunRequest) =>
      unwrap(
        api.orchestrator.POST("/v1/tasks/{task_id}/runs", {
          params: { path: { task_id: taskId }, header: { "Idempotency-Key": newIdempotencyKey() } },
          body,
        }),
      ) as Promise<Job>,
    onSuccess: (job) => navigate(`/runs/${encodeURIComponent(job.job_id)}`),
  });
  return (
    <>
      <Section title="Запустити зараз">
        <div className="grid-3">
          <Field label="Причина">
            <input value={reason} onChange={(e) => setReason(e.target.value)} maxLength={1000} />
          </Field>
          <Field label="URL для цього запуску (необов'язково)">
            <input
              value={urls}
              onChange={(e) => setUrls(e.target.value)}
              placeholder="https://… через пробіл"
            />
          </Field>
          <label className="checkbox">
            <input type="checkbox" checked={testMode} onChange={(e) => setTestMode(e.target.checked)} />
            Тестовий режим (без запису в робочі дані)
          </label>
        </div>
        <button
          type="button"
          className="btn btn-primary"
          disabled={start.isPending}
          onClick={() => {
            const list = urls.split(/\s+/).filter(Boolean);
            start.mutate({
              ...(reason ? { reason } : {}),
              ...(testMode ? { test_mode: true } : {}),
              ...(list.length ? { input_override: { urls: list } } : {}),
            });
          }}
        >
          Запустити
        </button>
        <ErrorBox error={start.error} title="Не вдалося запустити" />
      </Section>
      <Section title="Історія запусків">
        <ErrorBox error={list.error} />
        <Table
          label="Запуски завдання"
          rows={list.items}
          rowKey={(r) => r.run_id}
          columns={[
            {
              header: "Запуск",
              cell: (r) => <Link to={`/runs/${encodeURIComponent(r.run_id)}`}>{r.run_id}</Link>,
            },
            { header: "Стан", cell: (r) => <Status value={r.status} /> },
            { header: "Тригер", cell: (r) => r.trigger },
            { header: "Тест", cell: (r) => (r.test_mode ? "так" : "") },
            { header: "Створено", cell: (r) => formatDate(r.created_at) },
          ]}
        />
        <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
      </Section>
    </>
  );
}
