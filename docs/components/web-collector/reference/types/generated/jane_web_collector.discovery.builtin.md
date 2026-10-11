# jane_web_collector.discovery.builtin

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.discovery.builtin.SeedListStrategy](#jane_web_collectordiscoverybuiltinseedliststrategy)
- [jane_web_collector.discovery.builtin.SeedListStrategy.type_name](#jane_web_collectordiscoverybuiltinseedliststrategytype_name)
- [jane_web_collector.discovery.builtin.SeedListStrategy.__init__](#jane_web_collectordiscoverybuiltinseedliststrategy__init__)
- [jane_web_collector.discovery.builtin.SeedListStrategy.config](#jane_web_collectordiscoverybuiltinseedliststrategyconfig)
- [jane_web_collector.discovery.builtin.SeedListStrategy.strategy_id](#jane_web_collectordiscoverybuiltinseedliststrategystrategy_id)
- [jane_web_collector.discovery.builtin.SeedListStrategy.urls](#jane_web_collectordiscoverybuiltinseedliststrategyurls)
- [jane_web_collector.discovery.builtin.SeedListStrategy.priority](#jane_web_collectordiscoverybuiltinseedliststrategypriority)
- [jane_web_collector.discovery.builtin.SeedListStrategy.seeds](#jane_web_collectordiscoverybuiltinseedliststrategyseeds)
- [jane_web_collector.discovery.builtin.SeedListStrategy.on_fetched](#jane_web_collectordiscoverybuiltinseedliststrategyon_fetched)
- [jane_web_collector.discovery.builtin.SeedListStrategy.snapshot](#jane_web_collectordiscoverybuiltinseedliststrategysnapshot)
- [jane_web_collector.discovery.builtin.SeedListStrategy.restore](#jane_web_collectordiscoverybuiltinseedliststrategyrestore)
- [jane_web_collector.discovery.builtin.RecursiveStrategy](#jane_web_collectordiscoverybuiltinrecursivestrategy)
- [jane_web_collector.discovery.builtin.RecursiveStrategy.type_name](#jane_web_collectordiscoverybuiltinrecursivestrategytype_name)
- [jane_web_collector.discovery.builtin.RecursiveStrategy.__init__](#jane_web_collectordiscoverybuiltinrecursivestrategy__init__)
- [jane_web_collector.discovery.builtin.RecursiveStrategy.config](#jane_web_collectordiscoverybuiltinrecursivestrategyconfig)
- [jane_web_collector.discovery.builtin.RecursiveStrategy.strategy_id](#jane_web_collectordiscoverybuiltinrecursivestrategystrategy_id)
- [jane_web_collector.discovery.builtin.RecursiveStrategy.seed_urls](#jane_web_collectordiscoverybuiltinrecursivestrategyseed_urls)
- [jane_web_collector.discovery.builtin.RecursiveStrategy.follow](#jane_web_collectordiscoverybuiltinrecursivestrategyfollow)
- [jane_web_collector.discovery.builtin.RecursiveStrategy.link_sources](#jane_web_collectordiscoverybuiltinrecursivestrategylink_sources)
- [jane_web_collector.discovery.builtin.RecursiveStrategy.seeds](#jane_web_collectordiscoverybuiltinrecursivestrategyseeds)
- [jane_web_collector.discovery.builtin.RecursiveStrategy.on_fetched](#jane_web_collectordiscoverybuiltinrecursivestrategyon_fetched)
- [jane_web_collector.discovery.builtin.RecursiveStrategy.snapshot](#jane_web_collectordiscoverybuiltinrecursivestrategysnapshot)
- [jane_web_collector.discovery.builtin.RecursiveStrategy.restore](#jane_web_collectordiscoverybuiltinrecursivestrategyrestore)

## jane_web_collector.discovery.builtin.SeedListStrategy

**Клас.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:16](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L16).

```python
class SeedListStrategy:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [type_name](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinseedliststrategytype_name) | Поле | ні |
| [__init__](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinseedliststrategy__init__) | Конструктор | ні |
| [config](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinseedliststrategyconfig) | Поле екземпляра | ні |
| [strategy_id](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinseedliststrategystrategy_id) | Поле екземпляра | ні |
| [urls](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinseedliststrategyurls) | Поле екземпляра | ні |
| [priority](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinseedliststrategypriority) | Поле екземпляра | ні |
| [seeds](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinseedliststrategyseeds) | Метод | ні |
| [on_fetched](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinseedliststrategyon_fetched) | Метод | ні |
| [snapshot](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinseedliststrategysnapshot) | Метод | ні |
| [restore](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinseedliststrategyrestore) | Метод | ні |

### Опис із вихідного коду

```text
Explicit list of URLs (or just the home page). Seeds have ``depth=0``; no reaction to other pages.
```

## jane_web_collector.discovery.builtin.SeedListStrategy.type_name

**Поле.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:19](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L19).

```python
type_name: ClassVar[str] = 'seed_list'
```

Доступ: читання — так; запис — так.

## jane_web_collector.discovery.builtin.SeedListStrategy.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:21](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L21).

```python
def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `config` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `strategy_id` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.discovery.builtin.SeedListStrategy.config

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:22](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L22).

```python
self.config = config
```

## jane_web_collector.discovery.builtin.SeedListStrategy.strategy_id

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:23](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L23).

```python
self.strategy_id = strategy_id
```

## jane_web_collector.discovery.builtin.SeedListStrategy.urls

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:24](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L24).

```python
self.urls: list[str] = list(config.get('urls') or [])
```

## jane_web_collector.discovery.builtin.SeedListStrategy.priority

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:25](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L25).

```python
self.priority = int(config.get('priority', 0))
```

## jane_web_collector.discovery.builtin.SeedListStrategy.seeds

**Метод.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:27](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L27).

```python
async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ctx` | `DiscoveryContext` | `—` | positional-or-keyword |

Результат: `AsyncIterator[DiscoveredUrl]`.

## jane_web_collector.discovery.builtin.SeedListStrategy.on_fetched

**Метод.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:31](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L31).

```python
async def on_fetched(self, resource: FetchedResource, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `resource` | `FetchedResource` | `—` | positional-or-keyword |
| `ctx` | `DiscoveryContext` | `—` | positional-or-keyword |

Результат: `AsyncIterator[DiscoveredUrl]`.

## jane_web_collector.discovery.builtin.SeedListStrategy.snapshot

**Метод.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:37](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L37).

```python
def snapshot(self) -> Mapping[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Mapping[str, Any]`.

## jane_web_collector.discovery.builtin.SeedListStrategy.restore

**Метод.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:40](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L40).

```python
def restore(self, state: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.discovery.builtin.RecursiveStrategy

**Клас.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:44](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L44).

```python
class RecursiveStrategy:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [type_name](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinrecursivestrategytype_name) | Поле | ні |
| [__init__](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinrecursivestrategy__init__) | Конструктор | ні |
| [config](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinrecursivestrategyconfig) | Поле екземпляра | ні |
| [strategy_id](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinrecursivestrategystrategy_id) | Поле екземпляра | ні |
| [seed_urls](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinrecursivestrategyseed_urls) | Поле екземпляра | ні |
| [follow](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinrecursivestrategyfollow) | Поле екземпляра | ні |
| [link_sources](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinrecursivestrategylink_sources) | Поле екземпляра | ні |
| [seeds](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinrecursivestrategyseeds) | Метод | ні |
| [on_fetched](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinrecursivestrategyon_fetched) | Метод | ні |
| [snapshot](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinrecursivestrategysnapshot) | Метод | ні |
| [restore](jane_web_collector.discovery.builtin.md#jane_web_collectordiscoverybuiltinrecursivestrategyrestore) | Метод | ні |

### Опис із вихідного коду

```text
Follows links from every fetched HTML page (from any strategy, or from its own ``seeds``).

``link_sources`` chooses which links count (``a_href`` by default); ``follow`` additionally narrows
them to matching URLs. Scope, exclusions, robots, dedup, depth and frontier size are the core's job.
```

## jane_web_collector.discovery.builtin.RecursiveStrategy.type_name

**Поле.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:51](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L51).

```python
type_name: ClassVar[str] = 'recursive'
```

Доступ: читання — так; запис — так.

## jane_web_collector.discovery.builtin.RecursiveStrategy.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:53](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L53).

```python
def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `config` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `strategy_id` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.discovery.builtin.RecursiveStrategy.config

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:54](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L54).

```python
self.config = config
```

## jane_web_collector.discovery.builtin.RecursiveStrategy.strategy_id

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:55](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L55).

```python
self.strategy_id = strategy_id
```

## jane_web_collector.discovery.builtin.RecursiveStrategy.seed_urls

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:56](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L56).

```python
self.seed_urls: list[str] = list(config.get('seeds') or [])
```

## jane_web_collector.discovery.builtin.RecursiveStrategy.follow

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:57](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L57).

```python
self.follow = compile_patterns(config.get('follow'))
```

## jane_web_collector.discovery.builtin.RecursiveStrategy.link_sources

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:58](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L58).

```python
self.link_sources: tuple[str, ...] = tuple(config.get('link_sources') or ('a_href',))
```

## jane_web_collector.discovery.builtin.RecursiveStrategy.seeds

**Метод.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:60](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L60).

```python
async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ctx` | `DiscoveryContext` | `—` | positional-or-keyword |

Результат: `AsyncIterator[DiscoveredUrl]`.

## jane_web_collector.discovery.builtin.RecursiveStrategy.on_fetched

**Метод.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:64](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L64).

```python
async def on_fetched(self, resource: FetchedResource, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `resource` | `FetchedResource` | `—` | positional-or-keyword |
| `ctx` | `DiscoveryContext` | `—` | positional-or-keyword |

Результат: `AsyncIterator[DiscoveredUrl]`.

## jane_web_collector.discovery.builtin.RecursiveStrategy.snapshot

**Метод.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:84](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L84).

```python
def snapshot(self) -> Mapping[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Mapping[str, Any]`.

## jane_web_collector.discovery.builtin.RecursiveStrategy.restore

**Метод.** Код: [services/web-collector/src/jane_web_collector/discovery/builtin.py:87](../../../../../../services/web-collector/src/jane_web_collector/discovery/builtin.py#L87).

```python
def restore(self, state: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.
