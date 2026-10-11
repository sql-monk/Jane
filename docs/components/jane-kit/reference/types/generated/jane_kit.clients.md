# jane_kit.clients

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.clients.RetryPolicy](#jane_kitclientsretrypolicy)
- [jane_kit.clients.RetryPolicy.max_attempts](#jane_kitclientsretrypolicymax_attempts)
- [jane_kit.clients.RetryPolicy.initial_backoff_ms](#jane_kitclientsretrypolicyinitial_backoff_ms)
- [jane_kit.clients.RetryPolicy.max_backoff_ms](#jane_kitclientsretrypolicymax_backoff_ms)
- [jane_kit.clients.RetryPolicy.backoff_multiplier](#jane_kitclientsretrypolicybackoff_multiplier)
- [jane_kit.clients.RetryPolicy.jitter](#jane_kitclientsretrypolicyjitter)
- [jane_kit.clients.ClientLimits](#jane_kitclientsclientlimits)
- [jane_kit.clients.ClientLimits.connect_timeout_ms](#jane_kitclientsclientlimitsconnect_timeout_ms)
- [jane_kit.clients.ClientLimits.request_timeout_ms](#jane_kitclientsclientlimitsrequest_timeout_ms)
- [jane_kit.clients.ClientLimits.retries](#jane_kitclientsclientlimitsretries)
- [jane_kit.clients.ClientLimits.max_connections](#jane_kitclientsclientlimitsmax_connections)
- [jane_kit.clients.ClientLimits.job_poll_interval_ms](#jane_kitclientsclientlimitsjob_poll_interval_ms)
- [jane_kit.clients.ClientLimits.job_wait_timeout_ms](#jane_kitclientsclientlimitsjob_wait_timeout_ms)
- [jane_kit.clients.RemoteError](#jane_kitclientsremoteerror)
- [jane_kit.clients.RemoteError.__init__](#jane_kitclientsremoteerror__init__)
- [jane_kit.clients.RemoteError.status](#jane_kitclientsremoteerrorstatus)
- [jane_kit.clients.RemoteError.problem](#jane_kitclientsremoteerrorproblem)
- [jane_kit.clients.RemoteError.body](#jane_kitclientsremoteerrorbody)
- [jane_kit.clients.RemoteError.retryable](#jane_kitclientsremoteerrorretryable)
- [jane_kit.clients.ServiceClient](#jane_kitclientsserviceclient)
- [jane_kit.clients.ServiceClient.__init__](#jane_kitclientsserviceclient__init__)
- [jane_kit.clients.ServiceClient.limits](#jane_kitclientsserviceclientlimits)
- [jane_kit.clients.ServiceClient.__aenter__](#jane_kitclientsserviceclient__aenter__)
- [jane_kit.clients.ServiceClient.__aexit__](#jane_kitclientsserviceclient__aexit__)
- [jane_kit.clients.ServiceClient.aclose](#jane_kitclientsserviceclientaclose)
- [jane_kit.clients.ServiceClient.request](#jane_kitclientsserviceclientrequest)
- [jane_kit.clients.ServiceClient.get_json](#jane_kitclientsserviceclientget_json)
- [jane_kit.clients.ServiceClient.post_json](#jane_kitclientsserviceclientpost_json)
- [jane_kit.clients.ServiceClient.new_idempotency_key](#jane_kitclientsserviceclientnew_idempotency_key)
- [jane_kit.clients.ServiceClient.wait_for_job](#jane_kitclientsserviceclientwait_for_job)

## jane_kit.clients.RetryPolicy

**Клас.** Код: [libs/jane-kit/src/jane_kit/clients.py:37](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L37).

```python
class RetryPolicy(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_attempts](jane_kit.clients.md#jane_kitclientsretrypolicymax_attempts) | Поле | ні |
| [initial_backoff_ms](jane_kit.clients.md#jane_kitclientsretrypolicyinitial_backoff_ms) | Поле | ні |
| [max_backoff_ms](jane_kit.clients.md#jane_kitclientsretrypolicymax_backoff_ms) | Поле | ні |
| [backoff_multiplier](jane_kit.clients.md#jane_kitclientsretrypolicybackoff_multiplier) | Поле | ні |
| [jitter](jane_kit.clients.md#jane_kitclientsretrypolicyjitter) | Поле | ні |
| [model_config](jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Contract ``limits.retries`` (``RetryPolicy``).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_clients.py:10](../../../../../../libs/jane-kit/tests/test_clients.py#L10).

```python
FAST = ClientLimits(
    retries=RetryPolicy(max_attempts=3, initial_backoff_ms=0, max_backoff_ms=0, jitter=False),
    job_poll_interval_ms=1,
)
```

Контекст і передумови: [services/storage/tests/test_core.py:159](../../../../../../services/storage/tests/test_core.py#L159).

```python
policy = RetryPolicy(initial_backoff_ms=100, max_backoff_ms=250, backoff_multiplier=2.0, jitter=False)
```

## jane_kit.clients.RetryPolicy.max_attempts

**Поле.** Код: [libs/jane-kit/src/jane_kit/clients.py:40](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L40).

```python
max_attempts: int = Field(default=4, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "4",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Total attempts including the first one.
```

## jane_kit.clients.RetryPolicy.initial_backoff_ms

**Поле.** Код: [libs/jane-kit/src/jane_kit/clients.py:42](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L42).

```python
initial_backoff_ms: int = Field(default=200, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "200",
  "ge": "0"
}
```

## jane_kit.clients.RetryPolicy.max_backoff_ms

**Поле.** Код: [libs/jane-kit/src/jane_kit/clients.py:43](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L43).

```python
max_backoff_ms: int = Field(default=10000, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10000",
  "ge": "0"
}
```

## jane_kit.clients.RetryPolicy.backoff_multiplier

**Поле.** Код: [libs/jane-kit/src/jane_kit/clients.py:44](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L44).

```python
backoff_multiplier: float = Field(default=2.0, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2.0",
  "ge": "1"
}
```

## jane_kit.clients.RetryPolicy.jitter

**Поле.** Код: [libs/jane-kit/src/jane_kit/clients.py:45](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L45).

```python
jitter: bool = True
```

Доступ: читання — так; запис — так.

## jane_kit.clients.ClientLimits

**Клас.** Код: [libs/jane-kit/src/jane_kit/clients.py:48](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L48).

```python
class ClientLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [connect_timeout_ms](jane_kit.clients.md#jane_kitclientsclientlimitsconnect_timeout_ms) | Поле | ні |
| [request_timeout_ms](jane_kit.clients.md#jane_kitclientsclientlimitsrequest_timeout_ms) | Поле | ні |
| [retries](jane_kit.clients.md#jane_kitclientsclientlimitsretries) | Поле | ні |
| [max_connections](jane_kit.clients.md#jane_kitclientsclientlimitsmax_connections) | Поле | ні |
| [job_poll_interval_ms](jane_kit.clients.md#jane_kitclientsclientlimitsjob_poll_interval_ms) | Поле | ні |
| [job_wait_timeout_ms](jane_kit.clients.md#jane_kitclientsclientlimitsjob_wait_timeout_ms) | Поле | ні |
| [model_config](jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_clients.py:10](../../../../../../libs/jane-kit/tests/test_clients.py#L10).

```python
FAST = ClientLimits(
    retries=RetryPolicy(max_attempts=3, initial_backoff_ms=0, max_backoff_ms=0, jitter=False),
    job_poll_interval_ms=1,
)
```

Контекст і передумови: [libs/jane-kit/tests/test_clients.py:152](../../../../../../libs/jane-kit/tests/test_clients.py#L152).

```python
limits = ClientLimits(job_poll_interval_ms=1, job_wait_timeout_ms=10)
```

## jane_kit.clients.ClientLimits.connect_timeout_ms

**Поле.** Код: [libs/jane-kit/src/jane_kit/clients.py:49](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L49).

```python
connect_timeout_ms: int = contract_field('timeouts.connect_timeout_ms', 5000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'timeouts.connect_timeout_ms'",
  "ge": "1"
}
```

## jane_kit.clients.ClientLimits.request_timeout_ms

**Поле.** Код: [libs/jane-kit/src/jane_kit/clients.py:50](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L50).

```python
request_timeout_ms: int = contract_field('timeouts.request_timeout_ms', 30000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'timeouts.request_timeout_ms'",
  "ge": "1"
}
```

## jane_kit.clients.ClientLimits.retries

**Поле.** Код: [libs/jane-kit/src/jane_kit/clients.py:51](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L51).

```python
retries: RetryPolicy = contract_field('retries', RetryPolicy())
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'retries'"
}
```

## jane_kit.clients.ClientLimits.max_connections

**Поле.** Код: [libs/jane-kit/src/jane_kit/clients.py:52](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L52).

```python
max_connections: int = Field(default=20, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "20",
  "ge": "1"
}
```

## jane_kit.clients.ClientLimits.job_poll_interval_ms

**Поле.** Код: [libs/jane-kit/src/jane_kit/clients.py:53](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L53).

```python
job_poll_interval_ms: int = Field(default=1000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1000",
  "ge": "1"
}
```

## jane_kit.clients.ClientLimits.job_wait_timeout_ms

**Поле.** Код: [libs/jane-kit/src/jane_kit/clients.py:54](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L54).

```python
job_wait_timeout_ms: int = Field(default=3600000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "3600000",
  "ge": "1"
}
```

## jane_kit.clients.RemoteError

**Клас.** Код: [libs/jane-kit/src/jane_kit/clients.py:57](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L57).

```python
class RemoteError(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.clients.md#jane_kitclientsremoteerror__init__) | Конструктор | ні |
| [status](jane_kit.clients.md#jane_kitclientsremoteerrorstatus) | Поле екземпляра | ні |
| [problem](jane_kit.clients.md#jane_kitclientsremoteerrorproblem) | Поле екземпляра | ні |
| [body](jane_kit.clients.md#jane_kitclientsremoteerrorbody) | Поле екземпляра | ні |
| [retryable](jane_kit.clients.md#jane_kitclientsremoteerrorretryable) | Властивість | ні |

## jane_kit.clients.RemoteError.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/clients.py:58](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L58).

```python
def __init__(self, status: int, problem: Problem | None, body: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `status` | `int` | `—` | positional-or-keyword |
| `problem` | `Problem \| None` | `—` | positional-or-keyword |
| `body` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.clients.RemoteError.status

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/clients.py:59](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L59).

```python
self.status = status
```

## jane_kit.clients.RemoteError.problem

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/clients.py:60](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L60).

```python
self.problem = problem
```

## jane_kit.clients.RemoteError.body

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/clients.py:61](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L61).

```python
self.body = body
```

## jane_kit.clients.RemoteError.retryable

**Властивість.** Код: [libs/jane-kit/src/jane_kit/clients.py:65](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L65).

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

## jane_kit.clients.ServiceClient

**Клас.** Код: [libs/jane-kit/src/jane_kit/clients.py:71](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L71).

```python
class ServiceClient:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.clients.md#jane_kitclientsserviceclient__init__) | Конструктор | ні |
| [limits](jane_kit.clients.md#jane_kitclientsserviceclientlimits) | Поле екземпляра | ні |
| [__aenter__](jane_kit.clients.md#jane_kitclientsserviceclient__aenter__) | Метод | ні |
| [__aexit__](jane_kit.clients.md#jane_kitclientsserviceclient__aexit__) | Метод | ні |
| [aclose](jane_kit.clients.md#jane_kitclientsserviceclientaclose) | Метод | ні |
| [request](jane_kit.clients.md#jane_kitclientsserviceclientrequest) | Метод | ні |
| [get_json](jane_kit.clients.md#jane_kitclientsserviceclientget_json) | Метод | ні |
| [post_json](jane_kit.clients.md#jane_kitclientsserviceclientpost_json) | Метод | ні |
| [new_idempotency_key](jane_kit.clients.md#jane_kitclientsserviceclientnew_idempotency_key) | Метод | ні |
| [wait_for_job](jane_kit.clients.md#jane_kitclientsserviceclientwait_for_job) | Метод | ні |

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_clients.py:28](../../../../../../libs/jane-kit/tests/test_clients.py#L28).

```python
ServiceClient("http://svc", FAST, transport=t)
```

Контекст і передумови: [libs/jane-kit/tests/test_clients.py:43](../../../../../../libs/jane-kit/tests/test_clients.py#L43).

```python
ServiceClient("http://svc", FAST, transport=t)
```

## jane_kit.clients.ServiceClient.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/clients.py:72](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L72).

```python
def __init__(self, base_url: str, limits: ClientLimits | None=None, *, headers: Mapping[str, str] | None=None, transport: httpx.AsyncBaseTransport | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `base_url` | `str` | `—` | positional-or-keyword |
| `limits` | `ClientLimits \| None` | `None` | positional-or-keyword |
| `headers` | `Mapping[str, str] \| None` | `None` | keyword-only |
| `transport` | `httpx.AsyncBaseTransport \| None` | `None` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_clients.py:28](../../../../../../libs/jane-kit/tests/test_clients.py#L28).

```python
ServiceClient("http://svc", FAST, transport=t)
```

Контекст і передумови: [libs/jane-kit/tests/test_clients.py:43](../../../../../../libs/jane-kit/tests/test_clients.py#L43).

```python
ServiceClient("http://svc", FAST, transport=t)
```

## jane_kit.clients.ServiceClient.limits

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/clients.py:80](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L80).

```python
self.limits = limits or ClientLimits()
```

## jane_kit.clients.ServiceClient.__aenter__

**Метод.** Код: [libs/jane-kit/src/jane_kit/clients.py:91](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L91).

```python
async def __aenter__(self) -> Self:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Self`.

## jane_kit.clients.ServiceClient.__aexit__

**Метод.** Код: [libs/jane-kit/src/jane_kit/clients.py:94](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L94).

```python
async def __aexit__(self, *exc: object) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `exc` | `object` | `—` | var-positional |

Результат: `None`.

## jane_kit.clients.ServiceClient.aclose

**Метод.** Код: [libs/jane-kit/src/jane_kit/clients.py:97](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L97).

```python
async def aclose(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_llm_budget.py:140](../../../../../../services/assistant/tests/test_llm_budget.py#L140).

```python
await client.aclose()
```

Контекст і передумови: [services/assistant/tests/test_llm_budget.py:158](../../../../../../services/assistant/tests/test_llm_budget.py#L158).

```python
await client.aclose()
```

## jane_kit.clients.ServiceClient.request

**Метод.** Код: [libs/jane-kit/src/jane_kit/clients.py:113](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L113).

```python
async def request(self, method: str, url: str, *, json: Any=None, params: Mapping[str, Any] | None=None, headers: Mapping[str, str] | None=None, idempotency_key: str | None=None) -> httpx.Response:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `method` | `str` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |
| `json` | `Any` | `None` | keyword-only |
| `params` | `Mapping[str, Any] \| None` | `None` | keyword-only |
| `headers` | `Mapping[str, str] \| None` | `None` | keyword-only |
| `idempotency_key` | `str \| None` | `None` | keyword-only |

Результат: `httpx.Response`.

Явні `raise` у тілі: `error`, `повторний raise`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_kit.clients.ServiceClient.get_json

**Метод.** Код: [libs/jane-kit/src/jane_kit/clients.py:161](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L161).

```python
async def get_json(self, url: str, **kw: Any) -> Any:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |
| `kw` | `Any` | `—` | var-keyword |

Результат: `Any`.

## jane_kit.clients.ServiceClient.post_json

**Метод.** Код: [libs/jane-kit/src/jane_kit/clients.py:164](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L164).

```python
async def post_json(self, url: str, json: Any, *, idempotency_key: str | None=None, **kw: Any) -> Any:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |
| `json` | `Any` | `—` | positional-or-keyword |
| `idempotency_key` | `str \| None` | `None` | keyword-only |
| `kw` | `Any` | `—` | var-keyword |

Результат: `Any`.

## jane_kit.clients.ServiceClient.new_idempotency_key

**Метод.** Код: [libs/jane-kit/src/jane_kit/clients.py:168](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L168).

```python
def new_idempotency_key() -> str:
```

Декоратори: `staticmethod`.

Результат: `str`.

## jane_kit.clients.ServiceClient.wait_for_job

**Метод.** Код: [libs/jane-kit/src/jane_kit/clients.py:171](../../../../../../libs/jane-kit/src/jane_kit/clients.py#L171).

```python
async def wait_for_job(self, job_url: str) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job_url` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `TimeoutError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Poll ``job_url`` (``Location`` of a 202) until the job is terminal; return the job body.
```
