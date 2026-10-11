# pages/AssistantPage

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.pages.AssistantPage.sessionIdFromJob](#adminpagesassistantpagesessionidfromjob)
- [admin.pages.AssistantPage.AssistantPage](#adminpagesassistantpageassistantpage)

## admin.pages.AssistantPage.sessionIdFromJob

**Функція.** Код: [web/admin/src/pages/AssistantPage.tsx:62](../../../../../../web/admin/src/pages/AssistantPage.tsx#L62).

```typescript
function sessionIdFromJob(job: Job): string | null
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `job` | `{ job_id: components["schemas"]["Id"]; kind: string; status: components["schemas"]["JobStatus"]; created_at: components["schemas"]["Timestamp"]; updated_at?: components["schemas"]["Timestamp"]; started_at?: components["schemas"]["Timestamp"]; finished_at?: components["schemas"]["Timestamp"]; progress?: components["schemas"]["JobProgress"]; result?: Record<string, unknown>; result_ref?: components["schemas"]["content-ref.schema"]; error?: components["schemas"]["problem.schema"]; cancellation?: components["schemas"]["JobCancellation"]; idempotency_key?: string; links?: { [key: string]: string; }; labels?: components["schemas"]["Labels"]; }` | `—` | required |

Результат: `string | null`.

### Опис із вихідного коду

```text
The session of an onboarding Job: `labels.session_id`, or its `links.session` (/v1/onboarding-sessions/{id}).
```

## admin.pages.AssistantPage.AssistantPage

**Функція.** Код: [web/admin/src/pages/AssistantPage.tsx:76](../../../../../../web/admin/src/pages/AssistantPage.tsx#L76).

```typescript
function AssistantPage(): JSX.Element
```

Результат: `JSX.Element`.
