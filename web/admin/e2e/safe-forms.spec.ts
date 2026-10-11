import { captureRequest, expect, fulfillJson, openapiExample, test } from "./fixtures";
import type { TaskConfig } from "../src/api/types";

test("source draft is protected on links, save-and-leave and native history @mock", async ({
  admin,
  apiRequests,
}) => {
  await admin.goto("/sources");
  await admin.getByRole("link", { name: "shop-example", exact: true }).click();
  const name = admin.getByLabel("Назва", { exact: true });
  await name.fill("Чернетка джерела");
  await admin
    .getByRole("navigation", { name: "Розділи" })
    .getByRole("link", { name: "Завдання", exact: true })
    .click();
  const warning = admin.getByRole("dialog", { name: "Незбережені зміни" });
  await expect(warning).toBeVisible();
  await warning.getByRole("button", { name: "Залишитися", exact: true }).click();
  await expect(name).toHaveValue("Чернетка джерела");
  await expect(admin).toHaveURL(/\/sources\/shop-example$/);
  expect(apiRequests.filter((request) => request.method() !== "GET")).toHaveLength(0);
  await admin.evaluate(() => window.history.back());
  await expect(warning).toBeVisible();
  await warning.getByRole("button", { name: "Залишитися", exact: true }).click();
  await expect(name).toHaveValue("Чернетка джерела");
  await expect(admin).toHaveURL(/\/sources\/shop-example$/);
  await admin
    .getByRole("navigation", { name: "Розділи" })
    .getByRole("link", { name: "Завдання", exact: true })
    .click();
  const { body } = await captureRequest(admin, "PUT", "/api/orchestrator/v1/sources/shop-example", () =>
    warning.getByRole("button", { name: "Зберегти й перейти" }).click(),
  );
  expect(body["title"]).toBe("Чернетка джерела");
  await expect(admin).toHaveURL(/\/tasks$/);
});

test("discard leaves without a write and browser reload warns about dirty source @mock", async ({
  admin,
  apiRequests,
}) => {
  await admin.goto("/sources/shop-example");
  await admin.getByLabel("Назва", { exact: true }).fill("Не зберігати");
  const dialogPromise = admin.waitForEvent("dialog");
  const reload = admin.reload({ timeout: 5000 }).catch(() => null);
  const dialog = await dialogPromise;
  expect(dialog.type()).toBe("beforeunload");
  await dialog.dismiss();
  await reload;
  await expect(admin.getByLabel("Назва", { exact: true })).toHaveValue("Не зберігати");
  await admin
    .getByRole("navigation", { name: "Розділи" })
    .getByRole("link", { name: "Завдання", exact: true })
    .click();
  await admin
    .getByRole("dialog", { name: "Незбережені зміни" })
    .getByRole("button", { name: "Відкинути й перейти" })
    .click();
  await expect(admin).toHaveURL(/\/tasks$/);
  expect(apiRequests.filter((request) => request.method() !== "GET")).toHaveLength(0);
});

test("new source stays quiet until submit, human validation stops invalid API writes @mock", async ({
  admin,
  apiRequests,
}) => {
  await admin.goto("/sources/new");
  await expect(admin.getByRole("alert")).toHaveCount(0);
  await admin.getByRole("button", { name: "Створити джерело" }).click();
  await expect(admin.getByLabel("Помилки форми")).toContainText("Заповніть поле");
  await expect(admin.getByLabel("Помилки форми")).not.toContainText("must");
  expect(apiRequests.filter((request) => request.method() !== "GET")).toHaveLength(0);
  await admin.getByLabel("Ідентифікатор (source_id)").fill("Invalid Source");
  await admin.getByLabel("Назва", { exact: true }).fill("Джерело");
  await admin.getByLabel("URL", { exact: true }).fill("https://example.test/");
  await admin.getByRole("button", { name: "Створити джерело" }).click();
  await expect(admin.getByLabel("Помилки форми")).toContainText("малі латинські літери");
  await expect(admin.getByLabel("Ідентифікатор (source_id)")).toHaveAttribute("aria-invalid", "true");
  expect(apiRequests.filter((request) => request.method() !== "GET")).toHaveLength(0);
});

test("source picker searches names and chain shows actual inherited rules without duplicate ref fields @mock", async ({
  admin,
}) => {
  await admin.goto("/tasks/new");
  await expect(admin.getByRole("alert")).toHaveCount(0);
  await admin.getByLabel("Пошук за назвою (джерело)").fill("Shop Example");
  await admin
    .getByRole("group", { name: "Збіги: Джерело (source_id)" })
    .getByRole("button", { name: /shop-example/ })
    .click();
  await expect(admin.getByLabel("Джерело (source_id)", { exact: false }).last()).toHaveValue("shop-example");
  await admin.getByRole("tab", { name: "Ланцюжок" }).click();
  await expect(admin.getByText("shop-example.web-rules@1.0.0", { exact: true })).toBeVisible();
  await expect(admin.getByLabel("Значення $.collector.mode", { exact: true })).toHaveJSProperty(
    "tagName",
    "SELECT",
  );
  await admin.getByLabel("Значення $.collector.mode", { exact: true }).selectOption("incremental");
  await admin.getByRole("button", { name: "Додати етап-обробник" }).click();
  await expect(admin.getByLabel("Назва $.handler", { exact: true })).toHaveCount(0);
  await admin.getByRole("button", { name: "Додати умову 1", exact: true }).click();
  await expect(admin.getByLabel("Значення $.op", { exact: true })).toHaveJSProperty("tagName", "SELECT");
});

