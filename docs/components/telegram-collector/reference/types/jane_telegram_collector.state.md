# Модуль `jane_telegram_collector.state`

> Згенеровано `scripts/docs_reference.py` з [services/telegram-collector/src/jane_telegram_collector/state.py](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py). Не редагуйте вручну.

Own state store of the Telegram Collector (SQLite, WAL): nobody else reads these tables (ADR-0009).

Tables: collections (runs) with their lease, per-run channel progress, persistent channel cursors per ``state_key`` (last message id, edit watermark, ``pts``), seen revisions per ``state_key`` (to tell an edit from a repeated delivery of the same revision), the buffer of emitted-but-unacknowledged materials, errors, managed connections, jobs and idempotency keys (tables of jane-kit's shared SQLite stores, R17) and counters.

Every emitted message is committed in one transaction (material + run progress + cursor + seen revision + stats), fenced by the run's lease: a killed process resumes from a consistent point and a run that lost its lease cannot write anything. Several processes may share the file on one host (SQLite locking).

## Класи

### Клас `LeaseLost`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_telegram_collector.state` |
| Успадкування | `Exception` |
| Код | [state.py:123](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L123) |

```python
class LeaseLost(Exception): ...
```

This instance no longer holds the lease of the collection (another instance took it over).

### Клас `StateFileTooNew`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_telegram_collector.state` |
| Успадкування | `RuntimeError` |
| Код | [state.py:37](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L37) |

```python
class StateFileTooNew(RuntimeError): ...
```

The state file was written by a newer collector (``PRAGMA user_version`` > :data:`SCHEMA_VERSION`).

### Клас `StateStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.state` |
| Код | [state.py:131](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L131) |

```python
class StateStore: ...
```

#### Конструктор `StateStore.__init__`

```python
def __init__(self, path: Path, *, busy_timeout_ms: int) -> None: ...
```

``busy_timeout_ms``: how long a writer waits for another process holding the SQLite lock (``JANE_TELEGRAM_COLLECTOR_STATE_BUSY_TIMEOUT_MS``, validated to stay below the lease).

Винятки в коді методу: `StateFileTooNew`.

Код: [state.py:132](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L132).

#### Метод `StateStore.schema_version`

```python
def schema_version(self) -> int: ...
```

Код: [state.py:164](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L164).

#### Метод `StateStore.close`

```python
def close(self) -> None: ...
```

Код: [state.py:168](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L168).

#### Метод `StateStore.tx`

```python
@contextmanager
def tx(self, fence: Fence | None = None) -> Iterator[sqlite3.Connection]: ...
```

``BEGIN IMMEDIATE`` transaction. With ``fence`` it is rolled back and :class:`LeaseLost` raised unless the owner still holds a valid lease.

Винятки в коді методу: `LeaseLost`.

Код: [state.py:173](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L173).

#### Метод `StateStore.ping`

```python
def ping(self) -> None: ...
```

Код: [state.py:200](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L200).

#### Метод `StateStore.next_counter`

```python
def next_counter(self, db: sqlite3.Connection, name: str) -> int: ...
```

Код: [state.py:203](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L203).

#### Метод `StateStore.create_collection`

```python
def create_collection(
    self,
    collection_id: str,
    *,
    state_key: str,
    request: Mapping[str, Any],
    rules: Mapping[str, Any],
    rules_ref: Mapping[str, Any] | None,
    created_at: str,
    effective_limits: Mapping[str, Any],
    owner: str,
    lease_seconds: float,
) -> bool: ...
```

Create a queued collection owned by ``owner``; False if ``state_key`` is used by an active one.

Код: [state.py:212](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L212).

#### Метод `StateStore.get_collection`

```python
def get_collection(self, collection_id: str) -> dict[str, Any] | None: ...
```

Код: [state.py:250](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L250).

#### Метод `StateStore.get_status`

```python
def get_status(self, collection_id: str) -> str | None: ...
```

Код: [state.py:260](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L260).

#### Метод `StateStore.set_running`

```python
def set_running(self, db: sqlite3.Connection, collection_id: str) -> None: ...
```

Код: [state.py:264](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L264).

#### Метод `StateStore.finish`

```python
def finish(
    self,
    db: sqlite3.Connection,
    collection_id: str,
    status: str,
    finished_at: str,
    result: Any = None,
) -> None: ...
```

Код: [state.py:270](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L270).

#### Метод `StateStore.finish_if_owner`

```python
def finish_if_owner(
    self,
    collection_id: str,
    owner: str,
    status: str,
    finished_at: str,
    result: Any = None,
) -> bool: ...
```

Terminal status written only by the holder of a valid lease (fenced like every other run write).

Код: [state.py:279](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L279).

#### Метод `StateStore.set_paused`

```python
def set_paused(self, collection_id: str, paused: bool, fence: Fence) -> None: ...
```

Backpressure flag of a run: written only under the run's lease (:class:`LeaseLost` otherwise).

Код: [state.py:298](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L298).

#### Метод `StateStore.save_stats`

```python
def save_stats(
    self,
    db: sqlite3.Connection,
    collection_id: str,
    stats: Mapping[str, Any],
) -> None: ...
```

Код: [state.py:305](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L305).

#### Метод `StateStore.lease`

```python
def lease(self, collection_id: str) -> tuple[str | None, float]: ...
```

Код: [state.py:308](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L308).

#### Метод `StateStore.claim`

```python
def claim(self, collection_id: str, owner: str, lease_seconds: float) -> bool: ...
```

Take (or renew) the lease of a non-terminal collection.

Код: [state.py:314](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L314).

#### Метод `StateStore.release`

```python
def release(self, collection_id: str, owner: str) -> None: ...
```

Код: [state.py:325](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L325).

#### Метод `StateStore.resumable`

```python
def resumable(self, owner: str) -> list[str]: ...
```

Non-terminal collections whose lease expired (or that this instance owned).

Код: [state.py:332](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L332).

#### Метод `StateStore.active_for_state_key`

```python
def active_for_state_key(self, state_key: str) -> list[str]: ...
```

Код: [state.py:341](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L341).

#### Метод `StateStore.expire_finished`

```python
def expire_finished(self, older_than_ts: float) -> list[str]: ...
```

Drop buffers of collections finished before ``older_than_ts``; keep a tombstone (410).

Код: [state.py:348](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L348).

#### Метод `StateStore.get_progress`

```python
def get_progress(self, collection_id: str, channel_key: str) -> dict[str, Any] | None: ...
```

Код: [state.py:366](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L366).

#### Метод `StateStore.put_progress`

```python
def put_progress(
    self,
    db: sqlite3.Connection,
    collection_id: str,
    channel_key: str,
    progress: Mapping[str, Any],
) -> None: ...
```

Код: [state.py:373](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L373).

#### Метод `StateStore.get_cursor`

```python
def get_cursor(self, state_key: str, channel_id: str) -> dict[str, Any] | None: ...
```

Код: [state.py:383](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L383).

#### Метод `StateStore.put_cursor`

```python
def put_cursor(
    self,
    db: sqlite3.Connection,
    state_key: str,
    channel_id: str,
    cursor: Mapping[str, Any],
    now: str,
) -> None: ...
```

Код: [state.py:389](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L389).

#### Метод `StateStore.latest_seen`

```python
def latest_seen(self, material_id: str) -> tuple[int, str] | None: ...
```

The newest revision of the message emitted under any ``state_key`` (``sequence``, text sha256).

Код: [state.py:398](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L398).

#### Метод `StateStore.seen`

```python
def seen(self, state_key: str, material_id: str) -> tuple[int, str] | None: ...
```

Код: [state.py:406](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L406).

#### Метод `StateStore.put_seen`

```python
def put_seen(
    self,
    db: sqlite3.Connection,
    state_key: str,
    material_id: str,
    sequence: int,
    sha: str,
) -> None: ...
```

Код: [state.py:413](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L413).

#### Метод `StateStore.state_summary`

```python
def state_summary(self, state_key: str) -> dict[str, Any] | None: ...
```

Код: [state.py:423](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L423).

#### Метод `StateStore.delete_state`

```python
def delete_state(self, state_key: str) -> None: ...
```

Код: [state.py:435](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L435).

#### Метод `StateStore.append_material`

```python
def append_material(
    self,
    db: sqlite3.Connection,
    collection_id: str,
    observation_id: str,
    material: Mapping[str, Any],
) -> int: ...
```

Код: [state.py:441](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L441).

#### Метод `StateStore.materials_after`

```python
def materials_after(
    self,
    collection_id: str,
    after_seq: int,
    limit: int,
) -> list[tuple[int, dict[str, Any]]]: ...
```

Код: [state.py:451](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L451).

#### Метод `StateStore.ack`

```python
def ack(self, collection_id: str, upto_seq: int) -> int: ...
```

Acknowledge every material with ``seq <= upto_seq``; returns how many were newly acknowledged.

Код: [state.py:460](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L460).

#### Метод `StateStore.unacked_count`

```python
def unacked_count(self, collection_id: str) -> int: ...
```

Код: [state.py:472](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L472).

#### Метод `StateStore.emitted_count`

```python
def emitted_count(self, collection_id: str) -> int: ...
```

Код: [state.py:476](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L476).

#### Метод `StateStore.add_error`

```python
def add_error(
    self,
    db: sqlite3.Connection,
    collection_id: str,
    error: Mapping[str, Any],
) -> None: ...
```

Код: [state.py:481](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L481).

#### Метод `StateStore.errors_after`

```python
def errors_after(
    self,
    collection_id: str,
    after_seq: int,
    limit: int,
) -> list[tuple[int, dict[str, Any]]]: ...
```

Код: [state.py:488](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L488).

#### Метод `StateStore.get_connection`

```python
def get_connection(self, connection_id: str) -> tuple[dict[str, Any], str] | None: ...
```

Код: [state.py:498](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L498).

#### Метод `StateStore.put_connection`

```python
def put_connection(self, connection_id: str, body: Mapping[str, Any], etag: str) -> bool: ...
```

Returns True if created.

Код: [state.py:502](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L502).

#### Метод `StateStore.delete_connection`

```python
def delete_connection(self, connection_id: str) -> bool: ...
```

Код: [state.py:515](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L515).

#### Метод `StateStore.list_connections`

```python
def list_connections(self, after: str | None, limit: int) -> list[dict[str, Any]]: ...
```

Код: [state.py:521](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L521).

#### Метод `StateStore.read`

```python
@contextmanager
def read(self) -> Iterator[sqlite3.Connection]: ...
```

The connection for single-statement reads (no write lock; ``jane_kit.stores.sqlite``).

Код: [state.py:530](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L530).

#### Метод `StateStore.get_job`

```python
def get_job(self, job_id: str) -> str | None: ...
```

Код: [state.py:535](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L535).

#### Метод `StateStore.work_row`

```python
def work_row(self, db: sqlite3.Connection, job_id: str) -> tuple[str | None, str] | None: ...
```

``(owner, status)`` of the collection of a job (``jane_kit.stores.sqlite.WorkRows``).

Код: [state.py:539](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L539).

#### Метод `StateStore.cancel_unstarted`

```python
def cancel_unstarted(self, db: sqlite3.Connection, job_id: str, owner: str) -> bool: ...
```

A collection cancelled before its run started ends ``cancelled`` (only its lease holder).

Код: [state.py:546](../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L546).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `SCHEMA_VERSION` | — | `1` | ``PRAGMA user_version`` of the state file - the format marker. 1 (WP-16, R04): ``tg_seen.sequence`` is in ``revision.sequence`` units (epoch seconds x ``SEQUENCE_SCALE`` + the revision number within the second); a version 0 file (seconds, collectors before WP-16) is migrated when a process opens it. A file of a newer version than the code knows is refused (:class:`StateFileTooNew`). Collectors before WP-16 do not read the marker: run them on a migrated file and they take the stored sequences for seconds, so every known message looks newer than its edits and no edit is emitted - instances sharing one ``STATE_DIR`` are upgraded together (README). |
| `Fence` | — | `tuple[str, str]` | ``(collection_id, owner)``: a transaction with a fence commits only while ``owner`` holds a valid lease. |
