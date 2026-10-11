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
| Код | [state.py:196](../../../../../services/web-collector/src/jane_web_collector/state.py#L196) |

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
| Код | [state.py:211](../../../../../services/web-collector/src/jane_web_collector/state.py#L211) |

```python
class StateStore: ...
```

#### Конструктор `StateStore.__init__`

```python
def __init__(self, path: Path, *, busy_timeout_ms: int = 10000) -> None: ...
```

``busy_timeout_ms``: how long a writer waits for another process holding the SQLite lock (configuration: ``JANE_WEB_COLLECTOR_STATE_BUSY_TIMEOUT_MS``, must stay below the lease).

Код: [state.py:212](../../../../../services/web-collector/src/jane_web_collector/state.py#L212).

#### Метод `StateStore.close`

```python
def close(self) -> None: ...
```

Код: [state.py:255](../../../../../services/web-collector/src/jane_web_collector/state.py#L255).

#### Метод `StateStore.tx`

```python
@contextmanager
def tx(self, fence: Fence | None = None) -> Iterator[sqlite3.Connection]: ...
```

``BEGIN IMMEDIATE`` transaction. With ``fence`` the transaction is rolled back and :class:`LeaseLost` raised unless the owner still holds a valid lease (fencing of a run that another instance has taken over).

Винятки в коді методу: `LeaseLost`.

Код: [state.py:306](../../../../../services/web-collector/src/jane_web_collector/state.py#L306).

#### Метод `StateStore.ping`

```python
def ping(self) -> None: ...
```

Код: [state.py:334](../../../../../services/web-collector/src/jane_web_collector/state.py#L334).

#### Метод `StateStore.next_counter`

```python
def next_counter(self, db: sqlite3.Connection, name: str) -> int: ...
```

Код: [state.py:338](../../../../../services/web-collector/src/jane_web_collector/state.py#L338).

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

Код: [state.py:348](../../../../../services/web-collector/src/jane_web_collector/state.py#L348).

#### Метод `StateStore.get_collection`

```python
def get_collection(self, collection_id: str) -> dict[str, Any] | None: ...
```

Код: [state.py:376](../../../../../services/web-collector/src/jane_web_collector/state.py#L376).

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

Код: [state.py:386](../../../../../services/web-collector/src/jane_web_collector/state.py#L386).

#### Метод `StateStore.get_status`

```python
def get_status(self, collection_id: str) -> str | None: ...
```

Код: [state.py:402](../../../../../services/web-collector/src/jane_web_collector/state.py#L402).

#### Метод `StateStore.set_meta`

```python
def set_meta(self, collection_id: str, meta: Mapping[str, Any]) -> None: ...
```

Код: [state.py:406](../../../../../services/web-collector/src/jane_web_collector/state.py#L406).

#### Метод `StateStore.set_paused`

```python
def set_paused(self, collection_id: str, paused: bool, *, fence: Fence) -> None: ...
```

Only the current lease holder may change a run's backpressure state.

Код: [state.py:412](../../../../../services/web-collector/src/jane_web_collector/state.py#L412).

#### Метод `StateStore.save_stats`

```python
def save_stats(
    self,
    db: sqlite3.Connection,
    collection_id: str,
    stats: Mapping[str, Any],
) -> None: ...
```

Код: [state.py:419](../../../../../services/web-collector/src/jane_web_collector/state.py#L419).

#### Метод `StateStore.lease`

```python
def lease(self, collection_id: str) -> tuple[str | None, float]: ...
```

Код: [state.py:422](../../../../../services/web-collector/src/jane_web_collector/state.py#L422).

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

Код: [state.py:428](../../../../../services/web-collector/src/jane_web_collector/state.py#L428).

#### Метод `StateStore.claim`

```python
def claim(self, collection_id: str, owner: str, lease_seconds: float) -> bool: ...
```

Take (or renew) the lease of a non-terminal collection.

Код: [state.py:440](../../../../../services/web-collector/src/jane_web_collector/state.py#L440).

#### Метод `StateStore.release`

```python
def release(self, collection_id: str, owner: str) -> None: ...
```

Код: [state.py:451](../../../../../services/web-collector/src/jane_web_collector/state.py#L451).

#### Метод `StateStore.resumable`

```python
def resumable(self, owner: str) -> list[str]: ...
```

Non-terminal collections whose lease expired (or that this instance owned).

Код: [state.py:458](../../../../../services/web-collector/src/jane_web_collector/state.py#L458).

#### Метод `StateStore.active_for_state_key`

```python
def active_for_state_key(self, state_key: str) -> list[str]: ...
```

Код: [state.py:468](../../../../../services/web-collector/src/jane_web_collector/state.py#L468).

#### Метод `StateStore.expire_finished`

```python
def expire_finished(self, older_than_ts: float) -> list[str]: ...
```

Drop buffers and frontier of collections finished before ``older_than_ts``; keep a tombstone (410).

Код: [state.py:475](../../../../../services/web-collector/src/jane_web_collector/state.py#L475).

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

Код: [state.py:538](../../../../../services/web-collector/src/jane_web_collector/state.py#L538).

#### Метод `StateStore.frontier_row`

```python
def frontier_row(self, collection_id: str, url: str) -> sqlite3.Row | None: ...
```

Код: [state.py:568](../../../../../services/web-collector/src/jane_web_collector/state.py#L568).

#### Метод `StateStore.known`

```python
def known(self, collection_id: str, url: str) -> bool: ...
```

Код: [state.py:571](../../../../../services/web-collector/src/jane_web_collector/state.py#L571).

#### Метод `StateStore.add_overflow`

```python
def add_overflow(self, db: sqlite3.Connection, collection_id: str, row: FrontierRow) -> int: ...
```

Compressed durable disk spool; these candidates do not occupy the bounded active queue.

Код: [state.py:581](../../../../../services/web-collector/src/jane_web_collector/state.py#L581).

#### Метод `StateStore.overflow_count`

```python
def overflow_count(self, collection_id: str) -> int: ...
```

Код: [state.py:608](../../../../../services/web-collector/src/jane_web_collector/state.py#L608).

#### Метод `StateStore.promote_overflow`

```python
def promote_overflow(
    self,
    db: sqlite3.Connection,
    collection_id: str,
    limit: int,
    *,
    status: str = 'pending',
    revisits: int | None = None,
    materials_only: bool = False,
) -> int: ...
```

Код: [state.py:612](../../../../../services/web-collector/src/jane_web_collector/state.py#L612).

#### Метод `StateStore.spool_known_pending`

```python
def spool_known_pending(self, db: sqlite3.Connection, collection_id: str) -> bool: ...
```

Код: [state.py:649](../../../../../services/web-collector/src/jane_web_collector/state.py#L649).

#### Метод `StateStore.take_pending`

```python
def take_pending(
    self,
    collection_id: str,
    limit: int,
    fence: Fence | None = None,
    *,
    materials_only: bool = False,
) -> list[FrontierRow]: ...
```

Код: [state.py:662](../../../../../services/web-collector/src/jane_web_collector/state.py#L662).

#### Метод `StateStore.mark_url`

```python
def mark_url(self, db: sqlite3.Connection, collection_id: str, url: str, status: str) -> None: ...
```

Код: [state.py:701](../../../../../services/web-collector/src/jane_web_collector/state.py#L701).

#### Метод `StateStore.reset_inflight`

```python
def reset_inflight(self, collection_id: str, fence: Fence | None = None) -> int: ...
```

Код: [state.py:716](../../../../../services/web-collector/src/jane_web_collector/state.py#L716).

#### Метод `StateStore.frontier_counts`

```python
def frontier_counts(self, collection_id: str) -> dict[str, int]: ...
```

Код: [state.py:723](../../../../../services/web-collector/src/jane_web_collector/state.py#L723).

#### Метод `StateStore.drop_pending`

```python
def drop_pending(self, collection_id: str, fence: Fence | None = None) -> int: ...
```

Budget reached: pending and stale in-flight URLs are dropped (not fetched in this run).

Код: [state.py:743](../../../../../services/web-collector/src/jane_web_collector/state.py#L743).

#### Метод `StateStore.defer_pending`

```python
def defer_pending(
    self,
    db: sqlite3.Connection,
    collection_id: str,
    state_key: str,
    fingerprint: str,
    seeded: Sequence[str],
) -> int: ...
```

Atomically checkpoint the collection, leaving its potentially millions of rows untouched.

Pending/inflight rows of this successful checkpoint are logically deferred. Legacy physical deferred rows remain readable; only the bounded batch actually borrowed changes ownership.

Код: [state.py:751](../../../../../services/web-collector/src/jane_web_collector/state.py#L751).

#### Метод `StateStore.settle_loans`

```python
def settle_loans(
    self,
    db: sqlite3.Connection,
    *,
    borrower_id: str | None = None,
    state_key: str | None = None,
    fingerprint: str | None = None,
) -> None: ...
```

Successful borrowers durably own their checkpoint; failed/cancelled ones return unfinished loans.

Completion is recorded with each page transaction, so recovery also works after retention removes a failed borrower's frontier. Its already processed pages are never loaned twice.

Код: [state.py:775](../../../../../services/web-collector/src/jane_web_collector/state.py#L775).

#### Метод `StateStore.adopt_deferred`

```python
def adopt_deferred(
    self,
    db: sqlite3.Connection,
    collection_id: str,
    state_key: str,
    fingerprint: str,
    limit: int,
    admit: Callable[[FrontierRow], FrontierRow | None],
) -> tuple[list[FrontierRow], list[str], dict[str, Any]]: ...
```

Atomically claim a bounded batch, validating it against the new run's effective policy.

Finished/cancelled/failed runs cannot supply each other's queue. The old collection keeps any unclaimed tail, so adoption is bounded even for multi-million URL catalogs.

Код: [state.py:809](../../../../../services/web-collector/src/jane_web_collector/state.py#L809).

#### Метод `StateStore.has_deferred_url`

```python
def has_deferred_url(self, state_key: str, fingerprint: str, url: str) -> bool: ...
```

Код: [state.py:878](../../../../../services/web-collector/src/jane_web_collector/state.py#L878).

#### Метод `StateStore.continuation_size`

```python
def continuation_size(self, state_key: str, fingerprint: str) -> int: ...
```

Код: [state.py:893](../../../../../services/web-collector/src/jane_web_collector/state.py#L893).

#### Метод `StateStore.save_seed_navigation`

```python
def save_seed_navigation(
    self,
    db: sqlite3.Connection,
    collection_id: str,
    strategy_id: str,
    url: str,
    resource: Mapping[str, Any],
    body: bytes,
) -> None: ...
```

Код: [state.py:909](../../../../../services/web-collector/src/jane_web_collector/state.py#L909).

#### Метод `StateStore.seed_navigation`

```python
def seed_navigation(
    self,
    collection_id: str,
    strategy_id: str,
    url: str,
    *,
    state_key: str | None = None,
    fingerprint: str | None = None,
) -> tuple[dict[str, Any], bytes] | None: ...
```

Код: [state.py:923](../../../../../services/web-collector/src/jane_web_collector/state.py#L923).

#### Метод `StateStore.clear_seed_navigation`

```python
def clear_seed_navigation(
    self,
    db: sqlite3.Connection,
    collection_id: str,
    strategy_id: str,
    state_key: str,
    fingerprint: str,
    seeded: Sequence[str],
) -> None: ...
```

Код: [state.py:949](../../../../../services/web-collector/src/jane_web_collector/state.py#L949).

#### Метод `StateStore.complete_discovery`

```python
def complete_discovery(
    self,
    db: sqlite3.Connection,
    state_key: str,
    fingerprint: str,
    seeded: Sequence[str],
) -> None: ...
```

Код: [state.py:965](../../../../../services/web-collector/src/jane_web_collector/state.py#L965).

#### Метод `StateStore.clear_continuation`

```python
def clear_continuation(self, db: sqlite3.Connection, state_key: str, fingerprint: str) -> None: ...
```

Код: [state.py:978](../../../../../services/web-collector/src/jane_web_collector/state.py#L978).

#### Метод `StateStore.pending_count`

```python
def pending_count(self, collection_id: str, *, materials_only: bool = False) -> int: ...
```

Код: [state.py:988](../../../../../services/web-collector/src/jane_web_collector/state.py#L988).

#### Метод `StateStore.frontier_size_for_state_key`

```python
def frontier_size_for_state_key(self, state_key: str) -> int: ...
```

Код: [state.py:996](../../../../../services/web-collector/src/jane_web_collector/state.py#L996).

#### Метод `StateStore.save_strategy_states`

```python
def save_strategy_states(
    self,
    db: sqlite3.Connection,
    collection_id: str,
    states: Mapping[str, Any],
) -> None: ...
```

Код: [state.py:1014](../../../../../services/web-collector/src/jane_web_collector/state.py#L1014).

#### Метод `StateStore.load_strategy_states`

```python
def load_strategy_states(self, collection_id: str) -> dict[str, Any]: ...
```

Код: [state.py:1024](../../../../../services/web-collector/src/jane_web_collector/state.py#L1024).

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

Код: [state.py:1030](../../../../../services/web-collector/src/jane_web_collector/state.py#L1030).

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

Код: [state.py:1041](../../../../../services/web-collector/src/jane_web_collector/state.py#L1041).

#### Метод `StateStore.materials_after`

```python
def materials_after(
    self,
    collection_id: str,
    after_seq: int,
    limit: int,
) -> list[tuple[int, dict[str, Any]]]: ...
```

Код: [state.py:1051](../../../../../services/web-collector/src/jane_web_collector/state.py#L1051).

#### Метод `StateStore.ack`

```python
def ack(self, collection_id: str, upto_seq: int) -> int: ...
```

Acknowledge every material with ``seq <= upto_seq``; returns how many were newly acknowledged.

Код: [state.py:1060](../../../../../services/web-collector/src/jane_web_collector/state.py#L1060).

#### Метод `StateStore.unacked_count`

```python
def unacked_count(self, collection_id: str) -> int: ...
```

Код: [state.py:1072](../../../../../services/web-collector/src/jane_web_collector/state.py#L1072).

#### Метод `StateStore.emitted_count`

```python
def emitted_count(self, collection_id: str) -> int: ...
```

Код: [state.py:1076](../../../../../services/web-collector/src/jane_web_collector/state.py#L1076).

#### Метод `StateStore.add_error`

```python
def add_error(
    self,
    db: sqlite3.Connection,
    collection_id: str,
    error: Mapping[str, Any],
) -> None: ...
```

Код: [state.py:1081](../../../../../services/web-collector/src/jane_web_collector/state.py#L1081).

#### Метод `StateStore.errors_after`

```python
def errors_after(
    self,
    collection_id: str,
    after_seq: int,
    limit: int,
) -> list[tuple[int, dict[str, Any]]]: ...
```

Код: [state.py:1088](../../../../../services/web-collector/src/jane_web_collector/state.py#L1088).

#### Метод `StateStore.url_state`

```python
def url_state(self, state_key: str, url: str) -> dict[str, Any] | None: ...
```

Код: [state.py:1098](../../../../../services/web-collector/src/jane_web_collector/state.py#L1098).

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

Код: [state.py:1106](../../../../../services/web-collector/src/jane_web_collector/state.py#L1106).

#### Метод `StateStore.state_summary`

```python
def state_summary(self, state_key: str) -> dict[str, Any] | None: ...
```

Код: [state.py:1138](../../../../../services/web-collector/src/jane_web_collector/state.py#L1138).

#### Метод `StateStore.delete_state`

```python
def delete_state(self, state_key: str) -> None: ...
```

Код: [state.py:1157](../../../../../services/web-collector/src/jane_web_collector/state.py#L1157).

#### Метод `StateStore.get_connection`

```python
def get_connection(self, connection_id: str) -> tuple[dict[str, Any], str] | None: ...
```

Код: [state.py:1177](../../../../../services/web-collector/src/jane_web_collector/state.py#L1177).

#### Метод `StateStore.put_connection`

```python
def put_connection(self, connection_id: str, body: Mapping[str, Any], etag: str) -> bool: ...
```

Returns True if created.

Код: [state.py:1181](../../../../../services/web-collector/src/jane_web_collector/state.py#L1181).

#### Метод `StateStore.delete_connection`

```python
def delete_connection(self, connection_id: str) -> bool: ...
```

Код: [state.py:1194](../../../../../services/web-collector/src/jane_web_collector/state.py#L1194).

#### Метод `StateStore.list_connections`

```python
def list_connections(self, after: str | None, limit: int) -> list[dict[str, Any]]: ...
```

Код: [state.py:1200](../../../../../services/web-collector/src/jane_web_collector/state.py#L1200).

#### Метод `StateStore.read`

```python
@contextmanager
def read(self) -> Iterator[sqlite3.Connection]: ...
```

The connection for single-statement reads (no write lock; ``jane_kit.stores.sqlite``).

Код: [state.py:1209](../../../../../services/web-collector/src/jane_web_collector/state.py#L1209).

#### Метод `StateStore.get_job`

```python
def get_job(self, job_id: str) -> str | None: ...
```

Код: [state.py:1214](../../../../../services/web-collector/src/jane_web_collector/state.py#L1214).

#### Метод `StateStore.work_row`

```python
def work_row(self, db: sqlite3.Connection, job_id: str) -> tuple[str | None, str] | None: ...
```

``(owner, status)`` of the collection of a job (``jane_kit.stores.sqlite.WorkRows``).

Код: [state.py:1218](../../../../../services/web-collector/src/jane_web_collector/state.py#L1218).

#### Метод `StateStore.cancel_unstarted`

```python
def cancel_unstarted(self, db: sqlite3.Connection, job_id: str, owner: str) -> bool: ...
```

A collection cancelled before its run started ends ``cancelled`` (only its lease holder).

Код: [state.py:1225](../../../../../services/web-collector/src/jane_web_collector/state.py#L1225).

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

Код: [state.py:1236](../../../../../services/web-collector/src/jane_web_collector/state.py#L1236).

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

Код: [state.py:1308](../../../../../services/web-collector/src/jane_web_collector/state.py#L1308).

#### Метод `StateStore.host_release_slot`

```python
def host_release_slot(self, host: str, token: str) -> None: ...
```

Give back the slot of ``token`` (or its place in line, if it never got one).

Код: [state.py:1331](../../../../../services/web-collector/src/jane_web_collector/state.py#L1331).

#### Метод `StateStore.host_push_back`

```python
def host_push_back(self, host: str, until: float) -> None: ...
```

Код: [state.py:1337](../../../../../services/web-collector/src/jane_web_collector/state.py#L1337).

#### Метод `StateStore.host_leave`

```python
def host_leave(self, host: str, instance_id: str) -> None: ...
```

Код: [state.py:1345](../../../../../services/web-collector/src/jane_web_collector/state.py#L1345).

#### Метод `StateStore.host_rows`

```python
def host_rows(self, host: str) -> dict[str, Any]: ...
```

Shared state of one host (diagnostics, tests).

Код: [state.py:1349](../../../../../services/web-collector/src/jane_web_collector/state.py#L1349).

#### Метод `StateStore.host_prune`

```python
def host_prune(self) -> int: ...
```

Drop expired registrations, slots and schedules of hosts nobody uses (housekeeping).

Код: [state.py:1355](../../../../../services/web-collector/src/jane_web_collector/state.py#L1355).
