# Модуль `jane_telegram_collector.stores`

> Згенеровано `scripts/docs_reference.py` з [services/telegram-collector/src/jane_telegram_collector/stores.py](../../../../../services/telegram-collector/src/jane_telegram_collector/stores.py). Не редагуйте вручну.

jane-kit's shared SQLite ``JobStore`` / ``IdempotencyStore`` on the collector's own state file (R17).

* jobs mirror their collections (``jane_kit.stores.sqlite.SqliteWorkJobStore``): the collection row (written in lease-fenced transactions) is the source of truth; only the instance holding a collection's lease writes its job, others may only request ``cancelling``; a terminal job status is stored only if the collection already has it; a run interrupted by a graceful shutdown leaves the collection ``running`` and resumable by another instance; a job cancelled before its run started ends the collection too;
* ``Idempotency-Key`` claims carry this instance, a token and a lease (``JANE_TELEGRAM_COLLECTOR_IDEMPOTENCY_LEASE_MS``) renewed by the resume loop.

## Класи

### Клас `SqliteIdempotencyStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.stores` |
| Успадкування | `_KitIdempotency` |
| Код | [stores.py:32](../../../../../services/telegram-collector/src/jane_telegram_collector/stores.py#L32) |

```python
class SqliteIdempotencyStore(_KitIdempotency): ...
```

#### Конструктор `SqliteIdempotencyStore.__init__`

```python
def __init__(self, state: StateStore, instance_id: str, in_progress_lease_s: float) -> None: ...
```

Код: [stores.py:33](../../../../../services/telegram-collector/src/jane_telegram_collector/stores.py#L33).

### Клас `SqliteJobStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.stores` |
| Успадкування | `SqliteWorkJobStore` |
| Код | [stores.py:22](../../../../../services/telegram-collector/src/jane_telegram_collector/stores.py#L22) |

```python
class SqliteJobStore(SqliteWorkJobStore): ...
```

Jobs of collections, shared by all instances on the state file.

#### Конструктор `SqliteJobStore.__init__`

```python
def __init__(self, state: StateStore, instance_id: str) -> None: ...
```

Код: [stores.py:25](../../../../../services/telegram-collector/src/jane_telegram_collector/stores.py#L25).
