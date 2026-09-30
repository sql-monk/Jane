// Starts one contract mock per Jane API (contracts/tools/mock.py) for `pnpm dev` without a real stack.
// Ports: JANE_ADMIN_MOCK_PORT_BASE (default 4611) + index, in the order of dev-proxy.ts MOCK_SERVICES.
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const APIS = ["orchestrator", "registry", "storage", "llm", "handler", "assistant", "collector"];
const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..", "..");
const base = Number.parseInt(process.env.JANE_ADMIN_MOCK_PORT_BASE ?? "4611", 10);

const children = APIS.map((api, index) => {
  const port = String(base + index);
  const child = spawn(
    "uv",
    ["run", "--quiet", "contracts/tools/mock.py", api, "--host", "127.0.0.1", "--port", port],
    {
      cwd: repoRoot,
      stdio: "inherit",
      shell: process.platform === "win32",
    },
  );
  child.on("exit", (code) => {
    if (code) console.error(`mock ${api} exited with ${code}`);
  });
  return child;
});

const stop = () => {
  for (const child of children) child.kill();
  process.exit(0);
};
process.on("SIGINT", stop);
process.on("SIGTERM", stop);
