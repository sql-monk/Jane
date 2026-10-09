// Attempt diagnostics of a run item (orchestrator.v1 StageItem / MaterialTrace stage: `attempt_history`,
// `available_at`): when the item was claimed, why and until when a retry waited, how it ended.
import { safeProblemCode } from "../api/problem";
import type { AttemptEvent } from "../api/types";
import { formatInstant } from "../lib/format";
import { Status } from "./ui";

export function AttemptHistory({ history, label }: { history: AttemptEvent[] | undefined; label: string }) {
  if (!history?.length) return <span className="muted">—</span>;
  return (
    <details>
      <summary>{history.length} подій</summary>
      <ol className="attempt-history" aria-label={label}>
        {history.map((event, i) => (
          <li key={i}>
            <Status value={event.event} /> {formatInstant(event.at)}
            {event.attempt !== undefined ? `, спроба ${event.attempt}` : ""}
            {event.available_at ? `, доступний з ${formatInstant(event.available_at)}` : ""}
            {event.delay_ms !== undefined ? `, затримка ${event.delay_ms} мс` : ""}
            {event.code ? (
              <>
                , код <code>{safeProblemCode(event.code)}</code>
              </>
            ) : null}
          </li>
        ))}
      </ol>
    </details>
  );
}
