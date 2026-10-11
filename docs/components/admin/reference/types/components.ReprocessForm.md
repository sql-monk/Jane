# Модуль `components.ReprocessForm`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/components/ReprocessForm.tsx](../../../../../web/admin/src/components/ReprocessForm.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `ReprocessForm`

```typescript
function ReprocessForm({ taskId, storageConnectionId, materialIds, objectIds, stored, }: { taskId?: string; storageConnectionId?: string; materialIds?: string[]; objectIds?: string[]; stored?: import("C:/repos/Jane/.claude/worktrees/docs/web/admin/src/components/ReprocessForm").StoredSelection; }): React.JSX.Element
```

Код: [ReprocessForm.tsx:34](../../../../../web/admin/src/components/ReprocessForm.tsx#L34).

## Інтерфейси

### Інтерфейс `StoredSelection`

```typescript
interface StoredSelection
```

One stored RAW object (storage.v1 StoredObject) the user picked, e.g. a row of the materials page.

| Член | Тип | Обов'язковий | Доступ | Опис |
|---|---|---|---|---|
| `object_id` | `string` | так | читання й запис |  |
| `material_id` | `string \| undefined` | ні | читання й запис |  |
| `observation_id` | `string \| undefined` | ні | читання й запис |  |

Код: [ReprocessForm.tsx:13](../../../../../web/admin/src/components/ReprocessForm.tsx#L13).
