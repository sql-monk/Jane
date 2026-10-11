# Модуль `jane_web_collector.engine`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/engine.py](../../../../../services/web-collector/src/jane_web_collector/engine.py). Не редагуйте вручну.

Service core: collections (start, resume after restart, cancellation), the one-shot fetch and housekeeping.

## Класи

### Клас `Engine`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.engine` |
| Код | [engine.py:45](../../../../../services/web-collector/src/jane_web_collector/engine.py#L45) |

```python
class Engine: ...
```

#### Конструктор `Engine.__init__`

```python
def __init__(
    self,
    settings: Settings,
    base_limits: ResolvedLimits[ServiceLimits],
    state: StateStore,
    registry: Registry,
    schemas: ContractSchemas,
    runner: JobRunner,
    *,
    idempotency: SqliteIdempotencyStore | None = None,
) -> None: ...
```

Код: [engine.py:46](../../../../../services/web-collector/src/jane_web_collector/engine.py#L46).

#### Метод `Engine.resolve`

```python
def resolve(
    self,
    source: Mapping[str, Any] | None = None,
    request: Mapping[str, Any] | None = None,
    *extra: LimitLayer,
) -> ResolvedLimits[ServiceLimits]: ...
```

Винятки в коді методу: `ValidationFailed`.

Код: [engine.py:130](../../../../../services/web-collector/src/jane_web_collector/engine.py#L130).

#### Метод `Engine.start`

```python
async def start(self) -> None: ...
```

Код: [engine.py:148](../../../../../services/web-collector/src/jane_web_collector/engine.py#L148).

#### Метод `Engine.stop`

```python
async def stop(self) -> None: ...
```

Код: [engine.py:152](../../../../../services/web-collector/src/jane_web_collector/engine.py#L152).

#### Метод `Engine.resume_pending`

```python
async def resume_pending(self) -> list[str]: ...
```

Take over non-terminal collections whose lease expired (after a crash/kill) and continue them.

Код: [engine.py:176](../../../../../services/web-collector/src/jane_web_collector/engine.py#L176).

#### Метод `Engine.gc`

```python
def gc(self) -> None: ...
```

Код: [engine.py:208](../../../../../services/web-collector/src/jane_web_collector/engine.py#L208).

#### Метод `Engine.start_collection`

```python
async def start_collection(self, payload: dict[str, Any]) -> Job: ...
```

Винятки в коді методу: `LimitExceeded`, `ValidationFailed`, `JaneError`.

Код: [engine.py:262](../../../../../services/web-collector/src/jane_web_collector/engine.py#L262).

#### Метод `Engine.collection_view`

```python
def collection_view(self, cid: str) -> dict[str, Any]: ...
```

Винятки в коді методу: `NotFound`.

Код: [engine.py:347](../../../../../services/web-collector/src/jane_web_collector/engine.py#L347).

#### Метод `Engine.acked`

```python
def acked(self, cid: str) -> None: ...
```

Код: [engine.py:390](../../../../../services/web-collector/src/jane_web_collector/engine.py#L390).

#### Метод `Engine.fetch_one`

```python
async def fetch_one(self, payload: dict[str, Any]) -> dict[str, Any]: ...
```

Винятки в коді методу: `ValidationFailed`, `JaneError`, `Forbidden`, `LimitExceeded`.

Код: [engine.py:396](../../../../../services/web-collector/src/jane_web_collector/engine.py#L396).

#### Метод `Engine.capabilities`

```python
def capabilities(self) -> dict[str, Any]: ...
```

Код: [engine.py:532](../../../../../services/web-collector/src/jane_web_collector/engine.py#L532).
