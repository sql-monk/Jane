import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { useApi } from "../app/context";
import { unwrap } from "../api/client";
import { useCursorList } from "../api/hooks";
import { ConnectionPicker } from "../components/ConnectionPicker";
import { ErrorBox, Field, JsonView, Loading, LoadMore, Notice, Page, Section, Table } from "../components/ui";
import { formatDate } from "../lib/format";

export function ResultsPage() {
  const api = useApi();
  const [params, setParams] = useSearchParams();
  const connectionId = params.get("connection_id") ?? "";
  const entityType = params.get("entity_type") ?? "";
  const scope = params.get("scope") ?? "";
  const [historyKey, setHistoryKey] = useState<string | null>(null);
  const ready = Boolean(connectionId && entityType);
  const list = useCursorList(["entities", connectionId, entityType, scope], (cursor, limit) =>
    ready
      ? unwrap(
          api.storage.GET("/v1/entities", {
            params: {
              query: {
                connection_id: connectionId,
                entity_type: entityType,
                limit,
                ...(cursor ? { cursor } : {}),
                ...(scope ? { scope } : {}),
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
    <Page title="Результати">
      <p className="muted">
        Актуальний стан сутностей у сховищі результатів та історія їх оновлень (включно із запізнілими).
      </p>
      <div className="filters">
        <ConnectionPicker
          label="Сховище результатів"
          value={connectionId}
          onChange={(v) => update("connection_id", v)}
        />
        <Field label="Тип сутності">
          <input
            value={entityType}
            onChange={(e) => update("entity_type", e.target.value)}
            placeholder="product"
          />
        </Field>
        <Field label="Область (scope)">
          <input value={scope} onChange={(e) => update("scope", e.target.value)} />
        </Field>
      </div>
      {!ready ? <Notice>Вкажіть підключення сховища й тип сутності.</Notice> : null}
      {list.isLoading ? <Loading /> : null}
      <ErrorBox error={list.error} />
      <Table
        label="Сутності"
        rows={list.items}
        rowKey={(e) => e.canonical_key ?? JSON.stringify(e.key)}
        empty={ready ? "Немає сутностей" : "—"}
        columns={[
          { header: "Ключ", cell: (e) => <code>{e.canonical_key ?? JSON.stringify(e.key)}</code> },
          { header: "Поля", cell: (e) => <JsonView value={e.fields} compact /> },
          { header: "Версія", cell: (e) => e.version ?? "—" },
          { header: "Оновлено", cell: (e) => formatDate(e.updated_at) },
          {
            header: "Історія",
            cell: (e) =>
              e.canonical_key ? (
                <button
                  type="button"
                  className="btn btn-small"
                  onClick={() => setHistoryKey(e.canonical_key ?? null)}
                >
                  Історія
                </button>
              ) : null,
          },
        ]}
      />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
      {historyKey ? (
        <EntityHistory connectionId={connectionId} entityType={entityType} entityKey={historyKey} />
      ) : null}
    </Page>
  );
}

function EntityHistory({
  connectionId,
  entityType,
  entityKey,
}: {
  connectionId: string;
  entityType: string;
  entityKey: string;
}) {
  const api = useApi();
  const history = useQuery({
    queryKey: ["entity-history", connectionId, entityType, entityKey],
    queryFn: () =>
      unwrap(
        api.storage.GET("/v1/entity-history", {
          params: { query: { connection_id: connectionId, entity_type: entityType, key: entityKey } },
        }),
      ),
  });
  return (
    <Section title={`Історія ${entityKey}`}>
      {history.isLoading ? <Loading /> : null}
      <ErrorBox error={history.error} />
      <Table
        label="Історія сутності"
        rows={history.data?.items ?? []}
        rowKey={(h, i) => `${h.delivery_key ?? ""}-${i}`}
        columns={[
          { header: "Отримано", cell: (h) => formatDate(h.received_at) },
          { header: "Спостереження", cell: (h) => formatDate(h.record.observation?.observed_at) },
          { header: "Застосовані поля", cell: (h) => (h.applied_fields ?? []).join(", ") || "—" },
          {
            header: "Запізнілі поля",
            cell: (h) =>
              h.stale_fields?.length ? (
                <span className="badge badge-warn">{h.stale_fields.join(", ")}</span>
              ) : (
                "—"
              ),
          },
          { header: "Запис", cell: (h) => <JsonView value={h.record.fields} compact /> },
        ]}
      />
    </Section>
  );
}
