# Модуль `jane_kit.stores`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/stores/__init__.py](../../../../../libs/jane-kit/src/jane_kit/stores/__init__.py). Не редагуйте вручну.

Shared ``IdempotencyStore`` / ``JobStore`` implementations on a service's own database (R17).

* :mod:`jane_kit.stores.postgres` - :class:`~jane_kit.stores.postgres.PgIdempotencyStore`, :class:`~jane_kit.stores.postgres.PgJobStore` (needs ``psycopg``: ``jane-kit[postgres]``);
* :mod:`jane_kit.stores.sqlite` - :class:`~jane_kit.stores.sqlite.SqliteIdempotencyStore`, :class:`~jane_kit.stores.sqlite.SqliteJobStore`, :class:`~jane_kit.stores.sqlite.SqliteWorkJobStore`.

The in-memory stores stay in :mod:`jane_kit.idempotency` / :mod:`jane_kit.jobs` (one instance, tests). Every store keeps the contract semantics (same key + same request -> stored response, other request -> 422, still running -> 409; job statuses and cancellation) and the write rules of :func:`jane_kit.jobs.decide_save`.

Leases are renewed by the instance's heartbeat (:func:`heartbeat_loop` with :class:`LeaseLimits` or the service's own lease settings); the data of each service stays in its own database (ADR-0009).

## Класи

### Клас `ClaimLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.stores` |
| Успадкування | `Limits` |
| Код | [__init__.py:32](../../../../../libs/jane-kit/src/jane_kit/stores/__init__.py#L32) |

```python
class ClaimLimits(Limits): ...
```

Leases of ``Idempotency-Key`` claims (a service without shared jobs, e.g. the orchestrator).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `in_progress_lease_ms` | `int` | `Field(default=900000, ge=1000)` | читання й запис | An ``Idempotency-Key`` claim not renewed for this long (its instance stopped) can be claimed again. |
| `heartbeat_interval_ms` | `int` | `Field(default=15000, ge=100)` | читання й запис | How often an instance renews its leases (keep well below them). |

### Клас `LeaseLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.stores` |
| Успадкування | `ClaimLimits` |
| Код | [__init__.py:41](../../../../../libs/jane-kit/src/jane_kit/stores/__init__.py#L41) |

```python
class LeaseLimits(ClaimLimits): ...
```

Leases of the shared stores (one group per service, e.g. ``limits.state``): claims and jobs.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `job_lease_ms` | `int` | `Field(default=60000, ge=1000)` | читання й запис | A job whose instance did not renew its lease for this long ends ``failed`` (retryable). |

## Функції

### Функція `heartbeat_loop`

```python
async def heartbeat_loop(
    beats: Iterable[Callable[[], Awaitable[Any]]],
    interval_s: float,
    *,
    name: str = 'store',
) -> None: ...
```

Call every ``beat`` (``store.heartbeat``, ``store.gc``...) each ``interval_s`` until cancelled; a failed beat is logged and retried at the next tick (the lease covers a few missed beats).

Код: [__init__.py:48](../../../../../libs/jane-kit/src/jane_kit/stores/__init__.py#L48).
