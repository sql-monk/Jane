# Модуль `pages.AssistantPage`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/pages/AssistantPage.tsx](../../../../../web/admin/src/pages/AssistantPage.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `AssistantPage`

```typescript
function AssistantPage(): React.JSX.Element
```

Код: [AssistantPage.tsx:78](../../../../../web/admin/src/pages/AssistantPage.tsx#L78).

## Функції

### Функція `sessionIdFromJob`

```typescript
function sessionIdFromJob(job: { job_id: string; kind: string; status: "queued" | "running" | "cancelling" | "succeeded" | "failed" | "cancelled"; created_at: string; updated_at?: string; started_at?: string; finished_at?: string; progress?: { completed?: number; total?: number | null; unit?: string; message?: string; counters?: { [key: string]: number; }; updated_at?: string; }; result?: Record<string, unknown>; result_ref?: { kind: "inline"; media_type: string; charset?: string; encoding: "utf-8" | "base64"; data: string; size_bytes?: number; sha256?: string; } | { kind: "blob"; uri: string; download_url?: string; download_url_expires_at?: string; media_type: string; charset?: string; size_bytes: number; sha256: string; store?: "transit" | "persistent"; expires_at?: string | null; }; error?: { type: string; title: string; status: number; detail?: string; instance?: string; code: string; retryable?: boolean; retry_after_seconds?: number; errors?: { pointer?: string; parameter?: string; code?: string; message: string; }[]; trace_id?: string; details?: Record<string, unknown>; }; cancellation?: { requested_at: string; requested_by?: string; reason?: string; }; idempotency_key?: string; links?: { [key: string]: string; }; labels?: { [key: string]: string; }; }): string | null
```

The session of an onboarding Job: `labels.session_id`, or its `links.session` (/v1/onboarding-sessions/{id}).

Код: [AssistantPage.tsx:64](../../../../../web/admin/src/pages/AssistantPage.tsx#L64).
