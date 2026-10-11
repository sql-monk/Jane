# config

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.config.ServiceKey](#adminconfigservicekey)
- [admin.config.AuthConfig](#adminconfigauthconfig)
- [admin.config.PollingConfig](#adminconfigpollingconfig)
- [admin.config.PollingConfig.initial_ms](#adminconfigpollingconfiginitial_ms)
- [admin.config.PollingConfig.max_ms](#adminconfigpollingconfigmax_ms)
- [admin.config.PollingConfig.multiplier](#adminconfigpollingconfigmultiplier)
- [admin.config.AdminConfig](#adminconfigadminconfig)
- [admin.config.AdminConfig.api_base](#adminconfigadminconfigapi_base)
- [admin.config.AdminConfig.services](#adminconfigadminconfigservices)
- [admin.config.AdminConfig.auth](#adminconfigadminconfigauth)
- [admin.config.AdminConfig.polling](#adminconfigadminconfigpolling)
- [admin.config.AdminConfig.page_size](#adminconfigadminconfigpage_size)
- [admin.config.AdminConfig.preview_max_bytes](#adminconfigadminconfigpreview_max_bytes)
- [admin.config.DEFAULT_CONFIG](#adminconfigdefault_config)
- [admin.config.parseConfig](#adminconfigparseconfig)
- [admin.config.loadConfig](#adminconfigloadconfig)
- [admin.config.serviceBaseUrl](#adminconfigservicebaseurl)
- [admin.config.absoluteUrl](#adminconfigabsoluteurl)

## admin.config.ServiceKey

**Тип.** Код: [web/admin/src/config.ts:4](../../../../../../web/admin/src/config.ts#L4).

```typescript
export type ServiceKey =
  "orchestrator" | "registry" | "storage" | "llm" | "handler" | "assistant" | "collector";
```

## admin.config.AuthConfig

**Тип.** Код: [web/admin/src/config.ts:7](../../../../../../web/admin/src/config.ts#L7).

```typescript
export type AuthConfig =
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

## admin.config.PollingConfig

**Інтерфейс.** Код: [web/admin/src/config.ts:19](../../../../../../web/admin/src/config.ts#L19).

```typescript
interface PollingConfig {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [initial_ms](config.md#adminconfigpollingconfiginitial_ms) | Поле | ні |
| [max_ms](config.md#adminconfigpollingconfigmax_ms) | Поле | ні |
| [multiplier](config.md#adminconfigpollingconfigmultiplier) | Поле | ні |

## admin.config.PollingConfig.initial_ms

**Поле.** Код: [web/admin/src/config.ts:21](../../../../../../web/admin/src/config.ts#L21).

```typescript
initial_ms: number
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
First delay between job polls, ms.
```

## admin.config.PollingConfig.max_ms

**Поле.** Код: [web/admin/src/config.ts:23](../../../../../../web/admin/src/config.ts#L23).

```typescript
max_ms: number
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Upper bound of the backoff, ms.
```

## admin.config.PollingConfig.multiplier

**Поле.** Код: [web/admin/src/config.ts:25](../../../../../../web/admin/src/config.ts#L25).

```typescript
multiplier: number
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Backoff multiplier (>= 1).
```

## admin.config.AdminConfig

**Інтерфейс.** Код: [web/admin/src/config.ts:28](../../../../../../web/admin/src/config.ts#L28).

```typescript
interface AdminConfig {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [api_base](config.md#adminconfigadminconfigapi_base) | Поле | ні |
| [services](config.md#adminconfigadminconfigservices) | Поле | ні |
| [auth](config.md#adminconfigadminconfigauth) | Поле | ні |
| [polling](config.md#adminconfigadminconfigpolling) | Поле | ні |
| [page_size](config.md#adminconfigadminconfigpage_size) | Поле | ні |
| [preview_max_bytes](config.md#adminconfigadminconfigpreview_max_bytes) | Поле | ні |

## admin.config.AdminConfig.api_base

**Поле.** Код: [web/admin/src/config.ts:30](../../../../../../web/admin/src/config.ts#L30).

```typescript
api_base: string
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Prefix of the reverse proxy: `<api_base>/<service>/v1/...` (ADR-0005). May be absolute (https://jane.example/api).
```

## admin.config.AdminConfig.services

**Поле.** Код: [web/admin/src/config.ts:32](../../../../../../web/admin/src/config.ts#L32).

```typescript
services: Record<ServiceKey, string>
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Reverse-proxy service name for every contract.
```

## admin.config.AdminConfig.auth

**Поле.** Код: [web/admin/src/config.ts:33](../../../../../../web/admin/src/config.ts#L33).

```typescript
auth: AuthConfig
```

Доступ: читання — так; запис — так.

## admin.config.AdminConfig.polling

**Поле.** Код: [web/admin/src/config.ts:34](../../../../../../web/admin/src/config.ts#L34).

```typescript
polling: PollingConfig
```

Доступ: читання — так; запис — так.

## admin.config.AdminConfig.page_size

**Поле.** Код: [web/admin/src/config.ts:36](../../../../../../web/admin/src/config.ts#L36).

```typescript
page_size: number
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Default `limit` of list requests (the service clamps it to its own maximum).
```

## admin.config.AdminConfig.preview_max_bytes

**Поле.** Код: [web/admin/src/config.ts:38](../../../../../../web/admin/src/config.ts#L38).

```typescript
preview_max_bytes: number
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
How many bytes of a stored object to fetch for the preview (HTTP Range).
```

## admin.config.DEFAULT_CONFIG

**Константа.** Код: [web/admin/src/config.ts:41](../../../../../../web/admin/src/config.ts#L41).

```typescript
DEFAULT_CONFIG: AdminConfig = {
  api_base: "/api",
  services: {
    orchestrator: "orchestrator",
    registry: "registry",
    storage: "storage",
    llm: "llm",
    handler: "handler-runtime",
    assistant: "assistant",
    collector: "web-collector",
  },
  auth: { mode: "api_key" },
  polling: { initial_ms: 1000, max_ms: 15000, multiplier: 1.5 },
  page_size: 50,
  preview_max_bytes: 262144,
}
```

Доступ: читання — так; запис — так.

## admin.config.parseConfig

**Функція.** Код: [web/admin/src/config.ts:67](../../../../../../web/admin/src/config.ts#L67).

```typescript
function parseConfig(raw: unknown): AdminConfig
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `raw` | `unknown` | `—` | required |

Результат: `AdminConfig`.

### Опис із вихідного коду

```text
Merges a raw config document over the defaults, rejecting malformed values instead of trusting them.
```

## admin.config.loadConfig

**Функція.** Код: [web/admin/src/config.ts:119](../../../../../../web/admin/src/config.ts#L119).

```typescript
function loadConfig(fetchImpl?: typeof fetch): Promise<AdminConfig>
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `fetchImpl` | `(input: RequestInfo \| URL, init?: RequestInit) => Promise<Response>` | `fetch` | required |

Результат: `Promise<AdminConfig>`.

## admin.config.serviceBaseUrl

**Функція.** Код: [web/admin/src/config.ts:125](../../../../../../web/admin/src/config.ts#L125).

```typescript
function serviceBaseUrl(config: AdminConfig, service: ServiceKey | { executor: string; }): string
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `config` | `AdminConfig` | `—` | required |
| `service` | `ServiceKey \| { executor: string; }` | `—` | required |

Результат: `string`.

## admin.config.absoluteUrl

**Функція.** Код: [web/admin/src/config.ts:131](../../../../../../web/admin/src/config.ts#L131).

```typescript
function absoluteUrl(base: string, origin?: string): string
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `base` | `string` | `—` | required |
| `origin` | `string` | `globalThis.location?.origin ?? "http://localhost"` | required |

Результат: `string`.

### Опис із вихідного коду

```text
Absolute form of a base URL (relative prefixes are resolved against the page origin).
```
