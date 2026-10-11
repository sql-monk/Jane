# lib/format

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.lib.format.formatDate](#adminlibformatformatdate)
- [admin.lib.format.formatInstant](#adminlibformatformatinstant)
- [admin.lib.format.formatMoney](#adminlibformatformatmoney)
- [admin.lib.format.formatBytes](#adminlibformatformatbytes)
- [admin.lib.format.refLabel](#adminlibformatreflabel)
- [admin.lib.format.bumpVersion](#adminlibformatbumpversion)
- [admin.lib.format.SEMVER_PATTERN](#adminlibformatsemver_pattern)
- [admin.lib.format.SLUG_PATTERN](#adminlibformatslug_pattern)

## admin.lib.format.formatDate

**Функція.** Код: [web/admin/src/lib/format.ts:3](../../../../../../web/admin/src/lib/format.ts#L3).

```typescript
function formatDate(value: string | null | undefined): string
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `string \| null \| undefined` | `—` | required |

Результат: `string`.

## admin.lib.format.formatInstant

**Функція.** Код: [web/admin/src/lib/format.ts:14](../../../../../../web/admin/src/lib/format.ts#L14).

```typescript
function formatInstant(value: string | null | undefined): string
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `string \| null \| undefined` | `—` | required |

Результат: `string`.

### Опис із вихідного коду

```text
Like formatDate, but keeps milliseconds (attempt diagnostics: a retry must start after its backoff).
```

## admin.lib.format.formatMoney

**Функція.** Код: [web/admin/src/lib/format.ts:21](../../../../../../web/admin/src/lib/format.ts#L21).

```typescript
function formatMoney(money: Money | null | undefined): string
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `money` | `{ amount: number; currency: string; } \| null \| undefined` | `—` | required |

Результат: `string`.

## admin.lib.format.formatBytes

**Функція.** Код: [web/admin/src/lib/format.ts:29](../../../../../../web/admin/src/lib/format.ts#L29).

```typescript
function formatBytes(bytes: number | null | undefined): string
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `bytes` | `number \| null \| undefined` | `—` | required |

Результат: `string`.

## admin.lib.format.refLabel

**Функція.** Код: [web/admin/src/lib/format.ts:42](../../../../../../web/admin/src/lib/format.ts#L42).

```typescript
function refLabel(ref: { package_id: string; version: string; } | null | undefined): string
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `ref` | `{ package_id: string; version: string; } \| null \| undefined` | `—` | required |

Результат: `string`.

## admin.lib.format.bumpVersion

**Функція.** Код: [web/admin/src/lib/format.ts:47](../../../../../../web/admin/src/lib/format.ts#L47).

```typescript
function bumpVersion(version: string, part?: "patch" | "minor" | "major"): string
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `version` | `string` | `—` | required |
| `part` | `"patch" \| "minor" \| "major"` | `"patch"` | required |

Результат: `string`.

### Опис із вихідного коду

```text
Next patch/minor/major of an exact SemVer (pre-release and build metadata are dropped).
```

## admin.lib.format.SEMVER_PATTERN

**Константа.** Код: [web/admin/src/lib/format.ts:56](../../../../../../web/admin/src/lib/format.ts#L56).

```typescript
SEMVER_PATTERN: RegExp = /^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/
```

Доступ: читання — так; запис — так.

## admin.lib.format.SLUG_PATTERN

**Константа.** Код: [web/admin/src/lib/format.ts:58](../../../../../../web/admin/src/lib/format.ts#L58).

```typescript
SLUG_PATTERN: RegExp = /^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$/
```

Доступ: читання — так; запис — так.
