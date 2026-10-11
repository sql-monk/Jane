import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useApi, useConfig } from "../app/context";
import { unwrap } from "../api/client";
import type { ModuleDefinition, ModuleTelemetry } from "../lib/modules";
import { ErrorBox, Loading, Notice } from "./ui";

function number(value: number | null | undefined): string {
  return value == null ? "—" : value.toLocaleString("uk-UA", { maximumFractionDigits: 2 });
}

export function TimeSeriesChart({
  history,
  metric,
}: {
  history: ModuleTelemetry;
  metric: ModuleTelemetry["metrics"][number];
}) {
  const [hover, setHover] = useState<number | null>(null);
  const samples = history.samples;
  const defined = samples.filter((sample) => sample.values[metric.key] != null);
  if (!defined.length)
    return (
      <article className="telemetry-chart telemetry-unavailable">
        <h3>{metric.label}</h3>
        <strong>—</strong>
        <p>Вимірювання недоступне для цього модуля або ще немає даних.</p>
      </article>
    );
  const max = Math.max(1, ...defined.map((sample) => sample.values[metric.key] ?? 0));
  const first = Date.parse(samples[0]?.at ?? "");
  const last = Date.parse(samples.at(-1)?.at ?? "");
  const span = Math.max(1, last - first);
  const points: string[] = [];
  let segment = "";
  let instance = "";
  let previousAt: number | null = null;
  for (const sample of samples) {
    const value = sample.values[metric.key];
    const at = Date.parse(sample.at);
    if (
      value == null ||
      instance !== sample.instance_id ||
      (previousAt !== null && at - previousAt > history.sample_interval_seconds * 3000)
    ) {
      if (segment) points.push(segment);
      segment = "";
    }
    if (value != null)
      segment += `${segment ? " L" : "M"}${(36 + ((at - first) / span) * 584).toFixed(2)},${(150 - (value / max) * 124).toFixed(2)}`;
    instance = sample.instance_id;
    previousAt = at;
  }
  if (segment) points.push(segment);
  const selected = hover === null ? samples.at(-1) : samples[hover];
  return (
    <article className="telemetry-chart">
      <div className="telemetry-chart-title">
        <h3>{metric.label}</h3>
        <strong>
          {number(selected?.values[metric.key])}
          <small>{metric.unit}</small>
        </strong>
      </div>
      <svg
        role="img"
        aria-label={`${metric.label}, ${metric.unit}`}
        viewBox="0 0 640 192"
        onMouseLeave={() => setHover(null)}
        onMouseMove={(event) => {
          const bounds = event.currentTarget.getBoundingClientRect();
          const at =
            first +
            Math.max(0, Math.min(1, (((event.clientX - bounds.left) / bounds.width) * 640 - 36) / 584)) *
              span;
          const index = samples.reduce(
            (best, sample, i) =>
              Math.abs(Date.parse(sample.at) - at) < Math.abs(Date.parse(samples[best]?.at ?? "") - at)
                ? i
                : best,
            0,
          );
          setHover(index);
        }}
      >
        {[0, 0.5, 1].map((fraction) => (
          <g key={fraction}>
            <line
              x1="36"
              x2="620"
              y1={150 - fraction * 124}
              y2={150 - fraction * 124}
              className="telemetry-gridline"
            />
            <text x="32" y={154 - fraction * 124} textAnchor="end">
              {number(max * fraction)}
            </text>
          </g>
        ))}
        {points.map((path, i) => (
          <path key={i} d={path} className="telemetry-line" />
        ))}
        {defined.length === 1 ? (
          <circle
            cx="36"
            cy={150 - ((defined[0]?.values[metric.key] ?? 0) / max) * 124}
            r="3"
            className="telemetry-point"
          />
        ) : null}
        <text x="36" y="181">
          {new Date(first).toLocaleTimeString("uk-UA")}
        </text>
        <text x="620" y="181" textAnchor="end">
          {new Date(last).toLocaleTimeString("uk-UA")}
        </text>
      </svg>
      <small className="muted">{selected ? new Date(selected.at).toLocaleString("uk-UA") : ""}</small>
    </article>
  );
}