test("invalid task schedule keeps the entered draft and explains error after submit @mock", async ({
  admin,
  apiRequests,
}) => {
  await admin.goto("/tasks/shop-catalog");
  await admin.getByLabel("Тип розкладу").selectOption("interval");
  await expect(admin.getByLabel("Помилки конфігурації")).toHaveCount(0);
  await admin.getByRole("button", { name: "Зберегти", exact: true }).click();
  await expect(admin.getByLabel("Помилки конфігурації")).toContainText("Інтервал у секундах");
  await expect(admin.getByLabel("Інтервал, секунд")).toHaveAttribute("aria-invalid", "true");
  expect(apiRequests.filter((request) => request.method() !== "GET")).toHaveLength(0);
  await admin.getByLabel("Інтервал, секунд").fill("60");
  await admin.getByLabel("Інтервал, секунд").fill("");
  await expect(admin.getByLabel("Інтервал, секунд")).toHaveValue("");
});

test("native forward protects the source draft and discard replays the destination @mock", async ({
  admin,
}) => {
  await admin.goto("/sources");
  await admin.getByRole("link", { name: "shop-example", exact: true }).click();
  await admin
    .getByRole("navigation", { name: "Розділи" })
    .getByRole("link", { name: "Завдання", exact: true })
    .click();
  await expect(admin).toHaveURL(/\/tasks$/);
  await admin.evaluate(() => window.history.back());
  await expect(admin).toHaveURL(/\/sources\/shop-example$/);
  await admin.getByLabel("Назва", { exact: true }).fill("Чернетка перед переходом уперед");
  await admin.evaluate(() => window.history.forward());
  const warning = admin.getByRole("dialog", { name: "Незбережені зміни" });
  await expect(warning).toBeVisible();
  await warning.getByRole("button", { name: "Залишитися", exact: true }).click();
  await expect(admin.getByLabel("Назва", { exact: true })).toHaveValue("Чернетка перед переходом уперед");
  await admin.evaluate(() => window.history.forward());
  await warning.getByRole("button", { name: "Відкинути й перейти", exact: true }).click();
  await expect(admin).toHaveURL(/\/tasks$/);
});

test("source editing is locked while the submitted snapshot is saving @mock", async ({ admin }) => {
  let finishSave!: () => void;
  const pending = new Promise<void>((resolve) => {
    finishSave = resolve;
  });
  await admin.route("**/api/orchestrator/v1/sources/shop-example", async (route) => {
    if (route.request().method() !== "PUT") return route.fallback();
    await pending;
    await route.continue();
  });
  await admin.goto("/sources/shop-example");
  await admin.getByLabel("Назва", { exact: true }).fill("Збережений знімок");
  try {
    await captureRequest(admin, "PUT", "/api/orchestrator/v1/sources/shop-example", () =>
      admin.getByRole("button", { name: "Зберегти", exact: true }).click(),
    );
    await expect(admin.getByLabel("Назва", { exact: true })).toBeDisabled();
    await expect(admin.getByLabel("Пакет правил", { exact: true })).toBeDisabled();
  } finally {
    finishSave();
  }
  await expect(admin.getByLabel("Назва", { exact: true })).toBeEnabled();
  await expect(admin.getByText("Є незбережені зміни", { exact: true })).toHaveCount(0);
});

test("task result link uses actual storage manifest and explicit scope only @mock", async ({ admin }) => {
  const task = openapiExample<TaskConfig>("task-catalog");
  const destination = task.stages.find((stage) => stage.stage_id === "store-products")!;
  destination.params = { scope: "shop_example" };
  await fulfillJson(admin, "/api/orchestrator/v1/tasks/shop-catalog", task);
  await admin.route("**/api/registry/v1/packages/jane.storage-postgresql/versions/1.0.0", async (route) => {
    const response = await route.fetch();
    const version = (await response.json()) as Record<string, unknown>;
    await route.fulfill({ response, json: { ...version, manifest: openapiExample("manifest-storage-pg") } });
  });
  await admin.goto("/tasks/shop-catalog");
  const link = admin.getByRole("link", { name: "Розібрані дані: store-products", exact: true });
  await expect(link).toHaveAttribute("href", "/results?connection_id=results-pg&scope=shop_example");
  expect(await link.getAttribute("href")).not.toContain("shop-example");
  delete destination.params;
  await fulfillJson(admin, "/api/orchestrator/v1/tasks/shop-catalog", task);
  await admin.reload();
  await expect(link).toHaveAttribute("href", "/results?connection_id=results-pg");
});
