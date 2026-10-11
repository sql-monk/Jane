# jane_telegram_collector.state

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_telegram_collector.state.SCHEMA_VERSION](#jane_telegram_collectorstateschema_version)
- [jane_telegram_collector.state.StateFileTooNew](#jane_telegram_collectorstatestatefiletoonew)
- [jane_telegram_collector.state.Fence](#jane_telegram_collectorstatefence)
- [jane_telegram_collector.state.LeaseLost](#jane_telegram_collectorstateleaselost)
- [jane_telegram_collector.state.StateStore](#jane_telegram_collectorstatestatestore)
- [jane_telegram_collector.state.StateStore.__init__](#jane_telegram_collectorstatestatestore__init__)
- [jane_telegram_collector.state.StateStore.path](#jane_telegram_collectorstatestatestorepath)
- [jane_telegram_collector.state.StateStore.schema_version](#jane_telegram_collectorstatestatestoreschema_version)
- [jane_telegram_collector.state.StateStore.close](#jane_telegram_collectorstatestatestoreclose)
- [jane_telegram_collector.state.StateStore.tx](#jane_telegram_collectorstatestatestoretx)
- [jane_telegram_collector.state.StateStore.ping](#jane_telegram_collectorstatestatestoreping)
- [jane_telegram_collector.state.StateStore.next_counter](#jane_telegram_collectorstatestatestorenext_counter)
- [jane_telegram_collector.state.StateStore.create_collection](#jane_telegram_collectorstatestatestorecreate_collection)
- [jane_telegram_collector.state.StateStore.get_collection](#jane_telegram_collectorstatestatestoreget_collection)
- [jane_telegram_collector.state.StateStore.get_status](#jane_telegram_collectorstatestatestoreget_status)
- [jane_telegram_collector.state.StateStore.set_running](#jane_telegram_collectorstatestatestoreset_running)
- [jane_telegram_collector.state.StateStore.finish](#jane_telegram_collectorstatestatestorefinish)
- [jane_telegram_collector.state.StateStore.finish_if_owner](#jane_telegram_collectorstatestatestorefinish_if_owner)
- [jane_telegram_collector.state.StateStore.set_paused](#jane_telegram_collectorstatestatestoreset_paused)
- [jane_telegram_collector.state.StateStore.save_stats](#jane_telegram_collectorstatestatestoresave_stats)
- [jane_telegram_collector.state.StateStore.lease](#jane_telegram_collectorstatestatestorelease)
- [jane_telegram_collector.state.StateStore.claim](#jane_telegram_collectorstatestatestoreclaim)
- [jane_telegram_collector.state.StateStore.release](#jane_telegram_collectorstatestatestorerelease)
- [jane_telegram_collector.state.StateStore.resumable](#jane_telegram_collectorstatestatestoreresumable)
- [jane_telegram_collector.state.StateStore.active_for_state_key](#jane_telegram_collectorstatestatestoreactive_for_state_key)
- [jane_telegram_collector.state.StateStore.expire_finished](#jane_telegram_collectorstatestatestoreexpire_finished)
- [jane_telegram_collector.state.StateStore.get_progress](#jane_telegram_collectorstatestatestoreget_progress)
- [jane_telegram_collector.state.StateStore.put_progress](#jane_telegram_collectorstatestatestoreput_progress)
- [jane_telegram_collector.state.StateStore.get_cursor](#jane_telegram_collectorstatestatestoreget_cursor)
- [jane_telegram_collector.state.StateStore.put_cursor](#jane_telegram_collectorstatestatestoreput_cursor)
- [jane_telegram_collector.state.StateStore.latest_seen](#jane_telegram_collectorstatestatestorelatest_seen)
- [jane_telegram_collector.state.StateStore.seen](#jane_telegram_collectorstatestatestoreseen)
- [jane_telegram_collector.state.StateStore.put_seen](#jane_telegram_collectorstatestatestoreput_seen)
- [jane_telegram_collector.state.StateStore.state_summary](#jane_telegram_collectorstatestatestorestate_summary)
- [jane_telegram_collector.state.StateStore.delete_state](#jane_telegram_collectorstatestatestoredelete_state)
- [jane_telegram_collector.state.StateStore.append_material](#jane_telegram_collectorstatestatestoreappend_material)
- [jane_telegram_collector.state.StateStore.materials_after](#jane_telegram_collectorstatestatestorematerials_after)
- [jane_telegram_collector.state.StateStore.ack](#jane_telegram_collectorstatestatestoreack)
- [jane_telegram_collector.state.StateStore.unacked_count](#jane_telegram_collectorstatestatestoreunacked_count)
- [jane_telegram_collector.state.StateStore.emitted_count](#jane_telegram_collectorstatestatestoreemitted_count)
- [jane_telegram_collector.state.StateStore.add_error](#jane_telegram_collectorstatestatestoreadd_error)
- [jane_telegram_collector.state.StateStore.errors_after](#jane_telegram_collectorstatestatestoreerrors_after)
- [jane_telegram_collector.state.StateStore.get_connection](#jane_telegram_collectorstatestatestoreget_connection)
- [jane_telegram_collector.state.StateStore.put_connection](#jane_telegram_collectorstatestatestoreput_connection)
- [jane_telegram_collector.state.StateStore.delete_connection](#jane_telegram_collectorstatestatestoredelete_connection)
- [jane_telegram_collector.state.StateStore.list_connections](#jane_telegram_collectorstatestatestorelist_connections)
- [jane_telegram_collector.state.StateStore.read](#jane_telegram_collectorstatestatestoreread)
- [jane_telegram_collector.state.StateStore.get_job](#jane_telegram_collectorstatestatestoreget_job)
- [jane_telegram_collector.state.StateStore.work_row](#jane_telegram_collectorstatestatestorework_row)
- [jane_telegram_collector.state.StateStore.cancel_unstarted](#jane_telegram_collectorstatestatestorecancel_unstarted)

## jane_telegram_collector.state.SCHEMA_VERSION

**Константа.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:28](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L28).

```python
SCHEMA_VERSION = 1
```

### Опис із вихідного коду

```text
``PRAGMA user_version`` of the state file - the format marker. 1 (WP-16, R04): ``tg_seen.sequence`` is in
``revision.sequence`` units (epoch seconds x ``SEQUENCE_SCALE`` + the revision number within the second); a
version 0 file (seconds, collectors before WP-16) is migrated when a process opens it. A file of a newer version
than the code knows is refused (:class:`StateFileTooNew`). Collectors before WP-16 do not read the marker: run
them on a migrated file and they take the stored sequences for seconds, so every known message looks newer than
its edits and no edit is emitted - instances sharing one ``STATE_DIR`` are upgraded together (README).
```

## jane_telegram_collector.state.StateFileTooNew

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:37](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L37).

```python
class StateFileTooNew(RuntimeError):
```

Базові типи / інтерфейси: `RuntimeError`.

### Опис із вихідного коду

```text
The state file was written by a newer collector (``PRAGMA user_version`` > :data:`SCHEMA_VERSION`).
```

## jane_telegram_collector.state.Fence

**Змінна.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:119](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L119).

```python
Fence = tuple[str, str]
```

### Опис із вихідного коду

```text
``(collection_id, owner)``: a transaction with a fence commits only while ``owner`` holds a valid lease.
```

## jane_telegram_collector.state.LeaseLost

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:123](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L123).

```python
class LeaseLost(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Опис із вихідного коду

```text
This instance no longer holds the lease of the collection (another instance took it over).
```

## jane_telegram_collector.state.StateStore

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:131](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L131).

```python
class StateStore:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestore__init__) | Конструктор | ні |
| [path](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestorepath) | Поле екземпляра | ні |
| [schema_version](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreschema_version) | Метод | ні |
| [close](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreclose) | Метод | ні |
| [tx](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoretx) | Метод | ні |
| [ping](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreping) | Метод | ні |
| [next_counter](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestorenext_counter) | Метод | ні |
| [create_collection](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestorecreate_collection) | Метод | ні |
| [get_collection](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreget_collection) | Метод | ні |
| [get_status](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreget_status) | Метод | ні |
| [set_running](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreset_running) | Метод | ні |
| [finish](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestorefinish) | Метод | ні |
| [finish_if_owner](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestorefinish_if_owner) | Метод | ні |
| [set_paused](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreset_paused) | Метод | ні |
| [save_stats](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoresave_stats) | Метод | ні |
| [lease](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestorelease) | Метод | ні |
| [claim](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreclaim) | Метод | ні |
| [release](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestorerelease) | Метод | ні |
| [resumable](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreresumable) | Метод | ні |
| [active_for_state_key](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreactive_for_state_key) | Метод | ні |
| [expire_finished](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreexpire_finished) | Метод | ні |
| [get_progress](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreget_progress) | Метод | ні |
| [put_progress](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreput_progress) | Метод | ні |
| [get_cursor](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreget_cursor) | Метод | ні |
| [put_cursor](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreput_cursor) | Метод | ні |
| [latest_seen](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestorelatest_seen) | Метод | ні |
| [seen](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreseen) | Метод | ні |
| [put_seen](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreput_seen) | Метод | ні |
| [state_summary](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestorestate_summary) | Метод | ні |
| [delete_state](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoredelete_state) | Метод | ні |
| [append_material](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreappend_material) | Метод | ні |
| [materials_after](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestorematerials_after) | Метод | ні |
| [ack](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreack) | Метод | ні |
| [unacked_count](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreunacked_count) | Метод | ні |
| [emitted_count](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreemitted_count) | Метод | ні |
| [add_error](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreadd_error) | Метод | ні |
| [errors_after](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreerrors_after) | Метод | ні |
| [get_connection](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreget_connection) | Метод | ні |
| [put_connection](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreput_connection) | Метод | ні |
| [delete_connection](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoredelete_connection) | Метод | ні |
| [list_connections](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestorelist_connections) | Метод | ні |
| [read](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreread) | Метод | ні |
| [get_job](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestoreget_job) | Метод | ні |
| [work_row](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestorework_row) | Метод | ні |
| [cancel_unstarted](jane_telegram_collector.state.md#jane_telegram_collectorstatestatestorecancel_unstarted) | Метод | ні |

## jane_telegram_collector.state.StateStore.__init__

**Конструктор.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:132](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L132).

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

Явні `raise` у тілі: `StateFileTooNew`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
``busy_timeout_ms``: how long a writer waits for another process holding the SQLite lock
(``JANE_TELEGRAM_COLLECTOR_STATE_BUSY_TIMEOUT_MS``, validated to stay below the lease).
```

## jane_telegram_collector.state.StateStore.path

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:136](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L136).

```python
self.path = path
```

## jane_telegram_collector.state.StateStore.schema_version

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:164](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L164).

```python
def schema_version(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

## jane_telegram_collector.state.StateStore.close

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:168](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L168).

```python
def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.state.StateStore.tx

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:173](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L173).

```python
def tx(self, fence: Fence | None=None) -> Iterator[sqlite3.Connection]:
```

Декоратори: `contextmanager`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `fence` | `Fence \| None` | `None` | positional-or-keyword |

Результат: `Iterator[sqlite3.Connection]`.

Явні `raise` у тілі: `LeaseLost`, `повторний raise`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
``BEGIN IMMEDIATE`` transaction. With ``fence`` it is rolled back and :class:`LeaseLost` raised
unless the owner still holds a valid lease.
```

## jane_telegram_collector.state.StateStore.ping

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:200](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L200).

```python
def ping(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.state.StateStore.next_counter

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:203](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L203).

```python
def next_counter(self, db: sqlite3.Connection, name: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `sqlite3.Connection` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |

Результат: `int`.

## jane_telegram_collector.state.StateStore.create_collection

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:212](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L212).

```python
def create_collection(self, collection_id: str, *, state_key: str, request: Mapping[str, Any], rules: Mapping[str, Any], rules_ref: Mapping[str, Any] | None, created_at: str, effective_limits: Mapping[str, Any], owner: str, lease_seconds: float) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `state_key` | `str` | `—` | keyword-only |
| `request` | `Mapping[str, Any]` | `—` | keyword-only |
| `rules` | `Mapping[str, Any]` | `—` | keyword-only |
| `rules_ref` | `Mapping[str, Any] \| None` | `—` | keyword-only |
| `created_at` | `str` | `—` | keyword-only |
| `effective_limits` | `Mapping[str, Any]` | `—` | keyword-only |
| `owner` | `str` | `—` | keyword-only |
| `lease_seconds` | `float` | `—` | keyword-only |

Результат: `bool`.

### Опис із вихідного коду

```text
Create a queued collection owned by ``owner``; False if ``state_key`` is used by an active one.
```

## jane_telegram_collector.state.StateStore.get_collection

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:250](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L250).

```python
def get_collection(self, collection_id: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

## jane_telegram_collector.state.StateStore.get_status

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:260](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L260).

```python
def get_status(self, collection_id: str) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |

Результат: `str | None`.

## jane_telegram_collector.state.StateStore.set_running

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:264](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L264).

```python
def set_running(self, db: sqlite3.Connection, collection_id: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `sqlite3.Connection` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.state.StateStore.finish

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:270](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L270).

```python
def finish(self, db: sqlite3.Connection, collection_id: str, status: str, finished_at: str, result: Any=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `sqlite3.Connection` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `status` | `str` | `—` | positional-or-keyword |
| `finished_at` | `str` | `—` | positional-or-keyword |
| `result` | `Any` | `None` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.state.StateStore.finish_if_owner

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:279](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L279).

```python
def finish_if_owner(self, collection_id: str, owner: str, status: str, finished_at: str, result: Any=None) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `owner` | `str` | `—` | positional-or-keyword |
| `status` | `str` | `—` | positional-or-keyword |
| `finished_at` | `str` | `—` | positional-or-keyword |
| `result` | `Any` | `None` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
Terminal status written only by the holder of a valid lease (fenced like every other run write).
```

## jane_telegram_collector.state.StateStore.set_paused

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:298](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L298).

```python
def set_paused(self, collection_id: str, paused: bool, fence: Fence) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `paused` | `bool` | `—` | positional-or-keyword |
| `fence` | `Fence` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Backpressure flag of a run: written only under the run's lease (:class:`LeaseLost` otherwise).
```

## jane_telegram_collector.state.StateStore.save_stats

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:305](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L305).

```python
def save_stats(self, db: sqlite3.Connection, collection_id: str, stats: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `sqlite3.Connection` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `stats` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.state.StateStore.lease

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:308](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L308).

```python
def lease(self, collection_id: str) -> tuple[str | None, float]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |

Результат: `tuple[str | None, float]`.

## jane_telegram_collector.state.StateStore.claim

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:314](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L314).

```python
def claim(self, collection_id: str, owner: str, lease_seconds: float) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `owner` | `str` | `—` | positional-or-keyword |
| `lease_seconds` | `float` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
Take (or renew) the lease of a non-terminal collection.
```

## jane_telegram_collector.state.StateStore.release

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:325](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L325).

```python
def release(self, collection_id: str, owner: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `owner` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.state.StateStore.resumable

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:332](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L332).

```python
def resumable(self, owner: str) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `owner` | `str` | `—` | positional-or-keyword |

Результат: `list[str]`.

### Опис із вихідного коду

```text
Non-terminal collections whose lease expired (or that this instance owned).
```

## jane_telegram_collector.state.StateStore.active_for_state_key

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:341](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L341).

```python
def active_for_state_key(self, state_key: str) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state_key` | `str` | `—` | positional-or-keyword |

Результат: `list[str]`.

## jane_telegram_collector.state.StateStore.expire_finished

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:348](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L348).

```python
def expire_finished(self, older_than_ts: float) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `older_than_ts` | `float` | `—` | positional-or-keyword |

Результат: `list[str]`.

### Опис із вихідного коду

```text
Drop buffers of collections finished before ``older_than_ts``; keep a tombstone (410).
```

## jane_telegram_collector.state.StateStore.get_progress

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:366](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L366).

```python
def get_progress(self, collection_id: str, channel_key: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `channel_key` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

## jane_telegram_collector.state.StateStore.put_progress

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:373](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L373).

```python
def put_progress(self, db: sqlite3.Connection, collection_id: str, channel_key: str, progress: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `sqlite3.Connection` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `channel_key` | `str` | `—` | positional-or-keyword |
| `progress` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.state.StateStore.get_cursor

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:383](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L383).

```python
def get_cursor(self, state_key: str, channel_id: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state_key` | `str` | `—` | positional-or-keyword |
| `channel_id` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

## jane_telegram_collector.state.StateStore.put_cursor

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:389](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L389).

```python
def put_cursor(self, db: sqlite3.Connection, state_key: str, channel_id: str, cursor: Mapping[str, Any], now: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `sqlite3.Connection` | `—` | positional-or-keyword |
| `state_key` | `str` | `—` | positional-or-keyword |
| `channel_id` | `str` | `—` | positional-or-keyword |
| `cursor` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `now` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.state.StateStore.latest_seen

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:398](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L398).

```python
def latest_seen(self, material_id: str) -> tuple[int, str] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `material_id` | `str` | `—` | positional-or-keyword |

Результат: `tuple[int, str] | None`.

### Опис із вихідного коду

```text
The newest revision of the message emitted under any ``state_key`` (``sequence``, text sha256).
```

## jane_telegram_collector.state.StateStore.seen

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:406](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L406).

```python
def seen(self, state_key: str, material_id: str) -> tuple[int, str] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state_key` | `str` | `—` | positional-or-keyword |
| `material_id` | `str` | `—` | positional-or-keyword |

Результат: `tuple[int, str] | None`.

## jane_telegram_collector.state.StateStore.put_seen

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:413](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L413).

```python
def put_seen(self, db: sqlite3.Connection, state_key: str, material_id: str, sequence: int, sha: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `sqlite3.Connection` | `—` | positional-or-keyword |
| `state_key` | `str` | `—` | positional-or-keyword |
| `material_id` | `str` | `—` | positional-or-keyword |
| `sequence` | `int` | `—` | positional-or-keyword |
| `sha` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.state.StateStore.state_summary

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:423](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L423).

```python
def state_summary(self, state_key: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state_key` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

## jane_telegram_collector.state.StateStore.delete_state

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:435](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L435).

```python
def delete_state(self, state_key: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state_key` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.state.StateStore.append_material

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:441](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L441).

```python
def append_material(self, db: sqlite3.Connection, collection_id: str, observation_id: str, material: Mapping[str, Any]) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `sqlite3.Connection` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `observation_id` | `str` | `—` | positional-or-keyword |
| `material` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `int`.

## jane_telegram_collector.state.StateStore.materials_after

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:451](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L451).

```python
def materials_after(self, collection_id: str, after_seq: int, limit: int) -> list[tuple[int, dict[str, Any]]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `after_seq` | `int` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `list[tuple[int, dict[str, Any]]]`.

## jane_telegram_collector.state.StateStore.ack

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:460](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L460).

```python
def ack(self, collection_id: str, upto_seq: int) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `upto_seq` | `int` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Acknowledge every material with ``seq <= upto_seq``; returns how many were newly acknowledged.
```

## jane_telegram_collector.state.StateStore.unacked_count

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:472](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L472).

```python
def unacked_count(self, collection_id: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |

Результат: `int`.

## jane_telegram_collector.state.StateStore.emitted_count

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:476](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L476).

```python
def emitted_count(self, collection_id: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |

Результат: `int`.

## jane_telegram_collector.state.StateStore.add_error

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:481](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L481).

```python
def add_error(self, db: sqlite3.Connection, collection_id: str, error: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `sqlite3.Connection` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `error` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.state.StateStore.errors_after

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:488](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L488).

```python
def errors_after(self, collection_id: str, after_seq: int, limit: int) -> list[tuple[int, dict[str, Any]]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `after_seq` | `int` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `list[tuple[int, dict[str, Any]]]`.

## jane_telegram_collector.state.StateStore.get_connection

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:498](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L498).

```python
def get_connection(self, connection_id: str) -> tuple[dict[str, Any], str] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |

Результат: `tuple[dict[str, Any], str] | None`.

## jane_telegram_collector.state.StateStore.put_connection

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:502](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L502).

```python
def put_connection(self, connection_id: str, body: Mapping[str, Any], etag: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |
| `body` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `etag` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
Returns True if created.
```

## jane_telegram_collector.state.StateStore.delete_connection

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:515](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L515).

```python
def delete_connection(self, connection_id: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_telegram_collector.state.StateStore.list_connections

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:521](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L521).

```python
def list_connections(self, after: str | None, limit: int) -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `after` | `str \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `list[dict[str, Any]]`.

## jane_telegram_collector.state.StateStore.read

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:530](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L530).

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
The connection for single-statement reads (no write lock; ``jane_kit.stores.sqlite``).
```

## jane_telegram_collector.state.StateStore.get_job

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:535](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L535).

```python
def get_job(self, job_id: str) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job_id` | `str` | `—` | positional-or-keyword |

Результат: `str | None`.

## jane_telegram_collector.state.StateStore.work_row

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:539](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L539).

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
``(owner, status)`` of the collection of a job (``jane_kit.stores.sqlite.WorkRows``).
```

## jane_telegram_collector.state.StateStore.cancel_unstarted

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/state.py:546](../../../../../../services/telegram-collector/src/jane_telegram_collector/state.py#L546).

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
A collection cancelled before its run started ends ``cancelled`` (only its lease holder).
```
