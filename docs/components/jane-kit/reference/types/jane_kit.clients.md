# Модуль `jane_kit.clients`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/clients.py](../../../../../libs/jane-kit/src/jane_kit/clients.py). Не редагуйте вручну.

HTTP client base for calling other Jane services (and base class of generated clients).

* timeouts, retries and pool size come from :class:`ClientLimits` (names follow ``limits.schema.json``: ``timeouts.*_ms``, ``retries`` = ``RetryPolicy``);
* retries only for safe methods or requests carrying ``Idempotency-Key``, and only for retryable failures (connection errors, 429/502/503/504, Problem ``retryable: true``); honours ``Retry-After``;
* propagates ``traceparent`` (W3C) and ``X-Request-ID`` from the log context;
* error responses become :class:`RemoteError` with the parsed :class:`~jane_kit.errors.Problem`;
* :meth:`ServiceClient.wait_for_job` polls a ``202`` job until it is terminal.

## Зміст

- [Клас `ClientLimits`](#клас-clientlimits)
- [Клас `RemoteError`](#клас-remoteerror)
- [Клас `RetryPolicy`](#клас-retrypolicy)
- [Клас `ServiceClient`](#клас-serviceclient)

## Класи

### Клас `ClientLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.clients` |
| Успадкування | `Limits` |
| Код | [clients.py:48](../../../../../libs/jane-kit/src/jane_kit/clients.py#L48) |

```python
class ClientLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `connect_timeout_ms` | `int` | `contract_field('timeouts.connect_timeout_ms', 5000, ge=1)` | читання й запис |  |
| `request_timeout_ms` | `int` | `contract_field('timeouts.request_timeout_ms', 30000, ge=1)` | читання й запис |  |
| `retries` | `RetryPolicy` | `contract_field('retries', RetryPolicy())` | читання й запис |  |
| `max_connections` | `int` | `Field(default=20, ge=1)` | читання й запис |  |
| `job_poll_interval_ms` | `int` | `Field(default=1000, ge=1)` | читання й запис |  |
| `job_wait_timeout_ms` | `int` | `Field(default=3600000, ge=1)` | читання й запис |  |

### Клас `RemoteError`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.clients` |
| Успадкування | `Exception` |
| Код | [clients.py:57](../../../../../libs/jane-kit/src/jane_kit/clients.py#L57) |

```python
class RemoteError(Exception): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `retryable` | `bool` | — | читання (властивість) |  |

#### Конструктор `RemoteError.__init__`

```python
def __init__(self, status: int, problem: Problem | None, body: str) -> None: ...
```

Код: [clients.py:58](../../../../../libs/jane-kit/src/jane_kit/clients.py#L58).

### Клас `RetryPolicy`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.clients` |
| Успадкування | `Limits` |
| Код | [clients.py:37](../../../../../libs/jane-kit/src/jane_kit/clients.py#L37) |

```python
class RetryPolicy(Limits): ...
```

Contract ``limits.retries`` (``RetryPolicy``).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_attempts` | `int` | `Field(default=4, ge=1)` | читання й запис | Total attempts including the first one. |
| `initial_backoff_ms` | `int` | `Field(default=200, ge=0)` | читання й запис |  |
| `max_backoff_ms` | `int` | `Field(default=10000, ge=0)` | читання й запис |  |
| `backoff_multiplier` | `float` | `Field(default=2.0, ge=1)` | читання й запис |  |
| `jitter` | `bool` | `True` | читання й запис |  |

### Клас `ServiceClient`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.clients` |
| Код | [clients.py:71](../../../../../libs/jane-kit/src/jane_kit/clients.py#L71) |

```python
class ServiceClient: ...
```

#### Конструктор `ServiceClient.__init__`

```python
def __init__(
    self,
    base_url: str,
    limits: ClientLimits | None = None,
    *,
    headers: Mapping[str, str] | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> None: ...
```

Код: [clients.py:72](../../../../../libs/jane-kit/src/jane_kit/clients.py#L72).

#### Метод `ServiceClient.__aenter__`

```python
async def __aenter__(self) -> Self: ...
```

Код: [clients.py:91](../../../../../libs/jane-kit/src/jane_kit/clients.py#L91).

#### Метод `ServiceClient.__aexit__`

```python
async def __aexit__(self, *exc: object) -> None: ...
```

Код: [clients.py:94](../../../../../libs/jane-kit/src/jane_kit/clients.py#L94).

#### Метод `ServiceClient.aclose`

```python
async def aclose(self) -> None: ...
```

Код: [clients.py:97](../../../../../libs/jane-kit/src/jane_kit/clients.py#L97).

#### Метод `ServiceClient.request`

```python
async def request(
    self,
    method: str,
    url: str,
    *,
    json: Any = None,
    params: Mapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
    idempotency_key: str | None = None,
) -> httpx.Response: ...
```

Код: [clients.py:113](../../../../../libs/jane-kit/src/jane_kit/clients.py#L113).

#### Метод `ServiceClient.get_json`

```python
async def get_json(self, url: str, **kw: Any) -> Any: ...
```

Код: [clients.py:161](../../../../../libs/jane-kit/src/jane_kit/clients.py#L161).

#### Метод `ServiceClient.post_json`

```python
async def post_json(
    self,
    url: str,
    json: Any,
    *,
    idempotency_key: str | None = None,
    **kw: Any,
) -> Any: ...
```

Код: [clients.py:164](../../../../../libs/jane-kit/src/jane_kit/clients.py#L164).

#### Метод `ServiceClient.new_idempotency_key`

```python
@staticmethod
def new_idempotency_key() -> str: ...
```

Код: [clients.py:168](../../../../../libs/jane-kit/src/jane_kit/clients.py#L168).

#### Метод `ServiceClient.wait_for_job`

```python
async def wait_for_job(self, job_url: str) -> dict[str, Any]: ...
```

Poll ``job_url`` (``Location`` of a 202) until the job is terminal; return the job body.

Винятки в коді методу: `TimeoutError`.

Код: [clients.py:171](../../../../../libs/jane-kit/src/jane_kit/clients.py#L171).
