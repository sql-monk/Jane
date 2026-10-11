# Модуль `jane_storage.connections`

> Згенеровано `scripts/docs_reference.py` з [services/storage/src/jane_storage/connections.py](../../../../../services/storage/src/jane_storage/connections.py). Не редагуйте вручну.

Managed connections of the storage executor (ADR-0006) and the pool of opened adapters.

* Definitions (``connection.schema.json``: ``params`` + ``secret_refs``) come from a config file (``JANE_STORAGE_CONNECTIONS_FILE``, JSON/YAML: ``{"connections": [...]}``) and from ``PUT /v1/connections/{id}`` (the orchestrator syncs its registry; values are never secrets).
* ``secret_refs`` are resolved only here, in the executor's environment, under the secret policy (:mod:`jane_storage.policy`): ``env:`` only with the configured prefix, ``file:`` only inside the secrets directory, ``vault:`` disabled, and every network address of the connection from the host allowlist. ``PUT`` of a violating connection → 422 (``secret_ref_not_allowed`` / ``host_not_allowed``); a violating connection from the config file (or stored bypassing the API) is kept, but gets no secrets and is rejected (422) when used.
* :class:`AdapterPool` keeps one opened adapter per (connection, definition ETag, options) and closes adapters whose connection changed or was deleted. Adapter errors raised while opening are redacted: the resolved secret values of the connection never reach responses or logs.

## Зміст

