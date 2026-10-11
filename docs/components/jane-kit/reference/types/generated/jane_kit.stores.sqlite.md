# jane_kit.stores.sqlite

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.stores.sqlite.SqliteTx](#jane_kitstoressqlitesqlitetx)
- [jane_kit.stores.sqlite.SqliteTx.tx](#jane_kitstoressqlitesqlitetxtx)
- [jane_kit.stores.sqlite.SqliteDatabase](#jane_kitstoressqlitesqlitedatabase)
- [jane_kit.stores.sqlite.SqliteDatabase.__init__](#jane_kitstoressqlitesqlitedatabase__init__)
- [jane_kit.stores.sqlite.SqliteDatabase.path](#jane_kitstoressqlitesqlitedatabasepath)
- [jane_kit.stores.sqlite.SqliteDatabase.tx](#jane_kitstoressqlitesqlitedatabasetx)
- [jane_kit.stores.sqlite.SqliteDatabase.read](#jane_kitstoressqlitesqlitedatabaseread)
- [jane_kit.stores.sqlite.SqliteDatabase.close](#jane_kitstoressqlitesqlitedatabaseclose)
- [jane_kit.stores.sqlite.SqliteIdempotencyStore](#jane_kitstoressqlitesqliteidempotencystore)
- [jane_kit.stores.sqlite.SqliteIdempotencyStore.__init__](#jane_kitstoressqlitesqliteidempotencystore__init__)
- [jane_kit.stores.sqlite.SqliteIdempotencyStore.db](#jane_kitstoressqlitesqliteidempotencystoredb)
- [jane_kit.stores.sqlite.SqliteIdempotencyStore.owner](#jane_kitstoressqlitesqliteidempotencystoreowner)
- [jane_kit.stores.sqlite.SqliteIdempotencyStore.lease_s](#jane_kitstoressqlitesqliteidempotencystorelease_s)
- [jane_kit.stores.sqlite.SqliteIdempotencyStore.table](#jane_kitstoressqlitesqliteidempotencystoretable)
- [jane_kit.stores.sqlite.SqliteIdempotencyStore.migrate](#jane_kitstoressqlitesqliteidempotencystoremigrate)
- [jane_kit.stores.sqlite.SqliteIdempotencyStore.begin_sync](#jane_kitstoressqlitesqliteidempotencystorebegin_sync)
- [jane_kit.stores.sqlite.SqliteIdempotencyStore.complete_sync](#jane_kitstoressqlitesqliteidempotencystorecomplete_sync)
- [jane_kit.stores.sqlite.SqliteIdempotencyStore.release_sync](#jane_kitstoressqlitesqliteidempotencystorerelease_sync)
- [jane_kit.stores.sqlite.SqliteIdempotencyStore.heartbeat_sync](#jane_kitstoressqlitesqliteidempotencystoreheartbeat_sync)
- [jane_kit.stores.sqlite.SqliteIdempotencyStore.begin](#jane_kitstoressqlitesqliteidempotencystorebegin)
- [jane_kit.stores.sqlite.SqliteIdempotencyStore.complete](#jane_kitstoressqlitesqliteidempotencystorecomplete)
- [jane_kit.stores.sqlite.SqliteIdempotencyStore.release](#jane_kitstoressqlitesqliteidempotencystorerelease)
- [jane_kit.stores.sqlite.SqliteIdempotencyStore.heartbeat](#jane_kitstoressqlitesqliteidempotencystoreheartbeat)
- [jane_kit.stores.sqlite.SqliteJobStore](#jane_kitstoressqlitesqlitejobstore)
- [jane_kit.stores.sqlite.SqliteJobStore.__init__](#jane_kitstoressqlitesqlitejobstore__init__)
- [jane_kit.stores.sqlite.SqliteJobStore.owner](#jane_kitstoressqlitesqlitejobstoreowner)
- [jane_kit.stores.sqlite.SqliteJobStore.lease_s](#jane_kitstoressqlitesqlitejobstorelease_s)
- [jane_kit.stores.sqlite.SqliteJobStore.retention_s](#jane_kitstoressqlitesqlitejobstoreretention_s)
- [jane_kit.stores.sqlite.SqliteJobStore.migrate](#jane_kitstoressqlitesqlitejobstoremigrate)
- [jane_kit.stores.sqlite.SqliteJobStore.create_sync](#jane_kitstoressqlitesqlitejobstorecreate_sync)
- [jane_kit.stores.sqlite.SqliteJobStore.get_sync](#jane_kitstoressqlitesqlitejobstoreget_sync)
- [jane_kit.stores.sqlite.SqliteJobStore.save_sync](#jane_kitstoressqlitesqlitejobstoresave_sync)
- [jane_kit.stores.sqlite.SqliteJobStore.heartbeat_sync](#jane_kitstoressqlitesqlitejobstoreheartbeat_sync)
- [jane_kit.stores.sqlite.SqliteJobStore.sweep_sync](#jane_kitstoressqlitesqlitejobstoresweep_sync)
- [jane_kit.stores.sqlite.SqliteJobStore.heartbeat](#jane_kitstoressqlitesqlitejobstoreheartbeat)
- [jane_kit.stores.sqlite.SqliteJobStore.sweep](#jane_kitstoressqlitesqlitejobstoresweep)
- [jane_kit.stores.sqlite.WorkRows](#jane_kitstoressqliteworkrows)
- [jane_kit.stores.sqlite.WorkRows.work_row](#jane_kitstoressqliteworkrowswork_row)
- [jane_kit.stores.sqlite.WorkRows.cancel_unstarted](#jane_kitstoressqliteworkrowscancel_unstarted)
- [jane_kit.stores.sqlite.SqliteWorkJobStore](#jane_kitstoressqlitesqliteworkjobstore)
- [jane_kit.stores.sqlite.SqliteWorkJobStore.__init__](#jane_kitstoressqlitesqliteworkjobstore__init__)
- [jane_kit.stores.sqlite.SqliteWorkJobStore.work](#jane_kitstoressqlitesqliteworkjobstorework)
- [jane_kit.stores.sqlite.SqliteWorkJobStore.owner](#jane_kitstoressqlitesqliteworkjobstoreowner)
- [jane_kit.stores.sqlite.SqliteWorkJobStore.migrate](#jane_kitstoressqlitesqliteworkjobstoremigrate)
- [jane_kit.stores.sqlite.SqliteWorkJobStore.create_sync](#jane_kitstoressqlitesqliteworkjobstorecreate_sync)
- [jane_kit.stores.sqlite.SqliteWorkJobStore.save_sync](#jane_kitstoressqlitesqliteworkjobstoresave_sync)

## jane_kit.stores.sqlite.SqliteTx

**Клас.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:62](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L62).

```python
class SqliteTx(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [tx](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitetxtx) | Метод | ні |

## jane_kit.stores.sqlite.SqliteTx.tx

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:63](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L63).

```python
def tx(self) -> AbstractContextManager[sqlite3.Connection]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `AbstractContextManager[sqlite3.Connection]`.

### Опис із вихідного коду

```text
``BEGIN IMMEDIATE`` ... ``COMMIT`` (rollback on error) on the service's connection.
```

## jane_kit.stores.sqlite.SqliteDatabase

**Клас.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:75](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L75).

```python
class SqliteDatabase:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitedatabase__init__) | Конструктор | ні |
| [path](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitedatabasepath) | Поле екземпляра | ні |
| [tx](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitedatabasetx) | Метод | ні |
| [read](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitedatabaseread) | Метод | ні |
| [close](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitedatabaseclose) | Метод | ні |

### Опис із вихідного коду

```text
A SQLite state file shared by the processes of one host (WAL, ``busy_timeout_ms`` lock wait).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:97](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L97).

```python
sqlite = SqliteDatabase(tmp_path / "claims.sqlite", busy_timeout_ms=5_000)
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_sqlite.py:21](../../../../../../libs/jane-kit/tests/test_stores_sqlite.py#L21).

```python
return SqliteDatabase(tmp_path / "state.sqlite", busy_timeout_ms=5_000)
```

## jane_kit.stores.sqlite.SqliteDatabase.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:78](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L78).

```python
def __init__(self, path: Path, *, busy_timeout_ms: int) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `path` | `Path` | `—` | positional-or-keyword |
| `busy_timeout_ms` | `int` | `—` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:97](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L97).

```python
sqlite = SqliteDatabase(tmp_path / "claims.sqlite", busy_timeout_ms=5_000)
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_sqlite.py:21](../../../../../../libs/jane-kit/tests/test_stores_sqlite.py#L21).

```python
return SqliteDatabase(tmp_path / "state.sqlite", busy_timeout_ms=5_000)
```

## jane_kit.stores.sqlite.SqliteDatabase.path

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:80](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L80).

```python
self.path = path
```

## jane_kit.stores.sqlite.SqliteDatabase.tx

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:90](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L90).

```python
def tx(self) -> Iterator[sqlite3.Connection]:
```

Декоратори: `contextmanager`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Iterator[sqlite3.Connection]`.

Явні `raise` у тілі: `повторний raise`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_stores_sqlite.py:192](../../../../../../libs/jane-kit/tests/test_stores_sqlite.py#L192).

```python
db.tx()
```

## jane_kit.stores.sqlite.SqliteDatabase.read

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:101](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L101).

```python
def read(self) -> Iterator[sqlite3.Connection]:
```

Декоратори: `contextmanager`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Iterator[sqlite3.Connection]`.

### Опис із вихідного коду

```text
The connection for single-statement reads (autocommit; no write lock).
```

## jane_kit.stores.sqlite.SqliteDatabase.close

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:106](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L106).

```python
def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:103](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L103).

```python
sqlite.close()
```

## jane_kit.stores.sqlite.SqliteIdempotencyStore

**Клас.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:123](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L123).

```python
class SqliteIdempotencyStore:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystore__init__) | Конструктор | ні |
| [db](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystoredb) | Поле екземпляра | ні |
| [owner](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystoreowner) | Поле екземпляра | ні |
| [lease_s](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystorelease_s) | Поле екземпляра | ні |
| [table](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystoretable) | Поле екземпляра | ні |
| [migrate](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystoremigrate) | Метод | ні |
| [begin_sync](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystorebegin_sync) | Метод | ні |
| [complete_sync](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystorecomplete_sync) | Метод | ні |
| [release_sync](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystorerelease_sync) | Метод | ні |
| [heartbeat_sync](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystoreheartbeat_sync) | Метод | ні |
| [begin](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystorebegin) | Метод | ні |
| [complete](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystorecomplete) | Метод | ні |
| [release](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystorerelease) | Метод | ні |
| [heartbeat](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteidempotencystoreheartbeat) | Метод | ні |

### Опис із вихідного коду

```text
jane-kit ``IdempotencyStore`` on table ``table`` (``key``, ``fingerprint``, ``state``, ``expires_at``,
``response`` JSON text, ``lease_until``, ``owner``, ``token``).

``begin`` and its matching ``complete``/``release`` run in the same caller context (as in
``run_idempotent``); concurrent requests on this store keep separate tokens. Heartbeat is process-wide.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:98](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L98).

```python
store = SqliteIdempotencyStore(sqlite, owner="one-service", in_progress_lease_s=60)
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_sqlite.py:25](../../../../../../libs/jane-kit/tests/test_stores_sqlite.py#L25).

```python
store = SqliteIdempotencyStore(db, owner=owner, in_progress_lease_s=lease)
```

## jane_kit.stores.sqlite.SqliteIdempotencyStore.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:131](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L131).

```python
def __init__(self, db: SqliteTx, *, owner: str, in_progress_lease_s: float, table: str='idempotency') -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `SqliteTx` | `—` | positional-or-keyword |
| `owner` | `str` | `—` | keyword-only |
| `in_progress_lease_s` | `float` | `—` | keyword-only |
| `table` | `str` | `'idempotency'` | keyword-only |

Результат: `None`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:98](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L98).

```python
store = SqliteIdempotencyStore(sqlite, owner="one-service", in_progress_lease_s=60)
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_sqlite.py:25](../../../../../../libs/jane-kit/tests/test_stores_sqlite.py#L25).

```python
store = SqliteIdempotencyStore(db, owner=owner, in_progress_lease_s=lease)
```

## jane_kit.stores.sqlite.SqliteIdempotencyStore.db

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:136](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L136).

```python
self.db = db
```

## jane_kit.stores.sqlite.SqliteIdempotencyStore.owner

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:137](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L137).

```python
self.owner = owner
```

## jane_kit.stores.sqlite.SqliteIdempotencyStore.lease_s

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:138](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L138).

```python
self.lease_s = float(in_progress_lease_s)
```

## jane_kit.stores.sqlite.SqliteIdempotencyStore.table

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:139](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L139).

```python
self.table = _ident(table)
```

## jane_kit.stores.sqlite.SqliteIdempotencyStore.migrate

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:142](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L142).

```python
def migrate(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:99](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L99).

```python
store.migrate()
```

## jane_kit.stores.sqlite.SqliteIdempotencyStore.begin_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:151](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L151).

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

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:279](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L279).

```python
replay = store.begin_sync("k", "fp", 86_400)
```

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:276](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L276).

```python
assert store.begin_sync("k", "fp", 86_400) is None
```

## jane_kit.stores.sqlite.SqliteIdempotencyStore.complete_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:206](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L206).

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

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:278](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L278).

```python
store.complete_sync("k", response)
```

## jane_kit.stores.sqlite.SqliteIdempotencyStore.release_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:226](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L226).

```python
def release_sync(self, key: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:282](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L282).

```python
store.release_sync("retry")
```

## jane_kit.stores.sqlite.SqliteIdempotencyStore.heartbeat_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:238](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L238).

```python
def heartbeat_sync(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

## jane_kit.stores.sqlite.SqliteIdempotencyStore.begin

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:253](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L253).

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

## jane_kit.stores.sqlite.SqliteIdempotencyStore.complete

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:260](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L260).

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

## jane_kit.stores.sqlite.SqliteIdempotencyStore.release

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:264](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L264).

```python
async def release(self, key: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.stores.sqlite.SqliteIdempotencyStore.heartbeat

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:268](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L268).

```python
async def heartbeat(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:209](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L209).

```python
assert await store.heartbeat() == 1
```

Контекст і передумови: [libs/jane-kit/tests/test_idempotency_claims.py:220](../../../../../../libs/jane-kit/tests/test_idempotency_claims.py#L220).

```python
assert await store.heartbeat() == 0
```

## jane_kit.stores.sqlite.SqliteJobStore

**Клас.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:309](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L309).

```python
class SqliteJobStore(_SqliteJobs):
```

Базові типи / інтерфейси: `_SqliteJobs`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitejobstore__init__) | Конструктор | ні |
| [owner](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitejobstoreowner) | Поле екземпляра | ні |
| [lease_s](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitejobstorelease_s) | Поле екземпляра | ні |
| [retention_s](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitejobstoreretention_s) | Поле екземпляра | ні |
| [migrate](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitejobstoremigrate) | Метод | ні |
| [create_sync](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitejobstorecreate_sync) | Метод | ні |
| [get_sync](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitejobstoreget_sync) | Метод | ні |
| [save_sync](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitejobstoresave_sync) | Метод | ні |
| [heartbeat_sync](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitejobstoreheartbeat_sync) | Метод | ні |
| [sweep_sync](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitejobstoresweep_sync) | Метод | ні |
| [heartbeat](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitejobstoreheartbeat) | Метод | ні |
| [sweep](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqlitejobstoresweep) | Метод | ні |

### Опис із вихідного коду

```text
jane-kit ``JobStore`` with its own ``owner``/``lease_until`` (epoch seconds), like the PostgreSQL store.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_stores_sqlite.py:117](../../../../../../libs/jane-kit/tests/test_stores_sqlite.py#L117).

```python
store = SqliteJobStore(db, owner=owner, lease_s=lease, retention_s=3600)
```

## jane_kit.stores.sqlite.SqliteJobStore.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:312](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L312).

```python
def __init__(self, db: SqliteTx, *, owner: str, lease_s: float, retention_s: float, table: str='jobs', doc_column: str='doc') -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `SqliteTx` | `—` | positional-or-keyword |
| `owner` | `str` | `—` | keyword-only |
| `lease_s` | `float` | `—` | keyword-only |
| `retention_s` | `float` | `—` | keyword-only |
| `table` | `str` | `'jobs'` | keyword-only |
| `doc_column` | `str` | `'doc'` | keyword-only |

Результат: `None`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_stores_sqlite.py:117](../../../../../../libs/jane-kit/tests/test_stores_sqlite.py#L117).

```python
store = SqliteJobStore(db, owner=owner, lease_s=lease, retention_s=3600)
```

## jane_kit.stores.sqlite.SqliteJobStore.owner

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:325](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L325).

```python
self.owner = owner
```

## jane_kit.stores.sqlite.SqliteJobStore.lease_s

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:326](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L326).

```python
self.lease_s = float(lease_s)
```

## jane_kit.stores.sqlite.SqliteJobStore.retention_s

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:327](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L327).

```python
self.retention_s = float(retention_s)
```

## jane_kit.stores.sqlite.SqliteJobStore.migrate

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:331](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L331).

```python
def migrate(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.stores.sqlite.SqliteJobStore.create_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:339](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L339).

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

## jane_kit.stores.sqlite.SqliteJobStore.get_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:366](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L366).

```python
def get_sync(self, job_id: str) -> Job | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job_id` | `str` | `—` | positional-or-keyword |

Результат: `Job | None`.

## jane_kit.stores.sqlite.SqliteJobStore.save_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:377](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L377).

```python
def save_sync(self, job: Job) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job` | `Job` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.stores.sqlite.SqliteJobStore.heartbeat_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:402](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L402).

```python
def heartbeat_sync(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

## jane_kit.stores.sqlite.SqliteJobStore.sweep_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:418](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L418).

```python
def sweep_sync(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

## jane_kit.stores.sqlite.SqliteJobStore.heartbeat

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:429](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L429).

```python
async def heartbeat(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

## jane_kit.stores.sqlite.SqliteJobStore.sweep

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:432](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L432).

```python
async def sweep(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

## jane_kit.stores.sqlite.WorkRows

**Клас.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:436](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L436).

```python
class WorkRows(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [work_row](jane_kit.stores.sqlite.md#jane_kitstoressqliteworkrowswork_row) | Метод | ні |
| [cancel_unstarted](jane_kit.stores.sqlite.md#jane_kitstoressqliteworkrowscancel_unstarted) | Метод | ні |

### Опис із вихідного коду

```text
The service's leased work rows (one per job, same id), read inside the job store's transaction.
```

## jane_kit.stores.sqlite.WorkRows.work_row

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:439](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L439).

```python
def work_row(self, db: sqlite3.Connection, job_id: str) -> tuple[str | None, str] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `sqlite3.Connection` | `—` | positional-or-keyword |
| `job_id` | `str` | `—` | positional-or-keyword |

Результат: `tuple[str | None, str] | None`.

### Опис із вихідного коду

```text
``(owner, status)`` of the work row, ``None`` if there is none.
```

## jane_kit.stores.sqlite.WorkRows.cancel_unstarted

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:443](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L443).

```python
def cancel_unstarted(self, db: sqlite3.Connection, job_id: str, owner: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `sqlite3.Connection` | `—` | positional-or-keyword |
| `job_id` | `str` | `—` | positional-or-keyword |
| `owner` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
End a work row that ``owner`` holds and that never started (``queued``) as ``cancelled``.
```

## jane_kit.stores.sqlite.SqliteWorkJobStore

**Клас.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:448](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L448).

```python
class SqliteWorkJobStore(_SqliteJobs):
```

Базові типи / інтерфейси: `_SqliteJobs`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteworkjobstore__init__) | Конструктор | ні |
| [work](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteworkjobstorework) | Поле екземпляра | ні |
| [owner](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteworkjobstoreowner) | Поле екземпляра | ні |
| [migrate](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteworkjobstoremigrate) | Метод | ні |
| [create_sync](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteworkjobstorecreate_sync) | Метод | ні |
| [save_sync](jane_kit.stores.sqlite.md#jane_kitstoressqlitesqliteworkjobstoresave_sync) | Метод | ні |

### Опис із вихідного коду

```text
jane-kit ``JobStore`` whose jobs mirror the service's leased work rows (see the module docstring).

No lease of its own: the work row's lease is renewed by the run and taken over by another instance, which
resumes the work and resubmits the job under the same ``job_id``.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_stores_sqlite.py:221](../../../../../../libs/jane-kit/tests/test_stores_sqlite.py#L221).

```python
store = SqliteWorkJobStore(db, work, owner=owner)
```

## jane_kit.stores.sqlite.SqliteWorkJobStore.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:455](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L455).

```python
def __init__(self, db: SqliteTx, work: WorkRows, *, owner: str, table: str='jobs', doc_column: str='body') -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `SqliteTx` | `—` | positional-or-keyword |
| `work` | `WorkRows` | `—` | positional-or-keyword |
| `owner` | `str` | `—` | keyword-only |
| `table` | `str` | `'jobs'` | keyword-only |
| `doc_column` | `str` | `'body'` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_stores_sqlite.py:221](../../../../../../libs/jane-kit/tests/test_stores_sqlite.py#L221).

```python
store = SqliteWorkJobStore(db, work, owner=owner)
```

## jane_kit.stores.sqlite.SqliteWorkJobStore.work

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:465](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L465).

```python
self.work = work
```

## jane_kit.stores.sqlite.SqliteWorkJobStore.owner

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:466](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L466).

```python
self.owner = owner
```

## jane_kit.stores.sqlite.SqliteWorkJobStore.migrate

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:468](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L468).

```python
def migrate(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_stores_sqlite.py:26](../../../../../../libs/jane-kit/tests/test_stores_sqlite.py#L26).

```python
store.migrate()
```

Контекст і передумови: [libs/jane-kit/tests/test_stores_sqlite.py:108](../../../../../../libs/jane-kit/tests/test_stores_sqlite.py#L108).

```python
store.migrate()
```

## jane_kit.stores.sqlite.SqliteWorkJobStore.create_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:481](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L481).

```python
def create_sync(self, job: Job) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job` | `Job` | `—` | positional-or-keyword |

Результат: `None`.

## jane_kit.stores.sqlite.SqliteWorkJobStore.save_sync

**Метод.** Код: [libs/jane-kit/src/jane_kit/stores/sqlite.py:522](../../../../../../libs/jane-kit/src/jane_kit/stores/sqlite.py#L522).

```python
def save_sync(self, job: Job) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job` | `Job` | `—` | positional-or-keyword |

Результат: `None`.
