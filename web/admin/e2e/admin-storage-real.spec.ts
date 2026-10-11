import { expect, realServiceUrl, test } from "./fixtures";
import { htmlMaterial, jsonRequest, storageInvoke, uniqueId } from "./seed";

// The storage HTTP service and filesystem adapter are real. Other APIs may be contract mocks.
test("materials and storage status from the real filesystem adapter @hybrid", async ({ admin, request }) => {
  const storage = realServiceUrl("storage");
  test.skip(
    !storage || !process.env["JANE_ADMIN_STORAGE_SMOKE_ROOT"],
    "Isolated filesystem smoke service is required",
  );
  const root = process.env["JANE_ADMIN_STORAGE_SMOKE_ROOT"] as string;
  const service = storage as string;
  const prefix = uniqueId("browser-storage");
  const source = `${prefix}-source`;
  const connections = [`${prefix}-a`, `${prefix}-b`] as const;
  for (const id of connections) {
    await jsonRequest(
      request,
      "put",
      `${service}/v1/connections/${id}`,
      {
        connection_id: id,
        kind: "filesystem",
        params: { base_path: `${root}/${id}` },
      },
      [200, 201],
    );
  }
  const html = `<h1>${prefix}</h1><script>window.__storageExecuted = true</script>`;
  for (const [index, id] of connections.entries()) {
    await storageInvoke(request, service, id, `${prefix}-delivery-${index}`, {
      kind: "material",
      material: htmlMaterial(
        source,
        `https://example.test/${prefix}/${index}`,
        html,
        `${prefix}-obs-${index}`,
        "2026-10-11T08:00:00Z",
      ),
    });
  }
  await admin.goto(`/materials?source_id=${source}`);
  for (const id of connections) {
    const table = admin.getByRole("table", { name: `Матеріали ${id}`, exact: true });
    await expect(table).toContainText(source);
    await expect(table.getByRole("row")).toHaveCount(2);
  }
  await admin
    .getByRole("table", { name: `Матеріали ${connections[0]}`, exact: true })
    .getByRole("button", { name: "Переглянути", exact: true })
    .click();
  await expect(admin.getByTestId("content-preview")).toContainText(html);
  expect(
    await admin.evaluate(() => (window as unknown as { __storageExecuted?: boolean }).__storageExecuted),
  ).toBeUndefined();

  await admin.goto("/storages");
  const card = admin.getByRole("region", { name: connections[0], exact: true });
  await expect(card).toContainText("Не перевірено");
  await expect(card).toContainText("Невідомо");
  await card.getByRole("button", { name: "Перевірити зараз", exact: true }).click();
  await expect(card).toContainText("Доступне");
  const statusResponse = await request.get(`${service}/v1/storage-status?connection_id=${connections[0]}`);
  expect(statusResponse.ok()).toBe(true);
  const status = (await statusResponse.json()) as {
    availability: string;
    checked_at: string;
    statistics: { object_count: number; total_size_bytes: number };
  };
  expect(status.availability).toBe("available");
  expect(status.checked_at).toBeTruthy();
  expect(status.statistics.object_count).toBe(1);
  expect(status.statistics.total_size_bytes).toBe(Buffer.byteLength(html));
  await admin.reload();
  await expect(admin.getByRole("region", { name: connections[0], exact: true })).toContainText("Доступне");
});
