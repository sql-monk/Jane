import { useState } from "react";
import { Link } from "react-router-dom";
import { useApi } from "../app/context";
import { unwrap } from "../api/client";
import { useCursorList } from "../api/hooks";
import { ErrorBox, Field, JsonView, Loading, LoadMore, Page, Table } from "../components/ui";
import { formatDate, inputInstant, SCOPE_LABELS } from "../lib/format";
import { redactSecrets } from "../lib/secrets";

type SubjectType = "source" | "task" | "stage" | "connection" | "limits" | "problem_group";
const SUBJECTS: SubjectType[] = ["source", "task", "stage", "connection", "limits", "problem_group"];

export function AuditPage() {
  const api = useApi();
  const [subjectType, setSubjectType] = useState<SubjectType | "">("");
  const [subjectId, setSubjectId] = useState("");
  const [since, setSince] = useState("");
  const [until, setUntil] = useState("");
  const sinceInstant = inputInstant(since);
  const untilInstant = inputInstant(until);
  const timeframe = {
    ...(sinceInstant ? { since: sinceInstant } : {}),
    ...(untilInstant ? { until: untilInstant } : {}),
  };
  const list = useCursorList(["audit", subjectType, subjectId, timeframe], (cursor, limit) =>
    unwrap(
      api.orchestrator.GET("/v1/audit-events", {
        params: {
          query: {
            limit,
            ...(cursor ? { cursor } : {}),
            ...(subjectType ? { subject_type: subjectType } : {}),
            ...(subjectId ? { subject_id: subjectId } : {}),
            ...timeframe,
          },
        },
      }),
    ),
  );
  return (
    <Page title="Журнал аудиту">
      <p className="muted">Активації, відкати, зміни конфігурацій, підключень і лімітів (оркестратор).</p>
      <div className="filters">
        <Field label="Тип об'єкта">
          <select value={subjectType} onChange={(e) => setSubjectType(e.target.value as SubjectType | "")}>
            <option value="">усі</option>
            {SUBJECTS.map((s) => (
              <option key={s} value={s}>
                {SCOPE_LABELS[s]}
              </option>
            ))}
          </select>
        </Field>
        <Field label="З дати" hint="Часовий пояс вашого браузера.">
          <input type="datetime-local" value={since} onChange={(event) => setSince(event.target.value)} />
        </Field>
        <Field label="До дати (не включно)">
          <input
            type="datetime-local"
            value={until}
            min={since || undefined}
            onChange={(event) => setUntil(event.target.value)}
          />
        </Field>
        <Field label="Об'єкт">
          <input
            value={subjectId}
            onChange={(e) => setSubjectId(e.target.value)}
            placeholder="shop-catalog/extract-products"
          />
        </Field>
      </div>
      {list.isLoading ? <Loading /> : null}
      <ErrorBox error={list.error} />
      <Table
        label="Події аудиту"
        loading={list.isLoading}
        error={list.error}
        rows={list.items}
        rowKey={(e) => e.event_id}
        columns={[
          { header: "Коли", cell: (e) => formatDate(e.at) },
          { header: "Хто", cell: (e) => e.actor },
          { header: "Дія", cell: (e) => <span title={e.action}>{actionLabel(e.action)}</span> },
          {
            header: "Об'єкт",
            cell: (e) => {
              const target = subjectLink(e.subject_type, e.subject_id);
              const label = `${SCOPE_LABELS[e.subject_type] ?? e.subject_type}: ${e.subject_id}`;
              return target ? <Link to={target}>{label}</Link> : label;
            },
          },
          { header: "Зміни", cell: (e) => <AuditChanges details={e.details} /> },
        ]}
      />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
    </Page>
  );
}

function subjectLink(type: string, id: string): string | null {
  if (type === "source") return `/sources/${encodeURIComponent(id)}`;
  if (type === "task") return `/tasks/${encodeURIComponent(id)}`;
  if (type === "stage" && id.includes("/"))
    return `/tasks/${encodeURIComponent(id.split("/")[0] ?? "")}?tab=versions`;
  if (type === "connection") return `/connections?connection_id=${encodeURIComponent(id)}`;
  if (type === "limits") return "/limits";
  if (type === "problem_group") return `/problems?group_id=${encodeURIComponent(id)}`;
  return null;
}
function actionLabel(action: string): string {
  const verbs: Record<string, string> = {
    create: "Створено",
    created: "Створено",
    update: "Змінено",
    updated: "Змінено",
    delete: "Видалено",
    deleted: "Видалено",
    activate: "Активовано",
    activated: "Активовано",
    rollback: "Відкочено",
    set: "Задано",
    patch: "Оновлено",
    replay: "Повторено",
    reprocess: "Повторна обробка",
    resolve: "Вирішено",
    ignore: "Ігноровано",
  };
  const parts = action.split(/[.:]/);
  return parts.map((part) => verbs[part] ?? SCOPE_LABELS[part] ?? part).join(" · ");
}
function AuditChanges({ details }: { details: unknown }) {
  if (!details || typeof details !== "object") return <span className="muted">Деталей не записано</span>;
  const safe = redactSecrets(details) as Record<string, unknown>;
  const before = safe.before;
  const after = safe.after;
  return (
    <div>
      {before !== undefined || after !== undefined ? (
        <details>
          <summary>Переглянути: було → стало</summary>
          <div className="audit-diff">
            <div>
              <strong>Було</strong>
              <JsonView value={before ?? null} />
            </div>
            <div>
              <strong>Стало</strong>
              <JsonView value={after ?? null} />
            </div>
          </div>
        </details>
      ) : (
        <span className="muted">Історичну різницю не записано</span>
      )}
      <details>
        <summary>Технічні деталі</summary>
        <JsonView value={safe} compact />
      </details>
    </div>
  );
}
