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
| Код | [crawler.py:175](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L175) |

```python
class CrawlRun: ...
```

#### Конструктор `CrawlRun.__init__`

```python
def __init__(self, deps: RunDeps, record: Mapping[str, Any]) -> None: ...
```

Винятки в коді методу: `ValidationFailed`.

Код: [crawler.py:176](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L176).

#### Метод `CrawlRun.scope_reason`

```python
def scope_reason(self, url: str) -> str | None: ...
```

Код: [crawler.py:289](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L289).

#### Метод `CrawlRun.section_for`

```python
def section_for(self, url: str) -> str | None: ...
```

Код: [crawler.py:294](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L294).

#### Метод `CrawlRun.rule_priority`

```python
def rule_priority(self, url: str) -> int: ...
```

Код: [crawler.py:300](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L300).

#### Метод `CrawlRun.extract_links`

```python
def extract_links(
    self,
    resource: FetchedResource,
    selector: LinkSelector | None = None,
    sources: Sequence[str] = ('a_href',),
) -> list[str]: ...
```

Код: [crawler.py:306](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L306).

#### Метод `CrawlRun.robots_allowed`

```python
async def robots_allowed(self, url: str) -> bool: ...
```

Код: [crawler.py:353](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L353).

#### Метод `CrawlRun.admit`

```python
def admit(
    self,
    candidates: Sequence[DiscoveredUrl],
    parent_depth: int | None,
) -> list[FrontierRow]: ...
```

Normalize and filter candidates (scope, depth); insert bounds the queue and spools its overflow.

Код: [crawler.py:382](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L382).

#### Метод `CrawlRun.insert_rows`

```python
def insert_rows(self, db: Any, rows: Iterable[FrontierRow], *, immediate: bool = False) -> None: ...
```

Код: [crawler.py:416](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L416).

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

Код: [crawler.py:574](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L574).

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

Код: [crawler.py:905](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L905).

#### Метод `CrawlRun.emit_for_strategy`

```python
async def emit_for_strategy(self, item: DiscoveredMaterial, *, caller: str) -> bool: ...
```

``DiscoveryContext.emit_material``: content a strategy already has (an API item) as a Material, under the rules of a fetched page - scope, depth, one material per canonical URL in the collection, ``revisit`` and ``dedup`` against the URL history, backpressure, one fenced transaction (R22).

Винятки в коді методу: `JobCancelledError`.

Код: [crawler.py:995](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L995).

#### Метод `CrawlRun.execute`

```python
async def execute(self, job: JobContext | None = None) -> dict[str, Any]: ...
```

Винятки в коді методу: `RuntimeError`.

Код: [crawler.py:1221](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L1221).

### Клас `RunDeps`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_web_collector.crawler` |
| Код | [crawler.py:98](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L98) |

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
| Код | [crawler.py:123](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L123) |

```python
class StrategyContext: ...
```

``DiscoveryContext`` given to one strategy (its own merged limits).

#### Конструктор `StrategyContext.__init__`

```python
def __init__(self, run: CrawlRun, strategy_id: str, limits: Mapping[str, Any]) -> None: ...
```

Код: [crawler.py:126](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L126).

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

Код: [crawler.py:135](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L135).

#### Метод `StrategyContext.emit_material`

```python
async def emit_material(self, item: DiscoveredMaterial) -> bool: ...
```

Код: [crawler.py:148](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L148).

#### Метод `StrategyContext.normalize`

```python
def normalize(self, url: str, base: str | None = None) -> str: ...
```

Винятки в коді методу: `ValueError`.

Код: [crawler.py:151](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L151).

#### Метод `StrategyContext.in_scope`

```python
def in_scope(self, url: str) -> bool: ...
```

Код: [crawler.py:157](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L157).

#### Метод `StrategyContext.section_for`

```python
def section_for(self, url: str) -> str | None: ...
```

Код: [crawler.py:160](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L160).

#### Метод `StrategyContext.extract_links`

```python
def extract_links(
    self,
    resource: FetchedResource,
    selector: LinkSelector | None = None,
) -> list[str]: ...
```

Код: [crawler.py:163](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L163).

#### Метод `StrategyContext.extract_links_from`

```python
def extract_links_from(
    self,
    resource: FetchedResource,
    sources: Sequence[str] = ('a_href',),
) -> list[str]: ...
```

Код: [crawler.py:166](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L166).

#### Метод `StrategyContext.is_cancelled`

```python
def is_cancelled(self) -> bool: ...
```

Код: [crawler.py:171](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L171).

## Функції

### Функція `new_stats`

```python
def new_stats() -> dict[str, Any]: ...
```

Код: [crawler.py:85](../../../../../services/web-collector/src/jane_web_collector/crawler.py#L85).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `NOT_FOUND_STATUSES` | — | `frozenset({404, 410})` | Source answers that mean "no such material": ``not_found`` in collection errors and in ``POST /v1/fetches``. |

## Реекспорт

| Назва | Визначено в |
|---|---|
| `LeaseLost` | [`jane_web_collector.state`](jane_web_collector.state.md) |
