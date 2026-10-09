// Configure the isolated Compose stack for the real admin browser suite.
// The base stack deliberately leaves cross-service wiring optional; this test-only override
// registers real executors and exposes the runtime profile to the real registry.
import { spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmdirSync, unlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "..");
const project = process.argv[2];
if (!project || !/^[a-z][a-z0-9-]*$/.test(project)) {
  console.error("Usage: pnpm e2e:real:prepare <compose-project>");
  process.exit(2);
}

const stack = JSON.parse(readFileSync(path.join(repoRoot, ".jane", `stack-${project}.json`), "utf8"));
if (stack.project !== project) throw new Error(`Stack project does not match ${project}`);

const executors = [
  {
    executor: "web-collector",
    role: "collector",
    base_url: "http://web-collector:8101",
    capabilities: { collector: "web" },
  },
  {
    executor: "handler-runtime",
    role: "handler",
    base_url: "http://handler-runtime:8000",
    capabilities: { handler_kinds: ["extractor", "transform"], default: true },
  },
  {
    executor: "storage",
    role: "handler",
    base_url: "http://storage:8000",
    capabilities: { packages: ["jane.storage-*"], handler_kinds: ["storage"] },
  },
  {
    executor: "storage-read",
    role: "storage_read",
    base_url: "http://storage:8000",
    sync_connections: false,
  },
  { executor: "registry", role: "registry", base_url: "http://registry:8000" },
  // LLM stages (packages of kind `llm`, e.g. page triage of unknown materials) run in the LLM gateway.
  { executor: "llm", role: "llm", base_url: "http://llm:8110", capabilities: { handler_kinds: ["llm"] } },
  { executor: "assistant", role: "assistant", base_url: "http://assistant:8000" },
];
// Model aliases of the source assistant on the TEST stack only. The real-mode specs point them at a
// deterministic fake provider through the LLM API (e2e/seed.ts), so aliases of a shared stack stay untouched.
const ASSISTANT_ALIASES = { cheap: "e2e-admin-cheap", strong: "e2e-admin-strong" };
// Onboarding by name (R26, as S-M2-06 in tests/e2e/compose.e2e.yaml): the static search provider of the assistant
// (a SUBSTITUTE of a web search) with the test site and a second match of the same name; one material per
// classification request, so that a scripted answer of the fake LLM classifies exactly that material.
const ASSISTANT_SEARCH_FILE = path.join(repoRoot, "tests", "e2e", "config", "assistant-search.json");
const LLM_REQUESTS_PER_MINUTE = process.env.JANE_ADMIN_E2E_LLM_MAX_REQUESTS_PER_MINUTE ?? "120";
if (!/^[1-9][0-9]*$/.test(LLM_REQUESTS_PER_MINUTE))
  throw new Error("JANE_ADMIN_E2E_LLM_MAX_REQUESTS_PER_MINUTE must be a positive integer");
const schemaRetries = Number(process.env.JANE_ADMIN_E2E_SCHEMA_RETRIES ?? "1");
if (!Number.isInteger(schemaRetries) || schemaRetries < 0)
  throw new Error("JANE_ADMIN_E2E_SCHEMA_RETRIES must be a non-negative integer");
const override = {
  services: {
    registry: {
      environment: {
        JANE_REGISTRY_RUNTIME_PROFILES: JSON.stringify(["http://handler-runtime:8000/v1/info"]),
      },
    },
    "handler-runtime": {
      environment: {
        JANE_HANDLER_RUNTIME_REGISTRY_URL: "http://registry:8000",
        // Stored RAW of the files adapter is a file:// ContentRef (ADR-0004: one node, shared volume);
        // reprocessing of stored RAW reads it read-only.
        JANE_HANDLER_RUNTIME_BLOB_ROOTS: JSON.stringify(["/var/lib/jane/storage/objects"]),
      },
      volumes: ["storage-data:/var/lib/jane/storage:ro"],
    },
    "web-collector": {
      environment: { JANE_WEB_COLLECTOR_REGISTRY_URL: "http://registry:8000" },
    },
    orchestrator: {
      environment: { JANE_ORCHESTRATOR_EXECUTORS: JSON.stringify(executors) },
    },
    llm: {
      // LLM packages of orchestrated stages come from the real registry (no package_archive in invocations).
      environment: {
        JANE_LLM_REGISTRY_URL: "http://registry:8000",
        JANE_LLM_LIMITS__GATEWAY__MAX_SCHEMA_RETRIES: String(schemaRetries),
        JANE_LLM_LIMITS__LLM__MAX_REQUESTS_PER_MINUTE: LLM_REQUESTS_PER_MINUTE,
      },
    },
    assistant: {
      environment: {
        JANE_ASSISTANT_REGISTRY_URL: "http://registry:8000",
        JANE_ASSISTANT_ORCHESTRATOR_URL: "http://orchestrator:8000",
        JANE_ASSISTANT_COLLECTOR_WEB_URL: "http://web-collector:8101",
        JANE_ASSISTANT_LLM_MODEL_CHEAP: ASSISTANT_ALIASES.cheap,
        JANE_ASSISTANT_LLM_MODEL_STRONG: ASSISTANT_ALIASES.strong,
        JANE_ASSISTANT_SEARCH_PROVIDER: "static",
        JANE_ASSISTANT_SEARCH_STATIC_FILE: "/cfg/assistant-search.json",
        JANE_ASSISTANT_LIMITS__ONBOARDING__SAMPLE_BATCH_SIZE: "1",
        JANE_ASSISTANT_LIMITS__ONBOARDING__POLL_PAGE_FACTOR: "10",
        JANE_ASSISTANT_LIMITS__LLM__MAX_REQUESTS_PER_MINUTE: LLM_REQUESTS_PER_MINUTE,
      },
      volumes: [
        {
          type: "bind",
          source: ASSISTANT_SEARCH_FILE,
          target: "/cfg/assistant-search.json",
          read_only: true,
        },
      ],
    },
  },
};

const tempDir = mkdtempSync(path.join(tmpdir(), "jane-admin-real-"));
const overrideFile = path.join(tempDir, "compose.override.json");
try {
  writeFileSync(overrideFile, JSON.stringify(override), "utf8");
  const result = spawnSync(
    "docker",
    [
      "compose",
      "-f",
      stack.compose_file,
      "-f",
      overrideFile,
      "-p",
      project,
      "up",
      "-d",
      "--wait",
      "--wait-timeout",
      "180",
      "--no-build",
      "registry",
      "handler-runtime",
      "orchestrator",
      "web-collector",
      "llm",
      "assistant",
    ],
    { env: { ...process.env, ...stack.env }, stdio: "inherit" },
  );
  if (result.error) throw result.error;
  process.exitCode = result.status ?? 1;
} finally {
  unlinkSync(overrideFile);
  rmdirSync(tempDir);
}
