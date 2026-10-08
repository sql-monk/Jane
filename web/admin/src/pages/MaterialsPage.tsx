import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { useApi, useConfig } from "../app/context";
import { unwrap } from "../api/client";
import { useCursorList } from "../api/hooks";
import { ApiError, toProblem } from "../api/problem";
import type { StoredObject } from "../api/types";
import { ConnectionPicker } from "../components/ConnectionPicker";
import { ReprocessForm } from "../components/ReprocessForm";
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
} from "../components/ui";
import { formatBytes, formatDate, refLabel } from "../lib/format";

export function MaterialsPage() {
  const api = useApi();
  const [params, setParams] = useSearchParams();
  const connectionId = params.get("connection_id") ?? "";
  const sourceId = params.get("source_id") ?? "";
  const [selected, setSelected] = useState<StoredObject | null>(null);
  const [reprocess, setReprocess] = useState<StoredObject | null>(null);
  const list = useCursorList(["objects", connectionId, sourceId], (cursor, limit) =>
    connectionId
      ? unwrap(
          api.storage.GET("/v1/objects", {
            params: {
              query: {
                connection_id: connectionId,
                limit,
                ...(cursor ? { cursor } : {}),
                ...(sourceId ? { source_id: sourceId } : {}),
              },
            },
          }),
        )
      : Promise.resolve({ items: [], next_cursor: null }),
  );
  const update = (key: string, value: string) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next);
  };
  return (
    <Page title="Матеріали">
      <p className="muted">
        Збережені RAW-матеріали й документи результатів (storage API). Вміст показується як текст — це дані,
        не розмітка.
      </p>
      <div className="filters">
        <ConnectionPicker
          label="Сховище (connection_id)"
          value={connectionId}
          onChange={(v) => update("connection_id", v)}
        />
        <Field label="Джерело">
          <input value={sourceId} onChange={(e) => update("source_id", e.target.value)} />
        </Field>
      </div>
      {!connectionId ? (
        <Notice>Оберіть підключення сховища, щоб переглянути збережені матеріали.</Notice>
      ) : null}
      {list.isLoading ? <Loading /> : null}
      <ErrorBox error={list.error} />
      <Table
        label="Збережені матеріали"
        rows={list.items}
        rowKey={(o) => o.object.object_id}
        empty={connectionId ? "Немає збережених об'єктів" : "—"}
        columns={[
          { header: "Об'єкт", cell: (o) => <code>{o.object.object_id}</code> },
          { header: "Медіатип", cell: (o) => o.object.media_type ?? "—" },
          { header: "Розмір", cell: (o) => formatBytes(o.object.size_bytes) },
          { header: "URL", cell: (o) => o.material?.url ?? "—" },
          { header: "Джерело", cell: (o) => o.material?.source_id ?? "—" },
          { header: "Отримано", cell: (o) => formatDate(o.material?.fetched_at) },
          { header: "Збережено", cell: (o) => formatDate(o.stored_at) },
          {
            header: "Дії",
            cell: (o) => (
              <span className="button-row">
                <button type="button" className="btn btn-small" onClick={() => setSelected(o)}>
                  Переглянути
                </button>
                {o.material?.material_id ? (
                  <Link
                    className="btn btn-small"
                    to={`/materials/${encodeURIComponent(o.material.material_id)}/trace`}
                  >
                    Простежити
                  </Link>
                ) : null}
                <button type="button" className="btn btn-small" onClick={() => setReprocess(o)}>
                  Повторно обробити
                </button>
              </span>
            ),
          },
        ]}
      />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
      {selected ? <ObjectDetail connectionId={connectionId} objectId={selected.object.object_id} /> : null}
      {reprocess ? (
        <Section title={`Повторна обробка ${reprocess.object.object_id}`}>
          <ReprocessForm
            storageConnectionId={connectionId}
            materialIds={reprocess.material?.material_id ? [reprocess.material.material_id] : []}
          />
        </Section>
      ) : null}
    </Page>
  );
}

