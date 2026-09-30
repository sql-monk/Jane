// Typed API clients generated from contracts (openapi-fetch over src/api/generated/*).
import createClient, { type Client, type Middleware } from "openapi-fetch";
import type { AdminConfig } from "../config";
import { absoluteUrl, serviceBaseUrl } from "../config";
import type { paths as OrchestratorPaths } from "./generated/orchestrator";
import type { paths as RegistryPaths } from "./generated/registry";
import type { paths as StoragePaths } from "./generated/storage";
import type { paths as LlmPaths } from "./generated/llm";
import type { paths as HandlerPaths } from "./generated/handler";
import type { paths as AssistantPaths } from "./generated/assistant";
import type { paths as CollectorPaths } from "./generated/collector";
import { ApiError, toProblem } from "./problem";

export interface ApiClients {
  orchestrator: Client<OrchestratorPaths>;
  registry: Client<RegistryPaths>;
  storage: Client<StoragePaths>;
  llm: Client<LlmPaths>;
  handler: Client<HandlerPaths>;
  assistant: Client<AssistantPaths>;
  collector: Client<CollectorPaths>;
  /** handler.v1 connection endpoints of a named executor (`/api/<executor>`), from GET /v1/executors. */
  executor: (name: string) => Client<HandlerPaths>;
  /** collector.v1 of a named collector executor. */
  collectorExecutor: (name: string) => Client<CollectorPaths>;
}

export interface AuthHooks {
  /** Bearer token of the current user (API key in dev, OIDC access token in prod) or null. */
  getToken: () => string | null;
  onUnauthenticated: () => void;
}

function authMiddleware(hooks: AuthHooks): Middleware {
  return {
    onRequest({ request }) {
      const token = hooks.getToken();
      if (token) request.headers.set("Authorization", `Bearer ${token}`);
      return request;
    },
    onResponse({ response }) {
      if (response.status === 401) hooks.onUnauthenticated();
      return response;
    },
  };
}

const EXECUTOR_NAME = /^[a-z0-9][a-z0-9._-]{0,98}$/;

export function createApiClients(config: AdminConfig, hooks: AuthHooks): ApiClients {
  const middleware = authMiddleware(hooks);
  function make<P extends object>(baseUrl: string): Client<P> {
    const client = createClient<P>({ baseUrl: absoluteUrl(baseUrl) });
    client.use(middleware);
    return client;
  }
  const executors = new Map<string, Client<HandlerPaths>>();
  const collectors = new Map<string, Client<CollectorPaths>>();
  function named<P extends object>(cache: Map<string, Client<P>>, name: string): Client<P> {
    if (!EXECUTOR_NAME.test(name)) throw new Error(`invalid executor name: ${name}`);
    let client = cache.get(name);
    if (!client) {
      client = make<P>(serviceBaseUrl(config, { executor: name }));
      cache.set(name, client);
    }
    return client;
  }
  return {
    orchestrator: make<OrchestratorPaths>(serviceBaseUrl(config, "orchestrator")),
    registry: make<RegistryPaths>(serviceBaseUrl(config, "registry")),
    storage: make<StoragePaths>(serviceBaseUrl(config, "storage")),
    llm: make<LlmPaths>(serviceBaseUrl(config, "llm")),
    handler: make<HandlerPaths>(serviceBaseUrl(config, "handler")),
    assistant: make<AssistantPaths>(serviceBaseUrl(config, "assistant")),
    collector: make<CollectorPaths>(serviceBaseUrl(config, "collector")),
    executor: (name) => named(executors, name),
    collectorExecutor: (name) => named(collectors, name),
  };
}

interface FetchResult<T> {
  data?: T;
  error?: unknown;
  response: Response;
}

async function settle<T>(promise: Promise<FetchResult<T>>): Promise<FetchResult<T>> {
  try {
    return await promise;
  } catch (cause) {
    throw new ApiError(502, {
      type: "urn:jane:problem:upstream_unavailable",
      title: "Service is unreachable",
      status: 502,
      code: "upstream_unavailable",
      detail: cause instanceof Error ? cause.message : String(cause),
      retryable: true,
    });
  }
}

/** Resolves to the response body or throws ApiError with the problem+json of the service. */
export async function unwrap<T>(promise: Promise<FetchResult<T>>): Promise<T> {
  const result = await settle(promise);
  if (result.error !== undefined || !result.response.ok) {
    throw new ApiError(
      result.response.status,
      toProblem(result.response.status, result.error, result.response.statusText),
    );
  }
  return result.data as T;
}

/** Same as unwrap, plus the ETag for a later PUT/PATCH with If-Match. */
export async function unwrapWithEtag<T>(
  promise: Promise<FetchResult<T>>,
): Promise<{ data: T; etag: string | null }> {
  const result = await settle(promise);
  if (result.error !== undefined || !result.response.ok) {
    throw new ApiError(
      result.response.status,
      toProblem(result.response.status, result.error, result.response.statusText),
    );
  }
  return { data: result.data as T, etag: result.response.headers.get("ETag") };
}

/** A fresh Idempotency-Key for one user action (retries of that action reuse it). */
export function newIdempotencyKey(): string {
  return crypto.randomUUID();
}

/** `If-Match` header object, only when the ETag is known. */
export function ifMatch(etag: string | null | undefined): { "If-Match"?: string } {
  return etag ? { "If-Match": etag } : {};
}
