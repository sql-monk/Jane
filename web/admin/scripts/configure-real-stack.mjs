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
  { executor: "llm", role: "llm", base_url: "http://llm:8110" },
  { executor: "assistant", role: "assistant", base_url: "http://assistant:8000" },
];
const override = {
  services: {
    registry: {
      environment: {
        JANE_REGISTRY_RUNTIME_PROFILES: JSON.stringify(["http://handler-runtime:8000/v1/info"]),
      },
    },
    "handler-runtime": {
      environment: { JANE_HANDLER_RUNTIME_REGISTRY_URL: "http://registry:8000" },
    },
    "web-collector": {
      environment: { JANE_WEB_COLLECTOR_REGISTRY_URL: "http://registry:8000" },
    },
    orchestrator: {
      environment: { JANE_ORCHESTRATOR_EXECUTORS: JSON.stringify(executors) },
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
    ],
    { env: { ...process.env, ...stack.env }, stdio: "inherit" },
  );
  if (result.error) throw result.error;
  process.exitCode = result.status ?? 1;
} finally {
  unlinkSync(overrideFile);
  rmdirSync(tempDir);
}
