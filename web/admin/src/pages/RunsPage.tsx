import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { useApi } from "../app/context";
import { unwrap } from "../api/client";
import { errorMessage, safeProblemCode } from "../api/problem";
import { looksLikeSecretValue } from "../lib/secrets";
import { TERMINAL_JOB_STATUSES, pollDelay, useCursorList } from "../api/hooks";
import { useConfig } from "../app/context";
import type { JobStatus, Run, StageItem } from "../api/types";
import { AttemptHistory } from "../components/AttemptHistory";
import { ReprocessForm } from "../components/ReprocessForm";
import {
  ErrorBox,
  Field,
  KeyValue,
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
import { formatDate, formatInstant, formatMoney, refLabel } from "../lib/format";
import { formatDuration, statusLabel } from "../lib/format";
import { resultsHref, entityTypeLabel } from "../lib/results-context";
import { useTaskOptions } from "../lib/pickers";

const JOB_STATUSES: JobStatus[] = ["queued", "running", "cancelling", "succeeded", "failed", "cancelled"];
const TRIGGER_LABELS: Record<string, string> = {
  manual: "Вручну",
  schedule: "За розкладом",
  reprocess: "Повторна обробка",
  assistant: "Асистент",
  api: "Зовнішній запит",
};
const ITEM_STATUSES: NonNullable<StageItem["status"]>[] = [
  "queued",
  "leased",
  "running",
  "completed",
  "retrying",
  "failed",
  "skipped",
  "cancelled",
];

type RunActionFeedback = { runId: string; error?: unknown };

export function RunsPage() {
  const api = useApi();
  const tasks = useTaskOptions();
  const [feedback, setFeedback] = useState<RunActionFeedback | null>(null);
  const [params, setParams] = useSearchParams();
  const taskId = params.get("task_id") ?? "";
  const status = (params.get("status") ?? "") as JobStatus | "";
  const list = useCursorList(
    ["runs", taskId, status],
    (cursor, limit) =>
      unwrap(
        api.orchestrator.GET("/v1/runs", {
          params: {
            query: {
              limit,
              ...(cursor ? { cursor } : {}),
              ...(taskId ? { task_id: taskId } : {}),
              ...(status ? { status } : {}),
            },
          },
        }),
      ),
    (items) => items.some((run) => !TERMINAL_JOB_STATUSES.has(run.status)),
  );
  const update = (key: string, value: string) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next);
  };
  return (
    <Page
      title="Запуски"
      actions={
        <button className="btn" type="button" onClick={list.refetch}>
          Оновити список
        </button>
      }
    >
      <div className="filters">
        <Field label="Завдання">
          <input
            list="run-task-options"
            value={taskId}
            onChange={(e) => update("task_id", e.target.value)}
            placeholder="Назва або ідентифікатор завдання"
          />
          <datalist id="run-task-options">
            {tasks.options.map((task) => (
              <option key={task.value} value={task.value}>
                {task.label}
              </option>
            ))}
          </datalist>
          {tasks.hasMore ? (
            <button
              type="button"
              className="btn btn-small"
              onClick={tasks.loadMore}
              disabled={tasks.loadingMore}
            >
              Більше завдань
            </button>
          ) : null}
        </Field>
        <Field label="Стан">
          <select value={status} onChange={(e) => update("status", e.target.value)}>
            <option value="">усі</option>
            {JOB_STATUSES.map((s) => (
              <option key={s} value={s}>
                {statusLabel(s)}
              </option>
            ))}
          </select>
        </Field>
      </div>
      {list.isLoading ? <Loading /> : null}
      <ErrorBox error={list.error} />
      <ErrorBox error={tasks.error} title="Список завдань недоступний" />
      {feedback ? (
        <div>
          <div className="button-row">
            <span className="muted">Запуск {feedback.runId}</span>
            <button className="btn btn-small" type="button" onClick={() => setFeedback(null)}>
              Закрити повідомлення
            </button>
          </div>
          {feedback.error ? (
            <ErrorBox error={feedback.error} title="Не вдалося зупинити" />
          ) : (
            <Notice>Скасування прийнято. Уже збережені дані залишаються у сховищах.</Notice>
          )}
        </div>
      ) : null}
      <Table
        label="Запуски"
        rows={list.items}
        loading={list.isLoading}
        error={list.error}
        rowKey={(r) => r.run_id}
        columns={[
          {
            header: "Запуск",
            cell: (r) => (
              <Link title={r.run_id} to={`/runs/${encodeURIComponent(r.run_id)}`}>
                {r.run_id}
              </Link>
            ),
          },
          {
            header: "Завдання",
            cell: (r) => (
              <Link title={r.task_id} to={`/tasks/${encodeURIComponent(r.task_id)}`}>
                {r.task_id}
              </Link>
            ),
          },
          { header: "Стан", cell: (r) => <Status value={r.status} /> },
          { header: "Спосіб запуску", cell: (r) => TRIGGER_LABELS[r.trigger] ?? r.trigger },
          { header: "Тест", cell: (r) => (r.test_mode ? "так" : "") },
          { header: "Створено", cell: (r) => formatDate(r.created_at) },
          { header: "Завершено", cell: (r) => formatDate(r.finished_at) },
          { header: "Тривалість", cell: (r) => formatDuration(r.started_at, r.finished_at) },
          { header: "Дії", cell: (run) => <RunListActions run={run} onFeedback={setFeedback} /> },
        ]}
      />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
    </Page>
  );
}