- [Клас `AdapterPool`](#клас-adapterpool)
- [Клас `ConnectionRegistry`](#клас-connectionregistry)
- [Клас `SecretUnresolved`](#клас-secretunresolved)
- [Клас `StoredConnection`](#клас-storedconnection)

## Класи

### Клас `AdapterPool`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.connections` |
| Код | [connections.py:242](../../../../../services/storage/src/jane_storage/connections.py#L242) |

```python
class AdapterPool: ...
```

Opened adapters per connection; implements ``jane_storage.handler.AdapterProvider``.

One adapter per (connection, definition ETag, options). A changed definition (``PUT``) or a deleted connection *retires* the connection's adapters: new work opens a new adapter, while work that already holds one through :meth:`lease` finishes on it; a retired adapter is closed when its last lease ends. An unchanged ``PUT`` keeps the open adapter.

#### Конструктор `AdapterPool.__init__`

```python
def __init__(
    self,
    registry: ConnectionRegistry,
    default_options: Mapping[str, Any] | None = None,
    *,
    connection_first: Iterable[str] = (),
) -> None: ...
```

Код: [connections.py:251](../../../../../services/storage/src/jane_storage/connections.py#L251).

#### Метод `AdapterPool.check`

```python
def check(self, connection_id: str, adapter_kind: str) -> None: ...
```

Винятки в коді методу: `ValidationFailed`.

Код: [connections.py:270](../../../../../services/storage/src/jane_storage/connections.py#L270).

#### Метод `AdapterPool.adapter_for`

```python
async def adapter_for(
    self,
    connection_id: str,
    adapter_kind: str,
    options: Mapping[str, Any],
) -> StorageAdapter: ...
```

The opened adapter without a lease: a retirement may close it under the caller (prefer :meth:`lease`).

Код: [connections.py:316](../../../../../services/storage/src/jane_storage/connections.py#L316).

#### Метод `AdapterPool.lease`

```python
@asynccontextmanager
async def lease(
    self,
    connection_id: str,
    adapter_kind: str,
    options: Mapping[str, Any],
) -> AsyncIterator[StorageAdapter]: ...
```

The opened adapter for the duration of the block: retiring it waits for the block to end.

Код: [connections.py:323](../../../../../services/storage/src/jane_storage/connections.py#L323).

#### Метод `AdapterPool.forget`

```python
async def forget(self, connection_id: str) -> None: ...
```

The connection changed or was deleted: retire all its adapters (in-flight work finishes first).

Код: [connections.py:367](../../../../../services/storage/src/jane_storage/connections.py#L367).

#### Метод `AdapterPool.close`

```python
async def close(self) -> None: ...
```

Код: [connections.py:372](../../../../../services/storage/src/jane_storage/connections.py#L372).

### Клас `ConnectionRegistry`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.connections` |
| Код | [connections.py:84](../../../../../services/storage/src/jane_storage/connections.py#L84) |

```python
class ConnectionRegistry: ...
```

#### Конструктор `ConnectionRegistry.__init__`

```python
def __init__(
    self,
    validator: Any = None,
    environ: Mapping[str, str] | None = None,
    policy: ConnectionPolicy | None = None,
) -> None: ...
```

Код: [connections.py:85](../../../../../services/storage/src/jane_storage/connections.py#L85).

#### Метод `ConnectionRegistry.load_file`

```python
def load_file(self, path: Path) -> int: ...
```

Connections of the config file. A policy violation does not stop the service (the connection is kept, gets no secrets and is rejected when used); other validation errors do.

Код: [connections.py:98](../../../../../services/storage/src/jane_storage/connections.py#L98).

#### Метод `ConnectionRegistry.validate`

```python
def validate(self, doc: Mapping[str, Any]) -> None: ...
```

Винятки в коді методу: `JaneError`, `ValidationFailed`.

Код: [connections.py:108](../../../../../services/storage/src/jane_storage/connections.py#L108).

#### Метод `ConnectionRegistry.put`

```python
def put(
    self,
    doc: dict[str, Any],
    *,
    enforce_policy: bool = True,
) -> tuple[StoredConnection, bool]: ...
```

Store a definition. ``enforce_policy`` (the API): a secret-policy violation → 422 and nothing is stored; otherwise (config file) the connection is stored with a warning and rejected when used.

Винятки в коді методу: `ValidationFailed`.

Код: [connections.py:120](../../../../../services/storage/src/jane_storage/connections.py#L120).

#### Метод `ConnectionRegistry.add_resolved`

```python
def add_resolved(self, conn: ResolvedConnection) -> StoredConnection: ...
```

Register an already resolved connection (embedding, tests of adapters).

Код: [connections.py:143](../../../../../services/storage/src/jane_storage/connections.py#L143).

#### Метод `ConnectionRegistry.get`

```python
def get(self, connection_id: str) -> StoredConnection: ...
```

Винятки в коді методу: `NotFound`.

Код: [connections.py:151](../../../../../services/storage/src/jane_storage/connections.py#L151).

#### Метод `ConnectionRegistry.delete`

```python
def delete(self, connection_id: str) -> None: ...
```

Код: [connections.py:157](../../../../../services/storage/src/jane_storage/connections.py#L157).

#### Метод `ConnectionRegistry.list`

```python
def list(self) -> list[StoredConnection]: ...
```

Код: [connections.py:162](../../../../../services/storage/src/jane_storage/connections.py#L162).

#### Метод `ConnectionRegistry.policy_errors`

```python
def policy_errors(self, connection_id: str) -> builtins.list[FieldError]: ...
```

Secret-policy violations of a stored connection (``add_resolved`` ones are the embedder's).

Код: [connections.py:166](../../../../../services/storage/src/jane_storage/connections.py#L166).

#### Метод `ConnectionRegistry.ensure_allowed`

```python
def ensure_allowed(
    self,
    connection_id: str,
    *,
    pointer: str | None = None,
    parameter: str | None = None,
) -> None: ...
```

422 (``secret_ref_not_allowed`` / ``host_not_allowed``) if the connection violates the policy.

Винятки в коді методу: `ValidationFailed`.

Код: [connections.py:173](../../../../../services/storage/src/jane_storage/connections.py#L173).

#### Метод `ConnectionRegistry.secrets_resolved`

```python
def secrets_resolved(self, connection_id: str) -> dict[str, bool]: ...
```

Name → resolvable (never values); all ``False`` for a connection that violates the policy.

Код: [connections.py:197](../../../../../services/storage/src/jane_storage/connections.py#L197).

#### Метод `ConnectionRegistry.secret_values`

```python
def secret_values(self, connection_id: str) -> builtins.list[str]: ...
```

Resolved values of the connection — only to redact error messages.

Код: [connections.py:207](../../../../../services/storage/src/jane_storage/connections.py#L207).

#### Метод `ConnectionRegistry.resolve`

```python
def resolve(self, connection_id: str) -> ResolvedConnection: ...
```

Винятки в коді методу: `SecretUnresolved`.

Код: [connections.py:216](../../../../../services/storage/src/jane_storage/connections.py#L216).

### Клас `SecretUnresolved`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_storage.connections` |
| Успадкування | `JaneError` |
| Код | [connections.py:49](../../../../../services/storage/src/jane_storage/connections.py#L49) |

```python
class SecretUnresolved(JaneError): ...
```

A secret reference cannot be resolved in this executor's environment.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'upstream_unavailable'` |  |

### Клас `StoredConnection`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_storage.connections` |
| Код | [connections.py:56](../../../../../services/storage/src/jane_storage/connections.py#L56) |

```python
@dataclass(frozen=True)
class StoredConnection: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `document` | `dict[str, Any]` | — | читання |  |
| `etag` | `str` | — | читання |  |
| `connection_id` | `str` | — | читання (властивість) |  |
| `kind` | `str` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.
