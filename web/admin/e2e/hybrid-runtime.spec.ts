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

  test("run sandbox tests, edit and publish an immutable version, diff, retest and approve", async ({
    admin,
    request,
  }) => {
    test.setTimeout(180_000);
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

    const codePath = "src/testsite_products/main.py";
    await admin.goto(`/packages/${seeded.package_id}/versions/${seeded.version}/edit`);
    await admin.getByRole("button", { name: codePath }).click();
    const editor = admin.getByRole("textbox", { name: `Код ${codePath}` });
    await editor.click();
    await admin.keyboard.press("Control+End");
    await admin.keyboard.type("\n# e2e immutable editor version\n");
    await expect(admin.getByLabel("Локальні зміни")).toContainText("e2e immutable editor version");
    await admin.getByLabel("Опис змін").fill("Verify real editor publication");
    const published = await captureRequest(
      admin,
      "POST",
      `/api/registry/v1/packages/${seeded.package_id}/versions`,
      () => admin.getByRole("button", { name: "Опублікувати як нову версію" }).click(),
    );
    expect(published.request.headers()["idempotency-key"]).toBeTruthy();
    expect((published.body["manifest"] as { version: string }).version).toBe("1.0.1");
    expect((published.body["files"] as Record<string, { data: string }>)[codePath]?.data).toContain(
      "e2e immutable editor version",
    );
    await expect(admin).toHaveURL(new RegExp(`/packages/${seeded.package_id}\\?version=1\\.0\\.1`));
    await admin.getByRole("tab", { name: "Відмінності" }).click();
    await admin.getByLabel("Від (версія або parent:<версія>)").fill("1.0.0");
    await admin.getByLabel("До версії").fill("1.0.1");
    await admin.getByRole("button", { name: "Порівняти" }).click();
    await expect(admin.getByLabel("Відмінності версій")).toContainText("e2e immutable editor version");

    await admin.getByRole("tab", { name: "Версії й тести" }).click();
    await admin.getByRole("button", { name: "1.0.1" }).click();
    const retest = await captureRequest(admin, "POST", "/api/handler-runtime/v1/test-runs", () =>
      admin.getByRole("button", { name: "Запустити тести (без запису)" }).click(),
    );
    expect(retest.body).toMatchObject({
      handler: { package_id: seeded.package_id, version: "1.0.1" },
      tests: "all",
    });
    const retestPanel = admin.getByLabel("Прогін тестів");
    await expect(retestPanel.locator(".job-head .badge")).toHaveText("succeeded", { timeout: 120_000 });
    await expect(
      retestPanel
        .getByLabel("Звіт тестів")
        .getByRole("table", { name: "Тестові випадки" })
        .getByText("passed", { exact: true }),
    ).toHaveCount(testNames.length);
    await admin.getByRole("button", { name: "Погодити", exact: true }).click();
    await admin.getByLabel("Причина: Погодити").fill("All isolated package tests passed");
    const approve = await captureRequest(admin, "POST", /\/versions\/1\.0\.1\/status$/, () =>
      admin.getByRole("button", { name: "Погодити версію" }).click(),
    );
    expect(approve.body).toEqual({ status: "approved", reason: "All isolated package tests passed" });
    await expect(admin.getByRole("table", { name: "Версії", exact: true })).toContainText("approved");
  });
});
