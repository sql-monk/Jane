# components/PropertyGrid

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.components.PropertyGrid.PropertyIssuesContext](#admincomponentspropertygridpropertyissuescontext)
- [admin.components.PropertyGrid.PropertyDraftsBlockedContext](#admincomponentspropertygridpropertydraftsblockedcontext)
- [admin.components.PropertyGrid.PropertyGrid](#admincomponentspropertygridpropertygrid)

## admin.components.PropertyGrid.PropertyIssuesContext

**Змінна.** Код: [web/admin/src/components/PropertyGrid.tsx:5](../../../../../../web/admin/src/components/PropertyGrid.tsx#L5).

```typescript
PropertyIssuesContext: any = createContext<(key: string, error: string) => void>(() => {})
```

Доступ: читання — так; запис — так.

## admin.components.PropertyGrid.PropertyDraftsBlockedContext

**Змінна.** Код: [web/admin/src/components/PropertyGrid.tsx:6](../../../../../../web/admin/src/components/PropertyGrid.tsx#L6).

```typescript
PropertyDraftsBlockedContext: any = createContext(false)
```

Доступ: читання — так; запис — так.

## admin.components.PropertyGrid.PropertyGrid

**Функція.** Код: [web/admin/src/components/PropertyGrid.tsx:7](../../../../../../web/admin/src/components/PropertyGrid.tsx#L7).

```typescript
function PropertyGrid({ value, onChange, label, objectRoot, }: { value: JsonValue; onChange: (value: JsonValue) => void; label?: string; objectRoot?: boolean; }): any
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ value: JsonValue; onChange: (value: JsonValue) => void; label?: string; objectRoot?: boolean; }` | `—` | required |

Результат: `any`.