function ObjectDetail({ connectionId, objectId }: { connectionId: string; objectId: string }) {
  const api = useApi();
  const { preview_max_bytes } = useConfig();
  const detail = useQuery({
    queryKey: ["object", connectionId, objectId],
    queryFn: () =>
      unwrap(
        api.storage.GET("/v1/objects/{object_id}", {
          params: { path: { object_id: objectId }, query: { connection_id: connectionId } },
        }),
      ),
  });
  const content = useQuery({
    queryKey: ["object-content", connectionId, objectId, preview_max_bytes],
    queryFn: async () => {
      const { data, error, response } = await api.storage.GET("/v1/objects/{object_id}/content", {
        params: { path: { object_id: objectId }, query: { connection_id: connectionId } },
        headers: { Range: `bytes=0-${preview_max_bytes - 1}` },
        parseAs: "text",
      });
      if (error !== undefined || !response.ok)
        throw new ApiError(response.status, toProblem(response.status, error, response.statusText));
      const text = String(data ?? "");
      return {
        text: text.slice(0, preview_max_bytes),
        partial: response.status === 206 || text.length > preview_max_bytes,
      };
    },
  });
  return (
    <Section title={`Об'єкт ${objectId}`}>
      <ErrorBox error={detail.error} />
      {detail.data ? (
        <KeyValue
          rows={[
            ["Адаптер", detail.data.object.adapter ?? "—"],
            ["Підключення", detail.data.object.connection_id ?? "—"],
            ["Матеріал", detail.data.material?.material_id ?? "—"],
            ["Спостереження", detail.data.material?.observation_id ?? "—"],
            ["URL", detail.data.material?.locator?.url ?? "—"],
            ["Отримано", formatDate(detail.data.material?.fetched_at)],
            [
              "Колектор",
              detail.data.material?.collector
                ? `${detail.data.material.collector.name}@${detail.data.material.collector.version}`
                : "—",
            ],
          ]}
        />
      ) : null}
      <h3>Вміст{content.data?.partial ? ` (перші ${formatBytes(preview_max_bytes)})` : ""}</h3>
      <ErrorBox error={content.error} />
      {content.data ? (
        <pre className="content-preview" data-testid="content-preview">
          {content.data.text}
        </pre>
      ) : null}
    </Section>
  );
}

export function MaterialTracePage() {
  const { materialId = "" } = useParams();
  const api = useApi();
  const trace = useQuery({
    queryKey: ["trace", materialId],
    queryFn: () =>
      unwrap(
        api.orchestrator.GET("/v1/materials/{material_id}/trace", {
          params: { path: { material_id: materialId } },
        }),
      ),
  });
  return (
    <Page title={`Простежуваність ${materialId}`}>
      {trace.isLoading ? <Loading /> : null}
      <ErrorBox error={trace.error} />
      {trace.data ? (
        <>
          <KeyValue
            rows={[
              ["Джерело", trace.data.source_id ?? "—"],
              ["URL", trace.data.url ?? "—"],
            ]}
          />
          {/* Reprocessing of stored RAW runs the same observation again: one entry per (observation, run). */}
          {trace.data.observations.map((obs) => (
            <Section
              key={`${obs.observation_id}/${obs.run_id ?? ""}`}
              title={`Спостереження ${obs.observation_id}${obs.run_id ? `, запуск ${obs.run_id}` : ""}`}
            >
              <p className="muted">
                Запуск{" "}
                {obs.run_id ? <Link to={`/runs/${encodeURIComponent(obs.run_id)}`}>{obs.run_id}</Link> : "—"},
                завдання {obs.task_id ?? "—"}, отримано {formatDate(obs.fetched_at)}, sha256{" "}
                <code>{obs.content_sha256 ?? "—"}</code>
              </p>
              <Table
                label={`Етапи ${obs.observation_id}${obs.run_id ? ` (${obs.run_id})` : ""}`}
                rows={obs.stages}
                rowKey={(s) => s.stage_id}
                columns={[
                  { header: "Етап", cell: (s) => s.stage_id },
                  { header: "Версія пакета", cell: (s) => refLabel(s.handler) },
                  { header: "Результат", cell: (s) => <Status value={s.result_status ?? null} /> },
                  { header: "Виклик", cell: (s) => <code>{s.invocation_id ?? "—"}</code> },
                  {
                    header: "Виходи",
                    cell: (s) => (s.outputs?.length ? <JsonView value={s.outputs} compact /> : "—"),
                  },
                ]}
              />
            </Section>
          ))}
        </>
      ) : null}
    </Page>
  );
}
