# Модуль `jane_web_collector.discovery.registry`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/discovery/registry.py](../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py). Не редагуйте вручну.

Strategy registry (``jane_contracts.discovery.StrategyRegistry``) and the plug-in points for WP-03.

Sources, in this order (a later source may not redefine an existing ``type_name``):

1. built-ins of the core: ``seed_list``, ``recursive``;
2. the WP-03 package directory ``services/web-collector/strategies/discovery/`` (override: ``JANE_WEB_COLLECTOR_DISCOVERY_PATH``): imported as the package ``jane_web_collector_discovery`` (relative imports inside it work) and its ``STRATEGIES: list[type[DiscoveryStrategy]]`` is registered;
3. entry points of the group ``jane.web_collector.strategies`` (a class or a list of classes) for strategy packages installed next to the service.

``llm_explore`` is reserved and never supported by the collector (ADR-0010).

## Класи

### Клас `Registry`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.discovery.registry` |
| Код | [registry.py:76](../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L76) |

```python
class Registry: ...
```

``StrategyRegistry`` owned by WP-02.

#### Конструктор `Registry.__init__`

```python
def __init__(self) -> None: ...
```

Код: [registry.py:79](../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L79).

#### Метод `Registry.register`

```python
def register(self, strategy: type[DiscoveryStrategy], origin: str = 'code') -> None: ...
```

Винятки в коді методу: `TypeError`, `ValueError`.

Код: [registry.py:84](../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L84).

#### Метод `Registry.get`

```python
def get(self, type_name: str) -> type[DiscoveryStrategy]: ...
```

Код: [registry.py:100](../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L100).

#### Метод `Registry.types`

```python
def types(self) -> Sequence[str]: ...
```

Код: [registry.py:103](../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L103).

#### Метод `Registry.supported`

```python
def supported(self, type_name: str) -> bool: ...
```

Код: [registry.py:106](../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L106).

#### Метод `Registry.default`

```python
@classmethod
def default(
    cls,
    discovery_path: Path | None = None,
    *,
    use_entry_points: bool = True,
) -> Registry: ...
```

Код: [registry.py:118](../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L118).

## Функції

### Функція `default_discovery_path`

```python
def default_discovery_path() -> Path: ...
```

``services/web-collector/strategies/discovery`` next to ``src/`` (editable/dev checkout).

Код: [registry.py:47](../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L47).

### Функція `load_discovery_package`

```python
def load_discovery_package(path: Path) -> ModuleType | None: ...
```

Import the WP-03 package at ``path`` (a directory with ``__init__.py``) as ``jane_web_collector_discovery``.

Код: [registry.py:52](../../../../../services/web-collector/src/jane_web_collector/discovery/registry.py#L52).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `DISCOVERY_MODULE` | — | `'jane_web_collector_discovery'` |  |
| `ENTRY_POINT_GROUP` | — | `'jane.web_collector.strategies'` |  |
| `RESERVED_TYPES` | — | `frozenset({'llm_explore'})` | Valid in CollectorRules but not executed by the collector in v1 (ADR-0010). |
