# discovery.api_feed

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [discovery.api_feed.UnsupportedConfig](#discoveryapi_feedunsupportedconfig)
- [discovery.api_feed.ApiFeedStrategy](#discoveryapi_feedapifeedstrategy)
- [discovery.api_feed.ApiFeedStrategy.type_name](#discoveryapi_feedapifeedstrategytype_name)
- [discovery.api_feed.ApiFeedStrategy.__init__](#discoveryapi_feedapifeedstrategy__init__)
- [discovery.api_feed.ApiFeedStrategy.config](#discoveryapi_feedapifeedstrategyconfig)
- [discovery.api_feed.ApiFeedStrategy.strategy_id](#discoveryapi_feedapifeedstrategystrategy_id)
- [discovery.api_feed.ApiFeedStrategy.method](#discoveryapi_feedapifeedstrategymethod)
- [discovery.api_feed.ApiFeedStrategy.body](#discoveryapi_feedapifeedstrategybody)
- [discovery.api_feed.ApiFeedStrategy.emit_items](#discoveryapi_feedapifeedstrategyemit_items)
- [discovery.api_feed.ApiFeedStrategy.url](#discoveryapi_feedapifeedstrategyurl)
- [discovery.api_feed.ApiFeedStrategy.items_path](#discoveryapi_feedapifeedstrategyitems_path)
- [discovery.api_feed.ApiFeedStrategy.url_path](#discoveryapi_feedapifeedstrategyurl_path)
- [discovery.api_feed.ApiFeedStrategy.lastmod_path](#discoveryapi_feedapifeedstrategylastmod_path)
- [discovery.api_feed.ApiFeedStrategy.pagination](#discoveryapi_feedapifeedstrategypagination)
- [discovery.api_feed.ApiFeedStrategy.next_url_path](#discoveryapi_feedapifeedstrategynext_url_path)
- [discovery.api_feed.ApiFeedStrategy.cursor_path](#discoveryapi_feedapifeedstrategycursor_path)
- [discovery.api_feed.ApiFeedStrategy.cursor_param](#discoveryapi_feedapifeedstrategycursor_param)
- [discovery.api_feed.ApiFeedStrategy.page_param](#discoveryapi_feedapifeedstrategypage_param)
- [discovery.api_feed.ApiFeedStrategy.stats](#discoveryapi_feedapifeedstrategystats)
- [discovery.api_feed.ApiFeedStrategy.items](#discoveryapi_feedapifeedstrategyitems)
- [discovery.api_feed.ApiFeedStrategy.next_page](#discoveryapi_feedapifeedstrategynext_page)
- [discovery.api_feed.ApiFeedStrategy.seeds](#discoveryapi_feedapifeedstrategyseeds)
- [discovery.api_feed.ApiFeedStrategy.on_fetched](#discoveryapi_feedapifeedstrategyon_fetched)
- [discovery.api_feed.ApiFeedStrategy.snapshot](#discoveryapi_feedapifeedstrategysnapshot)
- [discovery.api_feed.ApiFeedStrategy.restore](#discoveryapi_feedapifeedstrategyrestore)

## discovery.api_feed.UnsupportedConfig

**Клас.** Код: [services/web-collector/strategies/discovery/api_feed.py:55](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L55).

```python
class UnsupportedConfig(ValueError):
```

Базові типи / інтерфейси: `ValueError`.

### Опис із вихідного коду

```text
Valid by the schema, but not executable by this collector.
```

## discovery.api_feed.ApiFeedStrategy

**Клас.** Код: [services/web-collector/strategies/discovery/api_feed.py:66](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L66).

```python
class ApiFeedStrategy:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [type_name](discovery.api_feed.md#discoveryapi_feedapifeedstrategytype_name) | Поле | ні |
| [__init__](discovery.api_feed.md#discoveryapi_feedapifeedstrategy__init__) | Конструктор | ні |
| [config](discovery.api_feed.md#discoveryapi_feedapifeedstrategyconfig) | Поле екземпляра | ні |
| [strategy_id](discovery.api_feed.md#discoveryapi_feedapifeedstrategystrategy_id) | Поле екземпляра | ні |
| [method](discovery.api_feed.md#discoveryapi_feedapifeedstrategymethod) | Поле екземпляра | ні |
| [body](discovery.api_feed.md#discoveryapi_feedapifeedstrategybody) | Поле екземпляра | ні |
| [emit_items](discovery.api_feed.md#discoveryapi_feedapifeedstrategyemit_items) | Поле екземпляра | ні |
| [url](discovery.api_feed.md#discoveryapi_feedapifeedstrategyurl) | Поле екземпляра | ні |
| [items_path](discovery.api_feed.md#discoveryapi_feedapifeedstrategyitems_path) | Поле екземпляра | ні |
| [url_path](discovery.api_feed.md#discoveryapi_feedapifeedstrategyurl_path) | Поле екземпляра | ні |
| [lastmod_path](discovery.api_feed.md#discoveryapi_feedapifeedstrategylastmod_path) | Поле екземпляра | ні |
| [pagination](discovery.api_feed.md#discoveryapi_feedapifeedstrategypagination) | Поле екземпляра | ні |
| [next_url_path](discovery.api_feed.md#discoveryapi_feedapifeedstrategynext_url_path) | Поле екземпляра | ні |
| [cursor_path](discovery.api_feed.md#discoveryapi_feedapifeedstrategycursor_path) | Поле екземпляра | ні |
| [cursor_param](discovery.api_feed.md#discoveryapi_feedapifeedstrategycursor_param) | Поле екземпляра | ні |
| [page_param](discovery.api_feed.md#discoveryapi_feedapifeedstrategypage_param) | Поле екземпляра | ні |
| [stats](discovery.api_feed.md#discoveryapi_feedapifeedstrategystats) | Поле екземпляра | ні |
| [items](discovery.api_feed.md#discoveryapi_feedapifeedstrategyitems) | Метод | ні |
| [next_page](discovery.api_feed.md#discoveryapi_feedapifeedstrategynext_page) | Метод | ні |
| [seeds](discovery.api_feed.md#discoveryapi_feedapifeedstrategyseeds) | Метод | ні |
| [on_fetched](discovery.api_feed.md#discoveryapi_feedapifeedstrategyon_fetched) | Метод | ні |
| [snapshot](discovery.api_feed.md#discoveryapi_feedapifeedstrategysnapshot) | Метод | ні |
| [restore](discovery.api_feed.md#discoveryapi_feedapifeedstrategyrestore) | Метод | ні |

## discovery.api_feed.ApiFeedStrategy.type_name

**Поле.** Код: [services/web-collector/strategies/discovery/api_feed.py:67](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L67).

```python
type_name: ClassVar[str] = 'api_feed'
```

Доступ: читання — так; запис — так.

## discovery.api_feed.ApiFeedStrategy.__init__

**Конструктор.** Код: [services/web-collector/strategies/discovery/api_feed.py:69](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L69).

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

Явні `raise` у тілі: `UnsupportedConfig`, `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

## discovery.api_feed.ApiFeedStrategy.config

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/api_feed.py:70](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L70).

```python
self.config = config
```

## discovery.api_feed.ApiFeedStrategy.strategy_id

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/api_feed.py:71](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L71).

```python
self.strategy_id = strategy_id
```

## discovery.api_feed.ApiFeedStrategy.method

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/api_feed.py:72](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L72).

```python
self.method = str(config.get('method', 'GET')).upper()
```

## discovery.api_feed.ApiFeedStrategy.body

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/api_feed.py:75](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L75).

```python
self.body: Any = config.get('body')
```

## discovery.api_feed.ApiFeedStrategy.emit_items

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/api_feed.py:76](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L76).

```python
self.emit_items = bool(config.get('emit_items_as_materials', False))
```

## discovery.api_feed.ApiFeedStrategy.url

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/api_feed.py:77](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L77).

```python
self.url: str = str(config['url'])
```

## discovery.api_feed.ApiFeedStrategy.items_path

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/api_feed.py:78](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L78).

```python
self.items_path = JsonPath(str(config['items_path']))
```

## discovery.api_feed.ApiFeedStrategy.url_path

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/api_feed.py:79](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L79).

```python
self.url_path = JsonPath(str(config['url_path']))
```

## discovery.api_feed.ApiFeedStrategy.lastmod_path

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/api_feed.py:80](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L80).

```python
self.lastmod_path = JsonPath(str(config['lastmod_path'])) if config.get('lastmod_path') else None
```

## discovery.api_feed.ApiFeedStrategy.pagination

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/api_feed.py:82](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L82).

```python
self.pagination = str(pagination.get('type', 'none'))
```

## discovery.api_feed.ApiFeedStrategy.next_url_path

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/api_feed.py:91](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L91).

```python
self.next_url_path = JsonPath(pagination['next_url_path']) if self.pagination == 'next_url' else None
```

## discovery.api_feed.ApiFeedStrategy.cursor_path

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/api_feed.py:92](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L92).

```python
self.cursor_path = JsonPath(pagination['cursor_path']) if self.pagination == 'cursor' else None
```

## discovery.api_feed.ApiFeedStrategy.cursor_param

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/api_feed.py:93](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L93).

```python
self.cursor_param: str = str(pagination.get('cursor_param') or '')
```

## discovery.api_feed.ApiFeedStrategy.page_param

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/api_feed.py:94](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L94).

```python
self.page_param: str = str(pagination.get('page_param') or '')
```

## discovery.api_feed.ApiFeedStrategy.stats

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/api_feed.py:95](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L95).

```python
self.stats: dict[str, int] = {}
```

## discovery.api_feed.ApiFeedStrategy.items

**Метод.** Код: [services/web-collector/strategies/discovery/api_feed.py:97](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L97).

```python
def items(self, document: Any) -> list[Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `document` | `Any` | `—` | positional-or-keyword |

Результат: `list[Any]`.

## discovery.api_feed.ApiFeedStrategy.next_page

**Метод.** Код: [services/web-collector/strategies/discovery/api_feed.py:103](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L103).

```python
def next_page(self, document: Any, current: str, item_count: int, cursors: set[str]) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `document` | `Any` | `—` | positional-or-keyword |
| `current` | `str` | `—` | positional-or-keyword |
| `item_count` | `int` | `—` | positional-or-keyword |
| `cursors` | `set[str]` | `—` | positional-or-keyword |

Результат: `str | None`.

### Опис із вихідного коду

```text
URL of the next page by the configured pagination, or ``None`` to stop.
```

## discovery.api_feed.ApiFeedStrategy.seeds

**Метод.** Код: [services/web-collector/strategies/discovery/api_feed.py:122](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L122).

```python
async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ctx` | `DiscoveryContext` | `—` | positional-or-keyword |

Результат: `AsyncIterator[DiscoveredUrl]`.

## discovery.api_feed.ApiFeedStrategy.on_fetched

**Метод.** Код: [services/web-collector/strategies/discovery/api_feed.py:229](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L229).

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

## discovery.api_feed.ApiFeedStrategy.snapshot

**Метод.** Код: [services/web-collector/strategies/discovery/api_feed.py:235](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L235).

```python
def snapshot(self) -> Mapping[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Mapping[str, Any]`.

## discovery.api_feed.ApiFeedStrategy.restore

**Метод.** Код: [services/web-collector/strategies/discovery/api_feed.py:238](../../../../../../services/web-collector/strategies/discovery/api_feed.py#L238).

```python
def restore(self, state: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.
