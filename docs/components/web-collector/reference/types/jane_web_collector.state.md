# Модуль `jane_web_collector.state`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/state.py](../../../../../services/web-collector/src/jane_web_collector/state.py). Не редагуйте вручну.

Own state store of the Web Collector (SQLite, WAL): nobody else reads these tables (ADR-0009).

Holds collections (runs) with their lease, the frontier (queue + per-run dedup: primary key ``(collection_id, url)``), strategy snapshots, the buffer of emitted-but-unacknowledged materials, URL errors, the per-``state_key`` URL history used for revisits (ETag, Last-Modified, content hash, outgoing links), managed connections, jobs and idempotency keys (tables of jane-kit's shared SQLite stores, R17) and the per-host schedule shared by the instances (``host_users``, ``host_schedule``, ``host_slots``: :mod:`.shared_hosts`, R15).

Every processed page is committed in one transaction (new URLs + page status + material + URL history + strategy snapshots + stats), so a killed process resumes from a consistent point. Several processes may share the same file on one host (SQLite locking); a collection is executed by the instance holding its lease.

## Класи

### Клас `FrontierRow`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_web_collector.state` |
| Код | [state.py:160](../../../../../services/web-collector/src/jane_web_collector/state.py#L160) |

```python
@dataclass(frozen=True)
class FrontierRow: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `url` | `str` | — | читання |  |
| `priority` | `int` | — | читання |  |
| `depth` | `int` | — | читання |  |
| `kind` | `str` | — | читання |  |
| `strategy_id` | `str \| None` | — | читання |  |
| `parent_url` | `str \| None` | `None` | читання |  |
| `section` | `str \| None` | `None` | читання |  |
| `lastmod` | `str \| None` | `None` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `StateStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.state` |
| Код | [state.py:175](../../../../../services/web-collector/src/jane_web_collector/state.py#L175) |

```python
class StateStore: ...
```

#### Конструктор `StateStore.__init__`

```python
def __init__(self, path: Path, *, busy_timeout_ms: int = 10000) -> None: ...
```

``busy_timeout_ms``: how long a writer waits for another process holding the SQLite lock (configuration: ``JANE_WEB_COLLECTOR_STATE_BUSY_TIMEOUT_MS``, must stay below the lease).

Код: [state.py:176](../../../../../services/web-collector/src/jane_web_collector/state.py#L176).

#### Метод `StateStore.close`

```python
def close(self) -> None: ...
```

Код: [state.py:190](../../../../../services/web-collector/src/jane_web_collector/state.py#L190).

#### Метод `StateStore.tx`

```python
@contextmanager
def tx(self, fence: Fence | None = None) -> Iterator[sqlite3.Connection]: ...
```

``BEGIN IMMEDIATE`` transaction. With ``fence`` the transaction is rolled back and :class:`LeaseLost` raised unless the owner still holds a valid lease (fencing of a run that another instance has taken over).

Винятки в коді методу: `LeaseLost`.

Код: [state.py:195](../../../../../services/web-collector/src/jane_web_collector/state.py#L195).

#### Метод `StateStore.ping`

```python
def ping(self) -> None: ...
```

Код: [state.py:223](../../../../../services/web-collector/src/jane_web_collector/state.py#L223).

#### Метод `StateStore.next_counter`

```python
def next_counter(self, db: sqlite3.Connection, name: str) -> int: ...
```

Код: [state.py:227](../../../../../services/web-collector/src/jane_web_collector/state.py#L227).

#### Метод `StateStore.create_collection`

```python
def create_collection(
    self,
    collection_id: str,
    *,
    state_key: str,
    status: str,
    request: Mapping[str, Any],
    rules: Mapping[str, Any],
    rules_ref: Mapping[str, Any] | None,
    created_at: str,
    effective_limits: Mapping[str, Any],
) -> None: ...
```

Код: [state.py:237](../../../../../services/web-collector/src/jane_web_collector/state.py#L237).

#### Метод `StateStore.get_collection`

```python
def get_collection(self, collection_id: str) -> dict[str, Any] | None: ...
```

Код: [state.py:265](../../../../../services/web-collector/src/jane_web_collector/state.py#L265).

#### Метод `StateStore.set_status`

```python
def set_status(
    self,
    collection_id: str,
    status: str,
    *,
    finished_at: str | None = None,
    db: sqlite3.Connection | None = None,
) -> None: ...
```

Код: [state.py:275](../../../../../services/web-collector/src/jane_web_collector/state.py#L275).

#### Метод `StateStore.get_status`

```python
def get_status(self, collection_id: str) -> str | None: ...
```

Код: [state.py:291](../../../../../services/web-collector/src/jane_web_collector/state.py#L291).

#### Метод `StateStore.set_meta`

```python
def set_meta(self, collection_id: str, meta: Mapping[str, Any]) -> None: ...
```

Код: [state.py:295](../../../../../services/web-collector/src/jane_web_collector/state.py#L295).

#### Метод `StateStore.set_paused`

```python
def set_paused(self, collection_id: str, paused: bool, *, fence: Fence) -> None: ...
```

Only the current lease holder may change a run's backpressure state.

Код: [state.py:301](../../../../../services/web-collector/src/jane_web_collector/state.py#L301).

#### Метод `StateStore.save_stats`

```python
def save_stats(
    self,
    db: sqlite3.Connection,
    collection_id: str,
    stats: Mapping[str, Any],
) -> None: ...
```

Код: [state.py:308](../../../../../services/web-collector/src/jane_web_collector/state.py#L308).

#### Метод `StateStore.lease`

```python
def lease(self, collection_id: str) -> tuple[str | None, float]: ...
```

Код: [state.py:311](../../../../../services/web-collector/src/jane_web_collector/state.py#L311).

#### Метод `StateStore.set_status_if_owner`

```python
def set_status_if_owner(
    self,
    collection_id: str,
    owner: str,
    status: str,
    *,
    finished_at: str | None,
) -> bool: ...
```

Terminal status written only by the lease holder (a run that lost its lease must not overwrite it).

Код: [state.py:317](../../../../../services/web-collector/src/jane_web_collector/state.py#L317).

#### Метод `StateStore.claim`

```python
def claim(self, collection_id: str, owner: str, lease_seconds: float) -> bool: ...
```

Take (or renew) the lease of a non-terminal collection.

Код: [state.py:329](../../../../../services/web-collector/src/jane_web_collector/state.py#L329).

#### Метод `StateStore.release`

```python
def release(self, collection_id: str, owner: str) -> None: ...
```

Код: [state.py:340](../../../../../services/web-collector/src/jane_web_collector/state.py#L340).

#### Метод `StateStore.resumable`

```python
def resumable(self, owner: str) -> list[str]: ...
```

Non-terminal collections whose lease expired (or that this instance owned).

Код: [state.py:347](../../../../../services/web-collector/src/jane_web_collector/state.py#L347).

#### Метод `StateStore.active_for_state_key`

```python
def active_for_state_key(self, state_key: str) -> list[str]: ...
```

Код: [state.py:357](../../../../../services/web-collector/src/jane_web_collector/state.py#L357).

#### Метод `StateStore.expire_finished`

```python
def expire_finished(self, older_than_ts: float) -> list[str]: ...
```

Drop buffers and frontier of collections finished before ``older_than_ts``; keep a tombstone (410).

Код: [state.py:364](../../../../../services/web-collector/src/jane_web_collector/state.py#L364).

#### Метод `StateStore.add_urls`

```python
def add_urls(
    self,
    db: sqlite3.Connection,
    collection_id: str,
    rows: Iterable[FrontierRow],
    status: str = 'pending',
) -> int: ...
```

Код: [state.py:382](../../../../../services/web-collector/src/jane_web_collector/state.py#L382).

#### Метод `StateStore.frontier_row`

```python
def frontier_row(self, collection_id: str, url: str) -> sqlite3.Row | None: ...
```

Код: [state.py:408](../../../../../services/web-collector/src/jane_web_collector/state.py#L408).

#### Метод `StateStore.known`

```python
def known(self, collection_id: str, url: str) -> bool: ...
```

Код: [state.py:411](../../../../../services/web-collector/src/jane_web_collector/state.py#L411).

#### Метод `StateStore.take_pending`

```python
def take_pending(
    self,
    collection_id: str,
    limit: int,
    fence: Fence | None = None,
) -> list[FrontierRow]: ...
```

Код: [state.py:417](../../../../../services/web-collector/src/jane_web_collector/state.py#L417).

#### Метод `StateStore.mark_url`

```python
def mark_url(self, db: sqlite3.Connection, collection_id: str, url: str, status: str) -> None: ...
```

Код: [state.py:443](../../../../../services/web-collector/src/jane_web_collector/state.py#L443).

#### Метод `StateStore.reset_inflight`

```python
def reset_inflight(self, collection_id: str, fence: Fence | None = None) -> int: ...
```

Код: [state.py:448](../../../../../services/web-collector/src/jane_web_collector/state.py#L448).

#### Метод `StateStore.frontier_counts`

```python
def frontier_counts(self, collection_id: str) -> dict[str, int]: ...
```

Код: [state.py:455](../../../../../services/web-collector/src/jane_web_collector/state.py#L455).

#### Метод `StateStore.drop_pending`

```python
def drop_pending(self, collection_id: str, fence: Fence | None = None) -> int: ...
```

Budget reached: pending and stale in-flight URLs are dropped (not fetched in this run).

Код: [state.py:461](../../../../../services/web-collector/src/jane_web_collector/state.py#L461).

#### Метод `StateStore.frontier_size_for_state_key`

```python
def frontier_size_for_state_key(self, state_key: str) -> int: ...
```

Код: [state.py:469](../../../../../services/web-collector/src/jane_web_collector/state.py#L469).

#### Метод `StateStore.save_strategy_states`

```python
def save_strategy_states(
    self,
    db: sqlite3.Connection,
    collection_id: str,
    states: Mapping[str, Any],
) -> None: ...
```

Код: [state.py:478](../../../../../services/web-collector/src/jane_web_collector/state.py#L478).

#### Метод `StateStore.load_strategy_states`

```python
def load_strategy_states(self, collection_id: str) -> dict[str, Any]: ...
```

Код: [state.py:488](../../../../../services/web-collector/src/jane_web_collector/state.py#L488).

#### Метод `StateStore.save_cursors`

```python
def save_cursors(
    self,
    db: sqlite3.Connection,
    state_key: str,
    cursors: Mapping[str, Any],
    now: str,
) -> None: ...
```

Код: [state.py:494](../../../../../services/web-collector/src/jane_web_collector/state.py#L494).

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

Код: [state.py:505](../../../../../services/web-collector/src/jane_web_collector/state.py#L505).

#### Метод `StateStore.materials_after`

```python
def materials_after(
    self,
    collection_id: str,
    after_seq: int,
    limit: int,
) -> list[tuple[int, dict[str, Any]]]: ...
```

Код: [state.py:515](../../../../../services/web-collector/src/jane_web_collector/state.py#L515).

#### Метод `StateStore.ack`

```python
def ack(self, collection_id: str, upto_seq: int) -> int: ...
```

Acknowledge every material with ``seq <= upto_seq``; returns how many were newly acknowledged.

Код: [state.py:524](../../../../../services/web-collector/src/jane_web_collector/state.py#L524).

#### Метод `StateStore.unacked_count`

```python
def unacked_count(self, collection_id: str) -> int: ...
```

Код: [state.py:536](../../../../../services/web-collector/src/jane_web_collector/state.py#L536).

#### Метод `StateStore.emitted_count`

```python
def emitted_count(self, collection_id: str) -> int: ...
```

Код: [state.py:540](../../../../../services/web-collector/src/jane_web_collector/state.py#L540).

#### Метод `StateStore.add_error`

```python
def add_error(
    self,
    db: sqlite3.Connection,
    collection_id: str,
    error: Mapping[str, Any],
) -> None: ...
```

Код: [state.py:545](../../../../../services/web-collector/src/jane_web_collector/state.py#L545).

#### Метод `StateStore.errors_after`

```python
def errors_after(
    self,
    collection_id: str,
    after_seq: int,
    limit: int,
) -> list[tuple[int, dict[str, Any]]]: ...
```

Код: [state.py:552](../../../../../services/web-collector/src/jane_web_collector/state.py#L552).

#### Метод `StateStore.url_state`

```python
def url_state(self, state_key: str, url: str) -> dict[str, Any] | None: ...
```

Код: [state.py:562](../../../../../services/web-collector/src/jane_web_collector/state.py#L562).

#### Метод `StateStore.put_url_state`

```python
def put_url_state(
    self,
    db: sqlite3.Connection,
    state_key: str,
    url: str,
    *,
    status: int | None,
    etag: str | None,
    last_modified: str | None,
    content_sha256: str | None,
    links: Sequence[str] | None,
) -> None: ...
```

Код: [state.py:570](../../../../../services/web-collector/src/jane_web_collector/state.py#L570).

#### Метод `StateStore.state_summary`

```python
def state_summary(self, state_key: str) -> dict[str, Any] | None: ...
```

Код: [state.py:602](../../../../../services/web-collector/src/jane_web_collector/state.py#L602).

#### Метод `StateStore.delete_state`

```python
def delete_state(self, state_key: str) -> None: ...
```

Код: [state.py:621](../../../../../services/web-collector/src/jane_web_collector/state.py#L621).

#### Метод `StateStore.get_connection`

```python
def get_connection(self, connection_id: str) -> tuple[dict[str, Any], str] | None: ...
```

Код: [state.py:627](../../../../../services/web-collector/src/jane_web_collector/state.py#L627).

#### Метод `StateStore.put_connection`

```python
def put_connection(self, connection_id: str, body: Mapping[str, Any], etag: str) -> bool: ...
```

Returns True if created.

Код: [state.py:631](../../../../../services/web-collector/src/jane_web_collector/state.py#L631).

#### Метод `StateStore.delete_connection`

```python
def delete_connection(self, connection_id: str) -> bool: ...
```

Код: [state.py:644](../../../../../services/web-collector/src/jane_web_collector/state.py#L644).

#### Метод `StateStore.list_connections`

```python
def list_connections(self, after: str | None, limit: int) -> list[dict[str, Any]]: ...
```

Код: [state.py:650](../../../../../services/web-collector/src/jane_web_collector/state.py#L650).

#### Метод `StateStore.read`

```python
@contextmanager
def read(self) -> Iterator[sqlite3.Connection]: ...
```

The connection for single-statement reads (no write lock; ``jane_kit.stores.sqlite``).

Код: [state.py:659](../../../../../services/web-collector/src/jane_web_collector/state.py#L659).

#### Метод `StateStore.get_job`

```python
def get_job(self, job_id: str) -> str | None: ...
```

Код: [state.py:664](../../../../../services/web-collector/src/jane_web_collector/state.py#L664).

#### Метод `StateStore.work_row`

```python
def work_row(self, db: sqlite3.Connection, job_id: str) -> tuple[str | None, str] | None: ...
```

``(owner, status)`` of the collection of a job (``jane_kit.stores.sqlite.WorkRows``).

Код: [state.py:668](../../../../../services/web-collector/src/jane_web_collector/state.py#L668).

#### Метод `StateStore.cancel_unstarted`

```python
def cancel_unstarted(self, db: sqlite3.Connection, job_id: str, owner: str) -> bool: ...
```

A collection cancelled before its run started ends ``cancelled`` (only its lease holder).

Код: [state.py:675](../../../../../services/web-collector/src/jane_web_collector/state.py#L675).

#### Метод `StateStore.host_take_slot`

```python
def host_take_slot(
    self,
    host: str,
    instance_id: str,
    token: str,
    *,
    interval: float,
    parallel: int,
    ttl: float,
) -> tuple[bool, float]: ...
```

One attempt of request ``token`` to start on ``host`` for the whole platform (R15), in one transaction.

Registers (renews) the limits of ``instance_id`` on the host and queues the request in arrival order (``host_waiters``). The request takes a slot only when it may start **now**: it is first in line (starts go strictly in arrival order: a younger request never takes the start the first one waits for), fewer requests than the smallest registered parallelism are in flight, and the schedule allows a start - the largest registered interval after the previous start of any instance has passed, and so has a ``Retry-After``. A slot is thus never held while waiting (review 1 of WP-16).

Returns ``(True, 0.0)`` when the slot is taken (the start is recorded as now), ``(False, seconds)`` when the request is first in line but the schedule allows a start only in ``seconds``, ``(False, 0.0)`` when it waits for a slot or an older waiter (try again after the poll interval). Expired registrations, slots and waiters (instances that died: nothing renews them) are dropped first.

Код: [state.py:686](../../../../../services/web-collector/src/jane_web_collector/state.py#L686).

#### Метод `StateStore.host_renew`

```python
def host_renew(
    self,
    instance_id: str,
    registrations: Mapping[str, tuple[float, int]],
    tokens: Sequence[str],
    ttl: float,
) -> None: ...
```

Keep alive what a live instance holds (R15): its registrations on hosts (``host -> (interval, parallel)``, re-created if they expired meanwhile), and the slots and places in line of ``tokens``. A killed instance renews nothing, so its rows expire ``ttl`` seconds after its last renewal.

Код: [state.py:758](../../../../../services/web-collector/src/jane_web_collector/state.py#L758).

#### Метод `StateStore.host_release_slot`

```python
def host_release_slot(self, host: str, token: str) -> None: ...
```

Give back the slot of ``token`` (or its place in line, if it never got one).

Код: [state.py:781](../../../../../services/web-collector/src/jane_web_collector/state.py#L781).

#### Метод `StateStore.host_push_back`

```python
def host_push_back(self, host: str, until: float) -> None: ...
```

Код: [state.py:787](../../../../../services/web-collector/src/jane_web_collector/state.py#L787).

#### Метод `StateStore.host_leave`

```python
def host_leave(self, host: str, instance_id: str) -> None: ...
```

Код: [state.py:795](../../../../../services/web-collector/src/jane_web_collector/state.py#L795).

#### Метод `StateStore.host_rows`

```python
def host_rows(self, host: str) -> dict[str, Any]: ...
```

Shared state of one host (diagnostics, tests).

Код: [state.py:799](../../../../../services/web-collector/src/jane_web_collector/state.py#L799).

#### Метод `StateStore.host_prune`

```python
def host_prune(self) -> int: ...
```

Drop expired registrations, slots and schedules of hosts nobody uses (housekeeping).

Код: [state.py:805](../../../../../services/web-collector/src/jane_web_collector/state.py#L805).
