import { useState, type ReactNode } from "react";
import { ApiError, errorMessage } from "../api/problem";
import { redactSecrets } from "../lib/secrets";

export function Page({
  title,
  actions,
  children,
}: {
  title: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="page">
      <header className="page-header">
        <h1>{title}</h1>
        {actions ? <div className="page-actions">{actions}</div> : null}
      </header>
      {children}
    </section>
  );
}

export function Section({
  title,
  actions,
  children,
}: {
  title: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="section" aria-label={title}>
      <header className="section-header">
        <h2>{title}</h2>
        {actions ? <div className="section-actions">{actions}</div> : null}
      </header>
      {children}
    </section>
  );
}

export function Loading({ what = "Завантаження" }: { what?: string }) {
  return (
    <p className="muted" role="status">
      {what}…
    </p>
  );
}

export function ErrorBox({ error, title }: { error: unknown; title?: string }) {
  if (!error) return null;
  const problem = error instanceof ApiError ? error.problem : null;
  return (
    <div className="error-box" role="alert">
      <strong>{title ?? "Помилка"}</strong>
      <span className="error-message"> {errorMessage(error)}</span>
      {problem ? (
        <span className="muted">
          {" "}
          (<code>{problem.code}</code>, HTTP {problem.status}
          {problem.trace_id ? `, trace ${problem.trace_id}` : ""})
        </span>
      ) : null}
      {problem?.errors?.length ? (
        <ul>
          {problem.errors.map((e, i) => (
            <li key={i}>
              {e.pointer ? <code>{e.pointer}</code> : null} {e.message}
            </li>
          ))}
        </ul>
      ) : null}
      {problem?.details ? <JsonView value={problem.details} compact /> : null}
    </div>
  );
}

const STATUS_TONE: Record<string, string> = {
  succeeded: "ok",
  success: "ok",
  completed: "ok",
  approved: "ok",
  passed: "ok",
  synced: "ok",
  ok: "ok",
  resolved: "ok",
  proposals_ready: "ok",
  running: "info",
  queued: "info",
  leased: "info",
  in_progress: "info",
  pending: "info",
  cancelling: "warn",
  retrying: "warn",
  draft: "info",
  sampling: "info",
  analyzing: "info",
  resolving: "info",
  applying: "info",
  degraded: "warn",
  unrecognized: "warn",
  empty: "muted",
  open: "warn",
  needs_disambiguation: "warn",
  insufficient_sample: "warn",
  unknown: "muted",
  skipped: "muted",
  ignored: "muted",
  deprecated: "muted",
  cancelled: "muted",
  failed: "bad",
  rejected: "bad",
  yanked: "bad",
  down: "bad",
  unresolved: "bad",
};

export function Status({ value }: { value: string | null | undefined }) {
  if (!value) return <span className="muted">—</span>;
  return <span className={`badge badge-${STATUS_TONE[value] ?? "muted"}`}>{value}</span>;
}

/** Pretty JSON of API data; secret-looking values are always masked (ТЗ §11). */
export function JsonView({ value, compact = false }: { value: unknown; compact?: boolean }) {
  return (
    <pre className={compact ? "json json-compact" : "json"} data-testid="json-view">
      {JSON.stringify(redactSecrets(value), null, 2)}
    </pre>
  );
}

export function KeyValue({ rows }: { rows: Array<[string, ReactNode]> }) {
  return (
    <dl className="kv">
      {rows.map(([k, v]) => (
        <div key={k} className="kv-row">
          <dt>{k}</dt>
          <dd>{v ?? "—"}</dd>
        </div>
      ))}
    </dl>
  );
}

export interface Column<T> {
  header: string;
  cell: (row: T) => ReactNode;
  className?: string;
}

export function Table<T>({
  rows,
  columns,
  rowKey,
  empty = "Немає даних",
  label,
}: {
  rows: readonly T[];
  columns: ReadonlyArray<Column<T>>;
  rowKey: (row: T, index: number) => string;
  empty?: string;
  label?: string;
}) {
  if (rows.length === 0) return <p className="muted">{empty}</p>;
  return (
    <div className="table-wrap">
      <table aria-label={label}>
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c.header} className={c.className}>
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={rowKey(row, i)}>
              {columns.map((c) => (
                <td key={c.header} className={c.className}>
                  {c.cell(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function LoadMore({
  hasMore,
  loading,
  onClick,
}: {
  hasMore: boolean;
  loading: boolean;
  onClick: () => void;
}) {
  if (!hasMore) return null;
  return (
    <button type="button" className="btn" onClick={onClick} disabled={loading}>
      {loading ? "Завантаження…" : "Показати ще"}
    </button>
  );
}

export function Tabs<K extends string>({
  tabs,
  active,
  onChange,
}: {
  tabs: ReadonlyArray<[K, string]>;
  active: K;
  onChange: (key: K) => void;
}) {
  return (
    <div className="tabs" role="tablist">
      {tabs.map(([key, label]) => (
        <button
          key={key}
          type="button"
          role="tab"
          aria-selected={key === active}
          className={key === active ? "tab tab-active" : "tab"}
          onClick={() => onChange(key)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}

export function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      {children}
      {hint ? <span className="field-hint">{hint}</span> : null}
    </label>
  );
}

/** A button that asks for a reason (audit) before running a destructive or auditable action. */
export function ReasonAction({
  label,
  confirmLabel,
  onConfirm,
  busy,
  danger = false,
  requireReason = true,
}: {
  label: string;
  confirmLabel?: string;
  onConfirm: (reason: string) => void;
  busy?: boolean;
  danger?: boolean;
  requireReason?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState("");
  if (!open) {
    return (
      <button
        type="button"
        className={danger ? "btn btn-danger" : "btn"}
        onClick={() => setOpen(true)}
        disabled={busy}
      >
        {label}
      </button>
    );
  }
  return (
    <span className="reason-action">
      <input
        aria-label={`Причина: ${label}`}
        placeholder="Причина (для аудиту)"
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        maxLength={1000}
      />
      <button
        type="button"
        className={danger ? "btn btn-danger" : "btn btn-primary"}
        disabled={busy || (requireReason && !reason.trim())}
        onClick={() => {
          onConfirm(reason.trim());
          setOpen(false);
          setReason("");
        }}
      >
        {confirmLabel ?? "Підтвердити"}
      </button>
      <button type="button" className="btn" onClick={() => setOpen(false)}>
        Назад
      </button>
    </span>
  );
}

export function Notice({ tone = "info", children }: { tone?: "info" | "ok" | "warn"; children: ReactNode }) {
  return (
    <div className={`notice notice-${tone}`} role="status">
      {children}
    </div>
  );
}
