# jane_web_collector.crawler

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.crawler.LeaseLost](#jane_web_collectorcrawlerleaselost)
- [jane_web_collector.crawler.NOT_FOUND_STATUSES](#jane_web_collectorcrawlernot_found_statuses)
- [jane_web_collector.crawler.new_stats](#jane_web_collectorcrawlernew_stats)
- [jane_web_collector.crawler.RunDeps](#jane_web_collectorcrawlerrundeps)
- [jane_web_collector.crawler.RunDeps.__init__](#jane_web_collectorcrawlerrundeps__init__)
- [jane_web_collector.crawler.RunDeps.state](#jane_web_collectorcrawlerrundepsstate)
- [jane_web_collector.crawler.RunDeps.registry](#jane_web_collectorcrawlerrundepsregistry)
- [jane_web_collector.crawler.RunDeps.client](#jane_web_collectorcrawlerrundepsclient)
- [jane_web_collector.crawler.RunDeps.resolve](#jane_web_collectorcrawlerrundepsresolve)
- [jane_web_collector.crawler.RunDeps.transit](#jane_web_collectorcrawlerrundepstransit)
- [jane_web_collector.crawler.RunDeps.instance_id](#jane_web_collectorcrawlerrundepsinstance_id)
- [jane_web_collector.crawler.RunDeps.lease_seconds](#jane_web_collectorcrawlerrundepslease_seconds)
- [jane_web_collector.crawler.RunDeps.heartbeat_seconds](#jane_web_collectorcrawlerrundepsheartbeat_seconds)
- [jane_web_collector.crawler.RunDeps.user_agent](#jane_web_collectorcrawlerrundepsuser_agent)
- [jane_web_collector.crawler.RunDeps.version](#jane_web_collectorcrawlerrundepsversion)
- [jane_web_collector.crawler.RunDeps.host_limiter](#jane_web_collectorcrawlerrundepshost_limiter)
- [jane_web_collector.crawler.RunDeps.connection_policy](#jane_web_collectorcrawlerrundepsconnection_policy)
- [jane_web_collector.crawler.RunDeps.ack_events](#jane_web_collectorcrawlerrundepsack_events)
- [jane_web_collector.crawler.RunDeps.renderer](#jane_web_collectorcrawlerrundepsrenderer)
- [jane_web_collector.crawler.StrategyContext](#jane_web_collectorcrawlerstrategycontext)
- [jane_web_collector.crawler.StrategyContext.__init__](#jane_web_collectorcrawlerstrategycontext__init__)
- [jane_web_collector.crawler.StrategyContext.strategy_id](#jane_web_collectorcrawlerstrategycontextstrategy_id)
- [jane_web_collector.crawler.StrategyContext.source_id](#jane_web_collectorcrawlerstrategycontextsource_id)
- [jane_web_collector.crawler.StrategyContext.collection_id](#jane_web_collectorcrawlerstrategycontextcollection_id)
- [jane_web_collector.crawler.StrategyContext.rules](#jane_web_collectorcrawlerstrategycontextrules)
- [jane_web_collector.crawler.StrategyContext.limits](#jane_web_collectorcrawlerstrategycontextlimits)
- [jane_web_collector.crawler.StrategyContext.log](#jane_web_collectorcrawlerstrategycontextlog)
- [jane_web_collector.crawler.StrategyContext.fetch](#jane_web_collectorcrawlerstrategycontextfetch)
- [jane_web_collector.crawler.StrategyContext.emit_material](#jane_web_collectorcrawlerstrategycontextemit_material)
- [jane_web_collector.crawler.StrategyContext.normalize](#jane_web_collectorcrawlerstrategycontextnormalize)
- [jane_web_collector.crawler.StrategyContext.in_scope](#jane_web_collectorcrawlerstrategycontextin_scope)
- [jane_web_collector.crawler.StrategyContext.section_for](#jane_web_collectorcrawlerstrategycontextsection_for)
- [jane_web_collector.crawler.StrategyContext.extract_links](#jane_web_collectorcrawlerstrategycontextextract_links)
- [jane_web_collector.crawler.StrategyContext.extract_links_from](#jane_web_collectorcrawlerstrategycontextextract_links_from)
- [jane_web_collector.crawler.StrategyContext.is_cancelled](#jane_web_collectorcrawlerstrategycontextis_cancelled)
- [jane_web_collector.crawler.CrawlRun](#jane_web_collectorcrawlercrawlrun)
- [jane_web_collector.crawler.CrawlRun.__init__](#jane_web_collectorcrawlercrawlrun__init__)
- [jane_web_collector.crawler.CrawlRun.deps](#jane_web_collectorcrawlercrawlrundeps)
- [jane_web_collector.crawler.CrawlRun.state](#jane_web_collectorcrawlercrawlrunstate)
- [jane_web_collector.crawler.CrawlRun.collection_id](#jane_web_collectorcrawlercrawlruncollection_id)
- [jane_web_collector.crawler.CrawlRun.state_key](#jane_web_collectorcrawlercrawlrunstate_key)
- [jane_web_collector.crawler.CrawlRun.request](#jane_web_collectorcrawlercrawlrunrequest)
- [jane_web_collector.crawler.CrawlRun.rules](#jane_web_collectorcrawlercrawlrunrules)
- [jane_web_collector.crawler.CrawlRun.rules_ref](#jane_web_collectorcrawlercrawlrunrules_ref)
- [jane_web_collector.crawler.CrawlRun.source_id](#jane_web_collectorcrawlercrawlrunsource_id)
- [jane_web_collector.crawler.CrawlRun.mode](#jane_web_collectorcrawlercrawlrunmode)
- [jane_web_collector.crawler.CrawlRun.meta](#jane_web_collectorcrawlercrawlrunmeta)
- [jane_web_collector.crawler.CrawlRun.stats](#jane_web_collectorcrawlercrawlrunstats)
- [jane_web_collector.crawler.CrawlRun.counters](#jane_web_collectorcrawlercrawlruncounters)
- [jane_web_collector.crawler.CrawlRun.resolved](#jane_web_collectorcrawlercrawlrunresolved)
- [jane_web_collector.crawler.CrawlRun.limits](#jane_web_collectorcrawlercrawlrunlimits)
- [jane_web_collector.crawler.CrawlRun.normalizer](#jane_web_collectorcrawlercrawlrunnormalizer)
- [jane_web_collector.crawler.CrawlRun.scope](#jane_web_collectorcrawlercrawlrunscope)
- [jane_web_collector.crawler.CrawlRun.sections](#jane_web_collectorcrawlercrawlrunsections)
- [jane_web_collector.crawler.CrawlRun.priority_rules](#jane_web_collectorcrawlercrawlrunpriority_rules)
- [jane_web_collector.crawler.CrawlRun.owner_policy](#jane_web_collectorcrawlercrawlrunowner_policy)
- [jane_web_collector.crawler.CrawlRun.user_agent](#jane_web_collectorcrawlercrawlrunuser_agent)
- [jane_web_collector.crawler.CrawlRun.render_js](#jane_web_collectorcrawlercrawlrunrender_js)
- [jane_web_collector.crawler.CrawlRun.dedup_key](#jane_web_collectorcrawlercrawlrundedup_key)
- [jane_web_collector.crawler.CrawlRun.use_link_canonical](#jane_web_collectorcrawlercrawlrunuse_link_canonical)
- [jane_web_collector.crawler.CrawlRun.revisit_mode](#jane_web_collectorcrawlercrawlrunrevisit_mode)
- [jane_web_collector.crawler.CrawlRun.delivery](#jane_web_collectorcrawlercrawlrundelivery)
- [jane_web_collector.crawler.CrawlRun.accept](#jane_web_collectorcrawlercrawlrunaccept)
- [jane_web_collector.crawler.CrawlRun.accept_language](#jane_web_collectorcrawlercrawlrunaccept_language)
- [jane_web_collector.crawler.CrawlRun.host_session](#jane_web_collectorcrawlercrawlrunhost_session)
- [jane_web_collector.crawler.CrawlRun.robots_fetcher](#jane_web_collectorcrawlercrawlrunrobots_fetcher)
- [jane_web_collector.crawler.CrawlRun.robots](#jane_web_collectorcrawlercrawlrunrobots)
- [jane_web_collector.crawler.CrawlRun.fetcher](#jane_web_collectorcrawlercrawlrunfetcher)
- [jane_web_collector.crawler.CrawlRun.strategies](#jane_web_collectorcrawlercrawlrunstrategies)
- [jane_web_collector.crawler.CrawlRun.cancelled](#jane_web_collectorcrawlercrawlruncancelled)
- [jane_web_collector.crawler.CrawlRun.stop_reason](#jane_web_collectorcrawlercrawlrunstop_reason)
- [jane_web_collector.crawler.CrawlRun.fetched_here](#jane_web_collectorcrawlercrawlrunfetched_here)
- [jane_web_collector.crawler.CrawlRun.fence](#jane_web_collectorcrawlercrawlrunfence)
- [jane_web_collector.crawler.CrawlRun.strategy_limits](#jane_web_collectorcrawlercrawlrunstrategy_limits)
- [jane_web_collector.crawler.CrawlRun.scope_reason](#jane_web_collectorcrawlercrawlrunscope_reason)
- [jane_web_collector.crawler.CrawlRun.section_for](#jane_web_collectorcrawlercrawlrunsection_for)
- [jane_web_collector.crawler.CrawlRun.rule_priority](#jane_web_collectorcrawlercrawlrunrule_priority)
- [jane_web_collector.crawler.CrawlRun.extract_links](#jane_web_collectorcrawlercrawlrunextract_links)
- [jane_web_collector.crawler.CrawlRun.robots_allowed](#jane_web_collectorcrawlercrawlrunrobots_allowed)
- [jane_web_collector.crawler.CrawlRun.admit](#jane_web_collectorcrawlercrawlrunadmit)
- [jane_web_collector.crawler.CrawlRun.insert_rows](#jane_web_collectorcrawlercrawlruninsert_rows)
- [jane_web_collector.crawler.CrawlRun.handle](#jane_web_collectorcrawlercrawlrunhandle)
- [jane_web_collector.crawler.CrawlRun.fetch_for_strategy](#jane_web_collectorcrawlercrawlrunfetch_for_strategy)
- [jane_web_collector.crawler.CrawlRun.emit_for_strategy](#jane_web_collectorcrawlercrawlrunemit_for_strategy)
- [jane_web_collector.crawler.CrawlRun.execute](#jane_web_collectorcrawlercrawlrunexecute)

## jane_web_collector.crawler.LeaseLost

**Повторний експорт.** Код: [services/web-collector/src/jane_web_collector/crawler.py:56](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L56).

```python
from jane_web_collector.state import LeaseLost as LeaseLost
```

Повторний експорт: [jane_web_collector.state.LeaseLost](jane_web_collector.state.md#jane_web_collectorstateleaselost).

## jane_web_collector.crawler.NOT_FOUND_STATUSES

**Константа.** Код: [services/web-collector/src/jane_web_collector/crawler.py:61](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L61).

```python
NOT_FOUND_STATUSES = frozenset({404, 410})
```

### Опис із вихідного коду

```text
Source answers that mean "no such material": ``not_found`` in collection errors and in ``POST /v1/fetches``.
```

## jane_web_collector.crawler.new_stats

**Функція.** Код: [services/web-collector/src/jane_web_collector/crawler.py:84](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L84).

```python
def new_stats() -> dict[str, Any]:
```

Результат: `dict[str, Any]`.

## jane_web_collector.crawler.RunDeps

**Клас.** Код: [services/web-collector/src/jane_web_collector/crawler.py:97](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L97).

```python
class RunDeps:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [state](jane_web_collector.crawler.md#jane_web_collectorcrawlerrundepsstate) | Поле | ні |
| [registry](jane_web_collector.crawler.md#jane_web_collectorcrawlerrundepsregistry) | Поле | ні |
| [client](jane_web_collector.crawler.md#jane_web_collectorcrawlerrundepsclient) | Поле | ні |
| [resolve](jane_web_collector.crawler.md#jane_web_collectorcrawlerrundepsresolve) | Поле | ні |
| [transit](jane_web_collector.crawler.md#jane_web_collectorcrawlerrundepstransit) | Поле | ні |
| [instance_id](jane_web_collector.crawler.md#jane_web_collectorcrawlerrundepsinstance_id) | Поле | ні |
| [lease_seconds](jane_web_collector.crawler.md#jane_web_collectorcrawlerrundepslease_seconds) | Поле | ні |
| [heartbeat_seconds](jane_web_collector.crawler.md#jane_web_collectorcrawlerrundepsheartbeat_seconds) | Поле | ні |
| [user_agent](jane_web_collector.crawler.md#jane_web_collectorcrawlerrundepsuser_agent) | Поле | ні |
| [version](jane_web_collector.crawler.md#jane_web_collectorcrawlerrundepsversion) | Поле | ні |
| [host_limiter](jane_web_collector.crawler.md#jane_web_collectorcrawlerrundepshost_limiter) | Поле | ні |
| [connection_policy](jane_web_collector.crawler.md#jane_web_collectorcrawlerrundepsconnection_policy) | Поле | ні |
| [ack_events](jane_web_collector.crawler.md#jane_web_collectorcrawlerrundepsack_events) | Поле | ні |
| [renderer](jane_web_collector.crawler.md#jane_web_collectorcrawlerrundepsrenderer) | Поле | ні |
| [__init__](jane_web_collector.crawler.md#jane_web_collectorcrawlerrundeps__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Service-level dependencies shared by all runs.
```

## jane_web_collector.crawler.RunDeps.__init__

**Конструктор dataclass.** Код: [services/web-collector/src/jane_web_collector/crawler.py:97](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L97).

```python
def __init__(self, state: StateStore, registry: Registry, client: httpx.AsyncClient, resolve: Callable[..., ResolvedLimits[ServiceLimits]], transit: TransitStore | None, instance_id: str, lease_seconds: float, heartbeat_seconds: float, user_agent: str, version: str, host_limiter: HostLimiter, connection_policy: ConnectionPolicy = <factory ConnectionPolicy>, ack_events: dict[str, asyncio.Event] = <factory dict>, renderer: Renderer | None = None) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `state` | `StateStore` | `—` | positional-or-keyword |
| `registry` | `Registry` | `—` | positional-or-keyword |
| `client` | `httpx.AsyncClient` | `—` | positional-or-keyword |
| `resolve` | `Callable[..., ResolvedLimits[ServiceLimits]]` | `—` | positional-or-keyword |
| `transit` | `TransitStore \| None` | `—` | positional-or-keyword |
| `instance_id` | `str` | `—` | positional-or-keyword |
| `lease_seconds` | `float` | `—` | positional-or-keyword |
| `heartbeat_seconds` | `float` | `—` | positional-or-keyword |
| `user_agent` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |
| `host_limiter` | `HostLimiter` | `—` | positional-or-keyword |
| `connection_policy` | `ConnectionPolicy` | `factory: ConnectionPolicy` | positional-or-keyword |
| `ack_events` | `dict[str, asyncio.Event]` | `factory: dict` | positional-or-keyword |
| `renderer` | `Renderer \| None` | `None` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.crawler.RunDeps.state

**Поле.** Код: [services/web-collector/src/jane_web_collector/crawler.py:100](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L100).

```python
state: StateStore
```

Доступ: читання — так; запис — так.

## jane_web_collector.crawler.RunDeps.registry

**Поле.** Код: [services/web-collector/src/jane_web_collector/crawler.py:101](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L101).

```python
registry: Registry
```

Доступ: читання — так; запис — так.

## jane_web_collector.crawler.RunDeps.client

**Поле.** Код: [services/web-collector/src/jane_web_collector/crawler.py:102](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L102).

```python
client: httpx.AsyncClient
```

Доступ: читання — так; запис — так.

## jane_web_collector.crawler.RunDeps.resolve

**Поле.** Код: [services/web-collector/src/jane_web_collector/crawler.py:103](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L103).

```python
resolve: Callable[..., ResolvedLimits[ServiceLimits]]
```

Доступ: читання — так; запис — так.

## jane_web_collector.crawler.RunDeps.transit

**Поле.** Код: [services/web-collector/src/jane_web_collector/crawler.py:104](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L104).

```python
transit: TransitStore | None
```

Доступ: читання — так; запис — так.

## jane_web_collector.crawler.RunDeps.instance_id

**Поле.** Код: [services/web-collector/src/jane_web_collector/crawler.py:105](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L105).

```python
instance_id: str
```

Доступ: читання — так; запис — так.

## jane_web_collector.crawler.RunDeps.lease_seconds

**Поле.** Код: [services/web-collector/src/jane_web_collector/crawler.py:106](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L106).

```python
lease_seconds: float
```

Доступ: читання — так; запис — так.

## jane_web_collector.crawler.RunDeps.heartbeat_seconds

**Поле.** Код: [services/web-collector/src/jane_web_collector/crawler.py:107](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L107).

```python
heartbeat_seconds: float
```

Доступ: читання — так; запис — так.

## jane_web_collector.crawler.RunDeps.user_agent

**Поле.** Код: [services/web-collector/src/jane_web_collector/crawler.py:108](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L108).

```python
user_agent: str
```

Доступ: читання — так; запис — так.

## jane_web_collector.crawler.RunDeps.version

**Поле.** Код: [services/web-collector/src/jane_web_collector/crawler.py:109](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L109).

```python
version: str
```

Доступ: читання — так; запис — так.

## jane_web_collector.crawler.RunDeps.host_limiter

**Поле.** Код: [services/web-collector/src/jane_web_collector/crawler.py:110](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L110).

```python
host_limiter: HostLimiter
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Per-host limits of the whole process, shared by every run and one-shot fetch.
```

## jane_web_collector.crawler.RunDeps.connection_policy

**Поле.** Код: [services/web-collector/src/jane_web_collector/crawler.py:112](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L112).

```python
connection_policy: ConnectionPolicy = field(default_factory=ConnectionPolicy)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "ConnectionPolicy"
}
```

## jane_web_collector.crawler.RunDeps.ack_events

**Поле.** Код: [services/web-collector/src/jane_web_collector/crawler.py:113](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L113).

```python
ack_events: dict[str, asyncio.Event] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_web_collector.crawler.RunDeps.renderer

**Поле.** Код: [services/web-collector/src/jane_web_collector/crawler.py:114](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L114).

```python
renderer: Renderer | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Headless browser for ``fetch.render_js`` (``None``: such URLs fail with ``not_implemented``).
```

## jane_web_collector.crawler.StrategyContext

**Клас.** Код: [services/web-collector/src/jane_web_collector/crawler.py:122](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L122).

```python
class StrategyContext:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.crawler.md#jane_web_collectorcrawlerstrategycontext__init__) | Конструктор | ні |
| [strategy_id](jane_web_collector.crawler.md#jane_web_collectorcrawlerstrategycontextstrategy_id) | Поле екземпляра | ні |
| [source_id](jane_web_collector.crawler.md#jane_web_collectorcrawlerstrategycontextsource_id) | Поле екземпляра | ні |
| [collection_id](jane_web_collector.crawler.md#jane_web_collectorcrawlerstrategycontextcollection_id) | Поле екземпляра | ні |
| [rules](jane_web_collector.crawler.md#jane_web_collectorcrawlerstrategycontextrules) | Поле екземпляра | ні |
| [limits](jane_web_collector.crawler.md#jane_web_collectorcrawlerstrategycontextlimits) | Поле екземпляра | ні |
| [log](jane_web_collector.crawler.md#jane_web_collectorcrawlerstrategycontextlog) | Поле екземпляра | ні |
| [fetch](jane_web_collector.crawler.md#jane_web_collectorcrawlerstrategycontextfetch) | Метод | ні |
| [emit_material](jane_web_collector.crawler.md#jane_web_collectorcrawlerstrategycontextemit_material) | Метод | ні |
| [normalize](jane_web_collector.crawler.md#jane_web_collectorcrawlerstrategycontextnormalize) | Метод | ні |
| [in_scope](jane_web_collector.crawler.md#jane_web_collectorcrawlerstrategycontextin_scope) | Метод | ні |
| [section_for](jane_web_collector.crawler.md#jane_web_collectorcrawlerstrategycontextsection_for) | Метод | ні |
| [extract_links](jane_web_collector.crawler.md#jane_web_collectorcrawlerstrategycontextextract_links) | Метод | ні |
| [extract_links_from](jane_web_collector.crawler.md#jane_web_collectorcrawlerstrategycontextextract_links_from) | Метод | ні |
| [is_cancelled](jane_web_collector.crawler.md#jane_web_collectorcrawlerstrategycontextis_cancelled) | Метод | ні |

### Опис із вихідного коду

```text
``DiscoveryContext`` given to one strategy (its own merged limits).
```

## jane_web_collector.crawler.StrategyContext.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/crawler.py:125](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L125).

```python
def __init__(self, run: CrawlRun, strategy_id: str, limits: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `run` | `CrawlRun` | `—` | positional-or-keyword |
| `strategy_id` | `str` | `—` | positional-or-keyword |
| `limits` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.crawler.StrategyContext.strategy_id

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:127](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L127).

```python
self.strategy_id = strategy_id
```

## jane_web_collector.crawler.StrategyContext.source_id

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:128](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L128).

```python
self.source_id = run.source_id
```

## jane_web_collector.crawler.StrategyContext.collection_id

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:129](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L129).

```python
self.collection_id = run.collection_id
```

## jane_web_collector.crawler.StrategyContext.rules

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:130](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L130).

```python
self.rules: Mapping[str, Any] = run.rules
```

## jane_web_collector.crawler.StrategyContext.limits

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:131](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L131).

```python
self.limits: Mapping[str, Any] = limits
```

## jane_web_collector.crawler.StrategyContext.log

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:132](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L132).

```python
self.log = logging.getLogger(f'jane_web_collector.strategy.{strategy_id}')
```

## jane_web_collector.crawler.StrategyContext.fetch

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:134](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L134).

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

## jane_web_collector.crawler.StrategyContext.emit_material

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:147](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L147).

```python
async def emit_material(self, item: DiscoveredMaterial) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `item` | `DiscoveredMaterial` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_web_collector.crawler.StrategyContext.normalize

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:150](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L150).

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

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_web_collector.crawler.StrategyContext.in_scope

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:156](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L156).

```python
def in_scope(self, url: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_web_collector.crawler.StrategyContext.section_for

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:159](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L159).

```python
def section_for(self, url: str) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `str | None`.

## jane_web_collector.crawler.StrategyContext.extract_links

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:162](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L162).

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

## jane_web_collector.crawler.StrategyContext.extract_links_from

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:165](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L165).

```python
def extract_links_from(self, resource: FetchedResource, sources: Sequence[str]=('a_href',)) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `resource` | `FetchedResource` | `—` | positional-or-keyword |
| `sources` | `Sequence[str]` | `('a_href',)` | positional-or-keyword |

Результат: `list[str]`.

## jane_web_collector.crawler.StrategyContext.is_cancelled

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:170](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L170).

```python
def is_cancelled(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_web_collector.crawler.CrawlRun

**Клас.** Код: [services/web-collector/src/jane_web_collector/crawler.py:174](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L174).

```python
class CrawlRun:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrun__init__) | Конструктор | ні |
| [deps](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrundeps) | Поле екземпляра | ні |
| [state](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunstate) | Поле екземпляра | ні |
| [collection_id](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlruncollection_id) | Поле екземпляра | ні |
| [state_key](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunstate_key) | Поле екземпляра | ні |
| [request](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunrequest) | Поле екземпляра | ні |
| [rules](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunrules) | Поле екземпляра | ні |
| [rules_ref](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunrules_ref) | Поле екземпляра | ні |
| [source_id](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunsource_id) | Поле екземпляра | ні |
| [mode](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunmode) | Поле екземпляра | ні |
| [meta](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunmeta) | Поле екземпляра | ні |
| [stats](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunstats) | Поле екземпляра | ні |
| [counters](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlruncounters) | Поле екземпляра | ні |
| [resolved](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunresolved) | Поле екземпляра | ні |
| [limits](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunlimits) | Поле екземпляра | ні |
| [normalizer](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunnormalizer) | Поле екземпляра | ні |
| [scope](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunscope) | Поле екземпляра | ні |
| [sections](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunsections) | Поле екземпляра | ні |
| [priority_rules](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunpriority_rules) | Поле екземпляра | ні |
| [owner_policy](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunowner_policy) | Поле екземпляра | ні |
| [user_agent](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunuser_agent) | Поле екземпляра | ні |
| [render_js](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunrender_js) | Поле екземпляра | ні |
| [dedup_key](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrundedup_key) | Поле екземпляра | ні |
| [use_link_canonical](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunuse_link_canonical) | Поле екземпляра | ні |
| [revisit_mode](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunrevisit_mode) | Поле екземпляра | ні |
| [delivery](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrundelivery) | Поле екземпляра | ні |
| [accept](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunaccept) | Поле екземпляра | ні |
| [accept_language](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunaccept_language) | Поле екземпляра | ні |
| [host_session](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunhost_session) | Поле екземпляра | ні |
| [robots_fetcher](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunrobots_fetcher) | Поле екземпляра | ні |
| [robots](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunrobots) | Поле екземпляра | ні |
| [fetcher](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunfetcher) | Поле екземпляра | ні |
| [strategies](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunstrategies) | Поле екземпляра | ні |
| [cancelled](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlruncancelled) | Поле екземпляра | ні |
| [stop_reason](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunstop_reason) | Поле екземпляра | ні |
| [fetched_here](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunfetched_here) | Поле екземпляра | ні |
| [fence](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunfence) | Поле екземпляра | ні |
| [strategy_limits](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunstrategy_limits) | Поле екземпляра | ні |
| [scope_reason](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunscope_reason) | Метод | ні |
| [section_for](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunsection_for) | Метод | ні |
| [rule_priority](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunrule_priority) | Метод | ні |
| [extract_links](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunextract_links) | Метод | ні |
| [robots_allowed](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunrobots_allowed) | Метод | ні |
| [admit](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunadmit) | Метод | ні |
| [insert_rows](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlruninsert_rows) | Метод | ні |
| [handle](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunhandle) | Метод | ні |
| [fetch_for_strategy](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunfetch_for_strategy) | Метод | ні |
| [emit_for_strategy](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunemit_for_strategy) | Метод | ні |
| [execute](jane_web_collector.crawler.md#jane_web_collectorcrawlercrawlrunexecute) | Метод | ні |

## jane_web_collector.crawler.CrawlRun.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/crawler.py:175](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L175).

```python
def __init__(self, deps: RunDeps, record: Mapping[str, Any]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `deps` | `RunDeps` | `—` | positional-or-keyword |
| `record` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.crawler.CrawlRun.deps

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:176](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L176).

```python
self.deps = deps
```

## jane_web_collector.crawler.CrawlRun.state

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:177](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L177).

```python
self.state = deps.state
```

## jane_web_collector.crawler.CrawlRun.collection_id

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:178](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L178).

```python
self.collection_id: str = record['collection_id']
```

## jane_web_collector.crawler.CrawlRun.state_key

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:179](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L179).

```python
self.state_key: str = record['state_key']
```

## jane_web_collector.crawler.CrawlRun.request

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:180](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L180).

```python
self.request: dict[str, Any] = record['request']
```

## jane_web_collector.crawler.CrawlRun.rules

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:181](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L181).

```python
self.rules: dict[str, Any] = record['rules']
```

## jane_web_collector.crawler.CrawlRun.rules_ref

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:182](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L182).

```python
self.rules_ref: dict[str, Any] | None = record.get('rules_ref')
```

## jane_web_collector.crawler.CrawlRun.source_id

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:183](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L183).

```python
self.source_id: str | None = self.request.get('source_id')
```

## jane_web_collector.crawler.CrawlRun.mode

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:184](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L184).

```python
self.mode: str = self.request.get('mode', 'full')
```

## jane_web_collector.crawler.CrawlRun.meta

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:185](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L185).

```python
self.meta: dict[str, Any] = dict(record.get('meta') or {})
```

## jane_web_collector.crawler.CrawlRun.stats

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:186](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L186).

```python
self.stats: dict[str, Any] = {**new_stats(), **(record.get('stats') or {})}
```

## jane_web_collector.crawler.CrawlRun.counters

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:187](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L187).

```python
self.counters: dict[str, int] = dict(self.meta.get('counters') or {})
```

## jane_web_collector.crawler.CrawlRun.resolved

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:188](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L188).

```python
self.resolved = deps.resolve(self.rules.get('limits'), self.request.get('limits'))
```

## jane_web_collector.crawler.CrawlRun.limits

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:189](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L189).

```python
self.limits: ServiceLimits = self.resolved.limits
```

## jane_web_collector.crawler.CrawlRun.normalizer

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:190](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L190).

```python
self.normalizer = Normalizer.from_rules(self.rules)
```

## jane_web_collector.crawler.CrawlRun.scope

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:191](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L191).

```python
self.scope = Scope.from_rules(self.rules)
```

## jane_web_collector.crawler.CrawlRun.sections

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:192](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L192).

```python
self.sections: list[tuple[str, tuple[UrlPattern, ...]]] = [(s['section_id'], compile_patterns(s['patterns'])) for s in self.rules.get('sections') or []]
```

## jane_web_collector.crawler.CrawlRun.priority_rules

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:195](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L195).

```python
self.priority_rules: list[tuple[UrlPattern, int]] = [(UrlPattern.from_rule(p['pattern']), int(p['priority'])) for p in self.rules.get('priorities') or []]
```

## jane_web_collector.crawler.CrawlRun.owner_policy

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:200](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L200).

```python
self.owner_policy = robots_cfg.get('mode') == 'owner_policy'
```

## jane_web_collector.crawler.CrawlRun.user_agent

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:203](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L203).

```python
self.user_agent: str = user_agent
```

## jane_web_collector.crawler.CrawlRun.render_js

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:204](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L204).

```python
self.render_js = bool(fetch_cfg.get('render_js'))
```

## jane_web_collector.crawler.CrawlRun.dedup_key

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:207](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L207).

```python
self.dedup_key = dedup.get('key', 'canonical_url')
```

## jane_web_collector.crawler.CrawlRun.use_link_canonical

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:208](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L208).

```python
self.use_link_canonical = bool(dedup.get('use_link_rel_canonical', True))
```

## jane_web_collector.crawler.CrawlRun.revisit_mode

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:209](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L209).

```python
self.revisit_mode = (self.rules.get('revisit') or {}).get('mode', 'never')
```

## jane_web_collector.crawler.CrawlRun.delivery

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:210](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L210).

```python
self.delivery = Delivery(mode=self.request.get('content_delivery', 'auto'), inline_max_bytes=self.limits.transfer.inline_max_bytes, transit_ttl_seconds=self.limits.transfer.transit_ttl_seconds, store=deps.transit)
```

## jane_web_collector.crawler.CrawlRun.accept

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:216](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L216).

```python
self.accept = fetch_cfg.get('accept_media_types')
```

## jane_web_collector.crawler.CrawlRun.accept_language

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:218](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L218).

```python
self.accept_language: str | None = next((v for k, v in headers.items() if k.lower() == 'accept-language'), None)
```

## jane_web_collector.crawler.CrawlRun.host_session

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:229](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L229).

```python
self.host_session = deps.host_limiter.session(self.limits)
```

## jane_web_collector.crawler.CrawlRun.robots_fetcher

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:230](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L230).

```python
self.robots_fetcher = Fetcher(deps.client, self.limits, self.host_session, user_agent=user_agent, headers=headers)
```

## jane_web_collector.crawler.CrawlRun.robots

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:233](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L233).

```python
self.robots = RobotsCache(self._fetch_robots, token, self.limits.collector.robots_cache_ttl_seconds)
```

## jane_web_collector.crawler.CrawlRun.fetcher

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:234](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L234).

```python
self.fetcher = Fetcher(deps.client, self.limits, self.host_session, user_agent=user_agent, headers=headers, auth_headers=creds, connection_policy=deps.connection_policy, crawl_delay_for=None if self.owner_policy else self._crawl_delay)
```

## jane_web_collector.crawler.CrawlRun.strategies

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:244](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L244).

```python
self.strategies: list[tuple[str, DiscoveryStrategy, StrategyContext, int]] = []
```

## jane_web_collector.crawler.CrawlRun.cancelled

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:245](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L245).

```python
self.cancelled = False
```

## jane_web_collector.crawler.CrawlRun.stop_reason

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:246](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L246).

```python
self.stop_reason: str | None = None
```

## jane_web_collector.crawler.CrawlRun.fetched_here

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:247](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L247).

```python
self.fetched_here: set[str] = set()
```

## jane_web_collector.crawler.CrawlRun.fence

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:249](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L249).

```python
self.fence = (self.collection_id, deps.instance_id)
```

## jane_web_collector.crawler.CrawlRun.strategy_limits

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/crawler.py:251](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L251).

```python
self.strategy_limits: dict[str, ServiceLimits] = {}
```

## jane_web_collector.crawler.CrawlRun.scope_reason

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:261](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L261).

```python
def scope_reason(self, url: str) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `str | None`.

## jane_web_collector.crawler.CrawlRun.section_for

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:266](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L266).

```python
def section_for(self, url: str) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `str | None`.

## jane_web_collector.crawler.CrawlRun.rule_priority

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:272](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L272).

```python
def rule_priority(self, url: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `int`.

## jane_web_collector.crawler.CrawlRun.extract_links

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:278](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L278).

```python
def extract_links(self, resource: FetchedResource, selector: LinkSelector | None=None, sources: Sequence[str]=('a_href',)) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `resource` | `FetchedResource` | `—` | positional-or-keyword |
| `selector` | `LinkSelector \| None` | `None` | positional-or-keyword |
| `sources` | `Sequence[str]` | `('a_href',)` | positional-or-keyword |

Результат: `list[str]`.

## jane_web_collector.crawler.CrawlRun.robots_allowed

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:325](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L325).

```python
async def robots_allowed(self, url: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_web_collector.crawler.CrawlRun.admit

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:354](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L354).

```python
def admit(self, candidates: Sequence[DiscoveredUrl], parent_depth: int | None) -> list[FrontierRow]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `candidates` | `Sequence[DiscoveredUrl]` | `—` | positional-or-keyword |
| `parent_depth` | `int \| None` | `—` | positional-or-keyword |

Результат: `list[FrontierRow]`.

### Опис із вихідного коду

```text
Normalize and filter candidates (scope, depth, frontier size); dedup happens on insert.
```

## jane_web_collector.crawler.CrawlRun.insert_rows

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:392](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L392).

```python
def insert_rows(self, db: Any, rows: Sequence[FrontierRow]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `db` | `Any` | `—` | positional-or-keyword |
| `rows` | `Sequence[FrontierRow]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.crawler.CrawlRun.handle

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:511](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L511).

```python
async def handle(self, row: FrontierRow, *, caller: str | None=None, conditional: bool=True, method: str='GET', json_body: bytes | None=None) -> FetchedResource | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `row` | `FrontierRow` | `—` | positional-or-keyword |
| `caller` | `str \| None` | `None` | keyword-only |
| `conditional` | `bool` | `True` | keyword-only |
| `method` | `str` | `'GET'` | keyword-only |
| `json_body` | `bytes \| None` | `None` | keyword-only |

Результат: `FetchedResource | None`.

Явні `raise` у тілі: `FetchRejected`, `повторний raise`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Fetch and process one admitted URL. Returns the resource (for ``ctx.fetch``) or ``None``.
```

## jane_web_collector.crawler.CrawlRun.fetch_for_strategy

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:842](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L842).

```python
async def fetch_for_strategy(self, url: str, *, kind: UrlKind, conditional: bool, caller: str, method: str='GET', body: Any=None) -> FetchedResource | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |
| `kind` | `UrlKind` | `—` | keyword-only |
| `conditional` | `bool` | `—` | keyword-only |
| `caller` | `str` | `—` | keyword-only |
| `method` | `str` | `'GET'` | keyword-only |
| `body` | `Any` | `None` | keyword-only |

Результат: `FetchedResource | None`.

Явні `raise` у тілі: `FetchRejected`, `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_web_collector.crawler.CrawlRun.emit_for_strategy

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:887](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L887).

```python
async def emit_for_strategy(self, item: DiscoveredMaterial, *, caller: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `item` | `DiscoveredMaterial` | `—` | positional-or-keyword |
| `caller` | `str` | `—` | keyword-only |

Результат: `bool`.

Явні `raise` у тілі: `JobCancelledError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
``DiscoveryContext.emit_material``: content a strategy already has (an API item) as a Material, under
the rules of a fetched page - scope, depth, one material per canonical URL in the collection, ``revisit``
and ``dedup`` against the URL history, backpressure, one fenced transaction (R22).
```

## jane_web_collector.crawler.CrawlRun.execute

**Метод.** Код: [services/web-collector/src/jane_web_collector/crawler.py:1068](../../../../../../services/web-collector/src/jane_web_collector/crawler.py#L1068).

```python
async def execute(self, job: JobContext | None=None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job` | `JobContext \| None` | `None` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `RuntimeError`, `self._stop_exc`, `повторний raise`. Винятки викликаних залежностей описуються у ручному довіднику.
