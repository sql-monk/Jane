// Runs the Playwright e2e suite (cross-platform wrapper, no shell-specific env syntax).
//
//   pnpm e2e                         contract mocks (default)
//   pnpm e2e:real http://127.0.0.1:8080   built admin and APIs on the real Jane reverse proxy; @mock tests skipped
//   pnpm e2e -- --grep packages      extra arguments go to `playwright test`
import { spawnSync } from "node:child_process";
import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = path.resolve(appRoot, "..", "..");
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
  const projectIndex = args.indexOf("--project");
  const project = projectIndex >= 0 ? args[projectIndex + 1] : undefined;
  if (projectIndex >= 0) {
    if (!project || !/^[a-z][a-z0-9-]*$/.test(project)) {
      console.error("e2e --real --project needs the Compose project created by just up");
      process.exit(2);
    }
    args.splice(projectIndex, 2);
  }
  try {
    const stackDir = path.join(repoRoot, ".jane");
    const stackFiles = project
      ? [path.join(stackDir, `stack-${project}.json`)]
      : env.JANE_STACK_FILE
        ? [path.resolve(env.JANE_STACK_FILE)]
        : readdirSync(stackDir)
            .filter((name) => /^stack-.*\.json$/.test(name))
            .map((name) => path.join(stackDir, name));
    const matching = stackFiles
      .map((file) => {
        // Never include JSON content or credentials in error messages.
        let stack;
        try {
          stack = JSON.parse(readFileSync(file, "utf8"));
        } catch {
          throw new Error(`Cannot read stack file ${file}`);
        }
        return stack;
      })
      .filter((stack) => stack.services?.proxy?.url === new URL(target).origin);
    if (matching.length !== 1)
      throw new Error("Choose one matching just up stack with --project or JANE_STACK_FILE");
    const key = matching[0].env?.JANE_API_KEY_ADMIN;
    if (typeof key !== "string" || !key)
      throw new Error("The stack has no admin API key; recreate it with just up after B2");
    // The Playwright fixtures consume this variable; its value always comes from the selected stack.
    env.JANE_ADMIN_E2E_API_KEY = key;
  } catch (error) {
    console.error(`e2e: ${error.message}`);
    process.exit(2);
  }
  env.JANE_ADMIN_API_TARGET = target;
  console.log(`e2e: real UI and API via ${target} (tests tagged @mock are skipped)`);
} else {
  delete env.JANE_ADMIN_API_TARGET;
  const real = Object.keys(env)
    .filter((k) => k.startsWith("JANE_ADMIN_TARGET_") && env[k])
    .map((k) => `${k.slice("JANE_ADMIN_TARGET_".length).toLowerCase()}=${env[k]}`);
  console.log(
    `e2e: contract mocks (contracts/tools/mock.py)${real.length ? `; real services instead of mocks: ${real.join(", ")}` : ""}`,
  );
}

const cli = path.join(appRoot, "node_modules", "@playwright", "test", "cli.js");
const result = spawnSync(process.execPath, [cli, "test", ...args], { cwd: appRoot, env, stdio: "inherit" });
process.exit(result.status ?? 1);
