# components/EffectiveLimitsView

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.components.EffectiveLimitsView.flattenLimits](#admincomponentseffectivelimitsviewflattenlimits)
- [admin.components.EffectiveLimitsView.EffectiveLimitsView](#admincomponentseffectivelimitsvieweffectivelimitsview)

## admin.components.EffectiveLimitsView.flattenLimits

**Функція.** Код: [web/admin/src/components/EffectiveLimitsView.tsx:7](../../../../../../web/admin/src/components/EffectiveLimitsView.tsx#L7).

```typescript
function flattenLimits(value: unknown, prefix?: string): Array<[string, unknown]>
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `unknown` | `—` | required |
| `prefix` | `string` | `""` | required |

Результат: `[string, unknown][]`.

### Опис із вихідного коду

```text
Flattens nested limits into `group.field` rows.
```

## admin.components.EffectiveLimitsView.EffectiveLimitsView

**Функція.** Код: [web/admin/src/components/EffectiveLimitsView.tsx:23](../../../../../../web/admin/src/components/EffectiveLimitsView.tsx#L23).

```typescript
function EffectiveLimitsView({ query, }: { query: { source_id?: string; task_id?: string; stage_id?: string; }; }): JSX.Element
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ query: { source_id?: string; task_id?: string; stage_id?: string; }; }` | `—` | required |

Результат: `JSX.Element`.

### Опис із вихідного коду

```text
Effective limits with the level every value comes from (orchestrator GET /v1/limits/effective).
```
