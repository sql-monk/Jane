# components/ImprovementRuns

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.components.ImprovementRuns.ImprovementRunFilter](#admincomponentsimprovementrunsimprovementrunfilter)
- [admin.components.ImprovementRuns.ImprovementRunFilter.package_id](#admincomponentsimprovementrunsimprovementrunfilterpackage_id)
- [admin.components.ImprovementRuns.ImprovementRunFilter.source_id](#admincomponentsimprovementrunsimprovementrunfiltersource_id)
- [admin.components.ImprovementRuns.ImprovementRunFilter.problem_group_id](#admincomponentsimprovementrunsimprovementrunfilterproblem_group_id)
- [admin.components.ImprovementRuns.ImprovementRunFilter.status](#admincomponentsimprovementrunsimprovementrunfilterstatus)
- [admin.components.ImprovementRuns.ImprovementRunList](#admincomponentsimprovementrunsimprovementrunlist)

## admin.components.ImprovementRuns.ImprovementRunFilter

**Інтерфейс.** Код: [web/admin/src/components/ImprovementRuns.tsx:11](../../../../../../web/admin/src/components/ImprovementRuns.tsx#L11).

```typescript
interface ImprovementRunFilter {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [package_id](components.ImprovementRuns.md#admincomponentsimprovementrunsimprovementrunfilterpackage_id) | Поле | ні |
| [source_id](components.ImprovementRuns.md#admincomponentsimprovementrunsimprovementrunfiltersource_id) | Поле | ні |
| [problem_group_id](components.ImprovementRuns.md#admincomponentsimprovementrunsimprovementrunfilterproblem_group_id) | Поле | ні |
| [status](components.ImprovementRuns.md#admincomponentsimprovementrunsimprovementrunfilterstatus) | Поле | ні |

## admin.components.ImprovementRuns.ImprovementRunFilter.package_id

**Поле.** Код: [web/admin/src/components/ImprovementRuns.tsx:12](../../../../../../web/admin/src/components/ImprovementRuns.tsx#L12).

```typescript
package_id?: string | undefined
```

Доступ: читання — так; запис — так.

## admin.components.ImprovementRuns.ImprovementRunFilter.source_id

**Поле.** Код: [web/admin/src/components/ImprovementRuns.tsx:13](../../../../../../web/admin/src/components/ImprovementRuns.tsx#L13).

```typescript
source_id?: string | undefined
```

Доступ: читання — так; запис — так.

## admin.components.ImprovementRuns.ImprovementRunFilter.problem_group_id

**Поле.** Код: [web/admin/src/components/ImprovementRuns.tsx:14](../../../../../../web/admin/src/components/ImprovementRuns.tsx#L14).

```typescript
problem_group_id?: string | undefined
```

Доступ: читання — так; запис — так.

## admin.components.ImprovementRuns.ImprovementRunFilter.status

**Поле.** Код: [web/admin/src/components/ImprovementRuns.tsx:15](../../../../../../web/admin/src/components/ImprovementRuns.tsx#L15).

```typescript
status?: "failed" | "cancelled" | "queued" | "running" | "cancelling" | "succeeded" | undefined
```

Доступ: читання — так; запис — так.

## admin.components.ImprovementRuns.ImprovementRunList

**Функція.** Код: [web/admin/src/components/ImprovementRuns.tsx:24](../../../../../../web/admin/src/components/ImprovementRuns.tsx#L24).

```typescript
function ImprovementRunList({ filter, label, selected, onOpen, }: { filter: ImprovementRunFilter; label: string; selected?: string | null; onOpen: (jobId: string) => void; }): JSX.Element
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ filter: ImprovementRunFilter; label: string; selected?: string \| null; onOpen: (jobId: string) => void; }` | `—` | required |

Результат: `JSX.Element`.
