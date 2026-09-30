// Runtime configuration of the admin (public/config.json, replaceable per deployment without a rebuild).
// Everything tunable lives here with safe defaults; nothing about limits is hard-coded in screens.

export type ServiceKey =
  "orchestrator" | "registry" | "storage" | "llm" | "handler" | "assistant" | "collector";

export type AuthConfig =
  | { mode: "api_key" }
  | { mode: "none" }
  | {
      mode: "oidc";
      authority: string;
      client_id: string;
      scope: string;
      redirect_path: string;
      post_logout_redirect_path: string;
    };

export interface PollingConfig {
  /** First delay between job polls, ms. */
  initial_ms: number;
  /** Upper bound of the backoff, ms. */
  max_ms: number;
  /** Backoff multiplier (>= 1). */
  multiplier: number;
}

export interface AdminConfig {
  /** Prefix of the reverse proxy: `<api_base>/<service>/v1/...` (ADR-0005). May be absolute (https://jane.example/api). */
  api_base: string;
  /** Reverse-proxy service name for every contract. */
  services: Record<ServiceKey, string>;
  auth: AuthConfig;
  polling: PollingConfig;
  /** Default `limit` of list requests (the service clamps it to its own maximum). */
  page_size: number;
  /** How many bytes of a stored object to fetch for the preview (HTTP Range). */
  preview_max_bytes: number;
}

export const DEFAULT_CONFIG: AdminConfig = {
  api_base: "/api",
  services: {
    orchestrator: "orchestrator",
    registry: "registry",
    storage: "storage",
    llm: "llm",
    handler: "handler-runtime",
    assistant: "assistant",
    collector: "web-collector",
  },
  auth: { mode: "api_key" },
  polling: { initial_ms: 1000, max_ms: 15000, multiplier: 1.5 },
  page_size: 50,
  preview_max_bytes: 262144,
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function positive(value: unknown, fallback: number, min = 1): number {
  return typeof value === "number" && Number.isFinite(value) && value >= min ? value : fallback;
}

/** Merges a raw config document over the defaults, rejecting malformed values instead of trusting them. */
export function parseConfig(raw: unknown): AdminConfig {
  if (!isRecord(raw)) return DEFAULT_CONFIG;
  const services = { ...DEFAULT_CONFIG.services };
  if (isRecord(raw["services"])) {
    for (const key of Object.keys(services) as ServiceKey[]) {
      const value = raw["services"][key];
      if (typeof value === "string" && /^[a-z0-9][a-z0-9._-]*$/.test(value)) services[key] = value;
    }
  }
  let auth: AuthConfig = DEFAULT_CONFIG.auth;
  const rawAuth = raw["auth"];
  if (isRecord(rawAuth)) {
    if (rawAuth["mode"] === "none") auth = { mode: "none" };
    if (rawAuth["mode"] === "oidc") {
      const authority = rawAuth["authority"];
      const clientId = rawAuth["client_id"];
      if (typeof authority !== "string" || typeof clientId !== "string" || !authority || !clientId) {
        throw new Error("config.json: auth.mode=oidc requires auth.authority and auth.client_id");
      }
      auth = {
        mode: "oidc",
        authority,
        client_id: clientId,
        scope: typeof rawAuth["scope"] === "string" ? rawAuth["scope"] : "openid profile",
        redirect_path:
          typeof rawAuth["redirect_path"] === "string" ? rawAuth["redirect_path"] : "/auth/callback",
        post_logout_redirect_path:
          typeof rawAuth["post_logout_redirect_path"] === "string"
            ? rawAuth["post_logout_redirect_path"]
            : "/",
      };
    }
  }
  const polling = isRecord(raw["polling"]) ? raw["polling"] : {};
  const initial = positive(polling["initial_ms"], DEFAULT_CONFIG.polling.initial_ms, 100);
  return {
    api_base:
      typeof raw["api_base"] === "string" && raw["api_base"]
        ? raw["api_base"].replace(/\/+$/, "")
        : DEFAULT_CONFIG.api_base,
    services,
    auth,
    polling: {
      initial_ms: initial,
      max_ms: Math.max(initial, positive(polling["max_ms"], DEFAULT_CONFIG.polling.max_ms, 100)),
      multiplier: positive(polling["multiplier"], DEFAULT_CONFIG.polling.multiplier, 1),
    },
    page_size: Math.floor(positive(raw["page_size"], DEFAULT_CONFIG.page_size)),
    preview_max_bytes: Math.floor(positive(raw["preview_max_bytes"], DEFAULT_CONFIG.preview_max_bytes)),
  };
}

export async function loadConfig(fetchImpl: typeof fetch = fetch): Promise<AdminConfig> {
  const response = await fetchImpl("/config.json", { cache: "no-store" });
  if (!response.ok) return DEFAULT_CONFIG;
  return parseConfig(await response.json());
}

export function serviceBaseUrl(config: AdminConfig, service: ServiceKey | { executor: string }): string {
  const name = typeof service === "string" ? config.services[service] : service.executor;
  return `${config.api_base}/${name}`;
}

/** Absolute form of a base URL (relative prefixes are resolved against the page origin). */
export function absoluteUrl(
  base: string,
  origin: string = globalThis.location?.origin ?? "http://localhost",
): string {
  return new URL(base, origin.endsWith("/") ? origin : `${origin}/`).toString().replace(/\/+$/, "");
}
