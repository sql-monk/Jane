// Dev/e2e wiring shared by vite.config.ts and playwright.config.ts.
//
// The admin always calls `<api_base>/<service>/v1/...` (ADR-0005: reverse proxy with /api/<service> prefixes).
// Locally Vite plays the reverse proxy:
//   * JANE_ADMIN_API_TARGET=http://127.0.0.1:8080  -> real stack: `/api/*` goes to the Jane reverse proxy as is;
//   * otherwise (default)                          -> contract mocks: `/api/<service>` goes to
//     `uv run contracts/tools/mock.py <api> --port <JANE_ADMIN_MOCK_PORT_BASE + i>` with the prefix stripped.
import type { ProxyOptions } from "vite";

/** Contract name (contracts/openapi/<api>.v1.yaml) -> reverse-proxy service name (public/config.json). */
export const MOCK_SERVICES: ReadonlyArray<{ api: string; service: string }> = [
  { api: "orchestrator", service: "orchestrator" },
  { api: "registry", service: "registry" },
  { api: "storage", service: "storage" },
  { api: "llm", service: "llm" },
  { api: "handler", service: "handler-runtime" },
  { api: "assistant", service: "assistant" },
  { api: "collector", service: "web-collector" },
];

export function mockPortBase(env: NodeJS.ProcessEnv = process.env): number {
  const raw = env["JANE_ADMIN_MOCK_PORT_BASE"];
  const value = raw ? Number.parseInt(raw, 10) : 4611;
  if (!Number.isInteger(value) || value < 1024 || value > 65000) {
    throw new Error(`JANE_ADMIN_MOCK_PORT_BASE must be an integer port, got ${raw}`);
  }
  return value;
}

export function mockPort(index: number, env: NodeJS.ProcessEnv = process.env): number {
  return mockPortBase(env) + index;
}

export function apiTarget(env: NodeJS.ProcessEnv = process.env): string | undefined {
  const target = env["JANE_ADMIN_API_TARGET"]?.trim();
  return target ? target.replace(/\/+$/, "") : undefined;
}

export function buildProxy(env: NodeJS.ProcessEnv = process.env): Record<string, ProxyOptions> {
  const target = apiTarget(env);
  if (target) {
    return { "/api": { target, changeOrigin: true } };
  }
  const proxy: Record<string, ProxyOptions> = {};
  MOCK_SERVICES.forEach(({ service }, index) => {
    const prefix = `/api/${service}`;
    proxy[prefix] = {
      target: `http://127.0.0.1:${mockPort(index, env)}`,
      changeOrigin: true,
      rewrite: (p: string) => p.slice(prefix.length) || "/",
    };
  });
  return proxy;
}
