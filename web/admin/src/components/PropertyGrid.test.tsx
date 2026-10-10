import { useState } from "react";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it } from "vitest";
import { PropertyGrid } from "./PropertyGrid";
import type { JsonValue } from "../lib/property";

afterEach(cleanup);
function Harness() {
  const [value, setValue] = useState<JsonValue>({
    params: { items: [null, false, 0, ""], nested: { untouched: [1, { a: true }] } },
  });
  return (
    <>
      <PropertyGrid value={value} onChange={setValue} />
      <output data-testid="json">{JSON.stringify(value)}</output>
    </>
  );
}
it("renders exactly three columns and edits nested JSON without loss", () => {
  render(<Harness />);
  expect(screen.getAllByRole("columnheader").map((h) => h.textContent)).toEqual(["Назва", "Тип", "Значення"]);
  fireEvent.click(screen.getByLabelText("Значення $.params.items[1]"));
  fireEvent.change(screen.getByLabelText("Значення $.params.items[2]"), { target: { value: "2.5" } });
  fireEvent.blur(screen.getByLabelText("Значення $.params.items[2]"));
  fireEvent.click(screen.getByLabelText("Вгору $.params.items[2]"));
  fireEvent.change(screen.getByLabelText("Назва $.params.nested"), { target: { value: "kept" } });
  fireEvent.blur(screen.getByLabelText("Назва $.params.nested"));
  expect(JSON.parse(screen.getByTestId("json").textContent!)).toEqual({
    params: { items: [null, 2.5, true, ""], kept: { untouched: [1, { a: true }] } },
  });
});
it("adds/removes fields and array items, rejects collisions, retains invalid number drafts", () => {
  render(<Harness />);
  fireEvent.click(screen.getByLabelText("Додати $.params.items"));
  expect(JSON.parse(screen.getByTestId("json").textContent!).params.items).toHaveLength(5);
  fireEvent.click(screen.getByLabelText("Видалити $.params.items[4]"));
  fireEvent.click(screen.getByLabelText("Додати $.params"));
  fireEvent.change(screen.getByLabelText("Назва $.params.new_field"), { target: { value: "items" } });
  fireEvent.blur(screen.getByLabelText("Назва $.params.new_field"));
  expect(screen.getByRole("alert")).toHaveTextContent("вже існує");
  fireEvent.click(screen.getByLabelText("Видалити $.params.new_field"));
  fireEvent.change(screen.getByLabelText("Значення $.params.items[2]"), { target: { value: "" } });
  fireEvent.blur(screen.getByLabelText("Значення $.params.items[2]"));
  expect(screen.getByRole("alert")).toHaveTextContent("попереднє значення збережено");
  expect(JSON.parse(screen.getByTestId("json").textContent!).params.items[2]).toBe(0);
});
