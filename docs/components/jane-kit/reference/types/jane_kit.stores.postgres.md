# Модуль `jane_kit.stores.postgres`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/stores/postgres.py](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py). Не редагуйте вручну.

``IdempotencyStore`` and ``JobStore`` in a service's own PostgreSQL database (R17).

Several instances of a service share these tables; each service keeps them in its **own** database/schema (ADR-0009) - the code is shared, the data is not.

* :class:`PgIdempotencyStore` - ``Idempotency-Key`` records. A claim (``in_progress``) carries the claiming instance (``owner``), a per-claim ``token`` and a lease (``lease_until``) that :meth:`~PgIdempotencyStore.heartbeat` renews while the request still runs in this process. An expired key, or the claim of a stopped instance (lease over), is claimed again; ``complete``/``release`` are fenced by the token, so a request whose claim was taken over cannot overwrite the new claim.
* :class:`PgJobStore` - jobs of :class:`~jane_kit.jobs.JobRunner`: ``owner`` + ``lease_until`` renewed by :meth:`~PgJobStore.heartbeat` for the jobs this process runs; writes follow :func:`jane_kit.jobs.decide_save` under ``SELECT ... FOR UPDATE``; a job whose lease expired ends ``failed`` (retryable ``service_unavailable``) or ``cancelled`` when read (:meth:`~PgJobStore.get`), listed (:meth:`~PgJobStore.page`) or swept (:meth:`~PgJobStore.sweep`). Finished jobs are purged after ``job_retention_seconds``.

Existing tables are migrated in place (:meth:`ddl` - ``CREATE ... IF NOT EXISTS`` / ``ADD COLUMN IF NOT EXISTS``, run by :func:`migrate` under an advisory lock, so instances may start together). Column layouts of earlier services are kept (``layout="json"`` - one ``response`` column; ``doc_column`` - the job document column), so their rows stay readable without a data copy.

psycopg is used synchronously (the async driver needs a selector event loop, not the Windows default); the async methods run it in worker threads (:func:`asyncio.to_thread`).

## Зміст

