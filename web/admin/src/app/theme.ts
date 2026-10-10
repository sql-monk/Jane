import { useSyncExternalStore } from "react";

export type ThemePreference = "dark" | "light" | "system";
export const THEME_KEY = "jane.admin.theme";
const listeners = new Set<() => void>();
let preference: ThemePreference = "system";

function valid(value: string | null): ThemePreference {
  return value === "dark" || value === "light" ? value : "system";
}

function systemTheme(): "dark" | "light" {
  return typeof window.matchMedia === "function" && window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

function snapshot() {
  return `${preference}:${preference === "system" ? systemTheme() : preference}`;
}

function applyTheme() {
  document.documentElement.dataset["theme"] = preference === "system" ? systemTheme() : preference;
  listeners.forEach((notify) => notify());
}

/** Called before rendering, including the login page. Storage is optional in restricted browsers. */
export function initializeTheme() {
  try {
    preference = valid(window.localStorage.getItem(THEME_KEY));
  } catch {
    preference = "system";
  }
  applyTheme();
}

export function setTheme(value: ThemePreference) {
  preference = value;
  try {
    window.localStorage.setItem(THEME_KEY, value);
  } catch {
    // The selection still works for this session if storage is unavailable.
  }
  applyTheme();
}

function subscribe(notify: () => void) {
  listeners.add(notify);
  const media =
    typeof window.matchMedia === "function" ? window.matchMedia("(prefers-color-scheme: dark)") : null;
  const onSystemChange = () => applyTheme();
  const onStorage = (event: StorageEvent) => {
    if (event.key === THEME_KEY || event.key === null) {
      preference = valid(event.newValue);
      applyTheme();
    }
  };
  media?.addEventListener("change", onSystemChange);
  window.addEventListener("storage", onStorage);
  return () => {
    listeners.delete(notify);
    media?.removeEventListener("change", onSystemChange);
    window.removeEventListener("storage", onStorage);
  };
}

export function useTheme() {
  const value = useSyncExternalStore(subscribe, snapshot);
  const [selected, resolved] = value.split(":");
  return { preference: selected as ThemePreference, theme: resolved as "dark" | "light", setTheme };
}
