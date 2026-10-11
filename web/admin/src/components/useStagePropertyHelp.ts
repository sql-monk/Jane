import { useCallback } from "react";
import { useQueries, useQuery } from "@tanstack/react-query";
import { useApi } from "../app/context";
import { unwrap, type ApiClients } from "../api/client";
import { fetchPackageFile } from "../api/packages";
import type { PackageManifest, Stage } from "../api/types";
import { describeStageProperty, type PropertySchema } from "../lib/property-help";

type ConnectionRequirement = NonNullable<PackageManifest["required_connections"]>[number];

function packageVersionQuery(api: ApiClients, packageId: string, version: string) {
  return {
    queryKey: ["stage-package-version", packageId, version],
    enabled: Boolean(packageId && version),
    queryFn: () =>
      unwrap(
        api.registry.GET("/v1/packages/{package_id}/versions/{version}", {
          params: { path: { package_id: packageId, version } },
        }),
      ),
  };
}

export function connectionRequirementHelp(requirement: ConnectionRequirement): string {
  return `${requirement.name} (${requirement.kind})${requirement.purpose ? ` — ${requirement.purpose}` : ""}. ${requirement.optional ? "Необов’язкове підключення." : "Обов’язкове підключення."}`;
}

/** Validate all handler stages, including those not currently selected in the grid. */
export function useRequiredStageConnections(stages: Stage[]) {
  const api = useApi();
  const references = Array.from(
    new Map(
      stages
        .filter((stage) => stage.kind === "handler" && stage.handler?.package_id && stage.handler.version)
        .map((stage) => [`${stage.handler!.package_id}/${stage.handler!.version}`, stage.handler!] as const),
    ).values(),
  );
  const queries = useQueries({
    queries: references.map((reference) => packageVersionQuery(api, reference.package_id, reference.version)),
  });
  const details = new Map(
    references.map((reference, index) => [
      `${reference.package_id}/${reference.version}`,
      queries[index]?.data?.manifest,
    ]),
  );
  const issues = stages.flatMap((stage) => {
    if (stage.kind !== "handler" || !stage.handler) return [];
    const manifest = details.get(`${stage.handler.package_id}/${stage.handler.version}`);
    return (manifest?.required_connections ?? []).flatMap((requirement) => {
      const value = stage.connections?.[requirement.name];
      if (requirement.optional || (typeof value === "string" && value.trim())) return [];
      return [
        `Етап «${stage.title || stage.stage_id}»: задайте connections.${requirement.name}. ${connectionRequirementHelp(requirement)}`,
      ];
    });
  });
  return {
    issues,
    loading: queries.some((query) => query.isLoading),
    unavailable: queries.some((query) => query.isError || (query.isSuccess && !query.data?.manifest)),
  };
}

export function useStagePropertyHelp(stage: Stage) {
  const api = useApi();
  const reference = stage.kind === "handler" ? stage.handler : stage.collector?.rules;
  const packageId = reference?.package_id ?? "";
  const version = reference?.version ?? "";
  const detail = useQuery(packageVersionQuery(api, packageId, version));
  const path = detail.data?.manifest?.params_schema;
  const help = useQuery({
    queryKey: ["stage-property-help", packageId, version, path],
    enabled: Boolean(path),
    queryFn: async (): Promise<PropertySchema | null> => {
      if (!path) return null;
      const file = await fetchPackageFile(api, packageId, version, path);
      if (file.encoding !== "utf-8") throw new Error("Схема параметрів пакета не є текстом UTF-8.");
      const schema: unknown = JSON.parse(file.data);
      if (typeof schema === "boolean") return null;
      if (!schema || typeof schema !== "object" || Array.isArray(schema))
        throw new Error("Схема параметрів пакета має бути JSON-об'єктом.");
      return schema as PropertySchema;
    },
  });
  const describe = useCallback(
    (path: string, keys?: readonly (string | number)[]) => {
      const description = describeStageProperty(stage, path, help.data ?? undefined, keys);
      if (keys?.[0] !== "connections") return description;
      const requirements = detail.data?.manifest?.required_connections ?? [];
      const relevant =
        keys.length === 2 ? requirements.filter((requirement) => requirement.name === keys[1]) : requirements;
      const guidance = relevant.map(connectionRequirementHelp).join(" ");
      return [description, guidance].filter(Boolean).join(" ") || undefined;
    },
    [stage, help.data, detail.data],
  );
  return {
    describe,
    schema: help.data ?? undefined,
    requirements: detail.data?.manifest?.required_connections ?? [],
    manifestUnavailable: detail.isSuccess && !detail.data?.manifest,
    loading: detail.isLoading || help.isLoading,
    error: detail.error ?? help.error,
  };
}
