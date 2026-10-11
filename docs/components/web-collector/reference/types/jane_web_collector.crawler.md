# Модуль `jane_web_collector.crawler`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/crawler.py](../../../../../services/web-collector/src/jane_web_collector/crawler.py). Не редагуйте вручну.

Crawl engine: one :class:`CrawlRun` per collection, implementing ``DiscoveryContext`` for strategies.

Pipeline for every URL (from the frontier or ``ctx.fetch``): scope/exclude (at admission) -> robots.txt (or the explicit ``owner_policy``) -> revisit decision (URL history of the ``state_key``) -> fetch (per-host limits, redirects re-checked hop by hop, size limit, conditional request) -> dedup of the final/canonical URL -> Material (buffer) -> ``on_fetched`` of every strategy -> admission of new candidates (normalize, scope, depth, frontier size, dedup by primary key) -> one transaction.

## Зміст

- [Клас `CrawlRun`](#клас-crawlrun)
- [Клас `RunDeps`](#клас-rundeps)
- [Клас `StrategyContext`](#клас-strategycontext)
- [Функція `new_stats`](#функція-new_stats)

## Класи

### Клас `CrawlRun`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.crawler` |
| Код | [crawler.py:174](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L174) |

```python
class CrawlRun: ...
```

#### Конструктор `CrawlRun.__init__`

```python
def __init__(self, deps: RunDeps, record: Mapping[str, Any]) -> None: ...
```

Код: [crawler.py:175](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L175).

#### Метод `CrawlRun.scope_reason`

```python
def scope_reason(self, url: str) -> str | None: ...
```

Код: [crawler.py:261](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L261).

#### Метод `CrawlRun.section_for`

```python
def section_for(self, url: str) -> str | None: ...
```

Код: [crawler.py:266](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L266).

#### Метод `CrawlRun.rule_priority`

```python
def rule_priority(self, url: str) -> int: ...
```

Код: [crawler.py:272](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L272).

#### Метод `CrawlRun.extract_links`

```python
def extract_links(
    self,
    resource: FetchedResource,
    selector: LinkSelector | None = None,
    sources: Sequence[str] = ('a_href',),
) -> list[str]: ...
```

Код: [crawler.py:278](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L278).

#### Метод `CrawlRun.robots_allowed`

```python
async def robots_allowed(self, url: str) -> bool: ...
```

Код: [crawler.py:325](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L325).

#### Метод `CrawlRun.admit`

```python
def admit(
    self,
    candidates: Sequence[DiscoveredUrl],
    parent_depth: int | None,
) -> list[FrontierRow]: ...
```

Normalize and filter candidates (scope, depth, frontier size); dedup happens on insert.

Код: [crawler.py:354](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L354).

#### Метод `CrawlRun.insert_rows`

```python
def insert_rows(self, db: Any, rows: Sequence[FrontierRow]) -> None: ...
```

Код: [crawler.py:392](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L392).

#### Метод `CrawlRun.handle`

```python
async def handle(
    self,
    row: FrontierRow,
    *,
    caller: str | None = None,
    conditional: bool = True,
    method: str = 'GET',
    json_body: bytes | None = None,
) -> FetchedResource | None: ...
```

Fetch and process one admitted URL. Returns the resource (for ``ctx.fetch``) or ``None``.

Винятки в коді методу: `FetchRejected`, `RedirectDuplicate`.

Код: [crawler.py:511](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L511).

#### Метод `CrawlRun.fetch_for_strategy`

```python
async def fetch_for_strategy(
    self,
    url: str,
    *,
    kind: UrlKind,
    conditional: bool,
    caller: str,
    method: str = 'GET',
    body: Any = None,
) -> FetchedResource | None: ...
```

Винятки в коді методу: `ValueError`, `FetchRejected`.

Код: [crawler.py:842](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L842).

#### Метод `CrawlRun.emit_for_strategy`

```python
async def emit_for_strategy(self, item: DiscoveredMaterial, *, caller: str) -> bool: ...
```

``DiscoveryContext.emit_material``: content a strategy already has (an API item) as a Material, under the rules of a fetched page - scope, depth, one material per canonical URL in the collection, ``revisit`` and ``dedup`` against the URL history, backpressure, one fenced transaction (R22).

Винятки в коді методу: `JobCancelledError`.

Код: [crawler.py:887](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L887).

#### Метод `CrawlRun.execute`

```python
async def execute(self, job: JobContext | None = None) -> dict[str, Any]: ...
```

Винятки в коді методу: `RuntimeError`.

Код: [crawler.py:1068](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L1068).

### Клас `RunDeps`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_web_collector.crawler` |
| Код | [crawler.py:97](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L97) |

```python
@dataclass
class RunDeps: ...
```

Service-level dependencies shared by all runs.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `state` | `StateStore` | — | читання й запис |  |
| `registry` | `Registry` | — | читання й запис |  |
| `client` | `httpx.AsyncClient` | — | читання й запис |  |
| `resolve` | `Callable[..., ResolvedLimits[ServiceLimits]]` | — | читання й запис |  |
| `transit` | `TransitStore \| None` | — | читання й запис |  |
| `instance_id` | `str` | — | читання й запис |  |
| `lease_seconds` | `float` | — | читання й запис |  |
| `heartbeat_seconds` | `float` | — | читання й запис |  |
| `user_agent` | `str` | — | читання й запис |  |
| `version` | `str` | — | читання й запис |  |
| `host_limiter` | `HostLimiter` | — | читання й запис | Per-host limits of the whole process, shared by every run and one-shot fetch. |
| `connection_policy` | `ConnectionPolicy` | `field(default_factory=ConnectionPolicy)` | читання й запис |  |
| `ack_events` | `dict[str, asyncio.Event]` | `field(default_factory=dict)` | читання й запис |  |
| `renderer` | `Renderer \| None` | `None` | читання й запис | Headless browser for ``fetch.render_js`` (``None``: such URLs fail with ``not_implemented``). |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `StrategyContext`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.crawler` |
| Код | [crawler.py:122](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L122) |

```python
class StrategyContext: ...
```

``DiscoveryContext`` given to one strategy (its own merged limits).

#### Конструктор `StrategyContext.__init__`

```python
def __init__(self, run: CrawlRun, strategy_id: str, limits: Mapping[str, Any]) -> None: ...
```

Код: [crawler.py:125](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L125).

#### Метод `StrategyContext.fetch`

```python
async def fetch(
    self,
    url: str,
    *,
    kind: UrlKind = 'navigation',
    conditional: bool = True,
    method: HttpMethod = 'GET',
    body: Any = None,
) -> FetchedResource | None: ...
```

Код: [crawler.py:134](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L134).

#### Метод `StrategyContext.emit_material`

```python
async def emit_material(self, item: DiscoveredMaterial) -> bool: ...
```

Код: [crawler.py:147](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L147).

#### Метод `StrategyContext.normalize`

```python
def normalize(self, url: str, base: str | None = None) -> str: ...
```

Винятки в коді методу: `ValueError`.

Код: [crawler.py:150](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L150).

#### Метод `StrategyContext.in_scope`

```python
def in_scope(self, url: str) -> bool: ...
```

Код: [crawler.py:156](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L156).

#### Метод `StrategyContext.section_for`

```python
def section_for(self, url: str) -> str | None: ...
```

Код: [crawler.py:159](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L159).

#### Метод `StrategyContext.extract_links`

```python
def extract_links(
    self,
    resource: FetchedResource,
    selector: LinkSelector | None = None,
) -> list[str]: ...
```

Код: [crawler.py:162](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L162).

#### Метод `StrategyContext.extract_links_from`

```python
def extract_links_from(
    self,
    resource: FetchedResource,
    sources: Sequence[str] = ('a_href',),
) -> list[str]: ...
```

Код: [crawler.py:165](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L165).

#### Метод `StrategyContext.is_cancelled`

```python
def is_cancelled(self) -> bool: ...
```

Код: [crawler.py:170](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L170).

## Функції

### Функція `new_stats`

```python
def new_stats() -> dict[str, Any]: ...
```

Код: [crawler.py:84](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L84).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `NOT_FOUND_STATUSES` | — | `frozenset({404, 410})` | Source answers that mean "no such material": ``not_found`` in collection errors and in ``POST /v1/fetches``. |

## Реекспорт

| Назва | Визначено в |
|---|---|
| `LeaseLost` | [`jane_web_collector.state`](jane_web_collector.state.md) |
