import { test, expect, openapiExample, mockUrl } from "./fixtures";
import type { Connection, StoredObject } from "../src/api/types";

const pg = openapiExample<Connection>("connection-pg");

test.describe("material/storage browser @mock", () => {
  test("automatic discovery, isolated failure, independent pagination and inert content", async ({
    admin,
  }) => {
    const sample = (await (
      await fetch(`${mockUrl("storage")}/v1/objects?connection_id=raw-files`)
    ).json()) as { items: StoredObject[] };
    const object = sample.items[0]!;
    await admin.route("**/api/storage/v1/connections?**", (route) =>
      route.fulfill({
        json: { items: [pg, { connection_id: "raw-files", kind: "filesystem" }], next_cursor: null },
      }),
    );
    await admin.route("**/api/storage/v1/objects?**", (route) => {
      const url = new URL(route.request().url());
      return url.searchParams.get("connection_id") === pg.connection_id
        ? route.fulfill({
            status: 503,
            json: {
              type: "urn:jane:problem:upstream_unavailable",
              title: "Offline",
              status: 503,
              code: "upstream_unavailable",
            },
          })
        : route.fulfill({
            json: {
              items: [
                {
                  ...object,
                  object: {
                    ...object.object,
                    object_id: url.searchParams.has("cursor") ? "obj_second" : object.object.object_id,
                  },
                },
              ],
              next_cursor: url.searchParams.has("cursor") ? null : "raw-next",
            },
          });
    });
    await admin.goto("/materials");
    const table = admin.getByRole("table", { name: "Матеріали raw-files" });
    await expect(table).toContainText(object.object.object_id);
    await expect(admin.getByRole("alert")).toContainText("upstream_unavailable");
    await admin
      .getByRole("region", { name: "raw-files" })
      .getByRole("button", { name: "Показати ще" })
      .click();
    await expect(table).toContainText("obj_second");
    await table.getByRole("button", { name: "Переглянути" }).first().click();
    await expect(admin).toHaveURL(/connection_id=raw-files.*object_id=/);
    await expect(admin.getByTestId("content-preview")).toContainText("<title>Kettle A-100</title>");
    expect(await admin.locator("title", { hasText: "Kettle A-100" }).count()).toBe(0);
    await admin.screenshot({ path: "../../.jane/wp25-materials-wide.png", fullPage: true });
    await admin.setViewportSize({ width: 390, height: 844 });
    await expect(admin.getByRole("heading", { name: "Матеріали", exact: true })).toBeVisible();
    await admin.screenshot({ path: "../../.jane/wp25-materials-narrow.png", fullPage: true });
  });

  test("unknown statistics and explicit check refresh the snapshot", async ({ admin }) => {
    let checked = false;
    await admin.route("**/api/storage/v1/connections?**", (route) =>
      route.fulfill({ json: { items: [pg], next_cursor: null } }),
    );
    await admin.route("**/api/storage/v1/storage-status?**", (route) =>
      route.fulfill({
        json: {
          connection_id: pg.connection_id,
          kind: pg.kind,
          availability: checked ? "available" : "unknown",
          checked_at: checked ? "2026-10-11T08:00:00Z" : null,
          message: null,
          statistics: {
            object_count: null,
            total_size_bytes: null,
            checked_at: null,
            scope: "connection_objects",
            unavailable_reason: "adapter_statistics_not_supported",
          },
        },
      }),
    );
    await admin.route("**/api/storage/v1/storage-status/checks", async (route) => {
      expect(route.request().headers()["idempotency-key"]).toBeTruthy();
      expect(route.request().postDataJSON()).toEqual({ connection_id: "results-pg" });
      return route.fulfill({
        status: 202,
        headers: { Location: "/v1/jobs/job_status_check" },
        json: {
          job_id: "job_status_check",
          kind: "storage_status_check",
          status: "queued",
          created_at: "2026-10-11T08:00:00Z",
        },
      });
    });
    let finish = false;
    await admin.route("**/api/storage/v1/jobs/job_status_check", (route) => {
      checked = finish;
      return route.fulfill({
        json: {
          job_id: "job_status_check",
          kind: "storage_status_check",
          status: finish ? "succeeded" : "running",
          created_at: "2026-10-11T08:00:00Z",
          progress: { completed: finish ? 1 : 0, total: 1, unit: "connections" },
          ...(finish
            ? {
                finished_at: "2026-10-11T08:00:01Z",
                result: {
                  connection_id: pg.connection_id,
                  kind: pg.kind,
                  availability: "available",
                  checked_at: "2026-10-11T08:00:00Z",
                  message: null,
                  statistics: {
                    object_count: null,
                    total_size_bytes: null,
                    checked_at: null,
                    scope: "connection_objects",
                    unavailable_reason: "adapter_statistics_not_supported",
                  },
                },
              }
            : {}),
        },
      });
    });
    await admin.goto("/storages");
    await expect(admin.getByText("Невідомо", { exact: true })).toHaveCount(2);
    await admin.getByRole("button", { name: "Перевірити зараз" }).click();
    await expect(admin.getByRole("button", { name: "Перевіряємо…" })).toBeDisabled();
    await expect(admin.getByText("Перевіряємо доступність і статистику…")).toBeVisible();
    finish = true;
    await expect(admin.getByText("Доступне", { exact: true })).toBeVisible();
    await expect(admin.getByRole("button", { name: "Перевірити зараз" })).toBeEnabled();
    await admin.screenshot({ path: "../../.jane/wp25-storages-wide.png", fullPage: true });
    await admin.setViewportSize({ width: 390, height: 844 });
    await admin.screenshot({ path: "../../.jane/wp25-storages-narrow.png", fullPage: true });
  });
});
