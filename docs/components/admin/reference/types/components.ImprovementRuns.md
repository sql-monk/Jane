# Модуль `components.ImprovementRuns`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/components/ImprovementRuns.tsx](../../../../../web/admin/src/components/ImprovementRuns.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `ImprovementRunList`

```typescript
function ImprovementRunList({ filter, label, selected, onOpen, }: { filter: import("C:/repos/Jane/web/admin/src/components/ImprovementRuns").ImprovementRunFilter; label: string; selected?: string | null; onOpen: (jobId: string) => void; }): React.JSX.Element
```

Код: [ImprovementRuns.tsx:24](../../../../../web/admin/src/components/ImprovementRuns.tsx#L24).

## Інтерфейси

### Інтерфейс `ImprovementRunFilter`

```typescript
interface ImprovementRunFilter
```

| Член | Тип | Обов'язковий | Доступ | Опис |
|---|---|---|---|---|
| `package_id` | `string` | ні | читання й запис |  |
| `source_id` | `string` | ні | читання й запис |  |
| `problem_group_id` | `string` | ні | читання й запис |  |
| `status` | `"queued" \| "running" \| "cancelling" \| "succeeded" \| "failed" \| "cancelled"` | ні | читання й запис |  |

Код: [ImprovementRuns.tsx:11](../../../../../web/admin/src/components/ImprovementRuns.tsx#L11).