export function TelemetryCharts({
  module,
  compact = false,
}: {
  module: ModuleDefinition;
  compact?: boolean;
}) {
  const api = useApi();
  const config = useConfig();
  const [minutes, setMinutes] = useState(config.monitoring.default_window_minutes);
  const [automatic, setAutomatic] = useState(true);
  const query = useQuery({
    queryKey: ["telemetry", module.executor, minutes],
    queryFn: () =>
      unwrap(
        api
          .module(module.executor)
          .GET("/v1/telemetry", {
            params: {
              query: {
                since: new Date(Date.now() - minutes * 60000).toISOString(),
                limit: config.monitoring.max_points,
              },
            },
          }),
      ),
    refetchInterval: automatic ? config.monitoring.refresh_interval_ms : false,
  });
  const history = query.data;
  const latest = history?.samples.at(-1);
  const stale =
    latest &&
    Date.now() - Date.parse(latest.at) >
      Math.max(config.monitoring.stale_after_ms, (history?.sample_interval_seconds ?? 5) * 3000);
  const meaningful =
    history?.metrics.filter(
      (metric) =>
        metric.key.startsWith("http_") || history.samples.some((sample) => sample.values[metric.key] != null),
    ) ?? [];
  const featured = compact
    ? meaningful.filter((metric) =>
        ["queue_depth", "oldest_queued_seconds", "materials_per_second", "stage_items_per_second"].includes(
          metric.key,
        ),
      )
    : meaningful;
  return (
    <div className="telemetry-panel">
      <div className="telemetry-toolbar">
        <label>
          Період
          <select
            aria-label="Період моніторингу"
            value={minutes}
            onChange={(event) => setMinutes(Number(event.target.value))}
          >
            <option value={15}>15 хвилин</option>
            <option value={60}>1 година</option>
            <option value={360}>6 годин</option>
            <option value={1440}>24 години</option>
          </select>
        </label>
        <label>
          <input
            type="checkbox"
            checked={automatic}
            onChange={(event) => setAutomatic(event.target.checked)}
          />{" "}
          Автооновлення
        </label>
        <button
          type="button"
          className="btn btn-small"
          onClick={() => void query.refetch()}
          disabled={query.isFetching}
        >
          Оновити
        </button>
        {latest ? (
          <span className={stale || query.isError ? "telemetry-stale" : "muted"}>
            Останнє вимірювання: {new Date(latest.at).toLocaleTimeString("uk-UA")}
            {stale ? " · дані застаріли" : ""}
          </span>
        ) : null}
      </div>
      <ErrorBox error={query.error} title="Моніторинг недоступний" />
      {query.isLoading ? <Loading /> : null}
      {history && !history.samples.length ? (
        <Notice>
          Модуль збирає історію. Перші вимірювання з’являться після запуску; частота — кожні{" "}
          {history.sample_interval_seconds} с.
        </Notice>
      ) : null}
      {history ? (
        <>
          <div className="telemetry-grid">
            {(compact && !featured.length ? meaningful.slice(0, 4) : featured).map((metric) => (
              <TimeSeriesChart key={metric.key} history={history} metric={metric} />
            ))}
          </div>
          <p className="muted telemetry-footnote">
            Історія зберігається модулем {Math.round(history.retention_seconds / 3600)} год. Пауза
            автооновлення зупиняє лише перегляд. Пропуски вимірювань і перезапуски розривають лінію графіка.
            Середній час показано лише для інтервалів із запитами.
          </p>
        </>
      ) : null}
      {compact ? (
        <Link to={`/modules/${module.id}?tab=monitoring`}>
          Моніторинг {module.name.toLocaleLowerCase("uk")} →
        </Link>
      ) : null}
    </div>
  );
}
