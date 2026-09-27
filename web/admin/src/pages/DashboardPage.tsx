import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useApi } from "../app/context";
import { unwrap } from "../api/client";
import { ErrorBox, Loading, Page, Section, Status, Table } from "../components/ui";
import { formatDate, formatMoney } from "../lib/format";

export function DashboardPage() {
  const api = useApi();
  const executors = useQuery({
    queryKey: ["executors"],
    queryFn: () => unwrap(api.orchestrator.GET("/v1/executors")),
  });
  const runs = useQuery({
    queryKey: ["runs", "recent"],
    queryFn: () => unwrap(api.orchestrator.GET("/v1/runs", { params: { query: { limit: 10 } } })),
  });
  const problems = useQuery({
    queryKey: ["problem-groups", "open"],
    queryFn: () =>
      unwrap(api.orchestrator.GET("/v1/problem-groups", { params: { query: { status: "open" } } })),
  });
  const usage = useQuery({
    queryKey: ["llm-usage", "dashboard"],
    queryFn: () => unwrap(api.llm.GET("/v1/usage", { params: { query: { group_by: "day" } } })),
  });

  return (
    <Page title="Огляд">
      <div className="grid-2">
        <Section title="Виконавці">
          {executors.isLoading ? <Loading /> : null}
          <ErrorBox error={executors.error} />
          <Table
            label="Виконавці"
            rows={executors.data?.items ?? []}
            rowKey={(e) => e.executor}
            columns={[
              { header: "Виконавець", cell: (e) => e.executor },
              { header: "Роль", cell: (e) => e.role },
              { header: "Стан", cell: (e) => <Status value={e.status} /> },
            ]}
          />
        </Section>
        <Section title="Витрати LLM">
          <ErrorBox error={usage.error} />
          {usage.data ? (
            <p>
              Разом: <strong data-testid="usage-total">{formatMoney(usage.data.totals?.cost)}</strong>,{" "}
              {usage.data.totals?.requests ?? 0} запитів
            </p>
          ) : null}
          <Link to="/llm">Деталі витрат і бюджети</Link>
        </Section>
      </div>
      <Section title="Останні запуски" actions={<Link to="/runs">Усі запуски</Link>}>
        <ErrorBox error={runs.error} />
        <Table
          label="Останні запуски"
          rows={runs.data?.items ?? []}
          rowKey={(r) => r.run_id}
          columns={[
            {
              header: "Запуск",
              cell: (r) => <Link to={`/runs/${encodeURIComponent(r.run_id)}`}>{r.run_id}</Link>,
            },
            {
              header: "Завдання",
              cell: (r) => <Link to={`/tasks/${encodeURIComponent(r.task_id)}`}>{r.task_id}</Link>,
            },
            { header: "Стан", cell: (r) => <Status value={r.status} /> },
            { header: "Тригер", cell: (r) => r.trigger },
            { header: "Створено", cell: (r) => formatDate(r.created_at) },
          ]}
        />
      </Section>
      <Section title="Відкриті групи проблем" actions={<Link to="/problems">Усі проблеми</Link>}>
        <ErrorBox error={problems.error} />
        <Table
          label="Відкриті групи проблем"
          rows={problems.data?.items ?? []}
          rowKey={(g) => g.group_id}
          columns={[
            { header: "Джерело", cell: (g) => g.source_id },
            { header: "Проблема", cell: (g) => <Status value={g.problem} /> },
            { header: "Сигнатура", cell: (g) => <code>{g.signature}</code> },
            { header: "Кількість", cell: (g) => g.count },
          ]}
        />
      </Section>
    </Page>
  );
}
