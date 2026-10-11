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
import { useUnsavedChanges } from "../components/UnsavedChanges";
import { ChainPackagePicker } from "../components/ChainEditor";
import { schemaIssueLabel, type SchemaIssue } from "../lib/schema";
import "../chain-editor.css";

export function SourcesPage() {
  const api = useApi();
  const [search, setSearch] = useState("");
  const [kind, setKind] = useState("");
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
      <div className="filters">
        <Field label="Пошук у завантажених джерелах">
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Назва, адреса або ідентифікатор…"
          />
        </Field>
        <Field label="Тип джерела">
          <select value={kind} onChange={(event) => setKind(event.target.value)}>
            <option value="">Усі джерела</option>
            <option value="web">Вебсайти</option>
            <option value="telegram">Telegram</option>
          </select>
        </Field>
      </div>
      {list.isLoading ? <Loading /> : null}
      <ErrorBox error={list.error} />
      <div className="list-summary">
        <span>
          Завантажено <strong>{list.isLoading || list.error ? "—" : list.items.length}</strong>
          {list.hasMore ? "+" : ""}
        </span>
        <button className="btn btn-small" type="button" onClick={list.refetch}>
          Оновити список
        </button>
      </div>
      <Table
        label="Джерела"
        rows={list.items.filter(
          (source) =>
            (!kind || source.kind === kind) &&
            `${source.source_id} ${source.title} ${source.locator.url ?? ""} ${source.locator.telegram_username ?? ""} ${source.locator.telegram_channel_id ?? ""}`
              .toLocaleLowerCase("uk")
              .includes(search.toLocaleLowerCase("uk")),
        )}
        empty={
          list.error
            ? "Дані джерел недоступні. Спробуйте оновити список."
            : list.isLoading
              ? "Завантаження джерел…"
              : search || kind
                ? "Збігів у завантажених джерелах немає. Змініть фільтри або завантажте наступну сторінку."
                : "Джерел ще немає. Додайте сайт або канал самостійно чи через асистента."
        }
        rowKey={(s) => s.source_id}
        columns={[
          {
            header: "Джерело",
            cell: (s) => <Link to={`/sources/${encodeURIComponent(s.source_id)}`}>{s.source_id}</Link>,
          },
          { header: "Назва", cell: (s) => s.title },
          {
            header: "Тип",
            cell: (s) => (s.kind === "web" ? "Вебсайт" : s.kind === "telegram" ? "Telegram" : s.kind),
          },
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
          {
            header: "Дії",
            cell: (source) => (
              <Link className="btn btn-small" to={`/tasks?source_id=${encodeURIComponent(source.source_id)}`}>
                Завдання джерела
              </Link>
            ),
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
  const [modified, setDirty] = useState(false);
  const [baseline, setBaseline] = useState(JSON.stringify([EMPTY_SOURCE, "", "", ""]));
  const snapshot = JSON.stringify([withoutReadOnly(draft), limitsText, connectionsText, entityTypes]);
  const dirty = modified && snapshot !== baseline;
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    const source = loaded.data?.data;
    if (!source || dirty) return;
    setDraft(source);
    setLimitsText(toJsonText(source.limits));
    setConnectionsText(toJsonText(source.connections));
    setEntityTypes((source.expected_entity_types ?? []).join(", "));
    setBaseline(
      JSON.stringify([
        withoutReadOnly(source),
        toJsonText(source.limits),
        toJsonText(source.connections),
        (source.expected_entity_types ?? []).join(", "),
      ]),
    );
  }, [loaded.data, dirty]);

  const assembled = useMemo<{ source: Source | null; issues: string[]; fieldIssues: SchemaIssue[] }>(() => {
    const limits = checkJson(limitsText, SCHEMAS.limits);
    const connections = checkJson(connectionsText);
    const issues: string[] = [];
    if (limits.parseError) issues.push(`limits: ${limits.parseError}`);
    if (connections.parseError) issues.push(`connections: ${connections.parseError}`);
    if (issues.length) return { source: null, issues, fieldIssues: [] };
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
    const fieldIssues = validateAgainst(SCHEMAS.source, source);
    for (const issue of fieldIssues) issues.push(schemaIssueLabel(issue));
    return { source, issues, fieldIssues };
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
      guard.markSaved();
      setDirty(false);
      setSubmitted(false);
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
      guard.markSaved();
      void queryClient.invalidateQueries({ queryKey: ["sources"] });
      navigate("/sources");
    },
  });

  const set = (patch: Partial<Source>) => {
    setSaved(false);
    setDirty(true);
    setDraft((d) => ({ ...d, ...patch }));
  };

  const guard = useUnsavedChanges({
    dirty,
    label: draft.title || "Джерело",
    onDiscard: () => setDirty(false),
    onSave: async () => {
      setSubmitted(true);
      if (!assembled.source || assembled.issues.length) return false;
      await save.mutateAsync(assembled.source);
      return true;
    },
  });

  if (!isNew && loaded.isLoading) return <Loading />;

  const fieldError = (pointer: string) =>
    submitted ? assembled.fieldIssues.find((issue) => issue.pointer === pointer)?.message : undefined;

  return (
    <Page
      title={isNew ? "Нове джерело" : `Джерело ${sourceId}`}
      actions={
        !isNew ? (
          <>
            <Link className="btn" to={`/tasks?source_id=${encodeURIComponent(sourceId)}`}>
              Завдання джерела
            </Link>
            <Link className="btn" to="/results">
              Розібрані дані
            </Link>
            <ReasonAction
              label="Видалити"
              confirmLabel="Видалити джерело"
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
      <form
        className="form"
        noValidate
        onSubmit={(e) => {
          e.preventDefault();
          setSubmitted(true);
          if (assembled.source && !assembled.issues.length) save.mutate(assembled.source);
        }}
      >
        <fieldset className="form-fields" disabled={save.isPending}>
          <div className="grid-2">
            <Field
              label="Ідентифікатор (source_id)"
              hint="нижній регістр, цифри, . _ -"
              error={fieldError("/source_id")}
            >
              <input
                value={draft.source_id}
                disabled={!isNew}
                onChange={(e) => set({ source_id: e.target.value })}
                required
              />
            </Field>
            <Field label="Тип джерела">
              <select value={draft.kind} onChange={(e) => set({ kind: e.target.value })} required>
                <option value="web">Вебсайт</option>
                <option value="telegram">Telegram</option>
                {!["web", "telegram"].includes(draft.kind) ? (
                  <option value={draft.kind}>{draft.kind}</option>
                ) : null}
              </select>
            </Field>
            <Field label="Назва" error={fieldError("/title")}>
              <input
                value={draft.title}
                onChange={(e) => set({ title: e.target.value })}
                required
                maxLength={200}
              />
            </Field>
            <Field label="Опис">
              <textarea
                rows={3}
                value={draft.description ?? ""}
                onChange={(e) => set({ description: e.target.value })}
                maxLength={4000}
              />
            </Field>
            {draft.kind === "telegram" ? (
              <>
                <Field label="Telegram username" error={fieldError("/locator/telegram_username")}>
                  <input
                    value={draft.locator.telegram_username ?? ""}
                    onChange={(e) =>
                      set({ locator: { ...draft.locator, telegram_username: e.target.value } })
                    }
                  />
                </Field>
                <Field label="Telegram channel id" error={fieldError("/locator/telegram_channel_id")}>
                  <input
                    value={draft.locator.telegram_channel_id ?? ""}
                    onChange={(e) =>
                      set({ locator: { ...draft.locator, telegram_channel_id: e.target.value } })
                    }
                  />
                </Field>
              </>
            ) : (
              <Field label="URL" error={fieldError("/locator/url") ?? fieldError("/locator")}>
                <input
                  type="url"
                  value={draft.locator.url ?? ""}
                  onChange={(e) => set({ locator: { ...draft.locator, url: e.target.value } })}
                />
              </Field>
            )}
            <Field label="Очікувані типи даних" hint="через кому: product, price, event">
              <input
                value={entityTypes}
                onChange={(e) => (setSaved(false), setDirty(true), setEntityTypes(e.target.value))}
              />
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
            <ChainPackagePicker
              inherit={false}
              stage={{
                stage_id: "collect",
                kind: "collect",
                collector: {
                  collector: draft.kind,
                  ...(draft.collector_rules ? { rules: draft.collector_rules } : {}),
                },
              }}
              onChange={(stage) => set({ collector_rules: stage.collector?.rules } as Partial<Source>)}
            />
            {draft.collector_rules?.package_id && draft.collector_rules.version ? (
              <StrategiesSummary rules={draft.collector_rules} />
            ) : (
              <p className="muted">
                Правила ще не прив'язано (їх готує асистент або створюється пакет collector-rules).
              </p>
            )}
          </Section>
          <details className="form-advanced">
            <summary>Додатково: ліміти та підключення</summary>
            <div className="grid-2">
              <Section title="Ліміти рівня джерела">
                <JsonEditor
                  text={limitsText}
                  onChange={(t) => (setSaved(false), setDirty(true), setLimitsText(t))}
                  schema={SCHEMAS.limits}
                  label="Ліміти джерела"
                  minHeight="8rem"
                  readOnly={save.isPending}
                />
              </Section>
              <Section title="Підключення (логічне ім'я → connection_id)">
                <JsonEditor
                  text={connectionsText}
                  onChange={(t) => (setSaved(false), setDirty(true), setConnectionsText(t))}
                  label="Підключення джерела"
                  minHeight="8rem"
                  readOnly={save.isPending}
                />
              </Section>
            </div>
          </details>
          {submitted && assembled.issues.length ? (
            <ul className="error-inline" role="alert" aria-label="Помилки форми">
              {assembled.issues.map((i) => (
                <li key={i}>{i}</li>
              ))}
            </ul>
          ) : null}
          <ErrorBox error={save.error} title="Не вдалося зберегти" />
          {saved ? <Notice tone="ok">Збережено</Notice> : null}
          <div className="form-save-bar">
            {dirty ? (
              <span role="status">Є незбережені зміни</span>
            ) : (
              <span className="muted">{isNew ? "Нове джерело ще не записано" : "Змін немає"}</span>
            )}
            <button type="submit" className="btn btn-primary" disabled={save.isPending}>
              {isNew ? "Створити джерело" : "Зберегти"}
            </button>
          </div>
          {!isNew && loaded.data?.data.updated_at ? (
            <span className="muted"> Оновлено {formatDate(loaded.data.data.updated_at)}</span>
          ) : null}
        </fieldset>
      </form>
      {!isNew ? (
        <Section title="Ефективні ліміти джерела">
          <EffectiveLimitsView query={{ source_id: sourceId }} />
        </Section>
      ) : null}
    </Page>
  );
}
