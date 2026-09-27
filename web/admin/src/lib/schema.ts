// Client-side validation of configuration documents against the contract JSON Schemas (2020-12).
// The service remains the authority (422 problem+json); this only gives early feedback in editors.
import Ajv2020, { type ErrorObject, type ValidateFunction } from "ajv/dist/2020";
import addFormats from "ajv-formats";
import { contractSchemas } from "../api/generated/schemas";

const BASE = "https://contracts.jane.invalid/schemas/";

let ajv: Ajv2020 | null = null;
const cache = new Map<string, ValidateFunction>();

function instance(): Ajv2020 {
  if (ajv) return ajv;
  // strict: false - the contracts use the OpenAPI `discriminator` annotation, which is not a JSON Schema keyword.
  const created = new Ajv2020({ strict: false, allErrors: true, validateFormats: true });
  addFormats(created);
  for (const [rel, schema] of Object.entries(contractSchemas)) {
    created.addSchema({ ...schema, $id: BASE + rel });
  }
  ajv = created;
  return created;
}

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
  let validate = cache.get(ref);
  if (!validate) {
    const [file, fragment] = ref.split("#");
    const id = BASE + file + (fragment ? `#${fragment}` : "");
    const found = instance().getSchema(id);
    if (!found) throw new Error(`unknown contract schema: ${ref}`);
    validate = found;
    cache.set(ref, validate);
  }
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
