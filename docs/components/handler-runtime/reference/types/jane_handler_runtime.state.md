# Модуль `jane_handler_runtime.state`

> Згенеровано `scripts/docs_reference.py` з [services/handler-runtime/src/jane_handler_runtime/state.py](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py). Не редагуйте вручну.

Service state shared by instances: idempotency keys, jobs and invocation results.

* ``InMemoryState`` - default for a single standalone instance and the CLI (lost on restart);
* ``PostgresState`` - own database/schema ``jane_handler_runtime`` (``JANE_HANDLER_RUNTIME_STATE_DSN``, data-ownership.md): jane-kit's shared ``PgIdempotencyStore`` / ``PgJobStore`` (R17) and the results of ``GET /v1/invocations/{id}``, so any instance answers a redelivery with the stored result (``duplicate: true``) and reads jobs/invocations created by another instance.

psycopg is used synchronously in worker threads (``asyncio.to_thread``): the async driver does not work with the Windows Proactor event loop, and the service must run on Windows and Linux.

## Зміст

- [Клас `InMemoryState`](#клас-inmemorystate)
- [Клас `PostgresState`](#клас-postgresstate)
- [Клас `ResultStore`](#клас-resultstore)
- [Клас `ServiceState`](#клас-servicestate)

## Класи

### Клас `InMemoryState`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_handler_runtime.state` |
| Код | [state.py:64](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L64) |

```python
class InMemoryState: ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `name` | `'memory'` |  |

#### Конструктор `InMemoryState.__init__`

```python
def __init__(self, limits: ServiceLimits) -> None: ...
```

Код: [state.py:67](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L67).

#### Метод `InMemoryState.open`

```python
async def open(self) -> None: ...
```

Код: [state.py:72](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L72).

#### Метод `InMemoryState.close`

```python
async def close(self) -> None: ...
```

Код: [state.py:75](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L75).

#### Метод `InMemoryState.ping`

```python
async def ping(self) -> bool: ...
```

Код: [state.py:78](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L78).

#### Метод `InMemoryState.heartbeat`

```python
async def heartbeat(self) -> None: ...
```

Код: [state.py:81](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L81).

### Клас `PostgresState`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_handler_runtime.state` |
| Код | [state.py:97](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L97) |

```python
class PostgresState: ...
```

Idempotency keys and jobs in jane-kit's shared stores (R17: leases, fencing, take-over), results here.

Tables ``idempotency`` and ``jobs`` keep their layout (split response columns, ``doc``); the kit migration adds the claim ``owner``/``token`` columns in place.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `name` | `'postgresql'` |  |

#### Конструктор `PostgresState.__init__`

```python
def __init__(self, dsn: str, schema: str, limits: ServiceLimits, instance_id: str) -> None: ...
```

Код: [state.py:106](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L106).

#### Метод `PostgresState.q`

```python
def q(self, text: str) -> sql.Composed: ...
```

Код: [state.py:131](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L131).

#### Метод `PostgresState.run`

```python
def run(
    self,
    text: str,
    params: tuple[Any, ...] = (),
    fetch: bool = False,
) -> list[dict[str, Any]]: ...
```

Код: [state.py:134](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L134).

#### Метод `PostgresState.open`

```python
async def open(self) -> None: ...
```

Код: [state.py:151](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L151).

#### Метод `PostgresState.close`

```python
async def close(self) -> None: ...
```

Код: [state.py:155](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L155).

#### Метод `PostgresState.ping`

```python
async def ping(self) -> bool: ...
```

Код: [state.py:158](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L158).

#### Метод `PostgresState.heartbeat`

```python
async def heartbeat(self) -> None: ...
```

Renew this process's job leases and idempotency claims; drop expired keys.

Код: [state.py:161](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L161).

### Клас `ResultStore`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_handler_runtime.state` |
| Успадкування | `Protocol` |
| Код | [state.py:32](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L32) |

```python
class ResultStore(Protocol): ...
```

#### Метод `ResultStore.put`

```python
async def put(self, result: dict[str, Any]) -> None: ...
```

Код: [state.py:33](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L33).

#### Метод `ResultStore.get`

```python
async def get(self, invocation_id: str) -> dict[str, Any] | None: ...
```

Код: [state.py:34](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L34).

### Клас `ServiceState`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_handler_runtime.state` |
| Успадкування | `Protocol` |
| Код | [state.py:37](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L37) |

```python
class ServiceState(Protocol): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `name` | `str` | — | читання й запис |  |
| `idempotency` | `IdempotencyStore` | — | читання й запис |  |
| `jobs` | `JobStore` | — | читання й запис |  |
| `results` | `ResultStore` | — | читання й запис |  |

#### Метод `ServiceState.open`

```python
async def open(self) -> None: ...
```

Код: [state.py:43](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L43).

#### Метод `ServiceState.close`

```python
async def close(self) -> None: ...
```

Код: [state.py:44](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L44).

#### Метод `ServiceState.ping`

```python
async def ping(self) -> bool: ...
```

Код: [state.py:45](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L45).

#### Метод `ServiceState.heartbeat`

```python
async def heartbeat(self) -> None: ...
```

Код: [state.py:46](../../../../../services/handler-runtime/src/jane_handler_runtime/state.py#L46).
