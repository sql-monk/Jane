# api/problem

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [admin.api.problem.Problem](#adminapiproblemproblem)
- [admin.api.problem.ApiError](#adminapiproblemapierror)
- [admin.api.problem.ApiError.status](#adminapiproblemapierrorstatus)
- [admin.api.problem.ApiError.problem](#adminapiproblemapierrorproblem)
- [admin.api.problem.ApiError.constructor](#adminapiproblemapierrorconstructor)
- [admin.api.problem.ApiError.code](#adminapiproblemapierrorcode)
- [admin.api.problem.toProblem](#adminapiproblemtoproblem)
- [admin.api.problem.errorMessage](#adminapiproblemerrormessage)
- [admin.api.problem.safeProblemCode](#adminapiproblemsafeproblemcode)

## admin.api.problem.Problem

**Тип.** Код: [web/admin/src/api/problem.ts:5](../../../../../../web/admin/src/api/problem.ts#L5).

```typescript
export type Problem = ProblemShape;
```

## admin.api.problem.ApiError

**Клас.** Код: [web/admin/src/api/problem.ts:7](../../../../../../web/admin/src/api/problem.ts#L7).

```typescript
class ApiError extends Error {}
```

Базові типи / інтерфейси: `extends Error`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [status](api.problem.md#adminapiproblemapierrorstatus) | Поле | ні |
| [problem](api.problem.md#adminapiproblemapierrorproblem) | Поле | ні |
| [code](api.problem.md#adminapiproblemapierrorcode) | Властивість | ні |
| [constructor](api.problem.md#adminapiproblemapierrorconstructor) | Конструктор | ні |

## admin.api.problem.ApiError.status

**Поле.** Код: [web/admin/src/api/problem.ts:8](../../../../../../web/admin/src/api/problem.ts#L8).

```typescript
readonly status: number
```

Доступ: читання — так; запис — ні.

## admin.api.problem.ApiError.problem

**Поле.** Код: [web/admin/src/api/problem.ts:9](../../../../../../web/admin/src/api/problem.ts#L9).

```typescript
readonly problem: { type: string; title: string; status: number; detail?: string; instance?: string; code: string; retryable?: boolean; retry_after_seconds?: number; errors?: components["schemas"]["FieldError"][]; trace_id?: string; details?: Record<string, unknown>; }
```

Доступ: читання — так; запис — ні.

## admin.api.problem.ApiError.constructor

**Конструктор.** Код: [web/admin/src/api/problem.ts:11](../../../../../../web/admin/src/api/problem.ts#L11).

```typescript
constructor(status: number, problem: Problem): ApiError
```

Базові типи / інтерфейси: `extends Error`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `status` | `number` | `—` | required |
| `problem` | `{ type: string; title: string; status: number; detail?: string; instance?: string; code: string; retryable?: boolean; retry_after_seconds?: number; errors?: components["schemas"]["FieldError"][]; trace_id?: string; details?: Record<string, unknown>; }` | `—` | required |

Результат: `ApiError`.

## admin.api.problem.ApiError.code

**Властивість.** Код: [web/admin/src/api/problem.ts:20](../../../../../../web/admin/src/api/problem.ts#L20).

```typescript
code: string
```

Доступ: читання — так; запис — ні.

```typescript
get code(): string
```

## admin.api.problem.toProblem

**Функція.** Код: [web/admin/src/api/problem.ts:35](../../../../../../web/admin/src/api/problem.ts#L35).

```typescript
function toProblem(status: number, body: unknown, statusText?: string): Problem
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `status` | `number` | `—` | required |
| `body` | `unknown` | `—` | required |
| `statusText` | `string` | `""` | required |

Результат: `{ type: string; title: string; status: number; detail?: string; instance?: string; code: string; retryable?: boolean; retry_after_seconds?: number; errors?: components["schemas"]["FieldError"][]; trace_id?: string; details?: Record<string, unknown>; }`.

### Опис із вихідного коду

```text
Normalises any error body into a Problem (services may be absent or return non-JSON errors).
```

## admin.api.problem.errorMessage

**Функція.** Код: [web/admin/src/api/problem.ts:56](../../../../../../web/admin/src/api/problem.ts#L56).

```typescript
function errorMessage(error: unknown): string
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `error` | `unknown` | `—` | required |

Результат: `string`.

## admin.api.problem.safeProblemCode

**Функція.** Код: [web/admin/src/api/problem.ts:96](../../../../../../web/admin/src/api/problem.ts#L96).

```typescript
function safeProblemCode(value: unknown): string
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `unknown` | `—` | required |

Результат: `string`.
