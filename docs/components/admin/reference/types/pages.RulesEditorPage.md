# Модуль `pages.RulesEditorPage`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/pages/RulesEditorPage.tsx](../../../../../web/admin/src/pages/RulesEditorPage.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `StrategiesSummary`

```typescript
function StrategiesSummary({ rules: ref }: { rules: { package_id: string; version: string; digest?: string; }; }): React.JSX.Element
```

Read-only summary of the strategies a source uses (source page).

Код: [RulesEditorPage.tsx:88](../../../../../web/admin/src/pages/RulesEditorPage.tsx#L88).

### Компонент `RulesEditorPage`

```typescript
function RulesEditorPage(): React.JSX.Element
```

Код: [RulesEditorPage.tsx:121](../../../../../web/admin/src/pages/RulesEditorPage.tsx#L121).

## Константи

### Константа `STRATEGY_TEMPLATES`

```typescript
const STRATEGY_TEMPLATES: Record<string, Json>
```

Templates for every strategy type of collector-rules.schema.json#/$defs/Strategy (required fields only).

Код: [RulesEditorPage.tsx:23](../../../../../web/admin/src/pages/RulesEditorPage.tsx#L23).

### Константа `STRATEGY_LABELS`

```typescript
const STRATEGY_LABELS: Record<string, string>
```

Код: [RulesEditorPage.tsx:47](../../../../../web/admin/src/pages/RulesEditorPage.tsx#L47).
