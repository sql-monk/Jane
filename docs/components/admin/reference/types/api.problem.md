# Модуль `api.problem`

> Згенеровано `scripts/docs_reference.py` з [web/admin/src/api/problem.ts](../../../../../web/admin/src/api/problem.ts). Не редагуйте вручну.

## Функції

### Функція `toProblem`

```typescript
function toProblem(status: number, body: unknown, statusText?: string): { type: string; title: string; status: number; detail?: string; instance?: string; code: string; retryable?: boolean; retry_after_seconds?: number; errors?: { pointer?: string; parameter?: string; code?: string; message: string; }[]; trace_id?: string; details?: Record<string, unknown>; }
```

Normalises any error body into a Problem (services may be absent or return non-JSON errors).

Код: [problem.ts:35](../../../../../web/admin/src/api/problem.ts#L35).

### Функція `errorMessage`

```typescript
function errorMessage(error: unknown): string
```

Код: [problem.ts:56](../../../../../web/admin/src/api/problem.ts#L56).

### Функція `safeProblemCode`

```typescript
function safeProblemCode(value: unknown): string
```

Код: [problem.ts:96](../../../../../web/admin/src/api/problem.ts#L96).

## Класи

### Клас `ApiError`

```typescript
class ApiError extends Error
```

| Член | Тип | Обов'язковий | Доступ | Опис |
|---|---|---|---|---|
| `status` | `number` | так | читання |  |
| `problem` | `{ type: string; title: string; status: number; detail?: string; instance?: string; code: string; retryable?: boolean; re` | так | читання |  |
| `code` | `string` | так | читання й запис |  |
| `name` | `string` | так | читання й запис |  |
| `message` | `string` | так | читання й запис |  |
| `stack` | `string` | ні | читання й запис |  |
| `cause` | `unknown` | ні | читання й запис |  |

Код: [problem.ts:7](../../../../../web/admin/src/api/problem.ts#L7).

## Типи

### Тип `Problem`

```typescript
type Problem = ProblemShape;
```

Код: [problem.ts:5](../../../../../web/admin/src/api/problem.ts#L5).
