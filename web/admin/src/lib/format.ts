import type { Money } from "../api/types";

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return `${new Intl.DateTimeFormat("uk-UA", { timeZone: "Europe/Kyiv", dateStyle: "short", timeStyle: "medium" }).format(date)} (Київ)`;
}

/** Like formatDate, but keeps milliseconds (attempt diagnostics: a retry must start after its backoff). */
export function formatInstant(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return `${formatDate(value)} · ${String(date.getMilliseconds()).padStart(3, "0")} мс`;
}

export function formatDuration(start: string | null | undefined, end?: string | null): string {
  if (!start) return "—";
  const elapsed = (end ? Date.parse(end) : Date.now()) - Date.parse(start);
  if (!Number.isFinite(elapsed) || elapsed < 0) return "—";
  const seconds = Math.floor(elapsed / 1000);
  if (seconds < 60) return `${seconds} с`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)} хв ${seconds % 60} с`;
  return `${Math.floor(seconds / 3600)} год ${Math.floor((seconds % 3600) / 60)} хв`;
}

/** datetime-local uses the browser's timezone; transmit an explicit RFC 3339 instant. */
export function inputInstant(value: string): string | undefined {
  if (!value) return undefined;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? undefined : date.toISOString();
}

export const SCOPE_LABELS: Record<string, string> = {
  platform: "Платформа",
  source: "Джерело",
  task: "Завдання",
  stage: "Етап",
  connection: "Підключення",
  limits: "Ліміти",
  problem_group: "Група проблем",
};
export const PERIOD_LABELS: Record<string, string> = {
  run: "за запуск",
  day: "за добу",
  week: "за тиждень",
  month: "за місяць",
  total: "за весь час",
};
const STATUS_LABELS: Record<string, string> = {
  succeeded: "Успішно",
  success: "Успішно",
  completed: "Завершено",
  approved: "Схвалено",
  passed: "Пройдено",
  synced: "Синхронізовано",
  ok: "Гаразд",
  resolved: "Вирішено",
  proposals_ready: "Варіанти готові",
  running: "Виконується",
  queued: "У черзі",
  leased: "Передано виконавцю",
  in_progress: "В обробці",
  pending: "Очікує",
  cancelling: "Скасовується",
  retrying: "Повторна спроба",
  claimed: "Взято в роботу",
  in_progress_parked: "Призупинено",
  retry_scheduled: "Повтор заплановано",
  lease_reclaimed: "Повернуто в чергу",
  draft: "Чернетка",
  sampling: "Збирається вибірка",
  analyzing: "Аналізується",
  resolving: "Вирішується",
  applying: "Застосовується",
  degraded: "Частково доступно",
  unrecognized: "Не розпізнано",
  empty: "Порожньо",
  open: "Відкрита",
  needs_disambiguation: "Потрібне уточнення",
  insufficient_sample: "Недостатня вибірка",
  unknown: "Невідомо",
  skipped: "Пропущено",
  ignored: "Ігноровано",
  deprecated: "Застаріле",
  cancelled: "Скасовано",
  failed: "Помилка",
  rejected: "Відхилено",
  yanked: "Відкликано",
  down: "Недоступно",
  unresolved: "Не вирішено",
  available: "Доступно",
  unavailable: "Недоступно",
  unsupported: "Не підтримується",
};
export function statusLabel(value: string): string {
  return STATUS_LABELS[value] ?? value;
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
