# api/hooks

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.api.hooks.TERMINAL_JOB_STATUSES](#adminapihooksterminal_job_statuses)
- [admin.api.hooks.pollDelay](#adminapihookspolldelay)
- [admin.api.hooks.useCursorList](#adminapihooksusecursorlist)
- [admin.api.hooks.useJob](#adminapihooksusejob)

## admin.api.hooks.TERMINAL_JOB_STATUSES

**Константа.** Код: [web/admin/src/api/hooks.ts:7](../../../../../../web/admin/src/api/hooks.ts#L7).

```typescript
TERMINAL_JOB_STATUSES: Set<string> = new Set(["succeeded", "failed", "cancelled"])
```

Доступ: читання — так; запис — так.

## admin.api.hooks.pollDelay

**Функція.** Код: [web/admin/src/api/hooks.ts:10](../../../../../../web/admin/src/api/hooks.ts#L10).

```typescript
function pollDelay(attempt: number, polling: { initial_ms: number; max_ms: number; multiplier: number; }): number
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `attempt` | `number` | `—` | required |
| `polling` | `{ initial_ms: number; max_ms: number; multiplier: number; }` | `—` | required |

Результат: `number`.

### Опис із вихідного коду

```text
Delay before the n-th poll: initial * multiplier^n, capped (config.polling).
```

## admin.api.hooks.useCursorList

**Функція.** Код: [web/admin/src/api/hooks.ts:26](../../../../../../web/admin/src/api/hooks.ts#L26).

```typescript
function useCursorList<T>(key: QueryKey, fetchPage: (cursor: string | undefined, limit: number) => Promise<Page<T>>, refetchWhile?: (items: T[]) => boolean): { items: T[]; isLoading: boolean; error: Error | null; hasMore: boolean; loadMore: () => undefined; loadingMore: boolean; refetch: () => undefined; }
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `key` | `readonly unknown[]` | `—` | required |
| `fetchPage` | `(cursor: string \| undefined, limit: number) => Promise<Page<T>>` | `—` | required |
| `refetchWhile` | `((items: T[]) => boolean) \| undefined` | `—` | required |

Результат: `{ items: T[]; isLoading: boolean; error: Error | null; hasMore: boolean; loadMore: () => undefined; loadingMore: boolean; refetch: () => undefined; }`.

### Опис із вихідного коду

```text
Cursor pagination (`?limit=&cursor=` -> `{items, next_cursor}`), page size from config. `refetchWhile` - poll the
loaded pages with the job backoff (config.polling) while it holds for the items, e.g. while a listed job runs.
```

## admin.api.hooks.useJob

**Функція.** Код: [web/admin/src/api/hooks.ts:69](../../../../../../web/admin/src/api/hooks.ts#L69).

```typescript
function useJob(service: string, client: Client<JobPaths> | Client<never>, jobId: string | null | undefined): UseQueryResult<{ job_id: components["schemas"]["Id"]; kind: string; status: components["schemas"]["JobStatus"]; created_at: components["schemas"]["Timestamp"]; updated_at?: components["schemas"]["Timestamp"] | undefined; started_at?: components["schemas"]["Timestamp"] | undefined; finished_at?: components["schemas"]["Timestamp"] | undefined; progress?: { completed?: number | undefined; total?: number | null | undefined; unit?: string | undefined; message?: string | undefined; counters?: { [x: string]: number; } | undefined; updated_at?: components["schemas"]["Timestamp"] | undefined; } | undefined; result?: { [x: string]: unknown; } | undefined; result_ref?: { kind: "inline"; media_type: components["schemas"]["MediaType"]; charset?: string | undefined; encoding: "utf-8" | "base64"; data: string; size_bytes?: number | undefined; sha256?: components["schemas"]["Sha256Hex"] | undefined; } | { kind: "blob"; uri: string; download_url?: string | undefined; download_url_expires_at?: components["schemas"]["Timestamp"] | undefined; media_type: components["schemas"]["MediaType"]; charset?: string | undefined; size_bytes: number; sha256: components["schemas"]["Sha256Hex"]; store?: "transit" | "persistent" | undefined; expires_at?: string | null | undefined; } | undefined; error?: { type: string; title: string; status: number; detail?: string | undefined; instance?: string | undefined; code: string; retryable?: boolean | undefined; retry_after_seconds?: number | undefined; errors?: { pointer?: string | undefined; parameter?: string | undefined; code?: string | undefined; message: string; }[] | undefined; trace_id?: string | undefined; details?: { [x: string]: unknown; } | undefined; } | undefined; cancellation?: { requested_at: components["schemas"]["Timestamp"]; requested_by?: string | undefined; reason?: string | undefined; } | undefined; idempotency_key?: string | undefined; links?: { [x: string]: string; } | undefined; labels?: { [x: string]: string; } | undefined; }, Error>
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `service` | `string` | `—` | required |
| `client` | `Client<JobPaths, `${string}/${string}`> \| Client<never, `${string}/${string}`>` | `—` | required |
| `jobId` | `string \| null \| undefined` | `—` | required |

Результат: `UseQueryResult<{ job_id: components["schemas"]["Id"]; kind: string; status: components["schemas"]["JobStatus"]; created_at: components["schemas"]["Timestamp"]; updated_at?: components["schemas"]["Timestamp"] | undefined; started_at?: components["schemas"]["Timestamp"] | undefined; finished_at?: components["schemas"]["Timestamp"] | undefined; progress?: { completed?: number | undefined; total?: number | null | undefined; unit?: string | undefined; message?: string | undefined; counters?: { [x: string]: number; } | undefined; updated_at?: components["schemas"]["Timestamp"] | undefined; } | undefined; result?: { [x: string]: unknown; } | undefined; result_ref?: { kind: "inline"; media_type: components["schemas"]["MediaType"]; charset?: string | undefined; encoding: "utf-8" | "base64"; data: string; size_bytes?: number | undefined; sha256?: components["schemas"]["Sha256Hex"] | undefined; } | { kind: "blob"; uri: string; download_url?: string | undefined; download_url_expires_at?: components["schemas"]["Timestamp"] | undefined; media_type: components["schemas"]["MediaType"]; charset?: string | undefined; size_bytes: number; sha256: components["schemas"]["Sha256Hex"]; store?: "transit" | "persistent" | undefined; expires_at?: string | null | undefined; } | undefined; error?: { type: string; title: string; status: number; detail?: string | undefined; instance?: string | undefined; code: string; retryable?: boolean | undefined; retry_after_seconds?: number | undefined; errors?: { pointer?: string | undefined; parameter?: string | undefined; code?: string | undefined; message: string; }[] | undefined; trace_id?: string | undefined; details?: { [x: string]: unknown; } | undefined; } | undefined; cancellation?: { requested_at: components["schemas"]["Timestamp"]; requested_by?: string | undefined; reason?: string | undefined; } | undefined; idempotency_key?: string | undefined; links?: { [x: string]: string; } | undefined; labels?: { [x: string]: string; } | undefined; }, Error>`.

### Опис із вихідного коду

```text
Polls a job with backoff until it reaches a terminal state.
```