function RunListActions({
  run,
  onFeedback,
}: {
  run: Run;
  onFeedback: (feedback: RunActionFeedback) => void;
}) {
  const api = useApi();
  const queryClient = useQueryClient();
  const cancel = useMutation({
    mutationFn: (reason: string) =>
      unwrap(
        api.orchestrator.POST("/v1/runs/{run_id}/cancel", {
          params: { path: { run_id: run.run_id } },
          body: reason ? { reason } : {},
        }),
      ),
    onSuccess: () => {
      onFeedback({ runId: run.run_id });
      void queryClient.invalidateQueries({ queryKey: ["runs"] });
      void queryClient.invalidateQueries({ queryKey: ["run", run.run_id] });
    },
    onError: (error) => onFeedback({ runId: run.run_id, error }),
  });
  return (
    <div>
      <div className="button-row row-actions">
        <Link className="btn btn-small" to={`/runs/${encodeURIComponent(run.run_id)}`}>
          Деталі
        </Link>
        {!TERMINAL_JOB_STATUSES.has(run.status) && run.status !== "cancelling" ? (
          <ReasonAction
            label="Зупинити"
            confirmLabel="Підтвердити зупинку"
            danger
            busy={cancel.isPending || cancel.isSuccess}
            requireReason={false}
            modal
            onConfirm={(reason) => cancel.mutate(reason)}
          />
        ) : null}
      </div>
    </div>
  );
}

type RunTab = "progress" | "items" | "collector" | "reprocess";

