# jane_handler_runtime.state

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_handler_runtime.state.ResultStore](#jane_handler_runtimestateresultstore)
- [jane_handler_runtime.state.ResultStore.put](#jane_handler_runtimestateresultstoreput)
- [jane_handler_runtime.state.ResultStore.get](#jane_handler_runtimestateresultstoreget)
- [jane_handler_runtime.state.ServiceState](#jane_handler_runtimestateservicestate)
- [jane_handler_runtime.state.ServiceState.name](#jane_handler_runtimestateservicestatename)
- [jane_handler_runtime.state.ServiceState.idempotency](#jane_handler_runtimestateservicestateidempotency)
- [jane_handler_runtime.state.ServiceState.jobs](#jane_handler_runtimestateservicestatejobs)
- [jane_handler_runtime.state.ServiceState.results](#jane_handler_runtimestateservicestateresults)
- [jane_handler_runtime.state.ServiceState.open](#jane_handler_runtimestateservicestateopen)
- [jane_handler_runtime.state.ServiceState.close](#jane_handler_runtimestateservicestateclose)
- [jane_handler_runtime.state.ServiceState.ping](#jane_handler_runtimestateservicestateping)
- [jane_handler_runtime.state.ServiceState.heartbeat](#jane_handler_runtimestateservicestateheartbeat)
- [jane_handler_runtime.state.InMemoryState](#jane_handler_runtimestateinmemorystate)
- [jane_handler_runtime.state.InMemoryState.name](#jane_handler_runtimestateinmemorystatename)
- [jane_handler_runtime.state.InMemoryState.__init__](#jane_handler_runtimestateinmemorystate__init__)
- [jane_handler_runtime.state.InMemoryState.idempotency](#jane_handler_runtimestateinmemorystateidempotency)
- [jane_handler_runtime.state.InMemoryState.jobs](#jane_handler_runtimestateinmemorystatejobs)
- [jane_handler_runtime.state.InMemoryState.results](#jane_handler_runtimestateinmemorystateresults)
- [jane_handler_runtime.state.InMemoryState.open](#jane_handler_runtimestateinmemorystateopen)
- [jane_handler_runtime.state.InMemoryState.close](#jane_handler_runtimestateinmemorystateclose)
- [jane_handler_runtime.state.InMemoryState.ping](#jane_handler_runtimestateinmemorystateping)
- [jane_handler_runtime.state.InMemoryState.heartbeat](#jane_handler_runtimestateinmemorystateheartbeat)
- [jane_handler_runtime.state.PostgresState](#jane_handler_runtimestatepostgresstate)
- [jane_handler_runtime.state.PostgresState.name](#jane_handler_runtimestatepostgresstatename)
- [jane_handler_runtime.state.PostgresState.__init__](#jane_handler_runtimestatepostgresstate__init__)
- [jane_handler_runtime.state.PostgresState.schema_name](#jane_handler_runtimestatepostgresstateschema_name)
- [jane_handler_runtime.state.PostgresState.schema](#jane_handler_runtimestatepostgresstateschema)
- [jane_handler_runtime.state.PostgresState.limits](#jane_handler_runtimestatepostgresstatelimits)
- [jane_handler_runtime.state.PostgresState.instance_id](#jane_handler_runtimestatepostgresstateinstance_id)
- [jane_handler_runtime.state.PostgresState.db](#jane_handler_runtimestatepostgresstatedb)
- [jane_handler_runtime.state.PostgresState.pool](#jane_handler_runtimestatepostgresstatepool)
- [jane_handler_runtime.state.PostgresState.idempotency](#jane_handler_runtimestatepostgresstateidempotency)
- [jane_handler_runtime.state.PostgresState.jobs](#jane_handler_runtimestatepostgresstatejobs)
- [jane_handler_runtime.state.PostgresState.results](#jane_handler_runtimestatepostgresstateresults)
- [jane_handler_runtime.state.PostgresState.q](#jane_handler_runtimestatepostgresstateq)
- [jane_handler_runtime.state.PostgresState.run](#jane_handler_runtimestatepostgresstaterun)
- [jane_handler_runtime.state.PostgresState.open](#jane_handler_runtimestatepostgresstateopen)
- [jane_handler_runtime.state.PostgresState.close](#jane_handler_runtimestatepostgresstateclose)
- [jane_handler_runtime.state.PostgresState.ping](#jane_handler_runtimestatepostgresstateping)
- [jane_handler_runtime.state.PostgresState.heartbeat](#jane_handler_runtimestatepostgresstateheartbeat)

## jane_handler_runtime.state.ResultStore

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:32](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L32).

```python
class ResultStore(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [put](jane_handler_runtime.state.md#jane_handler_runtimestateresultstoreput) | Метод | ні |
| [get](jane_handler_runtime.state.md#jane_handler_runtimestateresultstoreget) | Метод | ні |

## jane_handler_runtime.state.ResultStore.put

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:33](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L33).

```python
async def put(self, result: dict[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `result` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_handler_runtime.state.ResultStore.get

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:34](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L34).

```python
async def get(self, invocation_id: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `invocation_id` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

## jane_handler_runtime.state.ServiceState

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:37](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L37).

```python
class ServiceState(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_handler_runtime.state.md#jane_handler_runtimestateservicestatename) | Поле | ні |
| [idempotency](jane_handler_runtime.state.md#jane_handler_runtimestateservicestateidempotency) | Поле | ні |
| [jobs](jane_handler_runtime.state.md#jane_handler_runtimestateservicestatejobs) | Поле | ні |
| [results](jane_handler_runtime.state.md#jane_handler_runtimestateservicestateresults) | Поле | ні |
| [open](jane_handler_runtime.state.md#jane_handler_runtimestateservicestateopen) | Метод | ні |
| [close](jane_handler_runtime.state.md#jane_handler_runtimestateservicestateclose) | Метод | ні |
| [ping](jane_handler_runtime.state.md#jane_handler_runtimestateservicestateping) | Метод | ні |
| [heartbeat](jane_handler_runtime.state.md#jane_handler_runtimestateservicestateheartbeat) | Метод | ні |

## jane_handler_runtime.state.ServiceState.name

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:38](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L38).

```python
name: str
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.state.ServiceState.idempotency

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:39](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L39).

```python
idempotency: IdempotencyStore
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.state.ServiceState.jobs

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:40](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L40).

```python
jobs: JobStore
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.state.ServiceState.results

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:41](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L41).

```python
results: ResultStore
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.state.ServiceState.open

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:43](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L43).

```python
async def open(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_handler_runtime.state.ServiceState.close

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:44](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L44).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_handler_runtime.state.ServiceState.ping

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:45](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L45).

```python
async def ping(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_handler_runtime.state.ServiceState.heartbeat

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:46](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L46).

```python
async def heartbeat(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_handler_runtime.state.InMemoryState

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:64](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L64).

```python
class InMemoryState:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_handler_runtime.state.md#jane_handler_runtimestateinmemorystatename) | Поле | ні |
| [__init__](jane_handler_runtime.state.md#jane_handler_runtimestateinmemorystate__init__) | Конструктор | ні |
| [idempotency](jane_handler_runtime.state.md#jane_handler_runtimestateinmemorystateidempotency) | Поле екземпляра | ні |
| [jobs](jane_handler_runtime.state.md#jane_handler_runtimestateinmemorystatejobs) | Поле екземпляра | ні |
| [results](jane_handler_runtime.state.md#jane_handler_runtimestateinmemorystateresults) | Поле екземпляра | ні |
| [open](jane_handler_runtime.state.md#jane_handler_runtimestateinmemorystateopen) | Метод | ні |
| [close](jane_handler_runtime.state.md#jane_handler_runtimestateinmemorystateclose) | Метод | ні |
| [ping](jane_handler_runtime.state.md#jane_handler_runtimestateinmemorystateping) | Метод | ні |
| [heartbeat](jane_handler_runtime.state.md#jane_handler_runtimestateinmemorystateheartbeat) | Метод | ні |

## jane_handler_runtime.state.InMemoryState.name

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:65](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L65).

```python
name = 'memory'
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.state.InMemoryState.__init__

**Конструктор.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:67](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L67).

```python
def __init__(self, limits: ServiceLimits) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |

Результат: `None`.

## jane_handler_runtime.state.InMemoryState.idempotency

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:68](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L68).

```python
self.idempotency: IdempotencyStore = InMemoryIdempotencyStore(limits.idempotency)
```

## jane_handler_runtime.state.InMemoryState.jobs

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:69](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L69).

```python
self.jobs: JobStore = InMemoryJobStore(limits.jobs)
```

## jane_handler_runtime.state.InMemoryState.results

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:70](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L70).

```python
self.results: ResultStore = InMemoryResultStore(limits.packages.max_stored_results)
```

## jane_handler_runtime.state.InMemoryState.open

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:72](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L72).

```python
async def open(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_handler_runtime.state.InMemoryState.close

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:75](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L75).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_handler_runtime.state.InMemoryState.ping

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:78](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L78).

```python
async def ping(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_handler_runtime.state.InMemoryState.heartbeat

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:81](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L81).

```python
async def heartbeat(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_handler_runtime.state.PostgresState

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:97](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L97).

```python
class PostgresState:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_handler_runtime.state.md#jane_handler_runtimestatepostgresstatename) | Поле | ні |
| [__init__](jane_handler_runtime.state.md#jane_handler_runtimestatepostgresstate__init__) | Конструктор | ні |
| [schema_name](jane_handler_runtime.state.md#jane_handler_runtimestatepostgresstateschema_name) | Поле екземпляра | ні |
| [schema](jane_handler_runtime.state.md#jane_handler_runtimestatepostgresstateschema) | Поле екземпляра | ні |
| [limits](jane_handler_runtime.state.md#jane_handler_runtimestatepostgresstatelimits) | Поле екземпляра | ні |
| [instance_id](jane_handler_runtime.state.md#jane_handler_runtimestatepostgresstateinstance_id) | Поле екземпляра | ні |
| [db](jane_handler_runtime.state.md#jane_handler_runtimestatepostgresstatedb) | Поле екземпляра | ні |
| [pool](jane_handler_runtime.state.md#jane_handler_runtimestatepostgresstatepool) | Поле екземпляра | ні |
| [idempotency](jane_handler_runtime.state.md#jane_handler_runtimestatepostgresstateidempotency) | Поле екземпляра | ні |
| [jobs](jane_handler_runtime.state.md#jane_handler_runtimestatepostgresstatejobs) | Поле екземпляра | ні |
| [results](jane_handler_runtime.state.md#jane_handler_runtimestatepostgresstateresults) | Поле екземпляра | ні |
| [q](jane_handler_runtime.state.md#jane_handler_runtimestatepostgresstateq) | Метод | ні |
| [run](jane_handler_runtime.state.md#jane_handler_runtimestatepostgresstaterun) | Метод | ні |
| [open](jane_handler_runtime.state.md#jane_handler_runtimestatepostgresstateopen) | Метод | ні |
| [close](jane_handler_runtime.state.md#jane_handler_runtimestatepostgresstateclose) | Метод | ні |
| [ping](jane_handler_runtime.state.md#jane_handler_runtimestatepostgresstateping) | Метод | ні |
| [heartbeat](jane_handler_runtime.state.md#jane_handler_runtimestatepostgresstateheartbeat) | Метод | ні |

### Опис із вихідного коду

```text
Idempotency keys and jobs in jane-kit's shared stores (R17: leases, fencing, take-over), results here.

Tables ``idempotency`` and ``jobs`` keep their layout (split response columns, ``doc``); the kit migration
adds the claim ``owner``/``token`` columns in place.
```

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_state.py:181](../../../../../../services/handler-runtime/tests/test_state.py#L181).

```python
a = PostgresState(dsn[0], dsn[1], ServiceLimits(), "dead-owner")
```

Контекст і передумови: [services/handler-runtime/tests/test_state.py:182](../../../../../../services/handler-runtime/tests/test_state.py#L182).

```python
b = PostgresState(dsn[0], dsn[1], ServiceLimits(), "new-owner")
```

## jane_handler_runtime.state.PostgresState.name

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:104](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L104).

```python
name = 'postgresql'
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.state.PostgresState.__init__

**Конструктор.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:106](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L106).

```python
def __init__(self, dsn: str, schema: str, limits: ServiceLimits, instance_id: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `dsn` | `str` | `—` | positional-or-keyword |
| `schema` | `str` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |
| `instance_id` | `str` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_state.py:181](../../../../../../services/handler-runtime/tests/test_state.py#L181).

```python
a = PostgresState(dsn[0], dsn[1], ServiceLimits(), "dead-owner")
```

Контекст і передумови: [services/handler-runtime/tests/test_state.py:182](../../../../../../services/handler-runtime/tests/test_state.py#L182).

```python
b = PostgresState(dsn[0], dsn[1], ServiceLimits(), "new-owner")
```

## jane_handler_runtime.state.PostgresState.schema_name

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:107](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L107).

```python
self.schema_name = schema
```

## jane_handler_runtime.state.PostgresState.schema

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:108](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L108).

```python
self.schema = sql.Identifier(schema)
```

## jane_handler_runtime.state.PostgresState.limits

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:109](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L109).

```python
self.limits = limits
```

## jane_handler_runtime.state.PostgresState.instance_id

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:110](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L110).

```python
self.instance_id = instance_id
```

## jane_handler_runtime.state.PostgresState.db

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:112](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L112).

```python
self.db = PgDatabase(dsn, max_size=state.pool_max_size, connect_timeout_ms=state.connect_timeout_ms)
```

## jane_handler_runtime.state.PostgresState.pool

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:113](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L113).

```python
self.pool = self.db.pool
```

## jane_handler_runtime.state.PostgresState.idempotency

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:127](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L127).

```python
self.idempotency: IdempotencyStore = self._idem
```

## jane_handler_runtime.state.PostgresState.jobs

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:128](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L128).

```python
self.jobs: JobStore = self._jobs
```

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_state.py:187](../../../../../../services/handler-runtime/tests/test_state.py#L187).

```python
await a.jobs.create(job)
```

Контекст і передумови: [services/handler-runtime/tests/test_state.py:189](../../../../../../services/handler-runtime/tests/test_state.py#L189).

```python
await a.jobs.save(running)
```

## jane_handler_runtime.state.PostgresState.results

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:129](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L129).

```python
self.results: ResultStore = _PgResults(self)
```

## jane_handler_runtime.state.PostgresState.q

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:131](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L131).

```python
def q(self, text: str) -> sql.Composed:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `text` | `str` | `—` | positional-or-keyword |

Результат: `sql.Composed`.

## jane_handler_runtime.state.PostgresState.run

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:134](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L134).

```python
def run(self, text: str, params: tuple[Any, ...]=(), fetch: bool=False) -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `text` | `str` | `—` | positional-or-keyword |
| `params` | `tuple[Any, ...]` | `()` | positional-or-keyword |
| `fetch` | `bool` | `False` | positional-or-keyword |

Результат: `list[dict[str, Any]]`.

## jane_handler_runtime.state.PostgresState.open

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:151](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L151).

```python
async def open(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_state.py:183](../../../../../../services/handler-runtime/tests/test_state.py#L183).

```python
await a.open()
```

Контекст і передумови: [services/handler-runtime/tests/test_state.py:184](../../../../../../services/handler-runtime/tests/test_state.py#L184).

```python
await b.open()
```

## jane_handler_runtime.state.PostgresState.close

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:155](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L155).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_state.py:285](../../../../../../services/handler-runtime/tests/test_state.py#L285).

```python
await b.close()
```

Контекст і передумови: [services/handler-runtime/tests/test_state.py:286](../../../../../../services/handler-runtime/tests/test_state.py#L286).

```python
await a.close()
```

## jane_handler_runtime.state.PostgresState.ping

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:158](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L158).

```python
async def ping(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_handler_runtime.state.PostgresState.heartbeat

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/state.py:161](../../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L161).

```python
async def heartbeat(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Renew this process's job leases and idempotency claims; drop expired keys.
```

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_state.py:196](../../../../../../services/handler-runtime/tests/test_state.py#L196).

```python
await a.heartbeat()
```
