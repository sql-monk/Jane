# Модуль `config`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/config.ts](../../../../../web/admin/src/config.ts). Не редагуйте вручну.

## Функції

### Функція `parseConfig`

```typescript
function parseConfig(raw: unknown): import("C:/repos/Jane/web/admin/src/config").AdminConfig
```

Merges a raw config document over the defaults, rejecting malformed values instead of trusting them.

Код: [config.ts:81](../../../../../web/admin/src/config.ts#L81).

### Функція `loadConfig`

```typescript
function loadConfig(fetchImpl?: { (input: RequestInfo | URL, init?: RequestInit | undefined): Promise<Response>; (input: string | Request | URL, init?: RequestInit | undefined): Promise<Response>; }): Promise<import("C:/repos/Jane/web/admin/src/config").AdminConfig>
```

Код: [config.ts:153](../../../../../web/admin/src/config.ts#L153).

### Функція `serviceBaseUrl`

```typescript
function serviceBaseUrl(config: import("C:/repos/Jane/web/admin/src/config").AdminConfig, service: import("C:/repos/Jane/web/admin/src/config").ServiceKey | { executor: string; }): string
```

Код: [config.ts:159](../../../../../web/admin/src/config.ts#L159).

### Функція `absoluteUrl`

```typescript
function absoluteUrl(base: string, origin?: string): string
```

Absolute form of a base URL (relative prefixes are resolved against the page origin).

Код: [config.ts:165](../../../../../web/admin/src/config.ts#L165).

## Інтерфейси

### Інтерфейс `PollingConfig`

```typescript
interface PollingConfig
```

| Член | Тип | Обов'язковий | Доступ | Опис |
|---|---|---|---|---|
| `initial_ms` | `number` | так | читання й запис | First delay between job polls, ms. |
| `max_ms` | `number` | так | читання й запис | Upper bound of the backoff, ms. |
| `multiplier` | `number` | так | читання й запис | Backoff multiplier (>= 1). |

Код: [config.ts:19](../../../../../web/admin/src/config.ts#L19).

### Інтерфейс `AdminConfig`

```typescript
interface AdminConfig
```

| Член | Тип | Обов'язковий | Доступ | Опис |
|---|---|---|---|---|
| `module_services` | `Record&lt;string, string>` | так | читання й запис |  |
| `monitoring` | `{ refresh_interval_ms: number; default_window_minutes: number; stale_after_ms: number; max_points: number; }` | так | читання й запис |  |
| `api_base` | `string` | так | читання й запис | Prefix of the reverse proxy: `<api_base>/<service>/v1/...` (ADR-0005). May be absolute (https://jane.example/api). |
| `services` | `Record&lt;ServiceKey, string>` | так | читання й запис | Reverse-proxy service name for every contract. |
| `auth` | `AuthConfig` | так | читання й запис |  |
| `polling` | `PollingConfig` | так | читання й запис |  |
| `page_size` | `number` | так | читання й запис | Default `limit` of list requests (the service clamps it to its own maximum). |
| `preview_max_bytes` | `number` | так | читання й запис | How many bytes of a stored object to fetch for the preview (HTTP Range). |

Код: [config.ts:28](../../../../../web/admin/src/config.ts#L28).

## Типи

### Тип `ServiceKey`

```typescript
type ServiceKey =
  "orchestrator" | "registry" | "storage" | "llm" | "handler" | "assistant" | "collector";
```

Код: [config.ts:4](../../../../../web/admin/src/config.ts#L4).

### Тип `AuthConfig`

```typescript
type AuthConfig =
  | { mode: "api_key" }
  | { mode: "none" }
  | {
      mode: "oidc";
      authority: string;
      client_id: string;
      scope: string;
      redirect_path: string;
      post_logout_redirect_path: string;
    };
```

Код: [config.ts:7](../../../../../web/admin/src/config.ts#L7).

## Константи

### Константа `DEFAULT_CONFIG`

```typescript
const DEFAULT_CONFIG: AdminConfig
```

Код: [config.ts:48](../../../../../web/admin/src/config.ts#L48).
