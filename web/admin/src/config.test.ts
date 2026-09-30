import { describe, expect, it } from "vitest";
import { DEFAULT_CONFIG, parseConfig, serviceBaseUrl } from "./config";
import { pollDelay } from "./api/hooks";

describe("parseConfig", () => {
  it("falls back to safe defaults", () => {
    expect(parseConfig(null)).toEqual(DEFAULT_CONFIG);
    expect(
      parseConfig({ page_size: -1, polling: { initial_ms: 1 }, services: { orchestrator: "../evil" } }),
    ).toEqual(DEFAULT_CONFIG);
  });

  it("reads the reverse-proxy prefix and service names", () => {
    const config = parseConfig({ api_base: "https://jane.example/api/", services: { handler: "runtime" } });
    expect(serviceBaseUrl(config, "handler")).toBe("https://jane.example/api/runtime");
    expect(serviceBaseUrl(config, "orchestrator")).toBe("https://jane.example/api/orchestrator");
    expect(serviceBaseUrl(config, { executor: "storage" })).toBe("https://jane.example/api/storage");
  });

  it("requires authority and client_id for OIDC", () => {
    expect(() => parseConfig({ auth: { mode: "oidc" } })).toThrow(/authority/);
    const config = parseConfig({
      auth: { mode: "oidc", authority: "https://idp.example", client_id: "jane-admin" },
    });
    expect(config.auth).toMatchObject({
      mode: "oidc",
      redirect_path: "/auth/callback",
      scope: "openid profile",
    });
  });

  it("keeps the shipped public/config.json valid", async () => {
    const { readFileSync } = await import("node:fs");
    const raw = JSON.parse(readFileSync(`${process.cwd()}/public/config.json`, "utf8")) as unknown;
    expect(parseConfig(raw)).toEqual(DEFAULT_CONFIG);
  });
});

describe("pollDelay", () => {
  it("backs off exponentially up to the configured maximum", () => {
    const polling = { initial_ms: 1000, max_ms: 5000, multiplier: 2 };
    expect([0, 1, 2, 3, 10].map((n) => pollDelay(n, polling))).toEqual([1000, 2000, 4000, 5000, 5000]);
  });
});
