# jane_kit.idempotency

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.idempotency.IDEMPOTENCY_HEADER](#jane_kitidempotencyidempotency_header)
- [jane_kit.idempotency.REPLAY_HEADER](#jane_kitidempotencyreplay_header)
- [jane_kit.idempotency.IdempotencyLimits](#jane_kitidempotencyidempotencylimits)
- [jane_kit.idempotency.IdempotencyLimits.idempotency_ttl_seconds](#jane_kitidempotencyidempotencylimitsidempotency_ttl_seconds)
- [jane_kit.idempotency.IdempotencyLimits.in_memory_max_entries](#jane_kitidempotencyidempotencylimitsin_memory_max_entries)
- [jane_kit.idempotency.IdempotencyKeyReused](#jane_kitidempotencyidempotencykeyreused)
- [jane_kit.idempotency.IdempotencyKeyReused.code](#jane_kitidempotencyidempotencykeyreusedcode)
- [jane_kit.idempotency.IdempotencyInProgress](#jane_kitidempotencyidempotencyinprogress)
- [jane_kit.idempotency.IdempotencyInProgress.code](#jane_kitidempotencyidempotencyinprogresscode)
- [jane_kit.idempotency.StoredResponse](#jane_kitidempotencystoredresponse)
- [jane_kit.idempotency.StoredResponse.__init__](#jane_kitidempotencystoredresponse__init__)
- [jane_kit.idempotency.StoredResponse.status_code](#jane_kitidempotencystoredresponsestatus_code)
- [jane_kit.idempotency.StoredResponse.body](#jane_kitidempotencystoredresponsebody)
- [jane_kit.idempotency.StoredResponse.headers](#jane_kitidempotencystoredresponseheaders)
- [jane_kit.idempotency.IdempotencyRecord](#jane_kitidempotencyidempotencyrecord)
- [jane_kit.idempotency.IdempotencyRecord.__init__](#jane_kitidempotencyidempotencyrecord__init__)
- [jane_kit.idempotency.IdempotencyRecord.key](#jane_kitidempotencyidempotencyrecordkey)
- [jane_kit.idempotency.IdempotencyRecord.fingerprint](#jane_kitidempotencyidempotencyrecordfingerprint)
- [jane_kit.idempotency.IdempotencyRecord.state](#jane_kitidempotencyidempotencyrecordstate)
- [jane_kit.idempotency.IdempotencyRecord.expires_at](#jane_kitidempotencyidempotencyrecordexpires_at)
- [jane_kit.idempotency.IdempotencyRecord.response](#jane_kitidempotencyidempotencyrecordresponse)
- [jane_kit.idempotency.IdempotencyStore](#jane_kitidempotencyidempotencystore)
- [jane_kit.idempotency.IdempotencyStore.begin](#jane_kitidempotencyidempotencystorebegin)
- [jane_kit.idempotency.IdempotencyStore.complete](#jane_kitidempotencyidempotencystorecomplete)
- [jane_kit.idempotency.IdempotencyStore.release](#jane_kitidempotencyidempotencystorerelease)
- [jane_kit.idempotency.InMemoryIdempotencyStore](#jane_kitidempotencyinmemoryidempotencystore)
- [jane_kit.idempotency.InMemoryIdempotencyStore.__init__](#jane_kitidempotencyinmemoryidempotencystore__init__)
- [jane_kit.idempotency.InMemoryIdempotencyStore.limits](#jane_kitidempotencyinmemoryidempotencystorelimits)
- [jane_kit.idempotency.InMemoryIdempotencyStore.__len__](#jane_kitidempotencyinmemoryidempotencystore__len__)
- [jane_kit.idempotency.InMemoryIdempotencyStore.begin](#jane_kitidempotencyinmemoryidempotencystorebegin)
- [jane_kit.idempotency.InMemoryIdempotencyStore.complete](#jane_kitidempotencyinmemoryidempotencystorecomplete)
- [jane_kit.idempotency.InMemoryIdempotencyStore.release](#jane_kitidempotencyinmemoryidempotencystorerelease)
- [jane_kit.idempotency.fingerprint](#jane_kitidempotencyfingerprint)
- [jane_kit.idempotency.run_idempotent](#jane_kitidempotencyrun_idempotent)
- [jane_kit.idempotency.idempotent](#jane_kitidempotencyidempotent)

## jane_kit.idempotency.IDEMPOTENCY_HEADER

**Константа.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:52](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L52).

```python
IDEMPOTENCY_HEADER = 'Idempotency-Key'
```

## jane_kit.idempotency.REPLAY_HEADER

**Константа.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:53](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L53).

```python
REPLAY_HEADER = 'Idempotency-Replayed'
```

## jane_kit.idempotency.IdempotencyLimits

**Клас.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:57](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L57).

```python
class IdempotencyLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [idempotency_ttl_seconds](jane_kit.idempotency.md#jane_kitidempotencyidempotencylimitsidempotency_ttl_seconds) | Поле | ні |
| [in_memory_max_entries](jane_kit.idempotency.md#jane_kitidempotencyidempotencylimitsin_memory_max_entries) | Поле | ні |
| [model_config](jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency.py:85](../../../../../../libs/jane-kit/tests/test_idempotency.py#L85).

```python
limits = IdempotencyLimits(idempotency_ttl_seconds=60, in_memory_max_entries=2)
```

Контекст і передумови: [libs/jane-kit/tests/test_wp00_contracts.py:91](../../../../../../libs/jane-kit/tests/test_wp00_contracts.py#L91).

```python
idempotency: IdempotencyLimits = IdempotencyLimits()
```

## jane_kit.idempotency.IdempotencyLimits.idempotency_ttl_seconds

**Поле.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:58](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L58).

```python
idempotency_ttl_seconds: int = contract_field('transfer.idempotency_ttl_seconds', 86400, ge=60)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'transfer.idempotency_ttl_seconds'",
  "ge": "60"
}
```

### Опис із вихідного коду

```text
Contract ``limits.transfer.idempotency_ttl_seconds``: how long a key is remembered.
```

## jane_kit.idempotency.IdempotencyLimits.in_memory_max_entries

**Поле.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:60](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L60).

```python
in_memory_max_entries: int = Field(default=10000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Only :class:`InMemoryIdempotencyStore`: the oldest entries are evicted beyond this.
```

## jane_kit.idempotency.IdempotencyKeyReused

**Клас.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:64](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L64).

```python
class IdempotencyKeyReused(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_kit.idempotency.md#jane_kitidempotencyidempotencykeyreusedcode) | Поле | ні |
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

## jane_kit.idempotency.IdempotencyKeyReused.code

**Поле.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:65](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L65).

```python
code = 'idempotency_key_reused'
```

Доступ: читання — так; запис — так.

## jane_kit.idempotency.IdempotencyInProgress

**Клас.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:68](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L68).

```python
class IdempotencyInProgress(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_kit.idempotency.md#jane_kitidempotencyidempotencyinprogresscode) | Поле | ні |
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

## jane_kit.idempotency.IdempotencyInProgress.code

**Поле.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:69](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L69).

```python
code = 'idempotency_in_progress'
```

Доступ: читання — так; запис — так.

## jane_kit.idempotency.StoredResponse

**Клас.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:73](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L73).

```python
class StoredResponse:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [status_code](jane_kit.idempotency.md#jane_kitidempotencystoredresponsestatus_code) | Поле | ні |
| [body](jane_kit.idempotency.md#jane_kitidempotencystoredresponsebody) | Поле | ні |
| [headers](jane_kit.idempotency.md#jane_kitidempotencystoredresponseheaders) | Поле | ні |
| [__init__](jane_kit.idempotency.md#jane_kitidempotencystoredresponse__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency.py:30](../../../../../../libs/jane-kit/tests/test_idempotency.py#L30).

```python
return StoredResponse(201, {"n": calls})
```

Контекст і передумови: [libs/jane-kit/tests/test_idempotency.py:43](../../../../../../libs/jane-kit/tests/test_idempotency.py#L43).

```python
return StoredResponse(200, {})
```

## jane_kit.idempotency.StoredResponse.__init__

**Конструктор dataclass.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:73](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L73).

```python
def __init__(self, status_code: int, body: Any, headers: Mapping[str, str] = <factory dict>) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `status_code` | `int` | `—` | positional-or-keyword |
| `body` | `Any` | `—` | positional-or-keyword |
| `headers` | `Mapping[str, str]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency.py:30](../../../../../../libs/jane-kit/tests/test_idempotency.py#L30).

```python
return StoredResponse(201, {"n": calls})
```

Контекст і передумови: [libs/jane-kit/tests/test_idempotency.py:43](../../../../../../libs/jane-kit/tests/test_idempotency.py#L43).

```python
return StoredResponse(200, {})
```

## jane_kit.idempotency.StoredResponse.status_code

**Поле.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:74](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L74).

```python
status_code: int
```

Доступ: читання — так; запис — ні.

## jane_kit.idempotency.StoredResponse.body

**Поле.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:75](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L75).

```python
body: Any
```

Доступ: читання — так; запис — ні.

## jane_kit.idempotency.StoredResponse.headers

**Поле.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:76](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L76).

```python
headers: Mapping[str, str] = field(default_factory=dict)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_kit.idempotency.IdempotencyRecord

**Клас.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:80](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L80).

```python
class IdempotencyRecord:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [key](jane_kit.idempotency.md#jane_kitidempotencyidempotencyrecordkey) | Поле | ні |
| [fingerprint](jane_kit.idempotency.md#jane_kitidempotencyidempotencyrecordfingerprint) | Поле | ні |
| [state](jane_kit.idempotency.md#jane_kitidempotencyidempotencyrecordstate) | Поле | ні |
| [expires_at](jane_kit.idempotency.md#jane_kitidempotencyidempotencyrecordexpires_at) | Поле | ні |
| [response](jane_kit.idempotency.md#jane_kitidempotencyidempotencyrecordresponse) | Поле | ні |
| [__init__](jane_kit.idempotency.md#jane_kitidempotencyidempotencyrecord__init__) | Конструктор dataclass | ні |

## jane_kit.idempotency.IdempotencyRecord.__init__

**Конструктор dataclass.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:80](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L80).

```python
def __init__(self, key: str, fingerprint: str, state: Literal['in_progress', 'completed'], expires_at: float, response: StoredResponse | None = None) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `key` | `str` | `—` | positional-or-keyword |
| `fingerprint` | `str` | `—` | positional-or-keyword |
| `state` | `Literal['in_progress', 'completed']` | `—` | positional-or-keyword |
| `expires_at` | `float` | `—` | positional-or-keyword |
| `response` | `StoredResponse \| None` | `None` | positional-or-keyword |

Результат: `None`.

## jane_kit.idempotency.IdempotencyRecord.key

**Поле.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:81](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L81).

```python
key: str
```

Доступ: читання — так; запис — так.

## jane_kit.idempotency.IdempotencyRecord.fingerprint

**Поле.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:82](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L82).

```python
fingerprint: str
```

Доступ: читання — так; запис — так.

## jane_kit.idempotency.IdempotencyRecord.state

**Поле.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:83](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L83).

```python
state: Literal['in_progress', 'completed']
```

Доступ: читання — так; запис — так.

## jane_kit.idempotency.IdempotencyRecord.expires_at

**Поле.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:84](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L84).

```python
expires_at: float
```

Доступ: читання — так; запис — так.

## jane_kit.idempotency.IdempotencyRecord.response

**Поле.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:85](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L85).

```python
response: StoredResponse | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.idempotency.IdempotencyStore

**Клас.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:88](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L88).

```python
class IdempotencyStore(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [begin](jane_kit.idempotency.md#jane_kitidempotencyidempotencystorebegin) | Метод | ні |
| [complete](jane_kit.idempotency.md#jane_kitidempotencyidempotencystorecomplete) | Метод | ні |
| [release](jane_kit.idempotency.md#jane_kitidempotencyidempotencystorerelease) | Метод | ні |

## jane_kit.idempotency.IdempotencyStore.begin

**Метод.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:89](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L89).

```python
async def begin(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |
| `fingerprint` | `str` | `—` | positional-or-keyword |
| `ttl_s` | `float` | `—` | positional-or-keyword |

Результат: `IdempotencyRecord | None`.

### Опис із вихідного коду

```text
Atomically claim ``key``. Return ``None`` if claimed now, else the existing record.
```

## jane_kit.idempotency.IdempotencyStore.complete

**Метод.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:93](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L93).

```python
async def complete(self, key: str, response: StoredResponse) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |
| `response` | `StoredResponse` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.idempotency.IdempotencyStore.release

**Метод.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:95](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L95).

```python
async def release(self, key: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Forget an in-progress key (the handler failed; a retry must be possible).
```

## jane_kit.idempotency.InMemoryIdempotencyStore

**Клас.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:100](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L100).

```python
class InMemoryIdempotencyStore:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.idempotency.md#jane_kitidempotencyinmemoryidempotencystore__init__) | Конструктор | ні |
| [limits](jane_kit.idempotency.md#jane_kitidempotencyinmemoryidempotencystorelimits) | Поле екземпляра | ні |
| [__len__](jane_kit.idempotency.md#jane_kitidempotencyinmemoryidempotencystore__len__) | Метод | ні |
| [begin](jane_kit.idempotency.md#jane_kitidempotencyinmemoryidempotencystorebegin) | Метод | ні |
| [complete](jane_kit.idempotency.md#jane_kitidempotencyinmemoryidempotencystorecomplete) | Метод | ні |
| [release](jane_kit.idempotency.md#jane_kitidempotencyinmemoryidempotencystorerelease) | Метод | ні |

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency.py:24](../../../../../../libs/jane-kit/tests/test_idempotency.py#L24).

```python
store = InMemoryIdempotencyStore()
```

Контекст і передумови: [libs/jane-kit/tests/test_idempotency.py:40](../../../../../../libs/jane-kit/tests/test_idempotency.py#L40).

```python
store = InMemoryIdempotencyStore()
```

## jane_kit.idempotency.InMemoryIdempotencyStore.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:101](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L101).

```python
def __init__(self, limits: IdempotencyLimits | None=None, clock: Callable[[], float]=time.monotonic):
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `limits` | `IdempotencyLimits \| None` | `None` | positional-or-keyword |
| `clock` | `Callable[[], float]` | `time.monotonic` | positional-or-keyword |

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency.py:24](../../../../../../libs/jane-kit/tests/test_idempotency.py#L24).

```python
store = InMemoryIdempotencyStore()
```

Контекст і передумови: [libs/jane-kit/tests/test_idempotency.py:40](../../../../../../libs/jane-kit/tests/test_idempotency.py#L40).

```python
store = InMemoryIdempotencyStore()
```

## jane_kit.idempotency.InMemoryIdempotencyStore.limits

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:102](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L102).

```python
self.limits = limits or IdempotencyLimits()
```

## jane_kit.idempotency.InMemoryIdempotencyStore.__len__

**Метод.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:108](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L108).

```python
def __len__(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

## jane_kit.idempotency.InMemoryIdempotencyStore.begin

**Метод.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:117](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L117).

```python
async def begin(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |
| `fingerprint` | `str` | `—` | positional-or-keyword |
| `ttl_s` | `float` | `—` | positional-or-keyword |

Результат: `IdempotencyRecord | None`.

## jane_kit.idempotency.InMemoryIdempotencyStore.complete

**Метод.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:128](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L128).

```python
async def complete(self, key: str, response: StoredResponse) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |
| `response` | `StoredResponse` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.idempotency.InMemoryIdempotencyStore.release

**Метод.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:135](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L135).

```python
async def release(self, key: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.idempotency.fingerprint

**Функція.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:142](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L142).

```python
def fingerprint(method: str, path: str, body: bytes, extra: Mapping[str, str] | None=None) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `method` | `str` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |
| `body` | `bytes` | `—` | positional-or-keyword |
| `extra` | `Mapping[str, str] \| None` | `None` | positional-or-keyword |

Результат: `str`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:138](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L138).

```python
assert await claims.store.begin("k", fingerprint("POST", "/v1/orders", original), 86_400) is None
```

Контекст і передумови: [services/registry/tests/test_service_ops.py:385](../../../../../../services/registry/tests/test_service_ops.py#L385).

```python
claimed = portal.call(comp.idempotency.begin, key, fingerprint("POST", path, raw), 86400.0)
```

## jane_kit.idempotency.run_idempotent

**Функція.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:152](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L152).

```python
async def run_idempotent(store: IdempotencyStore, key: str, fp: str, handler: Callable[[], Awaitable[StoredResponse]], limits: IdempotencyLimits | None=None) -> tuple[StoredResponse, bool]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `store` | `IdempotencyStore` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |
| `fp` | `str` | `—` | positional-or-keyword |
| `handler` | `Callable[[], Awaitable[StoredResponse]]` | `—` | positional-or-keyword |
| `limits` | `IdempotencyLimits \| None` | `None` | positional-or-keyword |

Результат: `tuple[StoredResponse, bool]`.

Явні `raise` у тілі: `IdempotencyInProgress`, `IdempotencyKeyReused`, `ValidationFailed`, `повторний raise`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Run ``handler`` once per key. Returns ``(response, replayed)``.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency.py:32](../../../../../../libs/jane-kit/tests/test_idempotency.py#L32).

```python
r1, replayed1 = await run_idempotent(store, "k", "fp", handler)
```

Контекст і передумови: [libs/jane-kit/tests/test_idempotency.py:33](../../../../../../libs/jane-kit/tests/test_idempotency.py#L33).

```python
r2, replayed2 = await run_idempotent(store, "k", "fp", handler)
```

## jane_kit.idempotency.idempotent

**Функція.** Код: [libs/jane-kit/src/jane_kit/idempotency.py:182](../../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L182).

```python
async def idempotent(request: Request, store: IdempotencyStore, handler: Callable[[], Awaitable[StoredResponse]], *, required: bool=True, limits: IdempotencyLimits | None=None) -> Response:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `request` | `Request` | `—` | positional-or-keyword |
| `store` | `IdempotencyStore` | `—` | positional-or-keyword |
| `handler` | `Callable[[], Awaitable[StoredResponse]]` | `—` | positional-or-keyword |
| `required` | `bool` | `True` | keyword-only |
| `limits` | `IdempotencyLimits \| None` | `None` | keyword-only |

Результат: `Response`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
FastAPI helper: wrap an endpoint body so it honours ``Idempotency-Key``.

A missing header is ``422 validation_failed`` (the contract marks the header required);
``required=False`` runs the handler directly instead.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency.py:123](../../../../../../libs/jane-kit/tests/test_idempotency.py#L123).

```python
return await idempotent(request, store, handler)
```

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:135](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L135).

```python
return await idempotent(request, claims.store, handler)
```
