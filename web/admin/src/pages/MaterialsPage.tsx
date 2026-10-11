import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { useApi, useConfig } from "../app/context";
import { unwrap } from "../api/client";
import { useCursorList } from "../api/hooks";
import { ApiError, toProblem } from "../api/problem";
import type { StoredObject, MaterialTrace } from "../api/types";
import { AttemptHistory } from "../components/AttemptHistory";
import { useStorageConnections, storageName } from "../components/StorageConnections";
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
import { formatBytes, formatDate, formatInstant, refLabel } from "../lib/format";
import { resultsHref, entityTypeLabel } from "../lib/results-context";
import { useSourceOptions } from "../lib/pickers";
import "../materials-storage.css";

export function formatMaterialContent(text: string): string {
  // Preserve source number lexemes, duplicate keys and whitespace without parsing JSON.
  return text;
}

function dateInputValue(value: string) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

export function MaterialsPage() {
  const [params, setParams] = useSearchParams();
  const connections = useStorageConnections();
  const sources = useSourceOptions();
  const connectionId = params.get("connection_id") ?? "";
  const sourceId = params.get("source_id") ?? "";
  const since = params.get("since") ?? "";
  const until = params.get("until") ?? "";
  const mediaType = params.get("media_type") ?? "";
  const objectId = params.get("object_id") ?? "";
  const sinceTime = since ? Date.parse(since) : undefined;
  const untilTime = until ? Date.parse(until) : undefined;
  const dateError =
    (sinceTime !== undefined && Number.isNaN(sinceTime)) ||
    (untilTime !== undefined && Number.isNaN(untilTime))
      ? "Некоректна дата. Виберіть дату й час у фільтрі."
      : sinceTime !== undefined && untilTime !== undefined && sinceTime >= untilTime
        ? "Початок періоду має бути раніше його кінця."
        : null;
  const [reprocess, setReprocess] = useState<{ connectionId: string; object: StoredObject } | null>(null);
  const update = (key: string, value: string) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    next.delete("object_id");
    setReprocess(null);
    setParams(next);
  };
  const selectObject = (id: string, storage: string) => {
    const next = new URLSearchParams(params);
    next.set("connection_id", storage);
    next.set("object_id", id);
    setParams(next);
  };
  const ids = connectionId ? [connectionId] : connections.items.map((c) => c.connection_id);
  return (
    <Page
      title="Матеріали"
      actions={
        <>
          <Link className="btn" to="/results">
            Усі розібрані дані
          </Link>
          <Link className="btn" to="/storages">
            Стан сховищ
          </Link>
        </>
      }
    >
      <p className="muted">
        Збережені матеріали та результати з усіх налаштованих сховищ. Кожне сховище має власні сторінки та
        повідомлення про помилки.
      </p>
      <div className="filters materials-filters">
        <Field label="Сховище">
          <select value={connectionId} onChange={(e) => update("connection_id", e.target.value)}>
            <option value="">Усі сховища</option>
            {connectionId && !connections.items.some((c) => c.connection_id === connectionId) ? (
              <option value={connectionId}>{connectionId}</option>
            ) : null}
            {connections.items.map((c) => (
              <option key={c.connection_id} value={c.connection_id}>
                {storageName(c)}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Джерело">
          <input
            list="material-sources"
            value={sourceId}
            onChange={(e) => update("source_id", e.target.value)}
            placeholder="Назва або ідентифікатор джерела"
          />
          <datalist id="material-sources">
            {sources.options.map((source) => (
              <option key={source.value} value={source.value}>
                {source.label}
              </option>
            ))}
          </datalist>
          {sources.hasMore ? (
            <button
              type="button"
              className="btn btn-small"
              onClick={sources.loadMore}
              disabled={sources.loadingMore}
            >
              Більше джерел
            </button>
          ) : null}
        </Field>
        <Field label="Збережено з">
          <input
            type="datetime-local"
            value={dateInputValue(since)}
            onChange={(e) => update("since", e.target.value)}
          />
        </Field>
        <Field label="Збережено до (не включно)">
          <input
            type="datetime-local"
            value={dateInputValue(until)}
            onChange={(e) => update("until", e.target.value)}
          />
        </Field>
        <Field label="Медіатип у завантажених матеріалах">
          <input
            value={mediaType}
            placeholder="text/html або application/json"
            onChange={(e) => update("media_type", e.target.value)}
          />
        </Field>
      </div>
      {connections.isLoading ? <Loading /> : null}
      <ErrorBox error={connections.error} />
      <ErrorBox error={sources.error} title="Список джерел недоступний" />
      <LoadMore
        hasMore={connections.hasMore}
        loading={connections.loadingMore}
        onClick={connections.loadMore}
      />
      {!connections.isLoading && !connections.error && !ids.length ? (
        <Notice>Немає налаштованих сховищ. Додайте підключення у розділі «Підключення».</Notice>
      ) : null}
      {dateError ? (
        <div role="alert" className="error-box">
          {dateError}
        </div>
      ) : null}
      {(dateError ? [] : ids).map((id) => (
        <StorageMaterials
          key={id}
          connectionId={id}
          title={storageName(
            connections.items.find((c) => c.connection_id === id) ?? { connection_id: id, kind: "" },
          )}
          sourceId={sourceId}
          since={since}
          until={until}
          mediaType={mediaType}
          onSelect={(o) => selectObject(o.object.object_id, id)}
          onReprocess={(o) => setReprocess({ connectionId: id, object: o })}
        />
      ))}
      {connectionId && objectId ? (
        <MaterialDetail key={`${connectionId}/${objectId}`} connectionId={connectionId} objectId={objectId} />
      ) : null}
      {reprocess ? (
        <Section title={`Повторна обробка ${reprocess.object.object.object_id}`}>
          <ReprocessForm
            key={`${reprocess.connectionId}/${reprocess.object.object.object_id}`}
            storageConnectionId={reprocess.connectionId}
            stored={{
              object_id: reprocess.object.object.object_id,
              material_id: reprocess.object.material?.material_id,
              observation_id: reprocess.object.material?.observation_id,
            }}
          />
        </Section>
      ) : null}
    </Page>
  );
}

function StorageMaterials({
  connectionId,
  title,
  sourceId,
  since,
  until,
  mediaType,
  onSelect,
  onReprocess,
}: {
  connectionId: string;
  title: string;
  sourceId: string;
  since: string;
  until: string;
  mediaType: string;
  onSelect: (object: StoredObject) => void;
  onReprocess: (object: StoredObject) => void;
}) {
  const api = useApi();
  const list = useCursorList(["objects", connectionId, sourceId, since, until], (cursor, limit) =>
    unwrap(
      api.storage.GET("/v1/objects", {
        params: {
          query: {
            connection_id: connectionId,
            limit,
            ...(cursor ? { cursor } : {}),
            ...(sourceId ? { source_id: sourceId } : {}),
            ...(since ? { since: new Date(since).toISOString() } : {}),
            ...(until ? { until: new Date(until).toISOString() } : {}),
          },
        },
      }),
    ),
  );
  const filtered = list.items.filter(
    (o) => !mediaType || (o.object.media_type ?? "").toLowerCase().includes(mediaType.toLowerCase()),
  );
  return (
    <Section title={title}>
      {list.isLoading ? <Loading /> : null}
      <ErrorBox error={list.error} />
      <button className="btn btn-small" type="button" onClick={list.refetch}>
        Оновити матеріали
      </button>
      <Table
        label={`Матеріали ${connectionId}`}
        rows={filtered}
        loading={list.isLoading}
        error={list.error}
        rowKey={(o) => o.object.object_id}
        empty={
          mediaType
            ? "Немає відповідного медіатипу серед завантажених матеріалів"
            : "Немає збережених матеріалів"
        }
        columns={[
          {
            header: "Об'єкт",
            cell: (o) => (
              <button type="button" className="link" onClick={() => onSelect(o)}>
                {o.object.object_id}
              </button>
            ),
          },
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
                <button type="button" className="btn btn-small" onClick={() => onSelect(o)}>
                  Переглянути
                </button>
                {o.material?.material_id ? (
                  <>
                    <Link
                      className="btn btn-small"
                      to={`/materials/${encodeURIComponent(o.material.material_id)}/trace`}
                    >
                      Простежити
                    </Link>
                    <button type="button" className="btn btn-small" onClick={() => onReprocess(o)}>
                      Повторно обробити
                    </button>
                  </>
                ) : (
                  <Link
                    className="btn btn-small"
                    to={`/results?connection_id=${encodeURIComponent(connectionId)}`}
                  >
                    Результати
                  </Link>
                )}
              </span>
            ),
          },
        ]}
      />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
    </Section>
  );
}