- [Клас `PgDatabase`](#клас-pgdatabase)
- [Клас `PgIdempotencyStore`](#клас-pgidempotencystore)
- [Клас `PgJobStore`](#клас-pgjobstore)
- [Функція `migrate`](#функція-migrate)
- [Функція `pool_tx`](#функція-pool_tx)

## Класи

### Клас `PgDatabase`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.stores.postgres` |
| Код | [postgres.py:115](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L115) |

```python
class PgDatabase: ...
```

A psycopg pool of the service's own database (``autocommit``; transactions via :meth:`tx`).

#### Конструктор `PgDatabase.__init__`

```python
def __init__(
    self,
    dsn: str,
    *,
    max_size: int,
    connect_timeout_ms: int,
    min_size: int = 0,
) -> None: ...
```

Код: [postgres.py:118](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L118).

#### Метод `PgDatabase.open`

```python
def open(self) -> None: ...
```

Код: [postgres.py:132](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L132).

#### Метод `PgDatabase.close`

```python
def close(self) -> None: ...
```

Код: [postgres.py:135](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L135).

#### Метод `PgDatabase.ping`

```python
def ping(self) -> bool: ...
```

Код: [postgres.py:138](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L138).

### Клас `PgIdempotencyStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.stores.postgres` |
| Код | [postgres.py:145](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L145) |

```python
class PgIdempotencyStore: ...
```

jane-kit ``IdempotencyStore`` on table ``table`` (in ``schema``, or on the connection's search path).

``layout``: ``"split"`` - response in ``status_code``/``body``/``headers`` columns; ``"json"`` - one ``response`` jsonb column (``{"status_code", "body", "headers"}``). ``in_progress_lease_s``: how long a claim survives without :meth:`heartbeat` (a stopped instance releases its keys after this).

``begin`` and its matching ``complete``/``release`` run in the same caller context (as in ``run_idempotent``); concurrent requests on this store keep separate tokens. Heartbeat is process-wide.

#### Конструктор `PgIdempotencyStore.__init__`

```python
def __init__(
    self,
    tx: PgConnect,
    *,
    owner: str,
    in_progress_lease_s: float,
    table: str = 'idempotency',
    schema: str | None = None,
    layout: Literal['split', 'json'] = 'split',
    gc_batch: int = 500,
) -> None: ...
```

Винятки в коді методу: `ValueError`.

Код: [postgres.py:156](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L156).

#### Метод `PgIdempotencyStore.ddl`

```python
def ddl(self) -> list[sql.Composed]: ...
```

Код: [postgres.py:178](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L178).

#### Метод `PgIdempotencyStore.begin_sync`

```python
def begin_sync(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None: ...
```

Код: [postgres.py:214](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L214).

#### Метод `PgIdempotencyStore.complete_sync`

```python
def complete_sync(self, key: str, response: StoredResponse) -> None: ...
```

Код: [postgres.py:265](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L265).

#### Метод `PgIdempotencyStore.release_sync`

```python
def release_sync(self, key: str) -> None: ...
```

Код: [postgres.py:290](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L290).

#### Метод `PgIdempotencyStore.heartbeat_sync`

```python
def heartbeat_sync(self) -> int: ...
```

Renew the leases of the claims this process still holds (not those of a previous start).

Код: [postgres.py:304](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L304).

#### Метод `PgIdempotencyStore.gc_sync`

```python
def gc_sync(self) -> int: ...
```

Delete up to ``gc_batch`` expired keys (any instance; locked rows are skipped).

Код: [postgres.py:321](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L321).

#### Метод `PgIdempotencyStore.begin`

```python
async def begin(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None: ...
```

Код: [postgres.py:336](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L336).

#### Метод `PgIdempotencyStore.complete`

```python
async def complete(self, key: str, response: StoredResponse) -> None: ...
```

Код: [postgres.py:343](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L343).

#### Метод `PgIdempotencyStore.release`

```python
async def release(self, key: str) -> None: ...
```

Код: [postgres.py:347](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L347).

#### Метод `PgIdempotencyStore.heartbeat`

```python
async def heartbeat(self) -> int: ...
```

Код: [postgres.py:351](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L351).

#### Метод `PgIdempotencyStore.gc`

```python
async def gc(self) -> int: ...
```

Код: [postgres.py:354](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L354).

### Клас `PgJobStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.stores.postgres` |
| Код | [postgres.py:359](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L359) |

```python
class PgJobStore: ...
```

jane-kit ``JobStore`` on table ``table`` (columns ``job_id``, ``doc_column`` jsonb, ``owner``, ``lease_until``, ``finished_at``, ``updated_at``); see the module docstring for the rules.

#### Конструктор `PgJobStore.__init__`

```python
def __init__(
    self,
    tx: PgConnect,
    *,
    owner: str,
    lease_s: float,
    retention_s: float,
    table: str = 'jobs',
    schema: str | None = None,
    doc_column: str = 'doc',
) -> None: ...
```

Винятки в коді методу: `ValueError`.

Код: [postgres.py:363](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L363).

#### Метод `PgJobStore.ddl`

```python
def ddl(self) -> list[sql.Composed]: ...
```

Код: [postgres.py:386](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L386).

#### Метод `PgJobStore.create_sync`

```python
def create_sync(self, job: Job) -> None: ...
```

Винятки в коді методу: `Conflict`.

Код: [postgres.py:426](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L426).

#### Метод `PgJobStore.get_sync`

```python
def get_sync(self, job_id: str) -> Job | None: ...
```

Код: [postgres.py:481](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L481).

#### Метод `PgJobStore.save_sync`

```python
def save_sync(self, job: Job) -> None: ...
```

Код: [postgres.py:505](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L505).

#### Метод `PgJobStore.heartbeat_sync`

```python
def heartbeat_sync(self) -> int: ...
```

Renew the leases of the jobs this process runs (never those of a previous start).

Код: [postgres.py:539](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L539).

#### Метод `PgJobStore.sweep_sync`

```python
def sweep_sync(self) -> int: ...
```

End every job whose lease expired (any owner); returns how many.

Код: [postgres.py:558](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L558).

#### Метод `PgJobStore.release_owned_sync`

```python
def release_owned_sync(self, reason: str) -> int: ...
```

Graceful stop, after the runner cancelled this instance's jobs: unfinished jobs of this owner end ``cancelled`` and cancelled ones without a recorded cancellation get ``reason``.

Код: [postgres.py:563](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L563).

#### Метод `PgJobStore.page_sync`

```python
def page_sync(
    self,
    kind: str,
    *,
    labels: Mapping[str, str],
    statuses: Iterable[str] | None,
    after: JobPosition | None,
    limit: int,
) -> list[Job]: ...
```

Jobs of ``kind`` carrying all ``labels``, newest first (``created_at``, then ``job_id``), strictly after ``after``. Jobs of stopped instances are ended first, so a status filter sees them as ``get`` does.

Код: [postgres.py:600](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L600).

#### Метод `PgJobStore.create`

```python
async def create(self, job: Job) -> None: ...
```

Код: [postgres.py:649](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L649).

#### Метод `PgJobStore.get`

```python
async def get(self, job_id: str) -> Job | None: ...
```

Код: [postgres.py:652](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L652).

#### Метод `PgJobStore.save`

```python
async def save(self, job: Job) -> None: ...
```

Код: [postgres.py:655](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L655).

#### Метод `PgJobStore.heartbeat`

```python
async def heartbeat(self) -> int: ...
```

Код: [postgres.py:658](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L658).

#### Метод `PgJobStore.sweep`

```python
async def sweep(self) -> int: ...
```

Код: [postgres.py:661](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L661).

#### Метод `PgJobStore.release_owned`

```python
async def release_owned(self, reason: str) -> int: ...
```

Код: [postgres.py:664](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L664).

#### Метод `PgJobStore.page`

```python
async def page(
    self,
    kind: str,
    *,
    labels: Mapping[str, str],
    statuses: Iterable[str] | None,
    after: JobPosition | None,
    limit: int,
) -> list[Job]: ...
```

Код: [postgres.py:667](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L667).

## Функції

### Функція `migrate`

```python
def migrate(
    tx: PgConnect,
    lock: str,
    *stores: PgIdempotencyStore | PgJobStore,
    schema: str | None = None,
) -> None: ...
```

Create or upgrade the tables of ``stores`` in one transaction under ``pg_advisory_xact_lock(lock)``.

Idempotent and safe when several instances start at once. ``schema`` is created first when given.

Код: [postgres.py:99](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L99).

### Функція `pool_tx`

```python
def pool_tx(pool: Any) -> PgConnect: ...
```

:data:`PgConnect` over a ``psycopg_pool.ConnectionPool``.

Код: [postgres.py:74](../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L74).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `PgConnect` | — | `Callable[[], AbstractContextManager[Connection[Any]]]` | Yields a connection inside one transaction (commit on exit, rollback on error). |

## Реекспорт

| Назва | Визначено в |
|---|---|
| `JobPosition` | [`jane_kit.jobs`](jane_kit.jobs.md) |
