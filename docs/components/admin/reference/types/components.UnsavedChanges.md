# Модуль `components.UnsavedChanges`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/components/UnsavedChanges.tsx](../../../../../web/admin/src/components/UnsavedChanges.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `UnsavedChangesProvider`

```typescript
function UnsavedChangesProvider({ children }: { children: React.ReactNode; }): React.JSX.Element
```

BrowserRouter-compatible protection for route changes, history and local editor contexts.

Код: [UnsavedChanges.tsx:32](../../../../../web/admin/src/components/UnsavedChanges.tsx#L32).

## Функції

### Функція `useUnsavedChanges`

```typescript
function useUnsavedChanges(options: import("C:/repos/Jane/web/admin/src/components/UnsavedChanges").UnsavedChangesOptions): { confirmChange: (action: () => void) => void; markSaved: () => void | undefined; }
```

Код: [UnsavedChanges.tsx:241](../../../../../web/admin/src/components/UnsavedChanges.tsx#L241).

### Функція `useConfirmUnsavedChange`

```typescript
function useConfirmUnsavedChange(): (action: () => void) => void
```

Protect a parent tab/context which unmounts a dirty child form.

Код: [UnsavedChanges.tsx:263](../../../../../web/admin/src/components/UnsavedChanges.tsx#L263).

## Інтерфейси

### Інтерфейс `UnsavedChangesOptions`

```typescript
interface UnsavedChangesOptions
```

| Член | Тип | Обов'язковий | Доступ | Опис |
|---|---|---|---|---|
| `dirty` | `boolean` | так | читання й запис |  |
| `label` | `string` | ні | читання й запис |  |
| `onSave` | `() => Promise&lt;boolean>` | ні | читання й запис |  |
| `onDiscard` | `() => void` | ні | читання й запис |  |

Код: [UnsavedChanges.tsx:15](../../../../../web/admin/src/components/UnsavedChanges.tsx#L15).
