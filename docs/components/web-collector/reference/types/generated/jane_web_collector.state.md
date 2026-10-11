# jane_web_collector.state

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.state.LeaseLost](#jane_web_collectorstateleaselost)
- [jane_web_collector.state.FrontierRow](#jane_web_collectorstatefrontierrow)
- [jane_web_collector.state.FrontierRow.__init__](#jane_web_collectorstatefrontierrow__init__)
- [jane_web_collector.state.FrontierRow.url](#jane_web_collectorstatefrontierrowurl)
- [jane_web_collector.state.FrontierRow.priority](#jane_web_collectorstatefrontierrowpriority)
- [jane_web_collector.state.FrontierRow.depth](#jane_web_collectorstatefrontierrowdepth)
- [jane_web_collector.state.FrontierRow.kind](#jane_web_collectorstatefrontierrowkind)
- [jane_web_collector.state.FrontierRow.strategy_id](#jane_web_collectorstatefrontierrowstrategy_id)
- [jane_web_collector.state.FrontierRow.parent_url](#jane_web_collectorstatefrontierrowparent_url)
- [jane_web_collector.state.FrontierRow.section](#jane_web_collectorstatefrontierrowsection)
- [jane_web_collector.state.FrontierRow.lastmod](#jane_web_collectorstatefrontierrowlastmod)
- [jane_web_collector.state.StateStore](#jane_web_collectorstatestatestore)
- [jane_web_collector.state.StateStore.__init__](#jane_web_collectorstatestatestore__init__)
- [jane_web_collector.state.StateStore.path](#jane_web_collectorstatestatestorepath)
- [jane_web_collector.state.StateStore.close](#jane_web_collectorstatestatestoreclose)
- [jane_web_collector.state.StateStore.tx](#jane_web_collectorstatestatestoretx)
- [jane_web_collector.state.StateStore.ping](#jane_web_collectorstatestatestoreping)
- [jane_web_collector.state.StateStore.next_counter](#jane_web_collectorstatestatestorenext_counter)
- [jane_web_collector.state.StateStore.create_collection](#jane_web_collectorstatestatestorecreate_collection)
- [jane_web_collector.state.StateStore.get_collection](#jane_web_collectorstatestatestoreget_collection)
- [jane_web_collector.state.StateStore.set_status](#jane_web_collectorstatestatestoreset_status)
- [jane_web_collector.state.StateStore.get_status](#jane_web_collectorstatestatestoreget_status)
- [jane_web_collector.state.StateStore.set_meta](#jane_web_collectorstatestatestoreset_meta)
- [jane_web_collector.state.StateStore.set_paused](#jane_web_collectorstatestatestoreset_paused)
- [jane_web_collector.state.StateStore.save_stats](#jane_web_collectorstatestatestoresave_stats)
- [jane_web_collector.state.StateStore.lease](#jane_web_collectorstatestatestorelease)
- [jane_web_collector.state.StateStore.set_status_if_owner](#jane_web_collectorstatestatestoreset_status_if_owner)
- [jane_web_collector.state.StateStore.claim](#jane_web_collectorstatestatestoreclaim)
- [jane_web_collector.state.StateStore.release](#jane_web_collectorstatestatestorerelease)
- [jane_web_collector.state.StateStore.resumable](#jane_web_collectorstatestatestoreresumable)
- [jane_web_collector.state.StateStore.active_for_state_key](#jane_web_collectorstatestatestoreactive_for_state_key)
- [jane_web_collector.state.StateStore.expire_finished](#jane_web_collectorstatestatestoreexpire_finished)
- [jane_web_collector.state.StateStore.add_urls](#jane_web_collectorstatestatestoreadd_urls)
- [jane_web_collector.state.StateStore.frontier_row](#jane_web_collectorstatestatestorefrontier_row)
- [jane_web_collector.state.StateStore.known](#jane_web_collectorstatestatestoreknown)
- [jane_web_collector.state.StateStore.take_pending](#jane_web_collectorstatestatestoretake_pending)
- [jane_web_collector.state.StateStore.mark_url](#jane_web_collectorstatestatestoremark_url)
- [jane_web_collector.state.StateStore.reset_inflight](#jane_web_collectorstatestatestorereset_inflight)
- [jane_web_collector.state.StateStore.frontier_counts](#jane_web_collectorstatestatestorefrontier_counts)
- [jane_web_collector.state.StateStore.drop_pending](#jane_web_collectorstatestatestoredrop_pending)
- [jane_web_collector.state.StateStore.frontier_size_for_state_key](#jane_web_collectorstatestatestorefrontier_size_for_state_key)
- [jane_web_collector.state.StateStore.save_strategy_states](#jane_web_collectorstatestatestoresave_strategy_states)
- [jane_web_collector.state.StateStore.load_strategy_states](#jane_web_collectorstatestatestoreload_strategy_states)
- [jane_web_collector.state.StateStore.save_cursors](#jane_web_collectorstatestatestoresave_cursors)
- [jane_web_collector.state.StateStore.append_material](#jane_web_collectorstatestatestoreappend_material)
- [jane_web_collector.state.StateStore.materials_after](#jane_web_collectorstatestatestorematerials_after)
- [jane_web_collector.state.StateStore.ack](#jane_web_collectorstatestatestoreack)
- [jane_web_collector.state.StateStore.unacked_count](#jane_web_collectorstatestatestoreunacked_count)
- [jane_web_collector.state.StateStore.emitted_count](#jane_web_collectorstatestatestoreemitted_count)
- [jane_web_collector.state.StateStore.add_error](#jane_web_collectorstatestatestoreadd_error)
- [jane_web_collector.state.StateStore.errors_after](#jane_web_collectorstatestatestoreerrors_after)
- [jane_web_collector.state.StateStore.url_state](#jane_web_collectorstatestatestoreurl_state)
- [jane_web_collector.state.StateStore.put_url_state](#jane_web_collectorstatestatestoreput_url_state)
- [jane_web_collector.state.StateStore.state_summary](#jane_web_collectorstatestatestorestate_summary)
- [jane_web_collector.state.StateStore.delete_state](#jane_web_collectorstatestatestoredelete_state)
- [jane_web_collector.state.StateStore.get_connection](#jane_web_collectorstatestatestoreget_connection)
- [jane_web_collector.state.StateStore.put_connection](#jane_web_collectorstatestatestoreput_connection)
- [jane_web_collector.state.StateStore.delete_connection](#jane_web_collectorstatestatestoredelete_connection)
- [jane_web_collector.state.StateStore.list_connections](#jane_web_collectorstatestatestorelist_connections)
- [jane_web_collector.state.StateStore.read](#jane_web_collectorstatestatestoreread)
- [jane_web_collector.state.StateStore.get_job](#jane_web_collectorstatestatestoreget_job)
- [jane_web_collector.state.StateStore.work_row](#jane_web_collectorstatestatestorework_row)
- [jane_web_collector.state.StateStore.cancel_unstarted](#jane_web_collectorstatestatestorecancel_unstarted)
- [jane_web_collector.state.StateStore.host_take_slot](#jane_web_collectorstatestatestorehost_take_slot)
- [jane_web_collector.state.StateStore.host_renew](#jane_web_collectorstatestatestorehost_renew)
- [jane_web_collector.state.StateStore.host_release_slot](#jane_web_collectorstatestatestorehost_release_slot)
- [jane_web_collector.state.StateStore.host_push_back](#jane_web_collectorstatestatestorehost_push_back)
- [jane_web_collector.state.StateStore.host_leave](#jane_web_collectorstatestatestorehost_leave)
- [jane_web_collector.state.StateStore.host_rows](#jane_web_collectorstatestatestorehost_rows)
- [jane_web_collector.state.StateStore.host_prune](#jane_web_collectorstatestatestorehost_prune)

## jane_web_collector.state.LeaseLost

**Клас.** Код: [services/web-collector/src/jane_web_collector/state.py:155](../../../../../../services/web-collector/src/jane_web_collector/state.py#L155).

```python
class LeaseLost(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Опис із вихідного коду

```text
This instance no longer holds the lease of the collection (another instance took it over).
```

## jane_web_collector.state.FrontierRow

**Клас.** Код: [services/web-collector/src/jane_web_collector/state.py:160](../../../../../../services/web-collector/src/jane_web_collector/state.py#L160).

```python
class FrontierRow:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [url](jane_web_collector.state.md#jane_web_collectorstatefrontierrowurl) | Поле | ні |
| [priority](jane_web_collector.state.md#jane_web_collectorstatefrontierrowpriority) | Поле | ні |
| [depth](jane_web_collector.state.md#jane_web_collectorstatefrontierrowdepth) | Поле | ні |
| [kind](jane_web_collector.state.md#jane_web_collectorstatefrontierrowkind) | Поле | ні |
| [strategy_id](jane_web_collector.state.md#jane_web_collectorstatefrontierrowstrategy_id) | Поле | ні |
| [parent_url](jane_web_collector.state.md#jane_web_collectorstatefrontierrowparent_url) | Поле | ні |
| [section](jane_web_collector.state.md#jane_web_collectorstatefrontierrowsection) | Поле | ні |
| [lastmod](jane_web_collector.state.md#jane_web_collectorstatefrontierrowlastmod) | Поле | ні |
| [__init__](jane_web_collector.state.md#jane_web_collectorstatefrontierrow__init__) | Конструктор dataclass | ні |

## jane_web_collector.state.FrontierRow.__init__

**Конструктор dataclass.** Код: [services/web-collector/src/jane_web_collector/state.py:160](../../../../../../services/web-collector/src/jane_web_collector/state.py#L160).

```python
def __init__(self, url: str, priority: int, depth: int, kind: str, strategy_id: str | None, parent_url: str | None = None, section: str | None = None, lastmod: str | None = None) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `url` | `str` | `—` | positional-or-keyword |
| `priority` | `int` | `—` | positional-or-keyword |
| `depth` | `int` | `—` | positional-or-keyword |
| `kind` | `str` | `—` | positional-or-keyword |
| `strategy_id` | `str \| None` | `—` | positional-or-keyword |
| `parent_url` | `str \| None` | `None` | positional-or-keyword |
| `section` | `str \| None` | `None` | positional-or-keyword |
| `lastmod` | `str \| None` | `None` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.state.FrontierRow.url

**Поле.** Код: [services/web-collector/src/jane_web_collector/state.py:161](../../../../../../services/web-collector/src/jane_web_collector/state.py#L161).

```python
url: str
```

Доступ: читання — так; запис — ні.

## jane_web_collector.state.FrontierRow.priority

**Поле.** Код: [services/web-collector/src/jane_web_collector/state.py:162](../../../../../../services/web-collector/src/jane_web_collector/state.py#L162).

```python
priority: int
```

Доступ: читання — так; запис — ні.

## jane_web_collector.state.FrontierRow.depth

**Поле.** Код: [services/web-collector/src/jane_web_collector/state.py:163](../../../../../../services/web-collector/src/jane_web_collector/state.py#L163).

```python
depth: int
```

Доступ: читання — так; запис — ні.

## jane_web_collector.state.FrontierRow.kind

**Поле.** Код: [services/web-collector/src/jane_web_collector/state.py:164](../../../../../../services/web-collector/src/jane_web_collector/state.py#L164).

```python
kind: str
```

Доступ: читання — так; запис — ні.

## jane_web_collector.state.FrontierRow.strategy_id

**Поле.** Код: [services/web-collector/src/jane_web_collector/state.py:165](../../../../../../services/web-collector/src/jane_web_collector/state.py#L165).

```python
strategy_id: str | None
```

Доступ: читання — так; запис — ні.

## jane_web_collector.state.FrontierRow.parent_url

**Поле.** Код: [services/web-collector/src/jane_web_collector/state.py:166](../../../../../../services/web-collector/src/jane_web_collector/state.py#L166).

```python
parent_url: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_web_collector.state.FrontierRow.section

**Поле.** Код: [services/web-collector/src/jane_web_collector/state.py:167](../../../../../../services/web-collector/src/jane_web_collector/state.py#L167).

```python
section: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_web_collector.state.FrontierRow.lastmod

**Поле.** Код: [services/web-collector/src/jane_web_collector/state.py:168](../../../../../../services/web-collector/src/jane_web_collector/state.py#L168).

```python
lastmod: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_web_collector.state.StateStore

**Клас.** Код: [services/web-collector/src/jane_web_collector/state.py:175](../../../../../../services/web-collector/src/jane_web_collector/state.py#L175).

```python
class StateStore:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.state.md#jane_web_collectorstatestatestore__init__) | Конструктор | ні |
| [path](jane_web_collector.state.md#jane_web_collectorstatestatestorepath) | Поле екземпляра | ні |
| [close](jane_web_collector.state.md#jane_web_collectorstatestatestoreclose) | Метод | ні |
| [tx](jane_web_collector.state.md#jane_web_collectorstatestatestoretx) | Метод | ні |
| [ping](jane_web_collector.state.md#jane_web_collectorstatestatestoreping) | Метод | ні |
| [next_counter](jane_web_collector.state.md#jane_web_collectorstatestatestorenext_counter) | Метод | ні |
| [create_collection](jane_web_collector.state.md#jane_web_collectorstatestatestorecreate_collection) | Метод | ні |
| [get_collection](jane_web_collector.state.md#jane_web_collectorstatestatestoreget_collection) | Метод | ні |
| [set_status](jane_web_collector.state.md#jane_web_collectorstatestatestoreset_status) | Метод | ні |
| [get_status](jane_web_collector.state.md#jane_web_collectorstatestatestoreget_status) | Метод | ні |
| [set_meta](jane_web_collector.state.md#jane_web_collectorstatestatestoreset_meta) | Метод | ні |
| [set_paused](jane_web_collector.state.md#jane_web_collectorstatestatestoreset_paused) | Метод | ні |
| [save_stats](jane_web_collector.state.md#jane_web_collectorstatestatestoresave_stats) | Метод | ні |
| [lease](jane_web_collector.state.md#jane_web_collectorstatestatestorelease) | Метод | ні |
| [set_status_if_owner](jane_web_collector.state.md#jane_web_collectorstatestatestoreset_status_if_owner) | Метод | ні |
| [claim](jane_web_collector.state.md#jane_web_collectorstatestatestoreclaim) | Метод | ні |
| [release](jane_web_collector.state.md#jane_web_collectorstatestatestorerelease) | Метод | ні |
| [resumable](jane_web_collector.state.md#jane_web_collectorstatestatestoreresumable) | Метод | ні |
| [active_for_state_key](jane_web_collector.state.md#jane_web_collectorstatestatestoreactive_for_state_key) | Метод | ні |
| [expire_finished](jane_web_collector.state.md#jane_web_collectorstatestatestoreexpire_finished) | Метод | ні |
| [add_urls](jane_web_collector.state.md#jane_web_collectorstatestatestoreadd_urls) | Метод | ні |
| [frontier_row](jane_web_collector.state.md#jane_web_collectorstatestatestorefrontier_row) | Метод | ні |
| [known](jane_web_collector.state.md#jane_web_collectorstatestatestoreknown) | Метод | ні |
| [take_pending](jane_web_collector.state.md#jane_web_collectorstatestatestoretake_pending) | Метод | ні |
| [mark_url](jane_web_collector.state.md#jane_web_collectorstatestatestoremark_url) | Метод | ні |
| [reset_inflight](jane_web_collector.state.md#jane_web_collectorstatestatestorereset_inflight) | Метод | ні |
| [frontier_counts](jane_web_collector.state.md#jane_web_collectorstatestatestorefrontier_counts) | Метод | ні |
| [drop_pending](jane_web_collector.state.md#jane_web_collectorstatestatestoredrop_pending) | Метод | ні |
| [frontier_size_for_state_key](jane_web_collector.state.md#jane_web_collectorstatestatestorefrontier_size_for_state_key) | Метод | ні |
| [save_strategy_states](jane_web_collector.state.md#jane_web_collectorstatestatestoresave_strategy_states) | Метод | ні |
| [load_strategy_states](jane_web_collector.state.md#jane_web_collectorstatestatestoreload_strategy_states) | Метод | ні |
| [save_cursors](jane_web_collector.state.md#jane_web_collectorstatestatestoresave_cursors) | Метод | ні |
| [append_material](jane_web_collector.state.md#jane_web_collectorstatestatestoreappend_material) | Метод | ні |
| [materials_after](jane_web_collector.state.md#jane_web_collectorstatestatestorematerials_after) | Метод | ні |
| [ack](jane_web_collector.state.md#jane_web_collectorstatestatestoreack) | Метод | ні |
| [unacked_count](jane_web_collector.state.md#jane_web_collectorstatestatestoreunacked_count) | Метод | ні |
| [emitted_count](jane_web_collector.state.md#jane_web_collectorstatestatestoreemitted_count) | Метод | ні |
| [add_error](jane_web_collector.state.md#jane_web_collectorstatestatestoreadd_error) | Метод | ні |
| [errors_after](jane_web_collector.state.md#jane_web_collectorstatestatestoreerrors_after) | Метод | ні |
| [url_state](jane_web_collector.state.md#jane_web_collectorstatestatestoreurl_state) | Метод | ні |
| [put_url_state](jane_web_collector.state.md#jane_web_collectorstatestatestoreput_url_state) | Метод | ні |
| [state_summary](jane_web_collector.state.md#jane_web_collectorstatestatestorestate_summary) | Метод | ні |
| [delete_state](jane_web_collector.state.md#jane_web_collectorstatestatestoredelete_state) | Метод | ні |
| [get_connection](jane_web_collector.state.md#jane_web_collectorstatestatestoreget_connection) | Метод | ні |
| [put_connection](jane_web_collector.state.md#jane_web_collectorstatestatestoreput_connection) | Метод | ні |
| [delete_connection](jane_web_collector.state.md#jane_web_collectorstatestatestoredelete_connection) | Метод | ні |
| [list_connections](jane_web_collector.state.md#jane_web_collectorstatestatestorelist_connections) | Метод | ні |
| [read](jane_web_collector.state.md#jane_web_collectorstatestatestoreread) | Метод | ні |
| [get_job](jane_web_collector.state.md#jane_web_collectorstatestatestoreget_job) | Метод | ні |
| [work_row](jane_web_collector.state.md#jane_web_collectorstatestatestorework_row) | Метод | ні |
| [cancel_unstarted](jane_web_collector.state.md#jane_web_collectorstatestatestorecancel_unstarted) | Метод | ні |
| [host_take_slot](jane_web_collector.state.md#jane_web_collectorstatestatestorehost_take_slot) | Метод | ні |
| [host_renew](jane_web_collector.state.md#jane_web_collectorstatestatestorehost_renew) | Метод | ні |
| [host_release_slot](jane_web_collector.state.md#jane_web_collectorstatestatestorehost_release_slot) | Метод | ні |
| [host_push_back](jane_web_collector.state.md#jane_web_collectorstatestatestorehost_push_back) | Метод | ні |
| [host_leave](jane_web_collector.state.md#jane_web_collectorstatestatestorehost_leave) | Метод | ні |
| [host_rows](jane_web_collector.state.md#jane_web_collectorstatestatestorehost_rows) | Метод | ні |
| [host_prune](jane_web_collector.state.md#jane_web_collectorstatestatestorehost_prune) | Метод | ні |

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_backpressure_fencing.py:26](../../../../../../services/web-collector/tests/test_backpressure_fencing.py#L26).

```python
state = StateStore(tmp_path / "state.db")
```

Контекст і передумови: [services/web-collector/tests/test_review2.py:38](../../../../../../services/web-collector/tests/test_review2.py#L38).

```python
state = StateStore(tmp_path / "state.db")
```

## jane_web_collector.state.StateStore.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/state.py:176](../../../../../../services/web-collector/src/jane_web_collector/state.py#L176).

```python
def __init__(self, path: Path, *, busy_timeout_ms: int=10000) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `path` | `Path` | `—` | positional-or-keyword |
| `busy_timeout_ms` | `int` | `10000` | keyword-only |

Результат: `None`.

### Опис із вихідного коду

```text
``busy_timeout_ms``: how long a writer waits for another process holding the SQLite lock
(configuration: ``JANE_WEB_COLLECTOR_STATE_BUSY_TIMEOUT_MS``, must stay below the lease).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_backpressure_fencing.py:26](../../../../../../services/web-collector/tests/test_backpressure_fencing.py#L26).

```python
state = StateStore(tmp_path / "state.db")
```

Контекст і передумови: [services/web-collector/tests/test_review2.py:38](../../../../../../services/web-collector/tests/test_review2.py#L38).

```python
state = StateStore(tmp_path / "state.db")
```

## jane_web_collector.state.StateStore.path

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/state.py:180](../../../../../../services/web-collector/src/jane_web_collector/state.py#L180).

```python
self.path = path
```

## jane_web_collector.state.StateStore.close

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:190](../../../../../../services/web-collector/src/jane_web_collector/state.py#L190).

```python
def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_backpressure_fencing.py:96](../../../../../../services/web-collector/tests/test_backpressure_fencing.py#L96).

```python
state.close()
```

Контекст і передумови: [services/web-collector/tests/test_review2.py:62](../../../../../../services/web-collector/tests/test_review2.py#L62).

```python
state.close()
```

## jane_web_collector.state.StateStore.tx

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:195](../../../../../../services/web-collector/src/jane_web_collector/state.py#L195).

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
``BEGIN IMMEDIATE`` transaction. With ``fence`` the transaction is rolled back and
:class:`LeaseLost` raised unless the owner still holds a valid lease (fencing of a run that
another instance has taken over).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_backpressure_fencing.py:38](../../../../../../services/web-collector/tests/test_backpressure_fencing.py#L38).

```python
state.tx()
```

## jane_web_collector.state.StateStore.ping

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:223](../../../../../../services/web-collector/src/jane_web_collector/state.py#L223).

```python
def ping(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.state.StateStore.next_counter

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:227](../../../../../../services/web-collector/src/jane_web_collector/state.py#L227).

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

## jane_web_collector.state.StateStore.create_collection

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:237](../../../../../../services/web-collector/src/jane_web_collector/state.py#L237).

```python
def create_collection(self, collection_id: str, *, state_key: str, status: str, request: Mapping[str, Any], rules: Mapping[str, Any], rules_ref: Mapping[str, Any] | None, created_at: str, effective_limits: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `state_key` | `str` | `—` | keyword-only |
| `status` | `str` | `—` | keyword-only |
| `request` | `Mapping[str, Any]` | `—` | keyword-only |
| `rules` | `Mapping[str, Any]` | `—` | keyword-only |
| `rules_ref` | `Mapping[str, Any] \| None` | `—` | keyword-only |
| `created_at` | `str` | `—` | keyword-only |
| `effective_limits` | `Mapping[str, Any]` | `—` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_backpressure_fencing.py:28](../../../../../../services/web-collector/tests/test_backpressure_fencing.py#L28).

```python
state.create_collection(
        collection_id,
        state_key=collection_id,
        status="running",
        request={},
        rules={},
        rules_ref=None,
        created_at="2026-09-30T00:00:00Z",
        effective_limits={},
    )
```

Контекст і передумови: [services/web-collector/tests/test_review2.py:18](../../../../../../services/web-collector/tests/test_review2.py#L18).

```python
state.create_collection(
        cid,
        state_key=cid,
        status="running",
        request={},
        rules={},
        rules_ref=None,
        created_at="2026-09-27T00:00:00Z",
        effective_limits={},
    )
```

## jane_web_collector.state.StateStore.get_collection

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:265](../../../../../../services/web-collector/src/jane_web_collector/state.py#L265).

```python
def get_collection(self, collection_id: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_backpressure_fencing.py:17](../../../../../../services/web-collector/tests/test_backpressure_fencing.py#L17).

```python
record = state.get_collection(collection_id)
```

Контекст і передумови: [services/web-collector/tests/test_backpressure_fencing.py:74](../../../../../../services/web-collector/tests/test_backpressure_fencing.py#L74).

```python
record = state.get_collection(collection_id)
```

## jane_web_collector.state.StateStore.set_status

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:275](../../../../../../services/web-collector/src/jane_web_collector/state.py#L275).

```python
def set_status(self, collection_id: str, status: str, *, finished_at: str | None=None, db: sqlite3.Connection | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `status` | `str` | `—` | positional-or-keyword |
| `finished_at` | `str \| None` | `None` | keyword-only |
| `db` | `sqlite3.Connection \| None` | `None` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_review2.py:51](../../../../../../services/web-collector/tests/test_review2.py#L51).

```python
state.set_status("job_x", "succeeded", finished_at="2026-09-27T00:01:00Z")
```

Контекст і передумови: [services/web-collector/tests/test_review2.py:77](../../../../../../services/web-collector/tests/test_review2.py#L77).

```python
state.set_status(cid, "running")
```

## jane_web_collector.state.StateStore.get_status

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:291](../../../../../../services/web-collector/src/jane_web_collector/state.py#L291).

```python
def get_status(self, collection_id: str) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |

Результат: `str | None`.

## jane_web_collector.state.StateStore.set_meta

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:295](../../../../../../services/web-collector/src/jane_web_collector/state.py#L295).

```python
def set_meta(self, collection_id: str, meta: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `meta` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.state.StateStore.set_paused

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:301](../../../../../../services/web-collector/src/jane_web_collector/state.py#L301).

```python
def set_paused(self, collection_id: str, paused: bool, *, fence: Fence) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `paused` | `bool` | `—` | positional-or-keyword |
| `fence` | `Fence` | `—` | keyword-only |

Результат: `None`.

### Опис із вихідного коду

```text
Only the current lease holder may change a run's backpressure state.
```

## jane_web_collector.state.StateStore.save_stats

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:308](../../../../../../services/web-collector/src/jane_web_collector/state.py#L308).

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

## jane_web_collector.state.StateStore.lease

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:311](../../../../../../services/web-collector/src/jane_web_collector/state.py#L311).

```python
def lease(self, collection_id: str) -> tuple[str | None, float]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |

Результат: `tuple[str | None, float]`.

## jane_web_collector.state.StateStore.set_status_if_owner

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:317](../../../../../../services/web-collector/src/jane_web_collector/state.py#L317).

```python
def set_status_if_owner(self, collection_id: str, owner: str, status: str, *, finished_at: str | None) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `owner` | `str` | `—` | positional-or-keyword |
| `status` | `str` | `—` | positional-or-keyword |
| `finished_at` | `str \| None` | `—` | keyword-only |

Результат: `bool`.

### Опис із вихідного коду

```text
Terminal status written only by the lease holder (a run that lost its lease must not overwrite it).
```

## jane_web_collector.state.StateStore.claim

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:329](../../../../../../services/web-collector/src/jane_web_collector/state.py#L329).

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

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_backpressure_fencing.py:59](../../../../../../services/web-collector/tests/test_backpressure_fencing.py#L59).

```python
assert state.claim(collection_id, "owner-a", 10)
```

Контекст і передумови: [services/web-collector/tests/test_backpressure_fencing.py:66](../../../../../../services/web-collector/tests/test_backpressure_fencing.py#L66).

```python
assert state.claim(collection_id, "owner-b", 10)
```

## jane_web_collector.state.StateStore.release

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:340](../../../../../../services/web-collector/src/jane_web_collector/state.py#L340).

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

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_backpressure_fencing.py:65](../../../../../../services/web-collector/tests/test_backpressure_fencing.py#L65).

```python
state.release(collection_id, "owner-a")
```

## jane_web_collector.state.StateStore.resumable

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:347](../../../../../../services/web-collector/src/jane_web_collector/state.py#L347).

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

## jane_web_collector.state.StateStore.active_for_state_key

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:357](../../../../../../services/web-collector/src/jane_web_collector/state.py#L357).

```python
def active_for_state_key(self, state_key: str) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state_key` | `str` | `—` | positional-or-keyword |

Результат: `list[str]`.

## jane_web_collector.state.StateStore.expire_finished

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:364](../../../../../../services/web-collector/src/jane_web_collector/state.py#L364).

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
Drop buffers and frontier of collections finished before ``older_than_ts``; keep a tombstone (410).
```

## jane_web_collector.state.StateStore.add_urls

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:382](../../../../../../services/web-collector/src/jane_web_collector/state.py#L382).

```python
def add_urls(self, db: sqlite3.Connection, collection_id: str, rows: Iterable[FrontierRow], status: str='pending') -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `sqlite3.Connection` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `rows` | `Iterable[FrontierRow]` | `—` | positional-or-keyword |
| `status` | `str` | `'pending'` | positional-or-keyword |

Результат: `int`.

## jane_web_collector.state.StateStore.frontier_row

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:408](../../../../../../services/web-collector/src/jane_web_collector/state.py#L408).

```python
def frontier_row(self, collection_id: str, url: str) -> sqlite3.Row | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `sqlite3.Row | None`.

## jane_web_collector.state.StateStore.known

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:411](../../../../../../services/web-collector/src/jane_web_collector/state.py#L411).

```python
def known(self, collection_id: str, url: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_web_collector.state.StateStore.take_pending

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:417](../../../../../../services/web-collector/src/jane_web_collector/state.py#L417).

```python
def take_pending(self, collection_id: str, limit: int, fence: Fence | None=None) -> list[FrontierRow]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |
| `fence` | `Fence \| None` | `None` | positional-or-keyword |

Результат: `list[FrontierRow]`.

## jane_web_collector.state.StateStore.mark_url

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:443](../../../../../../services/web-collector/src/jane_web_collector/state.py#L443).

```python
def mark_url(self, db: sqlite3.Connection, collection_id: str, url: str, status: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `sqlite3.Connection` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |
| `status` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.state.StateStore.reset_inflight

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:448](../../../../../../services/web-collector/src/jane_web_collector/state.py#L448).

```python
def reset_inflight(self, collection_id: str, fence: Fence | None=None) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `fence` | `Fence \| None` | `None` | positional-or-keyword |

Результат: `int`.

## jane_web_collector.state.StateStore.frontier_counts

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:455](../../../../../../services/web-collector/src/jane_web_collector/state.py#L455).

```python
def frontier_counts(self, collection_id: str) -> dict[str, int]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, int]`.

## jane_web_collector.state.StateStore.drop_pending

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:461](../../../../../../services/web-collector/src/jane_web_collector/state.py#L461).

```python
def drop_pending(self, collection_id: str, fence: Fence | None=None) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `fence` | `Fence \| None` | `None` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Budget reached: pending and stale in-flight URLs are dropped (not fetched in this run).
```

## jane_web_collector.state.StateStore.frontier_size_for_state_key

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:469](../../../../../../services/web-collector/src/jane_web_collector/state.py#L469).

```python
def frontier_size_for_state_key(self, state_key: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state_key` | `str` | `—` | positional-or-keyword |

Результат: `int`.

## jane_web_collector.state.StateStore.save_strategy_states

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:478](../../../../../../services/web-collector/src/jane_web_collector/state.py#L478).

```python
def save_strategy_states(self, db: sqlite3.Connection, collection_id: str, states: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `sqlite3.Connection` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |
| `states` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.state.StateStore.load_strategy_states

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:488](../../../../../../services/web-collector/src/jane_web_collector/state.py#L488).

```python
def load_strategy_states(self, collection_id: str) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_web_collector.state.StateStore.save_cursors

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:494](../../../../../../services/web-collector/src/jane_web_collector/state.py#L494).

```python
def save_cursors(self, db: sqlite3.Connection, state_key: str, cursors: Mapping[str, Any], now: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `sqlite3.Connection` | `—` | positional-or-keyword |
| `state_key` | `str` | `—` | positional-or-keyword |
| `cursors` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `now` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.state.StateStore.append_material

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:505](../../../../../../services/web-collector/src/jane_web_collector/state.py#L505).

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

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_backpressure_fencing.py:40](../../../../../../services/web-collector/tests/test_backpressure_fencing.py#L40).

```python
state.append_material(db, collection_id, f"observation-{seq}", {})
```

## jane_web_collector.state.StateStore.materials_after

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:515](../../../../../../services/web-collector/src/jane_web_collector/state.py#L515).

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

## jane_web_collector.state.StateStore.ack

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:524](../../../../../../services/web-collector/src/jane_web_collector/state.py#L524).

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

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_backpressure_fencing.py:85](../../../../../../services/web-collector/tests/test_backpressure_fencing.py#L85).

```python
assert state.ack(collection_id, 1) == 1
```

## jane_web_collector.state.StateStore.unacked_count

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:536](../../../../../../services/web-collector/src/jane_web_collector/state.py#L536).

```python
def unacked_count(self, collection_id: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |

Результат: `int`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_backpressure_fencing.py:81](../../../../../../services/web-collector/tests/test_backpressure_fencing.py#L81).

```python
assert state.unacked_count(collection_id) == 2
```

## jane_web_collector.state.StateStore.emitted_count

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:540](../../../../../../services/web-collector/src/jane_web_collector/state.py#L540).

```python
def emitted_count(self, collection_id: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `collection_id` | `str` | `—` | positional-or-keyword |

Результат: `int`.

## jane_web_collector.state.StateStore.add_error

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:545](../../../../../../services/web-collector/src/jane_web_collector/state.py#L545).

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

## jane_web_collector.state.StateStore.errors_after

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:552](../../../../../../services/web-collector/src/jane_web_collector/state.py#L552).

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

## jane_web_collector.state.StateStore.url_state

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:562](../../../../../../services/web-collector/src/jane_web_collector/state.py#L562).

```python
def url_state(self, state_key: str, url: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state_key` | `str` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

## jane_web_collector.state.StateStore.put_url_state

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:570](../../../../../../services/web-collector/src/jane_web_collector/state.py#L570).

```python
def put_url_state(self, db: sqlite3.Connection, state_key: str, url: str, *, status: int | None, etag: str | None, last_modified: str | None, content_sha256: str | None, links: Sequence[str] | None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `sqlite3.Connection` | `—` | positional-or-keyword |
| `state_key` | `str` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |
| `status` | `int \| None` | `—` | keyword-only |
| `etag` | `str \| None` | `—` | keyword-only |
| `last_modified` | `str \| None` | `—` | keyword-only |
| `content_sha256` | `str \| None` | `—` | keyword-only |
| `links` | `Sequence[str] \| None` | `—` | keyword-only |

Результат: `None`.

## jane_web_collector.state.StateStore.state_summary

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:602](../../../../../../services/web-collector/src/jane_web_collector/state.py#L602).

```python
def state_summary(self, state_key: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state_key` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

## jane_web_collector.state.StateStore.delete_state

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:621](../../../../../../services/web-collector/src/jane_web_collector/state.py#L621).

```python
def delete_state(self, state_key: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state_key` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.state.StateStore.get_connection

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:627](../../../../../../services/web-collector/src/jane_web_collector/state.py#L627).

```python
def get_connection(self, connection_id: str) -> tuple[dict[str, Any], str] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |

Результат: `tuple[dict[str, Any], str] | None`.

## jane_web_collector.state.StateStore.put_connection

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:631](../../../../../../services/web-collector/src/jane_web_collector/state.py#L631).

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

## jane_web_collector.state.StateStore.delete_connection

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:644](../../../../../../services/web-collector/src/jane_web_collector/state.py#L644).

```python
def delete_connection(self, connection_id: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `connection_id` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_web_collector.state.StateStore.list_connections

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:650](../../../../../../services/web-collector/src/jane_web_collector/state.py#L650).

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

## jane_web_collector.state.StateStore.read

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:659](../../../../../../services/web-collector/src/jane_web_collector/state.py#L659).

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

## jane_web_collector.state.StateStore.get_job

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:664](../../../../../../services/web-collector/src/jane_web_collector/state.py#L664).

```python
def get_job(self, job_id: str) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job_id` | `str` | `—` | positional-or-keyword |

Результат: `str | None`.

## jane_web_collector.state.StateStore.work_row

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:668](../../../../../../services/web-collector/src/jane_web_collector/state.py#L668).

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

## jane_web_collector.state.StateStore.cancel_unstarted

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:675](../../../../../../services/web-collector/src/jane_web_collector/state.py#L675).

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

## jane_web_collector.state.StateStore.host_take_slot

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:686](../../../../../../services/web-collector/src/jane_web_collector/state.py#L686).

```python
def host_take_slot(self, host: str, instance_id: str, token: str, *, interval: float, parallel: int, ttl: float) -> tuple[bool, float]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |
| `instance_id` | `str` | `—` | positional-or-keyword |
| `token` | `str` | `—` | positional-or-keyword |
| `interval` | `float` | `—` | keyword-only |
| `parallel` | `int` | `—` | keyword-only |
| `ttl` | `float` | `—` | keyword-only |

Результат: `tuple[bool, float]`.

### Опис із вихідного коду

```text
One attempt of request ``token`` to start on ``host`` for the whole platform (R15), in one transaction.

Registers (renews) the limits of ``instance_id`` on the host and queues the request in arrival order
(``host_waiters``). The request takes a slot only when it may start **now**: it is first in line (starts go
strictly in arrival order: a younger request never takes the start the first one waits for), fewer requests
than the smallest registered parallelism are in flight, and the schedule allows a start - the largest registered interval after the previous start of any instance has
passed, and so has a ``Retry-After``. A slot is thus never held while waiting (review 1 of WP-16).

Returns ``(True, 0.0)`` when the slot is taken (the start is recorded as now), ``(False, seconds)`` when the
request is first in line but the schedule allows a start only in ``seconds``, ``(False, 0.0)`` when it waits
for a slot or an older waiter (try again after the poll interval). Expired registrations, slots and waiters
(instances that died: nothing renews them) are dropped first.
```

## jane_web_collector.state.StateStore.host_renew

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:758](../../../../../../services/web-collector/src/jane_web_collector/state.py#L758).

```python
def host_renew(self, instance_id: str, registrations: Mapping[str, tuple[float, int]], tokens: Sequence[str], ttl: float) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `instance_id` | `str` | `—` | positional-or-keyword |
| `registrations` | `Mapping[str, tuple[float, int]]` | `—` | positional-or-keyword |
| `tokens` | `Sequence[str]` | `—` | positional-or-keyword |
| `ttl` | `float` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Keep alive what a live instance holds (R15): its registrations on hosts (``host -> (interval, parallel)``,
re-created if they expired meanwhile), and the slots and places in line of ``tokens``. A killed instance
renews nothing, so its rows expire ``ttl`` seconds after its last renewal.
```

## jane_web_collector.state.StateStore.host_release_slot

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:781](../../../../../../services/web-collector/src/jane_web_collector/state.py#L781).

```python
def host_release_slot(self, host: str, token: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |
| `token` | `str` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Give back the slot of ``token`` (or its place in line, if it never got one).
```

## jane_web_collector.state.StateStore.host_push_back

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:787](../../../../../../services/web-collector/src/jane_web_collector/state.py#L787).

```python
def host_push_back(self, host: str, until: float) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |
| `until` | `float` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.state.StateStore.host_leave

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:795](../../../../../../services/web-collector/src/jane_web_collector/state.py#L795).

```python
def host_leave(self, host: str, instance_id: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |
| `instance_id` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.state.StateStore.host_rows

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:799](../../../../../../services/web-collector/src/jane_web_collector/state.py#L799).

```python
def host_rows(self, host: str) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
Shared state of one host (diagnostics, tests).
```

## jane_web_collector.state.StateStore.host_prune

**Метод.** Код: [services/web-collector/src/jane_web_collector/state.py:805](../../../../../../services/web-collector/src/jane_web_collector/state.py#L805).

```python
def host_prune(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Drop expired registrations, slots and schedules of hosts nobody uses (housekeeping).
```
