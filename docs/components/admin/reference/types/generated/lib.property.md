# lib/property

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.lib.property.JsonValue](#adminlibpropertyjsonvalue)
- [admin.lib.property.JsonType](#adminlibpropertyjsontype)
- [admin.lib.property.jsonType](#adminlibpropertyjsontype)
- [admin.lib.property.emptyValue](#adminlibpropertyemptyvalue)
- [admin.lib.property.renameField](#adminlibpropertyrenamefield)
- [admin.lib.property.moveItem](#adminlibpropertymoveitem)
- [admin.lib.property.renameStage](#adminlibpropertyrenamestage)
- [admin.lib.property.removeStage](#adminlibpropertyremovestage)

## admin.lib.property.JsonValue

**Тип.** Код: [web/admin/src/lib/property.ts:3](../../../../../../web/admin/src/lib/property.ts#L3).

```typescript
export type JsonValue = null | boolean | number | string | JsonValue[] | { [key: string]: JsonValue };
```

## admin.lib.property.JsonType

**Тип.** Код: [web/admin/src/lib/property.ts:4](../../../../../../web/admin/src/lib/property.ts#L4).

```typescript
export type JsonType = "null" | "boolean" | "number" | "string" | "array" | "object";
```

## admin.lib.property.jsonType

**Функція.** Код: [web/admin/src/lib/property.ts:5](../../../../../../web/admin/src/lib/property.ts#L5).

```typescript
function jsonType(value: JsonValue): JsonType
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `JsonValue` | `—` | required |

Результат: `JsonType`.

## admin.lib.property.emptyValue

**Функція.** Код: [web/admin/src/lib/property.ts:8](../../../../../../web/admin/src/lib/property.ts#L8).

```typescript
function emptyValue(type: JsonType): JsonValue
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `type` | `JsonType` | `—` | required |

Результат: `JsonValue`.

## admin.lib.property.renameField

**Функція.** Код: [web/admin/src/lib/property.ts:11](../../../../../../web/admin/src/lib/property.ts#L11).

```typescript
function renameField(value: Record<string, JsonValue>, from: string, to: string): { [k: string]: JsonValue; }
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `Record<string, JsonValue>` | `—` | required |
| `from` | `string` | `—` | required |
| `to` | `string` | `—` | required |

Результат: `{ [k: string]: JsonValue; }`.

## admin.lib.property.moveItem

**Функція.** Код: [web/admin/src/lib/property.ts:15](../../../../../../web/admin/src/lib/property.ts#L15).

```typescript
function moveItem(value: JsonValue[], index: number, delta: number): JsonValue[]
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `JsonValue[]` | `—` | required |
| `index` | `number` | `—` | required |
| `delta` | `number` | `—` | required |

Результат: `JsonValue[]`.

## admin.lib.property.renameStage

**Функція.** Код: [web/admin/src/lib/property.ts:22](../../../../../../web/admin/src/lib/property.ts#L22).

```typescript
function renameStage(stages: Stage[], from: string, to: string): Stage[]
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `stages` | `{ stage_id: components["schemas"]["Slug"]; kind: "collect" \| "handler"; title?: string; collector?: components["schemas"]["CollectorStage"]; handler?: components["schemas"]["package-ref.schema"]; params?: Record<string, unknown>; connections?: { [key: string]: components["schemas"]["Slug"]; }; inputs?: components["schemas"]["StageInput"][]; bindings?: components["schemas"]["Binding"][]; limits?: components["schemas"]["limits.schema"]; retries?: components["schemas"]["RetryPolicy"]; on_failure?: "continue" \| "fail_run"; }[]` | `—` | required |
| `from` | `string` | `—` | required |
| `to` | `string` | `—` | required |

Результат: `{ stage_id: components["schemas"]["Slug"]; kind: "collect" | "handler"; title?: string; collector?: components["schemas"]["CollectorStage"]; handler?: components["schemas"]["package-ref.schema"]; params?: Record<string, unknown>; connections?: { [key: string]: components["schemas"]["Slug"]; }; inputs?: components["schemas"]["StageInput"][]; bindings?: components["schemas"]["Binding"][]; limits?: components["schemas"]["limits.schema"]; retries?: components["schemas"]["RetryPolicy"]; on_failure?: "continue" | "fail_run"; }[]`.

## admin.lib.property.removeStage

**Функція.** Код: [web/admin/src/lib/property.ts:36](../../../../../../web/admin/src/lib/property.ts#L36).

```typescript
function removeStage(stages: Stage[], id: string): Stage[]
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `stages` | `{ stage_id: components["schemas"]["Slug"]; kind: "collect" \| "handler"; title?: string; collector?: components["schemas"]["CollectorStage"]; handler?: components["schemas"]["package-ref.schema"]; params?: Record<string, unknown>; connections?: { [key: string]: components["schemas"]["Slug"]; }; inputs?: components["schemas"]["StageInput"][]; bindings?: components["schemas"]["Binding"][]; limits?: components["schemas"]["limits.schema"]; retries?: components["schemas"]["RetryPolicy"]; on_failure?: "continue" \| "fail_run"; }[]` | `—` | required |
| `id` | `string` | `—` | required |

Результат: `{ stage_id: components["schemas"]["Slug"]; kind: "collect" | "handler"; title?: string; collector?: components["schemas"]["CollectorStage"]; handler?: components["schemas"]["package-ref.schema"]; params?: Record<string, unknown>; connections?: { [key: string]: components["schemas"]["Slug"]; }; inputs?: components["schemas"]["StageInput"][]; bindings?: components["schemas"]["Binding"][]; limits?: components["schemas"]["limits.schema"]; retries?: components["schemas"]["RetryPolicy"]; on_failure?: "continue" | "fail_run"; }[]`.
