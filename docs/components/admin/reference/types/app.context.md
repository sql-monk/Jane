# Модуль `app.context`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/app/context.tsx](../../../../../web/admin/src/app/context.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `AppProvider`

```typescript
function AppProvider({ config, children }: { config: import("C:/repos/Jane/.claude/worktrees/merge/web/admin/src/config").AdminConfig; children: React.ReactNode; }): React.JSX.Element
```

Код: [context.tsx:38](../../../../../web/admin/src/app/context.tsx#L38).

## Функції

### Функція `useApi`

```typescript
function useApi(): import("C:/repos/Jane/.claude/worktrees/merge/web/admin/src/api/client").ApiClients
```

Код: [context.tsx:125](../../../../../web/admin/src/app/context.tsx#L125).

### Функція `useConfig`

```typescript
function useConfig(): import("C:/repos/Jane/.claude/worktrees/merge/web/admin/src/config").AdminConfig
```

Код: [context.tsx:126](../../../../../web/admin/src/app/context.tsx#L126).

### Функція `useAuth`

```typescript
function useAuth(): import("C:/repos/Jane/.claude/worktrees/merge/web/admin/src/app/context").AuthState
```

Код: [context.tsx:127](../../../../../web/admin/src/app/context.tsx#L127).

## Інтерфейси

### Інтерфейс `AuthState`

```typescript
interface AuthState
```

| Член | Тип | Обов'язковий | Доступ | Опис |
|---|---|---|---|---|
| `mode` | `"oidc" \| "api_key" \| "none"` | так | читання й запис |  |
| `authenticated` | `boolean` | так | читання й запис |  |
| `expired` | `boolean` | так | читання й запис | A request was rejected with 401: the key/token is wrong or expired. |
| `principal` | `string \| null` | так | читання й запис | Who is signed in (OIDC profile name/email); never the key itself. |
| `loginWithApiKey` | `(key: string) => void` | так | читання й запис |  |
| `loginWithOidc` | `() => Promise&lt;void>` | так | читання й запис |  |
| `completeOidcLogin` | `() => Promise&lt;void>` | так | читання й запис |  |
| `logout` | `() => void` | так | читання й запис |  |

Код: [context.tsx:17](../../../../../web/admin/src/app/context.tsx#L17).
