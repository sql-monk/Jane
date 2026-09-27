// Dev-mode API key storage (ADR-0005 §4): only sessionStorage, never localStorage, never the URL.
const API_KEY_ITEM = "jane.admin.api_key";

function storage(): Storage | null {
  try {
    return window.sessionStorage;
  } catch {
    return null;
  }
}

export function readApiKey(): string | null {
  return storage()?.getItem(API_KEY_ITEM) ?? null;
}

export function writeApiKey(key: string): void {
  storage()?.setItem(API_KEY_ITEM, key);
}

export function clearApiKey(): void {
  storage()?.removeItem(API_KEY_ITEM);
}
