import path from "node:path";
import { captureRequest, expect, realServiceUrl, test } from "./fixtures";
import { startRegistryStandin, type Standin } from "./registry-standin";
import { publishExtractorPackage } from "./seed";

// «Тести без запису» against the REAL handler-runtime (WP-06, Docker sandbox). With a real registry,
// seed an SDK example through registry.v1; the contract stand-in remains available for isolated runtime runs. Run:
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
const enabled = Boolean(realServiceUrl("handler") && realServiceUrl("registry"));

test.describe("real handler-runtime: package tests without writes @hybrid", () => {
  let standin: Standin | null = null;
  test.beforeAll(async () => {
    if (enabled && Number.isInteger(standinPort))
      standin = await startRegistryStandin(packageDir, standinPort);
  });
  test.afterAll(async () => {
    await standin?.close();
  });

  test("run the manifest tests of a package in the sandbox and show the TestReport", async ({
    admin,
    request,
  }) => {
    test.skip(
      !enabled,
      "JANE_ADMIN_TARGET_HANDLER and JANE_ADMIN_TARGET_REGISTRY / JANE_ADMIN_API_TARGET are not set",
    );
    const seeded = standin
      ? {
          package_id: standin.pkg.package_id,
          version: standin.version.version,
          digest: standin.version.digest,
          manifest: standin.version.manifest as Record<string, unknown>,
        }
      : await publishExtractorPackage(request, realServiceUrl("registry") as string, packageDir);
    const testNames = ((seeded.manifest["tests"] ?? []) as Array<{ name: string }>).map((t) => t.name);
    expect(testNames.length).toBeGreaterThan(0);

    await admin.goto(`/packages/${seeded.package_id}`);
    await admin.getByRole("tab", { name: "Версії й тести" }).click();
    await admin.getByRole("button", { name: seeded.version }).click();
    await expect(admin.getByRole("table", { name: "Файли версії" })).toContainText("jane-package.json");

    const run = await captureRequest(admin, "POST", "/api/handler-runtime/v1/test-runs", () =>
      admin.getByRole("button", { name: "Запустити тести (без запису)" }).click(),
    );
    expect(run.body).toEqual({
      handler: { package_id: seeded.package_id, version: seeded.version, digest: seeded.digest },
      tests: "all",
    });

    const panel = admin.getByLabel("Прогін тестів");
    await expect(panel.locator(".job-head .badge")).toHaveText("succeeded", { timeout: 120_000 });
    const report = panel.getByLabel("Звіт тестів");
    await expect(report).toContainText(`${seeded.package_id}@${seeded.version}`);
    for (const name of testNames)
      await expect(report.getByRole("table", { name: "Тестові випадки" })).toContainText(name);
    await expect(
      report.getByRole("table", { name: "Тестові випадки" }).getByText("passed", { exact: true }),
    ).toHaveCount(testNames.length);
  });
});
