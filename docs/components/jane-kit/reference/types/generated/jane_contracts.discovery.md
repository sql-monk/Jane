# jane_contracts.discovery

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_contracts.discovery.UrlKind](#jane_contractsdiscoveryurlkind)
- [jane_contracts.discovery.HttpMethod](#jane_contractsdiscoveryhttpmethod)
- [jane_contracts.discovery.DiscoveredUrl](#jane_contractsdiscoverydiscoveredurl)
- [jane_contracts.discovery.DiscoveredUrl.__init__](#jane_contractsdiscoverydiscoveredurl__init__)
- [jane_contracts.discovery.DiscoveredUrl.url](#jane_contractsdiscoverydiscoveredurlurl)
- [jane_contracts.discovery.DiscoveredUrl.strategy_id](#jane_contractsdiscoverydiscoveredurlstrategy_id)
- [jane_contracts.discovery.DiscoveredUrl.kind](#jane_contractsdiscoverydiscoveredurlkind)
- [jane_contracts.discovery.DiscoveredUrl.priority](#jane_contractsdiscoverydiscoveredurlpriority)
- [jane_contracts.discovery.DiscoveredUrl.depth](#jane_contractsdiscoverydiscoveredurldepth)
- [jane_contracts.discovery.DiscoveredUrl.parent_url](#jane_contractsdiscoverydiscoveredurlparent_url)
- [jane_contracts.discovery.DiscoveredUrl.section](#jane_contractsdiscoverydiscoveredurlsection)
- [jane_contracts.discovery.DiscoveredUrl.lastmod](#jane_contractsdiscoverydiscoveredurllastmod)
- [jane_contracts.discovery.DiscoveredUrl.metadata](#jane_contractsdiscoverydiscoveredurlmetadata)
- [jane_contracts.discovery.FetchedResource](#jane_contractsdiscoveryfetchedresource)
- [jane_contracts.discovery.FetchedResource.__init__](#jane_contractsdiscoveryfetchedresource__init__)
- [jane_contracts.discovery.FetchedResource.url](#jane_contractsdiscoveryfetchedresourceurl)
- [jane_contracts.discovery.FetchedResource.final_url](#jane_contractsdiscoveryfetchedresourcefinal_url)
- [jane_contracts.discovery.FetchedResource.status](#jane_contractsdiscoveryfetchedresourcestatus)
- [jane_contracts.discovery.FetchedResource.media_type](#jane_contractsdiscoveryfetchedresourcemedia_type)
- [jane_contracts.discovery.FetchedResource.headers](#jane_contractsdiscoveryfetchedresourceheaders)
- [jane_contracts.discovery.FetchedResource.body](#jane_contractsdiscoveryfetchedresourcebody)
- [jane_contracts.discovery.FetchedResource.fetched_at](#jane_contractsdiscoveryfetchedresourcefetched_at)
- [jane_contracts.discovery.FetchedResource.depth](#jane_contractsdiscoveryfetchedresourcedepth)
- [jane_contracts.discovery.FetchedResource.strategy_id](#jane_contractsdiscoveryfetchedresourcestrategy_id)
- [jane_contracts.discovery.FetchedResource.kind](#jane_contractsdiscoveryfetchedresourcekind)
- [jane_contracts.discovery.FetchedResource.truncated](#jane_contractsdiscoveryfetchedresourcetruncated)
- [jane_contracts.discovery.LinkSelector](#jane_contractsdiscoverylinkselector)
- [jane_contracts.discovery.LinkSelector.__init__](#jane_contractsdiscoverylinkselector__init__)
- [jane_contracts.discovery.LinkSelector.value](#jane_contractsdiscoverylinkselectorvalue)
- [jane_contracts.discovery.LinkSelector.type](#jane_contractsdiscoverylinkselectortype)
- [jane_contracts.discovery.LinkSelector.attribute](#jane_contractsdiscoverylinkselectorattribute)
- [jane_contracts.discovery.DiscoveredMaterial](#jane_contractsdiscoverydiscoveredmaterial)
- [jane_contracts.discovery.DiscoveredMaterial.__init__](#jane_contractsdiscoverydiscoveredmaterial__init__)
- [jane_contracts.discovery.DiscoveredMaterial.url](#jane_contractsdiscoverydiscoveredmaterialurl)
- [jane_contracts.discovery.DiscoveredMaterial.strategy_id](#jane_contractsdiscoverydiscoveredmaterialstrategy_id)
- [jane_contracts.discovery.DiscoveredMaterial.body](#jane_contractsdiscoverydiscoveredmaterialbody)
- [jane_contracts.discovery.DiscoveredMaterial.fetched_at](#jane_contractsdiscoverydiscoveredmaterialfetched_at)
- [jane_contracts.discovery.DiscoveredMaterial.media_type](#jane_contractsdiscoverydiscoveredmaterialmedia_type)
- [jane_contracts.discovery.DiscoveredMaterial.depth](#jane_contractsdiscoverydiscoveredmaterialdepth)
- [jane_contracts.discovery.DiscoveredMaterial.parent_url](#jane_contractsdiscoverydiscoveredmaterialparent_url)
- [jane_contracts.discovery.DiscoveredMaterial.section](#jane_contractsdiscoverydiscoveredmaterialsection)
- [jane_contracts.discovery.DiscoveredMaterial.lastmod](#jane_contractsdiscoverydiscoveredmateriallastmod)
- [jane_contracts.discovery.DiscoveredMaterial.metadata](#jane_contractsdiscoverydiscoveredmaterialmetadata)
- [jane_contracts.discovery.FetchRejected](#jane_contractsdiscoveryfetchrejected)
- [jane_contracts.discovery.FetchRejected.__init__](#jane_contractsdiscoveryfetchrejected__init__)
- [jane_contracts.discovery.FetchRejected.code](#jane_contractsdiscoveryfetchrejectedcode)
- [jane_contracts.discovery.DiscoveryContext](#jane_contractsdiscoverydiscoverycontext)
- [jane_contracts.discovery.DiscoveryContext.source_id](#jane_contractsdiscoverydiscoverycontextsource_id)
- [jane_contracts.discovery.DiscoveryContext.collection_id](#jane_contractsdiscoverydiscoverycontextcollection_id)
- [jane_contracts.discovery.DiscoveryContext.rules](#jane_contractsdiscoverydiscoverycontextrules)
- [jane_contracts.discovery.DiscoveryContext.limits](#jane_contractsdiscoverydiscoverycontextlimits)
- [jane_contracts.discovery.DiscoveryContext.log](#jane_contractsdiscoverydiscoverycontextlog)
- [jane_contracts.discovery.DiscoveryContext.fetch](#jane_contractsdiscoverydiscoverycontextfetch)
- [jane_contracts.discovery.DiscoveryContext.emit_material](#jane_contractsdiscoverydiscoverycontextemit_material)
- [jane_contracts.discovery.DiscoveryContext.normalize](#jane_contractsdiscoverydiscoverycontextnormalize)
- [jane_contracts.discovery.DiscoveryContext.in_scope](#jane_contractsdiscoverydiscoverycontextin_scope)
- [jane_contracts.discovery.DiscoveryContext.section_for](#jane_contractsdiscoverydiscoverycontextsection_for)
- [jane_contracts.discovery.DiscoveryContext.extract_links](#jane_contractsdiscoverydiscoverycontextextract_links)
- [jane_contracts.discovery.DiscoveryContext.is_cancelled](#jane_contractsdiscoverydiscoverycontextis_cancelled)
- [jane_contracts.discovery.DiscoveryStrategy](#jane_contractsdiscoverydiscoverystrategy)
- [jane_contracts.discovery.DiscoveryStrategy.type_name](#jane_contractsdiscoverydiscoverystrategytype_name)
- [jane_contracts.discovery.DiscoveryStrategy.__init__](#jane_contractsdiscoverydiscoverystrategy__init__)
- [jane_contracts.discovery.DiscoveryStrategy.seeds](#jane_contractsdiscoverydiscoverystrategyseeds)
- [jane_contracts.discovery.DiscoveryStrategy.on_fetched](#jane_contractsdiscoverydiscoverystrategyon_fetched)
- [jane_contracts.discovery.DiscoveryStrategy.snapshot](#jane_contractsdiscoverydiscoverystrategysnapshot)
- [jane_contracts.discovery.DiscoveryStrategy.restore](#jane_contractsdiscoverydiscoverystrategyrestore)
- [jane_contracts.discovery.RefreshingStrategy](#jane_contractsdiscoveryrefreshingstrategy)
- [jane_contracts.discovery.RefreshingStrategy.refresh_on_revisit](#jane_contractsdiscoveryrefreshingstrategyrefresh_on_revisit)
- [jane_contracts.discovery.StrategyRegistry](#jane_contractsdiscoverystrategyregistry)
- [jane_contracts.discovery.StrategyRegistry.register](#jane_contractsdiscoverystrategyregistryregister)
- [jane_contracts.discovery.StrategyRegistry.get](#jane_contractsdiscoverystrategyregistryget)
- [jane_contracts.discovery.StrategyRegistry.types](#jane_contractsdiscoverystrategyregistrytypes)

## jane_contracts.discovery.UrlKind

**Змінна.** Код: [contracts/python/src/jane_contracts/discovery.py:45](../../../../../../contracts/python/src/jane_contracts/discovery.py#L45).

```python
UrlKind = Literal['material', 'navigation']
```

### Опис із вихідного коду

```text
``material`` — candidate content page (emitted as Material if fetched successfully);
``navigation`` — fetched only to discover more URLs (sitemap, feed, listing page, API page).
```

## jane_contracts.discovery.HttpMethod

**Змінна.** Код: [contracts/python/src/jane_contracts/discovery.py:49](../../../../../../contracts/python/src/jane_contracts/discovery.py#L49).

```python
HttpMethod = Literal['GET', 'POST']
```

### Опис із вихідного коду

```text
``POST`` (with a JSON body) only for ``navigation`` documents: API pages that are queried, not crawled.
```

## jane_contracts.discovery.DiscoveredUrl

**Клас.** Код: [contracts/python/src/jane_contracts/discovery.py:54](../../../../../../contracts/python/src/jane_contracts/discovery.py#L54).

```python
class DiscoveredUrl:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [url](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredurlurl) | Поле | ні |
| [strategy_id](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredurlstrategy_id) | Поле | ні |
| [kind](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredurlkind) | Поле | ні |
| [priority](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredurlpriority) | Поле | ні |
| [depth](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredurldepth) | Поле | ні |
| [parent_url](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredurlparent_url) | Поле | ні |
| [section](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredurlsection) | Поле | ні |
| [lastmod](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredurllastmod) | Поле | ні |
| [metadata](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredurlmetadata) | Поле | ні |
| [__init__](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredurl__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
A candidate URL proposed by a strategy. The core may drop it (scope, robots, dedup, depth).

``lastmod`` - when the source says the URL last changed (sitemap ``lastmod``, feed ``updated``, API
``lastmod_path``). In an ``incremental`` collection a ``lastmod`` later than the previous fetch of the URL
(the URL history of the ``state_key``) makes the core fetch it although ``revisit`` would skip it; an older
or missing ``lastmod`` never prevents a fetch that ``revisit`` allows.
```

## jane_contracts.discovery.DiscoveredUrl.__init__

**Конструктор dataclass.** Код: [contracts/python/src/jane_contracts/discovery.py:54](../../../../../../contracts/python/src/jane_contracts/discovery.py#L54).

```python
def __init__(self, url: str, strategy_id: str, kind: UrlKind = 'material', priority: int = 0, depth: int = 0, parent_url: str | None = None, section: str | None = None, lastmod: datetime | None = None, metadata: Mapping[str, Any] = <factory dict>) -> None:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `url` | `str` | `—` | positional-or-keyword |
| `strategy_id` | `str` | `—` | positional-or-keyword |
| `kind` | `UrlKind` | `'material'` | positional-or-keyword |
| `priority` | `int` | `0` | positional-or-keyword |
| `depth` | `int` | `0` | positional-or-keyword |
| `parent_url` | `str \| None` | `None` | positional-or-keyword |
| `section` | `str \| None` | `None` | positional-or-keyword |
| `lastmod` | `datetime \| None` | `None` | positional-or-keyword |
| `metadata` | `Mapping[str, Any]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

## jane_contracts.discovery.DiscoveredUrl.url

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:62](../../../../../../contracts/python/src/jane_contracts/discovery.py#L62).

```python
url: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredUrl.strategy_id

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:63](../../../../../../contracts/python/src/jane_contracts/discovery.py#L63).

```python
strategy_id: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredUrl.kind

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:64](../../../../../../contracts/python/src/jane_contracts/discovery.py#L64).

```python
kind: UrlKind = 'material'
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredUrl.priority

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:65](../../../../../../contracts/python/src/jane_contracts/discovery.py#L65).

```python
priority: int = 0
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredUrl.depth

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:66](../../../../../../contracts/python/src/jane_contracts/discovery.py#L66).

```python
depth: int = 0
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredUrl.parent_url

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:67](../../../../../../contracts/python/src/jane_contracts/discovery.py#L67).

```python
parent_url: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredUrl.section

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:68](../../../../../../contracts/python/src/jane_contracts/discovery.py#L68).

```python
section: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredUrl.lastmod

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:69](../../../../../../contracts/python/src/jane_contracts/discovery.py#L69).

```python
lastmod: datetime | None = None
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredUrl.metadata

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:70](../../../../../../contracts/python/src/jane_contracts/discovery.py#L70).

```python
metadata: Mapping[str, Any] = field(default_factory=dict)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_contracts.discovery.FetchedResource

**Клас.** Код: [contracts/python/src/jane_contracts/discovery.py:74](../../../../../../contracts/python/src/jane_contracts/discovery.py#L74).

```python
class FetchedResource:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [url](jane_contracts.discovery.md#jane_contractsdiscoveryfetchedresourceurl) | Поле | ні |
| [final_url](jane_contracts.discovery.md#jane_contractsdiscoveryfetchedresourcefinal_url) | Поле | ні |
| [status](jane_contracts.discovery.md#jane_contractsdiscoveryfetchedresourcestatus) | Поле | ні |
| [media_type](jane_contracts.discovery.md#jane_contractsdiscoveryfetchedresourcemedia_type) | Поле | ні |
| [headers](jane_contracts.discovery.md#jane_contractsdiscoveryfetchedresourceheaders) | Поле | ні |
| [body](jane_contracts.discovery.md#jane_contractsdiscoveryfetchedresourcebody) | Поле | ні |
| [fetched_at](jane_contracts.discovery.md#jane_contractsdiscoveryfetchedresourcefetched_at) | Поле | ні |
| [depth](jane_contracts.discovery.md#jane_contractsdiscoveryfetchedresourcedepth) | Поле | ні |
| [strategy_id](jane_contracts.discovery.md#jane_contractsdiscoveryfetchedresourcestrategy_id) | Поле | ні |
| [kind](jane_contracts.discovery.md#jane_contractsdiscoveryfetchedresourcekind) | Поле | ні |
| [truncated](jane_contracts.discovery.md#jane_contractsdiscoveryfetchedresourcetruncated) | Поле | ні |
| [__init__](jane_contracts.discovery.md#jane_contractsdiscoveryfetchedresource__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
A response obtained through :meth:`DiscoveryContext.fetch` (already within limits).
```

## jane_contracts.discovery.FetchedResource.__init__

**Конструктор dataclass.** Код: [contracts/python/src/jane_contracts/discovery.py:74](../../../../../../contracts/python/src/jane_contracts/discovery.py#L74).

```python
def __init__(self, url: str, final_url: str, status: int, media_type: str, headers: Mapping[str, str], body: bytes, fetched_at: datetime, depth: int, strategy_id: str | None, kind: UrlKind, truncated: bool = False) -> None:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `url` | `str` | `—` | positional-or-keyword |
| `final_url` | `str` | `—` | positional-or-keyword |
| `status` | `int` | `—` | positional-or-keyword |
| `media_type` | `str` | `—` | positional-or-keyword |
| `headers` | `Mapping[str, str]` | `—` | positional-or-keyword |
| `body` | `bytes` | `—` | positional-or-keyword |
| `fetched_at` | `datetime` | `—` | positional-or-keyword |
| `depth` | `int` | `—` | positional-or-keyword |
| `strategy_id` | `str \| None` | `—` | positional-or-keyword |
| `kind` | `UrlKind` | `—` | positional-or-keyword |
| `truncated` | `bool` | `False` | positional-or-keyword |

Результат: `None`.

## jane_contracts.discovery.FetchedResource.url

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:77](../../../../../../contracts/python/src/jane_contracts/discovery.py#L77).

```python
url: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.FetchedResource.final_url

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:78](../../../../../../contracts/python/src/jane_contracts/discovery.py#L78).

```python
final_url: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.FetchedResource.status

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:79](../../../../../../contracts/python/src/jane_contracts/discovery.py#L79).

```python
status: int
```

Доступ: читання — так; запис — ні.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_discovery_context.py:85](../../../../../../services/web-collector/tests/test_discovery_context.py#L85).

```python
SEEN.append((_path(resource.url), resource.status, resource.strategy_id))
```

## jane_contracts.discovery.FetchedResource.media_type

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:80](../../../../../../contracts/python/src/jane_contracts/discovery.py#L80).

```python
media_type: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.FetchedResource.headers

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:81](../../../../../../contracts/python/src/jane_contracts/discovery.py#L81).

```python
headers: Mapping[str, str]
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.FetchedResource.body

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:82](../../../../../../contracts/python/src/jane_contracts/discovery.py#L82).

```python
body: bytes
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.FetchedResource.fetched_at

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:83](../../../../../../contracts/python/src/jane_contracts/discovery.py#L83).

```python
fetched_at: datetime
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.FetchedResource.depth

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:84](../../../../../../contracts/python/src/jane_contracts/discovery.py#L84).

```python
depth: int
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.FetchedResource.strategy_id

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:85](../../../../../../contracts/python/src/jane_contracts/discovery.py#L85).

```python
strategy_id: str | None
```

Доступ: читання — так; запис — ні.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_discovery_context.py:58](../../../../../../services/web-collector/tests/test_discovery_context.py#L58).

```python
resource.strategy_id
```

Контекст і передумови: [services/web-collector/tests/test_discovery_context.py:85](../../../../../../services/web-collector/tests/test_discovery_context.py#L85).

```python
SEEN.append((_path(resource.url), resource.status, resource.strategy_id))
```

## jane_contracts.discovery.FetchedResource.kind

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:86](../../../../../../contracts/python/src/jane_contracts/discovery.py#L86).

```python
kind: UrlKind
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.FetchedResource.truncated

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:87](../../../../../../contracts/python/src/jane_contracts/discovery.py#L87).

```python
truncated: bool = False
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.LinkSelector

**Клас.** Код: [contracts/python/src/jane_contracts/discovery.py:91](../../../../../../contracts/python/src/jane_contracts/discovery.py#L91).

```python
class LinkSelector:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [value](jane_contracts.discovery.md#jane_contractsdiscoverylinkselectorvalue) | Поле | ні |
| [type](jane_contracts.discovery.md#jane_contractsdiscoverylinkselectortype) | Поле | ні |
| [attribute](jane_contracts.discovery.md#jane_contractsdiscoverylinkselectorattribute) | Поле | ні |
| [__init__](jane_contracts.discovery.md#jane_contractsdiscoverylinkselector__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Mirrors CollectorRules ``$defs/Selector``.
```

## jane_contracts.discovery.LinkSelector.__init__

**Конструктор dataclass.** Код: [contracts/python/src/jane_contracts/discovery.py:91](../../../../../../contracts/python/src/jane_contracts/discovery.py#L91).

```python
def __init__(self, value: str, type: Literal['css', 'xpath', 'rel'] = 'css', attribute: str = 'href') -> None:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `str` | `—` | positional-or-keyword |
| `type` | `Literal['css', 'xpath', 'rel']` | `'css'` | positional-or-keyword |
| `attribute` | `str` | `'href'` | positional-or-keyword |

Результат: `None`.

## jane_contracts.discovery.LinkSelector.value

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:94](../../../../../../contracts/python/src/jane_contracts/discovery.py#L94).

```python
value: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.LinkSelector.type

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:95](../../../../../../contracts/python/src/jane_contracts/discovery.py#L95).

```python
type: Literal['css', 'xpath', 'rel'] = 'css'
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.LinkSelector.attribute

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:96](../../../../../../contracts/python/src/jane_contracts/discovery.py#L96).

```python
attribute: str = 'href'
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredMaterial

**Клас.** Код: [contracts/python/src/jane_contracts/discovery.py:100](../../../../../../contracts/python/src/jane_contracts/discovery.py#L100).

```python
class DiscoveredMaterial:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [url](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredmaterialurl) | Поле | ні |
| [strategy_id](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredmaterialstrategy_id) | Поле | ні |
| [body](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredmaterialbody) | Поле | ні |
| [fetched_at](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredmaterialfetched_at) | Поле | ні |
| [media_type](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredmaterialmedia_type) | Поле | ні |
| [depth](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredmaterialdepth) | Поле | ні |
| [parent_url](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredmaterialparent_url) | Поле | ні |
| [section](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredmaterialsection) | Поле | ні |
| [lastmod](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredmateriallastmod) | Поле | ні |
| [metadata](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredmaterialmetadata) | Поле | ні |
| [__init__](jane_contracts.discovery.md#jane_contractsdiscoverydiscoveredmaterial__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
A material whose content the strategy already has: one JSON item of an API page (``api_feed`` with
``emit_items_as_materials``). :meth:`DiscoveryContext.emit_material` turns it into a Material.

``url`` identifies the material (``material_id`` from its canonical URL, as for a fetched page) and is
not fetched; ``body`` is the content as is (``media_type``, UTF-8 for text); ``fetched_at`` is when the
page it comes from was fetched; ``parent_url`` is that page.
```

## jane_contracts.discovery.DiscoveredMaterial.__init__

**Конструктор dataclass.** Код: [contracts/python/src/jane_contracts/discovery.py:100](../../../../../../contracts/python/src/jane_contracts/discovery.py#L100).

```python
def __init__(self, url: str, strategy_id: str, body: bytes, fetched_at: datetime, media_type: str = 'application/json', depth: int = 0, parent_url: str | None = None, section: str | None = None, lastmod: datetime | None = None, metadata: Mapping[str, Any] = <factory dict>) -> None:
```

Декоратори: `dataclass(frozen=True, slots=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `url` | `str` | `—` | positional-or-keyword |
| `strategy_id` | `str` | `—` | positional-or-keyword |
| `body` | `bytes` | `—` | positional-or-keyword |
| `fetched_at` | `datetime` | `—` | positional-or-keyword |
| `media_type` | `str` | `'application/json'` | positional-or-keyword |
| `depth` | `int` | `0` | positional-or-keyword |
| `parent_url` | `str \| None` | `None` | positional-or-keyword |
| `section` | `str \| None` | `None` | positional-or-keyword |
| `lastmod` | `datetime \| None` | `None` | positional-or-keyword |
| `metadata` | `Mapping[str, Any]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

## jane_contracts.discovery.DiscoveredMaterial.url

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:108](../../../../../../contracts/python/src/jane_contracts/discovery.py#L108).

```python
url: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredMaterial.strategy_id

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:109](../../../../../../contracts/python/src/jane_contracts/discovery.py#L109).

```python
strategy_id: str
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredMaterial.body

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:110](../../../../../../contracts/python/src/jane_contracts/discovery.py#L110).

```python
body: bytes
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredMaterial.fetched_at

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:111](../../../../../../contracts/python/src/jane_contracts/discovery.py#L111).

```python
fetched_at: datetime
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredMaterial.media_type

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:112](../../../../../../contracts/python/src/jane_contracts/discovery.py#L112).

```python
media_type: str = 'application/json'
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredMaterial.depth

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:113](../../../../../../contracts/python/src/jane_contracts/discovery.py#L113).

```python
depth: int = 0
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredMaterial.parent_url

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:114](../../../../../../contracts/python/src/jane_contracts/discovery.py#L114).

```python
parent_url: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredMaterial.section

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:115](../../../../../../contracts/python/src/jane_contracts/discovery.py#L115).

```python
section: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredMaterial.lastmod

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:116](../../../../../../contracts/python/src/jane_contracts/discovery.py#L116).

```python
lastmod: datetime | None = None
```

Доступ: читання — так; запис — ні.

## jane_contracts.discovery.DiscoveredMaterial.metadata

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:117](../../../../../../contracts/python/src/jane_contracts/discovery.py#L117).

```python
metadata: Mapping[str, Any] = field(default_factory=dict)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_contracts.discovery.FetchRejected

**Клас.** Код: [contracts/python/src/jane_contracts/discovery.py:120](../../../../../../contracts/python/src/jane_contracts/discovery.py#L120).

```python
class FetchRejected(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_contracts.discovery.md#jane_contractsdiscoveryfetchrejected__init__) | Конструктор | ні |
| [code](jane_contracts.discovery.md#jane_contractsdiscoveryfetchrejectedcode) | Поле екземпляра | ні |

### Опис із вихідного коду

```text
Raised by :meth:`DiscoveryContext.fetch` when policy forbids the request.

``code`` is a Problem code: ``out_of_scope`` (the URL or a redirect hop), ``access_denied_by_policy``
(robots.txt, outbound address policy), ``limit_exceeded`` (only a run budget: ``crawl.max_pages_per_run``,
``crawl.max_bytes_per_run``) or ``rate_limited`` (the source asks to wait longer than the configured maximum:
``Retry-After`` / ``Crawl-delay`` above the collector's limit, or 429 after the retries). A strategy skips
the URL; ``limit_exceeded`` and ``rate_limited`` mean "stop asking this run".
```

## jane_contracts.discovery.FetchRejected.__init__

**Конструктор.** Код: [contracts/python/src/jane_contracts/discovery.py:130](../../../../../../contracts/python/src/jane_contracts/discovery.py#L130).

```python
def __init__(self, code: str, message: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `code` | `str` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_contracts.discovery.FetchRejected.code

**Поле екземпляра.** Код: [contracts/python/src/jane_contracts/discovery.py:132](../../../../../../contracts/python/src/jane_contracts/discovery.py#L132).

```python
self.code = code
```

## jane_contracts.discovery.DiscoveryContext

**Клас.** Код: [contracts/python/src/jane_contracts/discovery.py:135](../../../../../../contracts/python/src/jane_contracts/discovery.py#L135).

```python
class DiscoveryContext(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [source_id](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverycontextsource_id) | Поле | ні |
| [collection_id](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverycontextcollection_id) | Поле | ні |
| [rules](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverycontextrules) | Поле | ні |
| [limits](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverycontextlimits) | Поле | ні |
| [log](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverycontextlog) | Поле | ні |
| [fetch](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverycontextfetch) | Метод | ні |
| [emit_material](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverycontextemit_material) | Метод | ні |
| [normalize](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverycontextnormalize) | Метод | ні |
| [in_scope](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverycontextin_scope) | Метод | ні |
| [section_for](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverycontextsection_for) | Метод | ні |
| [extract_links](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverycontextextract_links) | Метод | ні |
| [is_cancelled](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverycontextis_cancelled) | Метод | ні |

### Опис із вихідного коду

```text
Services the Web Collector core provides to a running strategy.
```

## jane_contracts.discovery.DiscoveryContext.source_id

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:138](../../../../../../contracts/python/src/jane_contracts/discovery.py#L138).

```python
source_id: str | None
```

Доступ: читання — так; запис — так.

## jane_contracts.discovery.DiscoveryContext.collection_id

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:139](../../../../../../contracts/python/src/jane_contracts/discovery.py#L139).

```python
collection_id: str
```

Доступ: читання — так; запис — так.

## jane_contracts.discovery.DiscoveryContext.rules

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:140](../../../../../../contracts/python/src/jane_contracts/discovery.py#L140).

```python
rules: Mapping[str, Any]
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
The full validated WebRules document.
```

## jane_contracts.discovery.DiscoveryContext.limits

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:142](../../../../../../contracts/python/src/jane_contracts/discovery.py#L142).

```python
limits: Mapping[str, Any]
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Effective Limits (read-only); strategy-level ``limits`` are already merged in.
```

## jane_contracts.discovery.DiscoveryContext.log

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:144](../../../../../../contracts/python/src/jane_contracts/discovery.py#L144).

```python
log: logging.Logger
```

Доступ: читання — так; запис — так.

## jane_contracts.discovery.DiscoveryContext.fetch

**Метод.** Код: [contracts/python/src/jane_contracts/discovery.py:146](../../../../../../contracts/python/src/jane_contracts/discovery.py#L146).

```python
async def fetch(self, url: str, *, kind: UrlKind='navigation', conditional: bool=True, method: HttpMethod='GET', body: Any=None) -> FetchedResource | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |
| `kind` | `UrlKind` | `'navigation'` | keyword-only |
| `conditional` | `bool` | `True` | keyword-only |
| `method` | `HttpMethod` | `'GET'` | keyword-only |
| `body` | `Any` | `None` | keyword-only |

Результат: `FetchedResource | None`.

### Опис із вихідного коду

```text
Fetch through the core with exactly the policy and resources of the frontier's own fetches:

* shared with the core: scope and ``exclude`` (also for every redirect hop), robots.txt (or the owner
  policy), the outbound address policy, the per-host limits of the collector (interval, parallelism,
  ``Crawl-delay``, ``Retry-After``; shared with every collection and one-shot fetch of the collector),
  retries, size limit (``crawl.max_material_bytes``, ``truncated``), the run budgets
  (``crawl.max_pages_per_run``, ``max_bytes_per_run``: a fetch counts like any other), the URL history of
  the ``state_key`` and backpressure for ``kind="material"``; timeouts come from the strategy's limits;
* the URL joins the frontier of the collection (one row per canonical URL): a ``material`` is emitted as
  a Material like a frontier page; a ``navigation`` document is never emitted;
* the resource is passed to :meth:`DiscoveryStrategy.on_fetched` of every **other** strategy (not back
  to the caller, which has it already).

Returns the resource with any final status except 304 (a 404 is a resource: ``url_template`` counts
misses with it). Returns ``None`` when: not modified (``conditional=True`` and the URL history has a
validator, 304); already fetched in this process for this collection, or already done as a material;
a redirect leads to a URL already known; the fetch failed after the retries (network error, 5xx) - the
core records it in the collection errors. ``revisit`` is not applied: a strategy asks for what it needs.

``method="POST"`` sends ``body`` as JSON (``Content-Type: application/json``) and is allowed only for
``kind="navigation"`` (``ValueError`` otherwise); it is never conditional; 307/308 redirects repeat the
POST, 301/302/303 continue with GET; retries follow the same policy as GET, so it must be a read-only
query of the source (an API search or listing).

Raises :class:`FetchRejected` on policy violations (see its codes).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_discovery_context.py:47](../../../../../../services/web-collector/tests/test_discovery_context.py#L47).

```python
res = await ctx.fetch(url, kind="navigation", conditional=False)
```

## jane_contracts.discovery.DiscoveryContext.emit_material

**Метод.** Код: [contracts/python/src/jane_contracts/discovery.py:182](../../../../../../contracts/python/src/jane_contracts/discovery.py#L182).

```python
async def emit_material(self, item: DiscoveredMaterial) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `item` | `DiscoveredMaterial` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
Emit content the strategy already has as a Material (``api_feed`` JSON items). The core applies the
same rules as to a fetched page: ``item.url`` is normalized and must be in scope (robots.txt is not
consulted: nothing is fetched), the strategy's ``crawl.max_depth``, one material per canonical URL in a
collection (the URL is claimed in the frontier, so no other strategy fetches it again in this collection),
``revisit``/``dedup`` against the URL history in ``incremental`` collections (``lastmod`` newer than the
last observation forces it), backpressure. Returns ``True`` if a Material was emitted, ``False`` if
the item was dropped (out of scope, too deep, duplicate, unchanged).
```

## jane_contracts.discovery.DiscoveryContext.normalize

**Метод.** Код: [contracts/python/src/jane_contracts/discovery.py:192](../../../../../../contracts/python/src/jane_contracts/discovery.py#L192).

```python
def normalize(self, url: str, base: str | None=None) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |
| `base` | `str \| None` | `None` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Resolve relative URLs and apply CollectorRules ``normalization``.
```

## jane_contracts.discovery.DiscoveryContext.in_scope

**Метод.** Код: [contracts/python/src/jane_contracts/discovery.py:196](../../../../../../contracts/python/src/jane_contracts/discovery.py#L196).

```python
def in_scope(self, url: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_contracts.discovery.DiscoveryContext.section_for

**Метод.** Код: [contracts/python/src/jane_contracts/discovery.py:198](../../../../../../contracts/python/src/jane_contracts/discovery.py#L198).

```python
def section_for(self, url: str) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `str | None`.

## jane_contracts.discovery.DiscoveryContext.extract_links

**Метод.** Код: [contracts/python/src/jane_contracts/discovery.py:200](../../../../../../contracts/python/src/jane_contracts/discovery.py#L200).

```python
def extract_links(self, resource: FetchedResource, selector: LinkSelector | None=None) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `resource` | `FetchedResource` | `—` | positional-or-keyword |
| `selector` | `LinkSelector \| None` | `None` | positional-or-keyword |

Результат: `list[str]`.

### Опис із вихідного коду

```text
Links from an HTML resource (``a[href]`` by default), normalized and absolute.
```

## jane_contracts.discovery.DiscoveryContext.is_cancelled

**Метод.** Код: [contracts/python/src/jane_contracts/discovery.py:204](../../../../../../contracts/python/src/jane_contracts/discovery.py#L204).

```python
def is_cancelled(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_contracts.discovery.DiscoveryStrategy

**Клас.** Код: [contracts/python/src/jane_contracts/discovery.py:208](../../../../../../contracts/python/src/jane_contracts/discovery.py#L208).

```python
class DiscoveryStrategy(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

Декоратори: `runtime_checkable`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [type_name](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverystrategytype_name) | Поле | ні |
| [__init__](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverystrategy__init__) | Конструктор | ні |
| [seeds](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverystrategyseeds) | Метод | ні |
| [on_fetched](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverystrategyon_fetched) | Метод | ні |
| [snapshot](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverystrategysnapshot) | Метод | ні |
| [restore](jane_contracts.discovery.md#jane_contractsdiscoverydiscoverystrategyrestore) | Метод | ні |

### Опис із вихідного коду

```text
One material discovery mode. Instances live for one collection run.
```

## jane_contracts.discovery.DiscoveryStrategy.type_name

**Поле.** Код: [contracts/python/src/jane_contracts/discovery.py:211](../../../../../../contracts/python/src/jane_contracts/discovery.py#L211).

```python
type_name: ClassVar[str]
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Equals the strategy ``type`` in CollectorRules, e.g. ``"sitemap"``.
```

## jane_contracts.discovery.DiscoveryStrategy.__init__

**Конструктор.** Код: [contracts/python/src/jane_contracts/discovery.py:214](../../../../../../contracts/python/src/jane_contracts/discovery.py#L214).

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

### Опис із вихідного коду

```text
``config`` is the validated strategy object; ``strategy_id`` is its id or a generated one.
```

## jane_contracts.discovery.DiscoveryStrategy.seeds

**Метод.** Код: [contracts/python/src/jane_contracts/discovery.py:218](../../../../../../contracts/python/src/jane_contracts/discovery.py#L218).

```python
def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ctx` | `DiscoveryContext` | `—` | positional-or-keyword |

Результат: `AsyncIterator[DiscoveredUrl]`.

### Опис із вихідного коду

```text
Initial candidates. May fetch navigation documents (sitemaps, feeds, API pages).
```

## jane_contracts.discovery.DiscoveryStrategy.on_fetched

**Метод.** Код: [contracts/python/src/jane_contracts/discovery.py:222](../../../../../../contracts/python/src/jane_contracts/discovery.py#L222).

```python
def on_fetched(self, resource: FetchedResource, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]:
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
Called by the core for every fetched resource (from any strategy), so strategies combine: e.g.
``recursive`` follows links from pages found by ``sitemap``. Strategies that do not react to other
pages yield nothing.

"Fetched" means an HTTP response with a body, **whatever its status**: 2xx, and also 4xx (404, 410, 403...)
and 5xx that are not retried; check ``resource.status`` (``url_template`` counts 404/410 as misses,
``listing`` stops a chain on a non-2xx page). Not called for: 304 (nothing new; ``recursive`` gets the
stored links of the page instead), a page skipped by ``revisit``, a redirect to an already known URL, a
page whose final or ``rel=canonical`` URL is already known in the collection (a duplicate), a failed fetch
(retried statuses 429/500/502/503/504 that stayed failing, network errors) and a refused one. A resource
fetched through :meth:`DiscoveryContext.fetch` goes to every strategy except the caller.
```

## jane_contracts.discovery.DiscoveryStrategy.snapshot

**Метод.** Код: [contracts/python/src/jane_contracts/discovery.py:236](../../../../../../contracts/python/src/jane_contracts/discovery.py#L236).

```python
def snapshot(self) -> Mapping[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Mapping[str, Any]`.

### Опис із вихідного коду

```text
JSON-serialisable progress state (cursor, page number, processed sitemap files).
```

## jane_contracts.discovery.DiscoveryStrategy.restore

**Метод.** Код: [contracts/python/src/jane_contracts/discovery.py:240](../../../../../../contracts/python/src/jane_contracts/discovery.py#L240).

```python
def restore(self, state: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Restore state saved by :meth:`snapshot` after a restart.
```

## jane_contracts.discovery.RefreshingStrategy

**Клас.** Код: [contracts/python/src/jane_contracts/discovery.py:246](../../../../../../contracts/python/src/jane_contracts/discovery.py#L246).

```python
class RefreshingStrategy(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

Декоратори: `runtime_checkable`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [refresh_on_revisit](jane_contracts.discovery.md#jane_contractsdiscoveryrefreshingstrategyrefresh_on_revisit) | Метод | ні |

### Опис із вихідного коду

```text
Optional hook of a :class:`DiscoveryStrategy` (contract 1.1).

A strategy that finds new materials on pages it already knows (``listing``: category, pagination and
search pages) answers ``True`` for such a URL. The core then fetches the page in full in every run - it is
not skipped by ``revisit`` in an ``incremental`` collection and never sent as a conditional request (no 304)
- so :meth:`DiscoveryStrategy.on_fetched` sees the current page. The materials it lists still follow
``revisit``. Asked when the URL is about to be fetched; strategies without the method are never asked.
```

## jane_contracts.discovery.RefreshingStrategy.refresh_on_revisit

**Метод.** Код: [contracts/python/src/jane_contracts/discovery.py:255](../../../../../../contracts/python/src/jane_contracts/discovery.py#L255).

```python
def refresh_on_revisit(self, url: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_contracts.discovery.StrategyRegistry

**Клас.** Код: [contracts/python/src/jane_contracts/discovery.py:258](../../../../../../contracts/python/src/jane_contracts/discovery.py#L258).

```python
class StrategyRegistry(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [register](jane_contracts.discovery.md#jane_contractsdiscoverystrategyregistryregister) | Метод | ні |
| [get](jane_contracts.discovery.md#jane_contractsdiscoverystrategyregistryget) | Метод | ні |
| [types](jane_contracts.discovery.md#jane_contractsdiscoverystrategyregistrytypes) | Метод | ні |

### Опис із вихідного коду

```text
Registry owned by WP-02.
```

## jane_contracts.discovery.StrategyRegistry.register

**Метод.** Код: [contracts/python/src/jane_contracts/discovery.py:261](../../../../../../contracts/python/src/jane_contracts/discovery.py#L261).

```python
def register(self, strategy: type[DiscoveryStrategy]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `strategy` | `type[DiscoveryStrategy]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_contracts.discovery.StrategyRegistry.get

**Метод.** Код: [contracts/python/src/jane_contracts/discovery.py:263](../../../../../../contracts/python/src/jane_contracts/discovery.py#L263).

```python
def get(self, type_name: str) -> type[DiscoveryStrategy]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `type_name` | `str` | `—` | positional-or-keyword |

Результат: `type[DiscoveryStrategy]`.

### Опис із вихідного коду

```text
Raises ``KeyError`` for unknown types (collector answers ``supported: false``).
```

## jane_contracts.discovery.StrategyRegistry.types

**Метод.** Код: [contracts/python/src/jane_contracts/discovery.py:267](../../../../../../contracts/python/src/jane_contracts/discovery.py#L267).

```python
def types(self) -> Sequence[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Sequence[str]`.
