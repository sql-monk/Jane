// Platform limits (defaults + hard caps) and effective limits with provenance (ТЗ §13.1.5, criterion 13).
import { useCallback, useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useApi } from "../app/context";
import { ifMatch, unwrapWithEtag } from "../api/client";
import type { PlatformLimits } from "../api/types";
import { EffectiveLimitsView } from "../components/EffectiveLimitsView";
import { JsonEditor, checkJson, toJsonText } from "../components/JsonEditor";
import { ErrorBox, Field, Loading, Notice, Page, Section } from "../components/ui";
import { SCHEMAS } from "../lib/schema";
import { useUnsavedChanges } from "../components/UnsavedChanges";
import {
  PropertyGrid,
  PropertyIssuesContext,
  PropertyDraftsBlockedContext,
} from "../components/PropertyGrid";
import type { JsonValue } from "../lib/property";
import { useSourceOptions, useTaskOptions } from "../lib/pickers";
import { LoadMore } from "../components/ui";
import { unwrap } from "../api/client";
import { PlatformLimitsForm } from "../components/PlatformLimitsForm";

export function LimitsPage() {
  const api = useApi();
  const queryClient = useQueryClient();
  const platform = useQuery({
    queryKey: ["platform-limits"],
    queryFn: () => unwrapWithEtag(api.orchestrator.GET("/v1/limits/platform")),
  });
  const [text, setText] = useState("");
  const [baseline, setBaseline] = useState("");
  const [propertyIssues, setPropertyIssues] = useState<Record<string, string>>({});
  const reportPropertyIssue = useCallback(
    (key: string, message: string) =>
      setPropertyIssues((previous) => {
        if ((previous[key] ?? "") === message) return previous;
        const next = { ...previous };
        if (message) next[key] = message;
        else delete next[key];
        return next;
      }),
    [],
  );
  useEffect(() => {
    if (platform.data && text === baseline) {
      const loaded = toJsonText(platform.data.data);
      setText(loaded);
      setBaseline(loaded);
    }
  }, [platform.data, text, baseline]);
  const check = checkJson(text, SCHEMAS.platformLimits);
  const save = useMutation({
    mutationFn: (limits: PlatformLimits) =>
      unwrapWithEtag(
        api.orchestrator.PUT("/v1/limits/platform", {
          params: { header: ifMatch(platform.data?.etag) },
          body: limits,
        }),
      ),
    onSuccess: (result) => {
      guard.markSaved();
      const saved = toJsonText(result.data);
      setText(saved);
      setBaseline(saved);
      queryClient.setQueryData(["platform-limits"], result);
    },
  });
  const guard = useUnsavedChanges({
    dirty: text !== baseline || Object.keys(propertyIssues).length > 0,
    label: "Ліміти платформи",
    onSave: async () => {
      if (!check.ok || !check.value || Object.keys(propertyIssues).length) return false;
      await save.mutateAsync(check.value as PlatformLimits);
      return true;
    },
  });
  const [ctx, setCtx] = useState({ source_id: "", task_id: "", stage_id: "" });
  const sources = useSourceOptions();
  const tasks = useTaskOptions(ctx.source_id || undefined);
  const task = useQuery({
    queryKey: ["task", "limits-picker", ctx.task_id],
    enabled: Boolean(ctx.task_id),
    queryFn: () =>
      unwrap(api.orchestrator.GET("/v1/tasks/{task_id}", { params: { path: { task_id: ctx.task_id } } })),
  });
  const [query, setQuery] = useState<{ source_id?: string; task_id?: string; stage_id?: string } | null>(
    null,
  );

  return (
    <Page title="Ліміти">
      <Notice>
        Ліміти не зашиті в код: платформа → джерело → завдання → етап, нижчий рівень перекриває вищий, жорсткі
        стелі (hard_caps) обмежують усі рівні. Нові запуски використовують нові значення.
      </Notice>
      <Section
        title={`Ліміти платформи${platform.data?.data.profile ? ` (профіль ${platform.data.data.profile})` : ""}`}
      >
        {platform.isLoading ? <Loading /> : null}
        <ErrorBox error={platform.error} />
        <fieldset className="form-fields" disabled={save.isPending || Object.keys(propertyIssues).length > 0}>
          <PlatformLimitsForm text={text} onChange={setText} />
        </fieldset>
        <details className="module-setting-group">
          <summary>Усі властивості лімітів</summary>
          {check.value && check.ok ? (
            <PropertyIssuesContext.Provider value={reportPropertyIssue}>
              <PropertyDraftsBlockedContext.Provider value={save.isPending}>
                <PropertyGrid
                  objectRoot
                  value={check.value as JsonValue}
                  onChange={(value) => setText(toJsonText(value))}
                  label="Ліміти платформи"
                />
              </PropertyDraftsBlockedContext.Provider>
            </PropertyIssuesContext.Provider>
          ) : null}
        </details>
        <details className="module-setting-group">
          <summary>Редагувати ліміти як JSON</summary>
          <JsonEditor
            text={text}
            onChange={setText}
            schema={SCHEMAS.platformLimits}
            label="Ліміти платформи"
            readOnly={save.isPending}
            minHeight="20rem"
          />
        </details>
        <div className="sticky-actions">
          <button
            type="button"
            className="btn btn-primary"
            disabled={!check.ok || !check.value || Object.keys(propertyIssues).length > 0 || save.isPending}
            onClick={() => save.mutate(check.value as PlatformLimits)}
          >
            Зберегти ліміти платформи
          </button>
        </div>
        <ErrorBox error={save.error} title="Ліміти не збережено" />
        {save.isSuccess ? <Notice tone="ok">Збережено</Notice> : null}
      </Section>
      <Section title="Ефективні ліміти для контексту">
        <div className="filters">
          <Field label="Джерело">
            <select
              value={ctx.source_id}
              onChange={(e) => {
                setCtx({ source_id: e.target.value, task_id: "", stage_id: "" });
                setQuery(null);
              }}
            >
              <option value="">Усі джерела</option>
              {sources.options.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label} · {option.value}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Завдання">
            <select
              value={ctx.task_id}
              onChange={(e) => {
                setCtx({ ...ctx, task_id: e.target.value, stage_id: "" });
                setQuery(null);
              }}
            >
              <option value="">Без завдання</option>
              {tasks.options.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label} · {option.value}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Етап">
            <select
              value={ctx.stage_id}
              disabled={!ctx.task_id || task.isLoading}
              onChange={(e) => {
                setCtx({ ...ctx, stage_id: e.target.value });
                setQuery(null);
              }}
            >
              <option value="">Усі етапи</option>
              {task.data?.stages.map((stage) => (
                <option key={stage.stage_id} value={stage.stage_id}>
                  {stage.stage_id}
                </option>
              ))}
            </select>
          </Field>
          <button
            type="button"
            className="btn"
            onClick={() =>
              setQuery(
                Object.fromEntries(Object.entries(ctx).filter(([, v]) => v)) as {
                  source_id?: string;
                  task_id?: string;
                  stage_id?: string;
                },
              )
            }
          >
            Показати
          </button>
        </div>
        <ErrorBox error={sources.error ?? tasks.error ?? task.error} title="Каталог контекстів" />
        <LoadMore
          hasMore={sources.hasMore || tasks.hasMore}
          loading={sources.loadingMore || tasks.loadingMore}
          onClick={() => {
            if (sources.hasMore) sources.loadMore();
            if (tasks.hasMore) tasks.loadMore();
          }}
        />
        {query ? <EffectiveLimitsView query={query} /> : null}
      </Section>
    </Page>
  );
}
