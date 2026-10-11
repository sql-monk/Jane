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
  technical?: string;
}

function describe(error: ErrorObject): SchemaIssue {
  const params = error.params as Record<string, unknown>;
  let message = "Перевірте значення поля";
  if (error.keyword === "additionalProperties" || error.keyword === "unevaluatedProperties") {
    const extra = params["additionalProperty"] ?? params["unevaluatedProperty"];
    message = `невідоме поле «${String(extra)}»`;
  } else if (error.keyword === "required") {
    message = "Заповніть обов’язкове поле";
  } else if (error.keyword === "enum") {
    message = `допустимі значення: ${JSON.stringify(params["allowedValues"])}`;
  } else if (error.keyword === "type") {
    const types: Record<string, string> = {
      string: "текст",
      number: "число",
      integer: "ціле число",
      object: "об’єкт",
      array: "масив",
      boolean: "так / ні",
      null: "порожнє значення",
    };
    message = `Очікується ${types[String(params["type"])] ?? "значення потрібного типу"}`;
  } else if (error.keyword === "minLength") {
    message =
      Number(params["limit"]) === 1
        ? "Заповніть поле"
        : `Введіть щонайменше ${String(params["limit"])} символів`;
  } else if (error.keyword === "maxLength") {
    message = `Скоротіть до ${String(params["limit"])} символів`;
  } else if (error.keyword === "pattern") {
    message = error.instancePath.endsWith("_id")
      ? "Використовуйте малі латинські літери, цифри, крапку, дефіс або підкреслення; перший символ — літера або цифра"
      : error.instancePath.endsWith("/version")
        ? "Вкажіть номер версії у форматі 1.2.3"
        : "Значення не відповідає потрібному формату";
  } else if (error.keyword === "format") {
    message =
      params["format"] === "date-time"
        ? "Вкажіть дату, час і часовий пояс"
        : "Перевірте формат адреси або значення";
  } else if (error.keyword === "minimum" || error.keyword === "exclusiveMinimum") {
    message = `Значення має бути ${error.keyword === "minimum" ? "не менше" : "більше"} ${String(params["limit"])}`;
  } else if (error.keyword === "maximum" || error.keyword === "exclusiveMaximum") {
    message = `Значення має бути ${error.keyword === "maximum" ? "не більше" : "менше"} ${String(params["limit"])}`;
  } else if (error.keyword === "minProperties" || error.keyword === "minItems") {
    message = "Додайте щонайменше один елемент";
  } else if (error.keyword === "maxItems" || error.keyword === "maxProperties") {
    message = `Дозволено не більше ${String(params["limit"])} елементів`;
  } else if (error.keyword === "const") {
    message = `Очікується значення ${JSON.stringify(params["allowedValue"])}`;
  } else if (error.keyword === "uniqueItems") {
    message = "Приберіть повторювані елементи";
  } else if (["if", "oneOf", "anyOf"].includes(error.keyword)) {
    message = "Перевірте обов’язкові поля для вибраного типу";
  }
  const missing = error.keyword === "required" ? `/${String(params["missingProperty"])}` : "";
  return {
    pointer: `${error.instancePath}${missing}` || "/",
    message,
    technical: `${error.instancePath || "/"}: ${error.message ?? error.keyword}`,
  };
}

const FIELD_LABELS: Record<string, string> = {
  source_id: "Джерело",
  task_id: "Ідентифікатор завдання",
  title: "Назва",
  locator: "Адреса джерела",
  url: "URL",
  telegram_username: "Назва каналу Telegram",
  telegram_channel_id: "Ідентифікатор каналу Telegram",
  schedule: "Розклад",
  interval_seconds: "Інтервал у секундах",
  cron: "Розклад cron",
  at: "Час запуску",
  version: "Версія",
  package_id: "Пакет",
  stages: "Етапи",
  connections: "Підключення",
  limits: "Ліміти",
};
export function schemaIssueLabel(issue: SchemaIssue): string {
  const key = issue.pointer.split("/").filter(Boolean).at(-1) ?? "";
  return `${FIELD_LABELS[key] ?? (key ? `Поле «${key}»` : "Конфігурація")}: ${issue.message}`;
}

export function validateAgainst(ref: SchemaRef, value: unknown): SchemaIssue[] {
  const validate = validators[ref];
  if (!validate) throw new Error(`unknown contract schema: ${ref}`);
  if (validate(value)) return [];
  const errors = validate.errors ?? [];
  const specific = errors.filter((error) => !["if", "oneOf", "anyOf"].includes(error.keyword));
  const issues = (specific.length ? specific : errors).map(describe);
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
