# Модуль `components.EffectiveLimitsView`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/components/EffectiveLimitsView.tsx](../../../../../web/admin/src/components/EffectiveLimitsView.tsx). Не редагуйте вручну.

## Компоненти React

### Компонент `EffectiveLimitsView`

```typescript
function EffectiveLimitsView({ query, }: { query: { source_id?: string; task_id?: string; stage_id?: string; }; }): React.JSX.Element
```

Effective limits with the level every value comes from (orchestrator GET /v1/limits/effective).

Код: [EffectiveLimitsView.tsx:23](../../../../../web/admin/src/components/EffectiveLimitsView.tsx#L23).

## Функції

### Функція `flattenLimits`

```typescript
function flattenLimits(value: unknown, prefix?: string): [string, unknown][]
```

Flattens nested limits into `group.field` rows.

Код: [EffectiveLimitsView.tsx:7](../../../../../web/admin/src/components/EffectiveLimitsView.tsx#L7).
