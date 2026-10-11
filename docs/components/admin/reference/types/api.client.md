# Модуль `api.client`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/api/client.ts](../../../../../web/admin/src/api/client.ts). Не редагуйте вручну.

## Функції

### Функція `createApiClients`

```typescript
function createApiClients(config: import("C:/repos/Jane/.claude/worktrees/docs/web/admin/src/config").AdminConfig, hooks: import("C:/repos/Jane/.claude/worktrees/docs/web/admin/src/api/client").AuthHooks): import("C:/repos/Jane/.claude/worktrees/docs/web/admin/src/api/client").ApiClients
```

Код: [client.ts:50](../../../../../web/admin/src/api/client.ts#L50).

### Функція `unwrap`

```typescript
function unwrap<T>(promise: Promise<FetchResult<T>>): Promise<T>
```

Resolves to the response body or throws ApiError with the problem+json of the service.

Код: [client.ts:103](../../../../../web/admin/src/api/client.ts#L103).

### Функція `unwrapWithEtag`

```typescript
function unwrapWithEtag<T>(promise: Promise<FetchResult<T>>): Promise<{ data: T; etag: string | null; }>
```

Same as unwrap, plus the ETag for a later PUT/PATCH with If-Match.

Код: [client.ts:115](../../../../../web/admin/src/api/client.ts#L115).

### Функція `newIdempotencyKey`

```typescript
function newIdempotencyKey(): string
```

A fresh Idempotency-Key for one user action (retries of that action reuse it).

Код: [client.ts:129](../../../../../web/admin/src/api/client.ts#L129).

### Функція `ifMatch`

```typescript
function ifMatch(etag: string | null | undefined): { "If-Match"?: string; }
```

`If-Match` header object, only when the ETag is known.

Код: [client.ts:134](../../../../../web/admin/src/api/client.ts#L134).

## Інтерфейси

### Інтерфейс `ApiClients`

```typescript
interface ApiClients
```

| Член | Тип | Обов'язковий | Доступ | Опис |
|---|---|---|---|---|
| `orchestrator` | `Client&lt;paths, `${string}/${string}`>` | так | читання й запис |  |
| `registry` | `Client&lt;paths, `${string}/${string}`>` | так | читання й запис |  |
| `storage` | `Client&lt;paths, `${string}/${string}`>` | так | читання й запис |  |
| `llm` | `Client&lt;paths, `${string}/${string}`>` | так | читання й запис |  |
| `handler` | `Client&lt;paths, `${string}/${string}`>` | так | читання й запис |  |
| `assistant` | `Client&lt;paths, `${string}/${string}`>` | так | читання й запис |  |
| `collector` | `Client&lt;paths, `${string}/${string}`>` | так | читання й запис |  |
| `executor` | `(name: string) => Client&lt;paths, `${string}/${string}`>` | так | читання й запис | handler.v1 connection endpoints of a named executor (`/api/<executor>`), from GET /v1/executors. |
| `collectorExecutor` | `(name: string) => Client&lt;paths, `${string}/${string}`>` | так | читання й запис | collector.v1 of a named collector executor. |

Код: [client.ts:14](../../../../../web/admin/src/api/client.ts#L14).

### Інтерфейс `AuthHooks`

```typescript
interface AuthHooks
```

| Член | Тип | Обов'язковий | Доступ | Опис |
|---|---|---|---|---|
| `getToken` | `() => string \| null` | так | читання й запис | Bearer token of the current user (API key in dev, OIDC access token in prod) or null. |
| `onUnauthenticated` | `() => void` | так | читання й запис |  |

Код: [client.ts:28](../../../../../web/admin/src/api/client.ts#L28).
