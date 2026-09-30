// Runs the Playwright e2e suite (cross-platform wrapper, no shell-specific env syntax).
//
//   pnpm e2e                         contract mocks (default)
//   pnpm e2e:real http://127.0.0.1:8080   real Jane reverse proxy (`just env` prints its port); @mock tests skipped
//   pnpm e2e -- --grep packages      extra arguments go to `playwright test`
import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2).filter((a) => a !== "--");
const env = { ...process.env };

const realIndex = args.indexOf("--real");
if (realIndex >= 0) {
  const next = args[realIndex + 1];
  const target = next && !next.startsWith("-") ? next : env.JANE_ADMIN_API_TARGET;
  args.splice(realIndex, next && !next.startsWith("-") ? 2 : 1);
  if (!target) {
    console.error(
      "e2e --real needs the URL of the Jane reverse proxy, e.g. `pnpm e2e:real http://127.0.0.1:8080`",
    );
    process.exit(2);
  }
  env.JANE_ADMIN_API_TARGET = target;
  console.log(`e2e: real API via ${target} (tests tagged @mock are skipped)`);
} else {
  delete env.JANE_ADMIN_API_TARGET;
  console.log("e2e: contract mocks (contracts/tools/mock.py)");
}

const cli = path.join(appRoot, "node_modules", "@playwright", "test", "cli.js");
const result = spawnSync(process.execPath, [cli, "test", ...args], { cwd: appRoot, env, stdio: "inherit" });
process.exit(result.status ?? 1);
