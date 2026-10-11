import { captureRequest, expect, openapiExample, test } from "./fixtures";
import type { TaskConfig } from "../src/api/types";

test("visual chain preserves nested properties, refs and branches through save @mock", async ({ admin }) => {
  await admin.goto("/tasks/shop-catalog");
  await admin.getByRole("tab", { name: "Ланцюжок" }).click();
  await admin.getByTestId("dag-node-extract-products").click();
  await admin.getByLabel("Ідентифікатор етапу").fill("extract-renamed");
  await admin.getByLabel("Ідентифікатор етапу").blur();
  await expect(admin.getByTestId("dag-edge-extract-renamed-store-products")).toBeVisible();
  const grid = admin.getByRole("table", { name: "Властивості", exact: true });
  await grid.getByLabel("Додати $", { exact: true }).click();
  await grid.getByLabel("Назва $.new_field", { exact: true }).fill("params");
  await grid.getByLabel("Назва $.new_field", { exact: true }).blur();
  await grid.getByLabel("Тип $.params", { exact: true }).selectOption("object");
  await grid.getByLabel("Додати $.params", { exact: true }).click();
  await grid.getByLabel("Тип $.params.new_field", { exact: true }).selectOption("array");
  await grid.getByLabel("Додати $.params.new_field", { exact: true }).click();
  await grid.getByLabel("Тип $.params.new_field[0]", { exact: true }).selectOption("boolean");
  await grid.getByLabel("Додати $.params", { exact: true }).click();
  await grid.getByLabel("Тип $.params.new_field_1", { exact: true }).selectOption("number");
  await grid.getByLabel("Значення $.params.new_field_1", { exact: true }).fill("");
  await grid.getByLabel("Значення $.params.new_field_1", { exact: true }).blur();
  await expect(admin.getByRole("button", { name: "Зберегти", exact: true })).toBeDisabled();
  await grid.getByLabel("Розгорнути $.params", { exact: true }).click();
  await expect(admin.getByRole("button", { name: "Зберегти", exact: true })).toBeDisabled();
  await expect(admin.getByRole("button", { name: "Редагувати JSON", exact: true })).toBeDisabled();
  await admin.getByTestId("dag-node-collect").click();
  await expect(admin.getByLabel("Ідентифікатор етапу")).toHaveValue("extract-renamed");
  await admin.getByRole("tab", { name: "Конфігурація" }).click();
  await expect(admin.getByRole("tab", { name: "Ланцюжок" })).toHaveAttribute("aria-selected", "true");
  await grid.getByLabel("Розгорнути $.params", { exact: true }).click();
  await expect(grid.getByLabel("Значення $.params.new_field_1", { exact: true })).toHaveValue("");
  await grid.getByLabel("Значення $.params.new_field_1", { exact: true }).fill("7.25");
  await grid.getByLabel("Значення $.params.new_field_1", { exact: true }).blur();
  await admin.getByRole("button", { name: "Редагувати JSON", exact: true }).click();
  await admin.getByRole("button", { name: "Візуальний редактор" }).click();
  await expect(grid.getByLabel("Значення $.params.new_field[0]", { exact: true })).not.toBeChecked();
  const { body } = await captureRequest(admin, "PUT", "/api/orchestrator/v1/tasks/shop-catalog", () =>
    admin.getByRole("button", { name: "Зберегти", exact: true }).click(),
  );
  const stages = body["stages"] as Array<{
    stage_id: string;
    inputs?: Array<{ from: string }>;
    params?: unknown;
  }>;
  expect(stages.find((s) => s.stage_id === "extract-renamed")?.params).toEqual({
    new_field: [false],
    new_field_1: 7.25,
  });
  expect(stages.find((s) => s.stage_id === "store-products")?.inputs?.[0]?.from).toBe("extract-renamed");
});

