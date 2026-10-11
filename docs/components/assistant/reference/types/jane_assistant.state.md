# Модуль `jane_assistant.state`

> Згенеровано `scripts/docs_reference.py` з [services/assistant/src/jane_assistant/state.py](../../../../../services/assistant/src/jane_assistant/state.py). Не редагуйте вручну.

State of the assistant shared by instances: onboarding sessions, jobs and idempotency keys.

* ``InMemoryState`` - default for a single standalone instance and tests (lost on restart);
* ``PostgresState`` - the service's own database/schema (``JANE_ASSISTANT_STATE_DSN``, ``JANE_ASSISTANT_STATE_SCHEMA``, default ``jane_assistant``; data-ownership.md): ``SessionStore`` and jane-kit's shared ``PgJobStore`` / ``PgIdempotencyStore`` (R17), so any instance reads and continues a session or job created by another one and replays an ``Idempotency-Key`` response.

Concurrency and failures:

* session state transitions of the API use an optimistic version (``UPDATE ... WHERE version = %s``): two instances cannot both select a candidate or accept a proposal;
* a job belongs to the instance that runs it (``owner``) and holds a lease renewed by that instance's heartbeat (``limits.state.heartbeat_interval_ms``). A job whose lease expired (the instance was killed) is marked ``failed`` with the reason by whichever instance reads or lists it next; a terminal job is never overwritten, and only the owner with a live lease writes progress or the result (fencing). On a graceful shutdown the instance cancels its jobs and records the reason.

psycopg is used synchronously in worker threads (``asyncio.to_thread``): the async driver does not work with the Windows Proactor event loop, and the service runs on Windows and Linux.

## Класи

### Клас `InMemoryState`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.state` |
| Код | [state.py:77](../../../../../services/assistant/src/jane_assistant/state.py#L77) |

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

Код: [state.py:80](../../../../../services/assistant/src/jane_assistant/state.py#L80).

#### Метод `InMemoryState.open`

```python
async def open(self) -> None: ...
```

Код: [state.py:87](../../../../../services/assistant/src/jane_assistant/state.py#L87).

#### Метод `InMemoryState.close`

```python
async def close(self) -> None: ...
```

Код: [state.py:90](../../../../../services/assistant/src/jane_assistant/state.py#L90).

#### Метод `InMemoryState.ping`

```python
async def ping(self) -> bool: ...
```

Код: [state.py:93](../../../../../services/assistant/src/jane_assistant/state.py#L93).

#### Метод `InMemoryState.heartbeat`

```python
async def heartbeat(self) -> None: ...
```

Код: [state.py:96](../../../../../services/assistant/src/jane_assistant/state.py#L96).

#### Метод `InMemoryState.release_owned`

```python
async def release_owned(self, reason: str) -> None: ...
```

Код: [state.py:99](../../../../../services/assistant/src/jane_assistant/state.py#L99).

### Клас `PostgresState`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.state` |
| Код | [state.py:114](../../../../../services/assistant/src/jane_assistant/state.py#L114) |

```python
class PostgresState: ...
```

Jobs and ``Idempotency-Key`` records in jane-kit's shared stores (R17), onboarding sessions here.

The tables ``idempotency`` and ``jobs`` keep their layout; the kit migration adds the claim columns in place.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `name` | `'postgresql'` |  |

#### Конструктор `PostgresState.__init__`

```python
def __init__(self, dsn: str, schema: str, limits: ServiceLimits, instance_id: str) -> None: ...
```

Код: [state.py:122](../../../../../services/assistant/src/jane_assistant/state.py#L122).

#### Метод `PostgresState.q`

```python
def q(self, text: str) -> sql.Composed: ...
```

Код: [state.py:145](../../../../../services/assistant/src/jane_assistant/state.py#L145).

#### Метод `PostgresState.run`

```python
def run(
    self,
    text: str,
    params: tuple[Any, ...] = (),
    fetch: bool = False,
) -> list[dict[str, Any]]: ...
```

Код: [state.py:148](../../../../../services/assistant/src/jane_assistant/state.py#L148).

#### Метод `PostgresState.rowcount`

```python
def rowcount(self, text: str, params: tuple[Any, ...]) -> int: ...
```

Код: [state.py:153](../../../../../services/assistant/src/jane_assistant/state.py#L153).

#### Метод `PostgresState.open`

```python
async def open(self) -> None: ...
```

Код: [state.py:166](../../../../../services/assistant/src/jane_assistant/state.py#L166).

#### Метод `PostgresState.close`

```python
async def close(self) -> None: ...
```

Код: [state.py:170](../../../../../services/assistant/src/jane_assistant/state.py#L170).

#### Метод `PostgresState.ping`

```python
async def ping(self) -> bool: ...
```

Код: [state.py:173](../../../../../services/assistant/src/jane_assistant/state.py#L173).

#### Метод `PostgresState.heartbeat`

```python
async def heartbeat(self) -> None: ...
```

Renew this process's job leases and idempotency claims; drop expired keys.

Код: [state.py:176](../../../../../services/assistant/src/jane_assistant/state.py#L176).

#### Метод `PostgresState.release_owned`

```python
async def release_owned(self, reason: str) -> None: ...
```

After the runner cancelled this instance's jobs: record why, close anything left open.

Код: [state.py:182](../../../../../services/assistant/src/jane_assistant/state.py#L182).

### Клас `ServiceState`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_assistant.state` |
| Успадкування | `Protocol` |
| Код | [state.py:63](../../../../../services/assistant/src/jane_assistant/state.py#L63) |

```python
class ServiceState(Protocol): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `name` | `str` | — | читання й запис |  |
| `idempotency` | `IdempotencyStore` | — | читання й запис |  |
| `jobs` | `JobStore` | — | читання й запис |  |
| `job_list` | `JobLister` | — | читання й запис |  |
| `sessions` | `SessionStore` | — | читання й запис |  |

#### Метод `ServiceState.open`

```python
async def open(self) -> None: ...
```

Код: [state.py:70](../../../../../services/assistant/src/jane_assistant/state.py#L70).

#### Метод `ServiceState.close`

```python
async def close(self) -> None: ...
```

Код: [state.py:71](../../../../../services/assistant/src/jane_assistant/state.py#L71).

#### Метод `ServiceState.ping`

```python
async def ping(self) -> bool: ...
```

Код: [state.py:72](../../../../../services/assistant/src/jane_assistant/state.py#L72).

#### Метод `ServiceState.heartbeat`

```python
async def heartbeat(self) -> None: ...
```

Код: [state.py:73](../../../../../services/assistant/src/jane_assistant/state.py#L73).

#### Метод `ServiceState.release_owned`

```python
async def release_owned(self, reason: str) -> None: ...
```

Код: [state.py:74](../../../../../services/assistant/src/jane_assistant/state.py#L74).
