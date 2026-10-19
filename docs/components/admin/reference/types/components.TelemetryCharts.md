# Модуль `components.TelemetryCharts`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/components/TelemetryCharts.tsx](../../../../../web/admin/src/components/TelemetryCharts.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `TimeSeriesChart`

```typescript
function TimeSeriesChart({ history, metric, }: { history: { service: string; instance_id: string; sample_interval_seconds: number; retention_seconds: number; resolution_seconds?: number; metrics: { key: string; label: string; unit: string; }[]; samples: { at: string; instance_id: string; values: { [key: string]: number | null; }; }[]; }; metric: { key: string; label: string; unit: string; }; }): React.JSX.Element
```

Код: [TelemetryCharts.tsx:13](../../../../../web/admin/src/components/TelemetryCharts.tsx#L13).

### Компонент `TelemetryCharts`

```typescript
function TelemetryCharts({ module, compact, }: { module: import("C:/repos/Jane/web/admin/src/lib/modules").ModuleDefinition; compact?: boolean; }): React.JSX.Element
```

Код: [TelemetryCharts.tsx:123](../../../../../web/admin/src/components/TelemetryCharts.tsx#L123).
