# discovery.listing

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [discovery.listing.ListingStrategy](#discoverylistinglistingstrategy)
- [discovery.listing.ListingStrategy.type_name](#discoverylistinglistingstrategytype_name)
- [discovery.listing.ListingStrategy.__init__](#discoverylistinglistingstrategy__init__)
- [discovery.listing.ListingStrategy.config](#discoverylistinglistingstrategyconfig)
- [discovery.listing.ListingStrategy.strategy_id](#discoverylistinglistingstrategystrategy_id)
- [discovery.listing.ListingStrategy.start_urls](#discoverylistinglistingstrategystart_urls)
- [discovery.listing.ListingStrategy.item_links](#discoverylistinglistingstrategyitem_links)
- [discovery.listing.ListingStrategy.next_link](#discoverylistinglistingstrategynext_link)
- [discovery.listing.ListingStrategy.page_param](#discoverylistinglistingstrategypage_param)
- [discovery.listing.ListingStrategy.page_start](#discoverylistinglistingstrategypage_start)
- [discovery.listing.ListingStrategy.page_step](#discoverylistinglistingstrategypage_step)
- [discovery.listing.ListingStrategy.stop_when_empty](#discoverylistinglistingstrategystop_when_empty)
- [discovery.listing.ListingStrategy.pages](#discoverylistinglistingstrategypages)
- [discovery.listing.ListingStrategy.stats](#discoverylistinglistingstrategystats)
- [discovery.listing.ListingStrategy.seeds](#discoverylistinglistingstrategyseeds)
- [discovery.listing.ListingStrategy.refresh_on_revisit](#discoverylistinglistingstrategyrefresh_on_revisit)
- [discovery.listing.ListingStrategy.on_fetched](#discoverylistinglistingstrategyon_fetched)
- [discovery.listing.ListingStrategy.snapshot](#discoverylistinglistingstrategysnapshot)
- [discovery.listing.ListingStrategy.restore](#discoverylistinglistingstrategyrestore)

## discovery.listing.ListingStrategy

**Клас.** Код: [services/web-collector/strategies/discovery/listing.py:65](../../../../../../services/web-collector/strategies/discovery/listing.py#L65).

```python
class ListingStrategy:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [type_name](discovery.listing.md#discoverylistinglistingstrategytype_name) | Поле | ні |
| [__init__](discovery.listing.md#discoverylistinglistingstrategy__init__) | Конструктор | ні |
| [config](discovery.listing.md#discoverylistinglistingstrategyconfig) | Поле екземпляра | ні |
| [strategy_id](discovery.listing.md#discoverylistinglistingstrategystrategy_id) | Поле екземпляра | ні |
| [start_urls](discovery.listing.md#discoverylistinglistingstrategystart_urls) | Поле екземпляра | ні |
| [item_links](discovery.listing.md#discoverylistinglistingstrategyitem_links) | Поле екземпляра | ні |
| [next_link](discovery.listing.md#discoverylistinglistingstrategynext_link) | Поле екземпляра | ні |
| [page_param](discovery.listing.md#discoverylistinglistingstrategypage_param) | Поле екземпляра | ні |
| [page_start](discovery.listing.md#discoverylistinglistingstrategypage_start) | Поле екземпляра | ні |
| [page_step](discovery.listing.md#discoverylistinglistingstrategypage_step) | Поле екземпляра | ні |
| [stop_when_empty](discovery.listing.md#discoverylistinglistingstrategystop_when_empty) | Поле екземпляра | ні |
| [pages](discovery.listing.md#discoverylistinglistingstrategypages) | Поле екземпляра | ні |
| [stats](discovery.listing.md#discoverylistinglistingstrategystats) | Поле екземпляра | ні |
| [seeds](discovery.listing.md#discoverylistinglistingstrategyseeds) | Метод | ні |
| [refresh_on_revisit](discovery.listing.md#discoverylistinglistingstrategyrefresh_on_revisit) | Метод | ні |
| [on_fetched](discovery.listing.md#discoverylistinglistingstrategyon_fetched) | Метод | ні |
| [snapshot](discovery.listing.md#discoverylistinglistingstrategysnapshot) | Метод | ні |
| [restore](discovery.listing.md#discoverylistinglistingstrategyrestore) | Метод | ні |

## discovery.listing.ListingStrategy.type_name

**Поле.** Код: [services/web-collector/strategies/discovery/listing.py:66](../../../../../../services/web-collector/strategies/discovery/listing.py#L66).

```python
type_name: ClassVar[str] = 'listing'
```

Доступ: читання — так; запис — так.

## discovery.listing.ListingStrategy.__init__

**Конструктор.** Код: [services/web-collector/strategies/discovery/listing.py:68](../../../../../../services/web-collector/strategies/discovery/listing.py#L68).

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

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

## discovery.listing.ListingStrategy.config

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/listing.py:69](../../../../../../services/web-collector/strategies/discovery/listing.py#L69).

```python
self.config = config
```

## discovery.listing.ListingStrategy.strategy_id

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/listing.py:70](../../../../../../services/web-collector/strategies/discovery/listing.py#L70).

```python
self.strategy_id = strategy_id
```

## discovery.listing.ListingStrategy.start_urls

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/listing.py:71](../../../../../../services/web-collector/strategies/discovery/listing.py#L71).

```python
self.start_urls: list[str] = [u for u in config.get('start_urls') or [] if isinstance(u, str)]
```

## discovery.listing.ListingStrategy.item_links

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/listing.py:78](../../../../../../services/web-collector/strategies/discovery/listing.py#L78).

```python
self.item_links = _selector(config.get('item_links'))
```

## discovery.listing.ListingStrategy.next_link

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/listing.py:79](../../../../../../services/web-collector/strategies/discovery/listing.py#L79).

```python
self.next_link = _selector(config.get('next_page'), LinkSelector(value='next', type='rel'))
```

## discovery.listing.ListingStrategy.page_param

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/listing.py:81](../../../../../../services/web-collector/strategies/discovery/listing.py#L81).

```python
self.page_param: str | None = str(page_param['name']) if page_param else None
```

## discovery.listing.ListingStrategy.page_start

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/listing.py:82](../../../../../../services/web-collector/strategies/discovery/listing.py#L82).

```python
self.page_start = int(page_param.get('start', 1))
```

## discovery.listing.ListingStrategy.page_step

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/listing.py:83](../../../../../../services/web-collector/strategies/discovery/listing.py#L83).

```python
self.page_step = int(page_param.get('step', 1))
```

## discovery.listing.ListingStrategy.stop_when_empty

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/listing.py:84](../../../../../../services/web-collector/strategies/discovery/listing.py#L84).

```python
self.stop_when_empty = bool(page_param.get('stop_when_empty', True))
```

## discovery.listing.ListingStrategy.pages

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/listing.py:87](../../../../../../services/web-collector/strategies/discovery/listing.py#L87).

```python
self.pages: dict[str, dict[str, Any]] = {}
```

## discovery.listing.ListingStrategy.stats

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/listing.py:89](../../../../../../services/web-collector/strategies/discovery/listing.py#L89).

```python
self.stats: dict[str, int] = {}
```

## discovery.listing.ListingStrategy.seeds

**Метод.** Код: [services/web-collector/strategies/discovery/listing.py:92](../../../../../../services/web-collector/strategies/discovery/listing.py#L92).

```python
async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ctx` | `DiscoveryContext` | `—` | positional-or-keyword |

Результат: `AsyncIterator[DiscoveredUrl]`.

## discovery.listing.ListingStrategy.refresh_on_revisit

**Метод.** Код: [services/web-collector/strategies/discovery/listing.py:101](../../../../../../services/web-collector/strategies/discovery/listing.py#L101).

```python
def refresh_on_revisit(self, url: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
``RefreshingStrategy``: a listing page is read again in every run (new items appear on known pages).
```

## discovery.listing.ListingStrategy.on_fetched

**Метод.** Код: [services/web-collector/strategies/discovery/listing.py:115](../../../../../../services/web-collector/strategies/discovery/listing.py#L115).

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

## discovery.listing.ListingStrategy.snapshot

**Метод.** Код: [services/web-collector/strategies/discovery/listing.py:186](../../../../../../services/web-collector/strategies/discovery/listing.py#L186).

```python
def snapshot(self) -> Mapping[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Mapping[str, Any]`.

## discovery.listing.ListingStrategy.restore

**Метод.** Код: [services/web-collector/strategies/discovery/listing.py:191](../../../../../../services/web-collector/strategies/discovery/listing.py#L191).

```python
def restore(self, state: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.
