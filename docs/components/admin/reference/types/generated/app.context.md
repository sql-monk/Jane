# app/context

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.app.context.AuthState](#adminappcontextauthstate)
- [admin.app.context.AuthState.mode](#adminappcontextauthstatemode)
- [admin.app.context.AuthState.authenticated](#adminappcontextauthstateauthenticated)
- [admin.app.context.AuthState.expired](#adminappcontextauthstateexpired)
- [admin.app.context.AuthState.principal](#adminappcontextauthstateprincipal)
- [admin.app.context.AuthState.loginWithApiKey](#adminappcontextauthstateloginwithapikey)
- [admin.app.context.AuthState.loginWithOidc](#adminappcontextauthstateloginwithoidc)
- [admin.app.context.AuthState.completeOidcLogin](#adminappcontextauthstatecompleteoidclogin)
- [admin.app.context.AuthState.logout](#adminappcontextauthstatelogout)
- [admin.app.context.AppProvider](#adminappcontextappprovider)
- [admin.app.context.useApi](#adminappcontextuseapi)
- [admin.app.context.useConfig](#adminappcontextuseconfig)
- [admin.app.context.useAuth](#adminappcontextuseauth)

## admin.app.context.AuthState

**Інтерфейс.** Код: [web/admin/src/app/context.tsx:17](../../../../../../web/admin/src/app/context.tsx#L17).

```typescript
interface AuthState {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [mode](app.context.md#adminappcontextauthstatemode) | Поле | ні |
| [authenticated](app.context.md#adminappcontextauthstateauthenticated) | Поле | ні |
| [expired](app.context.md#adminappcontextauthstateexpired) | Поле | ні |
| [principal](app.context.md#adminappcontextauthstateprincipal) | Поле | ні |
| [loginWithApiKey](app.context.md#adminappcontextauthstateloginwithapikey) | Поле | ні |
| [loginWithOidc](app.context.md#adminappcontextauthstateloginwithoidc) | Поле | ні |
| [completeOidcLogin](app.context.md#adminappcontextauthstatecompleteoidclogin) | Поле | ні |
| [logout](app.context.md#adminappcontextauthstatelogout) | Поле | ні |

## admin.app.context.AuthState.mode

**Поле.** Код: [web/admin/src/app/context.tsx:18](../../../../../../web/admin/src/app/context.tsx#L18).

```typescript
mode: "api_key" | "none" | "oidc"
```

Доступ: читання — так; запис — так.

## admin.app.context.AuthState.authenticated

**Поле.** Код: [web/admin/src/app/context.tsx:19](../../../../../../web/admin/src/app/context.tsx#L19).

```typescript
authenticated: boolean
```

Доступ: читання — так; запис — так.

## admin.app.context.AuthState.expired

**Поле.** Код: [web/admin/src/app/context.tsx:21](../../../../../../web/admin/src/app/context.tsx#L21).

```typescript
expired: boolean
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
A request was rejected with 401: the key/token is wrong or expired.
```

## admin.app.context.AuthState.principal

**Поле.** Код: [web/admin/src/app/context.tsx:23](../../../../../../web/admin/src/app/context.tsx#L23).

```typescript
principal: string | null
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Who is signed in (OIDC profile name/email); never the key itself.
```

## admin.app.context.AuthState.loginWithApiKey

**Поле.** Код: [web/admin/src/app/context.tsx:24](../../../../../../web/admin/src/app/context.tsx#L24).

```typescript
loginWithApiKey: (key: string) => void
```

Сигнатури виклику:

```typescript
loginWithApiKey(key: string): void
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `key` | `string` | `—` | required |

Результат: `void`.

Доступ: читання — так; запис — так.

## admin.app.context.AuthState.loginWithOidc

**Поле.** Код: [web/admin/src/app/context.tsx:25](../../../../../../web/admin/src/app/context.tsx#L25).

```typescript
loginWithOidc: () => Promise<void>
```

Сигнатури виклику:

```typescript
loginWithOidc(): Promise<void>
```

Результат: `Promise<void>`.

Доступ: читання — так; запис — так.

## admin.app.context.AuthState.completeOidcLogin

**Поле.** Код: [web/admin/src/app/context.tsx:26](../../../../../../web/admin/src/app/context.tsx#L26).

```typescript
completeOidcLogin: () => Promise<void>
```

Сигнатури виклику:

```typescript
completeOidcLogin(): Promise<void>
```

Результат: `Promise<void>`.

Доступ: читання — так; запис — так.

## admin.app.context.AuthState.logout

**Поле.** Код: [web/admin/src/app/context.tsx:27](../../../../../../web/admin/src/app/context.tsx#L27).

```typescript
logout: () => void
```

Сигнатури виклику:

```typescript
logout(): void
```

Результат: `void`.

Доступ: читання — так; запис — так.

## admin.app.context.AppProvider

**Функція.** Код: [web/admin/src/app/context.tsx:38](../../../../../../web/admin/src/app/context.tsx#L38).

```typescript
function AppProvider({ config, children }: { config: AdminConfig; children: ReactNode; }): JSX.Element
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ config: AdminConfig; children: ReactNode; }` | `—` | required |

Результат: `JSX.Element`.

## admin.app.context.useApi

**Змінна.** Код: [web/admin/src/app/context.tsx:125](../../../../../../web/admin/src/app/context.tsx#L125).

```typescript
useApi: () => ApiClients = (): ApiClients => useApp().api
```

Сигнатури виклику:

```typescript
useApi(): ApiClients
```

Результат: `ApiClients`.

Доступ: читання — так; запис — так.

## admin.app.context.useConfig

**Змінна.** Код: [web/admin/src/app/context.tsx:126](../../../../../../web/admin/src/app/context.tsx#L126).

```typescript
useConfig: () => AdminConfig = (): AdminConfig => useApp().config
```

Сигнатури виклику:

```typescript
useConfig(): AdminConfig
```

Результат: `AdminConfig`.

Доступ: читання — так; запис — так.

## admin.app.context.useAuth

**Змінна.** Код: [web/admin/src/app/context.tsx:127](../../../../../../web/admin/src/app/context.tsx#L127).

```typescript
useAuth: () => AuthState = (): AuthState => useApp().auth
```

Сигнатури виклику:

```typescript
useAuth(): AuthState
```

Результат: `AuthState`.

Доступ: читання — так; запис — так.