test("new visual task picks registry package/version and creates branches @mock", async ({ admin }) => {
  await admin.goto("/tasks/new");
  await admin.getByLabel("Ідентифікатор (task_id)").fill("visual-task");
  await admin.getByLabel("Назва", { exact: true }).fill("Visual Task");
  await admin.getByLabel("Джерело (source_id)").fill("shop-example");
  await admin.getByRole("tab", { name: "Ланцюжок" }).click();
  await admin.getByRole("button", { name: "Додати етап-обробник" }).click();
  await admin.getByLabel("Пакет обробника").selectOption("shop-example.product-extractor");
  await admin.getByLabel("Версія пакета").selectOption("1.2.0");
  await admin.getByTestId("dag-node-collect").click();
  await admin.getByRole("button", { name: "Додати етап-обробник" }).click();
  await admin.getByLabel("Пакет обробника").selectOption("shop-example.product-extractor");
  await admin.getByLabel("Версія пакета").selectOption("1.2.0");
  await expect(admin.getByLabel("Вихід зв’язку 1").locator("option")).toHaveText([
    "output",
    "unmatched_materials",
  ]);
  await admin.getByLabel("Вихід зв’язку 1").selectOption("unmatched_materials");
  await admin.getByRole("button", { name: "Додати умову 1", exact: true }).click();
  const { body } = await captureRequest(admin, "POST", "/api/orchestrator/v1/tasks", () =>
    admin.getByRole("button", { name: "Створити завдання" }).click(),
  );
  const stages = body["stages"] as Array<{ kind: string; handler?: unknown; inputs?: unknown }>;
  expect(stages).toHaveLength(3);
  expect(stages[1]?.handler).toEqual({ package_id: "shop-example.product-extractor", version: "1.2.0" });
  expect(stages[2]?.inputs).toEqual([
    {
      from: "collect",
      select: "unmatched_materials",
      when: { field: "result.status", op: "eq", value: "success" },
    },
  ]);
});

test("visual chain blocks cycle and permits removing directed link @mock", async ({ admin }) => {
  await admin.goto("/tasks/shop-catalog");
  await admin.getByRole("tab", { name: "Ланцюжок" }).click();
  await admin.getByTestId("dag-node-extract-products").click();
  await admin.getByLabel("З’єднати з етапом").selectOption("store-products");
  await admin.getByRole("button", { name: "Додати зв’язок", exact: true }).click();
  await expect(admin.getByRole("button", { name: "Зберегти", exact: true })).toBeDisabled();
  await expect(admin.getByLabel("Проблеми ланцюжка")).toContainText("цикл");
  await admin.getByRole("button", { name: "Видалити зв’язок 2", exact: true }).click();
  await expect(admin.getByRole("button", { name: "Зберегти", exact: true })).toBeEnabled();
  await admin
    .getByRole("button", { name: "Додати умову 1", exact: true })
    .count()
    .then(async (n) => {
      if (n) await admin.getByRole("button", { name: "Додати умову 1", exact: true }).click();
    });
  await expect(admin.getByRole("table", { name: "Умова зв’язку 1" })).toBeVisible();
});

test("raw JSON invalid selects remain visible and block saving @mock", async ({ admin }) => {
  await admin.goto("/tasks/shop-catalog");
  await admin.getByRole("tab", { name: "Ланцюжок" }).click();
  await admin.getByRole("button", { name: "Редагувати JSON", exact: true }).click();
  const task = openapiExample<TaskConfig>("task-catalog");
  const stages = structuredClone(task.stages);
  const extract = stages.find((s) => s.stage_id === "extract-products")!;
  extract.inputs![0]!.select = "problems";
  await admin.getByRole("textbox", { name: "Етапи завдання" }).fill(JSON.stringify(stages));
  await expect(admin.getByRole("button", { name: "Зберегти", exact: true })).toBeDisabled();
  await expect(admin.getByLabel("Помилки конфігурації")).toContainText("недопустимий вихід");
  await admin.getByRole("button", { name: "Візуальний редактор" }).click();
  await admin.getByTestId("dag-node-extract-products").click();
  await expect(admin.getByLabel("Вихід зв’язку 1")).toHaveValue("problems");
  await expect(admin.getByLabel("Вихід зв’язку 1").locator("option")).toHaveText([
    "Недопустимий: problems",
    "output",
    "unmatched_materials",
  ]);
  await admin.getByLabel("Вихід зв’язку 1").selectOption("output");
  await expect(admin.getByRole("button", { name: "Зберегти", exact: true })).toBeEnabled();
  await admin.getByRole("button", { name: "Редагувати JSON", exact: true }).click();
  extract.inputs![0]!.select = "output";
  stages.find((s) => s.stage_id === "store-products")!.inputs![0]!.select = "unmatched_materials";
  await admin.getByRole("textbox", { name: "Етапи завдання" }).fill(JSON.stringify(stages));
  await expect(admin.getByRole("button", { name: "Зберегти", exact: true })).toBeDisabled();
  await admin.getByRole("button", { name: "Візуальний редактор" }).click();
  await admin.getByTestId("dag-node-store-products").click();
  await expect(admin.getByLabel("Вихід зв’язку 1").locator("option")).toHaveText([
    "Недопустимий: unmatched_materials",
    "output",
    "input_material",
    "problems",
  ]);
  await admin.getByLabel("Вихід зв’язку 1").selectOption("input_material");
  await expect(admin.getByRole("button", { name: "Зберегти", exact: true })).toBeEnabled();
});

