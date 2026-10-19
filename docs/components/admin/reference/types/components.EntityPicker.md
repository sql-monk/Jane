# Модуль `components.EntityPicker`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/components/EntityPicker.tsx](../../../../../web/admin/src/components/EntityPicker.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `EntityPicker`

```typescript
function EntityPicker({ label, value, onChange, options, required, loading, error, validationError, }: { label: string; value: string; onChange: (value: string) => void; options: import("C:/repos/Jane/web/admin/src/components/EntityPicker").EntityOption[]; required?: boolean; loading?: boolean; error?: unknown; validationError?: string | undefined; }): React.JSX.Element
```

Searchable known entities; the identifier stays explicit and round-trips unchanged.

Код: [EntityPicker.tsx:6](../../../../../web/admin/src/components/EntityPicker.tsx#L6).

## Типи

### Тип `EntityOption`

```typescript
type EntityOption = { value: string; label: string; description?: string };
```

Код: [EntityPicker.tsx:4](../../../../../web/admin/src/components/EntityPicker.tsx#L4).
