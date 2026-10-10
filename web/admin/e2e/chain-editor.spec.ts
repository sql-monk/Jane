import { captureRequest, expect, test } from "./fixtures";

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
  await grid.getByLabel("Значення $.params.new_field_1", { exact: true }).fill("0");
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
    new_field_1: 0,
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
  await admin.getByLabel("Вихід зв’язку 1").selectOption("input_material");
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
      select: "input_material",
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
