// Playwright e2e for the admin.
//   * default: contract mocks (`uv run contracts/tools/mock.py <api>`, one per service) + Vite as the reverse proxy;
//   * real API: JANE_ADMIN_API_TARGET=<Jane reverse proxy URL> - Caddy serves the built admin and real APIs;
//     tests tagged @mock (they depend on contract example data) are skipped; auth and the data-independent
//     @hybrid scenarios (they seed their own data through the service APIs) run against the stack;
//   * hybrid: JANE_ADMIN_TARGET_<API>=<service URL> replaces one mock by a real service (see README).
// Ports are configurable: JANE_ADMIN_PORT (admin, 4600), JANE_ADMIN_MOCK_PORT_BASE (first mock, 4611).
import path from "node:path";
import { defineConfig, devices } from "@playwright/test";
import { MOCK_SERVICES, apiTarget, mockPort } from "./dev-proxy.ts";

const adminPort = Number.parseInt(process.env["JANE_ADMIN_PORT"] ?? "4600", 10);
const repoRoot = path.resolve(import.meta.dirname, "..", "..");
const real = apiTarget();
const reuse = !process.env["CI"];

const mocks = real
  ? []
  : MOCK_SERVICES.map(({ api }, index) => ({
      command: `uv run --quiet contracts/tools/mock.py ${api} --host 127.0.0.1 --port ${mockPort(index)}`,
      cwd: repoRoot,
      url: `http://127.0.0.1:${mockPort(index)}/v1/health`,
      reuseExistingServer: reuse,
      timeout: 120_000,
      stdout: "ignore" as const,
      stderr: "ignore" as const,
    }));

export default defineConfig({
  testDir: "e2e",
  fullyParallel: false,
  workers: 1,
  retries: process.env["CI"] ? 1 : 0,
  timeout: 60_000,
  expect: { timeout: 10_000 },
  reporter: [["list"], ["html", { open: "never", outputFolder: "playwright-report" }]],
  ...(real ? { grepInvert: /@mock/ } : {}),
  use: {
    baseURL: real ?? `http://127.0.0.1:${adminPort}`,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: real
    ? []
    : [
        ...mocks,
        {
          // A production build served by `vite preview` (same proxy as `vite dev`): fast, close to deployment.
          command: `node node_modules/vite/bin/vite.js build --logLevel warn && node node_modules/vite/bin/vite.js preview --port ${adminPort} --strictPort --host 127.0.0.1`,
          url: `http://127.0.0.1:${adminPort}/config.json`,
          reuseExistingServer: reuse,
          timeout: 120_000,
          stdout: "ignore",
          stderr: "pipe",
        },
      ],
});
