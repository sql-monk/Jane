import { Link } from "react-router-dom";
import type { ImprovementResult } from "../api/types";
import { formatMoney, refLabel } from "../lib/format";
import { TestReportView } from "./JobPanel";
import { KeyValue, Notice, Status } from "./ui";

/** Job.result of assistant startImprovement (assistant.v1 ImprovementResult). */
export function ImprovementResultView({ result }: { result: Record<string, unknown> }) {
  const r = result as unknown as ImprovementResult;
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
            r.version ? (
              <Link
                to={`/packages/${encodeURIComponent(r.version.package_id)}?version=${encodeURIComponent(r.version.version)}`}
              >
                {refLabel(r.version)}
              </Link>
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
