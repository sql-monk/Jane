import { API_KEY, captureRequest, expect, openapiExample, realServiceUrl, test } from "./fixtures";
import { uniqueId } from "./seed";

// The admin talks to a real registry. Each test creates its own package, so no contract example
// response or shared registry state is assumed. The contract examples supply valid input documents.
test.describe("real registry: rules package, approval and independent fork @hybrid", () => {
  test("create and publish rules, approve, fork, then explicitly port a later parent version", async ({
    admin,
    request,
  }) => {
    const registry = realServiceUrl("registry");
    test.skip(!registry, "JANE_ADMIN_TARGET_REGISTRY / JANE_ADMIN_API_TARGET is not set");
    const base = registry as string;
    const headers = { Authorization: `Bearer ${API_KEY}` };
    const packageId = uniqueId("e2e-rules");
    const forkId = `${packageId}-fork`;
    const manifest = openapiExample<Record<string, unknown>>("manifest-rules");
    const rules = openapiExample<Record<string, unknown>>("rules-web-shop");
    manifest["package_id"] = packageId;
    manifest["provenance"] = { created_by: "human" };

    await admin.goto("/packages");
    await admin.getByRole("button", { name: "Новий пакет" }).click();
    const creator = admin.getByRole("region", { name: "Новий пакет (без версій)" });
    await creator.getByLabel("package_id").fill(packageId);
    await creator.getByLabel("Тип").selectOption("collector-rules");
    await creator.getByLabel("Назва").fill(`E2E rules ${packageId}`);
    const created = await captureRequest(admin, "POST", "/api/registry/v1/packages", () =>
      creator.getByRole("button", { name: "Створити" }).click(),
    );
    expect(created.request.headers()["idempotency-key"]).toBeTruthy();
    await expect(admin).toHaveURL(new RegExp(`/packages/${packageId}$`));

    async function publish(version: string, document: Record<string, unknown>) {
      const response = await request.post(`${base}/v1/packages/${packageId}/versions`, {
        headers: { Authorization: `Bearer ${API_KEY}`, "Idempotency-Key": uniqueId("publish") },
        data: {
          manifest: { ...manifest, version },
          files: { "rules.json": { encoding: "utf-8", data: JSON.stringify(document) } },
        },
      });
      expect(response.status(), await response.text()).toBe(201);
      return (await response.json()) as { digest: string };
    }

    const first = await publish("1.0.0", rules);
    expect(first.digest).toMatch(/^sha256:[0-9a-f]{64}$/);
    await admin.reload();
    await admin.getByRole("tab", { name: "Версії й тести" }).click();
    await admin.getByRole("button", { name: "1.0.0" }).click();
    await expect(admin.getByRole("table", { name: "Файли версії" })).toContainText("rules.json");
    await admin.getByRole("button", { name: "Погодити", exact: true }).click();
    await admin.getByLabel("Причина: Погодити").fill("E2E review of rules");
    const approved = await captureRequest(admin, "POST", /\/versions\/1\.0\.0\/status$/, () =>
      admin.getByRole("button", { name: "Погодити версію" }).click(),
    );
    expect(approved.body).toEqual({ status: "approved", reason: "E2E review of rules" });
    await expect(admin.getByRole("table", { name: "Версії", exact: true })).toContainText("approved");

    await admin.getByRole("tab", { name: "Створити форк" }).click();
    await admin.getByLabel("Новий package_id").fill(forkId);
    await admin.getByRole("button", { name: "Створити форк" }).click();
    await expect(admin).toHaveURL(new RegExp(`/packages/${forkId}$`));
    await expect(admin.getByRole("alert")).toHaveCount(0);

    await admin.goto(`/packages/${packageId}/versions/1.0.0/rules`);
    await expect(admin.getByRole("heading", { name: /Стратегії обходу \(3\)/ })).toBeVisible();
    await admin.getByLabel("Тип нової стратегії").selectOption("feed");
    await admin.getByRole("button", { name: "Додати стратегію" }).click();
    await admin.getByLabel("Нова версія").fill("1.1.0");
    await admin.getByLabel("Опис змін").fill("Add feed strategy");
    const parentUpdate = await captureRequest(
      admin,
      "POST",
      `/api/registry/v1/packages/${packageId}/versions`,
      () => admin.getByRole("button", { name: "Опублікувати версію правил" }).click(),
    );
    expect((parentUpdate.body["manifest"] as { version: string }).version).toBe("1.1.0");
    await admin.goto(`/packages/${forkId}`);
    await admin.getByRole("tab", { name: "Оновлення батька" }).click();
    await expect(admin.getByTestId("newer-parent-versions")).toContainText("1.1.0");
    await admin.getByRole("button", { name: "Порівняти з батьком 1.1.0" }).click();
    await expect(admin.getByLabel("Відмінності версій")).toContainText("rules.json");
    const forkResponse = await request.get(`${base}/v1/packages/${forkId}/versions`, { headers });
    expect(forkResponse.status(), await forkResponse.text()).toBe(200);
    const forkVersions = await forkResponse.json();
    expect(forkVersions.items.map((v: { version: string }) => v.version)).toEqual(["1.0.0"]);

    await admin.getByLabel("Версія батька").selectOption("1.1.0");
    await admin.getByLabel("Нова версія форку").fill("1.1.0");
    await admin.getByRole("button", { name: "Перенести зміни" }).click();
    const port = await captureRequest(
      admin,
      "POST",
      `/api/registry/v1/packages/${forkId}/upstream-ports`,
      () => admin.getByRole("button", { name: "Так, перенести в нову версію" }).click(),
    );
    expect(port.request.headers()["idempotency-key"]).toBeTruthy();
    expect(port.body).toEqual({ parent_version: "1.1.0", new_version: "1.1.0", base_version: "1.0.0" });
    const panel = admin.getByLabel("Перенесення змін батька");
    await expect(panel.locator(".job-head .badge")).toHaveText("succeeded", { timeout: 120_000 });
    await expect
      .poll(async () => {
        const response = await request.get(`${base}/v1/packages/${forkId}/versions/1.1.0`, { headers });
        return response.status();
      })
      .toBe(200);
    const ported = await (await request.get(`${base}/v1/packages/${forkId}/versions/1.1.0`, { headers })).json();
    expect(ported.manifest?.provenance?.upstream_port?.parent_version).toBe("1.1.0");
    await admin.goto(`/packages/${forkId}`);
    await admin.getByRole("tab", { name: "Відмінності" }).click();
    await admin.getByLabel("Від (версія або parent:<версія>)").fill("1.0.0");
    await admin.getByLabel("До версії").fill("1.1.0");
    await admin.getByRole("button", { name: "Порівняти" }).click();
    await expect(admin.getByLabel("Відмінності версій")).toContainText("feed");
  });
});
