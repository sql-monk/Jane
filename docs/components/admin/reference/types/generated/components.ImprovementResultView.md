# components/ImprovementResultView

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.components.ImprovementResultView.ImprovementResultView](#admincomponentsimprovementresultviewimprovementresultview)
- [admin.components.ImprovementResultView.ProposalView](#admincomponentsimprovementresultviewproposalview)

## admin.components.ImprovementResultView.ImprovementResultView

**Функція.** Код: [web/admin/src/components/ImprovementResultView.tsx:9](../../../../../../web/admin/src/components/ImprovementResultView.tsx#L9).

```typescript
function ImprovementResultView({ result }: { result: Record<string, unknown>; }): JSX.Element
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ result: Record<string, unknown>; }` | `—` | required |

Результат: `JSX.Element`.

### Опис із вихідного коду

```text
Job.result of assistant startImprovement (assistant.v1 ImprovementResult).
```

## admin.components.ImprovementResultView.ProposalView

**Функція.** Код: [web/admin/src/components/ImprovementResultView.tsx:83](../../../../../../web/admin/src/components/ImprovementResultView.tsx#L83).

```typescript
function ProposalView({ proposal }: { proposal: ImprovementProposal; }): JSX.Element
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ proposal: ImprovementProposal; }` | `—` | required |

Результат: `JSX.Element`.

### Опис із вихідного коду

```text
`ImprovementResult.proposal` (outcome `proposal_only`): the package forbids automatic changes, the candidate passed
its tests but is not published. The user reviews the changed files, the manifest and the diff, and publishes the
version himself (registry publishPackageVersion with `based_on` + `files`). File contents are data: shown as text.
```
