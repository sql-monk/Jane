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
  return error instanceof ApiError ? "Запит не виконано" : "Операцію не виконано";
}

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
