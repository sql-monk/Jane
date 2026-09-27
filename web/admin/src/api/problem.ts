// application/problem+json (contracts/schemas/common/problem.schema.json). Decisions are made by `code`.
import type { components } from "./generated/orchestrator";

type ProblemShape = components["responses"]["NotFound"]["content"]["application/problem+json"];
export type Problem = ProblemShape;

export class ApiError extends Error {
  readonly status: number;
  readonly problem: Problem;

  constructor(status: number, problem: Problem) {
    super(problem.detail ? `${problem.title}: ${problem.detail}` : problem.title);
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
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return String(error);
}
