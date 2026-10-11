# jane_kit.stores.postgres

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.stores.postgres.JobPosition](#jane_kitstorespostgresjobposition)
- [jane_kit.stores.postgres.PgConnect](#jane_kitstorespostgrespgconnect)
- [jane_kit.stores.postgres.pool_tx](#jane_kitstorespostgrespool_tx)
- [jane_kit.stores.postgres.migrate](#jane_kitstorespostgresmigrate)
- [jane_kit.stores.postgres.PgDatabase](#jane_kitstorespostgrespgdatabase)
- [jane_kit.stores.postgres.PgDatabase.__init__](#jane_kitstorespostgrespgdatabase__init__)
- [jane_kit.stores.postgres.PgDatabase.connect_timeout_ms](#jane_kitstorespostgrespgdatabaseconnect_timeout_ms)
- [jane_kit.stores.postgres.PgDatabase.pool](#jane_kitstorespostgrespgdatabasepool)
- [jane_kit.stores.postgres.PgDatabase.tx](#jane_kitstorespostgrespgdatabasetx)
- [jane_kit.stores.postgres.PgDatabase.open](#jane_kitstorespostgrespgdatabaseopen)
- [jane_kit.stores.postgres.PgDatabase.close](#jane_kitstorespostgrespgdatabaseclose)
- [jane_kit.stores.postgres.PgDatabase.ping](#jane_kitstorespostgrespgdatabaseping)
- [jane_kit.stores.postgres.PgIdempotencyStore](#jane_kitstorespostgrespgidempotencystore)
- [jane_kit.stores.postgres.PgIdempotencyStore.__init__](#jane_kitstorespostgrespgidempotencystore__init__)
- [jane_kit.stores.postgres.PgIdempotencyStore.owner](#jane_kitstorespostgrespgidempotencystoreowner)
- [jane_kit.stores.postgres.PgIdempotencyStore.lease_s](#jane_kitstorespostgrespgidempotencystorelease_s)
- [jane_kit.stores.postgres.PgIdempotencyStore.layout](#jane_kitstorespostgrespgidempotencystorelayout)
- [jane_kit.stores.postgres.PgIdempotencyStore.gc_batch](#jane_kitstorespostgrespgidempotencystoregc_batch)
- [jane_kit.stores.postgres.PgIdempotencyStore.ddl](#jane_kitstorespostgrespgidempotencystoreddl)
- [jane_kit.stores.postgres.PgIdempotencyStore.begin_sync](#jane_kitstorespostgrespgidempotencystorebegin_sync)
- [jane_kit.stores.postgres.PgIdempotencyStore.complete_sync](#jane_kitstorespostgrespgidempotencystorecomplete_sync)
- [jane_kit.stores.postgres.PgIdempotencyStore.release_sync](#jane_kitstorespostgrespgidempotencystorerelease_sync)
- [jane_kit.stores.postgres.PgIdempotencyStore.heartbeat_sync](#jane_kitstorespostgrespgidempotencystoreheartbeat_sync)
- [jane_kit.stores.postgres.PgIdempotencyStore.gc_sync](#jane_kitstorespostgrespgidempotencystoregc_sync)
- [jane_kit.stores.postgres.PgIdempotencyStore.begin](#jane_kitstorespostgrespgidempotencystorebegin)
- [jane_kit.stores.postgres.PgIdempotencyStore.complete](#jane_kitstorespostgrespgidempotencystorecomplete)
- [jane_kit.stores.postgres.PgIdempotencyStore.release](#jane_kitstorespostgrespgidempotencystorerelease)
- [jane_kit.stores.postgres.PgIdempotencyStore.heartbeat](#jane_kitstorespostgrespgidempotencystoreheartbeat)
- [jane_kit.stores.postgres.PgIdempotencyStore.gc](#jane_kitstorespostgrespgidempotencystoregc)
- [jane_kit.stores.postgres.PgJobStore](#jane_kitstorespostgrespgjobstore)
- [jane_kit.stores.postgres.PgJobStore.__init__](#jane_kitstorespostgrespgjobstore__init__)
- [jane_kit.stores.postgres.PgJobStore.owner](#jane_kitstorespostgrespgjobstoreowner)
- [jane_kit.stores.postgres.PgJobStore.lease_s](#jane_kitstorespostgrespgjobstorelease_s)
- [jane_kit.stores.postgres.PgJobStore.retention_s](#jane_kitstorespostgrespgjobstoreretention_s)
- [jane_kit.stores.postgres.PgJobStore.ddl](#jane_kitstorespostgrespgjobstoreddl)
- [jane_kit.stores.postgres.PgJobStore.create_sync](#jane_kitstorespostgrespgjobstorecreate_sync)
- [jane_kit.stores.postgres.PgJobStore.get_sync](#jane_kitstorespostgrespgjobstoreget_sync)
- [jane_kit.stores.postgres.PgJobStore.save_sync](#jane_kitstorespostgrespgjobstoresave_sync)
- [jane_kit.stores.postgres.PgJobStore.heartbeat_sync](#jane_kitstorespostgrespgjobstoreheartbeat_sync)
- [jane_kit.stores.postgres.PgJobStore.sweep_sync](#jane_kitstorespostgrespgjobstoresweep_sync)
- [jane_kit.stores.postgres.PgJobStore.release_owned_sync](#jane_kitstorespostgrespgjobstorerelease_owned_sync)
- [jane_kit.stores.postgres.PgJobStore.page_sync](#jane_kitstorespostgrespgjobstorepage_sync)
- [jane_kit.stores.postgres.PgJobStore.create](#jane_kitstorespostgrespgjobstorecreate)
- [jane_kit.stores.postgres.PgJobStore.get](#jane_kitstorespostgrespgjobstoreget)
- [jane_kit.stores.postgres.PgJobStore.save](#jane_kitstorespostgrespgjobstoresave)
- [jane_kit.stores.postgres.PgJobStore.heartbeat](#jane_kitstorespostgrespgjobstoreheartbeat)
- [jane_kit.stores.postgres.PgJobStore.sweep](#jane_kitstorespostgrespgjobstoresweep)
- [jane_kit.stores.postgres.PgJobStore.release_owned](#jane_kitstorespostgrespgjobstorerelease_owned)
- [jane_kit.stores.postgres.PgJobStore.page](#jane_kitstorespostgrespgjobstorepage)

## jane_kit.stores.postgres.JobPosition

**Повторний експорт.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:45](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L45).

```python
from jane_kit.jobs import JobPosition as JobPosition
```

Повторний експорт: [jane_kit.jobs.JobPosition](jane_kit.jobs.md#jane_kitjobsjobposition).

## jane_kit.stores.postgres.PgConnect

**Змінна.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:68](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L68).

```python
PgConnect = Callable[[], AbstractContextManager[Connection[Any]]]
```

### Опис із вихідного коду

```text
Yields a connection inside one transaction (commit on exit, rollback on error).
```

## jane_kit.stores.postgres.pool_tx

**Функція.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:74](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L74).

```python
def pool_tx(pool: Any) -> PgConnect:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `pool` | `Any` | `—` | positional-or-keyword |

Результат: `PgConnect`.

### Опис із вихідного коду

```text
:data:`PgConnect` over a ``psycopg_pool.ConnectionPool``.
```

## jane_kit.stores.postgres.migrate

**Функція.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:99](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L99).

```python
def migrate(tx: PgConnect, lock: str, *stores: PgIdempotencyStore | PgJobStore, schema: str | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `tx` | `PgConnect` | `—` | positional-or-keyword |
| `lock` | `str` | `—` | positional-or-keyword |
| `stores` | `PgIdempotencyStore \| PgJobStore` | `—` | var-positional |
| `schema` | `str \| None` | `None` | keyword-only |

Результат: `None`.

### Опис із вихідного коду

```text
Create or upgrade the tables of ``stores`` in one transaction under ``pg_advisory_xact_lock(lock)``.

Idempotent and safe when several instances start at once. ``schema`` is created first when given.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:116](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L116).

```python
migrate(pg.tx, schema, pg_store, schema=schema)
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:60](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L60).

```python
migrate(db.tx, f"kit-test-{schema}", store, schema=schema)
```

## jane_kit.stores.postgres.PgDatabase

**Клас.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:115](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L115).

```python
class PgDatabase:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.stores.postgres.md#jane_kitstorespostgrespgdatabase__init__) | Конструктор | ні |
| [connect_timeout_ms](jane_kit.stores.postgres.md#jane_kitstorespostgrespgdatabaseconnect_timeout_ms) | Поле екземпляра | ні |
| [pool](jane_kit.stores.postgres.md#jane_kitstorespostgrespgdatabasepool) | Поле екземпляра | ні |
| [tx](jane_kit.stores.postgres.md#jane_kitstorespostgrespgdatabasetx) | Поле екземпляра | ні |
| [open](jane_kit.stores.postgres.md#jane_kitstorespostgrespgdatabaseopen) | Метод | ні |
| [close](jane_kit.stores.postgres.md#jane_kitstorespostgrespgdatabaseclose) | Метод | ні |
| [ping](jane_kit.stores.postgres.md#jane_kitstorespostgrespgdatabaseping) | Метод | ні |

### Опис із вихідного коду

```text
A psycopg pool of the service's own database (``autocommit``; transactions via :meth:`tx`).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:109](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L109).

```python
pg = PgDatabase(dsn, max_size=8, connect_timeout_ms=10_000)
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:47](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L47).

```python
db = PgDatabase(dsn, max_size=8, connect_timeout_ms=10_000)
```

## jane_kit.stores.postgres.PgDatabase.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:118](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L118).

```python
def __init__(self, dsn: str, *, max_size: int, connect_timeout_ms: int, min_size: int=0) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `dsn` | `str` | `—` | positional-or-keyword |
| `max_size` | `int` | `—` | keyword-only |
| `connect_timeout_ms` | `int` | `—` | keyword-only |
| `min_size` | `int` | `0` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:109](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L109).

```python
pg = PgDatabase(dsn, max_size=8, connect_timeout_ms=10_000)
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:47](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L47).

```python
db = PgDatabase(dsn, max_size=8, connect_timeout_ms=10_000)
```

## jane_kit.stores.postgres.PgDatabase.connect_timeout_ms

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:121](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L121).

```python
self.connect_timeout_ms = connect_timeout_ms
```

## jane_kit.stores.postgres.PgDatabase.pool

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:122](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L122).

```python
self.pool: Any = ConnectionPool(dsn, min_size=min_size, max_size=max_size, open=False, timeout=connect_timeout_ms / 1000, kwargs={'autocommit': True, 'connect_timeout': max(1, connect_timeout_ms // 1000)})
```

## jane_kit.stores.postgres.PgDatabase.tx

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:130](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L130).

```python
self.tx: PgConnect = pool_tx(self.pool)
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:119](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L119).

```python
pg.tx()
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:73](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L73).

```python
db.tx()
```

## jane_kit.stores.postgres.PgDatabase.open

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:132](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L132).

```python
def open(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:110](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L110).

```python
pg.open()
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:48](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L48).

```python
db.open()
```

## jane_kit.stores.postgres.PgDatabase.close

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:135](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L135).

```python
def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:121](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L121).

```python
pg.close()
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:52](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L52).

```python
db.close()
```

## jane_kit.stores.postgres.PgDatabase.ping

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:138](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L138).

```python
def ping(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_kit.stores.postgres.PgIdempotencyStore

**Клас.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:145](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L145).

```python
class PgIdempotencyStore:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.stores.postgres.md#jane_kitstorespostgrespgidempotencystore__init__) | Конструктор | ні |
| [owner](jane_kit.stores.postgres.md#jane_kitstorespostgrespgidempotencystoreowner) | Поле екземпляра | ні |
| [lease_s](jane_kit.stores.postgres.md#jane_kitstorespostgrespgidempotencystorelease_s) | Поле екземпляра | ні |
| [layout](jane_kit.stores.postgres.md#jane_kitstorespostgrespgidempotencystorelayout) | Поле екземпляра | ні |
| [gc_batch](jane_kit.stores.postgres.md#jane_kitstorespostgrespgidempotencystoregc_batch) | Поле екземпляра | ні |
| [ddl](jane_kit.stores.postgres.md#jane_kitstorespostgrespgidempotencystoreddl) | Метод | ні |
| [begin_sync](jane_kit.stores.postgres.md#jane_kitstorespostgrespgidempotencystorebegin_sync) | Метод | ні |
| [complete_sync](jane_kit.stores.postgres.md#jane_kitstorespostgrespgidempotencystorecomplete_sync) | Метод | ні |
| [release_sync](jane_kit.stores.postgres.md#jane_kitstorespostgrespgidempotencystorerelease_sync) | Метод | ні |
| [heartbeat_sync](jane_kit.stores.postgres.md#jane_kitstorespostgrespgidempotencystoreheartbeat_sync) | Метод | ні |
| [gc_sync](jane_kit.stores.postgres.md#jane_kitstorespostgrespgidempotencystoregc_sync) | Метод | ні |
| [begin](jane_kit.stores.postgres.md#jane_kitstorespostgrespgidempotencystorebegin) | Метод | ні |
| [complete](jane_kit.stores.postgres.md#jane_kitstorespostgrespgidempotencystorecomplete) | Метод | ні |
| [release](jane_kit.stores.postgres.md#jane_kitstorespostgrespgidempotencystorerelease) | Метод | ні |
| [heartbeat](jane_kit.stores.postgres.md#jane_kitstorespostgrespgidempotencystoreheartbeat) | Метод | ні |
| [gc](jane_kit.stores.postgres.md#jane_kitstorespostgrespgidempotencystoregc) | Метод | ні |

### Опис із вихідного коду

```text
jane-kit ``IdempotencyStore`` on table ``table`` (in ``schema``, or on the connection's search path).

``layout``: ``"split"`` - response in ``status_code``/``body``/``headers`` columns; ``"json"`` - one
``response`` jsonb column (``{"status_code", "body", "headers"}``). ``in_progress_lease_s``: how long a claim
survives without :meth:`heartbeat` (a stopped instance releases its keys after this).

``begin`` and its matching ``complete``/``release`` run in the same caller context (as in
``run_idempotent``); concurrent requests on this store keep separate tokens. Heartbeat is process-wide.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:112](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L112).

```python
pg_store = PgIdempotencyStore(
        pg.tx, owner="one-service", in_progress_lease_s=60, schema=schema, layout=request.param
    )
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:59](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L59).

```python
store = PgIdempotencyStore(db.tx, owner=owner, in_progress_lease_s=lease, schema=schema, **kw)
```

## jane_kit.stores.postgres.PgIdempotencyStore.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:156](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L156).

```python
def __init__(self, tx: PgConnect, *, owner: str, in_progress_lease_s: float, table: str='idempotency', schema: str | None=None, layout: Literal['split', 'json']='split', gc_batch: int=500) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `tx` | `PgConnect` | `—` | positional-or-keyword |
| `owner` | `str` | `—` | keyword-only |
| `in_progress_lease_s` | `float` | `—` | keyword-only |
| `table` | `str` | `'idempotency'` | keyword-only |
| `schema` | `str \| None` | `None` | keyword-only |
| `layout` | `Literal['split', 'json']` | `'split'` | keyword-only |
| `gc_batch` | `int` | `500` | keyword-only |

Результат: `None`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:112](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L112).

```python
pg_store = PgIdempotencyStore(
        pg.tx, owner="one-service", in_progress_lease_s=60, schema=schema, layout=request.param
    )
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:59](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L59).

```python
store = PgIdempotencyStore(db.tx, owner=owner, in_progress_lease_s=lease, schema=schema, **kw)
```

## jane_kit.stores.postgres.PgIdempotencyStore.owner

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:170](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L170).

```python
self.owner = owner
```

## jane_kit.stores.postgres.PgIdempotencyStore.lease_s

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:171](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L171).

```python
self.lease_s = float(in_progress_lease_s)
```

## jane_kit.stores.postgres.PgIdempotencyStore.layout

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:172](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L172).

```python
self.layout = layout
```

## jane_kit.stores.postgres.PgIdempotencyStore.gc_batch

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:173](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L173).

```python
self.gc_batch = gc_batch
```

## jane_kit.stores.postgres.PgIdempotencyStore.ddl

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:178](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L178).

```python
def ddl(self) -> list[sql.Composed]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `list[sql.Composed]`.

## jane_kit.stores.postgres.PgIdempotencyStore.begin_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:214](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L214).

```python
def begin_sync(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |
| `fingerprint` | `str` | `—` | positional-or-keyword |
| `ttl_s` | `float` | `—` | positional-or-keyword |

Результат: `IdempotencyRecord | None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:189](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L189).

```python
replay = store.begin_sync("old", "fp", 60)
```

## jane_kit.stores.postgres.PgIdempotencyStore.complete_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:265](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L265).

```python
def complete_sync(self, key: str, response: StoredResponse) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |
| `response` | `StoredResponse` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.stores.postgres.PgIdempotencyStore.release_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:290](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L290).

```python
def release_sync(self, key: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.stores.postgres.PgIdempotencyStore.heartbeat_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:304](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L304).

```python
def heartbeat_sync(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Renew the leases of the claims this process still holds (not those of a previous start).
```

## jane_kit.stores.postgres.PgIdempotencyStore.gc_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:321](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L321).

```python
def gc_sync(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Delete up to ``gc_batch`` expired keys (any instance; locked rows are skipped).
```

## jane_kit.stores.postgres.PgIdempotencyStore.begin

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:336](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L336).

```python
async def begin(self, key: str, fingerprint: str, ttl_s: float) -> IdempotencyRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |
| `fingerprint` | `str` | `—` | positional-or-keyword |
| `ttl_s` | `float` | `—` | positional-or-keyword |

Результат: `IdempotencyRecord | None`.

## jane_kit.stores.postgres.PgIdempotencyStore.complete

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:343](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L343).

```python
async def complete(self, key: str, response: StoredResponse) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |
| `response` | `StoredResponse` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.stores.postgres.PgIdempotencyStore.release

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:347](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L347).

```python
async def release(self, key: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.stores.postgres.PgIdempotencyStore.heartbeat

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:351](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L351).

```python
async def heartbeat(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

## jane_kit.stores.postgres.PgIdempotencyStore.gc

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:354](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L354).

```python
async def gc(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

## jane_kit.stores.postgres.PgJobStore

**Клас.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:359](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L359).

```python
class PgJobStore:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstore__init__) | Конструктор | ні |
| [owner](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstoreowner) | Поле екземпляра | ні |
| [lease_s](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstorelease_s) | Поле екземпляра | ні |
| [retention_s](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstoreretention_s) | Поле екземпляра | ні |
| [ddl](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstoreddl) | Метод | ні |
| [create_sync](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstorecreate_sync) | Метод | ні |
| [get_sync](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstoreget_sync) | Метод | ні |
| [save_sync](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstoresave_sync) | Метод | ні |
| [heartbeat_sync](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstoreheartbeat_sync) | Метод | ні |
| [sweep_sync](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstoresweep_sync) | Метод | ні |
| [release_owned_sync](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstorerelease_owned_sync) | Метод | ні |
| [page_sync](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstorepage_sync) | Метод | ні |
| [create](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstorecreate) | Метод | ні |
| [get](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstoreget) | Метод | ні |
| [save](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstoresave) | Метод | ні |
| [heartbeat](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstoreheartbeat) | Метод | ні |
| [sweep](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstoresweep) | Метод | ні |
| [release_owned](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstorerelease_owned) | Метод | ні |
| [page](jane_kit.stores.postgres.md#jane_kitstorespostgrespgjobstorepage) | Метод | ні |

### Опис із вихідного коду

```text
jane-kit ``JobStore`` on table ``table`` (columns ``job_id``, ``doc_column`` jsonb, ``owner``,
``lease_until``, ``finished_at``, ``updated_at``); see the module docstring for the rules.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:66](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L66).

```python
store = PgJobStore(db.tx, owner=owner, lease_s=lease, retention_s=3600, schema=schema, **kw)
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:176](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L176).

```python
job_store = PgJobStore(
        db.tx, owner="new", lease_s=60, retention_s=3600, schema=schema, table="legacy_jobs", doc_column="job"
    )
```

## jane_kit.stores.postgres.PgJobStore.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:363](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L363).

```python
def __init__(self, tx: PgConnect, *, owner: str, lease_s: float, retention_s: float, table: str='jobs', schema: str | None=None, doc_column: str='doc') -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `tx` | `PgConnect` | `—` | positional-or-keyword |
| `owner` | `str` | `—` | keyword-only |
| `lease_s` | `float` | `—` | keyword-only |
| `retention_s` | `float` | `—` | keyword-only |
| `table` | `str` | `'jobs'` | keyword-only |
| `schema` | `str \| None` | `None` | keyword-only |
| `doc_column` | `str` | `'doc'` | keyword-only |

Результат: `None`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:66](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L66).

```python
store = PgJobStore(db.tx, owner=owner, lease_s=lease, retention_s=3600, schema=schema, **kw)
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:176](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L176).

```python
job_store = PgJobStore(
        db.tx, owner="new", lease_s=60, retention_s=3600, schema=schema, table="legacy_jobs", doc_column="job"
    )
```

## jane_kit.stores.postgres.PgJobStore.owner

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:377](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L377).

```python
self.owner = owner
```

## jane_kit.stores.postgres.PgJobStore.lease_s

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:378](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L378).

```python
self.lease_s = float(lease_s)
```

## jane_kit.stores.postgres.PgJobStore.retention_s

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:379](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L379).

```python
self.retention_s = float(retention_s)
```

## jane_kit.stores.postgres.PgJobStore.ddl

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:386](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L386).

```python
def ddl(self) -> list[sql.Composed]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `list[sql.Composed]`.

## jane_kit.stores.postgres.PgJobStore.create_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:426](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L426).

```python
def create_sync(self, job: Job) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job` | `Job` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `Conflict`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_kit.stores.postgres.PgJobStore.get_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:481](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L481).

```python
def get_sync(self, job_id: str) -> Job | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job_id` | `str` | `—` | positional-or-keyword |

Результат: `Job | None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:192](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L192).

```python
legacy = job_store.get_sync("job_running")
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_postgres.py:195](../../../../../../libs/jane-kit/tests/test_stores_postgres.py#L195).

```python
reaped = job_store.get_sync("job_running")
```

## jane_kit.stores.postgres.PgJobStore.save_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:505](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L505).

```python
def save_sync(self, job: Job) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job` | `Job` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.stores.postgres.PgJobStore.heartbeat_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:539](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L539).

```python
def heartbeat_sync(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Renew the leases of the jobs this process runs (never those of a previous start).
```

## jane_kit.stores.postgres.PgJobStore.sweep_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:558](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L558).

```python
def sweep_sync(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
End every job whose lease expired (any owner); returns how many.
```

## jane_kit.stores.postgres.PgJobStore.release_owned_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:563](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L563).

```python
def release_owned_sync(self, reason: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `reason` | `str` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Graceful stop, after the runner cancelled this instance's jobs: unfinished jobs of this owner end
``cancelled`` and cancelled ones without a recorded cancellation get ``reason``.
```

## jane_kit.stores.postgres.PgJobStore.page_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:600](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L600).

```python
def page_sync(self, kind: str, *, labels: Mapping[str, str], statuses: Iterable[str] | None, after: JobPosition | None, limit: int) -> list[Job]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `str` | `—` | positional-or-keyword |
| `labels` | `Mapping[str, str]` | `—` | keyword-only |
| `statuses` | `Iterable[str] \| None` | `—` | keyword-only |
| `after` | `JobPosition \| None` | `—` | keyword-only |
| `limit` | `int` | `—` | keyword-only |

Результат: `list[Job]`.

### Опис із вихідного коду

```text
Jobs of ``kind`` carrying all ``labels``, newest first (``created_at``, then ``job_id``), strictly after
``after``. Jobs of stopped instances are ended first, so a status filter sees them as ``get`` does.
```

## jane_kit.stores.postgres.PgJobStore.create

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:649](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L649).

```python
async def create(self, job: Job) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job` | `Job` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.stores.postgres.PgJobStore.get

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:652](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L652).

```python
async def get(self, job_id: str) -> Job | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job_id` | `str` | `—` | positional-or-keyword |

Результат: `Job | None`.

## jane_kit.stores.postgres.PgJobStore.save

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:655](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L655).

```python
async def save(self, job: Job) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job` | `Job` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.stores.postgres.PgJobStore.heartbeat

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:658](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L658).

```python
async def heartbeat(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

## jane_kit.stores.postgres.PgJobStore.sweep

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:661](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L661).

```python
async def sweep(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

## jane_kit.stores.postgres.PgJobStore.release_owned

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:664](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L664).

```python
async def release_owned(self, reason: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `reason` | `str` | `—` | positional-or-keyword |

Результат: `int`.

## jane_kit.stores.postgres.PgJobStore.page

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/postgres.py:667](../../../../../../libs/jane-kit/src/jane_kit/stores/postgres.py#L667).

```python
async def page(self, kind: str, *, labels: Mapping[str, str], statuses: Iterable[str] | None, after: JobPosition | None, limit: int) -> list[Job]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `str` | `—` | positional-or-keyword |
| `labels` | `Mapping[str, str]` | `—` | keyword-only |
| `statuses` | `Iterable[str] \| None` | `—` | keyword-only |
| `after` | `JobPosition \| None` | `—` | keyword-only |
| `limit` | `int` | `—` | keyword-only |

Результат: `list[Job]`.
