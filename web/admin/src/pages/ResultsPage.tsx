import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useApi } from "../app/context";
import { unwrap } from "../api/client";
import { useCursorList } from "../api/hooks";
import type { EntityState, EntityHistoryEntry } from "../api/types";
import { storageName, useStorageConnections } from "../components/StorageConnections";
import {
  ErrorBox,
  Field,
  JsonView,
  Loading,
  LoadMore,
  Notice,
  Page,
  Section,
  Table,
  type Column,
} from "../components/ui";
import { formatDate } from "../lib/format";
import "../results.css";

type HistorySelection = { connectionId: string; entityType: string; entityKey: string; context: string };

export function ResultsPage() {
  const api = useApi();
  const [params, setParams] = useSearchParams();
  const connections = useStorageConnections();
  const sources = useCursorList(["result-source-types"], (cursor, limit) =>
    unwrap(
      api.orchestrator.GET("/v1/sources", { params: { query: { limit, ...(cursor ? { cursor } : {}) } } }),
    ),
  );
  // Resolve the complete catalogs before inferring a unique type or claiming all stores are listed.
  useEffect(() => {
    if (connections.hasMore && !connections.loadingMore && !connections.error) connections.loadMore();
  }, [connections]);
  useEffect(() => {
    if (sources.hasMore && !sources.loadingMore && !sources.error) sources.loadMore();
  }, [sources]);
  const types = [...new Set(sources.items.flatMap((source) => source.expected_entity_types ?? []))].sort();
  const inferredType =
    !sources.isLoading && !sources.hasMore && !sources.error && types.length === 1 ? types[0]! : "";
  const connectionId = params.get("connection_id") ?? "";
  const entityType = params.has("entity_type") ? (params.get("entity_type") ?? "") : inferredType;
  const scope = params.get("scope") ?? "";
  const entityKey = params.get("key") ?? "";
  const [search, setSearch] = useState("");
  const [history, setHistory] = useState<HistorySelection | null>(null);
  const context = JSON.stringify([connectionId, entityType, scope, entityKey, search]);
  const ids = connectionId ? [connectionId] : connections.items.map((connection) => connection.connection_id);
  const update = (key: string, value: string) => {
    const next = new URLSearchParams(params);
    if (value || key === "entity_type") next.set(key, value);
    else next.delete(key);
    setHistory(null);
    setParams(next);
  };
  return (
    <Page
      title="Результати"
      actions={
        <Link className="btn" to="/materials">
          Зібрані матеріали
        </Link>
      }
    >
      <p className="muted">
        Розібрані дані: актуальні назви, ціни та інші поля сутностей зі сховищ. Повні записи й походження
        доступні в деталях та історії.
      </p>
      <div className="filters">
        <Field label="Сховище результатів">
          <select value={connectionId} onChange={(event) => update("connection_id", event.target.value)}>
            <option value="">Усі сховища</option>
            {connectionId &&
            !connections.items.some((connection) => connection.connection_id === connectionId) ? (
              <option value={connectionId}>{connectionId}</option>
            ) : null}
            {connections.items.map((connection) => (
              <option key={connection.connection_id} value={connection.connection_id}>
                {storageName(connection)}
              </option>
            ))}
          </select>
        </Field>
        <Field
          label="Тип результату"
          hint={
            inferredType && !params.has("entity_type")
              ? `Тип ${inferredType} обрано з каталогу джерел: це єдиний очікуваний тип.`
              : "Виберіть очікуваний тип зі списку або введіть інший."
          }
        >
          <input
            value={entityType}
            list="result-entity-types"
            onChange={(event) => update("entity_type", event.target.value)}
            placeholder="Тип із пакета обробника"
          />
          <datalist id="result-entity-types">
            {types.map((type) => (
              <option key={type} value={type} />
            ))}
          </datalist>
        </Field>
        <Field
          label="Пошук у завантажених результатах"
          hint="Шукає лише серед уже завантажених рядків. Натисніть «Показати ще», щоб додати дані."
        >
          <input
            type="search"
            value={search}
            onChange={(event) => {
              setHistory(null);
              setSearch(event.target.value);
            }}
          />
        </Field>
      </div>
      <details className="result-filters">
        <summary>Додаткові фільтри</summary>
        <div className="filters">
          <Field
            label="Область даних"
            hint="Групування ключів, визначене обробником. Залиште порожнім для всіх областей."
          >
            <input value={scope} onChange={(event) => update("scope", event.target.value)} />
          </Field>
          <Field label="Канонічний ключ">
            <input value={entityKey} onChange={(event) => update("key", event.target.value)} />
          </Field>
        </div>
      </details>
      {connections.isLoading || (!params.has("entity_type") && sources.isLoading) ? <Loading /> : null}
      <ErrorBox error={connections.error} title="Не вдалося отримати список сховищ" />
      <ErrorBox
        error={sources.error}
        title="Не вдалося отримати очікувані типи; введіть тип сутності вручну"
      />
      {connections.error && connections.hasMore ? (
        <LoadMore hasMore loading={connections.loadingMore} onClick={connections.loadMore} />
      ) : null}
      {!connections.isLoading && !connections.error && !ids.length ? (
        <Notice>Немає налаштованих сховищ. Додайте підключення у розділі «Підключення».</Notice>
      ) : null}
      {!entityType && !sources.isLoading ? (
        <Notice>Виберіть або введіть тип сутності, щоб переглянути розібрані дані.</Notice>
      ) : null}
      {entityType
        ? ids.map((id) => (
            <StorageResults
              key={id}
              connectionId={id}
              title={storageName(
                connections.items.find((connection) => connection.connection_id === id) ?? {
                  connection_id: id,
                  kind: "",
                },
              )}
              entityType={entityType}
              scope={scope}
              entityKey={entityKey}
              search={search}
              explicitStore={Boolean(connectionId)}
              onHistory={(key) => setHistory({ connectionId: id, entityType, entityKey: key, context })}
            />
          ))
        : null}
      {history?.context === context ? (
        <EntityHistory key={JSON.stringify(history)} selection={history} onClose={() => setHistory(null)} />
      ) : null}
    </Page>
  );
}