test("invalid array draft blocks structural edits and supports explicit discard @mock", async ({ admin }) => {
  await admin.goto("/tasks/shop-catalog");
  await admin.getByRole("tab", { name: "Ланцюжок" }).click();
  await admin.getByRole("button", { name: "Редагувати JSON", exact: true }).click();
  const stages = structuredClone(openapiExample<TaskConfig>("task-catalog").stages);
  stages.find((s) => s.stage_id === "extract-products")!.params = { items: [0, 1] };
  await admin.getByRole("textbox", { name: "Етапи завдання" }).fill(JSON.stringify(stages));
  await admin.getByRole("button", { name: "Візуальний редактор" }).click();
  await admin.getByTestId("dag-node-extract-products").click();
  const grid = admin.getByRole("table", { name: "Властивості", exact: true });
  const number = grid.getByLabel("Значення $.params.items[0]", { exact: true });
  await number.fill("");
  await number.blur();
  await expect(grid.getByLabel("Вниз $.params.items[0]", { exact: true })).toBeDisabled();
  await expect(grid.getByLabel("Видалити $.params.items[1]", { exact: true })).toBeDisabled();
  await expect(grid.getByLabel("Тип $.params.items", { exact: true })).toBeDisabled();
  await expect(grid.getByLabel("Назва $.params", { exact: true })).toBeDisabled();
  await expect(admin.getByRole("button", { name: "Зберегти", exact: true })).toBeDisabled();
  await admin.getByRole("button", { name: "Відкинути незбережені поля", exact: true }).click();
  await expect(number).toHaveValue("0");
  await expect(admin.getByRole("button", { name: "Зберегти", exact: true })).toBeEnabled();
  await number.fill("");
  await number.blur();
  await number.fill("9.5");
  await number.blur();
  await grid.getByLabel("Вниз $.params.items[0]", { exact: true }).click();
  const { body } = await captureRequest(admin, "PUT", "/api/orchestrator/v1/tasks/shop-catalog", () =>
    admin.getByRole("button", { name: "Зберегти", exact: true }).click(),
  );
  expect(
    (body["stages"] as TaskConfig["stages"]).find((s) => s.stage_id === "extract-products")?.params,
  ).toEqual({ items: [1, 9.5] });
});

test("property names and actions stay on one row with accessible parameter help @mock", async ({ admin }) => {
  await admin.setViewportSize({ width: 1360, height: 1000 });
  await admin.goto("/tasks/shop-catalog");
  await admin.getByRole("tab", { name: "Ланцюжок" }).click();
  await admin.getByTestId("dag-node-collect").click();
  const grid = admin.getByRole("table", { name: "Властивості", exact: true });
  const toggle = await grid.getByLabel("Розгорнути $.collector", { exact: true }).boundingBox();
  const name = await grid.getByLabel("Назва $.collector", { exact: true }).boundingBox();
  expect(toggle).not.toBeNull();
  expect(name).not.toBeNull();
  expect(Math.abs(toggle!.y + toggle!.height / 2 - name!.y - name!.height / 2)).toBeLessThan(2);
  expect(toggle!.x + toggle!.width).toBeLessThanOrEqual(name!.x);
  const value = await grid.getByLabel("Значення $.collector.mode", { exact: true }).boundingBox();
  const remove = await grid.getByLabel("Видалити $.collector.mode", { exact: true }).boundingBox();
  expect(value).not.toBeNull();
  expect(remove).not.toBeNull();
  expect(Math.abs(value!.y + value!.height / 2 - remove!.y - remove!.height / 2)).toBeLessThan(2);
  expect(value!.x + value!.width).toBeLessThanOrEqual(remove!.x);
  await expect(grid.getByLabel("Значення $.collector.mode", { exact: true })).toHaveAccessibleDescription(
    /full.*incremental/,
  );
  await expect(grid.getByRole("columnheader")).toHaveCount(3);
  await admin.setViewportSize({ width: 390, height: 844 });
  expect(await admin.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
  await expect(grid.getByLabel("Значення $.collector.mode", { exact: true })).toHaveValue("full");
});
