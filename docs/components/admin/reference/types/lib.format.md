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

Код: [format.ts:11](../../../../../web/admin/src/lib/format.ts#L11).

### Функція `formatDuration`

```typescript
function formatDuration(start: string | null | undefined, end?: string | null | undefined): string
```

Код: [format.ts:18](../../../../../web/admin/src/lib/format.ts#L18).

### Функція `inputInstant`

```typescript
function inputInstant(value: string): string | undefined
```

datetime-local uses the browser's timezone; transmit an explicit RFC 3339 instant.

Код: [format.ts:29](../../../../../web/admin/src/lib/format.ts#L29).

### Функція `statusLabel`

```typescript
function statusLabel(value: string): string
```

Код: [format.ts:97](../../../../../web/admin/src/lib/format.ts#L97).

### Функція `formatMoney`

```typescript
function formatMoney(money: { amount: number; currency: string; } | null | undefined): string
```

Код: [format.ts:101](../../../../../web/admin/src/lib/format.ts#L101).

### Функція `formatBytes`

```typescript
function formatBytes(bytes: number | null | undefined): string
```

Код: [format.ts:109](../../../../../web/admin/src/lib/format.ts#L109).

### Функція `refLabel`

```typescript
function refLabel(ref: { package_id: string; version: string; } | null | undefined): string
```

Код: [format.ts:122](../../../../../web/admin/src/lib/format.ts#L122).

### Функція `bumpVersion`

```typescript
function bumpVersion(version: string, part?: "patch" | "minor" | "major"): string
```

Next patch/minor/major of an exact SemVer (pre-release and build metadata are dropped).

Код: [format.ts:127](../../../../../web/admin/src/lib/format.ts#L127).

## Константи

### Константа `SCOPE_LABELS`

```typescript
const SCOPE_LABELS: Record<string, string>
```

Код: [format.ts:35](../../../../../web/admin/src/lib/format.ts#L35).

### Константа `PERIOD_LABELS`

```typescript
const PERIOD_LABELS: Record<string, string>
```

Код: [format.ts:44](../../../../../web/admin/src/lib/format.ts#L44).

### Константа `SEMVER_PATTERN`

```typescript
const SEMVER_PATTERN: RegExp
```

Код: [format.ts:136](../../../../../web/admin/src/lib/format.ts#L136).

### Константа `SLUG_PATTERN`

```typescript
const SLUG_PATTERN: RegExp
```

Код: [format.ts:138](../../../../../web/admin/src/lib/format.ts#L138).
