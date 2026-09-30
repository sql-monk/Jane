import { readFileSync } from "node:fs";
import path from "node:path";
import { test as base, expect, type Page, type Request } from "@playwright/test";
import { MOCK_SERVICES, mockPort } from "../dev-proxy.ts";

const REPO_ROOT = path.resolve(import.meta.dirname, "..", "..", "..");

/** `contracts/examples/openapi/<name>.json` -> its `value` (contract examples are the only test data). */
export function openapiExample<T = Record<string, unknown>>(name: string): T {
  const file = path.join(REPO_ROOT, "contracts", "examples", "openapi", `${name}.json`);
  return (JSON.parse(readFileSync(file, "utf8")) as { value: T }).value;
}

/** Dev API key used by the suite; it must never appear on a page, in a URL or in localStorage. */
export const API_KEY = "e2e-admin-key-7f3c-never-shown";

/** Base URL of the contract mock of an API (mock mode only), e.g. for reading contract examples. */
export function mockUrl(api: string): string {
  const index = MOCK_SERVICES.findIndex((s) => s.api === api);
  if (index < 0) throw new Error(`unknown api ${api}`);
  return `http://127.0.0.1:${mockPort(index)}`;
}

export async function login(page: Page): Promise<void> {
  await page.goto("/login");
  await page.getByLabel("Ключ API").fill(API_KEY);
  await page.getByRole("button", { name: "Увійти" }).click();
  await expect(page.getByRole("navigation", { name: "Розділи" })).toBeVisible();
}

/** Asserts that no secret value is visible or stored where it should not be. */
export async function expectNoSecretLeak(page: Page, secrets: readonly string[] = [API_KEY]): Promise<void> {
  const html = await page.content();
  const storage = await page.evaluate(() => JSON.stringify({ ...window.localStorage }));
  for (const secret of secrets) {
    expect(html, `page HTML contains ${secret}`).not.toContain(secret);
    expect(page.url(), "URL contains a secret").not.toContain(secret);
    expect(storage, "localStorage contains a secret").not.toContain(secret);
  }
}

interface Fixtures {
  admin: Page;
  apiRequests: Request[];
}

/** `admin` - a logged-in page; every API request is recorded and checked for auth and idempotency headers. */
export const test = base.extend<Fixtures>({
  apiRequests: async ({}, use) => {
    await use([]);
  },
  admin: async ({ page, apiRequests }, use) => {
    page.on("request", (request) => {
      if (new URL(request.url()).pathname.startsWith("/api/")) apiRequests.push(request);
    });
    await login(page);
    await use(page);
    for (const request of apiRequests) {
      expect(request.headers()["authorization"], `${request.method()} ${request.url()}`).toBe(
        `Bearer ${API_KEY}`,
      );
      expect(request.url()).not.toContain(API_KEY);
    }
    await expectNoSecretLeak(page);
  },
});

export { expect };

/** Waits for an API call and returns its parsed JSON body. */
export async function captureRequest(
  page: Page,
  method: string,
  pathPart: string | RegExp,
  action: () => Promise<unknown>,
): Promise<{ request: Request; body: Record<string, unknown> }> {
  const [request] = await Promise.all([
    page.waitForRequest((r) => {
      const url = new URL(r.url()).pathname;
      return (
        r.method() === method && (typeof pathPart === "string" ? url.includes(pathPart) : pathPart.test(url))
      );
    }),
    action(),
  ]);
  const raw = request.postData();
  return { request, body: raw ? (JSON.parse(raw) as Record<string, unknown>) : {} };
}

/** Forces a named contract example of the mock for requests to exactly this path (Prefer: example=<name>). */
export async function preferExample(
  page: Page,
  pathname: string,
  example: string,
  method = "GET",
): Promise<void> {
  await page.route(
    (url) => url.pathname === pathname,
    (route) =>
      route.request().method() === method
        ? route.continue({ headers: { ...route.request().headers(), prefer: `example=${example}` } })
        : route.fallback(),
  );
}

/** Fulfils requests to exactly this path (and method) with a JSON body taken from contract examples. */
export async function fulfillJson(
  page: Page,
  pathname: string,
  json: unknown,
  method = "GET",
  status = 200,
): Promise<void> {
  await page.route(
    (url) => url.pathname === pathname,
    (route) => (route.request().method() === method ? route.fulfill({ status, json }) : route.fallback()),
  );
}
