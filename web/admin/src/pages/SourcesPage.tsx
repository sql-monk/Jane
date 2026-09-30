import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useApi } from "../app/context";
import { ifMatch, newIdempotencyKey, unwrap, unwrapWithEtag } from "../api/client";
import { useCursorList } from "../api/hooks";
import type { Source } from "../api/types";
import { JsonEditor, checkJson, toJsonText } from "../components/JsonEditor";
import { EffectiveLimitsView } from "../components/EffectiveLimitsView";
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
} from "../components/ui";
import { SCHEMAS, validateAgainst } from "../lib/schema";
import { formatDate, refLabel } from "../lib/format";
import { StrategiesSummary } from "./RulesEditorPage";

export function SourcesPage() {
  const api = useApi();
  const list = useCursorList(["sources"], (cursor, limit) =>
    unwrap(
      api.orchestrator.GET("/v1/sources", { params: { query: { limit, ...(cursor ? { cursor } : {}) } } }),
    ),
  );
  return (
    <Page
      title="Джерела"
      actions={
        <>
          <Link className="btn" to="/assistant">
            Підключити через асистента
          </Link>
          <Link className="btn btn-primary" to="/sources/new">
            Нове джерело
          </Link>
        </>
      }
    >
      {list.isLoading ? <Loading /> : null}
      <ErrorBox error={list.error} />
      <Table
        label="Джерела"
        rows={list.items}
        rowKey={(s) => s.source_id}
        columns={[
          {
            header: "Джерело",
            cell: (s) => <Link to={`/sources/${encodeURIComponent(s.source_id)}`}>{s.source_id}</Link>,
          },
          { header: "Назва", cell: (s) => s.title },
          { header: "Тип", cell: (s) => s.kind },
          {
            header: "Адреса",
            cell: (s) => s.locator.url ?? s.locator.telegram_username ?? s.locator.telegram_channel_id ?? "—",
          },
          { header: "Правила колектора", cell: (s) => refLabel(s.collector_rules) },
          {
            header: "Невідомі сторінки → LLM",
            cell: (s) =>
              s.forward_unknown_to_llm ? <Status value="on" /> : <span className="muted">вимкнено</span>,
          },
        ]}
      />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
    </Page>
  );
}

const EMPTY_SOURCE: Source = {
  source_id: "",
  kind: "web",
  title: "",
  locator: { url: "" },
  forward_unknown_to_llm: false,
};

function withoutReadOnly(source: Source): Source {
  const { created_at: _c, updated_at: _u, ...rest } = source;
  return rest;
}

function cleanLocator(locator: Source["locator"]): Source["locator"] {
  const out: Source["locator"] = {};
  if (locator.url) out.url = locator.url;
  if (locator.telegram_username) out.telegram_username = locator.telegram_username;
  if (locator.telegram_channel_id) out.telegram_channel_id = locator.telegram_channel_id;
  return out;
}

