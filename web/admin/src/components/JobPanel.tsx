import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { ReactNode } from "react";
import type { Client } from "openapi-fetch";
import { unwrap } from "../api/client";
import { TERMINAL_JOB_STATUSES, useJob } from "../api/hooks";
import type { Job, TestReport } from "../api/types";
import { formatDate } from "../lib/format";
import { ErrorBox, JsonView, Status, Table } from "./ui";

interface CancelPaths {
  "/v1/jobs/{job_id}/cancel": {
    parameters: { query?: never; header?: never; path?: never; cookie?: never };
    post: {
      parameters: { query?: never; header?: never; path: { job_id: string }; cookie?: never };
      requestBody?: { content: { "application/json": { reason?: string } } };
      responses: {
        200: { headers: { [name: string]: unknown }; content: { "application/json": Job } };
        202: { headers: { [name: string]: unknown }; content: { "application/json": Job } };
      };
    };
  };
}

/** State, progress, error and result of a long-running operation (202 + job_id) of any Jane service. */
export function JobPanel({
  service,
  client,
  jobId,
  title,
  renderResult,
  cancellable = true,
}: {
  service: string;
  client: unknown;
  jobId: string;
  title: string;
  renderResult?: (result: Record<string, unknown>) => ReactNode;
  cancellable?: boolean;
}) {
  const job = useJob(service, client as never, jobId);
  const queryClient = useQueryClient();
  const cancel = useMutation({
    mutationFn: () =>
      unwrap(
        (client as Client<CancelPaths>).POST("/v1/jobs/{job_id}/cancel", {
          params: { path: { job_id: jobId } },
          body: { reason: "cancelled from admin" },
        }),
      ),
    onSuccess: (data) => queryClient.setQueryData(["job", service, jobId], data),
  });
  const data = job.data;
  return (
    <div className="job-panel" aria-label={title} data-testid="job-panel">
      <div className="job-head">
        <strong>{title}</strong> <code>{jobId}</code>{" "}
        <Status value={data?.status ?? (job.isLoading ? "queued" : null)} />
        {cancellable && data && !TERMINAL_JOB_STATUSES.has(data.status) ? (
          <button
            type="button"
            className="btn btn-danger"
            onClick={() => cancel.mutate()}
            disabled={cancel.isPending}
          >
            Скасувати job
          </button>
        ) : null}
      </div>
      <ErrorBox error={job.error ?? cancel.error} />
      {data?.progress ? (
        <p className="muted">
          Прогрес: {data.progress.completed ?? 0}
          {data.progress.total ? ` / ${data.progress.total}` : ""} {data.progress.unit ?? ""}
          {data.progress.message ? ` — ${data.progress.message}` : ""}
        </p>
      ) : null}
      {data?.error ? (
        <ErrorBox
          error={new Error(`${data.error.title} (${data.error.code})`)}
          title="Job завершився з помилкою"
        />
      ) : null}
      {data?.error?.details ? <JsonView value={data.error.details} compact /> : null}
      {data?.finished_at ? <p className="muted">Завершено: {formatDate(data.finished_at)}</p> : null}
      {data?.result ? renderResult ? renderResult(data.result) : <JsonView value={data.result} /> : null}
    </div>
  );
}

export function TestReportView({ report }: { report: TestReport }) {
  return (
    <div className="test-report" aria-label="Звіт тестів">
      <p>
        <strong>
          {report.package.package_id}@{report.package.version}
        </strong>
        : пройдено <span className="badge badge-ok">{report.passed}</span>, не пройдено{" "}
        <span className={report.failed ? "badge badge-bad" : "badge badge-muted"}>{report.failed}</span>
      </p>
      <Table
        label="Тестові випадки"
        rows={report.cases}
        rowKey={(c) => c.name}
        columns={[
          { header: "Тест", cell: (c) => c.name },
          { header: "Результат", cell: (c) => <Status value={c.passed ? "passed" : "failed"} /> },
          { header: "Очікувано", cell: (c) => c.expected_status ?? "—" },
          { header: "Фактично", cell: (c) => c.actual_status ?? "—" },
          {
            header: "Відмінності",
            cell: (c) => (c.differences?.length ? <JsonView value={c.differences} compact /> : "—"),
          },
        ]}
      />
    </div>
  );
}
