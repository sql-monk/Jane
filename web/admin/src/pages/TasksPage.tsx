import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useApi } from "../app/context";
import { ifMatch, newIdempotencyKey, unwrap, unwrapWithEtag } from "../api/client";
import { useCursorList } from "../api/hooks";
import type { Job, RunRequest, Stage, TaskConfig, TaskValidation } from "../api/types";
import { ChainEditor } from "../components/ChainEditor";
import { buildDag } from "../lib/dag";
import { EffectiveLimitsView } from "../components/EffectiveLimitsView";
import { JsonEditor, checkJson, toJsonText } from "../components/JsonEditor";
import { ScheduleEditor } from "../components/ScheduleEditor";
import { StageVersions } from "../components/StageVersions";
import { TaskQuickRun } from "../components/TaskQuickRun";
import {
  ErrorBox,
  Field,
  Loading,
  LoadMore,
  Notice,
  JsonView,
  Page,
  ReasonAction,
  Section,
  Status,
  Table,
  Tabs,
} from "../components/ui";
import { SCHEMAS, validateAgainst } from "../lib/schema";
import { formatDate, refLabel } from "../lib/format";
import { useUnsavedChanges } from "../components/UnsavedChanges";
import { EntityPicker } from "../components/EntityPicker";
import { schemaIssueLabel } from "../lib/schema";
import { useSourceOptions } from "../lib/pickers";
import { resultsHref } from "../lib/results-context";

function scheduleLabel(schedule: TaskConfig["schedule"]): string {
  if (!schedule || schedule.type === "manual") return "вручну";
  if (schedule.type === "cron") return `cron ${schedule.cron ?? ""} ${schedule.timezone ?? ""}`.trim();
  if (schedule.type === "interval") return `кожні ${schedule.interval_seconds ?? "?"} с`;
  return `одноразово ${schedule.at ?? ""}`;
}

