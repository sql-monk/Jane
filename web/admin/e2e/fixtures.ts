import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import path from "node:path";
import { test as base, expect, type Locator, type Page, type Request } from "@playwright/test";
import { MOCK_SERVICES, apiTarget, mockPort, serviceTarget } from "../dev-proxy.ts";
import type { ModuleTelemetry } from "../src/lib/modules";

/**
 * Direct URL of a REAL service for seeding data in hybrid/real runs: JANE_ADMIN_TARGET_<API> (hybrid) or
 * `<JANE_ADMIN_API_TARGET>/api/<service>` (whole stack behind the reverse proxy). Undefined on pure mocks.
 */
export function realServiceUrl(api: string): string | undefined {
  const direct = serviceTarget(api);
  if (direct) return direct;
  const stack = apiTarget();
  const service = MOCK_SERVICES.find((s) => s.api === api)?.service;
  return stack && service ? `${stack}/api/${service}` : undefined;
}

const REPO_ROOT = path.resolve(import.meta.dirname, "..", "..", "..");

let telemetryExample: ModuleTelemetry | undefined;

/** Read the shared Operations API example using the contract tools' YAML loader. */
function operationsTelemetryExample(): ModuleTelemetry {
  if (!telemetryExample) {
    const source = execFileSync(
      "uv",
      [
        "run",
        "--quiet",
        "--no-project",
        "--with",
        "pyyaml>=6",
        "python",
        "-c",
        [
          "import json, sys",
          "from pathlib import Path",
          'sys.path.insert(0, str(Path("contracts/tools").resolve()))',
          "from _common import load_file",
          'spec = load_file(Path("contracts/openapi/operations.v1.yaml"))',
          'print(json.dumps(spec["paths"]["/v1/telemetry"]["get"]["responses"]["200"]["content"]["application/json"]["example"]))',
        ].join("\n"),
      ],
      {
        cwd: REPO_ROOT,
        encoding: "utf8",
        env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1" },
      },
    );
    telemetryExample = JSON.parse(source) as ModuleTelemetry;
  }
  return telemetryExample;
}

/** Service mocks predate the shared Operations paths. Real and hybrid APIs remain real. */
async function mockOperationsTelemetry(page: Page): Promise<void> {
  const hybrid = Object.entries(process.env).some(
    ([name, value]) => name.startsWith("JANE_ADMIN_TARGET_") && value?.trim(),
  );
  if (apiTarget() || hybrid) return;
  const services = new Set([...MOCK_SERVICES.map(({ service }) => service), "telegram-collector"]);
  const example = operationsTelemetryExample();
  await page.route(
    (url) => {
      const parts = url.pathname.split("/");
      return (
        parts[1] === "api" && services.has(parts[2] ?? "") && parts.slice(3).join("/") === "v1/telemetry"
      );
    },
    (route) => {
      if (route.request().method() !== "GET") return route.fallback();
      const service = new URL(route.request().url()).pathname.split("/")[2]!;
      // Only the module identity changes; measurements and their timestamps stay from the contract.
      const instanceId = `${service}-${example.instance_id}`;
      return route.fulfill({
        json: {
          ...example,
          service,
          instance_id: instanceId,
          samples: example.samples.map((sample) => ({ ...sample, instance_id: instanceId })),
        },
      });
    },
  );
}

/** Enter the same instant in a datetime-local field on both Windows and Linux browsers. */
export async function fillInstant(page: Page, field: Locator, instant: string): Promise<void> {
  const value = await page.evaluate((timestamp) => {
    const date = new Date(timestamp);
    const two = (part: number) => String(part).padStart(2, "0");
    const input = document.createElement("input");
    input.type = "datetime-local";
    input.value = `${date.getFullYear()}-${two(date.getMonth() + 1)}-${two(date.getDate())}T${two(date.getHours())}:${two(date.getMinutes())}:${two(date.getSeconds())}.${String(date.getMilliseconds()).padStart(3, "0")}`;
    // Browsers omit zero seconds/fractions. Playwright requires this canonical native value.
    return input.value;
  }, instant);
  await field.fill(value);
}

/** Select an existing entity through its paginated UI catalog, without injecting options. */
export async function selectCatalogOption(
  container: Page | Locator,
  field: Locator,
  value: string,
  moreLabel = "Показати ще",
): Promise<void> {
  await expect
    .poll(
      async () => {
        const present = await field
          .locator("option")
          .evaluateAll(
            (options, id) => options.some((option) => (option as HTMLOptionElement).value === id),
            value,
          );
        if (present) return true;
        const more = container.getByRole("button", { name: moreLabel, exact: true });
        if ((await more.count()) === 1 && (await more.isVisible()) && (await more.isEnabled()))
          await more.click();
        return false;
      },
      { message: `Entity ${value} must be available in the UI catalog`, timeout: 10_000 },
    )
    .toBe(true);
  await field.selectOption(value);
}

/** Reprocessing offers its own task-catalog pagination control. */
export async function selectTask(container: Page | Locator, field: Locator, taskId: string): Promise<void> {
  await selectCatalogOption(container, field, taskId, "Більше завдань");
}

/** `contracts/examples/openapi/<name>.json` -> its `value` (contract examples are the only test data). */
export function openapiExample<T = Record<string, unknown>>(name: string): T {
  const file = path.join(REPO_ROOT, "contracts", "examples", "openapi", `${name}.json`);
  return (JSON.parse(readFileSync(file, "utf8")) as { value: T }).value;
}

/** Dev API key used by the suite; it must never appear on a page, in a URL or in localStorage. */
export const API_KEY = process.env["JANE_ADMIN_E2E_API_KEY"] || "e2e-admin-key-7f3c-never-shown";

/** Base URL of the contract mock of an API (mock mode only), e.g. for reading contract examples. */
export function mockUrl(api: string): string {
  const index = MOCK_SERVICES.findIndex((s) => s.api === api);
  if (index < 0) throw new Error(`unknown api ${api}`);
  return `http://127.0.0.1:${mockPort(index)}`;
}

export async function login(page: Page): Promise<void> {
  await mockOperationsTelemetry(page);
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
