# discovery.sitemap

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [discovery.sitemap.SitemapEntry](#discoverysitemapsitemapentry)
- [discovery.sitemap.SitemapEntry.__init__](#discoverysitemapsitemapentry__init__)
- [discovery.sitemap.SitemapEntry.loc](#discoverysitemapsitemapentryloc)
- [discovery.sitemap.SitemapEntry.lastmod](#discoverysitemapsitemapentrylastmod)
- [discovery.sitemap.SitemapDocument](#discoverysitemapsitemapdocument)
- [discovery.sitemap.SitemapDocument.__init__](#discoverysitemapsitemapdocument__init__)
- [discovery.sitemap.SitemapDocument.kind](#discoverysitemapsitemapdocumentkind)
- [discovery.sitemap.SitemapDocument.urls](#discoverysitemapsitemapdocumenturls)
- [discovery.sitemap.SitemapDocument.sitemaps](#discoverysitemapsitemapdocumentsitemaps)
- [discovery.sitemap.SitemapDocument.dropped](#discoverysitemapsitemapdocumentdropped)
- [discovery.sitemap.SitemapDocument.compressed](#discoverysitemapsitemapdocumentcompressed)
- [discovery.sitemap.SitemapDocument.truncated](#discoverysitemapsitemapdocumenttruncated)
- [discovery.sitemap.parse_robots_sitemaps](#discoverysitemapparse_robots_sitemaps)
- [discovery.sitemap.parse_sitemap](#discoverysitemapparse_sitemap)
- [discovery.sitemap.SitemapStrategy](#discoverysitemapsitemapstrategy)
- [discovery.sitemap.SitemapStrategy.type_name](#discoverysitemapsitemapstrategytype_name)
- [discovery.sitemap.SitemapStrategy.__init__](#discoverysitemapsitemapstrategy__init__)
- [discovery.sitemap.SitemapStrategy.config](#discoverysitemapsitemapstrategyconfig)
- [discovery.sitemap.SitemapStrategy.strategy_id](#discoverysitemapsitemapstrategystrategy_id)
- [discovery.sitemap.SitemapStrategy.urls](#discoverysitemapsitemapstrategyurls)
- [discovery.sitemap.SitemapStrategy.use_robots_txt](#discoverysitemapsitemapstrategyuse_robots_txt)
- [discovery.sitemap.SitemapStrategy.lastmod_since](#discoverysitemapsitemapstrategylastmod_since)
- [discovery.sitemap.SitemapStrategy.pass_lastmod](#discoverysitemapsitemapstrategypass_lastmod)
- [discovery.sitemap.SitemapStrategy.stats](#discoverysitemapsitemapstrategystats)
- [discovery.sitemap.SitemapStrategy.seeds](#discoverysitemapsitemapstrategyseeds)
- [discovery.sitemap.SitemapStrategy.on_fetched](#discoverysitemapsitemapstrategyon_fetched)
- [discovery.sitemap.SitemapStrategy.snapshot](#discoverysitemapsitemapstrategysnapshot)
- [discovery.sitemap.SitemapStrategy.restore](#discoverysitemapsitemapstrategyrestore)

## discovery.sitemap.SitemapEntry

**Клас.** Код: [services/web-collector/strategies/discovery/sitemap.py:53](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L53).

```python
class SitemapEntry:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [loc](discovery.sitemap.md#discoverysitemapsitemapentryloc) | Поле | ні |
| [lastmod](discovery.sitemap.md#discoverysitemapsitemapentrylastmod) | Поле | ні |
| [__init__](discovery.sitemap.md#discoverysitemapsitemapentry__init__) | Конструктор dataclass | ні |

## discovery.sitemap.SitemapEntry.__init__

**Конструктор dataclass.** Код: [services/web-collector/strategies/discovery/sitemap.py:53](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L53).

```python
def __init__(self, loc: str, lastmod: datetime | None = None) -> None:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `loc` | `str` | `—` | positional-or-keyword |
| `lastmod` | `datetime \| None` | `None` | positional-or-keyword |

Результат: `None`.

## discovery.sitemap.SitemapEntry.loc

**Поле.** Код: [services/web-collector/strategies/discovery/sitemap.py:54](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L54).

```python
loc: str
```

Доступ: читання — так; запис — ні.

## discovery.sitemap.SitemapEntry.lastmod

**Поле.** Код: [services/web-collector/strategies/discovery/sitemap.py:55](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L55).

```python
lastmod: datetime | None = None
```

Доступ: читання — так; запис — ні.

## discovery.sitemap.SitemapDocument

**Клас.** Код: [services/web-collector/strategies/discovery/sitemap.py:59](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L59).

```python
class SitemapDocument:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [kind](discovery.sitemap.md#discoverysitemapsitemapdocumentkind) | Поле | ні |
| [urls](discovery.sitemap.md#discoverysitemapsitemapdocumenturls) | Поле | ні |
| [sitemaps](discovery.sitemap.md#discoverysitemapsitemapdocumentsitemaps) | Поле | ні |
| [dropped](discovery.sitemap.md#discoverysitemapsitemapdocumentdropped) | Поле | ні |
| [compressed](discovery.sitemap.md#discoverysitemapsitemapdocumentcompressed) | Поле | ні |
| [truncated](discovery.sitemap.md#discoverysitemapsitemapdocumenttruncated) | Поле | ні |
| [__init__](discovery.sitemap.md#discoverysitemapsitemapdocument__init__) | Конструктор dataclass | ні |

## discovery.sitemap.SitemapDocument.__init__

**Конструктор dataclass.** Код: [services/web-collector/strategies/discovery/sitemap.py:59](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L59).

```python
def __init__(self, kind: str = 'unknown', urls: list[SitemapEntry] = <factory list>, sitemaps: list[SitemapEntry] = <factory list>, dropped: int = 0, compressed: bool = False, truncated: bool = False) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `kind` | `str` | `'unknown'` | positional-or-keyword |
| `urls` | `list[SitemapEntry]` | `factory: list` | positional-or-keyword |
| `sitemaps` | `list[SitemapEntry]` | `factory: list` | positional-or-keyword |
| `dropped` | `int` | `0` | positional-or-keyword |
| `compressed` | `bool` | `False` | positional-or-keyword |
| `truncated` | `bool` | `False` | positional-or-keyword |

Результат: `None`.

## discovery.sitemap.SitemapDocument.kind

**Поле.** Код: [services/web-collector/strategies/discovery/sitemap.py:60](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L60).

```python
kind: str = 'unknown'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``urlset``, ``sitemapindex``, ``text``, ``feed`` or ``unknown``.
```

## discovery.sitemap.SitemapDocument.urls

**Поле.** Код: [services/web-collector/strategies/discovery/sitemap.py:62](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L62).

```python
urls: list[SitemapEntry] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## discovery.sitemap.SitemapDocument.sitemaps

**Поле.** Код: [services/web-collector/strategies/discovery/sitemap.py:63](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L63).

```python
sitemaps: list[SitemapEntry] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## discovery.sitemap.SitemapDocument.dropped

**Поле.** Код: [services/web-collector/strategies/discovery/sitemap.py:64](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L64).

```python
dropped: int = 0
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Entries over ``crawl.max_links_per_page``.
```

## discovery.sitemap.SitemapDocument.compressed

**Поле.** Код: [services/web-collector/strategies/discovery/sitemap.py:66](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L66).

```python
compressed: bool = False
```

Доступ: читання — так; запис — так.

## discovery.sitemap.SitemapDocument.truncated

**Поле.** Код: [services/web-collector/strategies/discovery/sitemap.py:67](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L67).

```python
truncated: bool = False
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
The body (or its decompressed form) was cut at ``crawl.max_material_bytes``.
```

## discovery.sitemap.parse_robots_sitemaps

**Функція.** Код: [services/web-collector/strategies/discovery/sitemap.py:71](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L71).

```python
def parse_robots_sitemaps(text: str, base: str) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `text` | `str` | `—` | positional-or-keyword |
| `base` | `str` | `—` | positional-or-keyword |

Результат: `list[str]`.

### Опис із вихідного коду

```text
``Sitemap:`` lines of a robots.txt (case-insensitive, anywhere in the file).
```

## discovery.sitemap.parse_sitemap

**Функція.** Код: [services/web-collector/strategies/discovery/sitemap.py:90](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L90).

```python
def parse_sitemap(body: bytes, base: str, *, max_bytes: int, max_entries: int) -> SitemapDocument:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `body` | `bytes` | `—` | positional-or-keyword |
| `base` | `str` | `—` | positional-or-keyword |
| `max_bytes` | `int` | `—` | keyword-only |
| `max_entries` | `int` | `—` | keyword-only |

Результат: `SitemapDocument`.

### Опис із вихідного коду

```text
Parse one sitemap file. Raises ``UnsafeDocument`` for XML with DTD entity declarations.
```

## discovery.sitemap.SitemapStrategy

**Клас.** Код: [services/web-collector/strategies/discovery/sitemap.py:118](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L118).

```python
class SitemapStrategy:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [type_name](discovery.sitemap.md#discoverysitemapsitemapstrategytype_name) | Поле | ні |
| [__init__](discovery.sitemap.md#discoverysitemapsitemapstrategy__init__) | Конструктор | ні |
| [config](discovery.sitemap.md#discoverysitemapsitemapstrategyconfig) | Поле екземпляра | ні |
| [strategy_id](discovery.sitemap.md#discoverysitemapsitemapstrategystrategy_id) | Поле екземпляра | ні |
| [urls](discovery.sitemap.md#discoverysitemapsitemapstrategyurls) | Поле екземпляра | ні |
| [use_robots_txt](discovery.sitemap.md#discoverysitemapsitemapstrategyuse_robots_txt) | Поле екземпляра | ні |
| [lastmod_since](discovery.sitemap.md#discoverysitemapsitemapstrategylastmod_since) | Поле екземпляра | ні |
| [pass_lastmod](discovery.sitemap.md#discoverysitemapsitemapstrategypass_lastmod) | Поле екземпляра | ні |
| [stats](discovery.sitemap.md#discoverysitemapsitemapstrategystats) | Поле екземпляра | ні |
| [seeds](discovery.sitemap.md#discoverysitemapsitemapstrategyseeds) | Метод | ні |
| [on_fetched](discovery.sitemap.md#discoverysitemapsitemapstrategyon_fetched) | Метод | ні |
| [snapshot](discovery.sitemap.md#discoverysitemapsitemapstrategysnapshot) | Метод | ні |
| [restore](discovery.sitemap.md#discoverysitemapsitemapstrategyrestore) | Метод | ні |

### Опис із вихідного коду

```text
Reads sitemap files through ``ctx.fetch`` and proposes their URLs as material candidates.
```

## discovery.sitemap.SitemapStrategy.type_name

**Поле.** Код: [services/web-collector/strategies/discovery/sitemap.py:121](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L121).

```python
type_name: ClassVar[str] = 'sitemap'
```

Доступ: читання — так; запис — так.

## discovery.sitemap.SitemapStrategy.__init__

**Конструктор.** Код: [services/web-collector/strategies/discovery/sitemap.py:123](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L123).

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

## discovery.sitemap.SitemapStrategy.config

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/sitemap.py:124](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L124).

```python
self.config = config
```

## discovery.sitemap.SitemapStrategy.strategy_id

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/sitemap.py:125](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L125).

```python
self.strategy_id = strategy_id
```

## discovery.sitemap.SitemapStrategy.urls

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/sitemap.py:126](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L126).

```python
self.urls: list[str] = [u for u in config.get('urls') or [] if isinstance(u, str)]
```

## discovery.sitemap.SitemapStrategy.use_robots_txt

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/sitemap.py:127](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L127).

```python
self.use_robots_txt = bool(config.get('use_robots_txt', True))
```

## discovery.sitemap.SitemapStrategy.lastmod_since

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/sitemap.py:128](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L128).

```python
self.lastmod_since = parse_datetime(config.get('lastmod_since'))
```

## discovery.sitemap.SitemapStrategy.pass_lastmod

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/sitemap.py:131](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L131).

```python
self.pass_lastmod = bool(config.get('use_lastmod_for_revisit', True))
```

## discovery.sitemap.SitemapStrategy.stats

**Поле екземпляра.** Код: [services/web-collector/strategies/discovery/sitemap.py:132](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L132).

```python
self.stats: dict[str, int] = {}
```

## discovery.sitemap.SitemapStrategy.seeds

**Метод.** Код: [services/web-collector/strategies/discovery/sitemap.py:154](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L154).

```python
async def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ctx` | `DiscoveryContext` | `—` | positional-or-keyword |

Результат: `AsyncIterator[DiscoveredUrl]`.

## discovery.sitemap.SitemapStrategy.on_fetched

**Метод.** Код: [services/web-collector/strategies/discovery/sitemap.py:237](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L237).

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

## discovery.sitemap.SitemapStrategy.snapshot

**Метод.** Код: [services/web-collector/strategies/discovery/sitemap.py:243](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L243).

```python
def snapshot(self) -> Mapping[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Mapping[str, Any]`.

## discovery.sitemap.SitemapStrategy.restore

**Метод.** Код: [services/web-collector/strategies/discovery/sitemap.py:246](../../../../../../services/web-collector/strategies/discovery/sitemap.py#L246).

```python
def restore(self, state: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.
