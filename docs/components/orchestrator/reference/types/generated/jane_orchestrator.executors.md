# jane_orchestrator.executors

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.executors.ExecutorError](#jane_orchestratorexecutorsexecutorerror)
- [jane_orchestrator.executors.ExecutorError.__init__](#jane_orchestratorexecutorsexecutorerror__init__)
- [jane_orchestrator.executors.ExecutorError.executor](#jane_orchestratorexecutorsexecutorerrorexecutor)
- [jane_orchestrator.executors.ExecutorError.status](#jane_orchestratorexecutorsexecutorerrorstatus)
- [jane_orchestrator.executors.ExecutorError.problem](#jane_orchestratorexecutorsexecutorerrorproblem)
- [jane_orchestrator.executors.ExecutorError.message](#jane_orchestratorexecutorsexecutorerrormessage)
- [jane_orchestrator.executors.ExecutorError.__str__](#jane_orchestratorexecutorsexecutorerror__str__)
- [jane_orchestrator.executors.ExecutorError.code](#jane_orchestratorexecutorsexecutorerrorcode)
- [jane_orchestrator.executors.ExecutorError.retryable](#jane_orchestratorexecutorsexecutorerrorretryable)
- [jane_orchestrator.executors.ExecutorError.as_problem](#jane_orchestratorexecutorsexecutorerroras_problem)
- [jane_orchestrator.executors.Executors](#jane_orchestratorexecutorsexecutors)
- [jane_orchestrator.executors.Executors.__init__](#jane_orchestratorexecutorsexecutors__init__)
- [jane_orchestrator.executors.Executors.configs](#jane_orchestratorexecutorsexecutorsconfigs)
- [jane_orchestrator.executors.Executors.connect_timeout_ms](#jane_orchestratorexecutorsexecutorsconnect_timeout_ms)
- [jane_orchestrator.executors.Executors.request_timeout_ms](#jane_orchestratorexecutorsexecutorsrequest_timeout_ms)
- [jane_orchestrator.executors.Executors.keepalive_expiry_ms](#jane_orchestratorexecutorsexecutorskeepalive_expiry_ms)
- [jane_orchestrator.executors.Executors.stale_connection_retries](#jane_orchestratorexecutorsexecutorsstale_connection_retries)
- [jane_orchestrator.executors.Executors.close](#jane_orchestratorexecutorsexecutorsclose)
- [jane_orchestrator.executors.Executors.by_role](#jane_orchestratorexecutorsexecutorsby_role)
- [jane_orchestrator.executors.Executors.first](#jane_orchestratorexecutorsexecutorsfirst)
- [jane_orchestrator.executors.Executors.collector](#jane_orchestratorexecutorsexecutorscollector)
- [jane_orchestrator.executors.Executors.handler_for](#jane_orchestratorexecutorsexecutorshandler_for)
- [jane_orchestrator.executors.Executors.call](#jane_orchestratorexecutorsexecutorscall)
- [jane_orchestrator.executors.Executors.health](#jane_orchestratorexecutorsexecutorshealth)

## jane_orchestrator.executors.ExecutorError

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:42](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L42).

```python
class ExecutorError(Exception):
```

Базові типи / інтерфейси: `Exception`.

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [executor](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorerrorexecutor) | Поле | ні |
| [status](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorerrorstatus) | Поле | ні |
| [problem](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorerrorproblem) | Поле | ні |
| [message](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorerrormessage) | Поле | ні |
| [__str__](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorerror__str__) | Метод | ні |
| [code](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorerrorcode) | Властивість | ні |
| [retryable](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorerrorretryable) | Властивість | ні |
| [as_problem](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorerroras_problem) | Метод | ні |
| [__init__](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorerror__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
A call did not happen or was rejected (HTTP error, connection error, timeout).
```

## jane_orchestrator.executors.ExecutorError.__init__

**Конструктор dataclass.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:42](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L42).

```python
def __init__(self, executor: str, status: int | None, problem: dict[str, Any] | None, message: str) -> None:
```

Базові типи / інтерфейси: `Exception`.

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `executor` | `str` | `—` | positional-or-keyword |
| `status` | `int \| None` | `—` | positional-or-keyword |
| `problem` | `dict[str, Any] \| None` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_orchestrator.executors.ExecutorError.executor

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:45](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L45).

```python
executor: str
```

Доступ: читання — так; запис — так.

## jane_orchestrator.executors.ExecutorError.status

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:46](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L46).

```python
status: int | None
```

Доступ: читання — так; запис — так.

## jane_orchestrator.executors.ExecutorError.problem

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:47](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L47).

```python
problem: dict[str, Any] | None
```

Доступ: читання — так; запис — так.

## jane_orchestrator.executors.ExecutorError.message

**Поле.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:48](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L48).

```python
message: str
```

Доступ: читання — так; запис — так.

## jane_orchestrator.executors.ExecutorError.__str__

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:50](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L50).

```python
def __str__(self) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

## jane_orchestrator.executors.ExecutorError.code

**Властивість.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:54](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L54).

```python
def code(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## jane_orchestrator.executors.ExecutorError.retryable

**Властивість.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:62](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L62).

```python
def retryable(self) -> bool:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

Доступ: читання — так; запис — ні.

## jane_orchestrator.executors.ExecutorError.as_problem

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:67](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L67).

```python
def as_problem(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_orchestrator.executors.Executors

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:89](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L89).

```python
class Executors:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutors__init__) | Конструктор | ні |
| [configs](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorsconfigs) | Поле екземпляра | ні |
| [connect_timeout_ms](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorsconnect_timeout_ms) | Поле екземпляра | ні |
| [request_timeout_ms](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorsrequest_timeout_ms) | Поле екземпляра | ні |
| [keepalive_expiry_ms](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorskeepalive_expiry_ms) | Поле екземпляра | ні |
| [stale_connection_retries](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorsstale_connection_retries) | Поле екземпляра | ні |
| [close](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorsclose) | Метод | ні |
| [by_role](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorsby_role) | Метод | ні |
| [first](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorsfirst) | Метод | ні |
| [collector](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorscollector) | Метод | ні |
| [handler_for](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorshandler_for) | Метод | ні |
| [call](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorscall) | Метод | ні |
| [health](jane_orchestrator.executors.md#jane_orchestratorexecutorsexecutorshealth) | Метод | ні |

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_auth.py:41](../../../../../../services/orchestrator/tests/test_auth.py#L41).

```python
clients = Executors(settings.all_executors(), connect_timeout_ms=1000, request_timeout_ms=1000)
```

Контекст і передумови: [services/orchestrator/tests/test_executors.py:95](../../../../../../services/orchestrator/tests/test_executors.py#L95).

```python
return Executors([cfg], connect_timeout_ms=2_000, request_timeout_ms=5_000, **kwargs), cfg
```

## jane_orchestrator.executors.Executors.__init__

**Конструктор.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:90](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L90).

```python
def __init__(self, configs: list[ExecutorConfig], *, connect_timeout_ms: int, request_timeout_ms: int, keepalive_expiry_ms: int=4000, stale_connection_retries: int=1) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `configs` | `list[ExecutorConfig]` | `—` | positional-or-keyword |
| `connect_timeout_ms` | `int` | `—` | keyword-only |
| `request_timeout_ms` | `int` | `—` | keyword-only |
| `keepalive_expiry_ms` | `int` | `4000` | keyword-only |
| `stale_connection_retries` | `int` | `1` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_auth.py:41](../../../../../../services/orchestrator/tests/test_auth.py#L41).

```python
clients = Executors(settings.all_executors(), connect_timeout_ms=1000, request_timeout_ms=1000)
```

Контекст і передумови: [services/orchestrator/tests/test_executors.py:95](../../../../../../services/orchestrator/tests/test_executors.py#L95).

```python
return Executors([cfg], connect_timeout_ms=2_000, request_timeout_ms=5_000, **kwargs), cfg
```

## jane_orchestrator.executors.Executors.configs

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:99](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L99).

```python
self.configs = {c.executor: c for c in configs}
```

## jane_orchestrator.executors.Executors.connect_timeout_ms

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:103](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L103).

```python
self.connect_timeout_ms = connect_timeout_ms
```

## jane_orchestrator.executors.Executors.request_timeout_ms

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:104](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L104).

```python
self.request_timeout_ms = request_timeout_ms
```

## jane_orchestrator.executors.Executors.keepalive_expiry_ms

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:105](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L105).

```python
self.keepalive_expiry_ms = keepalive_expiry_ms
```

## jane_orchestrator.executors.Executors.stale_connection_retries

**Поле екземпляра.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:106](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L106).

```python
self.stale_connection_retries = stale_connection_retries
```

## jane_orchestrator.executors.Executors.close

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:108](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L108).

```python
def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_auth.py:46](../../../../../../services/orchestrator/tests/test_auth.py#L46).

```python
clients.close()
```

## jane_orchestrator.executors.Executors.by_role

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:129](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L129).

```python
def by_role(self, role: str) -> list[ExecutorConfig]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `role` | `str` | `—` | positional-or-keyword |

Результат: `list[ExecutorConfig]`.

## jane_orchestrator.executors.Executors.first

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:132](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L132).

```python
def first(self, role: str) -> ExecutorConfig | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `role` | `str` | `—` | positional-or-keyword |

Результат: `ExecutorConfig | None`.

## jane_orchestrator.executors.Executors.collector

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:136](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L136).

```python
def collector(self, name: str) -> ExecutorConfig | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |

Результат: `ExecutorConfig | None`.

## jane_orchestrator.executors.Executors.handler_for

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:144](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L144).

```python
def handler_for(self, package_id: str) -> ExecutorConfig | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `ExecutorConfig | None`.

## jane_orchestrator.executors.Executors.call

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:176](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L176).

```python
def call(self, executor: ExecutorConfig, method: str, path: str, *, json: Any=None, params: Mapping[str, Any] | None=None, idempotency_key: str | None=None, trace_id: str | None=None, timeout_ms: int | None=None, ok: tuple[int, ...]=()) -> httpx.Response:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `executor` | `ExecutorConfig` | `—` | positional-or-keyword |
| `method` | `str` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |
| `json` | `Any` | `None` | keyword-only |
| `params` | `Mapping[str, Any] \| None` | `None` | keyword-only |
| `idempotency_key` | `str \| None` | `None` | keyword-only |
| `trace_id` | `str \| None` | `None` | keyword-only |
| `timeout_ms` | `int \| None` | `None` | keyword-only |
| `ok` | `tuple[int, ...]` | `()` | keyword-only |

Результат: `httpx.Response`.

Явні `raise` у тілі: `ExecutorError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.executors.Executors.health

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/executors.py:235](../../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L235).

```python
def health(self, executor: ExecutorConfig, timeout_ms: int) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `executor` | `ExecutorConfig` | `—` | positional-or-keyword |
| `timeout_ms` | `int` | `—` | positional-or-keyword |

Результат: `str`.
