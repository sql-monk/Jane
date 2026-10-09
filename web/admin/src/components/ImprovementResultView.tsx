import { Link } from "react-router-dom";
import type { ImprovementProposal, ImprovementResult } from "../api/types";
import { formatBytes, formatMoney, refLabel } from "../lib/format";
import { TestReportView } from "./JobPanel";
import { UnifiedDiff } from "./UnifiedDiff";
import { JsonView, KeyValue, Notice, Status, Table } from "./ui";

/** Job.result of assistant startImprovement (assistant.v1 ImprovementResult). */
export function ImprovementResultView({ result }: { result: Record<string, unknown> }) {
  const r = result as unknown as ImprovementResult;
  // proposal_only: `version` is the proposed number, nothing is published - no link to the registry.
  const published = r.version && r.outcome !== "proposal_only";
  return (
    <div aria-label="Результат вдосконалення">
      <KeyValue
        rows={[
          [
            "Підсумок",
            <Status
              value={
                r.outcome === "unresolved"
                  ? "unresolved"
                  : r.outcome === "proposal_only"
                    ? "draft"
                    : "succeeded"
              }
            />,
          ],
          ["Тип", r.outcome],
          [
            "Версія",
            published && r.version ? (
              <Link
                to={`/packages/${encodeURIComponent(r.version.package_id)}?version=${encodeURIComponent(r.version.version)}`}
              >
                {refLabel(r.version)}
              </Link>
            ) : r.version ? (
              `${refLabel(r.version)} (не опубліковано)`
            ) : (
              "—"
            ),
          ],
          ["Спроб", String(r.attempts ?? "—")],
          ["Активовано", r.activated ? "так" : "ні (потрібна активація людиною або політикою)"],
          ["Витрати LLM", formatMoney(r.costs)],
        ]}
      />
      {r.unresolved_reason ? <Notice tone="warn">Не вирішено: {r.unresolved_reason}</Notice> : null}
      {r.suggested_entity_types?.length ? (
        <Notice>
          Асистент пропонує розширити очікувані типи даних джерела:{" "}
          <strong>{r.suggested_entity_types.join(", ")}</strong> (приймає користувач у налаштуваннях джерела).
        </Notice>
      ) : null}
      {r.proposal ? <ProposalView proposal={r.proposal} /> : null}
      {(r.test_reports ?? []).map((t, i) =>
        t.report ? (
          <div key={i}>
            <p className="muted">{t.context ?? ""}</p>
            <TestReportView report={t.report} />
          </div>
        ) : null,
      )}
    </div>
  );
}

/** Size of a file of the proposal in bytes (UTF-8 text or base64 data). */
function fileBytes(file: ImprovementProposal["files"][string]): number {
  if (file.encoding === "base64") {
    const padding = file.data.endsWith("==") ? 2 : file.data.endsWith("=") ? 1 : 0;
    return Math.max(0, Math.floor((file.data.length * 3) / 4) - padding);
  }
  return new TextEncoder().encode(file.data).length;
}

/**
 * `ImprovementResult.proposal` (outcome `proposal_only`): the package forbids automatic changes, the candidate passed
 * its tests but is not published. The user reviews the changed files, the manifest and the diff, and publishes the
 * version himself (registry publishPackageVersion with `based_on` + `files`). File contents are data: shown as text.
 */
export function ProposalView({ proposal }: { proposal: ImprovementProposal }) {
  const files = Object.entries(proposal.files ?? {}).sort(([a], [b]) => a.localeCompare(b));
  return (
    <div className="card" aria-label="Пропозиція асистента">
      <Notice tone="warn">
        Пакет заборонено змінювати автоматично: версію {proposal.version} не опубліковано. Перегляньте зміни
        й, якщо згодні, опублікуйте її в репозиторії вручну.
      </Notice>
      <KeyValue
        rows={[
          [
            "На основі",
            <Link
              to={`/packages/${encodeURIComponent(proposal.based_on.package_id)}?version=${encodeURIComponent(proposal.based_on.version)}`}
            >
              {refLabel(proposal.based_on)}
            </Link>,
          ],
          ["Запропонована версія", proposal.version],
          ["Зміна схеми", proposal.schema_change ?? "—"],
          ["Опис змін", proposal.change_summary ?? "—"],
        ]}
      />
      <Table
        label="Змінені файли пропозиції"
        rows={files}
        rowKey={([path]) => path}
        empty="Змінених файлів немає"
        columns={[
          { header: "Файл", cell: ([path]) => <code>{path}</code> },
          { header: "Кодування", cell: ([, file]) => file.encoding },
          { header: "Розмір", cell: ([, file]) => formatBytes(fileBytes(file)) },
          {
            header: "Вміст",
            cell: ([path, file]) =>
              file.encoding === "utf-8" ? (
                <details>
                  <summary>показати</summary>
                  <pre className="content-preview" aria-label={`Вміст ${path}`}>
                    {file.data}
                  </pre>
                </details>
              ) : (
                <span className="muted">двійковий файл</span>
              ),
          },
        ]}
      />
      {proposal.omitted_files?.length ? (
        <Notice>
          Не вмістилися в межу пропозиції (improvement.max_proposal_bytes):{" "}
          {proposal.omitted_files.map((f) => (
            <code key={f}>{f} </code>
          ))}
        </Notice>
      ) : null}
      {proposal.diff ? (
        <>
          <h4>Diff коду й схем</h4>
          <UnifiedDiff diff={proposal.diff} label="Diff пропозиції" />
        </>
      ) : null}
      <details>
        <summary>Маніфест запропонованої версії</summary>
        <JsonView value={proposal.manifest} />
      </details>
    </div>
  );
}
