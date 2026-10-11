# Модуль `jane_kit.stores.sqlite`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/stores/sqlite.py](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py). Не редагуйте вручну.

``IdempotencyStore`` and ``JobStore`` in a service's own SQLite state file (R17).

For services whose instances share one state file on one host (the collectors; SQLite locking, WAL). The tables live next to the service's other tables; every write is one ``BEGIN IMMEDIATE`` transaction of the service's own connection (:class:`SqliteTx`), so it is atomic with respect to the other instances.

* :class:`SqliteIdempotencyStore` - the same semantics as the PostgreSQL store: per-claim token and lease renewed by :meth:`~SqliteIdempotencyStore.heartbeat`, take-over of an expired key or of a stopped instance's claim, token-fenced ``complete``/``release``. Times are epoch seconds (``REAL``).
* :class:`SqliteJobStore` - jobs with their own ``owner``/``lease_until`` (as :class:`~jane_kit.stores.postgres.PgJobStore`).
* :class:`SqliteWorkJobStore` - jobs that mirror a leased *work row* of the service (a collection of a collector): the work row's owner and status are the source of truth (:class:`WorkRows`). Only the work row's lease holder writes the job, others may only request ``cancelling``; a terminal job status is stored only when the work row already has it; a run that stopped without finishing (lost lease, graceful stop) never makes the job look finished, and resubmitting the same ``job_id`` (resume) keeps what the job recorded.

Existing tables are upgraded in place by :meth:`migrate` (missing columns added inside the transaction, so several processes may open the file at once).

## Зміст

