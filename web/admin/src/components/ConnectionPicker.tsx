import { useQuery } from "@tanstack/react-query";
import { useApi, useConfig } from "../app/context";
import { unwrap } from "../api/client";
import { Field } from "./ui";

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
  const { page_size } = useConfig();
  const connections = useQuery({
    queryKey: ["connections", "picker", page_size],
    queryFn: () =>
      unwrap(api.orchestrator.GET("/v1/connections", { params: { query: { limit: page_size } } })),
  });
  const id = `conn-${label.replace(/\W+/g, "-")}`;
  return (
    <Field label={label}>
      <input list={id} value={value} onChange={(e) => onChange(e.target.value)} />
      <datalist id={id}>
        {(connections.data?.items ?? []).map((c) => (
          <option key={c.connection.connection_id} value={c.connection.connection_id}>
            {c.connection.kind}
          </option>
        ))}
      </datalist>
    </Field>
  );
}
