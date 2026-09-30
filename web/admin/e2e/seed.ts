// Test data for runs against REAL services: every scenario seeds its own data through the service API
// (handler.v1 of storage) with unique identifiers, so it does not depend on contract example data or on
// what else is stored.
import { createHash } from "node:crypto";
import { readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import type { APIRequestContext } from "@playwright/test";
import { API_KEY, expect } from "./fixtures";

const REPO_ROOT = path.resolve(import.meta.dirname, "..", "..", "..");

/** The deterministic testsite (tests/fixtures/testsite) as the Compose services see it. */
export const TESTSITE_URL = "http://testsite:8080";

export function uniqueId(prefix: string): string {
  return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
}

/** A JSON call to a real service with the dev API key; every POST carries a fresh Idempotency-Key. */
export async function jsonRequest(
  request: APIRequestContext,
  method: "get" | "post" | "put",
  url: string,
  data?: unknown,
  expected: number | number[] = 200,
): Promise<Record<string, unknown>> {
  const response = await request[method](url, {
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      ...(method === "post" ? { "Idempotency-Key": uniqueId("e2e") } : {}),
    },
    ...(data === undefined ? {} : { data }),
  });
  expect([expected].flat(), `${method.toUpperCase()} ${url}: ${await response.text()}`).toContain(
    response.status(),
  );
  return (await response.json()) as Record<string, unknown>;
}

/**
 * Publishes and approves the testsite collector rules (tests/e2e/config/rules/testsite.web-rules: seed `/`,
 * recursive crawl, `/calendar/` excluded) under a unique package id in the real registry.
 */
export async function publishTestsiteRules(
  request: APIRequestContext,
  registryUrl: string,
  prefix: string,
  reason: string,
): Promise<{ package_id: string; version: string }> {
  const rulesDir = path.join(REPO_ROOT, "tests", "e2e", "config", "rules", "testsite.web-rules", "1.0.0");
  const manifest = JSON.parse(readFileSync(path.join(rulesDir, "jane-package.json"), "utf8")) as Record<
    string,
    unknown
  >;
  const packageId = uniqueId(prefix);
  const version = String(manifest["version"]);
  manifest["package_id"] = packageId;
  await jsonRequest(
    request,
    "post",
    `${registryUrl}/v1/packages`,
    { package_id: packageId, kind: "collector-rules", title: `Testsite rules ${packageId}` },
    201,
  );
  await jsonRequest(
    request,
    "post",
    `${registryUrl}/v1/packages/${packageId}/versions`,
    {
      manifest,
      files: {
        "rules.json": { encoding: "utf-8", data: readFileSync(path.join(rulesDir, "rules.json"), "utf8") },
      },
    },
    201,
  );
  await jsonRequest(request, "post", `${registryUrl}/v1/packages/${packageId}/versions/${version}/status`, {
    status: "approved",
    reason,
  });
  return { package_id: packageId, version };
}

/** Pages a complete recursive crawl of the testsite fetches (tests/fixtures/testsite/expected_urls.json). */
export function testsiteRecursivePageCount(): number {
  const file = path.join(REPO_ROOT, "tests", "fixtures", "testsite", "expected_urls.json");
  return (JSON.parse(readFileSync(file, "utf8")) as { sets: { recursive: string[] } }).sets.recursive.length;
}

