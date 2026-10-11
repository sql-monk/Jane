# components/DagView

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.components.DagView.DagView](#admincomponentsdagviewdagview)

## admin.components.DagView.DagView

**Функція.** Код: [web/admin/src/components/DagView.tsx:10](../../../../../../web/admin/src/components/DagView.tsx#L10).

```typescript
function DagView({ stages, selected, onSelect, requireCollect, }: { stages: readonly Stage[]; selected?: string; onSelect?: (id: string) => void; requireCollect?: boolean; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ stages: readonly Stage[]; selected?: string; onSelect?: (id: string) => void; requireCollect?: boolean; }` | `—` | required |

Результат: `any`.

### Опис із вихідного коду

```text
Processing chain of a task: stages as boxes, `inputs[].from` as arrows labelled with `select` (ТЗ §2).
```
