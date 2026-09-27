import { useQuery } from "@tanstack/react-query";
import { useApi } from "../app/context";
import { unwrap } from "../api/client";
import { ErrorBox, Loading, Table } from "./ui";

/** Flattens nested limits into `group.field` rows. */
export function flattenLimits(value: unknown, prefix = ""): Array<[string, unknown]> {
  if (value === null || typeof value !== "object" || Array.isArray(value))
    return prefix ? [[prefix, value]] : [];
  const rows: Array<[string, unknown]> = [];
  for (const [key, item] of Object.entries(value as Record<string, unknown>)) {
    const path = prefix ? `${prefix}.${key}` : key;
    if (item !== null && typeof item === "object" && !Array.isArray(item) && key !== "budget") {
      rows.push(...flattenLimits(item, path));
    } else {
      rows.push([path, item]);
    }
  }
  return rows;
}

/** Effective limits with the level every value comes from (orchestrator GET /v1/limits/effective). */
export function EffectiveLimitsView({
  query,
}: {
  query: { source_id?: string; task_id?: string; stage_id?: string };
}) {
  const api = useApi();
  const effective = useQuery({
    queryKey: ["effective-limits", query],
    queryFn: () => unwrap(api.orchestrator.GET("/v1/limits/effective", { params: { query } })),
  });
  if (effective.isLoading) return <Loading />;
  if (effective.error) return <ErrorBox error={effective.error} />;
  const provenance = effective.data?.provenance ?? {};
  const rows = flattenLimits(effective.data?.limits ?? {});
  return (
    <Table
      label="Ефективні ліміти"
      rows={rows}
      rowKey={([k]) => k}
      columns={[
        { header: "Параметр", cell: ([k]) => <code>{k}</code> },
        { header: "Значення", cell: ([, v]) => (typeof v === "object" ? JSON.stringify(v) : String(v)) },
        { header: "Рівень", cell: ([k]) => provenance[k] ?? provenance[k.split(".")[0] ?? ""] ?? "—" },
      ]}
    />
  );
}
