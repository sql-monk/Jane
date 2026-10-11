# Модуль `jane_telegram_collector.engine`

> Згенеровано `scripts/docs_reference.py` з [services/telegram-collector/src/jane_telegram_collector/engine.py](../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py). Не редагуйте вручну.

Service core: collections (start, resume after restart or takeover, cancellation), one-shot fetch, housekeeping.

## Класи

### Клас `Engine`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.engine` |
| Код | [engine.py:55](../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L55) |

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
    factory: ClientFactory,
    schemas: ContractSchemas,
    runner: JobRunner,
    *,
    idempotency: SqliteIdempotencyStore | None = None,
) -> None: ...
```

Код: [engine.py:56](../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L56).

#### Метод `Engine.resolve`

```python
def resolve(
    self,
    source: Mapping[str, Any] | None = None,
    request: Mapping[str, Any] | None = None,
) -> ResolvedLimits[ServiceLimits]: ...
```

Винятки в коді методу: `ValidationFailed`.

Код: [engine.py:99](../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L99).

#### Метод `Engine.start`

```python
async def start(self) -> None: ...
```

Код: [engine.py:113](../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L113).

#### Метод `Engine.stop`

```python
async def stop(self) -> None: ...
```

Код: [engine.py:117](../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L117).

#### Метод `Engine.resume_pending`

```python
async def resume_pending(self) -> list[str]: ...
```

Take over non-terminal collections whose lease expired (after a crash/kill) and continue them.

Код: [engine.py:138](../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L138).

#### Метод `Engine.gc`

```python
def gc(self) -> None: ...
```

Код: [engine.py:169](../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L169).

#### Метод `Engine.account`

```python
def account(self, rules: Mapping[str, Any], pointer: str) -> ResolvedAccount: ...
```

The ``telegram_account`` connection named by the rules (or the configured default), secrets resolved.

Винятки в коді методу: `ValidationFailed`.

Код: [engine.py:216](../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L216).

#### Метод `Engine.start_collection`

```python
async def start_collection(self, payload: dict[str, Any]) -> Job: ...
```

Винятки в коді методу: `ValidationFailed`, `JaneError`.

Код: [engine.py:241](../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L241).

#### Метод `Engine.collection_view`

```python
def collection_view(self, cid: str) -> dict[str, Any]: ...
```

Винятки в коді методу: `NotFound`.

Код: [engine.py:325](../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L325).

#### Метод `Engine.acked`

```python
def acked(self, cid: str) -> None: ...
```

Код: [engine.py:363](../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L363).

#### Метод `Engine.fetch_one`

```python
async def fetch_one(self, payload: dict[str, Any]) -> dict[str, Any]: ...
```

Винятки в коді методу: `ValidationFailed`, `JaneError`.

Код: [engine.py:369](../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L369).

#### Метод `Engine.capabilities`

```python
def capabilities(self) -> dict[str, Any]: ...
```

Код: [engine.py:463](../../../../../services/telegram-collector/src/jane_telegram_collector/engine.py#L463).