function plainValue(value: unknown): string {
  if (value === undefined || value === null || value === "") return "—";
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean")
    return String(value);
  return JSON.stringify(value);
}

function priceValue(value: unknown): string {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return plainValue(value);
  const price = value as Record<string, unknown>;
  const amount = price["amount"];
  if (amount === undefined || amount === null || amount === "") return "—";
  return `${plainValue(amount)}${typeof price["currency"] === "string" && price["currency"] ? ` ${price["currency"]}` : ""}`;
}

function OfferLink({ value }: { value: unknown }) {
  if (typeof value !== "string" || !value) return <>—</>;
  try {
    const url = new URL(value);
    if (url.protocol === "https:" || url.protocol === "http:")
      return (
        <a href={url.href} target="_blank" rel="noopener noreferrer">
          Відкрити товар
        </a>
      );
  } catch {
    /* Invalid URLs remain visible as data. */
  }
  return <span>{value}</span>;
}

function StateDetails({ entity }: { entity: EntityState }) {
  const materials = [
    ...new Set(
      Object.values(entity.field_orders ?? {}).flatMap((order) =>
        order.material_id ? [order.material_id] : [],
      ),
    ),
  ];
  return (
    <details className="result-details">
      <summary>Усі поля та метадані</summary>
      {materials.map((id) => (
        <p key={id}>
          <Link to={`/materials/${encodeURIComponent(id)}/trace`}>Матеріал {id}</Link>
        </p>
      ))}
      <JsonView value={entity} />
    </details>
  );
}

