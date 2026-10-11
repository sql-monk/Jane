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
function useCursorList<T>(key: QueryKey, fetchPage: (cursor: string | undefined, limit: number) => Promise<Page<T>>, refetchWhile?: (items: T[]) => boolean): { items: any; isLoading: any; error: any; hasMore: boolean; loadMore: () => undefined; loadingMore: any; refetch: () => undefined; }
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `key` | `QueryKey` | `—` | required |
| `fetchPage` | `(cursor: string \| undefined, limit: number) => Promise<Page<T>>` | `—` | required |
| `refetchWhile` | `((items: T[]) => boolean) \| undefined` | `—` | required |

Результат: `{ items: any; isLoading: any; error: any; hasMore: boolean; loadMore: () => undefined; loadingMore: any; refetch: () => undefined; }`.

### Опис із вихідного коду

```text
Cursor pagination (`?limit=&cursor=` -> `{items, next_cursor}`), page size from config. `refetchWhile` - poll the
loaded pages with the job backoff (config.polling) while it holds for the items, e.g. while a listed job runs.
```

## admin.api.hooks.useJob

**Функція.** Код: [web/admin/src/api/hooks.ts:69](../../../../../../web/admin/src/api/hooks.ts#L69).

```typescript
function useJob(service: string, client: Client<JobPaths> | Client<never>, jobId: string | null | undefined): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `service` | `string` | `—` | required |
| `client` | `any` | `—` | required |
| `jobId` | `string \| null \| undefined` | `—` | required |

Результат: `any`.

### Опис із вихідного коду

```text
Polls a job with backoff until it reaches a terminal state.
```
