# Модуль `pages.RulesEditorPage`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/pages/RulesEditorPage.tsx](../../../../../web/admin/src/pages/RulesEditorPage.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `StrategiesSummary`

```typescript
function StrategiesSummary({ rules: ref }: { rules: { package_id: string; version: string; digest?: string; }; }): React.JSX.Element
```

Read-only summary of the strategies a source uses (source page).

Код: [RulesEditorPage.tsx:91](../../../../../web/admin/src/pages/RulesEditorPage.tsx#L91).

### Компонент `RulesEditorPage`

```typescript
function RulesEditorPage(): React.JSX.Element
```

Код: [RulesEditorPage.tsx:124](../../../../../web/admin/src/pages/RulesEditorPage.tsx#L124).

## Константи

### Константа `STRATEGY_TEMPLATES`

```typescript
const STRATEGY_TEMPLATES: Record<string, Json>
```

Templates for every strategy type of collector-rules.schema.json#/$defs/Strategy (required fields only).

Код: [RulesEditorPage.tsx:26](../../../../../web/admin/src/pages/RulesEditorPage.tsx#L26).

### Константа `STRATEGY_LABELS`

```typescript
const STRATEGY_LABELS: Record<string, string>
```

Код: [RulesEditorPage.tsx:50](../../../../../web/admin/src/pages/RulesEditorPage.tsx#L50).