function StorageResults({
  connectionId,
  title,
  entityType,
  scope,
  entityKey,
  search,
  explicitStore,
  onHistory,
}: {
  connectionId: string;
  title: string;
  entityType: string;
  scope: string;
  entityKey: string;
  search: string;
  explicitStore: boolean;
  onHistory: (key: string) => void;
}) {
  const api = useApi();
  const list = useCursorList(["entities", connectionId, entityType, scope, entityKey], (cursor, limit) =>
    unwrap(
      api.storage.GET("/v1/entities", {
        params: {
          query: {
            connection_id: connectionId,
            entity_type: entityType,
            limit,
            ...(cursor ? { cursor } : {}),
            ...(scope ? { scope } : {}),
            ...(entityKey ? { key: entityKey } : {}),
          },
        },
      }),
    ),
  );
  const term = search.trim().toLocaleLowerCase();
  const rows = term
    ? list.items.filter((entity) => JSON.stringify(entity).toLocaleLowerCase().includes(term))
    : list.items;
  const common: Column<EntityState>[] = [
    { header: "Оновлено", cell: (entity) => formatDate(entity.updated_at) },
    {
      header: "Історія",
      cell: (entity) =>
        entity.canonical_key ? (
          <button type="button" className="btn btn-small" onClick={() => onHistory(entity.canonical_key!)}>
            Історія
          </button>
        ) : (
          "—"
        ),
    },
    { header: "Деталі", cell: (entity) => <StateDetails entity={entity} /> },
  ];
  const offerColumns: Column<EntityState>[] = [
    {
      header: "Назва",
      className: "result-title",
      cell: (entity) => <span>{plainValue((entity.fields as Record<string, unknown>)["title"])}</span>,
    },
    { header: "Магазин", cell: (entity) => plainValue((entity.fields as Record<string, unknown>)["shop"]) },
    { header: "Бренд", cell: (entity) => plainValue((entity.fields as Record<string, unknown>)["brand"]) },
    { header: "Ціна", cell: (entity) => priceValue((entity.fields as Record<string, unknown>)["price"]) },
    {
      header: "Наявність",
      cell: (entity) =>
        (entity.fields as Record<string, unknown>)["availability"] === "unknown"
          ? "Невідомо"
          : plainValue((entity.fields as Record<string, unknown>)["availability"]),
    },
    {
      header: "Посилання",
      cell: (entity) => <OfferLink value={(entity.fields as Record<string, unknown>)["url"]} />,
    },
  ];
  const genericColumns: Column<EntityState>[] = [
    { header: "Ключ", cell: (entity) => <code>{entity.canonical_key ?? JSON.stringify(entity.key)}</code> },
    { header: "Поля", cell: (entity) => <JsonView value={entity.fields} compact /> },
    { header: "Версія", cell: (entity) => entity.version ?? "—" },
  ];
  return (
    <Section
      title={title}
      actions={
        <button type="button" className="btn" onClick={list.refetch}>
          Оновити
        </button>
      }
    >
      {list.isLoading ? <Loading /> : null}
      <ErrorBox error={list.error} />
      <p className="muted">
        Завантажено: {list.items.length}. Показано: {rows.length}.
        {list.hasMore
          ? " Є наступна сторінка."
          : list.error
            ? " Повноту даних не підтверджено через помилку."
            : list.isLoading
              ? ""
              : " Усі сторінки завантажено."}
      </p>
      <div className="result-table">
        <Table
          label={explicitStore ? "Сутності" : `Сутності ${connectionId}`}
          rows={rows}
          rowKey={(entity) => entity.canonical_key ?? JSON.stringify(entity.key)}
          empty={
            list.isLoading
              ? "Завантаження даних…"
              : list.error
                ? "Дані недоступні через помилку"
                : term
                  ? "Немає збігів серед завантажених результатів"
                  : "Немає сутностей цього типу"
          }
          columns={[...(entityType === "offer" ? offerColumns : genericColumns), ...common]}
        />
      </div>
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
    </Section>
  );
}

function HistoryDetails({ entry }: { entry: EntityHistoryEntry }) {
  const materialId = entry.record.observation.material_id;
  const runId = entry.record.provenance?.run_id;
  return (
    <details className="result-details">
      <summary>Повний запис і походження</summary>
      <div className="button-row">
        {materialId ? (
          <Link to={`/materials/${encodeURIComponent(materialId)}/trace`}>Матеріал {materialId}</Link>
        ) : null}
        {runId ? <Link to={`/runs/${encodeURIComponent(runId)}`}>Запуск {runId}</Link> : null}
      </div>
      <JsonView value={entry} />
    </details>
  );
}

function EntityHistory({ selection, onClose }: { selection: HistorySelection; onClose: () => void }) {
  const api = useApi();
  const { connectionId, entityType, entityKey } = selection;
  const history = useCursorList(["entity-history", connectionId, entityType, entityKey], (cursor, limit) =>
    unwrap(
      api.storage.GET("/v1/entity-history", {
        params: {
          query: {
            connection_id: connectionId,
            entity_type: entityType,
            key: entityKey,
            limit,
            ...(cursor ? { cursor } : {}),
          },
        },
      }),
    ),
  );
  return (
    <Section
      title={`Історія ${entityKey}`}
      actions={
        <button type="button" className="btn" onClick={onClose}>
          Закрити історію
        </button>
      }
    >
      <p className="muted">
        Сховище: {connectionId}. Тип: {entityType}. Завантажено оновлень: {history.items.length}.
        {history.hasMore ? " Є наступна сторінка." : ""}
      </p>
      {history.isLoading ? <Loading /> : null}
      <ErrorBox error={history.error} />
      <Table
        label="Історія сутності"
        rows={history.items}
        rowKey={(entry, index) => `${entry.delivery_key ?? ""}-${index}`}
        columns={[
          { header: "Отримано", cell: (entry) => formatDate(entry.received_at) },
          { header: "Спостереження", cell: (entry) => formatDate(entry.record.observation.observed_at) },
          { header: "Застосовані поля", cell: (entry) => entry.applied_fields.join(", ") || "—" },
          {
            header: "Запізнілі поля",
            cell: (entry) =>
              entry.stale_fields.length ? (
                <span className="badge badge-warn">{entry.stale_fields.join(", ")}</span>
              ) : (
                "—"
              ),
          },
          { header: "Запис", cell: (entry) => <JsonView value={entry.record.fields} compact /> },
          { header: "Деталі", cell: (entry) => <HistoryDetails entry={entry} /> },
        ]}
      />
      <LoadMore hasMore={history.hasMore} loading={history.loadingMore} onClick={history.loadMore} />
    </Section>
  );
}
