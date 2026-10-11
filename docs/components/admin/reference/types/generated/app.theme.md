# app/theme

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.app.theme.ThemePreference](#adminappthemethemepreference)
- [admin.app.theme.THEME_KEY](#adminappthemetheme_key)
- [admin.app.theme.initializeTheme](#adminappthemeinitializetheme)
- [admin.app.theme.setTheme](#adminappthemesettheme)
- [admin.app.theme.useTheme](#adminappthemeusetheme)

## admin.app.theme.ThemePreference

**Тип.** Код: [web/admin/src/app/theme.ts:3](../../../../../../web/admin/src/app/theme.ts#L3).

```typescript
export type ThemePreference = "dark" | "light" | "system";
```

## admin.app.theme.THEME_KEY

**Константа.** Код: [web/admin/src/app/theme.ts:4](../../../../../../web/admin/src/app/theme.ts#L4).

```typescript
THEME_KEY: "jane.admin.theme" = "jane.admin.theme"
```

Доступ: читання — так; запис — так.

## admin.app.theme.initializeTheme

**Функція.** Код: [web/admin/src/app/theme.ts:28](../../../../../../web/admin/src/app/theme.ts#L28).

```typescript
function initializeTheme(): void
```

Результат: `void`.

### Опис із вихідного коду

```text
Called before rendering, including the login page. Storage is optional in restricted browsers.
```

## admin.app.theme.setTheme

**Функція.** Код: [web/admin/src/app/theme.ts:37](../../../../../../web/admin/src/app/theme.ts#L37).

```typescript
function setTheme(value: ThemePreference): void
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `ThemePreference` | `—` | required |

Результат: `void`.

## admin.app.theme.useTheme

**Функція.** Код: [web/admin/src/app/theme.ts:67](../../../../../../web/admin/src/app/theme.ts#L67).

```typescript
function useTheme(): { preference: ThemePreference; theme: "dark" | "light"; setTheme: (value: ThemePreference) => void; }
```

Результат: `{ preference: ThemePreference; theme: "dark" | "light"; setTheme: (value: ThemePreference) => void; }`.