/** Publish an SDK example into the real registry for the real handler-runtime UI scenario. */
export async function publishExtractorPackage(
  request: APIRequestContext,
  registryUrl: string,
  packageDir: string,
): Promise<{ package_id: string; version: string; digest: string; manifest: Record<string, unknown> }> {
  const manifest = JSON.parse(readFileSync(path.join(packageDir, "jane-package.json"), "utf8")) as Record<
    string,
    unknown
  >;
  const packageId = uniqueId("e2e-extractor");
  manifest["package_id"] = packageId;
  const files: Record<string, { encoding: "base64"; data: string }> = {};
  function collect(dir: string) {
    for (const name of readdirSync(dir).sort()) {
      if (name.startsWith(".") || name === "__pycache__") continue;
      const full = path.join(dir, name);
      if (statSync(full).isDirectory()) collect(full);
      else {
        const relative = path.relative(packageDir, full).split(path.sep).join("/");
        if (relative !== "jane-package.json")
          files[relative] = { encoding: "base64", data: readFileSync(full).toString("base64") };
      }
    }
  }
  collect(packageDir);
  const headers = { Authorization: `Bearer ${API_KEY}`, "Idempotency-Key": uniqueId("registry") };
  const created = await request.post(`${registryUrl}/v1/packages`, {
    headers,
    data: { package_id: packageId, kind: "extractor", title: manifest["title"] },
  });
  if (created.status() !== 201)
    throw new Error(`registry create: HTTP ${created.status()} ${await created.text()}`);
  const published = await request.post(`${registryUrl}/v1/packages/${packageId}/versions`, {
    headers: { ...headers, "Idempotency-Key": uniqueId("publish") },
    data: { manifest, files },
  });
  if (published.status() !== 201)
    throw new Error(`registry publish: HTTP ${published.status()} ${await published.text()}`);
  const version = (await published.json()) as { version: string; digest: string };
  return { package_id: packageId, version: version.version, digest: version.digest, manifest };
}

const sha256 = (text: string): string => createHash("sha256").update(text, "utf8").digest("hex");

/** A web Material (contracts/schemas/material.schema.json) with inline HTML content. */
export function htmlMaterial(
  sourceId: string,
  url: string,
  html: string,
  observationId: string,
  fetchedAt: string,
) {
  const digest = sha256(html);
  return {
    material_id: `web:${sha256(url).slice(0, 32)}`,
    observation_id: observationId,
    source: { source_id: sourceId, kind: "web" },
    locator: { url },
    fetched_at: fetchedAt,
    format: { media_type: "text/html", charset: "utf-8", content_kind: "page" },
    revision: { content_sha256: digest },
    content: {
      kind: "inline",
      media_type: "text/html",
      encoding: "utf-8",
      data: html,
      size_bytes: Buffer.byteLength(html, "utf8"),
      sha256: digest,
    },
    collector: { name: "web-collector", version: "0.1.0" },
  };
}

/** A product entity record (contracts/schemas/entity.schema.json) observed at `observedAt`. */
export function productEntity(
  scope: string,
  sku: string,
  fields: Record<string, unknown>,
  observationId: string,
  observedAt: string,
) {
  return {
    entity_type: "product",
    key: { scope, natural: { sku } },
    fields: { sku, ...fields },
    completeness: "partial",
    observation: { observation_id: observationId, observed_at: observedAt },
  };
}

/** POST /v1/invocations of the storage handler (jane.storage-files) with an Idempotency-Key. */
export async function storageInvoke(
  request: APIRequestContext,
  storageUrl: string,
  connectionId: string,
  deliveryKey: string,
  input: Record<string, unknown>,
  packageId = process.env["JANE_ADMIN_E2E_STORAGE_PACKAGE"] || "jane.storage-files",
): Promise<Record<string, unknown>> {
  const response = await request.post(`${storageUrl}/v1/invocations`, {
    headers: { "Idempotency-Key": deliveryKey, Authorization: `Bearer ${API_KEY}` },
    data: {
      handler: {
        package_id: packageId,
        version: "1.0.0",
      },
      connections: { target: connectionId },
      inputs: [input],
      delivery: { delivery_key: deliveryKey },
    },
  });
  const body = (await response.json()) as Record<string, unknown>;
  if (!response.ok() || body["status"] === "failed") {
    throw new Error(
      `storage invocation ${deliveryKey} failed: HTTP ${response.status()} ${JSON.stringify(body).slice(0, 800)}`,
    );
  }
  return body;
}
