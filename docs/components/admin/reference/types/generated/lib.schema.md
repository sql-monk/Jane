# lib/schema

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.lib.schema.SchemaRef](#adminlibschemaschemaref)
- [admin.lib.schema.SchemaIssue](#adminlibschemaschemaissue)
- [admin.lib.schema.SchemaIssue.pointer](#adminlibschemaschemaissuepointer)
- [admin.lib.schema.SchemaIssue.message](#adminlibschemaschemaissuemessage)
- [admin.lib.schema.validateAgainst](#adminlibschemavalidateagainst)
- [admin.lib.schema.SCHEMAS](#adminlibschemaschemas)

## admin.lib.schema.SchemaRef

**Тип.** Код: [web/admin/src/lib/schema.ts:8](../../../../../../web/admin/src/lib/schema.ts#L8).

```typescript
export type SchemaRef = string;
```

### Опис із вихідного коду

```text
A schema reference: `task-config.schema.json` or `common/limits.schema.json#/$defs/PlatformLimits`.
```

## admin.lib.schema.SchemaIssue

**Інтерфейс.** Код: [web/admin/src/lib/schema.ts:10](../../../../../../web/admin/src/lib/schema.ts#L10).

```typescript
interface SchemaIssue {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [pointer](lib.schema.md#adminlibschemaschemaissuepointer) | Поле | ні |
| [message](lib.schema.md#adminlibschemaschemaissuemessage) | Поле | ні |

## admin.lib.schema.SchemaIssue.pointer

**Поле.** Код: [web/admin/src/lib/schema.ts:11](../../../../../../web/admin/src/lib/schema.ts#L11).

```typescript
pointer: string
```

Доступ: читання — так; запис — так.

## admin.lib.schema.SchemaIssue.message

**Поле.** Код: [web/admin/src/lib/schema.ts:12](../../../../../../web/admin/src/lib/schema.ts#L12).

```typescript
message: string
```

Доступ: читання — так; запис — так.

## admin.lib.schema.validateAgainst

**Функція.** Код: [web/admin/src/lib/schema.ts:29](../../../../../../web/admin/src/lib/schema.ts#L29).

```typescript
function validateAgainst(ref: SchemaRef, value: unknown): SchemaIssue[]
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `ref` | `string` | `—` | required |
| `value` | `unknown` | `—` | required |

Результат: `SchemaIssue[]`.

## admin.lib.schema.SCHEMAS

**Константа.** Код: [web/admin/src/lib/schema.ts:47](../../../../../../web/admin/src/lib/schema.ts#L47).

```typescript
SCHEMAS: { readonly source: "source.schema.json"; readonly task: "task-config.schema.json"; readonly schedule: "task-config.schema.json#/$defs/Schedule"; readonly stage: "task-config.schema.json#/$defs/Stage"; readonly collectorRules: "collector-rules.schema.json"; readonly strategy: "collector-rules.schema.json#/$defs/Strategy"; readonly limits: "common/limits.schema.json"; readonly platformLimits: "common/limits.schema.json#/$defs/PlatformLimits"; readonly connection: "common/connection.schema.json"; readonly manifest: "package-manifest.schema.json"; } = {
  source: "source.schema.json",
  task: "task-config.schema.json",
  schedule: "task-config.schema.json#/$defs/Schedule",
  stage: "task-config.schema.json#/$defs/Stage",
  collectorRules: "collector-rules.schema.json",
  strategy: "collector-rules.schema.json#/$defs/Strategy",
  limits: "common/limits.schema.json",
  platformLimits: "common/limits.schema.json#/$defs/PlatformLimits",
  connection: "common/connection.schema.json",
  manifest: "package-manifest.schema.json",
} as const
```

Доступ: читання — так; запис — так.
