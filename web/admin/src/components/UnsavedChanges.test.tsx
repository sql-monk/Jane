import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { StrictMode, useState } from "react";
import { BrowserRouter, Link, Route, Routes, useNavigate } from "react-router-dom";
import { UnsavedChangesProvider, useUnsavedChanges } from "./UnsavedChanges";

beforeEach(() => {
  window.history.replaceState({ idx: 0 }, "", "/start");
  // jsdom lacks the native dialog API. Its DOM, event and focus behavior still run normally.
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute("open", "");
  };
  HTMLDialogElement.prototype.close = function () {
    this.removeAttribute("open");
  };
});
afterEach(cleanup);

function Draft({ save }: { save: () => Promise<boolean> }) {
  const [value, setValue] = useState("");
  const navigate = useNavigate();
  const guard = useUnsavedChanges({
    dirty: Boolean(value),
    label: "Джерело",
    onSave: async () => {
      const ok = await save();
      if (ok) {
        guard.markSaved();
        setValue("");
      }
      return ok;
    },
    onDiscard: () => setValue(""),
  });
  return (
    <>
      <input aria-label="Назва" value={value} onChange={(event) => setValue(event.target.value)} />
      <Link to="/end">Інший розділ</Link>
      <button onClick={() => navigate("/end")}>Програмний перехід</button>
      <button onClick={() => guard.confirmChange(() => setValue(""))}>Змінити контекст</button>
    </>
  );
}
function app(save: () => Promise<boolean>) {
  return render(
    <StrictMode>
      <BrowserRouter>
        <UnsavedChangesProvider>
          <Routes>
            <Route path="/start" element={<Link to="/draft">Редагувати</Link>} />
            <Route path="/draft" element={<Draft save={save} />} />
            <Route path="/end" element={<h1>Інший розділ відкрито</h1>} />
          </Routes>
        </UnsavedChangesProvider>
      </BrowserRouter>
    </StrictMode>,
  );
}

it("keeps drafts on Stay and follows a link only after successful Save", async () => {
  const save = vi.fn(async () => true);
  app(save);
  fireEvent.click(screen.getByRole("link", { name: "Редагувати" }));
  fireEvent.change(await screen.findByLabelText("Назва"), { target: { value: "Чернетка" } });
  fireEvent.click(screen.getByRole("link", { name: "Інший розділ" }));
  expect(await screen.findByRole("dialog", { name: "Незбережені зміни" })).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: "Залишитися" }));
  expect(screen.getByLabelText("Назва")).toHaveValue("Чернетка");
  fireEvent.click(screen.getByRole("button", { name: "Програмний перехід" }));
  fireEvent.click(await screen.findByRole("button", { name: "Зберегти й перейти" }));
  expect(await screen.findByRole("heading", { name: "Інший розділ відкрито" })).toBeVisible();
  expect(save).toHaveBeenCalledOnce();
});

it("restores the original history entry and draft after native Back and Stay", async () => {
  app(async () => true);
  fireEvent.click(screen.getByRole("link", { name: "Редагувати" }));
  fireEvent.change(await screen.findByLabelText("Назва"), { target: { value: "Чернетка" } });
  expect(window.history.state.idx).toBe(1);
  window.history.back();
  expect(await screen.findByRole("dialog", { name: "Незбережені зміни" })).toBeVisible();
  await waitFor(() => expect(window.location.pathname).toBe("/draft"));
  fireEvent.click(screen.getByRole("button", { name: "Залишитися" }));
  expect(screen.getByLabelText("Назва")).toHaveValue("Чернетка");
  window.history.back();
  fireEvent.click(await screen.findByRole("button", { name: "Відкинути й перейти" }));
  expect(await screen.findByRole("link", { name: "Редагувати" })).toBeVisible();
});

it("keeps invalid drafts in their context, and requests native unload confirmation", async () => {
  app(async () => false);
  fireEvent.click(screen.getByRole("link", { name: "Редагувати" }));
  fireEvent.change(await screen.findByLabelText("Назва"), { target: { value: "Чернетка" } });
  const unload = new Event("beforeunload", { cancelable: true });
  window.dispatchEvent(unload);
  expect(unload.defaultPrevented).toBe(true);
  fireEvent.click(screen.getByRole("button", { name: "Змінити контекст" }));
  fireEvent.click(await screen.findByRole("button", { name: "Зберегти й перейти" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("некоректні поля");
  expect(screen.getByLabelText("Назва")).toHaveValue("Чернетка");
});
