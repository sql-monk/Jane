# jane_kit.errors

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.errors.PROBLEM_CONTENT_TYPE](#jane_kiterrorsproblem_content_type)
- [jane_kit.errors.PROBLEM_TYPE_BASE](#jane_kiterrorsproblem_type_base)
- [jane_kit.errors.KNOWN_CODES](#jane_kiterrorsknown_codes)
- [jane_kit.errors.FieldError](#jane_kiterrorsfielderror)
- [jane_kit.errors.FieldError.model_config](#jane_kiterrorsfielderrormodel_config)
- [jane_kit.errors.FieldError.pointer](#jane_kiterrorsfielderrorpointer)
- [jane_kit.errors.FieldError.parameter](#jane_kiterrorsfielderrorparameter)
- [jane_kit.errors.FieldError.code](#jane_kiterrorsfielderrorcode)
- [jane_kit.errors.FieldError.message](#jane_kiterrorsfielderrormessage)
- [jane_kit.errors.Problem](#jane_kiterrorsproblem)
- [jane_kit.errors.Problem.model_config](#jane_kiterrorsproblemmodel_config)
- [jane_kit.errors.Problem.type](#jane_kiterrorsproblemtype)
- [jane_kit.errors.Problem.title](#jane_kiterrorsproblemtitle)
- [jane_kit.errors.Problem.status](#jane_kiterrorsproblemstatus)
- [jane_kit.errors.Problem.detail](#jane_kiterrorsproblemdetail)
- [jane_kit.errors.Problem.instance](#jane_kiterrorsprobleminstance)
- [jane_kit.errors.Problem.code](#jane_kiterrorsproblemcode)
- [jane_kit.errors.Problem.retryable](#jane_kiterrorsproblemretryable)
- [jane_kit.errors.Problem.retry_after_seconds](#jane_kiterrorsproblemretry_after_seconds)
- [jane_kit.errors.Problem.errors](#jane_kiterrorsproblemerrors)
- [jane_kit.errors.Problem.trace_id](#jane_kiterrorsproblemtrace_id)
- [jane_kit.errors.Problem.details](#jane_kiterrorsproblemdetails)
- [jane_kit.errors.JaneError](#jane_kiterrorsjaneerror)
- [jane_kit.errors.JaneError.code](#jane_kiterrorsjaneerrorcode)
- [jane_kit.errors.JaneError.__init__](#jane_kiterrorsjaneerror__init__)
- [jane_kit.errors.JaneError.error_code](#jane_kiterrorsjaneerrorerror_code)
- [jane_kit.errors.JaneError.status](#jane_kiterrorsjaneerrorstatus)
- [jane_kit.errors.JaneError.retryable](#jane_kiterrorsjaneerrorretryable)
- [jane_kit.errors.JaneError.title](#jane_kiterrorsjaneerrortitle)
- [jane_kit.errors.JaneError.detail](#jane_kiterrorsjaneerrordetail)
- [jane_kit.errors.JaneError.errors](#jane_kiterrorsjaneerrorerrors)
- [jane_kit.errors.JaneError.details](#jane_kiterrorsjaneerrordetails)
- [jane_kit.errors.JaneError.retry_after_seconds](#jane_kiterrorsjaneerrorretry_after_seconds)
- [jane_kit.errors.JaneError.headers](#jane_kiterrorsjaneerrorheaders)
- [jane_kit.errors.JaneError.to_problem](#jane_kiterrorsjaneerrorto_problem)
- [jane_kit.errors.BadRequest](#jane_kiterrorsbadrequest)
- [jane_kit.errors.BadRequest.code](#jane_kiterrorsbadrequestcode)
- [jane_kit.errors.ValidationFailed](#jane_kiterrorsvalidationfailed)
- [jane_kit.errors.ValidationFailed.code](#jane_kiterrorsvalidationfailedcode)
- [jane_kit.errors.Unauthenticated](#jane_kiterrorsunauthenticated)
- [jane_kit.errors.Unauthenticated.code](#jane_kiterrorsunauthenticatedcode)
- [jane_kit.errors.Forbidden](#jane_kiterrorsforbidden)
- [jane_kit.errors.Forbidden.code](#jane_kiterrorsforbiddencode)
- [jane_kit.errors.NotFound](#jane_kiterrorsnotfound)
- [jane_kit.errors.NotFound.code](#jane_kiterrorsnotfoundcode)
- [jane_kit.errors.Conflict](#jane_kiterrorsconflict)
- [jane_kit.errors.Conflict.code](#jane_kiterrorsconflictcode)
- [jane_kit.errors.LimitExceeded](#jane_kiterrorslimitexceeded)
- [jane_kit.errors.LimitExceeded.code](#jane_kiterrorslimitexceededcode)
- [jane_kit.errors.RateLimited](#jane_kiterrorsratelimited)
- [jane_kit.errors.RateLimited.code](#jane_kiterrorsratelimitedcode)
- [jane_kit.errors.ServiceUnavailable](#jane_kiterrorsserviceunavailable)
- [jane_kit.errors.ServiceUnavailable.code](#jane_kiterrorsserviceunavailablecode)
- [jane_kit.errors.UpstreamUnavailable](#jane_kiterrorsupstreamunavailable)
- [jane_kit.errors.UpstreamUnavailable.code](#jane_kiterrorsupstreamunavailablecode)
- [jane_kit.errors.Timeout](#jane_kiterrorstimeout)
- [jane_kit.errors.Timeout.code](#jane_kiterrorstimeoutcode)
- [jane_kit.errors.problem_response](#jane_kiterrorsproblem_response)
- [jane_kit.errors.install_error_handlers](#jane_kiterrorsinstall_error_handlers)

## jane_kit.errors.PROBLEM_CONTENT_TYPE

**Константа.** Код: [libs/jane-kit/src/jane_kit/errors.py:43](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L43).

```python
PROBLEM_CONTENT_TYPE = 'application/problem+json'
```

## jane_kit.errors.PROBLEM_TYPE_BASE

**Константа.** Код: [libs/jane-kit/src/jane_kit/errors.py:44](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L44).

```python
PROBLEM_TYPE_BASE = 'urn:jane:problem:'
```

## jane_kit.errors.KNOWN_CODES

**Константа.** Код: [libs/jane-kit/src/jane_kit/errors.py:47](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L47).

```python
KNOWN_CODES: dict[str, tuple[int, bool]] = {'bad_request': (400, False), 'validation_failed': (422, False), 'unauthenticated': (401, False), 'forbidden': (403, False), 'not_found': (404, False), 'method_not_allowed': (405, False), 'conflict': (409, False), 'version_exists': (409, False), 'idempotency_in_progress': (409, True), 'job_not_cancellable': (409, False), 'upstream_conflict': (409, False), 'precondition_failed': (412, False), 'precondition_required': (428, False), 'idempotency_key_reused': (422, False), 'payload_too_large': (413, False), 'unsupported_media_type': (415, False), 'limit_exceeded': (422, False), 'rate_limited': (429, True), 'budget_exhausted': (429, False), 'secret_detected': (422, False), 'dependency_not_allowed': (422, False), 'digest_mismatch': (422, False), 'schema_mismatch': (422, False), 'out_of_scope': (422, False), 'access_denied_by_policy': (403, False), 'source_unavailable': (502, True), 'upstream_unavailable': (502, True), 'internal_error': (500, True), 'not_implemented': (501, False), 'service_unavailable': (503, True), 'timeout': (504, True)}
```

## jane_kit.errors.FieldError

**Клас.** Код: [libs/jane-kit/src/jane_kit/errors.py:84](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L84).

```python
class FieldError(BaseModel):
```

Базові типи / інтерфейси: `BaseModel`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_config](jane_kit.errors.md#jane_kiterrorsfielderrormodel_config) | Поле | ні |
| [pointer](jane_kit.errors.md#jane_kiterrorsfielderrorpointer) | Поле | ні |
| [parameter](jane_kit.errors.md#jane_kiterrorsfielderrorparameter) | Поле | ні |
| [code](jane_kit.errors.md#jane_kiterrorsfielderrorcode) | Поле | ні |
| [message](jane_kit.errors.md#jane_kiterrorsfielderrormessage) | Поле | ні |

## jane_kit.errors.FieldError.model_config

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:85](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L85).

```python
model_config = ConfigDict(extra='allow')
```

Доступ: читання — так; запис — так.

## jane_kit.errors.FieldError.pointer

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:87](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L87).

```python
pointer: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
JSON Pointer into the request body, e.g. ``/stages/2/handler/version``.
```

## jane_kit.errors.FieldError.parameter

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:89](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L89).

```python
parameter: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Name of a query/path/header parameter.
```

## jane_kit.errors.FieldError.code

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:91](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L91).

```python
code: str | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.errors.FieldError.message

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:92](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L92).

```python
message: str
```

Доступ: читання — так; запис — так.

## jane_kit.errors.Problem

**Клас.** Код: [libs/jane-kit/src/jane_kit/errors.py:95](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L95).

```python
class Problem(BaseModel):
```

Базові типи / інтерфейси: `BaseModel`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_config](jane_kit.errors.md#jane_kiterrorsproblemmodel_config) | Поле | ні |
| [type](jane_kit.errors.md#jane_kiterrorsproblemtype) | Поле | ні |
| [title](jane_kit.errors.md#jane_kiterrorsproblemtitle) | Поле | ні |
| [status](jane_kit.errors.md#jane_kiterrorsproblemstatus) | Поле | ні |
| [detail](jane_kit.errors.md#jane_kiterrorsproblemdetail) | Поле | ні |
| [instance](jane_kit.errors.md#jane_kiterrorsprobleminstance) | Поле | ні |
| [code](jane_kit.errors.md#jane_kiterrorsproblemcode) | Поле | ні |
| [retryable](jane_kit.errors.md#jane_kiterrorsproblemretryable) | Поле | ні |
| [retry_after_seconds](jane_kit.errors.md#jane_kiterrorsproblemretry_after_seconds) | Поле | ні |
| [errors](jane_kit.errors.md#jane_kiterrorsproblemerrors) | Поле | ні |
| [trace_id](jane_kit.errors.md#jane_kiterrorsproblemtrace_id) | Поле | ні |
| [details](jane_kit.errors.md#jane_kiterrorsproblemdetails) | Поле | ні |

## jane_kit.errors.Problem.model_config

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:96](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L96).

```python
model_config = ConfigDict(extra='allow')
```

Доступ: читання — так; запис — так.

## jane_kit.errors.Problem.type

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:98](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L98).

```python
type: str
```

Доступ: читання — так; запис — так.

## jane_kit.errors.Problem.title

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:99](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L99).

```python
title: str
```

Доступ: читання — так; запис — так.

## jane_kit.errors.Problem.status

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:100](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L100).

```python
status: int
```

Доступ: читання — так; запис — так.

## jane_kit.errors.Problem.detail

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:101](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L101).

```python
detail: str | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.errors.Problem.instance

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:102](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L102).

```python
instance: str | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.errors.Problem.code

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:103](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L103).

```python
code: str
```

Доступ: читання — так; запис — так.

## jane_kit.errors.Problem.retryable

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:104](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L104).

```python
retryable: bool | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.errors.Problem.retry_after_seconds

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:105](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L105).

```python
retry_after_seconds: int | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.errors.Problem.errors

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:106](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L106).

```python
errors: list[FieldError] | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.errors.Problem.trace_id

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:107](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L107).

```python
trace_id: str | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.errors.Problem.details

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:108](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L108).

```python
details: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.errors.JaneError

**Клас.** Код: [libs/jane-kit/src/jane_kit/errors.py:115](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L115).

```python
class JaneError(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_kit.errors.md#jane_kiterrorsjaneerrorcode) | Поле | ні |
| [__init__](jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | ні |
| [error_code](jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | ні |
| [status](jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | ні |
| [retryable](jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | ні |
| [title](jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | ні |
| [detail](jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | ні |
| [errors](jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | ні |
| [details](jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | ні |
| [retry_after_seconds](jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | ні |
| [headers](jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | ні |
| [to_problem](jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | ні |

### Опис із вихідного коду

```text
Base class for errors that map to a Problem response. Status/retryable default from the catalogue.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_service.py:38](../../../../../../libs/jane-kit/tests/test_service.py#L38).

```python
JaneError("slow down", code="rate_limited", retry_after_seconds=30)
```

Контекст і передумови: [libs/jane-kit/tests/test_wp00_contracts.py:51](../../../../../../libs/jane-kit/tests/test_wp00_contracts.py#L51).

```python
COMMON.validate_component(
        "Problem",
        JaneError("detail", code=code).to_problem("/v1/x").model_dump(mode="json", exclude_none=True),
    )
```

## jane_kit.errors.JaneError.code

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:118](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L118).

```python
code: ClassVar[str] = 'internal_error'
```

Доступ: читання — так; запис — так.

## jane_kit.errors.JaneError.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/errors.py:120](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L120).

```python
def __init__(self, detail: str | None=None, *, code: str | None=None, status: int | None=None, retryable: bool | None=None, title: str | None=None, errors: list[FieldError] | None=None, details: dict[str, Any] | None=None, retry_after_seconds: int | None=None, headers: dict[str, str] | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `detail` | `str \| None` | `None` | positional-or-keyword |
| `code` | `str \| None` | `None` | keyword-only |
| `status` | `int \| None` | `None` | keyword-only |
| `retryable` | `bool \| None` | `None` | keyword-only |
| `title` | `str \| None` | `None` | keyword-only |
| `errors` | `list[FieldError] \| None` | `None` | keyword-only |
| `details` | `dict[str, Any] \| None` | `None` | keyword-only |
| `retry_after_seconds` | `int \| None` | `None` | keyword-only |
| `headers` | `dict[str, str] \| None` | `None` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_service.py:38](../../../../../../libs/jane-kit/tests/test_service.py#L38).

```python
JaneError("slow down", code="rate_limited", retry_after_seconds=30)
```

Контекст і передумови: [libs/jane-kit/tests/test_wp00_contracts.py:51](../../../../../../libs/jane-kit/tests/test_wp00_contracts.py#L51).

```python
COMMON.validate_component(
        "Problem",
        JaneError("detail", code=code).to_problem("/v1/x").model_dump(mode="json", exclude_none=True),
    )
```

## jane_kit.errors.JaneError.error_code

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/errors.py:133](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L133).

```python
self.error_code = code or type(self).code
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_content.py:56](../../../../../../libs/jane-kit/tests/test_content.py#L56).

```python
return err.status, err.error_code
```

## jane_kit.errors.JaneError.status

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/errors.py:135](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L135).

```python
self.status = status or default_status
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_content.py:56](../../../../../../libs/jane-kit/tests/test_content.py#L56).

```python
return err.status, err.error_code
```

## jane_kit.errors.JaneError.retryable

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/errors.py:136](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L136).

```python
self.retryable = default_retryable if retryable is None else retryable
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_content.py:244](../../../../../../libs/jane-kit/tests/test_content.py#L244).

```python
assert code(err) == (502, "upstream_unavailable") and err.retryable is False
```

Контекст і передумови: [libs/jane-kit/tests/test_content.py:319](../../../../../../libs/jane-kit/tests/test_content.py#L319).

```python
assert code(err) == (502, "upstream_unavailable") and err.retryable is True
```

## jane_kit.errors.JaneError.title

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/errors.py:137](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L137).

```python
self.title = title or _title(self.error_code)
```

## jane_kit.errors.JaneError.detail

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/errors.py:138](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L138).

```python
self.detail = detail
```

## jane_kit.errors.JaneError.errors

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/errors.py:139](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L139).

```python
self.errors = errors
```

## jane_kit.errors.JaneError.details

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/errors.py:140](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L140).

```python
self.details = details
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_content.py:290](../../../../../../libs/jane-kit/tests/test_content.py#L290).

```python
assert err.details == {"path": "test.max_bytes", "limit": 5_000}
```

## jane_kit.errors.JaneError.retry_after_seconds

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/errors.py:141](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L141).

```python
self.retry_after_seconds = retry_after_seconds
```

## jane_kit.errors.JaneError.headers

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/errors.py:142](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L142).

```python
self.headers = dict(headers or {})
```

## jane_kit.errors.JaneError.to_problem

**Метод.** Код: [libs/jane-kit/src/jane_kit/errors.py:147](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L147).

```python
def to_problem(self, instance: str | None=None) -> Problem:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `instance` | `str \| None` | `None` | positional-or-keyword |

Результат: `Problem`.

## jane_kit.errors.BadRequest

**Клас.** Код: [libs/jane-kit/src/jane_kit/errors.py:163](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L163).

```python
class BadRequest(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_kit.errors.md#jane_kiterrorsbadrequestcode) | Поле | ні |
| [__init__](jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

## jane_kit.errors.BadRequest.code

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:164](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L164).

```python
code = 'bad_request'
```

Доступ: читання — так; запис — так.

## jane_kit.errors.ValidationFailed

**Клас.** Код: [libs/jane-kit/src/jane_kit/errors.py:167](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L167).

```python
class ValidationFailed(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_kit.errors.md#jane_kiterrorsvalidationfailedcode) | Поле | ні |
| [__init__](jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_jobs.py:105](../../../../../../libs/jane-kit/tests/test_jobs.py#L105).

```python
ValidationFailed("bad input", code="schema_mismatch")
```

## jane_kit.errors.ValidationFailed.code

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:168](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L168).

```python
code = 'validation_failed'
```

Доступ: читання — так; запис — так.

## jane_kit.errors.Unauthenticated

**Клас.** Код: [libs/jane-kit/src/jane_kit/errors.py:171](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L171).

```python
class Unauthenticated(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_kit.errors.md#jane_kiterrorsunauthenticatedcode) | Поле | ні |
| [__init__](jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/orch_support.py:1095](../../../../../../services/orchestrator/tests/orch_support.py#L1095).

```python
Unauthenticated("bearer token required")
```

Контекст і передумови: [services/orchestrator/tests/orch_support.py:1098](../../../../../../services/orchestrator/tests/orch_support.py#L1098).

```python
Unauthenticated("invalid API key")
```

## jane_kit.errors.Unauthenticated.code

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:172](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L172).

```python
code = 'unauthenticated'
```

Доступ: читання — так; запис — так.

## jane_kit.errors.Forbidden

**Клас.** Код: [libs/jane-kit/src/jane_kit/errors.py:175](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L175).

```python
class Forbidden(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_kit.errors.md#jane_kiterrorsforbiddencode) | Поле | ні |
| [__init__](jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

## jane_kit.errors.Forbidden.code

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:176](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L176).

```python
code = 'forbidden'
```

Доступ: читання — так; запис — так.

## jane_kit.errors.NotFound

**Клас.** Код: [libs/jane-kit/src/jane_kit/errors.py:179](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L179).

```python
class NotFound(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_kit.errors.md#jane_kiterrorsnotfoundcode) | Поле | ні |
| [__init__](jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_contracts.py:84](../../../../../../libs/jane-kit/tests/test_contracts.py#L84).

```python
NotFound()
```

Контекст і передумови: [libs/jane-kit/tests/test_service.py:36](../../../../../../libs/jane-kit/tests/test_service.py#L36).

```python
NotFound("no such thing")
```

## jane_kit.errors.NotFound.code

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:180](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L180).

```python
code = 'not_found'
```

Доступ: читання — так; запис — так.

## jane_kit.errors.Conflict

**Клас.** Код: [libs/jane-kit/src/jane_kit/errors.py:183](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L183).

```python
class Conflict(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_kit.errors.md#jane_kiterrorsconflictcode) | Поле | ні |
| [__init__](jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

## jane_kit.errors.Conflict.code

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:184](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L184).

```python
code = 'conflict'
```

Доступ: читання — так; запис — так.

## jane_kit.errors.LimitExceeded

**Клас.** Код: [libs/jane-kit/src/jane_kit/errors.py:187](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L187).

```python
class LimitExceeded(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_kit.errors.md#jane_kiterrorslimitexceededcode) | Поле | ні |
| [__init__](jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

### Опис із вихідного коду

```text
A request asks for more than the effective limit or hard cap (422, not retryable).
```

## jane_kit.errors.LimitExceeded.code

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:190](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L190).

```python
code = 'limit_exceeded'
```

Доступ: читання — так; запис — так.

## jane_kit.errors.RateLimited

**Клас.** Код: [libs/jane-kit/src/jane_kit/errors.py:193](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L193).

```python
class RateLimited(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_kit.errors.md#jane_kiterrorsratelimitedcode) | Поле | ні |
| [__init__](jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

## jane_kit.errors.RateLimited.code

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:194](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L194).

```python
code = 'rate_limited'
```

Доступ: читання — так; запис — так.

## jane_kit.errors.ServiceUnavailable

**Клас.** Код: [libs/jane-kit/src/jane_kit/errors.py:197](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L197).

```python
class ServiceUnavailable(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_kit.errors.md#jane_kiterrorsserviceunavailablecode) | Поле | ні |
| [__init__](jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

## jane_kit.errors.ServiceUnavailable.code

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:198](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L198).

```python
code = 'service_unavailable'
```

Доступ: читання — так; запис — так.

## jane_kit.errors.UpstreamUnavailable

**Клас.** Код: [libs/jane-kit/src/jane_kit/errors.py:201](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L201).

```python
class UpstreamUnavailable(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_kit.errors.md#jane_kiterrorsupstreamunavailablecode) | Поле | ні |
| [__init__](jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

## jane_kit.errors.UpstreamUnavailable.code

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:202](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L202).

```python
code = 'upstream_unavailable'
```

Доступ: читання — так; запис — так.

## jane_kit.errors.Timeout

**Клас.** Код: [libs/jane-kit/src/jane_kit/errors.py:205](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L205).

```python
class Timeout(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_kit.errors.md#jane_kiterrorstimeoutcode) | Поле | ні |
| [__init__](jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

## jane_kit.errors.Timeout.code

**Поле.** Код: [libs/jane-kit/src/jane_kit/errors.py:206](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L206).

```python
code = 'timeout'
```

Доступ: читання — так; запис — так.

## jane_kit.errors.problem_response

**Функція.** Код: [libs/jane-kit/src/jane_kit/errors.py:209](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L209).

```python
def problem_response(problem: Problem, headers: dict[str, str] | None=None) -> JSONResponse:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `problem` | `Problem` | `—` | positional-or-keyword |
| `headers` | `dict[str, str] \| None` | `None` | positional-or-keyword |

Результат: `JSONResponse`.

## jane_kit.errors.install_error_handlers

**Функція.** Код: [libs/jane-kit/src/jane_kit/errors.py:252](../../../../../../libs/jane-kit/src/jane_kit/errors.py#L252).

```python
def install_error_handlers(app: FastAPI) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `app` | `FastAPI` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Make every error of ``app`` a Problem response (including 404/405 and validation).
```
