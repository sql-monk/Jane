# Модуль `jane_web_collector.settings`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/settings.py](../../../../../services/web-collector/src/jane_web_collector/settings.py). Не редагуйте вручну.

Settings and limits of the Web Collector. Every limit has a safe default documented in README.md.

Limit levels (``contracts/schemas/common/limits.schema.json``): service defaults -> platform (limits file, then ``JANE_WEB_COLLECTOR_LIMITS__*``) -> source (``rules.limits``) -> request (``CollectionRequest.limits``) -> strategy (``strategies[].limits``, only for that strategy's URLs). ``hard_caps`` bound the result.

The layers are jane-kit's, with the same error checks as every other service (R20): the limits file is a shared ``PlatformLimits`` profile (contract paths map to the fields that declare them, contract groups the collector does not use - ``sandbox``, ``llm``, ``telegram``... - are ignored and listed in ``ResolvedLimits.ignored``, a path unknown to the contract and to the model is an error); the environment layer takes model paths (``..._LIMITS__JOBS__JOB_RETENTION_SECONDS``); source, request and strategy layers are contract-shaped ``Limits`` documents (validated against the contract before they get here) and are applied the same way as the profile (:func:`contract_layer`).

## Зміст

- [Клас `Settings`](#клас-settings)
- [Клас `Concurrency`](#клас-concurrency)
- [Клас `Rate`](#клас-rate)
- [Клас `Crawl`](#клас-crawl)
- [Клас `Timeouts`](#клас-timeouts)
- [Клас `Retries`](#клас-retries)
- [Клас `Queue`](#клас-queue)
- [Клас `Transfer`](#клас-transfer)
- [Клас `Collector`](#клас-collector)
- [Клас `ServiceLimits`](#клас-servicelimits)
- [Функція `contract_layer`](#функція-contract_layer)
- [Функція `to_contract`](#функція-to_contract)
- [Функція `platform_layers`](#функція-platform_layers)
- [Функція `resolve_service_limits`](#функція-resolve_service_limits)

## Класи

### Клас `Settings`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_web_collector.settings` |
| Успадкування | `JaneSettings` |
| Код | [settings.py:47](../../../../../services/web-collector/src/jane_web_collector/settings.py#L47) |

```python
class Settings(JaneSettings): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `service_name` | `str` | `'web-collector'` | читання й запис |  |
| `port` | `int` | `8101` | читання й запис |  |
| `state_dir` | `Path` | `Path('.jane/web-collector')` | читання й запис | Own state store (SQLite ``state.db``): frontier, known URLs, strategy state, buffer, jobs. |
| `transit_dir` | `Path \| None` | `None` | читання й запис | Transit blob store for large materials (``file://`` ContentRef). Unset: inline only. |
| `rules_dir` | `Path \| None` | `None` | читання й запис | Local collector-rules packages for ``rules_ref`` without a registry (``<package_id>/<version>/``). |
| `registry_url` | `str \| None` | `None` | читання й запис | registry.v1 base URL for ``rules_ref``; checked after ``rules_dir``. |
| `registry_token_env` | `str \| None` | `None` | читання й запис | Name of the environment variable holding the bearer token for the registry (never the value). |
| `secret_env_prefix` | `str` | `'JANE_SECRET_'` | читання й запис | Only env: references with this prefix may be resolved; empty disables env: references. |
| `secret_files_dir` | `Path \| None` | `Path('/run/secrets')` | читання й запис | Only file: references inside this directory may be resolved; empty disables file: references. |
| `connection_origin_allowlist` | `list[str]` | `Field(default_factory=list)` | читання й запис | Exact HTTP(S) origins allowed to receive resolved connection credentials; empty denies all. |
| `egress_deny_link_local` | `bool` | `True` | читання й запис | Outbound policy: never connect to link-local addresses (169.254.0.0/16 with the cloud metadata service, fe80::/10, fd00:ec2::254). Checked after DNS resolution for every connection, including redirect hops. |
| `egress_deny_private` | `bool` | `False` | читання й запис | Outbound policy: also never connect to loopback, private and other non-public addresses. Off by default: the dev/e2e test site is in a private Docker network; turn it on where sources are public sites only. |
| `render_enabled` | `bool` | `True` | читання й запис | ``fetch.render_js`` of the rules is executed (headless Chromium through Playwright, the ``render`` extra). Off, or without Playwright/Chromium, such URLs fail with ``not_implemented``; nothing falls back to a plain fetch. |
| `render_wait_until` | `Literal['domcontentloaded', 'load', 'networkidle']` | `'networkidle'` | читання й запис | What a rendered page waits for before its DOM is taken (bounded by ``collector.render_timeout_ms``). |
| `render_block_resource_types` | `list[str]` | `Field(default_factory=lambda: ['image', 'media', 'font'])` | читання й запис | Playwright resource types the browser does not request at all (saves bandwidth; prices need none of them). |
| `render_browser_executable` | `Path \| None` | `None` | читання й запис | Chromium executable for rendering; default: the browser installed by ``playwright install chromium``. |
| `render_deny_private` | `bool` | `True` | читання й запис | Requests of the browser (page scripts) reach non-public addresses - loopback, RFC 1918, ``fc00::/7``... - only for the page's own host and the rules' ``scope.allowed_domains``: a page must not make the collector a proxy to internal services the caller did not choose. ``EGRESS_*`` applies on top for every host. |
| `contracts_dir` | `Path \| None` | `None` | читання й запис | ``contracts/`` with the JSON Schemas; default: ``JANE_CONTRACTS_DIR`` or the checkout's contracts. |
| `discovery_path` | `Path \| None` | `None` | читання й запис | Directory of the WP-03 discovery package; default ``services/web-collector/strategies/discovery``. |
| `user_agent` | `str` | `'JaneBot/0.1 (+https://github.com/jane)'` | читання й запис | Default User-Agent; ``rules.fetch.user_agent`` overrides it. The robots token is its first word. |
| `lease_seconds` | `int` | `Field(default=30, ge=2)` | читання й запис | A running collection is owned by one instance; after this long without a heartbeat another takes it. |
| `heartbeat_interval_ms` | `int` | `Field(default=5000, ge=50)` | читання й запис | How often the owner renews the lease and checks for cancellation from other instances. |
| `state_busy_timeout_ms` | `int` | `Field(default=10000, ge=1)` | читання й запис | How long a write waits for another process holding the SQLite lock. |
| `idempotency_lease_ms` | `int` | `Field(default=900000, ge=1000)` | читання й запис | An ``Idempotency-Key`` claim of a killed instance (not renewed for this long) can be claimed again; a live instance renews its claims in the resume loop (R17). |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `SettingsConfigDict(env_prefix=ENV_PREFIX, extra='ignore', env_nested_delimiter='` |  |

#### Метод `Settings.egress_policy`

```python
def egress_policy(self) -> EgressPolicy: ...
```

Код: [settings.py:118](../../../../../services/web-collector/src/jane_web_collector/settings.py#L118).

#### Метод `Settings.connection_policy`

```python
def connection_policy(self) -> ConnectionPolicy: ...
```

Код: [settings.py:123](../../../../../services/web-collector/src/jane_web_collector/settings.py#L123).

### Клас `Concurrency`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:131](../../../../../services/web-collector/src/jane_web_collector/settings.py#L131) |

```python
class Concurrency(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_parallel_fetches` | `int` | `Field(default=4, ge=1)` | читання й запис |  |
| `max_parallel_fetches_per_host` | `int` | `Field(default=2, ge=1)` | читання й запис |  |

### Клас `Rate`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:136](../../../../../services/web-collector/src/jane_web_collector/settings.py#L136) |

```python
class Rate(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `requests_per_second_per_host` | `float` | `Field(default=1.0, gt=0)` | читання й запис |  |
| `min_delay_ms_per_host` | `int` | `Field(default=500, ge=0)` | читання й запис |  |
| `respect_crawl_delay` | `bool` | `True` | читання й запис |  |

### Клас `Crawl`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:142](../../../../../services/web-collector/src/jane_web_collector/settings.py#L142) |

```python
class Crawl(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_depth` | `int` | `Field(default=5, ge=0)` | читання й запис |  |
| `max_pages_per_run` | `int` | `Field(default=5000, ge=1)` | читання й запис |  |
| `max_bytes_per_run` | `int` | `Field(default=2 * 1024 ** 3, ge=1)` | читання й запис |  |
| `max_material_bytes` | `int` | `Field(default=10 * 1024 ** 2, ge=1)` | читання й запис |  |
| `max_redirects` | `int` | `Field(default=5, ge=0)` | читання й запис |  |
| `max_links_per_page` | `int` | `Field(default=2000, ge=0)` | читання й запис |  |
| `max_seed_urls` | `int` | `Field(default=100000, ge=1)` | читання й запис |  |
| `max_frontier_size` | `int` | `Field(default=100000, ge=1)` | читання й запис |  |
| `revisit_interval_seconds` | `int` | `Field(default=86400, ge=0)` | читання й запис |  |

### Клас `Timeouts`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:154](../../../../../services/web-collector/src/jane_web_collector/settings.py#L154) |

```python
class Timeouts(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `connect_timeout_ms` | `int` | `Field(default=10000, ge=1)` | читання й запис |  |
| `request_timeout_ms` | `int` | `Field(default=30000, ge=1)` | читання й запис |  |

### Клас `Retries`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:159](../../../../../services/web-collector/src/jane_web_collector/settings.py#L159) |

```python
class Retries(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_attempts` | `int` | `Field(default=3, ge=1)` | читання й запис |  |
| `initial_backoff_ms` | `int` | `Field(default=1000, ge=0)` | читання й запис |  |
| `max_backoff_ms` | `int` | `Field(default=60000, ge=0)` | читання й запис |  |
| `backoff_multiplier` | `float` | `Field(default=2.0, ge=1)` | читання й запис |  |
| `jitter` | `bool` | `True` | читання й запис |  |

### Клас `Queue`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:167](../../../../../services/web-collector/src/jane_web_collector/settings.py#L167) |

```python
class Queue(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_unacked_materials` | `int` | `Field(default=500, ge=1)` | читання й запис |  |

### Клас `Transfer`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:171](../../../../../services/web-collector/src/jane_web_collector/settings.py#L171) |

```python
class Transfer(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `inline_max_bytes` | `int` | `Field(default=262144, ge=0)` | читання й запис |  |
| `transit_ttl_seconds` | `int` | `Field(default=604800, ge=60)` | читання й запис |  |

### Клас `Collector`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:176](../../../../../services/web-collector/src/jane_web_collector/settings.py#L176) |

```python
class Collector(Limits): ...
```

Service-specific limits (not in the contract; visible only in the start-up log).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_wait_ms` | `int` | `Field(default=30000, ge=0)` | читання й запис | Upper bound of ``wait_ms`` long-poll on ``/materials``. |
| `robots_cache_ttl_seconds` | `int` | `Field(default=3600, ge=0)` | читання й запис |  |
| `robots_max_bytes` | `int` | `Field(default=512000, ge=1)` | читання й запис | robots.txt larger than this is truncated (RFC 9309 allows >= 500 KiB). |
| `max_retry_after_seconds` | `int` | `Field(default=300, ge=0)` | читання й запис | A source asking to wait longer (Retry-After, Crawl-delay) makes the URL fail with ``rate_limited``. |
| `backpressure_poll_ms` | `int` | `Field(default=1000, ge=10)` | читання й запис | While paused by backpressure: how often the buffer is re-checked (acks may arrive via another instance). |
| `long_poll_interval_ms` | `int` | `Field(default=100, ge=10)` | читання й запис | ``/materials?wait_ms=``: how often new materials are looked for while waiting. |
| `gc_interval_seconds` | `int` | `Field(default=3600, ge=1)` | читання й запис | How often expired collections and transit files are cleaned up. |
| `host_state_prune_interval_seconds` | `int` | `Field(default=60, ge=1)` | читання й запис | How often the shared per-host limiter drops the state of hosts nobody uses any more. |
| `shared_host_limits` | `bool` | `True` | читання й запис | Coordinate the per-host limits with the other instances that share the state store (R15). |
| `shared_host_poll_ms` | `int` | `Field(default=100, ge=10)` | читання й запис | A request waiting for a host slot that other instances hold re-checks this often. |
| `shared_host_ttl_seconds` | `int` | `Field(default=120, ge=1)` | читання й запис | How long the registration, slot or place in line of an instance that died keeps limiting the others. A live instance renews them every TTL / 3 (also during long downloads, Retry-After and Crawl-delay waits), so the TTL need not exceed them; start-up rule: TTL * 2/3 > ``STATE_BUSY_TIMEOUT_MS``. |
| `render_timeout_ms` | `int` | `Field(default=30000, ge=1)` | читання й запис | ``fetch.render_js``: how long a page may load in the browser (navigation and ``RENDER_WAIT_UNTIL``); after that the DOM is taken as it is (diagnostic ``render_incomplete``). Taking the DOM has the same bound. |
| `render_extra_wait_ms` | `int` | `Field(default=0, ge=0)` | читання й запис | Extra pause after the wait condition, for scripts that fill the page late (within ``render_timeout_ms``). |
| `render_max_pages` | `int` | `Field(default=2, ge=1)` | читання й запис | Browser pages rendering at once in this process (every collection and fetch together); others wait. |
| `render_max_transfer_bytes` | `int` | `Field(default=50 * 1024 ** 2, ge=1)` | читання й запис | Bytes the browser may download for one page (scripts, XHR, styles); then its connections are cut and the DOM is taken as it is (diagnostic ``render_budget_exceeded``). |
| `render_launch_timeout_ms` | `int` | `Field(default=30000, ge=1)` | читання й запис | How long starting headless Chromium may take; longer counts as "no browser" (``not_implemented``). |
| `render_close_timeout_ms` | `int` | `Field(default=30000, ge=1)` | читання й запис | How long closing a page's browser context, and the browser and its driver on restart or stop, may take; a context that does not close in time makes the browser start again before the next page. Generous on purpose: Chromium on Windows sometimes needs several seconds to exit, and a browser given up on may be left running. |

### Клас `ServiceLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:220](../../../../../services/web-collector/src/jane_web_collector/settings.py#L220) |

```python
class ServiceLimits(Limits): ...
```

Limits of the Web Collector; group and field names follow ``limits.schema.json``.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `concurrency` | `Concurrency` | `contract_field('concurrency', Concurrency())` | читання й запис |  |
| `rate` | `Rate` | `contract_field('rate', Rate())` | читання й запис |  |
| `crawl` | `Crawl` | `contract_field('crawl', Crawl())` | читання й запис |  |
| `timeouts` | `Timeouts` | `contract_field('timeouts', Timeouts())` | читання й запис |  |
| `retries` | `Retries` | `contract_field('retries', Retries())` | читання й запис |  |
| `queue` | `Queue` | `contract_field('queue', Queue())` | читання й запис |  |
| `transfer` | `Transfer` | `contract_field('transfer', Transfer())` | читання й запис |  |
| `jobs` | `JobLimits` | `JobLimits()` | читання й запис |  |
| `idempotency` | `IdempotencyLimits` | `IdempotencyLimits()` | читання й запис |  |
| `page` | `PageLimits` | `PageLimits()` | читання й запис |  |
| `collector` | `Collector` | `Collector()` | читання й запис |  |

## Функції

### Функція `contract_layer`

```python
def contract_layer(layer: LimitLayer) -> LimitLayer: ...
```

A contract-shaped ``Limits`` document (``rules.limits``, request ``limits``, ``strategies[].limits``) as a jane-kit layer: contract paths go to the fields that declare them (``transfer.job_retention_seconds`` -> ``jobs.job_retention_seconds``), contract limits the collector does not have are ignored, anything else is a :class:`~jane_kit.config.LimitError` - exactly as for the platform profile.

Код: [settings.py:245](../../../../../services/web-collector/src/jane_web_collector/settings.py#L245).

### Функція `to_contract`

```python
def to_contract(limits: ServiceLimits) -> dict[str, Any]: ...
```

Model -> contract ``Limits`` document (only fields that exist in the contract), by jane-kit's mapping.

Код: [settings.py:253](../../../../../services/web-collector/src/jane_web_collector/settings.py#L253).

### Функція `platform_layers`

```python
def platform_layers(settings: Settings) -> list[LimitLayer]: ...
```

jane-kit's platform layers: the ``PlatformLimits`` file (shared profile) and the env overrides.

Код: [settings.py:261](../../../../../services/web-collector/src/jane_web_collector/settings.py#L261).

### Функція `resolve_service_limits`

```python
def resolve_service_limits(
    settings: Settings,
    *extra: LimitLayer,
) -> ResolvedLimits[ServiceLimits]: ...
```

Defaults &lt;- platform file (``..._LIMITS_FILE``) &lt;- ``JANE_WEB_COLLECTOR_LIMITS__*`` &lt;- ``extra`` (source/request/strategy layers, contract-shaped). Invalid limits raise :class:`~jane_kit.config.LimitError`.

Код: [settings.py:266](../../../../../services/web-collector/src/jane_web_collector/settings.py#L266).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `ENV_PREFIX` | — | `'JANE_WEB_COLLECTOR_'` |  |
| `LIMITS_ENV_PREFIX` | — | `f'{ENV_PREFIX}LIMITS__'` |  |
| `log` | — | `logging.getLogger(__name__)` |  |
