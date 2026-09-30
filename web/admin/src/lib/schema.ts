// Client-side validation of configuration documents against the contract JSON Schemas (2020-12).
// Ajv compiles at build time: runtime compilation uses new Function, forbidden by the Caddy CSP.
// The service remains the authority (422 problem+json); this only gives early feedback in editors.
import type { ErrorObject, ValidateFunction } from "ajv";
import * as compiled from "../api/generated/validators.js";

/** A schema reference: `task-config.schema.json` or `common/limits.schema.json#/$defs/PlatformLimits`. */
export type SchemaRef = string;

export interface SchemaIssue {
  pointer: string;
  message: string;
}

function describe(error: ErrorObject): SchemaIssue {
  const params = error.params as Record<string, unknown>;
  let message = error.message ?? "invalid";
  if (error.keyword === "additionalProperties" || error.keyword === "unevaluatedProperties") {
    const extra = params["additionalProperty"] ?? params["unevaluatedProperty"];
    message = `невідоме поле «${String(extra)}»`;
  } else if (error.keyword === "required") {
    message = `обов'язкове поле «${String(params["missingProperty"])}»`;
  } else if (error.keyword === "enum") {
    message = `допустимі значення: ${JSON.stringify(params["allowedValues"])}`;
  }
  return { pointer: error.instancePath || "/", message };
}

export function validateAgainst(ref: SchemaRef, value: unknown): SchemaIssue[] {
  const validate = validators[ref];
  if (!validate) throw new Error(`unknown contract schema: ${ref}`);
  if (validate(value)) return [];
  const issues = (validate.errors ?? []).map(describe);
  // oneOf/anyOf branches produce noise: keep unique messages, most specific (deepest pointer) first.
  const seen = new Set<string>();
  return issues
    .sort((a, b) => b.pointer.length - a.pointer.length)
    .filter((issue) => {
      const key = `${issue.pointer} ${issue.message}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .slice(0, 20);
}

export const SCHEMAS = {
  source: "source.schema.json",
  task: "task-config.schema.json",
  schedule: "task-config.schema.json#/$defs/Schedule",
  stage: "task-config.schema.json#/$defs/Stage",
  collectorRules: "collector-rules.schema.json",
  strategy: "collector-rules.schema.json#/$defs/Strategy",
  limits: "common/limits.schema.json",
  platformLimits: "common/limits.schema.json#/$defs/PlatformLimits",
  connection: "common/connection.schema.json",
  manifest: "package-manifest.schema.json",
} as const;

const validators: Record<string, ValidateFunction> = {
  [SCHEMAS.source]: compiled.source,
  [SCHEMAS.task]: compiled.task,
  [SCHEMAS.schedule]: compiled.schedule,
  [SCHEMAS.stage]: compiled.stage,
  [SCHEMAS.collectorRules]: compiled.collectorRules,
  [SCHEMAS.strategy]: compiled.strategy,
  [SCHEMAS.limits]: compiled.limits,
  [SCHEMAS.platformLimits]: compiled.platformLimits,
  [SCHEMAS.connection]: compiled.connection,
  [SCHEMAS.manifest]: compiled.manifest,
};
