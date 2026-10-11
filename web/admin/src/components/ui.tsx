import {
  Children,
  cloneElement,
  isValidElement,
  useEffect,
  useId,
  useRef,
  useState,
  type ReactElement,
  type ReactNode,
} from "react";
import { createPortal } from "react-dom";
import { ApiError, errorMessage, safeProblemCode, problemFrom } from "../api/problem";
import { statusLabel } from "../lib/format";
import { redactSecrets } from "../lib/secrets";
import { useLocation } from "react-router-dom";
import { navigationFor } from "../lib/navigation";

export function Page({
  title,
  actions,
  children,
}: {
  title: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  const location = useLocation();
  const description = navigationFor(location.pathname)?.description;
  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h1>{title}</h1>
          {description ? <p className="page-description">{description}</p> : null}
        </div>
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
  const problem = problemFrom(error);
  const httpStatus =
    error instanceof ApiError && Number.isInteger(error.status) && error.status >= 400 && error.status <= 599
      ? error.status
      : problem?.status && problem.status >= 400 && problem.status <= 599
        ? problem.status
        : null;
  return (
    <div className="error-box" role="alert">
      <strong>{title ?? "Помилка"}</strong>
      <span className="error-message"> {errorMessage(error)}</span>
      {problem ? (
        <span className="muted">
          {" "}
          (<code>{safeProblemCode(problem.code)}</code>
          {httpStatus ? `, HTTP ${httpStatus}` : ""})
          {typeof problem.retryable === "boolean"
            ? problem.retryable
              ? " · Можна повторити"
              : " · Спершу виправте причину"
            : ""}
        </span>
      ) : null}
      {problem?.trace_id && /^[a-f0-9]{32}$/.test(problem.trace_id) ? (
        <small className="muted">
          Ідентифікатор діагностики: <code>{problem.trace_id}</code>
        </small>
      ) : null}
    </div>
  );
}

const STATUS_TONE: Record<string, string> = {
  available: "ok",
  unavailable: "bad",
  unsupported: "muted",
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
  claimed: "info",
  in_progress_parked: "info",
  retry_scheduled: "warn",
  lease_reclaimed: "warn",
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
  return (
    <span className={`badge badge-${STATUS_TONE[value] ?? "muted"}`} title={value} data-status={value}>
      {statusLabel(value)}
    </span>
  );
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

function TableValue({ value }: { value: ReactNode }) {
  return typeof value === "string" || typeof value === "number" ? (
    <span className="table-value" title={String(value)}>
      {value}
    </span>
  ) : (
    value
  );
}

export function Table<T>({
  rows,
  columns,
  rowKey,
  empty = "Немає даних",
  label,
  loading = false,
  error,
}: {
  rows: readonly T[];
  columns: ReadonlyArray<Column<T>>;
  rowKey: (row: T, index: number) => string;
  empty?: string;
  label?: string;
  loading?: boolean;
  error?: unknown;
}) {
  if (rows.length === 0 && loading) return <Loading />;
  if (rows.length === 0 && error) return null;
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
                <td key={c.header} className={c.className} data-label={c.header}>
                  <TableValue value={c.cell(row)} />
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

export function Field({
  label,
  hint,
  error,
  children,
}: {
  label: string;
  hint?: string;
  error?: string | undefined;
  children: ReactNode;
}) {
  const id = useId();
  let controlId: string | undefined;
  let controlCount = 0;
  const decorate = (nodes: ReactNode): ReactNode =>
    Children.map(nodes, (child) => {
      if (
        !isValidElement(child) ||
        typeof child.type !== "string" ||
        !["input", "select", "textarea"].includes(child.type)
      )
        return isValidElement(child) && typeof child.type === "string"
          ? cloneElement(child as ReactElement<{ children?: ReactNode }>, {
              children: decorate((child.props as { children?: ReactNode }).children),
            })
          : child;
      const control = child as ReactElement<{
        id?: string;
        "aria-describedby"?: string;
        "aria-invalid"?: boolean;
      }>;
      const assignedId = control.props.id ?? (controlCount ? `${id}-${controlCount}` : id);
      controlCount += 1;
      controlId ??= assignedId;
      return cloneElement(control, {
        id: assignedId,
        ...(hint || error
          ? {
              "aria-describedby": [
                control.props["aria-describedby"],
                hint ? `${id}-hint` : null,
                error ? `${id}-error` : null,
              ]
                .filter(Boolean)
                .join(" "),
            }
          : {}),
        ...(error ? { "aria-invalid": true } : {}),
      });
    });
  const controls = decorate(children);
  return (
    <div className="field">
      {controlId ? (
        <label className="field-label" htmlFor={controlId}>
          {label}
        </label>
      ) : (
        <span className="field-label">{label}</span>
      )}
      {controls}
      {hint ? (
        <span className="field-hint" id={`${id}-hint`}>
          {hint}
        </span>
      ) : null}
      {error ? (
        <span className="error-inline" id={`${id}-error`} role="alert">
          {error}
        </span>
      ) : null}
    </div>
  );
}

/** Native modal: focus stays inside it and table rows keep their compact layout. */
export function ActionDialog({
  title,
  onClose,
  children,
}: {
  title: string;
  onClose: () => void;
  children: ReactNode;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const element = dialog.current;
    const previouslyFocused = document.activeElement;
    element?.showModal();
    return () => {
      if (element?.open) element.close();
      if (previouslyFocused instanceof HTMLElement && previouslyFocused.isConnected)
        previouslyFocused.focus();
    };
  }, []);
  return createPortal(
    <dialog
      ref={dialog}
      className="action-dialog"
      aria-label={title}
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
    >
      <h2>{title}</h2>
      {children}
    </dialog>,
    document.body,
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
  modal = true,
  impact,
}: {
  label: string;
  confirmLabel?: string;
  onConfirm: (reason: string) => void;
  busy?: boolean;
  danger?: boolean;
  requireReason?: boolean;
  modal?: boolean;
  impact?: ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState("");
  const trigger = (
    <button
      type="button"
      className={danger ? "btn btn-danger" : "btn"}
      onClick={() => setOpen(true)}
      disabled={busy}
    >
      {label}
    </button>
  );
  if (!open) return trigger;
  const confirmation = (
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
  return modal ? (
    <>
      {trigger}
      <ActionDialog
        title={label}
        onClose={() => {
          if (!busy) setOpen(false);
        }}
      >
        {impact ? <p>{impact}</p> : null}
        {confirmation}
      </ActionDialog>
    </>
  ) : (
    confirmation
  );
}

export function Notice({ tone = "info", children }: { tone?: "info" | "ok" | "warn"; children: ReactNode }) {
  return (
    <div className={`notice notice-${tone}`} role="status">
      {children}
    </div>
  );
}
