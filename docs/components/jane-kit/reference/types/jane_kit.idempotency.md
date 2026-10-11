# Модуль `jane_kit.idempotency`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/idempotency.py](../../../../../libs/jane-kit/src/jane_kit/idempotency.py). Не редагуйте вручну.

Idempotent request handling by ``Idempotency-Key`` (TZ §11: a repeated technical delivery is a duplicate).

Semantics of the WP-00 contract (``common.yaml#/components/parameters/IdempotencyKey``):

* first request with a key runs the handler; the response is stored for ``transfer.idempotency_ttl_seconds``;
* same key + same request -> stored response with ``Idempotency-Replayed: true``, no new effect;
* same key + different request -> 422 ``idempotency_key_reused``;
* same key while the first request still runs -> 409 ``idempotency_in_progress`` (retryable);
* the key is 1-255 printable ASCII characters;
* if the handler raises, the key is released so the client can retry.

:class:`InMemoryIdempotencyStore` suits one instance and tests. Services running several instances use the shared stores of :mod:`jane_kit.stores` (PostgreSQL / SQLite: per-claim token, lease renewed by heartbeat, take-over of a stopped instance's claim) on their own database.

## Зміст

- [Клас `IdempotencyInProgress`](#клас-idempotencyinprogress)
- [Клас `IdempotencyKeyReused`](#клас-idempotencykeyreused)
- [Клас `IdempotencyLimits`](#клас-idempotencylimits)
- [Клас `IdempotencyRecord`](#клас-idempotencyrecord)
- [Клас `IdempotencyStore`](#клас-idempotencystore)
- [Клас `InMemoryIdempotencyStore`](#клас-inmemoryidempotencystore)
- [Клас `StoredResponse`](#клас-storedresponse)
- [Функція `fingerprint`](#функція-fingerprint)
- [Функція `idempotent`](#функція-idempotent)
- [Функція `run_idempotent`](#функція-run_idempotent)

## Класи

### Клас `IdempotencyInProgress`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.idempotency` |
| Успадкування | `JaneError` |
| Код | [idempotency.py:68](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L68) |

```python
class IdempotencyInProgress(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'idempotency_in_progress'` |  |

### Клас `IdempotencyKeyReused`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.idempotency` |
| Успадкування | `JaneError` |
| Код | [idempotency.py:64](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L64) |

```python
class IdempotencyKeyReused(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'idempotency_key_reused'` |  |

### Клас `IdempotencyLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.idempotency` |
| Успадкування | `Limits` |
| Код | [idempotency.py:57](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L57) |

```python
class IdempotencyLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `idempotency_ttl_seconds` | `int` | `contract_field('transfer.idempotency_ttl_seconds', 86400, ge=60)` | читання й запис | Contract ``limits.transfer.idempotency_ttl_seconds``: how long a key is remembered. |
| `in_memory_max_entries` | `int` | `Field(default=10000, ge=1)` | читання й запис | Only :class:`InMemoryIdempotencyStore`: the oldest entries are evicted beyond this. |

### Клас `IdempotencyRecord`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_kit.idempotency` |
| Код | [idempotency.py:80](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L80) |

```python
@dataclass
class IdempotencyRecord: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `key` | `str` | — | читання й запис |  |
| `fingerprint` | `str` | — | читання й запис |  |
| `state` | `Literal['in_progress', 'completed']` | — | читання й запис |  |
| `expires_at` | `float` | — | читання й запис |  |
| `response` | `StoredResponse \| None` | `None` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `IdempotencyStore`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_kit.idempotency` |
| Успадкування | `Protocol` |
| Код | [idempotency.py:88](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L88) |

```python
class IdempotencyStore(Protocol): ...
```

#### Метод `IdempotencyStore.begin`

```python
async def begin(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None: ...
```

Atomically claim ``key``. Return ``None`` if claimed now, else the existing record.

Код: [idempotency.py:89](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L89).

#### Метод `IdempotencyStore.complete`

```python
async def complete(self, key: str, response: StoredResponse) -> None: ...
```

Код: [idempotency.py:93](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L93).

#### Метод `IdempotencyStore.release`

```python
async def release(self, key: str) -> None: ...
```

Forget an in-progress key (the handler failed; a retry must be possible).

Код: [idempotency.py:95](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L95).

### Клас `InMemoryIdempotencyStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.idempotency` |
| Код | [idempotency.py:100](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L100) |

```python
class InMemoryIdempotencyStore: ...
```

#### Конструктор `InMemoryIdempotencyStore.__init__`

```python
def __init__(
    self,
    limits: IdempotencyLimits | None = None,
    clock: Callable[[], float] = time.monotonic,
): ...
```

Код: [idempotency.py:101](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L101).

#### Метод `InMemoryIdempotencyStore.__len__`

```python
def __len__(self) -> int: ...
```

Код: [idempotency.py:108](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L108).

#### Метод `InMemoryIdempotencyStore.begin`

```python
async def begin(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None: ...
```

Код: [idempotency.py:117](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L117).

#### Метод `InMemoryIdempotencyStore.complete`

```python
async def complete(self, key: str, response: StoredResponse) -> None: ...
```

Код: [idempotency.py:128](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L128).

#### Метод `InMemoryIdempotencyStore.release`

```python
async def release(self, key: str) -> None: ...
```

Код: [idempotency.py:135](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L135).

### Клас `StoredResponse`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_kit.idempotency` |
| Код | [idempotency.py:73](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L73) |

```python
@dataclass(frozen=True)
class StoredResponse: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `status_code` | `int` | — | читання |  |
| `body` | `Any` | — | читання |  |
| `headers` | `Mapping[str, str]` | `field(default_factory=dict)` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `fingerprint`

```python
def fingerprint(
    method: str,
    path: str,
    body: bytes,
    extra: Mapping[str, str] | None = None,
) -> str: ...
```

Код: [idempotency.py:142](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L142).

### Функція `idempotent`

```python
async def idempotent(
    request: Request,
    store: IdempotencyStore,
    handler: Callable[[], Awaitable[StoredResponse]],
    *,
    required: bool = True,
    limits: IdempotencyLimits | None = None,
) -> Response: ...
```

FastAPI helper: wrap an endpoint body so it honours ``Idempotency-Key``.

A missing header is ``422 validation_failed`` (the contract marks the header required); ``required=False`` runs the handler directly instead.

Винятки в коді функції: `ValidationFailed`.

Код: [idempotency.py:182](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L182).

### Функція `run_idempotent`

```python
async def run_idempotent(
    store: IdempotencyStore,
    key: str,
    fp: str,
    handler: Callable[[], Awaitable[StoredResponse]],
    limits: IdempotencyLimits | None = None,
) -> tuple[StoredResponse, bool]: ...
```

Run ``handler`` once per key. Returns ``(response, replayed)``.

Винятки в коді функції: `ValidationFailed`, `IdempotencyKeyReused`, `IdempotencyInProgress`.

Код: [idempotency.py:152](../../../../../libs/jane-kit/src/jane_kit/idempotency.py#L152).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `IDEMPOTENCY_HEADER` | — | `'Idempotency-Key'` |  |
| `REPLAY_HEADER` | — | `'Idempotency-Replayed'` |  |
