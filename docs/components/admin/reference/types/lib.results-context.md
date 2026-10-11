# Модуль `lib.results-context`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/lib/results-context.ts](../../../../../web/admin/src/lib/results-context.ts). Не редагуйте вручну.

## Функції

### Функція `resultsHref`

```typescript
function resultsHref(context?: import("C:/repos/Jane/.claude/worktrees/merge/web/admin/src/lib/results-context").ResultsContext): string
```

Only storage API filters are accepted. A source/task/run identifier never implies key.scope.

Код: [results-context.ts:9](../../../../../web/admin/src/lib/results-context.ts#L9).

### Функція `entityTypeLabel`

```typescript
function entityTypeLabel(type: string): string
```

Код: [results-context.ts:22](../../../../../web/admin/src/lib/results-context.ts#L22).

## Інтерфейси

### Інтерфейс `ResultsContext`

```typescript
interface ResultsContext
```

| Член | Тип | Обов'язковий | Доступ | Опис |
|---|---|---|---|---|
| `connectionId` | `string` | ні | читання й запис |  |
| `entityType` | `string` | ні | читання й запис |  |
| `scope` | `string` | ні | читання й запис |  |
| `key` | `string` | ні | читання й запис |  |

Код: [results-context.ts:1](../../../../../web/admin/src/lib/results-context.ts#L1).
