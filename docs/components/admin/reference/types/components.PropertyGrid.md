# Модуль `components.PropertyGrid`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/components/PropertyGrid.tsx](../../../../../web/admin/src/components/PropertyGrid.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `PropertyIssuesContext`

```typescript
function PropertyIssuesContext(props: React.ProviderProps<(key: string, error: string) => void>): React.ReactNode
```

Код: [PropertyGrid.tsx:34](../../../../../web/admin/src/components/PropertyGrid.tsx#L34).

### Компонент `PropertyDraftsBlockedContext`

```typescript
function PropertyDraftsBlockedContext(props: React.ProviderProps<boolean>): React.ReactNode
```

Код: [PropertyGrid.tsx:35](../../../../../web/admin/src/components/PropertyGrid.tsx#L35).

### Компонент `PropertyGrid`

```typescript
function PropertyGrid({ value, onChange, label, objectRoot, describe, choices, renderValue, }: { value: import("C:/repos/Jane/web/admin/src/lib/property").JsonValue; onChange: (value: import("C:/repos/Jane/web/admin/src/lib/property").JsonValue) => void; label?: string; objectRoot?: boolean; describe?: ((path: string, keys: readonly (string | number)[]) => string | undefined) | undefined; choices?: ((path: string, keys: readonly (string | number)[]) => unknown[] | undefined) | undefined; renderValue?: ((path: string, keys: readonly (string | number)[], value: import("C:/repos/Jane/web/admin/src/lib/property").JsonValue, onChange: (value: import("C:/repos/Jane/web/admin/src/lib/property").JsonValue) => void) => React.ReactNode) | undefined; }): React.JSX.Element
```

Код: [PropertyGrid.tsx:36](../../../../../web/admin/src/components/PropertyGrid.tsx#L36).
