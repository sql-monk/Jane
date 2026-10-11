import { useQueries } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useApi, useConfig } from "../app/context";
import { unwrap } from "../api/client";
import { useCursorList } from "../api/hooks";
import type { EntityState, EntityHistoryEntry } from "../api/types";
import type { components as StorageComponents } from "../api/generated/storage";
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
import { ApiError } from "../api/problem";
import { entityTypeLabel, resultsHref } from "../lib/results-context";
import { formatDate } from "../lib/format";
import "../results.css";

type HistorySelection = { connectionId: string; entityType: string; entityKey: string; context: string };

export function ResultsPage() {
  const api = useApi();
  const [params, setParams] = useSearchParams();
  const connections = useStorageConnections();
  const { page_size } = useConfig();
  useEffect(() => {
    if (connections.hasMore && !connections.loadingMore && !connections.error) connections.loadMore();
  }, [connections]);
  const connectionId = params.get("connection_id") ?? "";
  const ids = connectionId ? [connectionId] : connections.items.map((connection) => connection.connection_id);
  const catalogs = useQueries({
    queries: ids.map((id) => ({
      queryKey: ["entity-types", id, params.get("scope") ?? "", page_size],
      queryFn: async () => {
        const items: StorageComponents["schemas"]["EntityTypeSummary"][] = [];
        let cursor: string | undefined;
        let searchSupported: boolean;
        const seen = new Set<string>();
        do {
          const page = await unwrap(
            api.storage.GET("/v1/entity-types", {
              params: {
                query: {
                  connection_id: id,
                  limit: page_size,
                  ...(params.get("scope") ? { scope: params.get("scope")! } : {}),
                  ...(cursor ? { cursor } : {}),
                },
              },
            }),
          );
          items.push(...page.items);
          searchSupported = page.search_supported;
          cursor = page.next_cursor ?? undefined;
          if (cursor && seen.has(cursor)) throw new Error("Каталог повернув повторний курсор");
          if (cursor) seen.add(cursor);
        } while (cursor);
        return { items, searchSupported };
      },
    })),
  });
  const types = [
    ...new Set(catalogs.flatMap((catalog) => catalog.data?.items.map((row) => row.entity_type) ?? [])),
  ].sort();
  const complete =
    !connections.isLoading &&
    !connections.hasMore &&
    !connections.error &&
    catalogs.every((catalog) => catalog.isSuccess);
  const inferredType = complete && types.length === 1 ? types[0]! : "";
  const entityType = params.has("entity_type") ? (params.get("entity_type") ?? "") : inferredType;
  const scope = params.get("scope") ?? "";
  const entityKey = params.get("key") ?? "";
  const search = params.get("search") ?? "";
  const [searchDraft, setSearchDraft] = useState(search);
  useEffect(() => setSearchDraft(search), [search]);
  const [history, setHistory] = useState<HistorySelection | null>(null);
  const context = JSON.stringify([connectionId, entityType, scope, entityKey, search]);
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
              ? `Тип ${entityTypeLabel(inferredType)} обрано зі сховищ: це єдиний збережений тип.`
              : "Виберіть фактично збережені дані нижче або введіть тип вручну для старого адаптера."
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
              <option key={type} value={type}>
                {entityTypeLabel(type)}
              </option>
            ))}
          </datalist>
        </Field>
        <Field label="Пошук у всьому сховищі" hint="Пошук по ключах і полях до розбиття на сторінки.">
          <form
            className="result-search"
            onSubmit={(event) => {
              event.preventDefault();
              update("search", searchDraft.trim());
            }}
          >
            <input
              type="search"
              value={searchDraft}
              onChange={(event) => setSearchDraft(event.target.value)}
            />
            <button className="btn" type="submit" disabled={!entityType}>
              Знайти
            </button>
          </form>
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
      {connections.isLoading || catalogs.some((catalog) => catalog.isLoading) ? <Loading /> : null}
      <ErrorBox error={connections.error} title="Не вдалося отримати список сховищ" />
      {!connections.isLoading && !connections.error && !ids.length ? (
        <Notice>Немає налаштованих сховищ. Додайте підключення у розділі «Підключення».</Notice>
      ) : null}
      {!params.get("entity_type") ? (
        <div className="result-catalogs">
          {catalogs.map((catalog, index) => {
            const id = ids[index]!;
            const title = storageName(
              connections.items.find((connection) => connection.connection_id === id) ?? {
                connection_id: id,
                kind: "",
              },
            );
            return (
              <Section
                key={id}
                title={"Збережені дані: " + title}
                actions={
                  <button
                    className="btn"
                    type="button"
                    disabled={catalog.isFetching}
                    onClick={() => void catalog.refetch()}
                  >
                    Оновити каталог
                  </button>
                }
              >
                {catalog.error instanceof ApiError && catalog.error.problem.code === "not_implemented" ? (
                  <Notice>
                    Цей адаптер не надає каталог типів. Введіть тип результату вручну; можливість пошуку
                    залежить від адаптера.
                  </Notice>
                ) : (
                  <ErrorBox error={catalog.error} title="Не вдалося отримати каталог даних" />
                )}
                {catalog.isSuccess && !catalog.data.items.length ? (
                  <Notice>У цьому сховищі ще немає розібраних даних.</Notice>
                ) : null}
                <div className="result-type-cards">
                  {catalog.data?.items.map((row) => (
                    <Link
                      key={row.entity_type}
                      className="result-type-card"
                      to={resultsHref({
                        connectionId: id,
                        entityType: row.entity_type,
                        scope,
                        key: entityKey,
                      })}
                    >
                      <strong>{entityTypeLabel(row.entity_type)}</strong>
                      <span>{row.entity_count.toLocaleString("uk-UA")} записів</span>
                      <small>{row.entity_type}</small>
                    </Link>
                  ))}
                </div>
              </Section>
            );
          })}
        </div>
      ) : null}
      {!entityType && params.has("entity_type") ? (
        <Notice>Виберіть тип із каталогу або введіть його назву.</Notice>
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
  const list = useCursorList(
    ["entities", connectionId, entityType, scope, entityKey, search],
    (cursor, limit) =>
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
              ...(search.trim() ? { search: search.trim() } : {}),
            },
          },
        }),
      ),
  );
  const term = search.trim();
  const rows = list.items;
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
          loading={list.isLoading}
          error={list.error}
          rowKey={(entity) => entity.canonical_key ?? JSON.stringify(entity.key)}
          empty={
            list.isLoading
              ? "Завантаження даних…"
              : list.error
                ? "Дані недоступні через помилку"
                : term
                  ? "Немає збігів у сховищі"
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
        loading={history.isLoading}
        error={history.error}
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
