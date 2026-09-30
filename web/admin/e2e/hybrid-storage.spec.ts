import { expect, realServiceUrl, test } from "./fixtures";
import { htmlMaterial, productEntity, storageInvoke, uniqueId } from "./seed";

// «Матеріали» and «Результати» against the REAL storage service (WP-07, files and PostgreSQL adapters). Data is seeded through
// the storage API inside the test, so the scenario does not depend on example data.
// Hybrid: JANE_ADMIN_TARGET_STORAGE=http://127.0.0.1:<port>; whole stack: JANE_ADMIN_API_TARGET.
// The default dev stack has separate connections for RAW files and result entities.
const rawConnectionId = process.env["JANE_ADMIN_E2E_STORAGE_CONNECTION"] || "raw-files";
const resultsConnectionId = process.env["JANE_ADMIN_E2E_RESULTS_CONNECTION"] || "results-pg";
const resultsPackageId = process.env["JANE_ADMIN_E2E_RESULTS_PACKAGE"] || "jane.storage-postgresql";

test.describe("real storage: materials and results @hybrid", () => {
  test("stored RAW is listed and shown as text; entity state and late (stale) updates are visible", async ({
    admin,
    request,
  }) => {
    const storage = realServiceUrl("storage");
    test.skip(!storage, "JANE_ADMIN_TARGET_STORAGE / JANE_ADMIN_API_TARGET is not set");
    const storageUrl = storage as string;
    const sourceId = uniqueId("e2e-src");
    const url = `https://shop.example.test/product/${sourceId}`;
    const marker = `Kettle ${sourceId}`;
    // The script must stay inert text in the admin (material content is data, not markup).
    const html = `<html><head><title>${marker}</title></head><body><h1>${marker}</h1><script>window.__janePwned = 1</script></body></html>`;

    await storageInvoke(request, storageUrl, rawConnectionId, `${sourceId}-raw`, {
      kind: "material",
      material: htmlMaterial(sourceId, url, html, `obs_${sourceId}_1`, "2026-09-28T06:00:00Z"),
    });
    // Newer observation first, then a late one with an older observed_at: its price must be stale.
    await storageInvoke(
      request,
      storageUrl,
      resultsConnectionId,
      `${sourceId}-e1`,
      {
        kind: "entities",
        entities: [
          productEntity(
            sourceId,
            "A-100",
            { title: marker, price: { amount: 1199, currency: "UAH" } },
            `obs_${sourceId}_2`,
            "2026-09-28T06:00:00Z",
          ),
        ],
      },
      resultsPackageId,
    );
    await storageInvoke(
      request,
      storageUrl,
      resultsConnectionId,
      `${sourceId}-e2`,
      {
        kind: "entities",
        entities: [
          productEntity(
            sourceId,
            "A-100",
            { price: { amount: 1399, currency: "UAH" } },
            `obs_${sourceId}_0`,
            "2026-09-26T08:00:00Z",
          ),
        ],
      },
      resultsPackageId,
    );

    await admin.goto(`/materials?connection_id=${rawConnectionId}&source_id=${sourceId}`);
    const table = admin.getByRole("table", { name: "Збережені матеріали" });
    await expect(table).toContainText(url);
    await expect(table.getByRole("row")).toHaveCount(2); // header + the seeded object only (source filter)
    await table.getByRole("button", { name: "Переглянути" }).click();
    const preview = admin.getByTestId("content-preview");
    await expect(preview).toContainText(`<title>${marker}</title>`);
    await expect(preview).toContainText("<script>window.__janePwned = 1</script>");
    expect(
      await admin.evaluate(() => (window as unknown as { __janePwned?: number }).__janePwned),
    ).toBeUndefined();
    await expect(admin.getByRole("region", { name: /^Об'єкт / })).toContainText(`obs_${sourceId}_1`);

    await admin.goto(`/results?connection_id=${resultsConnectionId}&entity_type=product&scope=${sourceId}`);
    const entities = admin.getByRole("table", { name: "Сутності" });
    await expect(entities).toContainText(marker);
    await expect(entities).toContainText("1199");
    await expect(entities).not.toContainText("1399");
    await entities.getByRole("button", { name: "Історія" }).click();
    const history = admin.getByRole("table", { name: "Історія сутності" });
    await expect(history.getByRole("row")).toHaveCount(3);
    // Only the late record has stale fields (its price and the repeated sku lose to the newer observation).
    await expect(history.locator(".badge-warn")).toHaveCount(1);
    await expect(history.locator(".badge-warn")).toContainText("price");
    await expect(admin.getByRole("alert")).toHaveCount(0);
  });
});
