# Модуль `lib.format`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/lib/format.ts](../../../../../web/admin/src/lib/format.ts). Не редагуйте вручну.

## Функції

### Функція `formatDate`

```typescript
function formatDate(value: string | null | undefined): string
```

Код: [format.ts:3](../../../../../web/admin/src/lib/format.ts#L3).

### Функція `formatInstant`

```typescript
function formatInstant(value: string | null | undefined): string
```

Like formatDate, but keeps milliseconds (attempt diagnostics: a retry must start after its backoff).

Код: [format.ts:14](../../../../../web/admin/src/lib/format.ts#L14).

### Функція `formatMoney`

```typescript
function formatMoney(money: { amount: number; currency: string; } | null | undefined): string
```

Код: [format.ts:21](../../../../../web/admin/src/lib/format.ts#L21).

### Функція `formatBytes`

```typescript
function formatBytes(bytes: number | null | undefined): string
```

Код: [format.ts:29](../../../../../web/admin/src/lib/format.ts#L29).

### Функція `refLabel`

```typescript
function refLabel(ref: { package_id: string; version: string; } | null | undefined): string
```

Код: [format.ts:42](../../../../../web/admin/src/lib/format.ts#L42).

### Функція `bumpVersion`

```typescript
function bumpVersion(version: string, part?: "patch" | "minor" | "major"): string
```

Next patch/minor/major of an exact SemVer (pre-release and build metadata are dropped).

Код: [format.ts:47](../../../../../web/admin/src/lib/format.ts#L47).

## Константи

### Константа `SEMVER_PATTERN`

```typescript
const SEMVER_PATTERN: RegExp
```

Код: [format.ts:56](../../../../../web/admin/src/lib/format.ts#L56).

### Константа `SLUG_PATTERN`

```typescript
const SLUG_PATTERN: RegExp
```

Код: [format.ts:58](../../../../../web/admin/src/lib/format.ts#L58).