export function RunPage() {
  const { runId = "" } = useParams();
  const api = useApi();
  const { polling } = useConfig();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<RunTab>("progress");
  const run = useQuery({
    queryKey: ["run", runId],
    queryFn: () => unwrap(api.orchestrator.GET("/v1/runs/{run_id}", { params: { path: { run_id: runId } } })),
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data || TERMINAL_JOB_STATUSES.has(data.status) || query.state.error) return false;
      return pollDelay(query.state.dataUpdateCount, polling);
    },
  });
  const cancel = useMutation({
    mutationFn: (reason: string) =>
      unwrap(
        api.orchestrator.POST("/v1/runs/{run_id}/cancel", {
          params: { path: { run_id: runId } },
          body: reason ? { reason } : {},
        }),
      ),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["run", runId] }),
  });

  const data = run.data;
  return (
    <Page
      title={`Запуск ${runId}`}
      actions={
        <>
          <Link className="btn" to="/results">
            Усі розібрані дані
          </Link>
          {data?.source_id ? (
            <Link className="btn" to={`/materials?source_id=${encodeURIComponent(data.source_id)}`}>
              Матеріали джерела
            </Link>
          ) : null}
          {data && !TERMINAL_JOB_STATUSES.has(data.status) ? (
            <ReasonAction
              label="Скасувати запуск"
              confirmLabel="Скасувати"
              danger
              busy={cancel.isPending}
              requireReason={false}
              onConfirm={(r) => cancel.mutate(r)}
            />
          ) : null}
        </>
      }
    >
      {run.isLoading ? <Loading /> : null}
      <ErrorBox error={run.error} />
      <ErrorBox error={cancel.error} title="Не вдалося скасувати" />
      {cancel.data ? (
        <Notice tone="ok">
          Скасування: <Status value={cancel.data.status} /> — колектор і етапи зупиняються, уже записане не
          відкочується.
        </Notice>
      ) : null}
      {data ? (
        <>
          <KeyValue
            rows={[
              ["Завдання", <Link to={`/tasks/${encodeURIComponent(data.task_id)}`}>{data.task_id}</Link>],
              [
                "Джерело",
                data.source_id ? (
                  <Link to={`/sources/${encodeURIComponent(data.source_id)}`}>{data.source_id}</Link>
                ) : (
                  "Недоступно"
                ),
              ],
              ["Стан", <Status value={data.status} />],
              ["Спосіб запуску", TRIGGER_LABELS[data.trigger] ?? data.trigger],
              ["Тестовий режим", data.test_mode ? "так (без запису в робочі дані)" : "ні"],
              ["Створено", formatDate(data.created_at)],
              ["Почато", formatDate(data.started_at)],
              ["Завершено", formatDate(data.finished_at)],
              ["Тривалість", formatDuration(data.started_at, data.finished_at)],
              ["Останній прогрес", formatDate(data.updated_at)],
              ["Витрати LLM", <span data-testid="run-cost">{formatMoney(data.costs?.llm)}</span>],
              ["Збір пригальмовано через чергу", data.backpressure ? "так" : "ні"],
              ["Версія конфігурації", data.task_etag ?? "—"],
            ]}
          />
          {data.error ? <ErrorBox error={data.error} title="Помилка запуску" /> : null}
          <RunOutcome run={data} />
          <Tabs<RunTab>
            tabs={[
              ["progress", "Прогрес етапів"],
              ["items", "Елементи й помилки"],
              ["collector", "Помилки колектора"],
              ["reprocess", "Повторна обробка"],
            ]}
            active={tab}
            onChange={setTab}
          />
          {tab === "progress" ? <StageProgressTable run={data} /> : null}
          {tab === "items" ? <RunItems runId={runId} /> : null}
          {tab === "collector" ? <CollectorErrors run={data} /> : null}
          {tab === "reprocess" ? <ReprocessForm taskId={data.task_id} /> : null}
        </>
      ) : null}
    </Page>
  );
}

function StageProgressTable({ run }: { run: Run }) {
  const stages = run.stages ?? [];
  const keys = [...new Set(stages.flatMap((s) => Object.keys(s.counts ?? {})))];
  return (
    <>
      <Table
        label="Прогрес етапів"
        rows={stages}
        rowKey={(s) => s.stage_id}
        columns={[
          { header: "Етап", cell: (s) => s.stage_id },
          { header: "Пакет", cell: (s) => refLabel(s.handler) },
          ...keys.map((k) => ({
            header:
              (
                {
                  completed: "Завершено",
                  success: "Успішно",
                  running: "Виконується",
                  failed: "З помилкою",
                  queued: "У черзі",
                  unrecognized: "Не розпізнано",
                  empty: "Без результатів",
                  cancelled: "Скасовано",
                  retrying: "Повтор",
                  skipped: "Пропущено",
                  leased: "Взято в роботу",
                } as Record<string, string>
              )[k] ?? k,
            cell: (s: (typeof stages)[number]) => s.counts?.[k] ?? 0,
          })),
        ]}
      />
      {run.counters && Object.keys(run.counters).length ? (
        <KeyValue
          rows={Object.entries(run.counters).map(
            ([k, v]) =>
              [
                (
                  { materials: "Отримані матеріали", unknown_materials: "Невідомі матеріали" } as Record<
                    string,
                    string
                  >
                )[k] ?? k,
                String(v),
              ] as [string, string],
          )}
        />
      ) : null}
    </>
  );
}

