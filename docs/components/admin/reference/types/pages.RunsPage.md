# Модуль `pages.RunsPage`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/pages/RunsPage.tsx](../../../../../web/admin/src/pages/RunsPage.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `RunsPage`

```typescript
function RunsPage(): React.JSX.Element
```

Код: [RunsPage.tsx:53](../../../../../web/admin/src/pages/RunsPage.tsx#L53).

### Компонент `RunPage`

```typescript
function RunPage(): React.JSX.Element
```

Код: [RunsPage.tsx:232](../../../../../web/admin/src/pages/RunsPage.tsx#L232).

### Компонент `RunOutcome`

```typescript
function RunOutcome({ run }: { run: { run_id: string; task_id: string; task_etag?: string; source_id?: string; collector_kind?: string; updated_at?: string; summary?: { basis?: string; complete?: boolean; legacy_trace?: boolean; extracted_entities?: number; saved_records?: number; result_groups?: { connection_id?: string; entity_type?: string; scope?: string; count?: number; }[]; }; status: "queued" | "running" | "cancelling" | "succeeded" | "failed" | "cancelled"; trigger: "assistant" | "schedule" | "manual" | "reprocess" | "api"; test_mode?: boolean; created_at: string; started_at?: string; finished_at?: string; collection_id?: string; stages?: { stage_id: string; handler?: { package_id: string; version: string; digest?: string; }; counts?: { [key: string]: number; }; }[]; counters?: { [key: string]: number; }; backpressure?: boolean; costs?: { llm?: { amount: number; currency: string; }; }; error?: { type: string; title: string; status: number; detail?: string; instance?: string; code: string; retryable?: boolean; retry_after_seconds?: number; errors?: { pointer?: string; parameter?: string; code?: string; message: string; }[]; trace_id?: string; details?: Record<string, unknown>; }; }; }): React.JSX.Element
```

Код: [RunsPage.tsx:395](../../../../../web/admin/src/pages/RunsPage.tsx#L395).

## Функції

### Функція `collectorAddress`

```typescript
function collectorAddress(value: string | undefined): string | null
```

Код: [RunsPage.tsx:609](../../../../../web/admin/src/pages/RunsPage.tsx#L609).