- [Клас `SqliteDatabase`](#клас-sqlitedatabase)
- [Клас `SqliteIdempotencyStore`](#клас-sqliteidempotencystore)
- [Клас `SqliteJobStore`](#клас-sqlitejobstore)
- [Клас `SqliteTx`](#клас-sqlitetx)
- [Клас `SqliteWorkJobStore`](#клас-sqliteworkjobstore)
- [Клас `WorkRows`](#клас-workrows)

## Класи

### Клас `SqliteDatabase`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.stores.sqlite` |
| Код | [sqlite.py:75](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L75) |

```python
class SqliteDatabase: ...
```

A SQLite state file shared by the processes of one host (WAL, ``busy_timeout_ms`` lock wait).

#### Конструктор `SqliteDatabase.__init__`

```python
def __init__(self, path: Path, *, busy_timeout_ms: int) -> None: ...
```

Код: [sqlite.py:78](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L78).

#### Метод `SqliteDatabase.tx`

```python
@contextmanager
def tx(self) -> Iterator[sqlite3.Connection]: ...
```

Код: [sqlite.py:90](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L90).

#### Метод `SqliteDatabase.read`

```python
@contextmanager
def read(self) -> Iterator[sqlite3.Connection]: ...
```

The connection for single-statement reads (autocommit; no write lock).

Код: [sqlite.py:101](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L101).

#### Метод `SqliteDatabase.close`

```python
def close(self) -> None: ...
```

Код: [sqlite.py:106](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L106).

### Клас `SqliteIdempotencyStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.stores.sqlite` |
| Код | [sqlite.py:123](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L123) |

```python
class SqliteIdempotencyStore: ...
```

jane-kit ``IdempotencyStore`` on table ``table`` (``key``, ``fingerprint``, ``state``, ``expires_at``, ``response`` JSON text, ``lease_until``, ``owner``, ``token``).

``begin`` and its matching ``complete``/``release`` run in the same caller context (as in ``run_idempotent``); concurrent requests on this store keep separate tokens. Heartbeat is process-wide.

#### Конструктор `SqliteIdempotencyStore.__init__`

```python
def __init__(
    self,
    db: SqliteTx,
    *,
    owner: str,
    in_progress_lease_s: float,
    table: str = 'idempotency',
) -> None: ...
```

Винятки в коді методу: `ValueError`.

Код: [sqlite.py:131](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L131).

#### Метод `SqliteIdempotencyStore.migrate`

```python
def migrate(self) -> None: ...
```

Код: [sqlite.py:142](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L142).

#### Метод `SqliteIdempotencyStore.begin_sync`

```python
def begin_sync(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None: ...
```

Код: [sqlite.py:151](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L151).

#### Метод `SqliteIdempotencyStore.complete_sync`

```python
def complete_sync(self, key: str, response: StoredResponse) -> None: ...
```

Код: [sqlite.py:206](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L206).

#### Метод `SqliteIdempotencyStore.release_sync`

```python
def release_sync(self, key: str) -> None: ...
```

Код: [sqlite.py:226](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L226).

#### Метод `SqliteIdempotencyStore.heartbeat_sync`

```python
def heartbeat_sync(self) -> int: ...
```

Код: [sqlite.py:238](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L238).

#### Метод `SqliteIdempotencyStore.begin`

```python
async def begin(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None: ...
```

Код: [sqlite.py:253](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L253).

#### Метод `SqliteIdempotencyStore.complete`

```python
async def complete(self, key: str, response: StoredResponse) -> None: ...
```

Код: [sqlite.py:260](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L260).

#### Метод `SqliteIdempotencyStore.release`

```python
async def release(self, key: str) -> None: ...
```

Код: [sqlite.py:264](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L264).

#### Метод `SqliteIdempotencyStore.heartbeat`

```python
async def heartbeat(self) -> int: ...
```

Код: [sqlite.py:268](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L268).

### Клас `SqliteJobStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.stores.sqlite` |
| Успадкування | `_SqliteJobs` |
| Код | [sqlite.py:309](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L309) |

```python
class SqliteJobStore(_SqliteJobs): ...
```

jane-kit ``JobStore`` with its own ``owner``/``lease_until`` (epoch seconds), like the PostgreSQL store.

#### Конструктор `SqliteJobStore.__init__`

```python
def __init__(
    self,
    db: SqliteTx,
    *,
    owner: str,
    lease_s: float,
    retention_s: float,
    table: str = 'jobs',
    doc_column: str = 'doc',
) -> None: ...
```

Винятки в коді методу: `ValueError`.

Код: [sqlite.py:312](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L312).

#### Метод `SqliteJobStore.migrate`

```python
def migrate(self) -> None: ...
```

Код: [sqlite.py:331](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L331).

#### Метод `SqliteJobStore.create_sync`

```python
def create_sync(self, job: Job) -> None: ...
```

Винятки в коді методу: `Conflict`.

Код: [sqlite.py:339](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L339).

#### Метод `SqliteJobStore.get_sync`

```python
def get_sync(self, job_id: str) -> Job | None: ...
```

Код: [sqlite.py:366](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L366).

#### Метод `SqliteJobStore.save_sync`

```python
def save_sync(self, job: Job) -> None: ...
```

Код: [sqlite.py:377](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L377).

#### Метод `SqliteJobStore.heartbeat_sync`

```python
def heartbeat_sync(self) -> int: ...
```

Код: [sqlite.py:402](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L402).

#### Метод `SqliteJobStore.sweep_sync`

```python
def sweep_sync(self) -> int: ...
```

Код: [sqlite.py:418](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L418).

#### Метод `SqliteJobStore.heartbeat`

```python
async def heartbeat(self) -> int: ...
```

Код: [sqlite.py:429](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L429).

#### Метод `SqliteJobStore.sweep`

```python
async def sweep(self) -> int: ...
```

Код: [sqlite.py:432](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L432).

### Клас `SqliteTx`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_kit.stores.sqlite` |
| Успадкування | `Protocol` |
| Код | [sqlite.py:62](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L62) |

```python
class SqliteTx(Protocol): ...
```

#### Метод `SqliteTx.tx`

```python
def tx(self) -> AbstractContextManager[sqlite3.Connection]: ...
```

``BEGIN IMMEDIATE`` ... ``COMMIT`` (rollback on error) on the service's connection.

Код: [sqlite.py:63](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L63).

### Клас `SqliteWorkJobStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.stores.sqlite` |
| Успадкування | `_SqliteJobs` |
| Код | [sqlite.py:448](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L448) |

```python
class SqliteWorkJobStore(_SqliteJobs): ...
```

jane-kit ``JobStore`` whose jobs mirror the service's leased work rows (see the module docstring).

No lease of its own: the work row's lease is renewed by the run and taken over by another instance, which resumes the work and resubmits the job under the same ``job_id``.

#### Конструктор `SqliteWorkJobStore.__init__`

```python
def __init__(
    self,
    db: SqliteTx,
    work: WorkRows,
    *,
    owner: str,
    table: str = 'jobs',
    doc_column: str = 'body',
) -> None: ...
```

Код: [sqlite.py:455](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L455).

#### Метод `SqliteWorkJobStore.migrate`

```python
def migrate(self) -> None: ...
```

Код: [sqlite.py:468](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L468).

#### Метод `SqliteWorkJobStore.create_sync`

```python
def create_sync(self, job: Job) -> None: ...
```

Код: [sqlite.py:481](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L481).

#### Метод `SqliteWorkJobStore.save_sync`

```python
def save_sync(self, job: Job) -> None: ...
```

Код: [sqlite.py:522](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L522).

### Клас `WorkRows`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_kit.stores.sqlite` |
| Успадкування | `Protocol` |
| Код | [sqlite.py:436](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L436) |

```python
class WorkRows(Protocol): ...
```

The service's leased work rows (one per job, same id), read inside the job store's transaction.

#### Метод `WorkRows.work_row`

```python
def work_row(self, db: sqlite3.Connection, job_id: str) -> tuple[str | None, str] | None: ...
```

``(owner, status)`` of the work row, ``None`` if there is none.

Код: [sqlite.py:439](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L439).

#### Метод `WorkRows.cancel_unstarted`

```python
def cancel_unstarted(self, db: sqlite3.Connection, job_id: str, owner: str) -> bool: ...
```

End a work row that ``owner`` holds and that never started (``queued``) as ``cancelled``.

Код: [sqlite.py:443](../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L443).
