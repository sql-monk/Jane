# components/ReprocessForm

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.components.ReprocessForm.StoredSelection](#admincomponentsreprocessformstoredselection)
- [admin.components.ReprocessForm.StoredSelection.object_id](#admincomponentsreprocessformstoredselectionobject_id)
- [admin.components.ReprocessForm.StoredSelection.material_id](#admincomponentsreprocessformstoredselectionmaterial_id)
- [admin.components.ReprocessForm.StoredSelection.observation_id](#admincomponentsreprocessformstoredselectionobservation_id)
- [admin.components.ReprocessForm.ReprocessForm](#admincomponentsreprocessformreprocessform)

## admin.components.ReprocessForm.StoredSelection

**Інтерфейс.** Код: [web/admin/src/components/ReprocessForm.tsx:13](../../../../../../web/admin/src/components/ReprocessForm.tsx#L13).

```typescript
interface StoredSelection {}
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [object_id](components.ReprocessForm.md#admincomponentsreprocessformstoredselectionobject_id) | Поле | ні |
| [material_id](components.ReprocessForm.md#admincomponentsreprocessformstoredselectionmaterial_id) | Поле | ні |
| [observation_id](components.ReprocessForm.md#admincomponentsreprocessformstoredselectionobservation_id) | Поле | ні |

### Опис із вихідного коду

```text
One stored RAW object (storage.v1 StoredObject) the user picked, e.g. a row of the materials page.
```

## admin.components.ReprocessForm.StoredSelection.object_id

**Поле.** Код: [web/admin/src/components/ReprocessForm.tsx:14](../../../../../../web/admin/src/components/ReprocessForm.tsx#L14).

```typescript
object_id: string
```

Доступ: читання — так; запис — так.

## admin.components.ReprocessForm.StoredSelection.material_id

**Поле.** Код: [web/admin/src/components/ReprocessForm.tsx:15](../../../../../../web/admin/src/components/ReprocessForm.tsx#L15).

```typescript
material_id?: string | undefined
```

Доступ: читання — так; запис — так.

## admin.components.ReprocessForm.StoredSelection.observation_id

**Поле.** Код: [web/admin/src/components/ReprocessForm.tsx:16](../../../../../../web/admin/src/components/ReprocessForm.tsx#L16).

```typescript
observation_id?: string | undefined
```

Доступ: читання — так; запис — так.

## admin.components.ReprocessForm.ReprocessForm

**Функція.** Код: [web/admin/src/components/ReprocessForm.tsx:34](../../../../../../web/admin/src/components/ReprocessForm.tsx#L34).

```typescript
function ReprocessForm({ taskId, storageConnectionId, materialIds, objectIds, stored, }: { taskId?: string; storageConnectionId?: string; materialIds?: string[]; objectIds?: string[]; stored?: StoredSelection; }): JSX.Element
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ taskId?: string; storageConnectionId?: string; materialIds?: string[]; objectIds?: string[]; stored?: StoredSelection; }` | `—` | required |

Результат: `JSX.Element`.
