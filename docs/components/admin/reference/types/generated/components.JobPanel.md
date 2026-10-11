# components/JobPanel

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.components.JobPanel.JobPanel](#admincomponentsjobpaneljobpanel)
- [admin.components.JobPanel.TestReportView](#admincomponentsjobpaneltestreportview)

## admin.components.JobPanel.JobPanel

**Функція.** Код: [web/admin/src/components/JobPanel.tsx:25](../../../../../../web/admin/src/components/JobPanel.tsx#L25).

```typescript
function JobPanel({ service, client, jobId, title, renderResult, cancellable, }: { service: string; client: unknown; jobId: string; title: string; renderResult?: (result: Record<string, unknown>) => ReactNode; cancellable?: boolean; }): JSX.Element
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ service: string; client: unknown; jobId: string; title: string; renderResult?: (result: Record<string, unknown>) => ReactNode; cancellable?: boolean; }` | `—` | required |

Результат: `JSX.Element`.

### Опис із вихідного коду

```text
State, progress, error and result of a long-running operation (202 + job_id) of any Jane service.
```

## admin.components.JobPanel.TestReportView

**Функція.** Код: [web/admin/src/components/JobPanel.tsx:83](../../../../../../web/admin/src/components/JobPanel.tsx#L83).

```typescript
function TestReportView({ report }: { report: TestReport; }): JSX.Element
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `__0` | `{ report: TestReport; }` | `—` | required |

Результат: `JSX.Element`.