export function MaterialDetail({ connectionId, objectId }: { connectionId: string; objectId: string }) {
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
            ["Збережено", formatDate(detail.data.stored_at)],
            ["Розмір", formatBytes(detail.data.object.size_bytes)],
            ["Медіатип", detail.data.object.media_type ?? "—"],
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
      {detail.data ? (
        <>
          <div className="button-row">
            {detail.data.material?.material_id ? (
              <Link
                className="btn"
                to={`/materials/${encodeURIComponent(detail.data.material.material_id)}/trace`}
              >
                Історія обробки та результати
              </Link>
            ) : null}
            {detail.data.material?.source.source_id ? (
              <Link
                className="btn"
                to={`/sources/${encodeURIComponent(detail.data.material.source.source_id)}`}
              >
                Джерело
              </Link>
            ) : null}
          </div>
          <details>
            <summary>Метадані матеріалу</summary>
            <JsonView
              value={{
                object: detail.data.object,
                material: detail.data.material,
                stored_at: detail.data.stored_at,
              }}
            />
          </details>
        </>
      ) : null}
      {detail.isLoading || content.isLoading ? <Loading /> : null}
      <h3>Вміст{content.data?.partial ? ` (перші ${formatBytes(preview_max_bytes)})` : ""}</h3>
      <ErrorBox error={content.error} />
      {content.data ? (
        <pre className="content-preview" data-testid="content-preview">
          {formatMaterialContent(content.data.text)}
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
                  { header: "Стан елемента", cell: (s) => <Status value={s.status ?? null} /> },
                  { header: "Спроби", cell: (s) => (s.attempts !== undefined ? String(s.attempts) : "—") },
                  { header: "Доступний з", cell: (s) => formatInstant(s.available_at) },
                  {
                    header: "Історія спроб",
                    cell: (s) => (
                      <AttemptHistory
                        history={s.attempt_history}
                        label={`Історія спроб ${s.item_id ?? s.stage_id}`}
                      />
                    ),
                  },
                  {
                    header: "Виклик",
                    cell: (s) => (
                      <details>
                        <summary>Діагностика</summary>
                        <code>{s.invocation_id ?? "—"}</code>
                      </details>
                    ),
                  },
                  {
                    header: "Виходи",
                    cell: (s) => <TraceOutputs outputs={s.outputs} />,
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

type TraceOutput = NonNullable<MaterialTrace["observations"][number]["stages"][number]["outputs"]>[number];

export function TraceOutputs({ outputs }: { outputs: TraceOutput[] | undefined }) {
  if (!outputs?.length) return <span className="muted">Немає зафіксованих виходів</span>;
  const entities = outputs.filter((output) => output.kind === "entity").length;
  const raw = outputs.filter((output) => output.kind === "stored_object").length;
  return (
    <div className="trace-outputs">
      <span>
        {entities ? `Посилань на сутності: ${entities}. ` : ""}
        {raw ? `Збережених об'єктів: ${raw}.` : ""}
      </span>
      <details>
        <summary>Відкрити результати й об'єкти</summary>
        <ul>
          {outputs.map((output, index) => {
            // A scope may contain '|'. The exact key remains sufficient; no scope is guessed here.
            return (
              <li key={index}>
                {output.write_status === "simulated" ? (
                  <span>Імітований запис — робочі дані не збережено</span>
                ) : output.kind === "entity" && output.entity_type && output.canonical_key ? (
                  <Link
                    to={resultsHref({
                      ...(output.connection_id ? { connectionId: output.connection_id } : {}),
                      entityType: output.entity_type,
                      key: output.canonical_key,
                    })}
                  >
                    {entityTypeLabel(output.entity_type)} · {output.canonical_key}{" "}
                    {output.connection_id ? `(${output.connection_id})` : ""}
                  </Link>
                ) : output.kind === "stored_object" && output.connection_id && output.object_id ? (
                  <Link
                    to={`/materials?connection_id=${encodeURIComponent(output.connection_id)}&object_id=${encodeURIComponent(output.object_id)}`}
                  >
                    RAW {output.object_id} ({output.connection_id})
                  </Link>
                ) : (
                  <span>Вихід {output.kind}: адреса перегляду недоступна</span>
                )}
              </li>
            );
          })}
        </ul>
        <p className="muted">
          Це зафіксовані посилання. Трасування обмежене налаштуванням сервісу; актуальні записи могли
          змінитися після запуску.
        </p>
      </details>
      <details>
        <summary>Технічний JSON виходів</summary>
        <JsonView value={outputs} compact />
      </details>
    </div>
  );
}
