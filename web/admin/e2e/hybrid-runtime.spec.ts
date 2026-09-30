import path from "node:path";
import { serviceTarget } from "../dev-proxy.ts";
import { captureRequest, expect, test } from "./fixtures";
import { startRegistryStandin, type Standin } from "./registry-standin";

// «Тести без запису» against the REAL handler-runtime (WP-06, Docker sandbox). The registry (WP-05) is not in main,
// so a contract-shaped stand-in serves one real package (the extractor SDK example) both to the admin and to the
// runtime (see registry-standin.ts). Run:
//   handler-runtime with JANE_HANDLER_RUNTIME_REGISTRY_URL=http://127.0.0.1:<standin port>
//   JANE_ADMIN_TARGET_HANDLER=http://127.0.0.1:<runtime port> JANE_ADMIN_TARGET_REGISTRY=http://127.0.0.1:<standin port>
//   JANE_ADMIN_E2E_REGISTRY_STANDIN_PORT=<standin port> pnpm e2e --grep @hybrid
const standinPort = Number.parseInt(process.env["JANE_ADMIN_E2E_REGISTRY_STANDIN_PORT"] ?? "", 10);
const packageDir =
  process.env["JANE_ADMIN_E2E_PACKAGE_DIR"] ||
  path.resolve(
    import.meta.dirname,
    "..",
    "..",
    "..",
    "libs",
    "extractor-sdk",
    "examples",
    "testsite-product-extractor",
  );
const enabled = Boolean(
  serviceTarget("handler") && serviceTarget("registry") && Number.isInteger(standinPort),
);

test.describe("real handler-runtime: package tests without writes @hybrid", () => {
  let standin: Standin | null = null;
  test.beforeAll(async () => {
    if (enabled) standin = await startRegistryStandin(packageDir, standinPort);
  });
  test.afterAll(async () => {
    await standin?.close();
  });

  test("run the manifest tests of a package in the sandbox and show the TestReport", async ({ admin }) => {
    test.skip(
      !enabled,
      "JANE_ADMIN_TARGET_HANDLER, JANE_ADMIN_TARGET_REGISTRY and JANE_ADMIN_E2E_REGISTRY_STANDIN_PORT are not set",
    );
    const { pkg, version } = standin as Standin;
    const testNames = (version.manifest?.tests ?? []).map((t) => t.name);
    expect(testNames.length).toBeGreaterThan(0);

    await admin.goto(`/packages/${pkg.package_id}`);
    await admin.getByRole("tab", { name: "Версії й тести" }).click();
    await admin.getByRole("button", { name: version.version }).click();
    await expect(admin.getByRole("table", { name: "Файли версії" })).toContainText("jane-package.json");

    const run = await captureRequest(admin, "POST", "/api/handler-runtime/v1/test-runs", () =>
      admin.getByRole("button", { name: "Запустити тести (без запису)" }).click(),
    );
    expect(run.body).toEqual({
      handler: { package_id: pkg.package_id, version: version.version, digest: version.digest },
      tests: "all",
    });

    const panel = admin.getByLabel("Прогін тестів");
    await expect(panel.locator(".job-head .badge")).toHaveText("succeeded", { timeout: 120_000 });
    const report = panel.getByLabel("Звіт тестів");
    await expect(report).toContainText(`${pkg.package_id}@${version.version}`);
    for (const name of testNames)
      await expect(report.getByRole("table", { name: "Тестові випадки" })).toContainText(name);
    await expect(
      report.getByRole("table", { name: "Тестові випадки" }).getByText("passed", { exact: true }),
    ).toHaveCount(testNames.length);
  });
});
