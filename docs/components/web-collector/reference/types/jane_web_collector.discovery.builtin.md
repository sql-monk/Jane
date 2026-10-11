# Модуль `jane_web_collector.discovery.builtin`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/discovery/builtin.py](../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py). Не редагуйте вручну.

Built-in discovery strategies of the core: ``seed_list`` (explicit list / home page) and ``recursive``.

## Класи

### Клас `RecursiveStrategy`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.discovery.builtin` |
| Код | [builtin.py:44](../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L44) |

```python
class RecursiveStrategy: ...
```

Follows links from every fetched HTML page (from any strategy, or from its own ``seeds``).

``link_sources`` chooses which links count (``a_href`` by default); ``follow`` additionally narrows them to matching URLs. Scope, exclusions, robots, dedup, depth and frontier size are the core's job.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `type_name` | `ClassVar[str]` | `'recursive'` | читання |  |

#### Конструктор `RecursiveStrategy.__init__`

```python
def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None: ...
```

Код: [builtin.py:53](../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L53).

#### Метод `RecursiveStrategy.seeds`

```python
async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]: ...
```

Код: [builtin.py:60](../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L60).

#### Метод `RecursiveStrategy.on_fetched`

```python
async def on_fetched(
    self,
    resource: FetchedResource,
    ctx: DiscoveryContext,
) -> AsyncIterator[DiscoveredUrl]: ...
```

Код: [builtin.py:64](../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L64).

#### Метод `RecursiveStrategy.snapshot`

```python
def snapshot(self) -> Mapping[str, Any]: ...
```

Код: [builtin.py:84](../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L84).

#### Метод `RecursiveStrategy.restore`

```python
def restore(self, state: Mapping[str, Any]) -> None: ...
```

Код: [builtin.py:87](../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L87).

### Клас `SeedListStrategy`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.discovery.builtin` |
| Код | [builtin.py:16](../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L16) |

```python
class SeedListStrategy: ...
```

Explicit list of URLs (or just the home page). Seeds have ``depth=0``; no reaction to other pages.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `type_name` | `ClassVar[str]` | `'seed_list'` | читання |  |

#### Конструктор `SeedListStrategy.__init__`

```python
def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None: ...
```

Код: [builtin.py:21](../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L21).

#### Метод `SeedListStrategy.seeds`

```python
async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]: ...
```

Код: [builtin.py:27](../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L27).

#### Метод `SeedListStrategy.on_fetched`

```python
async def on_fetched(
    self,
    resource: FetchedResource,
    ctx: DiscoveryContext,
) -> AsyncIterator[DiscoveredUrl]: ...
```

Код: [builtin.py:31](../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L31).

#### Метод `SeedListStrategy.snapshot`

```python
def snapshot(self) -> Mapping[str, Any]: ...
```

Код: [builtin.py:37](../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L37).

#### Метод `SeedListStrategy.restore`

```python
def restore(self, state: Mapping[str, Any]) -> None: ...
```

Код: [builtin.py:40](../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L40).
