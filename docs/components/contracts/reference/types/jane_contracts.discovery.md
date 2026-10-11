# Модуль `jane_contracts.discovery`

> Згенеровано `scripts/docs_reference.py` з [contracts/python/src/jane_contracts/discovery.py](../../../../../contracts/python/src/jane_contracts/discovery.py). Не редагуйте вручну.

Material discovery strategy contract for the Web Collector.

Owners: WP-02 implements the core (fetcher, scope, robots, normalization, frontier with dedup and priorities, depth, revisit, per-host limits, state persistence) and the strategy registry plus the ``seed_list`` and ``recursive`` strategies. WP-03 implements ``sitemap``, ``feed``, ``listing``, ``url_template`` and ``api_feed`` against this protocol.

``llm_explore`` is NOT implemented by the collector in v1: the strategy registry reports it as unsupported (``POST /v1/rules/validations`` answers ``supported: false``; a collection with it fails validation). LLM-driven source exploration is done by the assistant's onboarding (WP-11, ``assistant.v1``), which turns its findings into ordinary strategies (seed_list, sitemap, listing, …) in the proposed rules.

Division of responsibility (see contracts/docs/discovery-strategy.md):

* A strategy only *proposes* candidate URLs (:class:`DiscoveredUrl`). It never performs HTTP itself: all network access goes through :meth:`DiscoveryContext.fetch`, which applies scope, exclusions, robots.txt, rate limits, redirects, size limits and conditional requests.
* The core normalizes, checks scope and exclusions, deduplicates, enforces ``limits.crawl.max_depth`` and ``max_frontier_size``, orders by priority and decides what is emitted as a Material.
* Strategies are configured with the validated strategy object from CollectorRules (``contracts/schemas/collector-rules.schema.json#/$defs/Strategy``); ``type_name`` equals its ``type``.
* Strategy state must be JSON-serialisable (:meth:`DiscoveryStrategy.snapshot`) so a killed collection resumes without re-emitting everything.

Registration: WP-03 exposes ``STRATEGIES: list[type[DiscoveryStrategy]]`` in its package ``strategies/discovery/__init__.py``; the WP-02 registry imports that list at start-up.

Version 1.1 (WP-16, backward compatible: every 1.0 strategy works unchanged):

* :meth:`DiscoveryContext.fetch` documents exactly what it shares with the core and what it returns (R03), and takes ``method="POST"`` with a JSON ``body`` for API pages (R22);
* :meth:`DiscoveryContext.emit_material` emits a JSON item of an API page as a Material (R22);
* :class:`RefreshingStrategy` - an optional hook: pages a strategy lists materials from (listing pages) are re-read in every run instead of being skipped by ``revisit`` or answered 304 (R23).

## Зміст

- [Клас `DiscoveredUrl`](#клас-discoveredurl)
- [Клас `FetchedResource`](#клас-fetchedresource)
- [Клас `LinkSelector`](#клас-linkselector)
- [Клас `DiscoveredMaterial`](#клас-discoveredmaterial)
- [Клас `FetchRejected`](#клас-fetchrejected)
- [Клас `DiscoveryContext`](#клас-discoverycontext)
- [Клас `DiscoveryStrategy`](#клас-discoverystrategy)
- [Клас `RefreshingStrategy`](#клас-refreshingstrategy)
- [Клас `StrategyRegistry`](#клас-strategyregistry)

## Класи

### Клас `DiscoveredUrl`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_contracts.discovery` |
| Код | [discovery.py:54](../../../../../contracts/python/src/jane_contracts/discovery.py#L54) |

```python
@dataclass(frozen=True, slots=True)
class DiscoveredUrl: ...
```

A candidate URL proposed by a strategy. The core may drop it (scope, robots, dedup, depth).

``lastmod`` - when the source says the URL last changed (sitemap ``lastmod``, feed ``updated``, API ``lastmod_path``). In an ``incremental`` collection a ``lastmod`` later than the previous fetch of the URL (the URL history of the ``state_key``) makes the core fetch it although ``revisit`` would skip it; an older or missing ``lastmod`` never prevents a fetch that ``revisit`` allows.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `url` | `str` | — | читання |  |
| `strategy_id` | `str` | — | читання |  |
| `kind` | `UrlKind` | `'material'` | читання |  |
| `priority` | `int` | `0` | читання |  |
| `depth` | `int` | `0` | читання |  |
| `parent_url` | `str \| None` | `None` | читання |  |
| `section` | `str \| None` | `None` | читання |  |
| `lastmod` | `datetime \| None` | `None` | читання |  |
| `metadata` | `Mapping[str, Any]` | `field(default_factory=dict)` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `FetchedResource`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_contracts.discovery` |
| Код | [discovery.py:74](../../../../../contracts/python/src/jane_contracts/discovery.py#L74) |

```python
@dataclass(frozen=True, slots=True)
class FetchedResource: ...
```

A response obtained through :meth:`DiscoveryContext.fetch` (already within limits).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `url` | `str` | — | читання |  |
| `final_url` | `str` | — | читання |  |
| `status` | `int` | — | читання |  |
| `media_type` | `str` | — | читання |  |
| `headers` | `Mapping[str, str]` | — | читання |  |
| `body` | `bytes` | — | читання |  |
| `fetched_at` | `datetime` | — | читання |  |
| `depth` | `int` | — | читання |  |
| `strategy_id` | `str \| None` | — | читання |  |
| `kind` | `UrlKind` | — | читання |  |
| `truncated` | `bool` | `False` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `LinkSelector`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_contracts.discovery` |
| Код | [discovery.py:91](../../../../../contracts/python/src/jane_contracts/discovery.py#L91) |

```python
@dataclass(frozen=True, slots=True)
class LinkSelector: ...
```

Mirrors CollectorRules ``$defs/Selector``.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `value` | `str` | — | читання |  |
| `type` | `Literal['css', 'xpath', 'rel']` | `'css'` | читання |  |
| `attribute` | `str` | `'href'` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `DiscoveredMaterial`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_contracts.discovery` |
| Код | [discovery.py:100](../../../../../contracts/python/src/jane_contracts/discovery.py#L100) |

```python
@dataclass(frozen=True, slots=True)
class DiscoveredMaterial: ...
```

A material whose content the strategy already has: one JSON item of an API page (``api_feed`` with ``emit_items_as_materials``). :meth:`DiscoveryContext.emit_material` turns it into a Material.

``url`` identifies the material (``material_id`` from its canonical URL, as for a fetched page) and is not fetched; ``body`` is the content as is (``media_type``, UTF-8 for text); ``fetched_at`` is when the page it comes from was fetched; ``parent_url`` is that page.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `url` | `str` | — | читання |  |
| `strategy_id` | `str` | — | читання |  |
| `body` | `bytes` | — | читання |  |
| `fetched_at` | `datetime` | — | читання |  |
| `media_type` | `str` | `'application/json'` | читання |  |
| `depth` | `int` | `0` | читання |  |
| `parent_url` | `str \| None` | `None` | читання |  |
| `section` | `str \| None` | `None` | читання |  |
| `lastmod` | `datetime \| None` | `None` | читання |  |
| `metadata` | `Mapping[str, Any]` | `field(default_factory=dict)` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `FetchRejected`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_contracts.discovery` |
| Успадкування | `Exception` |
| Код | [discovery.py:120](../../../../../contracts/python/src/jane_contracts/discovery.py#L120) |

```python
class FetchRejected(Exception): ...
```

Raised by :meth:`DiscoveryContext.fetch` when policy forbids the request.

``code`` is a Problem code: ``out_of_scope`` (the URL or a redirect hop), ``access_denied_by_policy`` (robots.txt, outbound address policy), ``limit_exceeded`` (only a run budget: ``crawl.max_pages_per_run``, ``crawl.max_bytes_per_run``) or ``rate_limited`` (the source asks to wait longer than the configured maximum: ``Retry-After`` / ``Crawl-delay`` above the collector's limit, or 429 after the retries). A strategy skips the URL; ``limit_exceeded`` and ``rate_limited`` mean "stop asking this run".

#### Конструктор `FetchRejected.__init__`

```python
def __init__(self, code: str, message: str) -> None: ...
```

Код: [discovery.py:130](../../../../../contracts/python/src/jane_contracts/discovery.py#L130).

### Клас `DiscoveryContext`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_contracts.discovery` |
| Успадкування | `Protocol` |
| Код | [discovery.py:135](../../../../../contracts/python/src/jane_contracts/discovery.py#L135) |

```python
class DiscoveryContext(Protocol): ...
```

Services the Web Collector core provides to a running strategy.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `source_id` | `str \| None` | — | читання й запис |  |
| `collection_id` | `str` | — | читання й запис |  |
| `rules` | `Mapping[str, Any]` | — | читання й запис | The full validated WebRules document. |
| `limits` | `Mapping[str, Any]` | — | читання й запис | Effective Limits (read-only); strategy-level ``limits`` are already merged in. |
| `log` | `logging.Logger` | — | читання й запис |  |

#### Метод `DiscoveryContext.fetch`

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

Fetch through the core with exactly the policy and resources of the frontier's own fetches:

* shared with the core: scope and ``exclude`` (also for every redirect hop), robots.txt (or the owner policy), the outbound address policy, the per-host limits of the collector (interval, parallelism, ``Crawl-delay``, ``Retry-After``; shared with every collection and one-shot fetch of the collector), retries, size limit (``crawl.max_material_bytes``, ``truncated``), the run budgets (``crawl.max_pages_per_run``, ``max_bytes_per_run``: a fetch counts like any other), the URL history of the ``state_key`` and backpressure for ``kind="material"``; timeouts come from the strategy's limits;
* the URL joins the frontier of the collection (one row per canonical URL): a ``material`` is emitted as a Material like a frontier page; a ``navigation`` document is never emitted;
* the resource is passed to :meth:`DiscoveryStrategy.on_fetched` of every **other** strategy (not back to the caller, which has it already).

Returns the resource with any final status except 304 (a 404 is a resource: ``url_template`` counts misses with it). Returns ``None`` when: not modified (``conditional=True`` and the URL history has a validator, 304); already fetched in this process for this collection, or already done as a material; a redirect leads to a URL already known; the fetch failed after the retries (network error, 5xx) - the core records it in the collection errors. ``revisit`` is not applied: a strategy asks for what it needs.

``method="POST"`` sends ``body`` as JSON (``Content-Type: application/json``) and is allowed only for ``kind="navigation"`` (``ValueError`` otherwise); it is never conditional; 307/308 redirects repeat the POST, 301/302/303 continue with GET; retries follow the same policy as GET, so it must be a read-only query of the source (an API search or listing).

Raises :class:`FetchRejected` on policy violations (see its codes).

Код: [discovery.py:146](../../../../../contracts/python/src/jane_contracts/discovery.py#L146).

#### Метод `DiscoveryContext.emit_material`

```python
async def emit_material(self, item: DiscoveredMaterial) -> bool: ...
```

Emit content the strategy already has as a Material (``api_feed`` JSON items). The core applies the same rules as to a fetched page: ``item.url`` is normalized and must be in scope (robots.txt is not consulted: nothing is fetched), the strategy's ``crawl.max_depth``, one material per canonical URL in a collection (the URL is claimed in the frontier, so no other strategy fetches it again in this collection), ``revisit``/``dedup`` against the URL history in ``incremental`` collections (``lastmod`` newer than the last observation forces it), backpressure. Returns ``True`` if a Material was emitted, ``False`` if the item was dropped (out of scope, too deep, duplicate, unchanged).

Код: [discovery.py:182](../../../../../contracts/python/src/jane_contracts/discovery.py#L182).

#### Метод `DiscoveryContext.normalize`

```python
def normalize(self, url: str, base: str | None = None) -> str: ...
```

Resolve relative URLs and apply CollectorRules ``normalization``.

Код: [discovery.py:192](../../../../../contracts/python/src/jane_contracts/discovery.py#L192).

#### Метод `DiscoveryContext.in_scope`

```python
def in_scope(self, url: str) -> bool: ...
```

Код: [discovery.py:196](../../../../../contracts/python/src/jane_contracts/discovery.py#L196).

#### Метод `DiscoveryContext.section_for`

```python
def section_for(self, url: str) -> str | None: ...
```

Код: [discovery.py:198](../../../../../contracts/python/src/jane_contracts/discovery.py#L198).

#### Метод `DiscoveryContext.extract_links`

```python
def extract_links(
    self,
    resource: FetchedResource,
    selector: LinkSelector | None = None,
) -> list[str]: ...
```

Links from an HTML resource (``a[href]`` by default), normalized and absolute.

Код: [discovery.py:200](../../../../../contracts/python/src/jane_contracts/discovery.py#L200).

#### Метод `DiscoveryContext.is_cancelled`

```python
def is_cancelled(self) -> bool: ...
```

Код: [discovery.py:204](../../../../../contracts/python/src/jane_contracts/discovery.py#L204).

### Клас `DiscoveryStrategy`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_contracts.discovery` |
| Успадкування | `Protocol` |
| Код | [discovery.py:208](../../../../../contracts/python/src/jane_contracts/discovery.py#L208) |

```python
@runtime_checkable
class DiscoveryStrategy(Protocol): ...
```

One material discovery mode. Instances live for one collection run.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `type_name` | `ClassVar[str]` | — | читання | Equals the strategy ``type`` in CollectorRules, e.g. ``"sitemap"``. |

#### Конструктор `DiscoveryStrategy.__init__`

```python
def __init__(self, config: Mapping[str, Any], strategy_id: str) -> None: ...
```

``config`` is the validated strategy object; ``strategy_id`` is its id or a generated one.

Код: [discovery.py:214](../../../../../contracts/python/src/jane_contracts/discovery.py#L214).

#### Метод `DiscoveryStrategy.seeds`

```python
def seeds(self, ctx: DiscoveryContext) -> AsyncIterator[DiscoveredUrl]: ...
```

Initial candidates. May fetch navigation documents (sitemaps, feeds, API pages).

Код: [discovery.py:218](../../../../../contracts/python/src/jane_contracts/discovery.py#L218).

#### Метод `DiscoveryStrategy.on_fetched`

```python
def on_fetched(
    self,
    resource: FetchedResource,
    ctx: DiscoveryContext,
) -> AsyncIterator[DiscoveredUrl]: ...
```

Called by the core for every fetched resource (from any strategy), so strategies combine: e.g. ``recursive`` follows links from pages found by ``sitemap``. Strategies that do not react to other pages yield nothing.

"Fetched" means an HTTP response with a body, **whatever its status**: 2xx, and also 4xx (404, 410, 403...) and 5xx that are not retried; check ``resource.status`` (``url_template`` counts 404/410 as misses, ``listing`` stops a chain on a non-2xx page). Not called for: 304 (nothing new; ``recursive`` gets the stored links of the page instead), a page skipped by ``revisit``, a redirect to an already known URL, a page whose final or ``rel=canonical`` URL is already known in the collection (a duplicate), a failed fetch (retried statuses 429/500/502/503/504 that stayed failing, network errors) and a refused one. A resource fetched through :meth:`DiscoveryContext.fetch` goes to every strategy except the caller.

Код: [discovery.py:222](../../../../../contracts/python/src/jane_contracts/discovery.py#L222).

#### Метод `DiscoveryStrategy.snapshot`

```python
def snapshot(self) -> Mapping[str, Any]: ...
```

JSON-serialisable progress state (cursor, page number, processed sitemap files).

Код: [discovery.py:236](../../../../../contracts/python/src/jane_contracts/discovery.py#L236).

#### Метод `DiscoveryStrategy.restore`

```python
def restore(self, state: Mapping[str, Any]) -> None: ...
```

Restore state saved by :meth:`snapshot` after a restart.

Код: [discovery.py:240](../../../../../contracts/python/src/jane_contracts/discovery.py#L240).

### Клас `RefreshingStrategy`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_contracts.discovery` |
| Успадкування | `Protocol` |
| Код | [discovery.py:246](../../../../../contracts/python/src/jane_contracts/discovery.py#L246) |

```python
@runtime_checkable
class RefreshingStrategy(Protocol): ...
```

Optional hook of a :class:`DiscoveryStrategy` (contract 1.1).

A strategy that finds new materials on pages it already knows (``listing``: category, pagination and search pages) answers ``True`` for such a URL. The core then fetches the page in full in every run - it is not skipped by ``revisit`` in an ``incremental`` collection and never sent as a conditional request (no 304)
- so :meth:`DiscoveryStrategy.on_fetched` sees the current page. The materials it lists still follow ``revisit``. Asked when the URL is about to be fetched; strategies without the method are never asked.

#### Метод `RefreshingStrategy.refresh_on_revisit`

```python
def refresh_on_revisit(self, url: str) -> bool: ...
```

Код: [discovery.py:255](../../../../../contracts/python/src/jane_contracts/discovery.py#L255).

### Клас `StrategyRegistry`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_contracts.discovery` |
| Успадкування | `Protocol` |
| Код | [discovery.py:258](../../../../../contracts/python/src/jane_contracts/discovery.py#L258) |

```python
class StrategyRegistry(Protocol): ...
```

Registry owned by WP-02.

#### Метод `StrategyRegistry.register`

```python
def register(self, strategy: type[DiscoveryStrategy]) -> None: ...
```

Код: [discovery.py:261](../../../../../contracts/python/src/jane_contracts/discovery.py#L261).

#### Метод `StrategyRegistry.get`

```python
def get(self, type_name: str) -> type[DiscoveryStrategy]: ...
```

Raises ``KeyError`` for unknown types (collector answers ``supported: false``).

Код: [discovery.py:263](../../../../../contracts/python/src/jane_contracts/discovery.py#L263).

#### Метод `StrategyRegistry.types`

```python
def types(self) -> Sequence[str]: ...
```

Код: [discovery.py:267](../../../../../contracts/python/src/jane_contracts/discovery.py#L267).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `UrlKind` | — | `Literal['material', 'navigation']` | ``material`` — candidate content page (emitted as Material if fetched successfully); ``navigation`` — fetched only to discover more URLs (sitemap, feed, listing page, API page). |
| `HttpMethod` | — | `Literal['GET', 'POST']` | ``POST`` (with a JSON body) only for ``navigation`` documents: API pages that are queried, not crawled. |