export function RunOutcome({ run }: { run: Run }) {
  const summary = run.summary;
  const label = (count: number | undefined) =>
    count === undefined ? "Недоступно" : `${summary?.complete === false ? "Щонайменше " : ""}${count}`;
  return (
    <Section title="Результат ланцюжка">
      <KeyValue
        rows={[
          [
            run.trigger === "reprocess" ? "RAW отримано зі сховища" : "Зібрано матеріалів",
            String(run.counters?.materials ?? "Недоступно"),
          ],
          ["Розібрано унікальних сутностей", label(summary?.extracted_entities)],
          ["Підтверджено збережених записів", label(summary?.saved_records)],
        ]}
      />
      <p className="muted">
        Кількості отримано з відповідей обробників цього запуску. Кількості елементів етапу означають
        оброблені порції матеріалів, а не кількість сутностей.
      </p>
      {summary?.complete === false ? (
        <Notice>
          {summary.legacy_trace
            ? "Точні кількості недоступні: історичне трасування було обрізане й не зберігало повний облік сутностей."
            : "Підсумок неповний: частину сутностей передано за посиланням. Зафіксовані кількості є нижньою межею."}
        </Notice>
      ) : null}
      {(summary?.result_groups?.length ?? 0) > 0 ? (
        <>
          <div className="button-row">
            {summary?.result_groups?.map((group) => (
              <Link
                className="btn"
                key={`${group.connection_id}/${group.entity_type}/${group.scope}`}
                to={resultsHref({
                  ...(group.connection_id ? { connectionId: group.connection_id } : {}),
                  ...(group.entity_type ? { entityType: group.entity_type } : {}),
                  ...(group.scope ? { scope: group.scope } : {}),
                })}
              >
                {entityTypeLabel(group.entity_type ?? "")} · {group.scope} · {group.connection_id}
              </Link>
            ))}
          </div>
          <p className="muted">
            Посилання відкривають актуальні записи відповідного типу, області ключів і сховища. Там можуть
            бути результати інших запусків.
          </p>
        </>
      ) : null}
    </Section>
  );
}

function RunItems({ runId }: { runId: string }) {
  const api = useApi();
  const [stageId, setStageId] = useState("");
  const [status, setStatus] = useState<StageItem["status"] | "">("");
  const list = useCursorList(["run-items", runId, stageId, status], (cursor, limit) =>
    unwrap(
      api.orchestrator.GET("/v1/runs/{run_id}/items", {
        params: {
          path: { run_id: runId },
          query: {
            limit,
            ...(cursor ? { cursor } : {}),
            ...(stageId ? { stage_id: stageId } : {}),
            ...(status ? { status } : {}),
          },
        },
      }),
    ),
  );
  return (
    <Section title="Елементи запуску">
      <div className="filters">
        <Field label="Етап">
          <input value={stageId} onChange={(e) => setStageId(e.target.value)} />
        </Field>
        <Field label="Стан елемента">
          <select value={status} onChange={(e) => setStatus(e.target.value as StageItem["status"] | "")}>
            <option value="">усі</option>
            {ITEM_STATUSES.map((s) => (
              <option key={s} value={s}>
                {statusLabel(s)}
              </option>
            ))}
          </select>
        </Field>
      </div>
      <ErrorBox error={list.error} />
      <Table
        label="Елементи запуску"
        rows={list.items}
        loading={list.isLoading}
        error={list.error}
        empty={status === "failed" ? "Помилок у цій вибірці немає" : "Елементів у цій вибірці немає"}
        rowKey={(i) => i.item_id}
        columns={[
          { header: "Етап", cell: (i) => i.stage_id },
          {
            header: "Матеріал",
            cell: (i) =>
              i.material_id ? (
                <Link to={`/materials/${encodeURIComponent(i.material_id)}/trace`}>{i.material_id}</Link>
              ) : (
                "—"
              ),
          },
          { header: "Стан", cell: (i) => <Status value={i.status} /> },
          { header: "Результат", cell: (i) => <Status value={i.result_status ?? null} /> },
          { header: "Спроби", cell: (i) => i.attempts },
          { header: "Доступний з", cell: (i) => formatInstant(i.available_at) },
          {
            header: "Історія спроб",
            cell: (i) => <AttemptHistory history={i.attempt_history} label={`Історія спроб ${i.item_id}`} />,
          },
          { header: "Пакет", cell: (i) => refLabel(i.handler) },
          {
            header: "Помилка",
            cell: (i) =>
              i.error ? (
                <>
                  <ErrorBox error={i.error} title="Помилка елемента" />
                </>
              ) : (
                "—"
              ),
          },
        ]}
      />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
    </Section>
  );
}

