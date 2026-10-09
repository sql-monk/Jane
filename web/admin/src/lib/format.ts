import type { Money } from "../api/types";

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date
    .toISOString()
    .replace("T", " ")
    .replace(/\.\d{3}Z$/, "Z");
}

/** Like formatDate, but keeps milliseconds (attempt diagnostics: a retry must start after its backoff). */
export function formatInstant(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toISOString().replace("T", " ");
}

export function formatMoney(money: Money | null | undefined): string {
  if (!money) return "—";
  return `${money.amount
    .toFixed(money.amount < 1 ? 4 : 2)
    .replace(/0+$/, "")
    .replace(/\.$/, "")} ${money.currency}`;
}

export function formatBytes(bytes: number | null | undefined): string {
  if (bytes === null || bytes === undefined) return "—";
  if (bytes < 1024) return `${bytes} B`;
  const units = ["KiB", "MiB", "GiB", "TiB"];
  let value = bytes / 1024;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit += 1;
  }
  return `${value.toFixed(1)} ${units[unit]}`;
}

export function refLabel(ref: { package_id: string; version: string } | null | undefined): string {
  return ref ? `${ref.package_id}@${ref.version}` : "—";
}

/** Next patch/minor/major of an exact SemVer (pre-release and build metadata are dropped). */
export function bumpVersion(version: string, part: "patch" | "minor" | "major" = "patch"): string {
  const match = /^(\d+)\.(\d+)\.(\d+)/.exec(version);
  if (!match) return "0.1.0";
  const [major, minor, patch] = [Number(match[1]), Number(match[2]), Number(match[3])];
  if (part === "major") return `${major + 1}.0.0`;
  if (part === "minor") return `${major}.${minor + 1}.0`;
  return `${major}.${minor}.${patch + 1}`;
}

export const SEMVER_PATTERN =
  /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/;
export const SLUG_PATTERN = /^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$/;
