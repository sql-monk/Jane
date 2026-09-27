// Managed connections (ТЗ §11, ADR-0006): only non-secret params and secret references are shown and edited.
import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useApi } from "../app/context";
import { ifMatch, unwrap, unwrapWithEtag } from "../api/client";
import { useCursorList } from "../api/hooks";
import type { Connection, ConnectionTestResult, PlatformConnection } from "../api/types";
import { JsonEditor, checkJson, toJsonText } from "../components/JsonEditor";
import {
  ErrorBox,
  Field,
  JsonView,
  Loading,
  LoadMore,
  Notice,
  Page,
  ReasonAction,
  Section,
  Status,
  Table,
} from "../components/ui";
import { SCHEMAS, validateAgainst } from "../lib/schema";
import { redactSecrets, validateConnectionSecrets } from "../lib/secrets";
import { formatDate } from "../lib/format";

export function ConnectionsPage() {
  const api = useApi();
  const [kind, setKind] = useState("");
  const [editing, setEditing] = useState<string | "new" | null>(null);
  const list = useCursorList(["connections", kind], (cursor, limit) =>
    unwrap(
      api.orchestrator.GET("/v1/connections", {
        params: { query: { limit, ...(cursor ? { cursor } : {}), ...(kind ? { kind } : {}) } },
      }),
    ),
  );
  return (
    <Page
      title="Підключення"
      actions={
        <button type="button" className="btn btn-primary" onClick={() => setEditing("new")}>
          Нове підключення
        </button>
      }
    >
      <Notice>
        Значення секретів ніколи не передаються через API й не відображаються: підключення містить лише
        посилання <code>env:</code>, <code>file:</code> або <code>vault:</code>, які розв'язує
        сервіс-виконавець у своєму середовищі.
      </Notice>
      <div className="filters">
        <Field label="Тип">
          <input value={kind} onChange={(e) => setKind(e.target.value)} placeholder="postgresql" />
        </Field>
      </div>
      {list.isLoading ? <Loading /> : null}
      <ErrorBox error={list.error} />
      <Table
        label="Підключення"
        rows={list.items.map(redactSecrets)}
        rowKey={(c) => c.connection.connection_id}
        columns={[
          {
            header: "Підключення",
            cell: (c) => (
              <button type="button" className="link" onClick={() => setEditing(c.connection.connection_id)}>
                {c.connection.connection_id}
              </button>
            ),
          },
          { header: "Тип", cell: (c) => c.connection.kind },
          { header: "Параметри", cell: (c) => <JsonView value={c.connection.params ?? {}} compact /> },
          { header: "Посилання на секрети", cell: (c) => <SecretRefs refs={c.connection.secret_refs} /> },
          { header: "Синхронізація", cell: (c) => <ExecutorsSync executors={c.executors} /> },
        ]}
      />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
      {editing ? (
        <ConnectionEditor
          key={editing}
          connectionId={editing === "new" ? null : editing}
          onDone={() => setEditing(null)}
        />
      ) : null}
    </Page>
  );
}

function SecretRefs({ refs }: { refs: Connection["secret_refs"] }) {
  const entries = Object.entries(redactSecrets(refs ?? {}));
  if (!entries.length) return <span className="muted">—</span>;
  return (
    <ul className="plain">
      {entries.map(([name, ref]) => (
        <li key={name}>
          {name}: <code>{ref}</code>
        </li>
      ))}
    </ul>
  );
}

function ExecutorsSync({ executors }: { executors: PlatformConnection["executors"] }) {
  if (!executors?.length) return <span className="muted">—</span>;
  return (
    <ul className="plain">
      {executors.map((e) => (
        <li key={e.executor}>
          {e.executor}: <Status value={e.sync_status} />{" "}
          {e.message ? <span className="muted">{e.message}</span> : null}
        </li>
      ))}
    </ul>
  );
}

interface RefRow {
  name: string;
  ref: string;
}

