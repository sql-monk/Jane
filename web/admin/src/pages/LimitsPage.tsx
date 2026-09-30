// Platform limits (defaults + hard caps) and effective limits with provenance (ТЗ §13.1.5, criterion 13).
import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useApi } from "../app/context";
import { ifMatch, unwrapWithEtag } from "../api/client";
import type { PlatformLimits } from "../api/types";
import { EffectiveLimitsView } from "../components/EffectiveLimitsView";
import { JsonEditor, checkJson, toJsonText } from "../components/JsonEditor";
import { ErrorBox, Field, Loading, Notice, Page, Section } from "../components/ui";
import { SCHEMAS } from "../lib/schema";

export function LimitsPage() {
  const api = useApi();
  const queryClient = useQueryClient();
  const platform = useQuery({
    queryKey: ["platform-limits"],
    queryFn: () => unwrapWithEtag(api.orchestrator.GET("/v1/limits/platform")),
  });
  const [text, setText] = useState("");
  useEffect(() => {
    if (platform.data) setText(toJsonText(platform.data.data));
  }, [platform.data]);
  const check = checkJson(text, SCHEMAS.platformLimits);
  const save = useMutation({
    mutationFn: (limits: PlatformLimits) =>
      unwrapWithEtag(
        api.orchestrator.PUT("/v1/limits/platform", {
          params: { header: ifMatch(platform.data?.etag) },
          body: limits,
        }),
      ),
    onSuccess: (result) => queryClient.setQueryData(["platform-limits"], result),
  });
  const [ctx, setCtx] = useState({ source_id: "", task_id: "", stage_id: "" });
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
        <JsonEditor
          text={text}
          onChange={setText}
          schema={SCHEMAS.platformLimits}
          label="Ліміти платформи"
          minHeight="20rem"
        />
        <button
          type="button"
          className="btn btn-primary"
          disabled={!check.ok || !check.value || save.isPending}
          onClick={() => save.mutate(check.value as PlatformLimits)}
        >
          Зберегти ліміти платформи
        </button>
        <ErrorBox error={save.error} title="Ліміти не збережено" />
        {save.isSuccess ? <Notice tone="ok">Збережено</Notice> : null}
      </Section>
      <Section title="Ефективні ліміти для контексту">
        <div className="filters">
          <Field label="Джерело">
            <input value={ctx.source_id} onChange={(e) => setCtx({ ...ctx, source_id: e.target.value })} />
          </Field>
          <Field label="Завдання">
            <input value={ctx.task_id} onChange={(e) => setCtx({ ...ctx, task_id: e.target.value })} />
          </Field>
          <Field label="Етап">
            <input value={ctx.stage_id} onChange={(e) => setCtx({ ...ctx, stage_id: e.target.value })} />
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
        {query ? <EffectiveLimitsView query={query} /> : null}
      </Section>
    </Page>
  );
}
