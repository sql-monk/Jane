# Модуль `pages.MaterialsPage`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/pages/MaterialsPage.tsx](../../../../../web/admin/src/pages/MaterialsPage.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `MaterialsPage`

```typescript
function MaterialsPage(): React.JSX.Element
```

Код: [MaterialsPage.tsx:42](../../../../../web/admin/src/pages/MaterialsPage.tsx#L42).

### Компонент `MaterialDetail`

```typescript
function MaterialDetail({ connectionId, objectId }: { connectionId: string; objectId: string; }): React.JSX.Element
```

Код: [MaterialsPage.tsx:316](../../../../../web/admin/src/pages/MaterialsPage.tsx#L316).

### Компонент `MaterialTracePage`

```typescript
function MaterialTracePage(): React.JSX.Element
```

Код: [MaterialsPage.tsx:413](../../../../../web/admin/src/pages/MaterialsPage.tsx#L413).

### Компонент `TraceOutputs`

```typescript
function TraceOutputs({ outputs }: { outputs: { kind: "data" | "entity" | "stored_object"; entity_type?: string; canonical_key?: string; object_id?: string; connection_id?: string; write_status?: string; }[] | undefined; }): React.JSX.Element
```

Код: [MaterialsPage.tsx:494](../../../../../web/admin/src/pages/MaterialsPage.tsx#L494).

## Функції

### Функція `formatMaterialContent`

```typescript
function formatMaterialContent(text: string): string
```

Код: [MaterialsPage.tsx:30](../../../../../web/admin/src/pages/MaterialsPage.tsx#L30).
