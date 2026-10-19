# Модуль `lib.schema`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/lib/schema.ts](../../../../../web/admin/src/lib/schema.ts). Не редагуйте вручну.

## Функції

### Функція `schemaIssueLabel`

```typescript
function schemaIssueLabel(issue: import("C:/repos/Jane/web/admin/src/lib/schema").SchemaIssue): string
```

Код: [schema.ts:96](../../../../../web/admin/src/lib/schema.ts#L96).

### Функція `validateAgainst`

```typescript
function validateAgainst(ref: string, value: unknown): import("C:/repos/Jane/web/admin/src/lib/schema").SchemaIssue[]
```

Код: [schema.ts:101](../../../../../web/admin/src/lib/schema.ts#L101).

## Інтерфейси

### Інтерфейс `SchemaIssue`

```typescript
interface SchemaIssue
```

| Член | Тип | Обов'язковий | Доступ | Опис |
|---|---|---|---|---|
| `pointer` | `string` | так | читання й запис |  |
| `message` | `string` | так | читання й запис |  |
| `technical` | `string` | ні | читання й запис |  |

Код: [schema.ts:10](../../../../../web/admin/src/lib/schema.ts#L10).

## Типи

### Тип `SchemaRef`

```typescript
type SchemaRef = string;
```

A schema reference: `task-config.schema.json` or `common/limits.schema.json#/$defs/PlatformLimits`.

Код: [schema.ts:8](../../../../../web/admin/src/lib/schema.ts#L8).

## Константи

### Константа `SCHEMAS`

```typescript
const SCHEMAS: { readonly source: "source.schema.json"; readonly task: "task-config.schema.json"; readonly schedule: "task-config.schema.json#/$defs/Schedule"; readonly stage: "task-config.schema.json#/$defs/Stage"; readonly collectorRules: "collector-rules.schema.json"; readonly strategy: "collector-rules.schema.json#/$defs/Strategy"; readonly limits: "common/limits.schema.json"; readonly platformLimits: "commo …
```

Код: [schema.ts:121](../../../../../web/admin/src/lib/schema.ts#L121).
