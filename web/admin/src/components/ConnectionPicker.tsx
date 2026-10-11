import { useId } from "react";
import { useApi } from "../app/context";
import { useCursorList } from "../api/hooks";
import { unwrap } from "../api/client";
import { ErrorBox, Field, Loading, LoadMore } from "./ui";

/** Picks a platform connection (orchestrator registry) by id; free text is allowed as well. */
export function ConnectionPicker({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  const api = useApi();
  const connections = useCursorList(["connections", "picker"], (cursor, limit) =>
    unwrap(
      api.orchestrator.GET("/v1/connections", {
        params: { query: { limit, ...(cursor ? { cursor } : {}) } },
      }),
    ),
  );
  const id = useId();
  return (
    <div>
      <Field label={label} hint="Виберіть підключення за назвою або введіть його ідентифікатор.">
        <input list={id} value={value} onChange={(e) => onChange(e.target.value)} />
        <datalist id={id}>
          {connections.items.map((c) => (
            <option key={c.connection.connection_id} value={c.connection.connection_id}>
              {c.connection.title || c.connection.connection_id} · {c.connection.kind}
            </option>
          ))}
        </datalist>
      </Field>
      {connections.isLoading ? <Loading what="Підключення" /> : null}
      <ErrorBox error={connections.error} />
      <LoadMore
        hasMore={connections.hasMore}
        loading={connections.loadingMore}
        onClick={connections.loadMore}
      />
    </div>
  );
}
