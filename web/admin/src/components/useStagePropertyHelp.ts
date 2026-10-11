import { useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { useApi } from "../app/context";
import { unwrap } from "../api/client";
import { fetchPackageFile } from "../api/packages";
import type { Stage } from "../api/types";
import { describeStageProperty, type PropertySchema } from "../lib/property-help";

export function useStagePropertyHelp(stage: Stage) {
  const api = useApi();
  const reference = stage.kind === "handler" ? stage.handler : stage.collector?.rules;
  const packageId = reference?.package_id ?? "";
  const version = reference?.version ?? "";
  const help = useQuery({
    queryKey: ["stage-property-help", packageId, version],
    enabled: Boolean(packageId && version),
    queryFn: async (): Promise<PropertySchema | null> => {
      const detail = await unwrap(
        api.registry.GET("/v1/packages/{package_id}/versions/{version}", {
          params: { path: { package_id: packageId, version } },
        }),
      );
      const path = detail.manifest?.params_schema;
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
    (path: string, keys?: readonly (string | number)[]) =>
      describeStageProperty(stage, path, help.data ?? undefined, keys),
    [stage, help.data],
  );
  return { describe, schema: help.data ?? undefined, loading: help.isLoading, error: help.error };
}
