// Improvement runs of the source assistant (assistant.v1 listImprovementRuns): jobs `kind = improvement`, newest
// first, so the admin restores them after a reload instead of keeping job ids in the browser.
import { Link } from "react-router-dom";
import { useApi } from "../app/context";
import { unwrap } from "../api/client";
import { useCursorList } from "../api/hooks";
import type { ImprovementResult, ImprovementRun, JobStatus } from "../api/types";
import { formatDate, refLabel } from "../lib/format";
import { ErrorBox, Loading, LoadMore, Status, Table } from "./ui";

export interface ImprovementRunFilter {
  package_id?: string;
  source_id?: string;
  problem_group_id?: string;
  status?: JobStatus;
}

/** Outcome of a finished run (`Job.result` = ImprovementResult), tolerant of unknown shapes. */
function outcomeOf(run: ImprovementRun): ImprovementResult | null {
  const result = run.result as Partial<ImprovementResult> | undefined;
  return result && typeof result.outcome === "string" ? (result as ImprovementResult) : null;
}

export function ImprovementRunList({
  filter,
  label,
  selected,
  onOpen,
}: {
  filter: ImprovementRunFilter;
  label: string;
  selected?: string | null;
  onOpen: (jobId: string) => void;
}) {
  const api = useApi();
  const list = useCursorList(["improvement-runs", filter], (cursor, limit) =>
    unwrap(
      api.assistant.GET("/v1/improvement-runs", {
        params: {
          query: {
            limit,
            ...(cursor ? { cursor } : {}),
            ...(filter.package_id ? { package_id: filter.package_id } : {}),
            ...(filter.source_id ? { source_id: filter.source_id } : {}),
            ...(filter.problem_group_id ? { problem_group_id: filter.problem_group_id } : {}),
            ...(filter.status ? { status: [filter.status] } : {}),
          },
        },
      }),
    ),
  );
  return (
    <>
      {list.isLoading ? <Loading /> : null}
      <ErrorBox error={list.error} />
      <Table
        label={label}
        rows={list.items}
        rowKey={(run) => run.job_id}
        empty="Запусків ще не було"
        columns={[
          {
            header: "Job",
            cell: (run) => (
              <button
                type="button"
                className={run.job_id === selected ? "link link-active" : "link"}
                onClick={() => onOpen(run.job_id)}
              >
                {run.job_id}
              </button>
            ),
          },
          { header: "Стан", cell: (run) => <Status value={run.status} /> },
          {
            header: "Пакет",
            cell: (run) =>
              run.labels?.["package_id"] ? (
                <Link to={`/packages/${encodeURIComponent(run.labels["package_id"])}`}>
                  {run.labels["package_id"]}
                </Link>
              ) : (
                "—"
              ),
          },
          { header: "Джерело", cell: (run) => run.labels?.["source_id"] ?? "—" },
          { header: "Група проблем", cell: (run) => run.labels?.["problem_group_id"] ?? "—" },
          { header: "Підсумок", cell: (run) => outcomeOf(run)?.outcome ?? "—" },
          {
            header: "Версія",
            cell: (run) => {
              const result = outcomeOf(run);
              if (result?.outcome === "proposal_only")
                return `${result.proposal?.version ?? result.version?.version ?? "?"} (не опубліковано)`;
              return refLabel(result?.version);
            },
          },
          { header: "Створено", cell: (run) => formatDate(run.created_at) },
          { header: "Завершено", cell: (run) => formatDate(run.finished_at) },
        ]}
      />
      <LoadMore hasMore={list.hasMore} loading={list.loadingMore} onClick={list.loadMore} />
    </>
  );
}
