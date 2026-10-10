import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ThemeControl } from "../components/ThemeControl";
import { initializeTheme, setTheme, THEME_KEY } from "./theme";

let dark = false;
let mediaListeners: Set<() => void>;
beforeEach(() => {
  localStorage.clear();
  dark = false;
  mediaListeners = new Set();
  vi.stubGlobal(
    "matchMedia",
    vi.fn(() => ({
      get matches() {
        return dark;
      },
      addEventListener: (_: string, listener: () => void) => mediaListeners.add(listener),
      removeEventListener: (_: string, listener: () => void) => mediaListeners.delete(listener),
    })),
  );
  initializeTheme();
});
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  localStorage.clear();
});

describe("workspace themes", () => {
  it("persists only the preference and restores it before rendering", async () => {
    render(<ThemeControl />);
    await userEvent.selectOptions(screen.getByLabelText("Тема оформлення"), "dark");
    expect(document.documentElement.dataset["theme"]).toBe("dark");
    expect({ ...localStorage }).toEqual({ [THEME_KEY]: "dark" });
    initializeTheme();
    expect(document.documentElement.dataset["theme"]).toBe("dark");
  });
  it("follows system changes until an explicit preference overrides them", () => {
    render(<ThemeControl />);
    act(() => {
      dark = true;
      mediaListeners.forEach((listener) => listener());
    });
    expect(document.documentElement.dataset["theme"]).toBe("dark");
    act(() => setTheme("light"));
    act(() => mediaListeners.forEach((listener) => listener()));
    expect(document.documentElement.dataset["theme"]).toBe("light");
    expect(screen.getByLabelText("Тема оформлення")).toHaveValue("light");
  });
  it("keeps the selector synchronized with another tab and clearing storage", () => {
    render(<ThemeControl />);
    act(() => window.dispatchEvent(new StorageEvent("storage", { key: THEME_KEY, newValue: "dark" })));
    expect(screen.getByLabelText("Тема оформлення")).toHaveValue("dark");
    expect(document.documentElement.dataset["theme"]).toBe("dark");
    act(() => window.dispatchEvent(new StorageEvent("storage", { key: null, newValue: null })));
    expect(screen.getByLabelText("Тема оформлення")).toHaveValue("system");
  });
  it("works when preference storage is denied", async () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new DOMException("denied", "SecurityError");
    });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new DOMException("denied", "SecurityError");
    });
    initializeTheme();
    render(<ThemeControl />);
    await userEvent.selectOptions(screen.getByLabelText("Тема оформлення"), "dark");
    expect(document.documentElement.dataset["theme"]).toBe("dark");
    expect(screen.getByLabelText("Тема оформлення")).toHaveValue("dark");
  });
});
