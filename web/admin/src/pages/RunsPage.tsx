import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { useApi } from "../app/context";
import { unwrap } from "../api/client";
import { TERMINAL_JOB_STATUSES, pollDelay, useCursorList } from "../api/hooks";
import { useConfig } from "../app/context";
import type { JobStatus, Run, StageItem } from "../api/types";
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
import { formatDate, formatMoney, refLabel } from "../lib/format";

const JOB_STATUSES: JobStatus[] = ["queued", "running", "cancelling", "succeeded", "failed", "cancelled"];
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

export function RunsPage() {
  const api = useApi();
  const [params, setParams] = useSearchParams();
  const taskId = params.get("task_id") ?? "";
  const status = (params.get("status") ?? "") as JobStatus | "";
  const list = useCursorList(["runs", taskId, status], (cursor, limit) =>
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
  );
  const update = (key: string, value: string) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next);
  };
  return (
    <Page title="Запуски">
      <div className="filters">
        <Field label="Завдання">
          <input value={taskId} onChange={(e) => update("task_id", e.target.value)} />
        </Field>
        <Field label="Стан">
          <select value={status} onChange={(e) => update("status", e.target.value)}>
            <option value="">усі</option>
            {JOB_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </Field>
      </div>
      {list.isLoading ? <Loading /> : null}
      <ErrorBox error={list.error} />
      <Table
        label="Запуски"
        rows={list.items}
        rowKey={(r) => r.run_id}
        columns={[
          {
            header: "Запуск",
            cell: (r) => <Link to={`/runs/${encodeURIComponent(r.run_id)}`}>{r.run_id}</Link>,
          },
          { header: "Завдання", cell: (r) => r.task_id },
          { header: "Стан", cell: (r) => <Status value={r.status} /> },
          { header: "Тригер", cell: (r) => r.trigger },
          { header: "Тест", cell: (r) => (r.test_mode ? "так" : "") },
          { header: "Створено", cell: (r) => formatDate(r.created_at) },
          { header: "Завершено", cell: (r) => formatDate(r.finished_at) },
        ]}
      />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
    </Page>
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
        data && !TERMINAL_JOB_STATUSES.has(data.status) ? (
          <ReasonAction
            label="Скасувати запуск"
            confirmLabel="Скасувати"
            danger
            busy={cancel.isPending}
            requireReason={false}
            onConfirm={(r) => cancel.mutate(r)}
          />
        ) : null
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
              ["Стан", <Status value={data.status} />],
              ["Тригер", data.trigger],
              ["Тестовий режим", data.test_mode ? "так (без запису в робочі дані)" : "ні"],
              ["Створено", formatDate(data.created_at)],
              ["Почато", formatDate(data.started_at)],
              ["Завершено", formatDate(data.finished_at)],
              ["Витрати LLM", <span data-testid="run-cost">{formatMoney(data.costs?.llm)}</span>],
              ["Backpressure", data.backpressure ? "так, збір пригальмовано" : "ні"],
              ["Версія конфігурації", data.task_etag ?? "—"],
            ]}
          />
          {data.error ? (
            <ErrorBox error={new Error(`${data.error.title} (${data.error.code})`)} title="Помилка запуску" />
          ) : null}
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
          ...keys.map((k) => ({ header: k, cell: (s: (typeof stages)[number]) => s.counts?.[k] ?? 0 })),
        ]}
      />
      {run.counters && Object.keys(run.counters).length ? (
        <KeyValue rows={Object.entries(run.counters).map(([k, v]) => [k, String(v)] as [string, string])} />
      ) : null}
    </>
  );
}

function RunItems({ runId }: { runId: string }) {
  const api = useApi();
  const [stageId, setStageId] = useState("");
  const [status, setStatus] = useState<StageItem["status"] | "">("failed");
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
                {s}
              </option>
            ))}
          </select>
        </Field>
      </div>
      <ErrorBox error={list.error} />
      <Table
        label="Елементи запуску"
        rows={list.items}
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
          { header: "Пакет", cell: (i) => refLabel(i.handler) },
          { header: "Помилка", cell: (i) => (i.error ? `${i.error.code}: ${i.error.title}` : "—") },
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
  const collectorExecutor = executors.data?.items.find((e) => e.role === "collector")?.executor;
  const collectionId = run.collection_id;
  const errors = useQuery({
    queryKey: ["collection-errors", collectorExecutor, collectionId],
    enabled: Boolean(collectionId && executors.isFetched),
    queryFn: () => {
      const client = collectorExecutor ? api.collectorExecutor(collectorExecutor) : api.collector;
      return unwrap(
        client.GET("/v1/collections/{collection_id}/errors", {
          params: { path: { collection_id: collectionId as string } },
        }),
      );
    },
  });
  if (!collectionId) return <p className="muted">Запуск без збору (наприклад повторна обробка).</p>;
  return (
    <Section title={`Помилки й пропуски збору ${collectionId}`}>
      <ErrorBox error={errors.error} />
      <Table
        label="Помилки колектора"
        rows={errors.data?.items ?? []}
        rowKey={(e, i) => `${e.url ?? ""}-${i}`}
        columns={[
          { header: "URL / повідомлення", cell: (e) => e.url ?? "—" },
          { header: "Код", cell: (e) => <code>{e.code}</code> },
          { header: "HTTP", cell: (e) => e.http_status ?? "—" },
          { header: "Спроби", cell: (e) => e.attempts ?? "—" },
          { header: "Повідомлення", cell: (e) => e.message ?? "—" },
          { header: "Коли", cell: (e) => formatDate(e.at) },
        ]}
      />
    </Section>
  );
}
