// application/problem+json (contracts/schemas/common/problem.schema.json). Decisions are made by `code`.
import type { components } from "./generated/orchestrator";

type ProblemShape = components["responses"]["NotFound"]["content"]["application/problem+json"];
export type Problem = ProblemShape;

export class ApiError extends Error {
  readonly status: number;
  readonly problem: Problem;

  constructor(status: number, problem: Problem) {
    // A service may accidentally include credentials in title/detail. Keep the raw Problem for
    // code-based decisions, but never put untrusted prose into Error.message (or the UI).
    super("Запит не виконано");
    this.name = "ApiError";
    this.status = status;
    this.problem = problem;
  }

  get code(): string {
    return this.problem.code;
  }
}

function isProblem(value: unknown): value is Problem {
  return (
    typeof value === "object" &&
    value !== null &&
    typeof (value as Record<string, unknown>)["code"] === "string" &&
    typeof (value as Record<string, unknown>)["title"] === "string"
  );
}

/** Normalises any error body into a Problem (services may be absent or return non-JSON errors). */
export function toProblem(status: number, body: unknown, statusText = ""): Problem {
  if (isProblem(body)) return { ...body, status: typeof body.status === "number" ? body.status : status };
  const code =
    status === 401
      ? "unauthenticated"
      : status === 403
        ? "forbidden"
        : status === 404
          ? "not_found"
          : status >= 500
            ? "upstream_unavailable"
            : "bad_request";
  return {
    type: `urn:jane:problem:${code}`,
    title: statusText || `HTTP ${status}`,
    status: status >= 400 && status <= 599 ? status : 502,
    code,
    ...(typeof body === "string" && body ? { detail: body.slice(0, 500) } : {}),
  };
}

export function errorMessage(error: unknown): string {
  const problem = problemFrom(error);
  return problem
    ? (PROBLEM_MESSAGES[safeProblemCode(problem.code)] ??
        "Операцію не виконано. Оновіть дані й спробуйте ще раз.")
    : "Операцію не виконано. Перевірте доступність сервісу й повторіть дію.";
}

export function problemFrom(error: unknown): Problem | null {
  return error instanceof ApiError ? error.problem : isProblem(error) ? error : null;
}

const PROBLEM_MESSAGES: Record<string, string> = {
  validation_failed: "Перевірка параметрів не пройдена. Виправте поля форми перед збереженням.",
  bad_request: "Некоректні параметри запиту. Перевірте налаштування.",
  unauthenticated: "Сесія завершилася. Увійдіть знову.",
  forbidden: "Недостатньо прав для цієї дії.",
  not_found: "Об'єкт не знайдено. Оновіть список і перевірте вибраний об'єкт.",
  conflict: "Об'єкт уже змінено або дія конфліктує з поточним станом. Оновіть дані.",
  precondition_failed: "Дані змінилися після відкриття форми. Збережіть чернетку та оновіть об'єкт.",
  precondition_required: "Для збереження потрібна актуальна версія об'єкта. Відкрийте його знову.",
  version_exists: "Така версія вже існує. Виберіть новий номер версії.",
  source_unavailable: "Джерело недоступне. Перевірте адресу, доступ і налаштування збору.",
  upstream_unavailable: "Залежний сервіс недоступний. Перевірте його стан і повторіть дію.",
  service_unavailable: "Сервіс тимчасово недоступний. Повторіть дію після відновлення.",
  timeout: "Час очікування вичерпано. Перевірте прогрес операції перед повтором.",
  not_implemented: "Цей виконавець не підтримує операцію.",
  budget_exhausted: "Бюджет вичерпано. Перевірте бюджет потрібного рівня.",
  limit_exceeded: "Перевищено ліміт. Перевірте ефективні ліміти для цього завдання.",
  rate_limited: "Досягнуто частоту запитів. Дочекайтеся наступної дозволеної спроби.",
  secret_detected: "Виявлено секрет у налаштуваннях. Використайте посилання на секрет у підключенні.",
  access_denied_by_policy: "Політика доступу забороняє дію. Перевірте дозволи та адресу джерела.",
  schema_mismatch: "Дані не відповідають схемі. Перевірте властивості етапу та версію пакета.",
  digest_mismatch: "Контрольна сума пакета не збігається. Повторно завантажте перевірену версію.",
};

// Only codes from contracts/schemas/common/problem.schema.json are safe to show. A syntactically
// valid but unknown code may still contain a credential, so it must not be reflected into the DOM.
const KNOWN_CODES = new Set([
  "bad_request",
  "validation_failed",
  "unauthenticated",
  "forbidden",
  "not_found",
  "method_not_allowed",
  "conflict",
  "version_exists",
  "precondition_failed",
  "precondition_required",
  "idempotency_key_reused",
  "idempotency_in_progress",
  "payload_too_large",
  "unsupported_media_type",
  "limit_exceeded",
  "rate_limited",
  "budget_exhausted",
  "job_not_cancellable",
  "secret_detected",
  "dependency_not_allowed",
  "digest_mismatch",
  "schema_mismatch",
  "out_of_scope",
  "access_denied_by_policy",
  "upstream_conflict",
  "source_unavailable",
  "upstream_unavailable",
  "internal_error",
  "not_implemented",
  "service_unavailable",
  "timeout",
]);

export function safeProblemCode(value: unknown): string {
  return typeof value === "string" && KNOWN_CODES.has(value) ? value : "unknown_error";
}
