# api/client

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.api.client.ApiClients](#adminapiclientapiclients)
- [admin.api.client.ApiClients.orchestrator](#adminapiclientapiclientsorchestrator)
- [admin.api.client.ApiClients.registry](#adminapiclientapiclientsregistry)
- [admin.api.client.ApiClients.storage](#adminapiclientapiclientsstorage)
- [admin.api.client.ApiClients.llm](#adminapiclientapiclientsllm)
- [admin.api.client.ApiClients.handler](#adminapiclientapiclientshandler)
- [admin.api.client.ApiClients.assistant](#adminapiclientapiclientsassistant)
- [admin.api.client.ApiClients.collector](#adminapiclientapiclientscollector)
- [admin.api.client.ApiClients.executor](#adminapiclientapiclientsexecutor)
- [admin.api.client.ApiClients.collectorExecutor](#adminapiclientapiclientscollectorexecutor)
- [admin.api.client.AuthHooks](#adminapiclientauthhooks)
- [admin.api.client.AuthHooks.getToken](#adminapiclientauthhooksgettoken)
- [admin.api.client.AuthHooks.onUnauthenticated](#adminapiclientauthhooksonunauthenticated)
- [admin.api.client.createApiClients](#adminapiclientcreateapiclients)
- [admin.api.client.unwrap](#adminapiclientunwrap)
- [admin.api.client.unwrapWithEtag](#adminapiclientunwrapwithetag)
- [admin.api.client.newIdempotencyKey](#adminapiclientnewidempotencykey)
- [admin.api.client.ifMatch](#adminapiclientifmatch)

## admin.api.client.ApiClients

**Інтерфейс.** Код: [web/admin/src/api/client.ts:14](../../../../../../web/admin/src/api/client.ts#L14).

```typescript
interface ApiClients {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [orchestrator](api.client.md#adminapiclientapiclientsorchestrator) | Поле | ні |
| [registry](api.client.md#adminapiclientapiclientsregistry) | Поле | ні |
| [storage](api.client.md#adminapiclientapiclientsstorage) | Поле | ні |
| [llm](api.client.md#adminapiclientapiclientsllm) | Поле | ні |
| [handler](api.client.md#adminapiclientapiclientshandler) | Поле | ні |
| [assistant](api.client.md#adminapiclientapiclientsassistant) | Поле | ні |
| [collector](api.client.md#adminapiclientapiclientscollector) | Поле | ні |
| [executor](api.client.md#adminapiclientapiclientsexecutor) | Поле | ні |
| [collectorExecutor](api.client.md#adminapiclientapiclientscollectorexecutor) | Поле | ні |

## admin.api.client.ApiClients.orchestrator

**Поле.** Код: [web/admin/src/api/client.ts:15](../../../../../../web/admin/src/api/client.ts#L15).

```typescript
orchestrator: Client<OrchestratorPaths>
```

Доступ: читання — так; запис — так.

## admin.api.client.ApiClients.registry

**Поле.** Код: [web/admin/src/api/client.ts:16](../../../../../../web/admin/src/api/client.ts#L16).

```typescript
registry: Client<RegistryPaths>
```

Доступ: читання — так; запис — так.

## admin.api.client.ApiClients.storage

**Поле.** Код: [web/admin/src/api/client.ts:17](../../../../../../web/admin/src/api/client.ts#L17).

```typescript
storage: Client<StoragePaths>
```

Доступ: читання — так; запис — так.

## admin.api.client.ApiClients.llm

**Поле.** Код: [web/admin/src/api/client.ts:18](../../../../../../web/admin/src/api/client.ts#L18).

```typescript
llm: Client<LlmPaths>
```

Доступ: читання — так; запис — так.

## admin.api.client.ApiClients.handler

**Поле.** Код: [web/admin/src/api/client.ts:19](../../../../../../web/admin/src/api/client.ts#L19).

```typescript
handler: Client<HandlerPaths>
```

Доступ: читання — так; запис — так.

## admin.api.client.ApiClients.assistant

**Поле.** Код: [web/admin/src/api/client.ts:20](../../../../../../web/admin/src/api/client.ts#L20).

```typescript
assistant: Client<AssistantPaths>
```

Доступ: читання — так; запис — так.

## admin.api.client.ApiClients.collector

**Поле.** Код: [web/admin/src/api/client.ts:21](../../../../../../web/admin/src/api/client.ts#L21).

```typescript
collector: Client<CollectorPaths>
```

Доступ: читання — так; запис — так.

## admin.api.client.ApiClients.executor

**Поле.** Код: [web/admin/src/api/client.ts:23](../../../../../../web/admin/src/api/client.ts#L23).

```typescript
executor: (name: string) => Client<HandlerPaths>
```

Сигнатури виклику:

```typescript
executor(name: string): Client<HandlerPaths>
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `name` | `string` | `—` | required |

Результат: `Client<HandlerPaths>`.

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
handler.v1 connection endpoints of a named executor (`/api/<executor>`), from GET /v1/executors.
```

## admin.api.client.ApiClients.collectorExecutor

**Поле.** Код: [web/admin/src/api/client.ts:25](../../../../../../web/admin/src/api/client.ts#L25).

```typescript
collectorExecutor: (name: string) => Client<CollectorPaths>
```

Сигнатури виклику:

```typescript
collectorExecutor(name: string): Client<CollectorPaths>
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `name` | `string` | `—` | required |

Результат: `Client<CollectorPaths>`.

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
collector.v1 of a named collector executor.
```

## admin.api.client.AuthHooks

**Інтерфейс.** Код: [web/admin/src/api/client.ts:28](../../../../../../web/admin/src/api/client.ts#L28).

```typescript
interface AuthHooks {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [getToken](api.client.md#adminapiclientauthhooksgettoken) | Поле | ні |
| [onUnauthenticated](api.client.md#adminapiclientauthhooksonunauthenticated) | Поле | ні |

## admin.api.client.AuthHooks.getToken

**Поле.** Код: [web/admin/src/api/client.ts:30](../../../../../../web/admin/src/api/client.ts#L30).

```typescript
getToken: () => string | null
```

Сигнатури виклику:

```typescript
getToken(): string | null
```

Результат: `string | null`.

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Bearer token of the current user (API key in dev, OIDC access token in prod) or null.
```

## admin.api.client.AuthHooks.onUnauthenticated

**Поле.** Код: [web/admin/src/api/client.ts:31](../../../../../../web/admin/src/api/client.ts#L31).

```typescript
onUnauthenticated: () => void
```

Сигнатури виклику:

```typescript
onUnauthenticated(): void
```

Результат: `void`.

Доступ: читання — так; запис — так.

## admin.api.client.createApiClients

**Функція.** Код: [web/admin/src/api/client.ts:50](../../../../../../web/admin/src/api/client.ts#L50).

```typescript
function createApiClients(config: AdminConfig, hooks: AuthHooks): ApiClients
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `config` | `AdminConfig` | `—` | required |
| `hooks` | `AuthHooks` | `—` | required |

Результат: `ApiClients`.

## admin.api.client.unwrap

**Функція.** Код: [web/admin/src/api/client.ts:103](../../../../../../web/admin/src/api/client.ts#L103).

```typescript
function unwrap<T>(promise: Promise<FetchResult<T>>): Promise<T>
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `promise` | `Promise<FetchResult<T>>` | `—` | required |

Результат: `Promise<T>`.

### Опис із вихідного коду

```text
Resolves to the response body or throws ApiError with the problem+json of the service.
```

## admin.api.client.unwrapWithEtag

**Функція.** Код: [web/admin/src/api/client.ts:115](../../../../../../web/admin/src/api/client.ts#L115).

```typescript
function unwrapWithEtag<T>(promise: Promise<FetchResult<T>>): Promise<{ data: T; etag: string | null; }>
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `promise` | `Promise<FetchResult<T>>` | `—` | required |

Результат: `Promise<{ data: T; etag: string | null; }>`.

### Опис із вихідного коду

```text
Same as unwrap, plus the ETag for a later PUT/PATCH with If-Match.
```

## admin.api.client.newIdempotencyKey

**Функція.** Код: [web/admin/src/api/client.ts:129](../../../../../../web/admin/src/api/client.ts#L129).

```typescript
function newIdempotencyKey(): string
```

Результат: `string`.

### Опис із вихідного коду

```text
A fresh Idempotency-Key for one user action (retries of that action reuse it).
```

## admin.api.client.ifMatch

**Функція.** Код: [web/admin/src/api/client.ts:134](../../../../../../web/admin/src/api/client.ts#L134).

```typescript
function ifMatch(etag: string | null | undefined): { "If-Match"?: string; }
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `etag` | `string \| null \| undefined` | `—` | required |

Результат: `{ "If-Match"?: string; }`.

### Опис із вихідного коду

```text
`If-Match` header object, only when the ETag is known.
```