export function SourcePage() {
  const { sourceId } = useParams();
  const isNew = !sourceId;
  const api = useApi();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const loaded = useQuery({
    queryKey: ["source", sourceId],
    enabled: !isNew,
    queryFn: () =>
      unwrapWithEtag(
        api.orchestrator.GET("/v1/sources/{source_id}", {
          params: { path: { source_id: sourceId as string } },
        }),
      ),
  });

  const [draft, setDraft] = useState<Source>(EMPTY_SOURCE);
  const [limitsText, setLimitsText] = useState("");
  const [connectionsText, setConnectionsText] = useState("");
  const [entityTypes, setEntityTypes] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const source = loaded.data?.data;
    if (!source) return;
    setDraft(source);
    setLimitsText(toJsonText(source.limits));
    setConnectionsText(toJsonText(source.connections));
    setEntityTypes((source.expected_entity_types ?? []).join(", "));
  }, [loaded.data]);

  const assembled = useMemo<{ source: Source | null; issues: string[] }>(() => {
    const limits = checkJson(limitsText, SCHEMAS.limits);
    const connections = checkJson(connectionsText);
    const issues: string[] = [];
    if (limits.parseError) issues.push(`limits: ${limits.parseError}`);
    if (connections.parseError) issues.push(`connections: ${connections.parseError}`);
    if (issues.length) return { source: null, issues };
    const types = entityTypes
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);
    const source: Source = {
      ...withoutReadOnly(draft),
      locator: cleanLocator(draft.locator),
      ...(limits.value !== undefined ? { limits: limits.value as NonNullable<Source["limits"]> } : {}),
      ...(connections.value !== undefined
        ? { connections: connections.value as Record<string, string> }
        : {}),
      ...(types.length ? { expected_entity_types: types } : {}),
    };
    if (limits.value === undefined) delete source.limits;
    if (connections.value === undefined) delete source.connections;
    if (!types.length) delete source.expected_entity_types;
    for (const issue of validateAgainst(SCHEMAS.source, source))
      issues.push(`${issue.pointer} ${issue.message}`);
    return { source, issues };
  }, [draft, limitsText, connectionsText, entityTypes]);

  const save = useMutation({
    mutationFn: async (source: Source) => {
      if (isNew) {
        return unwrapWithEtag(
          api.orchestrator.POST("/v1/sources", {
            params: { header: { "Idempotency-Key": newIdempotencyKey() } },
            body: source,
          }),
        );
      }
      return unwrapWithEtag(
        api.orchestrator.PUT("/v1/sources/{source_id}", {
          params: { path: { source_id: sourceId as string }, header: ifMatch(loaded.data?.etag) },
          body: source,
        }),
      );
    },
    onSuccess: (result) => {
      setSaved(true);
      void queryClient.invalidateQueries({ queryKey: ["sources"] });
      queryClient.setQueryData(["source", result.data.source_id], result);
      if (isNew) navigate(`/sources/${encodeURIComponent(result.data.source_id)}`, { replace: true });
    },
  });

  const remove = useMutation({
    mutationFn: () =>
      unwrap(
        api.orchestrator.DELETE("/v1/sources/{source_id}", {
          params: { path: { source_id: sourceId as string } },
        }),
      ),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["sources"] });
      navigate("/sources");
    },
  });

  const set = (patch: Partial<Source>) => {
    setSaved(false);
    setDraft((d) => ({ ...d, ...patch }));
  };

  if (!isNew && loaded.isLoading) return <Loading />;

  return (
    <Page
      title={isNew ? "Нове джерело" : `Джерело ${sourceId}`}
      actions={
        !isNew ? (
          <>
            <Link className="btn" to={`/tasks?source_id=${encodeURIComponent(sourceId)}`}>
              Завдання джерела
            </Link>
            <ReasonAction
              label="Видалити"
              confirmLabel="Видалити джерело"
              danger
              requireReason={false}
              onConfirm={() => remove.mutate()}
            />
          </>
        ) : null
      }
    >
      <ErrorBox error={loaded.error} />
      <ErrorBox error={remove.error} title="Не вдалося видалити" />
      <form
        className="form"
        onSubmit={(e) => {
          e.preventDefault();
          if (assembled.source && !assembled.issues.length) save.mutate(assembled.source);
        }}
      >
        <div className="grid-2">
          <Field label="Ідентифікатор (source_id)" hint="нижній регістр, цифри, . _ -">
            <input
              value={draft.source_id}
              disabled={!isNew}
              onChange={(e) => set({ source_id: e.target.value })}
              required
            />
          </Field>
          <Field label="Тип (kind)">
            <input
              list="source-kinds"
              value={draft.kind}
              onChange={(e) => set({ kind: e.target.value })}
              required
            />
            <datalist id="source-kinds">
              <option value="web" />
              <option value="telegram" />
            </datalist>
          </Field>
          <Field label="Назва">
            <input
              value={draft.title}
              onChange={(e) => set({ title: e.target.value })}
              required
              maxLength={200}
            />
          </Field>
          <Field label="Опис">
            <input
              value={draft.description ?? ""}
              onChange={(e) => set({ description: e.target.value })}
              maxLength={4000}
            />
          </Field>
          {draft.kind === "telegram" ? (
            <>
              <Field label="Telegram username">
                <input
                  value={draft.locator.telegram_username ?? ""}
                  onChange={(e) => set({ locator: { ...draft.locator, telegram_username: e.target.value } })}
                />
              </Field>
              <Field label="Telegram channel id">
                <input
                  value={draft.locator.telegram_channel_id ?? ""}
                  onChange={(e) =>
                    set({ locator: { ...draft.locator, telegram_channel_id: e.target.value } })
                  }
                />
              </Field>
            </>
          ) : (
            <Field label="URL">
              <input
                type="url"
                value={draft.locator.url ?? ""}
                onChange={(e) => set({ locator: { ...draft.locator, url: e.target.value } })}
              />
            </Field>
          )}
          <Field label="Очікувані типи даних" hint="через кому: product, price, event">
            <input value={entityTypes} onChange={(e) => (setSaved(false), setEntityTypes(e.target.value))} />
          </Field>
          <Field label="Версії від LLM (change_policy)">
            <select
              value={draft.change_policy?.llm_versions ?? "manual_approval"}
              onChange={(e) =>
                set({
                  change_policy: {
                    llm_versions: e.target.value as NonNullable<
                      NonNullable<Source["change_policy"]>["llm_versions"]
                    >,
                  },
                })
              }
            >
              <option value="manual_approval">ручне погодження</option>
              <option value="auto_after_checks">автоактивація після перевірок</option>
              <option value="forbidden">заборонено</option>
            </select>
          </Field>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={Boolean(draft.forward_unknown_to_llm)}
              onChange={(e) => set({ forward_unknown_to_llm: e.target.checked })}
            />
            Передавати в LLM невідомі сторінки
          </label>
        </div>
        <Section title="Правила колектора (стратегії обходу)">
          <div className="grid-2">
            <Field label="Пакет правил (package_id)">
              <input
                value={draft.collector_rules?.package_id ?? ""}
                onChange={(e) =>
                  set({
                    collector_rules: e.target.value
                      ? { package_id: e.target.value, version: draft.collector_rules?.version ?? "" }
                      : undefined,
                  } as Partial<Source>)
                }
              />
            </Field>
            <Field label="Версія">
              <input
                value={draft.collector_rules?.version ?? ""}
                onChange={(e) =>
                  set({
                    collector_rules: {
                      package_id: draft.collector_rules?.package_id ?? "",
                      version: e.target.value,
                    },
                  })
                }
              />
            </Field>
          </div>
          {draft.collector_rules?.package_id && draft.collector_rules.version ? (
            <StrategiesSummary rules={draft.collector_rules} />
          ) : (
            <p className="muted">
              Правила ще не прив'язано (їх готує асистент або створюється пакет collector-rules).
            </p>
          )}
        </Section>
        <div className="grid-2">
          <Section title="Ліміти рівня джерела">
            <JsonEditor
              text={limitsText}
              onChange={(t) => (setSaved(false), setLimitsText(t))}
              schema={SCHEMAS.limits}
              label="Ліміти джерела"
              minHeight="8rem"
            />
          </Section>
          <Section title="Підключення (логічне ім'я → connection_id)">
            <JsonEditor
              text={connectionsText}
              onChange={(t) => (setSaved(false), setConnectionsText(t))}
              label="Підключення джерела"
              minHeight="8rem"
            />
          </Section>
        </div>
        {assembled.issues.length ? (
          <ul className="error-inline" role="alert" aria-label="Помилки форми">
            {assembled.issues.map((i) => (
              <li key={i}>{i}</li>
            ))}
          </ul>
        ) : null}
        <ErrorBox error={save.error} title="Не вдалося зберегти" />
        {saved ? <Notice tone="ok">Збережено</Notice> : null}
        <button
          type="submit"
          className="btn btn-primary"
          disabled={save.isPending || !assembled.source || assembled.issues.length > 0}
        >
          {isNew ? "Створити джерело" : "Зберегти"}
        </button>
        {!isNew && loaded.data?.data.updated_at ? (
          <span className="muted"> Оновлено {formatDate(loaded.data.data.updated_at)}</span>
        ) : null}
      </form>
      {!isNew ? (
        <Section title="Ефективні ліміти джерела">
          <EffectiveLimitsView query={{ source_id: sourceId }} />
        </Section>
      ) : null}
    </Page>
  );
}
