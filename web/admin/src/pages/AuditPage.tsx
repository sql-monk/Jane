import { useState } from "react";
import { useApi } from "../app/context";
import { unwrap } from "../api/client";
import { useCursorList } from "../api/hooks";
import { ErrorBox, Field, JsonView, Loading, LoadMore, Page, Table } from "../components/ui";
import { formatDate } from "../lib/format";

type SubjectType = "source" | "task" | "stage" | "connection" | "limits" | "problem_group";
const SUBJECTS: SubjectType[] = ["source", "task", "stage", "connection", "limits", "problem_group"];

export function AuditPage() {
  const api = useApi();
  const [subjectType, setSubjectType] = useState<SubjectType | "">("");
  const [subjectId, setSubjectId] = useState("");
  const list = useCursorList(["audit", subjectType, subjectId], (cursor, limit) =>
    unwrap(
      api.orchestrator.GET("/v1/audit-events", {
        params: {
          query: {
            limit,
            ...(cursor ? { cursor } : {}),
            ...(subjectType ? { subject_type: subjectType } : {}),
            ...(subjectId ? { subject_id: subjectId } : {}),
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
                {s}
              </option>
            ))}
          </select>
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
        rows={list.items}
        rowKey={(e) => e.event_id}
        columns={[
          { header: "Коли", cell: (e) => formatDate(e.at) },
          { header: "Хто", cell: (e) => e.actor },
          { header: "Дія", cell: (e) => <code>{e.action}</code> },
          { header: "Об'єкт", cell: (e) => `${e.subject_type}: ${e.subject_id}` },
          { header: "Деталі", cell: (e) => (e.details ? <JsonView value={e.details} compact /> : "—") },
        ]}
      />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
    </Page>
  );
}
