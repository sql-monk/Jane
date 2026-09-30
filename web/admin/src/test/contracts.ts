// Test helper: contract examples from contracts/examples (the only source of neighbour data in tests).
// Vitest runs with web/admin as the working directory (vite.config.ts lives there).
import { readFileSync } from "node:fs";
import path from "node:path";

export const REPO_ROOT = path.resolve(process.cwd(), "..", "..");

/** `contracts/examples/openapi/<name>.json` -> its `value`. */
export function openapiExample<T = unknown>(name: string): T {
  const file = path.join(REPO_ROOT, "contracts", "examples", "openapi", `${name}.json`);
  const doc = JSON.parse(readFileSync(file, "utf8")) as { value: T };
  return doc.value;
}