export function TasksPage() {
  const api = useApi();
  const sources = useSourceOptions();
  const [params, setParams] = useSearchParams();
  const sourceId = params.get("source_id") ?? "";
  const packageId = params.get("package_id") ?? "";
  const [search, setSearch] = useState("");
  const [enabled, setEnabled] = useState("");
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
  const filtered = list.items.filter(
    (task) =>
      `${task.task_id} ${task.title} ${task.source_id}`
        .toLocaleLowerCase("uk")
        .includes(search.toLocaleLowerCase("uk")) &&
      (!enabled || task.enabled === (enabled === "on")),
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
        <Field label="Пошук у завантажених завданнях">
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Назва або ідентифікатор…"
          />
        </Field>
        <Field label="Активність">
          <select value={enabled} onChange={(event) => setEnabled(event.target.value)}>
            <option value="">Усі завдання</option>
            <option value="on">Увімкнені</option>
            <option value="off">Призупинені</option>
          </select>
        </Field>
        <EntityPicker
          label="Джерело"
          value={sourceId}
          options={sources.options}
          loading={sources.isLoading}
          error={sources.error}
          onChange={(value) => {
            const next = new URLSearchParams(params);
            if (value) next.set("source_id", value);
            else next.delete("source_id");
            setParams(next);
          }}
        />
        <LoadMore hasMore={sources.hasMore} loading={sources.loadingMore} onClick={sources.loadMore} />
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
      <div className="list-summary">
        <span>
          Завантажено <strong>{list.isLoading || list.error ? "—" : list.items.length}</strong>
          {list.hasMore ? "+" : ""}
        </span>
        <span>
          Увімкнено{" "}
          <strong>
            {list.isLoading || list.error ? "—" : list.items.filter((task) => task.enabled).length}
          </strong>
        </span>
        <button className="btn btn-small" type="button" onClick={list.refetch}>
          Оновити список
        </button>
      </div>
      <Table
        label="Завдання"
        rows={filtered}
        empty={
          list.error
            ? "Дані завдань недоступні. Спробуйте оновити список."
            : list.isLoading
              ? "Завантаження завдань…"
              : search || enabled
                ? "Збігів у завантажених завданнях немає. Змініть фільтри або завантажте наступну сторінку."
                : "Завдань ще немає. Створіть завдання, щоб налаштувати збір, обробку та розклад."
        }
        rowKey={(t) => t.task_id}
        columns={[
          {
            header: "Завдання",
            cell: (t) => (
              <Link title={t.task_id} to={`/tasks/${encodeURIComponent(t.task_id)}`}>
                {t.task_id}
              </Link>
            ),
          },
          { header: "Назва", cell: (t) => t.title },
          {
            header: "Джерело",
            cell: (t) => (
              <Link title={t.source_id} to={`/sources/${encodeURIComponent(t.source_id)}`}>
                {t.source_id}
              </Link>
            ),
          },
          { header: "Розклад", cell: (t) => scheduleLabel(t.schedule) },
          { header: "Наступний запуск", cell: (t) => formatDate(t.next_run_at) },
          {
            header: "Останній запуск",
            cell: (t) => (t.last_run ? <Status value={t.last_run.status ?? null} /> : "—"),
          },
          { header: "Увімкнено", cell: (t) => (t.enabled ? "так" : "ні") },
          {
            header: "Дії",
            cell: (task) => (
              <div className="button-row row-actions">
                <TaskQuickRun taskId={task.task_id} />
                <Link className="btn btn-small" to={`/runs?task_id=${encodeURIComponent(task.task_id)}`}>
                  Історія
                </Link>
              </div>
            ),
          },
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
  const [chainValid, setChainValid] = useState(true);
  const [modified, setDirty] = useState(false);
  const [baseline, setBaseline] = useState(
    JSON.stringify([NEW_TASK, toJsonText(NEW_TASK.stages), "", "", ""]),
  );
  const snapshot = JSON.stringify([draft, stagesText, limitsText, retriesText, urlsText]);
  const dirty = modified && snapshot !== baseline;
  const [submitted, setSubmitted] = useState(false);
  const sources = useCursorList(["source-options"], (cursor, limit) =>
    unwrap(
      api.orchestrator.GET("/v1/sources", { params: { query: { limit, ...(cursor ? { cursor } : {}) } } }),
    ),
  );
  const selectedSource = useQuery({
    queryKey: ["source", draft.input.source_id],
    enabled: Boolean(draft.input.source_id),
    queryFn: () =>
      unwrapWithEtag(
        api.orchestrator.GET("/v1/sources/{source_id}", {
          params: { path: { source_id: draft.input.source_id } },
        }),
      ),
  });

  useEffect(() => {
    const task = loaded.data?.data;
    if (!task || dirty) return;
    setDraft(task);
    setStagesText(toJsonText(task.stages));
    setLimitsText(toJsonText(task.limits));
    setRetriesText(toJsonText(task.retries));
    setUrlsText((task.input.urls ?? []).join("\n"));
    setBaseline(
      JSON.stringify([
        task,
        toJsonText(task.stages),
        toJsonText(task.limits),
        toJsonText(task.retries),
        (task.input.urls ?? []).join("\n"),
      ]),
    );
  }, [loaded.data, dirty]);

  const assembled = useMemo(() => {
    const stages = checkJson(stagesText);
    const limits = checkJson(limitsText, SCHEMAS.limits);
    const retries = checkJson(retriesText);
    const errors = [stages, limits, retries].filter((c) => c.parseError).map((c) => c.parseError as string);
    if (errors.length)
      return { task: null as TaskConfig | null, issues: errors.map((e) => `JSON: ${e}`), fieldIssues: [] };
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
    const fieldIssues = validateAgainst(SCHEMAS.task, task);
    const issues = fieldIssues.map(schemaIssueLabel);
    if (
      Array.isArray(task.stages) &&
      task.stages.every(
        (s) =>
          s &&
          typeof s.stage_id === "string" &&
          (!s.inputs || (Array.isArray(s.inputs) && s.inputs.every((i) => i && typeof i.from === "string"))),
      )
    )
      issues.push(...buildDag(task.stages).issues);
    return { task, issues, fieldIssues };
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
      guard.markSaved();
      setDirty(false);
      setSubmitted(false);
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
    onSuccess: () => {
      guard.markSaved();
      navigate("/tasks");
    },
  });

  const set = (patch: Partial<TaskConfig>) => {
    setSaved(false);
    setDirty(true);
    setDraft((d) => ({ ...d, ...patch }));
  };
  const guard = useUnsavedChanges({
    dirty: dirty || !chainValid,
    label: draft.title || "Завдання",
    onDiscard: () => {
      setDirty(false);
      setChainValid(true);
    },
    onSave: async () => {
      setSubmitted(true);
      if (!chainValid || !assembled.task || assembled.issues.length) return false;
      await save.mutateAsync(assembled.task);
      return true;
    },
  });

  if (!isNew && loaded.isLoading) return <Loading />;

  const fieldError = (pointer: string) =>
    submitted ? assembled.fieldIssues.find((issue) => issue.pointer === pointer)?.message : undefined;

  return (
    <Page
      title={isNew ? "Нове завдання" : `Завдання ${taskId}`}
      actions={
        !isNew ? (
          <>
            <Link className="btn" to="/results">
              Каталог результатів
            </Link>
            <ReasonAction
              label="Видалити"
              confirmLabel="Видалити завдання"
              danger
              busy={save.isPending || remove.isPending}
              requireReason={false}
              onConfirm={() => remove.mutate()}
            />
          </>
        ) : null
      }
    >
      <ErrorBox error={loaded.error} />
      <ErrorBox error={remove.error} title="Не вдалося видалити" />
      {!isNew && loaded.data ? <TaskResultsLinks task={loaded.data.data} /> : null}
      {dirty || !chainValid ? (
        <Notice tone="warn">
          Є незбережені зміни конфігурації. Вони залишаються у чернетці між вкладками.
        </Notice>
      ) : null}
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
        onChange={(next) => {
          if (chainValid && !save.isPending) setTab(next);
        }}
      />
      {tab === "config" || tab === "chain" ? (
        <form
          className="form"
          noValidate
          onSubmit={(e) => {
            e.preventDefault();
            setSubmitted(true);
            if (chainValid && assembled.task && !assembled.issues.length) save.mutate(assembled.task);
          }}
        >
          <fieldset className="form-fields" disabled={save.isPending}>
            {tab === "config" ? (
              <>
                <div className="grid-2">
                  <Field label="Ідентифікатор (task_id)" error={fieldError("/task_id")}>
                    <input
                      value={draft.task_id}
                      disabled={!isNew}
                      onChange={(e) => set({ task_id: e.target.value })}
                      required
                    />
                  </Field>
                  <Field label="Назва" error={fieldError("/title")}>
                    <input
                      value={draft.title}
                      onChange={(e) => set({ title: e.target.value })}
                      required
                      maxLength={200}
                    />
                  </Field>
                  <div>
                    <EntityPicker
                      label="Джерело (source_id)"
                      value={draft.input.source_id}
                      onChange={(source_id) => set({ input: { ...draft.input, source_id } })}
                      options={sources.items.map((source) => ({
                        value: source.source_id,
                        label: source.title,
                        description: source.locator.url ?? source.locator.telegram_username ?? source.kind,
                      }))}
                      loading={sources.isLoading}
                      error={sources.error}
                      validationError={fieldError("/input/source_id")}
                      required
                    />
                    <LoadMore
                      hasMore={sources.hasMore}
                      loading={sources.loadingMore}
                      onClick={sources.loadMore}
                    />
                  </div>
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
                        setDirty(true);
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
                    onChange={(e) => (setSaved(false), setDirty(true), setUrlsText(e.target.value))}
                  />
                </Field>
                <Section title="Розклад">
                  <ScheduleEditor
                    value={draft.schedule}
                    issues={submitted ? assembled.fieldIssues : []}
                    onChange={(schedule) => {
                      const next = { ...draft };
                      if (schedule) next.schedule = schedule;
                      else delete next.schedule;
                      setSaved(false);
                      setDirty(true);
                      setDraft(next);
                    }}
                  />
                </Section>
                <details className="form-advanced">
                  <summary>Додатково: ліміти та повторні спроби</summary>
                  <div className="grid-2">
                    <Section title="Ліміти рівня завдання">
                      <JsonEditor
                        text={limitsText}
                        onChange={(t) => (setSaved(false), setDirty(true), setLimitsText(t))}
                        schema={SCHEMAS.limits}
                        label="Ліміти завдання"
                        minHeight="8rem"
                        readOnly={save.isPending}
                      />
                    </Section>
                    <Section title="Повторні спроби">
                      <JsonEditor
                        text={retriesText}
                        onChange={(t) => (setSaved(false), setDirty(true), setRetriesText(t))}
                        label="Повторні спроби"
                        minHeight="8rem"
                        readOnly={save.isPending}
                      />
                    </Section>
                  </div>
                </details>
              </>
            ) : null}
            {tab === "chain" ? (
              <>
                <ChainEditor
                  onValidityChange={setChainValid}
                  text={stagesText}
                  source={selectedSource.data?.data}
                  readOnly={save.isPending}
                  onChange={(t) => {
                    setSaved(false);
                    setDirty(true);
                    setStagesText(t);
                  }}
                />
              </>
            ) : null}
            {(submitted || (tab === "chain" && dirty)) && assembled.issues.length ? (
              <ul className="error-inline" role="alert" aria-label="Помилки конфігурації">
                {assembled.issues.map((i) => (
                  <li key={i}>{i}</li>
                ))}
              </ul>
            ) : null}
            <div className="button-row form-save-bar">
              {dirty ? <span role="status">Є незбережені зміни</span> : null}
              <button
                type="button"
                className="btn"
                disabled={!chainValid || !assembled.task || validate.isPending}
                onClick={() => {
                  setSubmitted(true);
                  if (chainValid && assembled.task) validate.mutate(assembled.task);
                }}
              >
                Перевірити в оркестраторі
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={
                  !chainValid ||
                  save.isPending ||
                  (tab === "chain" && (!assembled.task || assembled.issues.length > 0))
                }
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
          </fieldset>
        </form>
      ) : null}
      {tab === "runs" && taskId ? <TaskRuns taskId={taskId} /> : null}
      {tab === "versions" && loaded.data ? <StageVersions task={loaded.data.data} /> : null}
      {tab === "limits" && taskId ? <EffectiveLimitsView query={{ task_id: taskId }} /> : null}
    </Page>
  );
}

/** Storage scope comes only from explicit stage parameters, never from a source identifier. */
function TaskResultsLinks({ task }: { task: TaskConfig }) {
  const api = useApi();
  const candidates = task.stages.filter(
    (stage) =>
      stage.handler &&
      stage.connections?.target &&
      stage.inputs?.some(
        (input) =>
          (input.select ?? "output") === "output" &&
          task.stages.some((upstream) => upstream.stage_id === input.from && upstream.kind === "handler"),
      ),
  );
  const destinations = useQuery({
    queryKey: ["task-result-destinations", candidates],
    enabled: candidates.length > 0,
    queryFn: async () => {
      const details = await Promise.all(
        candidates.map(async (stage) => {
          const reference = stage.handler!;
          const detail = await unwrap(
            api.registry.GET("/v1/packages/{package_id}/versions/{version}", {
              params: { path: { package_id: reference.package_id, version: reference.version } },
            }),
          );
          if (detail.manifest?.kind !== "storage") return null;
          const scope = stage.params?.["scope"];
          return {
            stageId: stage.stage_id,
            label: stage.title || stage.stage_id,
            href: resultsHref({
              connectionId: stage.connections!.target!,
              ...(typeof scope === "string" && scope ? { scope } : {}),
            }),
          };
        }),
      );
      return details.filter((detail) => detail !== null);
    },
  });
  if (destinations.isLoading) return <p className="muted">Визначення сховищ результатів…</p>;
  if (destinations.error)
    return <ErrorBox error={destinations.error} title="Не вдалося визначити сховища результатів" />;
  if (!destinations.data?.length)
    return (
      <p className="muted">
        Етап збереження результатів обробки ще не визначено. Доступний каталог результатів.
      </p>
    );
  return (
    <div aria-label="Сховища результатів завдання">
      <div className="button-row">
        {destinations.data.map((destination) => (
          <Link key={destination.stageId} className="btn" to={destination.href}>
            Розібрані дані: {destination.label}
          </Link>
        ))}
      </div>
      <p className="muted">Перегляд за підключенням етапу. Сховище може містити результати інших завдань.</p>
    </div>
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
      ].map(([level, issue], i) => (
        <p key={i} className={level === "error" ? "error-inline" : "warn-inline"}>
          {level === "error" ? "Помилка" : "Попередження"}: Перевірте конфігурацію завдання.
          {issue.pointer ? ` Поле: ${issue.pointer}.` : null}
        </p>
      ))}
      {validation.errors.length || validation.warnings?.length ? (
        <details>
          <summary>Подробиці перевірки</summary>
          <JsonView value={{ errors: validation.errors, warnings: validation.warnings ?? [] }} compact />
        </details>
      ) : null}
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
