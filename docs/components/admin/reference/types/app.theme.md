# Модуль `app.theme`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/app/theme.ts](../../../../../web/admin/src/app/theme.ts). Не редагуйте вручну.

## Функції

### Функція `initializeTheme`

```typescript
function initializeTheme(): void
```

Called before rendering, including the login page. Storage is optional in restricted browsers.

Код: [theme.ts:28](../../../../../web/admin/src/app/theme.ts#L28).

### Функція `setTheme`

```typescript
function setTheme(value: import("C:/repos/Jane/.claude/worktrees/docs/web/admin/src/app/theme").ThemePreference): void
```

Код: [theme.ts:37](../../../../../web/admin/src/app/theme.ts#L37).

### Функція `useTheme`

```typescript
function useTheme(): { preference: import("C:/repos/Jane/.claude/worktrees/docs/web/admin/src/app/theme").ThemePreference; theme: "dark" | "light"; setTheme: (value: import("C:/repos/Jane/.claude/worktrees/docs/web/admin/src/app/theme").ThemePreference) => void; }
```

Код: [theme.ts:67](../../../../../web/admin/src/app/theme.ts#L67).

## Типи

### Тип `ThemePreference`

```typescript
type ThemePreference = "dark" | "light" | "system";
```

Код: [theme.ts:3](../../../../../web/admin/src/app/theme.ts#L3).

## Константи

### Константа `THEME_KEY`

```typescript
const THEME_KEY: "jane.admin.theme"
```

Код: [theme.ts:4](../../../../../web/admin/src/app/theme.ts#L4).