function ConnectionEditor({ connectionId, onDone }: { connectionId: string | null; onDone: () => void }) {
  const api = useApi();
  const queryClient = useQueryClient();
  const isNew = connectionId === null;
  const [id, setId] = useState(connectionId ?? "");
  const [kind, setKind] = useState("postgresql");
  const [title, setTitle] = useState("");
  const [paramsText, setParamsText] = useState("{}");
  const [refs, setRefs] = useState<RefRow[]>([]);
  const [etag, setEtag] = useState<string | null>(null);
  const [test, setTest] = useState<{ executor: string; result: ConnectionTestResult } | null>(null);

  const loaded = useQuery({
    queryKey: ["connection", connectionId],
    enabled: !isNew,
    queryFn: async () => {
      const result = await unwrapWithEtag(
        api.orchestrator.GET("/v1/connections/{connection_id}", {
          params: { path: { connection_id: connectionId as string } },
        }),
      );
      const c = redactSecrets(result.data).connection;
      setKind(c.kind);
      setTitle(c.title ?? "");
      setParamsText(toJsonText(c.params ?? {}));
      setRefs(Object.entries(c.secret_refs ?? {}).map(([name, ref]) => ({ name, ref })));
      setEtag(result.etag);
      return result;
    },
    staleTime: Infinity,
  });

  const params = checkJson(paramsText);
  const secretRefs = Object.fromEntries(refs.filter((r) => r.name || r.ref).map((r) => [r.name, r.ref]));
  const connection: Connection = {
    connection_id: id,
    kind,
    ...(title ? { title } : {}),
    ...(params.value && typeof params.value === "object"
      ? { params: params.value as Record<string, unknown> }
      : {}),
    ...(Object.keys(secretRefs).length ? { secret_refs: secretRefs } : {}),
  } as Connection;
  const issues = [
    ...(params.parseError ? [`params: ${params.parseError}`] : []),
    ...validateConnectionSecrets((params.value as Record<string, unknown> | undefined) ?? {}, secretRefs),
    ...validateAgainst(SCHEMAS.connection, connection).map((i) => `${i.pointer} ${i.message}`),
  ];

  const save = useMutation({
    mutationFn: () =>
      unwrapWithEtag(
        api.orchestrator.PUT("/v1/connections/{connection_id}", {
          params: { path: { connection_id: id }, header: ifMatch(etag) },
          body: connection,
        }),
      ),
    onSuccess: (result) => {
      setEtag(result.etag);
      void queryClient.invalidateQueries({ queryKey: ["connections"] });
    },
  });
  const remove = useMutation({
    mutationFn: () =>
      unwrap(
        api.orchestrator.DELETE("/v1/connections/{connection_id}", {
          params: { path: { connection_id: id } },
        }),
      ),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["connections"] });
      onDone();
    },
  });
  const runTest = useMutation({
    mutationFn: async (executor: string) => ({
      executor,
      result: await unwrap(
        api
          .executor(executor)
          .POST("/v1/connections/{connection_id}/test", { params: { path: { connection_id: id } } }),
      ),
    }),
    onSuccess: setTest,
  });

  const executors = (save.data?.data ?? loaded.data?.data)?.executors ?? [];

  return (
    <Section
      title={isNew ? "Нове підключення" : `Підключення ${connectionId}`}
      actions={
        <button type="button" className="btn" onClick={onDone}>
          Закрити
        </button>
      }
    >
      {loaded.isLoading ? <Loading /> : null}
      <ErrorBox error={loaded.error} />
      <div className="grid-3">
        <Field label="connection_id">
          <input value={id} disabled={!isNew} onChange={(e) => setId(e.target.value)} />
        </Field>
        <Field label="Тип">
          <input list="connection-kinds" value={kind} onChange={(e) => setKind(e.target.value)} />
          <datalist id="connection-kinds">
            {[
              "postgresql",
              "sqlserver",
              "mongodb",
              "s3",
              "minio",
              "filesystem",
              "llm_provider",
              "telegram_account",
              "search_provider",
              "http",
            ].map((k) => (
              <option key={k} value={k} />
            ))}
          </datalist>
        </Field>
        <Field label="Назва">
          <input value={title} onChange={(e) => setTitle(e.target.value)} />
        </Field>
      </div>
      <Field label="Несекретні параметри (host, port, database, bucket…)">
        <JsonEditor
          text={paramsText}
          onChange={setParamsText}
          label="Параметри підключення"
          minHeight="6rem"
        />
      </Field>
      <h3>Посилання на секрети</h3>
      <p className="muted">
        Лише посилання: env:ЗМІННА, file:/шлях, vault:шлях#ключ. Самі значення тут не вводяться.
      </p>
      {refs.map((row, i) => (
        <div key={i} className="inline-form">
          <input
            aria-label={`Ім'я секрету ${i + 1}`}
            placeholder="password"
            value={row.name}
            onChange={(e) => setRefs(refs.map((r, j) => (j === i ? { ...r, name: e.target.value } : r)))}
          />
          <input
            aria-label={`Посилання на секрет ${i + 1}`}
            placeholder="env:RESULTS_PG_PASSWORD"
            value={row.ref}
            autoComplete="off"
            onChange={(e) => setRefs(refs.map((r, j) => (j === i ? { ...r, ref: e.target.value } : r)))}
          />
          <button
            type="button"
            className="btn btn-small"
            onClick={() => setRefs(refs.filter((_, j) => j !== i))}
          >
            Прибрати
          </button>
        </div>
      ))}
      <button
        type="button"
        className="btn btn-small"
        onClick={() => setRefs([...refs, { name: "", ref: "" }])}
      >
        Додати посилання
      </button>
      {issues.length ? (
        <ul className="error-inline" role="alert" aria-label="Помилки підключення">
          {issues.map((i) => (
            <li key={i}>{i}</li>
          ))}
        </ul>
      ) : null}
      <div className="button-row">
        <button
          type="button"
          className="btn btn-primary"
          disabled={issues.length > 0 || save.isPending}
          onClick={() => save.mutate()}
        >
          Зберегти й синхронізувати
        </button>
        {!isNew ? (
          <ReasonAction
            label="Видалити"
            confirmLabel="Видалити підключення"
            danger
            requireReason={false}
            onConfirm={() => remove.mutate()}
          />
        ) : null}
      </div>
      <ErrorBox error={save.error} title="Не збережено" />
      <ErrorBox error={remove.error} title="Не видалено" />
      {save.isSuccess ? (
        <Notice tone="ok">Збережено; синхронізація з виконавцями — асинхронна.</Notice>
      ) : null}
      {executors.length ? (
        <>
          <h3>Синхронізація й перевірка у виконавців</h3>
          <Table
            label="Виконавці підключення"
            rows={executors}
            rowKey={(e) => e.executor}
            columns={[
              { header: "Виконавець", cell: (e) => e.executor },
              { header: "Стан", cell: (e) => <Status value={e.sync_status} /> },
              { header: "Синхронізовано", cell: (e) => formatDate(e.synced_at) },
              {
                header: "",
                cell: (e) => (
                  <button
                    type="button"
                    className="btn btn-small"
                    onClick={() => runTest.mutate(e.executor)}
                    disabled={runTest.isPending}
                  >
                    Перевірити
                  </button>
                ),
              },
            ]}
          />
        </>
      ) : null}
      <ErrorBox error={runTest.error} title="Перевірку не виконано" />
      {test ? (
        <div aria-label="Результат перевірки підключення">
          <p>
            {test.executor}: <Status value={test.result.ok ? "ok" : "failed"} />{" "}
            {test.result.latency_ms !== undefined ? `${test.result.latency_ms} мс` : ""}{" "}
            {test.result.message ?? ""}
          </p>
          <Table
            label="Розв'язання секретів"
            rows={Object.entries(test.result.secrets_resolved ?? {})}
            rowKey={([k]) => k}
            columns={[
              { header: "Секрет", cell: ([k]) => k },
              { header: "Розв'язано", cell: ([, v]) => <Status value={v ? "ok" : "failed"} /> },
            ]}
          />
        </div>
      ) : null}
    </Section>
  );
}
