# Модуль `jane_web_collector.stores`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/stores.py](../../../../../services/web-collector/src/jane_web_collector/stores.py). Не редагуйте вручну.

jane-kit's shared SQLite ``JobStore`` / ``IdempotencyStore`` on the collector's own state file (R17).

* jobs mirror their collections (``jane_kit.stores.sqlite.SqliteWorkJobStore``): only the instance holding a collection's lease writes its job, others may only request ``cancelling``; a terminal job status is stored only when the collection already has it (written by the run's final lease-fenced transaction or by the owner on failure/cancellation), so a run that stopped without finishing (lease lost, graceful shutdown) never makes the job look finished; a job cancelled before its run started ends the collection too;
* ``Idempotency-Key`` claims carry this instance, a token and a lease (``JANE_WEB_COLLECTOR_IDEMPOTENCY_LEASE_MS``) renewed by the resume loop: a claim of a killed instance can be taken over after the lease instead of the key's whole TTL.

## Класи

### Клас `SqliteIdempotencyStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.stores` |
| Успадкування | `_KitIdempotency` |
| Код | [stores.py:33](../../../../../services/web-collector/src/jane_web_collector/stores.py#L33) |

```python
class SqliteIdempotencyStore(_KitIdempotency): ...
```

#### Конструктор `SqliteIdempotencyStore.__init__`

```python
def __init__(self, state: StateStore, instance_id: str, in_progress_lease_s: float) -> None: ...
```

Код: [stores.py:34](../../../../../services/web-collector/src/jane_web_collector/stores.py#L34).

### Клас `SqliteJobStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.stores` |
| Успадкування | `SqliteWorkJobStore` |
| Код | [stores.py:23](../../../../../services/web-collector/src/jane_web_collector/stores.py#L23) |

```python
class SqliteJobStore(SqliteWorkJobStore): ...
```

Jobs of collections, shared by all instances on the state file.

#### Конструктор `SqliteJobStore.__init__`

```python
def __init__(self, state: StateStore, instance_id: str) -> None: ...
```

Код: [stores.py:26](../../../../../services/web-collector/src/jane_web_collector/stores.py#L26).
