# Модуль `jane_kit.errors`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/errors.py](../../../../../libs/jane-kit/src/jane_kit/errors.py). Не редагуйте вручну.

Error model: RFC 9457 Problem Details (``application/problem+json``) per WP-00 contract.

Wire format: ``contracts/schemas/common/problem.schema.json``; code catalogue with HTTP statuses and ``retryable``: ``contracts/docs/errors.md``. This module is the single place that maps exceptions to that schema — services raise :class:`JaneError` subclasses (or ``JaneError(code=...)``).

## Зміст

- [Клас `BadRequest`](#клас-badrequest)
- [Клас `Conflict`](#клас-conflict)
- [Клас `FieldError`](#клас-fielderror)
- [Клас `Forbidden`](#клас-forbidden)
- [Клас `JaneError`](#клас-janeerror)
- [Клас `LimitExceeded`](#клас-limitexceeded)
- [Клас `NotFound`](#клас-notfound)
- [Клас `Problem`](#клас-problem)
- [Клас `RateLimited`](#клас-ratelimited)
- [Клас `ServiceUnavailable`](#клас-serviceunavailable)
- [Клас `Timeout`](#клас-timeout)
- [Клас `Unauthenticated`](#клас-unauthenticated)
- [Клас `UpstreamUnavailable`](#клас-upstreamunavailable)
- [Клас `ValidationFailed`](#клас-validationfailed)
- [Функція `install_error_handlers`](#функція-install_error_handlers)
- [Функція `problem_response`](#функція-problem_response)

## Класи

### Клас `BadRequest`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.errors` |
| Успадкування | `JaneError` |
| Код | [errors.py:163](../../../../../libs/jane-kit/src/jane_kit/errors.py#L163) |

```python
class BadRequest(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'bad_request'` |  |

### Клас `Conflict`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.errors` |
| Успадкування | `JaneError` |
| Код | [errors.py:183](../../../../../libs/jane-kit/src/jane_kit/errors.py#L183) |

```python
class Conflict(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'conflict'` |  |

### Клас `FieldError`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_kit.errors` |
| Успадкування | `BaseModel` |
| Код | [errors.py:84](../../../../../libs/jane-kit/src/jane_kit/errors.py#L84) |

```python
class FieldError(BaseModel): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `pointer` | `str \| None` | `None` | читання й запис | JSON Pointer into the request body, e.g. ``/stages/2/handler/version``. |
| `parameter` | `str \| None` | `None` | читання й запис | Name of a query/path/header parameter. |
| `code` | `str \| None` | `None` | читання й запис |  |
| `message` | `str` | — | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `ConfigDict(extra='allow')` |  |

### Клас `Forbidden`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.errors` |
| Успадкування | `JaneError` |
| Код | [errors.py:175](../../../../../libs/jane-kit/src/jane_kit/errors.py#L175) |

```python
class Forbidden(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'forbidden'` |  |

### Клас `JaneError`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.errors` |
| Успадкування | `Exception` |
| Код | [errors.py:115](../../../../../libs/jane-kit/src/jane_kit/errors.py#L115) |

```python
class JaneError(Exception): ...
```

Base class for errors that map to a Problem response. Status/retryable default from the catalogue.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `code` | `ClassVar[str]` | `'internal_error'` | читання |  |

#### Конструктор `JaneError.__init__`

```python
def __init__(
    self,
    detail: str | None = None,
    *,
    code: str | None = None,
    status: int | None = None,
    retryable: bool | None = None,
    title: str | None = None,
    errors: list[FieldError] | None = None,
    details: dict[str, Any] | None = None,
    retry_after_seconds: int | None = None,
    headers: dict[str, str] | None = None,
) -> None: ...
```

Код: [errors.py:120](../../../../../libs/jane-kit/src/jane_kit/errors.py#L120).

#### Метод `JaneError.to_problem`

```python
def to_problem(self, instance: str | None = None) -> Problem: ...
```

Код: [errors.py:147](../../../../../libs/jane-kit/src/jane_kit/errors.py#L147).

### Клас `LimitExceeded`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.errors` |
| Успадкування | `JaneError` |
| Код | [errors.py:187](../../../../../libs/jane-kit/src/jane_kit/errors.py#L187) |

```python
class LimitExceeded(JaneError): ...
```

A request asks for more than the effective limit or hard cap (422, not retryable).

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'limit_exceeded'` |  |

### Клас `NotFound`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.errors` |
| Успадкування | `JaneError` |
| Код | [errors.py:179](../../../../../libs/jane-kit/src/jane_kit/errors.py#L179) |

```python
class NotFound(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'not_found'` |  |

### Клас `Problem`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_kit.errors` |
| Успадкування | `BaseModel` |
| Код | [errors.py:95](../../../../../libs/jane-kit/src/jane_kit/errors.py#L95) |

```python
class Problem(BaseModel): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `type` | `str` | — | читання й запис |  |
| `title` | `str` | — | читання й запис |  |
| `status` | `int` | — | читання й запис |  |
| `detail` | `str \| None` | `None` | читання й запис |  |
| `instance` | `str \| None` | `None` | читання й запис |  |
| `code` | `str` | — | читання й запис |  |
| `retryable` | `bool \| None` | `None` | читання й запис |  |
| `retry_after_seconds` | `int \| None` | `None` | читання й запис |  |
| `errors` | `list[FieldError] \| None` | `None` | читання й запис |  |
| `trace_id` | `str \| None` | `None` | читання й запис |  |
| `details` | `dict[str, Any] \| None` | `None` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `ConfigDict(extra='allow')` |  |

### Клас `RateLimited`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.errors` |
| Успадкування | `JaneError` |
| Код | [errors.py:193](../../../../../libs/jane-kit/src/jane_kit/errors.py#L193) |

```python
class RateLimited(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'rate_limited'` |  |

### Клас `ServiceUnavailable`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.errors` |
| Успадкування | `JaneError` |
| Код | [errors.py:197](../../../../../libs/jane-kit/src/jane_kit/errors.py#L197) |

```python
class ServiceUnavailable(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'service_unavailable'` |  |

### Клас `Timeout`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.errors` |
| Успадкування | `JaneError` |
| Код | [errors.py:205](../../../../../libs/jane-kit/src/jane_kit/errors.py#L205) |

```python
class Timeout(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'timeout'` |  |

### Клас `Unauthenticated`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.errors` |
| Успадкування | `JaneError` |
| Код | [errors.py:171](../../../../../libs/jane-kit/src/jane_kit/errors.py#L171) |

```python
class Unauthenticated(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'unauthenticated'` |  |

### Клас `UpstreamUnavailable`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.errors` |
| Успадкування | `JaneError` |
| Код | [errors.py:201](../../../../../libs/jane-kit/src/jane_kit/errors.py#L201) |

```python
class UpstreamUnavailable(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'upstream_unavailable'` |  |

### Клас `ValidationFailed`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.errors` |
| Успадкування | `JaneError` |
| Код | [errors.py:167](../../../../../libs/jane-kit/src/jane_kit/errors.py#L167) |

```python
class ValidationFailed(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'validation_failed'` |  |

## Функції

### Функція `install_error_handlers`

```python
def install_error_handlers(app: FastAPI) -> None: ...
```

Make every error of ``app`` a Problem response (including 404/405 and validation).

Код: [errors.py:252](../../../../../libs/jane-kit/src/jane_kit/errors.py#L252).

### Функція `problem_response`

```python
def problem_response(problem: Problem, headers: dict[str, str] | None = None) -> JSONResponse: ...
```

Код: [errors.py:209](../../../../../libs/jane-kit/src/jane_kit/errors.py#L209).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `KNOWN_CODES` | `dict[str, tuple[int, bool]]` | `{'bad_request': (400, False), 'validation_failed': (422, False), 'unauthenticate` |  |
| `PROBLEM_CONTENT_TYPE` | — | `'application/problem+json'` |  |
| `PROBLEM_TYPE_BASE` | — | `'urn:jane:problem:'` |  |