function CollectorErrors({ run }: { run: Run }) {
  const api = useApi();
  const executors = useQuery({
    queryKey: ["executors"],
    queryFn: () => unwrap(api.orchestrator.GET("/v1/executors")),
  });
  const collectors = executors.data?.items.filter((executor) => executor.role === "collector") ?? [];
  const collectorExecutor =
    collectors.find((executor) => executor.capabilities?.["collector"] === run.collector_kind)?.executor ??
    (!run.collector_kind && collectors.length === 1 ? collectors[0]?.executor : undefined);
  const collectionId = run.collection_id;
  const errors = useQuery({
    queryKey: ["collection-errors", collectorExecutor, collectionId],
    enabled: Boolean(
      collectionId &&
      executors.isSuccess &&
      (collectorExecutor || (!run.collector_kind && collectors.length === 0)),
    ),
    queryFn: () => {
      const client = collectorExecutor ? api.collectorExecutor(collectorExecutor) : api.collector;
      return unwrap(
        client.GET("/v1/collections/{collection_id}/errors", {
          params: { path: { collection_id: collectionId as string } },
        }),
      );
    },
  });
  if (!collectionId)
    return (
      <Notice>
        {run.trigger === "reprocess"
          ? "Повторна обробка читає RAW зі сховища й не запускає колектор."
          : run.status === "failed"
            ? "Збір не вдалося почати: колектор не створив операцію збору. Причину показано у помилці запуску вище; перевірте джерело, правила й доступність виконавця."
            : "Операцію збору ще не створено. Очікуємо запуск колектора."}
      </Notice>
    );
  if (executors.error)
    return <ErrorBox error={executors.error} title="Не вдалося визначити виконавця збору" />;
  if (executors.isFetched && !collectorExecutor && (run.collector_kind || collectors.length > 1))
    return (
      <Notice>
        Не вдалося визначити колектор цього запуску. Перевірте тип колектора у джерелі та налаштованих
        виконавців.
      </Notice>
    );
  return (
    <Section title={`Помилки й пропуски збору ${collectionId}`}>
      <ErrorBox error={errors.error} />
      <Table
        label="Помилки колектора"
        rows={errors.data?.items ?? []}
        loading={errors.isLoading}
        error={errors.error}
        empty="Помилок і пропусків збору немає"
        rowKey={(e, i) => `${e.url ?? ""}-${i}`}
        columns={[
          {
            header: "URL / повідомлення",
            cell: (error) =>
              collectorAddress(error.url) ??
              (error.telegram_message ? "Повідомлення Telegram" : "Адреса недоступна"),
          },
          { header: "Код", cell: (e) => <code>{safeProblemCode(e.code)}</code> },
          { header: "HTTP", cell: (e) => e.http_status ?? "—" },
          { header: "Спроби", cell: (e) => e.attempts ?? "—" },
          {
            header: "Що перевірити",
            cell: (error) =>
              errorMessage({ title: "Помилка збору", code: error.code, status: error.http_status ?? 502 }),
          },
          { header: "Коли", cell: (e) => formatDate(e.at) },
        ]}
      />
    </Section>
  );
}

export function collectorAddress(value: string | undefined): string | null {
  if (!value) return null;
  try {
    const address = new URL(value);
    // Credentials and query tokens are excluded from the displayed address.
    if (!["http:", "https:"].includes(address.protocol) || looksLikeSecretValue(address.pathname))
      return null;
    return address.origin + address.pathname;
  } catch {
    return null;
  }
}
