# Модуль `api.hooks`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/api/hooks.ts](../../../../../web/admin/src/api/hooks.ts). Не редагуйте вручну.

## Функції

### Функція `pollDelay`

```typescript
function pollDelay(attempt: number, polling: { initial_ms: number; max_ms: number; multiplier: number; }): number
```

Delay before the n-th poll: initial * multiplier^n, capped (config.polling).

Код: [hooks.ts:10](../../../../../web/admin/src/api/hooks.ts#L10).

### Функція `useCursorList`

```typescript
function useCursorList<T>(key: readonly unknown[], fetchPage: (cursor: string | undefined, limit: number) => Promise<Page<T>>, refetchWhile?: ((items: T[]) => boolean) | undefined): { items: T[]; isLoading: boolean; error: Error | null; hasMore: boolean; loadMore: () => undefined; loadingMore: boolean; refetch: () => undefined; }
```

Cursor pagination (`?limit=&cursor=` -> `{items, next_cursor}`), page size from config. `refetchWhile` - poll the loaded pages with the job backoff (config.polling) while it holds for the items, e.g. while a listed job runs.

Код: [hooks.ts:26](../../../../../web/admin/src/api/hooks.ts#L26).

### Функція `useJob`

```typescript
function useJob(service: string, client: import("C:/repos/Jane/.claude/worktrees/merge/web/admin/node_modules/.pnpm/openapi-fetch@0.17.0/node_modules/openapi-fetch/dist/index").Client<JobPaths, `${string}/${string}`> | import("C:/repos/Jane/.claude/worktrees/merge/web/admin/node_modules/.pnpm/openapi-fetch@0.17.0/node_modules/openapi-fetch/dist/index").Client<never, `${string}/${string}`>, jobId: string | null | undefined): import("C:/repos/Jane/.claude/worktrees/merge/web/admin/node_modules/.pnpm/@tanstack+react-query@5.104.0_react@19.3.0/node_modules/@tanstack/react-query/build/modern/types").UseQueryResult<{ job_id: string; kind: string; status: "queued" | "running" | "cancelling" | "succeeded" | "failed" | "cancelled"; created_at: string; updated_at?: string; started_at?: string; finished_at?: string; progress?: { completed?: number; total?: number | null; unit?: string; message?: string; counters?: { [x: string]: number; }; updated_at?: string; }; result?: { [x: string]: unknown; }; result_ref?: { kind: "inline"; media_type: string; charset?: string; encoding: "utf-8" | "base64"; data: string; size_bytes?: number; sha256?: string; } | { kind: "blob"; uri: string; download_url?: string; download_url_expires_at?: string; media_type: string; charset?: string; size_bytes: number; sha256: string; store?: "transit" | "persistent"; expires_at?: string | null; }; error?: { type: string; title: string; status: number; detail?: string; instance?: string; code: string; retryable?: boolean; retry_after_seconds?: number; errors?: { pointer?: string; parameter?: string; code?: string; message: string; }[]; trace_id?: string; details?: { [x: string]: unknown; }; }; cancellation?: { requested_at: string; requested_by?: string; reason?: string; }; idempotency_key?: string; links?: { [x: string]: string; }; labels?: { [x: string]: string; }; }, Error>
```

Polls a job with backoff until it reaches a terminal state.

Код: [hooks.ts:69](../../../../../web/admin/src/api/hooks.ts#L69).

## Константи

### Константа `TERMINAL_JOB_STATUSES`

```typescript
const TERMINAL_JOB_STATUSES: Set<string>
```

Код: [hooks.ts:7](../../../../../web/admin/src/api/hooks.ts#L7).
