# Модуль `jane_orchestrator.executors`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/executors.py](../../../../../services/orchestrator/src/jane_orchestrator/executors.py). Не редагуйте вручну.

Calls to the services the orchestrator combines (collector.v1, handler.v1, storage.v1, registry.v1).

Only their versioned APIs are used — never their databases (ТЗ §4). Retries are decided by the caller (item-level retry policy with the same ``Idempotency-Key``). The only re-send done here is for a pooled keep-alive connection that the executor closed under the request: the request is repeated on a fresh connection (``engine.executor_stale_connection_retries``) when it is safe to repeat - an idempotent method or an ``Idempotency-Key`` - so such a race does not spend an item attempt. Pooled connections are dropped after ``engine.executor_keepalive_expiry_ms`` of idleness, below the executors' server keep-alive (uvicorn ``timeout_keep_alive``, 5 s), which avoids most of these races in the first place.

## Класи

### Клас `ExecutorError`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_orchestrator.executors` |
| Успадкування | `Exception` |
| Код | [executors.py:42](../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L42) |

```python
@dataclass
class ExecutorError(Exception): ...
```

A call did not happen or was rejected (HTTP error, connection error, timeout).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `executor` | `str` | — | читання й запис |  |
| `status` | `int \| None` | — | читання й запис |  |
| `problem` | `dict[str, Any] \| None` | — | читання й запис |  |
| `message` | `str` | — | читання й запис |  |
| `code` | `str` | — | читання (властивість) |  |
| `retryable` | `bool` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `ExecutorError.as_problem`

```python
def as_problem(self) -> dict[str, Any]: ...
```

Код: [executors.py:67](../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L67).

### Клас `Executors`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_orchestrator.executors` |
| Код | [executors.py:89](../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L89) |

```python
class Executors: ...
```

#### Конструктор `Executors.__init__`

```python
def __init__(
    self,
    configs: list[ExecutorConfig],
    *,
    connect_timeout_ms: int,
    request_timeout_ms: int,
    keepalive_expiry_ms: int = 4000,
    stale_connection_retries: int = 1,
) -> None: ...
```

Код: [executors.py:90](../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L90).

#### Метод `Executors.close`

```python
def close(self) -> None: ...
```

Код: [executors.py:108](../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L108).

#### Метод `Executors.by_role`

```python
def by_role(self, role: str) -> list[ExecutorConfig]: ...
```

Код: [executors.py:129](../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L129).

#### Метод `Executors.first`

```python
def first(self, role: str) -> ExecutorConfig | None: ...
```

Код: [executors.py:132](../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L132).

#### Метод `Executors.collector`

```python
def collector(self, name: str) -> ExecutorConfig | None: ...
```

Код: [executors.py:136](../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L136).

#### Метод `Executors.handler_for`

```python
def handler_for(self, package_id: str) -> ExecutorConfig | None: ...
```

Код: [executors.py:144](../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L144).

#### Метод `Executors.call`

```python
def call(
    self,
    executor: ExecutorConfig,
    method: str,
    path: str,
    *,
    json: Any = None,
    params: Mapping[str, Any] | None = None,
    idempotency_key: str | None = None,
    trace_id: str | None = None,
    timeout_ms: int | None = None,
    ok: tuple[int, ...] = (),
) -> httpx.Response: ...
```

Винятки в коді методу: `ExecutorError`.

Код: [executors.py:176](../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L176).

#### Метод `Executors.health`

```python
def health(self, executor: ExecutorConfig, timeout_ms: int) -> str: ...
```

Код: [executors.py:235](../../../../../services/orchestrator/src/jane_orchestrator/executors.py#L235).
