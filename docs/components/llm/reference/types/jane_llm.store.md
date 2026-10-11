# Модуль `jane_llm.store`

> Згенеровано `scripts/docs_reference.py` з [services/llm/src/jane_llm/store.py](../../../../../services/llm/src/jane_llm/store.py). Не редагуйте вручну.

Persistent state of the LLM service.

Everything that must be shared between instances lives here: configuration documents (providers, model aliases, budget definitions, connections), budget/rate counters with reservations, the usage ledger, handler results, ``Idempotency-Key`` records and jobs. The last two are jane-kit's shared stores (R17): ``store.idempotency`` / ``store.jobs`` - in-memory ones for :class:`MemoryStore`, ``jane_kit.stores.postgres`` (token-fenced claims, job leases renewed by the heartbeat, take-over after a crash) for :class:`PostgresStore`.

* :class:`PostgresStore` — the production store (own schema, ``SELECT ... FOR UPDATE`` on counter rows, so several instances never overspend a budget together);
* :class:`MemoryStore` — the same semantics in one process, for unit tests and demos only.

The store API is synchronous (psycopg's sync pool works the same on Windows and Linux); async code calls it through :func:`asyncio.to_thread`.

## Зміст

- [Клас `CounterKey`](#клас-counterkey)
- [Клас `BudgetCheck`](#клас-budgetcheck)
- [Клас `RateCheck`](#клас-ratecheck)
- [Клас `UsageRecord`](#клас-usagerecord)
- [Клас `UsageQuery`](#клас-usagequery)
- [Клас `UsageRow`](#клас-usagerow)
- [Клас `BudgetExceeded`](#клас-budgetexceeded)
- [Клас `RateExceeded`](#клас-rateexceeded)
- [Клас `Store`](#клас-store)
- [Клас `MemoryStore`](#клас-memorystore)
- [Клас `PostgresStore`](#клас-postgresstore)
- [Функція `iter_keys`](#функція-iter_keys)

## Класи

### Клас `CounterKey`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_llm.store` |
| Код | [store.py:40](../../../../../services/llm/src/jane_llm/store.py#L40) |

```python
@dataclass(frozen=True)
class CounterKey: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `scope_type` | `str` | — | читання |  |
| `scope_id` | `str` | — | читання |  |
| `window` | `str` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `CounterKey.as_tuple`

```python
def as_tuple(self) -> tuple[str, str, str]: ...
```

Код: [store.py:45](../../../../../services/llm/src/jane_llm/store.py#L45).

### Клас `BudgetCheck`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_llm.store` |
| Код | [store.py:50](../../../../../services/llm/src/jane_llm/store.py#L50) |

```python
@dataclass(frozen=True)
class BudgetCheck: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `key` | `CounterKey` | — | читання |  |
| `limit` | `float` | — | читання |  |
| `currency` | `str` | — | читання |  |
| `period` | `str` | — | читання |  |
| `resets_at` | `datetime \| None` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `RateCheck`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_llm.store` |
| Код | [store.py:59](../../../../../services/llm/src/jane_llm/store.py#L59) |

```python
@dataclass(frozen=True)
class RateCheck: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `key` | `CounterKey` | — | читання |  |
| `limit` | `int` | — | читання |  |
| `retry_after_seconds` | `int` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `UsageRecord`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_llm.store` |
| Код | [store.py:66](../../../../../services/llm/src/jane_llm/store.py#L66) |

```python
@dataclass
class UsageRecord: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `completion_id` | `str` | — | читання й запис |  |
| `created_at` | `datetime` | — | читання й запис |  |
| `provider_id` | `str` | — | читання й запис |  |
| `model_id` | `str` | — | читання й запис |  |
| `purpose` | `str` | — | читання й запис |  |
| `source_id` | `str \| None` | — | читання й запис |  |
| `task_id` | `str \| None` | — | читання й запис |  |
| `run_id` | `str \| None` | — | читання й запис |  |
| `input_tokens` | `int` | — | читання й запис |  |
| `output_tokens` | `int` | — | читання й запис |  |
| `cost` | `float` | — | читання й запис |  |
| `currency` | `str` | — | читання й запис |  |
| `test_mode` | `bool` | — | читання й запис |  |
| `outcome` | `str` | `'ok'` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `UsageQuery`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_llm.store` |
| Код | [store.py:84](../../../../../services/llm/src/jane_llm/store.py#L84) |

```python
@dataclass
class UsageQuery: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `scope_type` | `str \| None` | `None` | читання й запис |  |
| `scope_id` | `str \| None` | `None` | читання й запис |  |
| `since` | `datetime \| None` | `None` | читання й запис |  |
| `until` | `datetime \| None` | `None` | читання й запис |  |
| `group_by` | `str` | `'day'` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `UsageRow`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_llm.store` |
| Код | [store.py:93](../../../../../services/llm/src/jane_llm/store.py#L93) |

```python
@dataclass
class UsageRow: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `requests` | `int` | `0` | читання й запис |  |
| `input_tokens` | `int` | `0` | читання й запис |  |
| `output_tokens` | `int` | `0` | читання й запис |  |
| `cost` | `float` | `0.0` | читання й запис |  |
| `currency` | `str` | `'USD'` | читання й запис |  |
| `period_start` | `datetime \| None` | `None` | читання й запис |  |
| `scope_type` | `str \| None` | `None` | читання й запис |  |
| `scope_id` | `str \| None` | `None` | читання й запис |  |
| `model` | `str \| None` | `None` | читання й запис |  |
| `purpose` | `str \| None` | `None` | читання й запис |  |
| `test_mode` | `bool \| None` | `None` | читання й запис |  |
| `extra` | `dict[str, Any]` | `field(default_factory=dict)` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `BudgetExceeded`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_llm.store` |
| Успадкування | `Exception` |
| Код | [store.py:108](../../../../../services/llm/src/jane_llm/store.py#L108) |

```python
class BudgetExceeded(Exception): ...
```

#### Конструктор `BudgetExceeded.__init__`

```python
def __init__(self, check: BudgetCheck, spent: float, reserved: float, requested: float) -> None: ...
```

Код: [store.py:109](../../../../../services/llm/src/jane_llm/store.py#L109).

### Клас `RateExceeded`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_llm.store` |
| Успадкування | `Exception` |
| Код | [store.py:114](../../../../../services/llm/src/jane_llm/store.py#L114) |

```python
class RateExceeded(Exception): ...
```

#### Конструктор `RateExceeded.__init__`

```python
def __init__(self, check: RateCheck) -> None: ...
```

Код: [store.py:115](../../../../../services/llm/src/jane_llm/store.py#L115).

### Клас `Store`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_llm.store` |
| Успадкування | `Protocol` |
| Код | [store.py:121](../../../../../services/llm/src/jane_llm/store.py#L121) |

```python
class Store(Protocol): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `idempotency` | `IdempotencyStore` | — | читання й запис |  |
| `jobs` | `JobStore` | — | читання й запис |  |

#### Метод `Store.migrate`

```python
def migrate(self) -> None: ...
```

Код: [store.py:122](../../../../../services/llm/src/jane_llm/store.py#L122).

#### Метод `Store.ping`

```python
def ping(self) -> bool: ...
```

Код: [store.py:123](../../../../../services/llm/src/jane_llm/store.py#L123).

#### Метод `Store.close`

```python
def close(self) -> None: ...
```

Код: [store.py:124](../../../../../services/llm/src/jane_llm/store.py#L124).

#### Метод `Store.get_doc`

```python
def get_doc(self, kind: ConfigKind, key: str) -> dict[str, Any] | None: ...
```

Код: [store.py:127](../../../../../services/llm/src/jane_llm/store.py#L127).

#### Метод `Store.list_docs`

```python
def list_docs(self, kind: ConfigKind) -> list[dict[str, Any]]: ...
```

Код: [store.py:128](../../../../../services/llm/src/jane_llm/store.py#L128).

#### Метод `Store.put_doc`

```python
def put_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool: ...
```

Create or replace; returns True if created.

Код: [store.py:129](../../../../../services/llm/src/jane_llm/store.py#L129).

#### Метод `Store.seed_doc`

```python
def seed_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool: ...
```

Create only if absent; returns True if created.

Код: [store.py:133](../../../../../services/llm/src/jane_llm/store.py#L133).

#### Метод `Store.delete_doc`

```python
def delete_doc(self, kind: ConfigKind, key: str) -> bool: ...
```

Код: [store.py:137](../../../../../services/llm/src/jane_llm/store.py#L137).

#### Метод `Store.reserve`

```python
def reserve(
    self,
    reservation_id: str,
    amount: float,
    budgets: list[BudgetCheck],
    rates: list[RateCheck],
    now: datetime,
    stale_after: timedelta,
) -> None: ...
```

Atomically check budgets (spent + reserved + amount &lt;= limit) and rates, then reserve.

Код: [store.py:140](../../../../../services/llm/src/jane_llm/store.py#L140).

#### Метод `Store.settle`

```python
def settle(self, reservation_id: str, cost: float, usage: UsageRecord | None) -> None: ...
```

Replace a reservation by the actual cost and append the usage record.

Код: [store.py:152](../../../../../services/llm/src/jane_llm/store.py#L152).

#### Метод `Store.release`

```python
def release(self, reservation_id: str) -> None: ...
```

Код: [store.py:156](../../../../../services/llm/src/jane_llm/store.py#L156).

#### Метод `Store.counter`

```python
def counter(self, key: CounterKey) -> tuple[float, float]: ...
```

``(spent, reserved)`` of a counter row (zeros if absent).

Код: [store.py:157](../../../../../services/llm/src/jane_llm/store.py#L157).

#### Метод `Store.usage`

```python
def usage(self, query: UsageQuery) -> list[UsageRow]: ...
```

Код: [store.py:161](../../../../../services/llm/src/jane_llm/store.py#L161).

#### Метод `Store.save_invocation`

```python
def save_invocation(self, invocation_id: str, result: dict[str, Any]) -> None: ...
```

Код: [store.py:164](../../../../../services/llm/src/jane_llm/store.py#L164).

#### Метод `Store.get_invocation`

```python
def get_invocation(self, invocation_id: str) -> dict[str, Any] | None: ...
```

Код: [store.py:165](../../../../../services/llm/src/jane_llm/store.py#L165).

### Клас `MemoryStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.store` |
| Код | [store.py:219](../../../../../services/llm/src/jane_llm/store.py#L219) |

```python
class MemoryStore: ...
```

In-process store with the same semantics as :class:`PostgresStore` (tests, demos).

#### Конструктор `MemoryStore.__init__`

```python
def __init__(
    self,
    jobs: JobLimits | None = None,
    idempotency: IdempotencyLimits | None = None,
) -> None: ...
```

Код: [store.py:222](../../../../../services/llm/src/jane_llm/store.py#L222).

#### Метод `MemoryStore.migrate`

```python
def migrate(self) -> None: ...
```

Код: [store.py:232](../../../../../services/llm/src/jane_llm/store.py#L232).

#### Метод `MemoryStore.ping`

```python
def ping(self) -> bool: ...
```

Код: [store.py:235](../../../../../services/llm/src/jane_llm/store.py#L235).

#### Метод `MemoryStore.close`

```python
def close(self) -> None: ...
```

Код: [store.py:238](../../../../../services/llm/src/jane_llm/store.py#L238).

#### Метод `MemoryStore.get_doc`

```python
def get_doc(self, kind: ConfigKind, key: str) -> dict[str, Any] | None: ...
```

Код: [store.py:241](../../../../../services/llm/src/jane_llm/store.py#L241).

#### Метод `MemoryStore.list_docs`

```python
def list_docs(self, kind: ConfigKind) -> list[dict[str, Any]]: ...
```

Код: [store.py:246](../../../../../services/llm/src/jane_llm/store.py#L246).

#### Метод `MemoryStore.put_doc`

```python
def put_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool: ...
```

Код: [store.py:250](../../../../../services/llm/src/jane_llm/store.py#L250).

#### Метод `MemoryStore.seed_doc`

```python
def seed_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool: ...
```

Код: [store.py:256](../../../../../services/llm/src/jane_llm/store.py#L256).

#### Метод `MemoryStore.delete_doc`

```python
def delete_doc(self, kind: ConfigKind, key: str) -> bool: ...
```

Код: [store.py:263](../../../../../services/llm/src/jane_llm/store.py#L263).

#### Метод `MemoryStore.reserve`

```python
def reserve(
    self,
    reservation_id: str,
    amount: float,
    budgets: list[BudgetCheck],
    rates: list[RateCheck],
    now: datetime,
    stale_after: timedelta,
) -> None: ...
```

Винятки в коді методу: `BudgetExceeded`, `RateExceeded`.

Код: [store.py:276](../../../../../services/llm/src/jane_llm/store.py#L276).

#### Метод `MemoryStore.settle`

```python
def settle(self, reservation_id: str, cost: float, usage: UsageRecord | None) -> None: ...
```

Код: [store.py:302](../../../../../services/llm/src/jane_llm/store.py#L302).

#### Метод `MemoryStore.release`

```python
def release(self, reservation_id: str) -> None: ...
```

Код: [store.py:314](../../../../../services/llm/src/jane_llm/store.py#L314).

#### Метод `MemoryStore.counter`

```python
def counter(self, key: CounterKey) -> tuple[float, float]: ...
```

Код: [store.py:322](../../../../../services/llm/src/jane_llm/store.py#L322).

#### Метод `MemoryStore.usage`

```python
def usage(self, query: UsageQuery) -> list[UsageRow]: ...
```

Код: [store.py:327](../../../../../services/llm/src/jane_llm/store.py#L327).

#### Метод `MemoryStore.save_invocation`

```python
def save_invocation(self, invocation_id: str, result: dict[str, Any]) -> None: ...
```

Код: [store.py:342](../../../../../services/llm/src/jane_llm/store.py#L342).

#### Метод `MemoryStore.get_invocation`

```python
def get_invocation(self, invocation_id: str) -> dict[str, Any] | None: ...
```

Код: [store.py:346](../../../../../services/llm/src/jane_llm/store.py#L346).

### Клас `PostgresStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.store` |
| Код | [store.py:375](../../../../../services/llm/src/jane_llm/store.py#L375) |

```python
class PostgresStore: ...
```

Store in the service's own PostgreSQL schema; safe for several instances.

#### Конструктор `PostgresStore.__init__`

```python
def __init__(
    self,
    dsn: str,
    schema: str,
    *,
    min_size: int,
    max_size: int,
    owner: str | None = None,
    leases: LeaseLimits | None = None,
    job_retention_s: float | None = None,
) -> None: ...
```

Код: [store.py:378](../../../../../services/llm/src/jane_llm/store.py#L378).

#### Метод `PostgresStore.migrate`

```python
def migrate(self) -> None: ...
```

Код: [store.py:425](../../../../../services/llm/src/jane_llm/store.py#L425).

#### Метод `PostgresStore.ping`

```python
def ping(self) -> bool: ...
```

Код: [store.py:433](../../../../../services/llm/src/jane_llm/store.py#L433).

#### Метод `PostgresStore.close`

```python
def close(self) -> None: ...
```

Код: [store.py:438](../../../../../services/llm/src/jane_llm/store.py#L438).

#### Метод `PostgresStore.get_doc`

```python
def get_doc(self, kind: ConfigKind, key: str) -> dict[str, Any] | None: ...
```

Код: [store.py:442](../../../../../services/llm/src/jane_llm/store.py#L442).

#### Метод `PostgresStore.list_docs`

```python
def list_docs(self, kind: ConfigKind) -> list[dict[str, Any]]: ...
```

Код: [store.py:448](../../../../../services/llm/src/jane_llm/store.py#L448).

#### Метод `PostgresStore.put_doc`

```python
def put_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool: ...
```

Код: [store.py:453](../../../../../services/llm/src/jane_llm/store.py#L453).

#### Метод `PostgresStore.seed_doc`

```python
def seed_doc(self, kind: ConfigKind, key: str, doc: dict[str, Any]) -> bool: ...
```

Код: [store.py:464](../../../../../services/llm/src/jane_llm/store.py#L464).

#### Метод `PostgresStore.delete_doc`

```python
def delete_doc(self, kind: ConfigKind, key: str) -> bool: ...
```

Код: [store.py:473](../../../../../services/llm/src/jane_llm/store.py#L473).

#### Метод `PostgresStore.reserve`

```python
def reserve(
    self,
    reservation_id: str,
    amount: float,
    budgets: list[BudgetCheck],
    rates: list[RateCheck],
    now: datetime,
    stale_after: timedelta,
) -> None: ...
```

Винятки в коді методу: `BudgetExceeded`, `RateExceeded`.

Код: [store.py:494](../../../../../services/llm/src/jane_llm/store.py#L494).

#### Метод `PostgresStore.settle`

```python
def settle(self, reservation_id: str, cost: float, usage: UsageRecord | None) -> None: ...
```

Код: [store.py:576](../../../../../services/llm/src/jane_llm/store.py#L576).

#### Метод `PostgresStore.release`

```python
def release(self, reservation_id: str) -> None: ...
```

Код: [store.py:587](../../../../../services/llm/src/jane_llm/store.py#L587).

#### Метод `PostgresStore.counter`

```python
def counter(self, key: CounterKey) -> tuple[float, float]: ...
```

Код: [store.py:591](../../../../../services/llm/src/jane_llm/store.py#L591).

#### Метод `PostgresStore.usage`

```python
def usage(self, query: UsageQuery) -> list[UsageRow]: ...
```

Код: [store.py:601](../../../../../services/llm/src/jane_llm/store.py#L601).

#### Метод `PostgresStore.save_invocation`

```python
def save_invocation(self, invocation_id: str, result: dict[str, Any]) -> None: ...
```

Код: [store.py:651](../../../../../services/llm/src/jane_llm/store.py#L651).

#### Метод `PostgresStore.get_invocation`

```python
def get_invocation(self, invocation_id: str) -> dict[str, Any] | None: ...
```

Код: [store.py:659](../../../../../services/llm/src/jane_llm/store.py#L659).

## Функції

### Функція `iter_keys`

```python
def iter_keys(checks: Iterable[BudgetCheck]) -> list[CounterKey]: ...
```

Код: [store.py:668](../../../../../services/llm/src/jane_llm/store.py#L668).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `ConfigKind` | — | `Literal['provider', 'alias', 'budget', 'connection']` |  |
