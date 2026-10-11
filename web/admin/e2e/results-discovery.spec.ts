import { test, expect, openapiExample } from "./fixtures";
import type { Connection, EntityState } from "../src/api/types";

const pg = openapiExample<Connection>("connection-pg");
const entity = openapiExample<EntityState>("entity-state");

for (const width of [1360, 390]) {
  test("results discovery and server search at " + width + "px @mock", async ({ admin }) => {
    await admin.setViewportSize({ width, height: 900 });
    const entityRequests: URL[] = [];
    await admin.route("**/api/storage/v1/connections?**", (route) =>
      route.fulfill({ json: { items: [pg], next_cursor: null } }),
    );
    await admin.route("**/api/storage/v1/entity-types?**", (route) =>
      route.fulfill({
        json: {
          items: [
            { entity_type: "offer", entity_count: 7 },
            { entity_type: "article", entity_count: 3 },
          ],
          next_cursor: null,
          search_supported: true,
        },
      }),
    );
    await admin.route("**/api/storage/v1/entities?**", (route) => {
      const url = new URL(route.request().url());
      entityRequests.push(url);
      return route.fulfill({
        json: {
          items: [
            {
              ...entity,
              entity_type: "offer",
              fields: {
                title: url.searchParams.get("search") ? "Needle beyond first page" : "First page only",
                price: { amount: 0, currency: "UAH" },
              },
            },
          ],
          next_cursor: url.searchParams.get("search") ? null : "unloaded-page",
        },
      });
    });
    await admin.goto("/results");
    await expect(admin.getByRole("link", { name: /Пропозиції магазинів/ })).toBeVisible();
    await expect(admin.getByRole("link", { name: /Статті/ })).toBeVisible();
    expect(entityRequests).toHaveLength(0);
    await admin.getByRole("link", { name: /Пропозиції магазинів/ }).click();
    await expect(admin.getByRole("table", { name: "Сутності" })).toContainText("First page only");
    await admin.getByLabel(/^Пошук у всьому сховищі/).fill("Needle");
    await admin.getByRole("button", { name: "Знайти" }).click();
    await expect(admin.getByRole("table", { name: "Сутності" })).toContainText("Needle beyond first page");
    expect(entityRequests.some((url) => url.searchParams.has("cursor"))).toBe(false);
    expect(entityRequests.at(-1)?.searchParams.get("search")).toBe("Needle");
    await expect(admin.getByText("0 UAH", { exact: true })).toBeVisible();
  });
}
