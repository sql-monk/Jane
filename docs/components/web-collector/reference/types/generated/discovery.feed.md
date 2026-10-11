# discovery.feed

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [discovery.feed.FEED_AUTODISCOVERY_XPATH](#discoveryfeedfeed_autodiscovery_xpath)
- [discovery.feed.FeedEntry](#discoveryfeedfeedentry)
- [discovery.feed.FeedEntry.__init__](#discoveryfeedfeedentry__init__)
- [discovery.feed.FeedEntry.link](#discoveryfeedfeedentrylink)
- [discovery.feed.FeedEntry.lastmod](#discoveryfeedfeedentrylastmod)
- [discovery.feed.parse_feed](#discoveryfeedparse_feed)
- [discovery.feed.parse_feed_bytes](#discoveryfeedparse_feed_bytes)
- [discovery.feed.FeedStrategy](#discoveryfeedfeedstrategy)
- [discovery.feed.FeedStrategy.type_name](#discoveryfeedfeedstrategytype_name)
- [discovery.feed.FeedStrategy.__init__](#discoveryfeedfeedstrategy__init__)
- [discovery.feed.FeedStrategy.config](#discoveryfeedfeedstrategyconfig)
- [discovery.feed.FeedStrategy.strategy_id](#discoveryfeedfeedstrategystrategy_id)
- [discovery.feed.FeedStrategy.urls](#discoveryfeedfeedstrategyurls)
- [discovery.feed.FeedStrategy.autodiscover](#discoveryfeedfeedstrategyautodiscover)
- [discovery.feed.FeedStrategy.stats](#discoveryfeedfeedstrategystats)
- [discovery.feed.FeedStrategy.seeds](#discoveryfeedfeedstrategyseeds)
- [discovery.feed.FeedStrategy.on_fetched](#discoveryfeedfeedstrategyon_fetched)
- [discovery.feed.FeedStrategy.snapshot](#discoveryfeedfeedstrategysnapshot)
- [discovery.feed.FeedStrategy.restore](#discoveryfeedfeedstrategyrestore)

## discovery.feed.FEED_AUTODISCOVERY_XPATH

**Константа.** Код: [services/web-collector/strategies/discovery/feed.py:44](../../../../../../services/web-collector/strategies/discovery/feed.py#L44).

```python
FEED_AUTODISCOVERY_XPATH = f"//link[@href][contains(concat(' ', {_LOWER.format('normalize-space(@rel)')}, ' '), ' alternate ')][starts-with({_TYPE}, 'application/rss+xml') or starts-with({_TYPE}, 'application/atom+xml') or starts-with({_TYPE}, 'application/rdf+xml')]/@href"
```

### Опис із вихідного коду

```text
``<link rel="alternate">`` elements of RSS/Atom/RDF type (case-insensitive); yields their ``href``.
```

## discovery.feed.FeedEntry

**Клас.** Код: [services/web-collector/strategies/discovery/feed.py:54](../../../../../../services/web-collector/strategies/discovery/feed.py#L54).

```python
class FeedEntry:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [link](discovery.feed.md#discoveryfeedfeedentrylink) | Поле | ні |
| [lastmod](discovery.feed.md#discoveryfeedfeedentrylastmod) | Поле | ні |
| [__init__](discovery.feed.md#discoveryfeedfeedentry__init__) | Конструктор dataclass | ні |

## discovery.feed.FeedEntry.__init__

**Конструктор dataclass.** Код: [services/web-collector/strategies/discovery/feed.py:54](../../../../../../services/web-collector/strategies/discovery/feed.py#L54).

```python
def __init__(self, link: str, lastmod: datetime | None) -> None:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `link` | `str` | `—` | positional-or-keyword |
| `lastmod` | `datetime \| None` | `—` | positional-or-keyword |

Результат: `None`.

## discovery.feed.FeedEntry.link

**Поле.** Код: [services/web-collector/strategies/discovery/feed.py:55](../../../../../../services/web-collector/strategies/discovery/feed.py#L55).

```python
link: str
```

Доступ: читання — так; запис — ні.

## discovery.feed.FeedEntry.lastmod

**Поле.** Код: [services/web-collector/strategies/discovery/feed.py:56](../../../../../../services/web-collector/strategies/discovery/feed.py#L56).

```python
lastmod: datetime | None
```

Доступ: читання — так; запис — ні.

## discovery.feed.parse_feed

**Функція.** Код: [services/web-collector/strategies/discovery/feed.py:84](../../../../../../services/web-collector/strategies/discovery/feed.py#L84).

```python
def parse_feed(root: Any, base: str, max_entries: int) -> tuple[list[FeedEntry], int]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `root` | `Any` | `—` | positional-or-keyword |
| `base` | `str` | `—` | positional-or-keyword |
| `max_entries` | `int` | `—` | positional-or-keyword |

Результат: `tuple[list[FeedEntry], int]`.

### Опис із вихідного коду

```text
Entries of an RSS/RDF/Atom document (already parsed); returns ``(entries, dropped_over_limit)``.
```

## discovery.feed.parse_feed_bytes

**Функція.** Код: [services/web-collector/strategies/discovery/feed.py:113](../../../../../../services/web-collector/strategies/discovery/feed.py#L113).

```python
def parse_feed_bytes(body: bytes, base: str, *, max_bytes: int, max_entries: int) -> tuple[list[FeedEntry], int]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `body` | `bytes` | `—` | positional-or-keyword |
| `base` | `str` | `—` | positional-or-keyword |
| `max_bytes` | `int` | `—` | keyword-only |
| `max_entries` | `int` | `—` | keyword-only |

Результат: `tuple[list[FeedEntry], int]`.

### Опис із вихідного коду

```text
Decode (gzip up to ``max_bytes``) and parse a feed; ``([], 0)`` if the body is not a feed.
```

## discovery.feed.FeedStrategy

**Клас.** Код: [services/web-collector/strategies/discovery/feed.py:124](../../../../../../services/web-collector/strategies/discovery/feed.py#L124).

```python
class FeedStrategy:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [type_name](discovery.feed.md#discoveryfeedfeedstrategytype_name) | Поле | ні |
| [__init__](discovery.feed.md#discoveryfeedfeedstrategy__init__) | Конструктор | ні |
| [config](discovery.feed.md#discoveryfeedfeedstrategyconfig) | Поле екземпляра | ні |
| [strategy_id](discovery.feed.md#discoveryfeedfeedstrategystrategy_id) | Поле екземпляра | ні |
| [urls](discovery.feed.md#discoveryfeedfeedstrategyurls) | Поле екземпляра | ні |
| [autodiscover](discovery.feed.md#discoveryfeedfeedstrategyautodiscover) | Поле екземпляра | ні |
| [stats](discovery.feed.md#discoveryfeedfeedstrategystats) | Поле екземпляра | ні |
| [seeds](discovery.feed.md#discoveryfeedfeedstrategyseeds) | Метод | ні |
| [on_fetched](discovery.feed.md#discoveryfeedfeedstrategyon_fetched) | Метод | ні |
| [snapshot](discovery.feed.md#discoveryfeedfeedstrategysnapshot) | Метод | ні |
| [restore](discovery.feed.md#discoveryfeedfeedstrategyrestore) | Метод | ні |

### Опис із вихідного коду

```text
RSS/Atom feeds (``urls``) plus feed autodiscovery on seed pages.
```

## discovery.feed.FeedStrategy.type_name

**Поле.** Код: [services/web-collector/strategies/discovery/feed.py:127](../../../../../../services/web-collector/strategies/discovery/feed.py#L127).

```python
type_name: ClassVar[str] = 'feed'
```

Доступ: читання — так; запис — так.

## discovery.feed.FeedStrategy.__init__

**Конструктор.** Код: [services/web-collector/strategies/discovery/feed.py:129](../../../../../../services/web-collector/strategies/discovery/feed.py#L129).

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

## discovery.feed.FeedStrategy.config

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/feed.py:130](../../../../../../services/web-collector/strategies/discovery/feed.py#L130).

```python
self.config = config
```

## discovery.feed.FeedStrategy.strategy_id

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/feed.py:131](../../../../../../services/web-collector/strategies/discovery/feed.py#L131).

```python
self.strategy_id = strategy_id
```

## discovery.feed.FeedStrategy.urls

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/feed.py:132](../../../../../../services/web-collector/strategies/discovery/feed.py#L132).

```python
self.urls: list[str] = [u for u in config.get('urls') or [] if isinstance(u, str)]
```

## discovery.feed.FeedStrategy.autodiscover

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/feed.py:133](../../../../../../services/web-collector/strategies/discovery/feed.py#L133).

```python
self.autodiscover = bool(config.get('autodiscover', True))
```

## discovery.feed.FeedStrategy.stats

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/feed.py:134](../../../../../../services/web-collector/strategies/discovery/feed.py#L134).

```python
self.stats: dict[str, int] = {}
```

## discovery.feed.FeedStrategy.seeds

**Метод.** Код: [services/web-collector/strategies/discovery/feed.py:137](../../../../../../services/web-collector/strategies/discovery/feed.py#L137).

```python
async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ctx` | `DiscoveryContext` | `—` | positional-or-keyword |

Результат: `AsyncIterator[DiscoveredUrl]`.

## discovery.feed.FeedStrategy.on_fetched

**Метод.** Код: [services/web-collector/strategies/discovery/feed.py:148](../../../../../../services/web-collector/strategies/discovery/feed.py#L148).

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

### Опис із вихідного коду

```text
Autodiscovery on seed pages found by other strategies (HTML, depth 0).
```

## discovery.feed.FeedStrategy.snapshot

**Метод.** Код: [services/web-collector/strategies/discovery/feed.py:224](../../../../../../services/web-collector/strategies/discovery/feed.py#L224).

```python
def snapshot(self) -> Mapping[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Mapping[str, Any]`.

## discovery.feed.FeedStrategy.restore

**Метод.** Код: [services/web-collector/strategies/discovery/feed.py:227](../../../../../../services/web-collector/strategies/discovery/feed.py#L227).

```python
def restore(self, state: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.
