import { afterEach, describe, expect, it, vi } from "vitest";
import { createApiClients, unwrap, unwrapWithEtag } from "./client";
import { ApiError } from "./problem";
import { DEFAULT_CONFIG } from "../config";
import { openapiExample } from "../test/contracts";

function jsonResponse(body: unknown, status = 200, headers: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...headers },
  });
}

afterEach(() => vi.unstubAllGlobals());

describe("API clients", () => {
  it("calls <api_base>/<service>/v1/... with the bearer token", async () => {
    const fetchMock = vi.fn(async (_request: Request) =>
      jsonResponse(openapiExample("source-shop"), 200, { ETag: '"v3"' }),
    );
    vi.stubGlobal("fetch", fetchMock);
    const api = createApiClients(DEFAULT_CONFIG, { getToken: () => "dev-key", onUnauthenticated: () => {} });
    const result = await unwrapWithEtag(
      api.orchestrator.GET("/v1/sources/{source_id}", { params: { path: { source_id: "shop-example" } } }),
    );
    expect(result.etag).toBe('"v3"');
    expect(result.data.source_id).toBe("shop-example");
    const request = fetchMock.mock.calls[0]?.[0] as Request;
    expect(new URL(request.url).pathname).toBe("/api/orchestrator/v1/sources/shop-example");
    expect(request.headers.get("Authorization")).toBe("Bearer dev-key");
  });

  it("turns problem+json into ApiError and reports 401", async () => {
    const onUnauthenticated = vi.fn();
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        jsonResponse(
          {
            type: "urn:jane:problem:unauthenticated",
            title: "Unauthenticated",
            status: 401,
            code: "unauthenticated",
          },
          401,
        ),
      ),
    );
    const api = createApiClients(DEFAULT_CONFIG, { getToken: () => null, onUnauthenticated });
    const error = await unwrap(api.orchestrator.GET("/v1/sources")).catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).code).toBe("unauthenticated");
    expect(onUnauthenticated).toHaveBeenCalledOnce();
  });

  it("maps network failures to upstream_unavailable", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        throw new TypeError("Failed to fetch");
      }),
    );
    const api = createApiClients(DEFAULT_CONFIG, { getToken: () => null, onUnauthenticated: () => {} });
    const error = await unwrap(api.llm.GET("/v1/providers")).catch((e: unknown) => e);
    expect((error as ApiError).code).toBe("upstream_unavailable");
  });

  it("rejects executor names that could escape the proxy prefix", () => {
    const api = createApiClients(DEFAULT_CONFIG, { getToken: () => null, onUnauthenticated: () => {} });
    expect(() => api.executor("../orchestrator")).toThrow();
    expect(() => api.executor("storage")).not.toThrow();
  });
});
