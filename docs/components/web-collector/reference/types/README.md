# Типи й члени: Web Collector

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector](../../../../../services/web-collector/src/jane_web_collector). Не редагуйте вручну.

Довідник охоплює публічні модулі (без префікса `_`), їхні класи, функції, константи й реекспорт. Описи членів — docstring-и з коду (англійською); винятки — ті, що піднімаються в тілі.

## Модулі

| Модуль | Класи | Функції | Призначення |
|---|---|---|---|
| [`jane_web_collector`](jane_web_collector.md) | 0 | 0 | Web Collector of the Jane platform. |
| [`jane_web_collector.__main__`](jane_web_collector.__main__.md) | 0 | 1 | Entry point: ``python -m jane_web_collector`` (host/port from ``JANE_WEB_COLLECTOR_HOST/PORT``). |
| [`jane_web_collector.app`](jane_web_collector.app.md) | 0 | 4 | HTTP API ``collector.v1`` of the Web Collector (``contracts/openapi/collector.v1.yaml``). |
| [`jane_web_collector.connections`](jane_web_collector.connections.md) | 1 | 5 | Managed connections (``/v1/connections``, ADR-0006) for sites that need HTTP authentication. |
| [`jane_web_collector.crawler`](jane_web_collector.crawler.md) | 3 | 1 | Crawl engine: one :class:`CrawlRun` per collection, implementing ``DiscoveryContext`` for strategies. |
| [`jane_web_collector.discovery`](jane_web_collector.discovery.md) | 0 | 0 | Discovery strategies of the Web Collector: registry, built-ins and link extraction helpers. |
| [`jane_web_collector.discovery.builtin`](jane_web_collector.discovery.builtin.md) | 2 | 0 | Built-in discovery strategies of the core: ``seed_list`` (explicit list / home page) and ``recursive``. |
| [`jane_web_collector.discovery.links`](jane_web_collector.discovery.links.md) | 0 | 4 | Link extraction from HTML (lxml): ``a[href]`` by default, CSS / XPath / ``rel`` selectors, ``<base href>``. |
| [`jane_web_collector.discovery.registry`](jane_web_collector.discovery.registry.md) | 1 | 2 | Strategy registry (``jane_contracts.discovery.StrategyRegistry``) and the plug-in points for WP-03. |
| [`jane_web_collector.egress`](jane_web_collector.egress.md) | 4 | 1 | Outbound address policy of the fetch client (protection against SSRF). |
| [`jane_web_collector.engine`](jane_web_collector.engine.md) | 1 | 0 | Service core: collections (start, resume after restart, cancellation), the one-shot fetch and housekeeping. |
| [`jane_web_collector.fetcher`](jane_web_collector.fetcher.md) | 3 | 1 | HTTP fetching with per-host limits, retries, manual redirects, size limits and conditional requests. |
| [`jane_web_collector.host_limits`](jane_web_collector.host_limits.md) | 2 | 0 | Per-host politeness shared by every collection and one-shot fetch of one service process. |
| [`jane_web_collector.materials`](jane_web_collector.materials.md) | 1 | 5 | Material documents (``material.schema.json``) and content delivery (inline / transit blob, ADR-0004). |
| [`jane_web_collector.render`](jane_web_collector.render.md) | 3 | 1 | JavaScript rendering of pages (``fetch.render_js`` of the collector rules) in headless Chromium (Playwright). |
| [`jane_web_collector.robots`](jane_web_collector.robots.md) | 2 | 1 | robots.txt (RFC 9309): parsing, matching and the per-host cache. |
| [`jane_web_collector.rules`](jane_web_collector.rules.md) | 2 | 1 | Collector rules of the Web Collector: what this implementation supports, on top of the shared parts. |
| [`jane_web_collector.settings`](jane_web_collector.settings.md) | 10 | 4 | Settings and limits of the Web Collector. Every limit has a safe default documented in README.md. |
| [`jane_web_collector.shared_hosts`](jane_web_collector.shared_hosts.md) | 1 | 1 | Per-host politeness shared by the instances of the Web Collector that share one state store (R15). |
| [`jane_web_collector.state`](jane_web_collector.state.md) | 2 | 0 | Own state store of the Web Collector (SQLite, WAL): nobody else reads these tables (ADR-0009). |
| [`jane_web_collector.stores`](jane_web_collector.stores.md) | 2 | 0 | jane-kit's shared SQLite ``JobStore`` / ``IdempotencyStore`` on the collector's own state file (R17). |
| [`jane_web_collector.testing`](jane_web_collector.testing.md) | 2 | 9 | Test helpers for the Web Collector API (this service's tests; usable by WP-03 and WP-13 too). |
| [`jane_web_collector.urls`](jane_web_collector.urls.md) | 3 | 3 | URL normalization, URL patterns and scope checks (CollectorRules ``normalization``, ``UrlPattern``, ``scope``). |

## Покажчик

| Назва | Вид | Модуль |
|---|---|---|
| [`auth_headers`](jane_web_collector.connections.md#функція-auth_headers) | функція | `jane_web_collector.connections` |
| [`build_app`](jane_web_collector.app.md#функція-build_app) | функція | `jane_web_collector.app` |
| [`build_client`](jane_web_collector.fetcher.md#функція-build_client) | функція | `jane_web_collector.fetcher` |
| [`build_item_material`](jane_web_collector.materials.md#функція-build_item_material) | функція | `jane_web_collector.materials` |
| [`build_material`](jane_web_collector.materials.md#функція-build_material) | функція | `jane_web_collector.materials` |
| [`check_params`](jane_web_collector.connections.md#функція-check_params) | функція | `jane_web_collector.connections` |
| [`check_ttl`](jane_web_collector.shared_hosts.md#функція-check_ttl) | функція | `jane_web_collector.shared_hosts` |
| [`Collector`](jane_web_collector.settings.md#клас-collector) | клас | `jane_web_collector.settings` |
| [`compile_patterns`](jane_web_collector.urls.md#функція-compile_patterns) | функція | `jane_web_collector.urls` |
| [`Concurrency`](jane_web_collector.settings.md#клас-concurrency) | клас | `jane_web_collector.settings` |
| [`connection_etag`](jane_web_collector.connections.md#функція-connection_etag) | функція | `jane_web_collector.connections` |
| [`ConnectionPolicy`](jane_web_collector.connections.md#клас-connectionpolicy) | dataclass (незмінний) | `jane_web_collector.connections` |
| [`content_kind`](jane_web_collector.materials.md#функція-content_kind) | функція | `jane_web_collector.materials` |
| [`contract_layer`](jane_web_collector.settings.md#функція-contract_layer) | функція | `jane_web_collector.settings` |
| [`ContractSchemas`](jane_web_collector.rules.md#клас-contractschemas) | клас | `jane_web_collector.rules` |
| [`Crawl`](jane_web_collector.settings.md#клас-crawl) | клас | `jane_web_collector.settings` |
| [`CrawlRun`](jane_web_collector.crawler.md#клас-crawlrun) | клас | `jane_web_collector.crawler` |
| [`default_discovery_path`](jane_web_collector.discovery.registry.md#функція-default_discovery_path) | функція | `jane_web_collector.discovery.registry` |
| [`drain`](jane_web_collector.testing.md#функція-drain) | функція | `jane_web_collector.testing` |
| [`EgressDenied`](jane_web_collector.egress.md#клас-egressdenied) | виняток | `jane_web_collector.egress` |
| [`EgressPolicy`](jane_web_collector.egress.md#клас-egresspolicy) | dataclass (незмінний) | `jane_web_collector.egress` |
| [`EgressProxy`](jane_web_collector.render.md#клас-egressproxy) | клас | `jane_web_collector.render` |
| [`Engine`](jane_web_collector.engine.md#клас-engine) | клас | `jane_web_collector.engine` |
| [`errors`](jane_web_collector.testing.md#функція-errors) | функція | `jane_web_collector.testing` |
| [`extract_hrefs`](jane_web_collector.discovery.links.md#функція-extract_hrefs) | функція | `jane_web_collector.discovery.links` |
| [`Fetcher`](jane_web_collector.fetcher.md#клас-fetcher) | клас | `jane_web_collector.fetcher` |
| [`FetchError`](jane_web_collector.fetcher.md#клас-fetcherror) | виняток | `jane_web_collector.fetcher` |
| [`free_port`](jane_web_collector.testing.md#функція-free_port) | функція | `jane_web_collector.testing` |
| [`FrontierRow`](jane_web_collector.state.md#клас-frontierrow) | dataclass (незмінний) | `jane_web_collector.state` |
| [`GuardedBackend`](jane_web_collector.egress.md#клас-guardedbackend) | клас | `jane_web_collector.egress` |
| [`GuardedTransport`](jane_web_collector.egress.md#клас-guardedtransport) | клас | `jane_web_collector.egress` |
| [`header_name_safe`](jane_web_collector.connections.md#функція-header_name_safe) | функція | `jane_web_collector.connections` |
| [`HostLimiter`](jane_web_collector.host_limits.md#клас-hostlimiter) | клас | `jane_web_collector.host_limits` |
| [`HostSession`](jane_web_collector.host_limits.md#клас-hostsession) | клас | `jane_web_collector.host_limits` |
| [`html_meta`](jane_web_collector.discovery.links.md#функція-html_meta) | функція | `jane_web_collector.discovery.links` |
| [`HttpResult`](jane_web_collector.fetcher.md#клас-httpresult) | dataclass | `jane_web_collector.fetcher` |
| [`is_html`](jane_web_collector.discovery.links.md#функція-is_html) | функція | `jane_web_collector.discovery.links` |
| [`is_safe_rule_header`](jane_web_collector.connections.md#функція-is_safe_rule_header) | функція | `jane_web_collector.connections` |
| [`load_discovery_package`](jane_web_collector.discovery.registry.md#функція-load_discovery_package) | функція | `jane_web_collector.discovery.registry` |
| [`main`](jane_web_collector.__main__.md#функція-main) | функція | `jane_web_collector.__main__` |
| [`make_settings`](jane_web_collector.testing.md#функція-make_settings) | функція | `jane_web_collector.testing` |
| [`material_id`](jane_web_collector.urls.md#функція-material_id) | функція | `jane_web_collector.urls` |
| [`new_observation_id`](jane_web_collector.materials.md#функція-new_observation_id) | функція | `jane_web_collector.materials` |
| [`new_stats`](jane_web_collector.crawler.md#функція-new_stats) | функція | `jane_web_collector.crawler` |
| [`Normalizer`](jane_web_collector.urls.md#клас-normalizer) | dataclass (незмінний) | `jane_web_collector.urls` |
| [`parse_html`](jane_web_collector.discovery.links.md#функція-parse_html) | функція | `jane_web_collector.discovery.links` |
| [`parse_robots`](jane_web_collector.robots.md#функція-parse_robots) | функція | `jane_web_collector.robots` |
| [`patterns_match`](jane_web_collector.urls.md#функція-patterns_match) | функція | `jane_web_collector.urls` |
| [`platform_layers`](jane_web_collector.settings.md#функція-platform_layers) | функція | `jane_web_collector.settings` |
| [`Queue`](jane_web_collector.settings.md#клас-queue) | клас | `jane_web_collector.settings` |
| [`Rate`](jane_web_collector.settings.md#клас-rate) | клас | `jane_web_collector.settings` |
| [`RecursiveStrategy`](jane_web_collector.discovery.builtin.md#клас-recursivestrategy) | клас | `jane_web_collector.discovery.builtin` |
| [`Registry`](jane_web_collector.discovery.registry.md#клас-registry) | клас | `jane_web_collector.discovery.registry` |
| [`renderable`](jane_web_collector.render.md#функція-renderable) | функція | `jane_web_collector.render` |
| [`Renderer`](jane_web_collector.render.md#клас-renderer) | клас | `jane_web_collector.render` |
| [`RenderOptions`](jane_web_collector.render.md#клас-renderoptions) | dataclass (незмінний) | `jane_web_collector.render` |
| [`resolve_service_limits`](jane_web_collector.settings.md#функція-resolve_service_limits) | функція | `jane_web_collector.settings` |
| [`Retries`](jane_web_collector.settings.md#клас-retries) | клас | `jane_web_collector.settings` |
| [`rfc3339`](jane_web_collector.materials.md#функція-rfc3339) | функція | `jane_web_collector.materials` |
| [`rfc3339_now`](jane_web_collector.app.md#функція-rfc3339_now) | функція | `jane_web_collector.app` |
| [`rfc3339_ts`](jane_web_collector.app.md#функція-rfc3339_ts) | функція | `jane_web_collector.app` |
| [`RobotsCache`](jane_web_collector.robots.md#клас-robotscache) | клас | `jane_web_collector.robots` |
| [`RobotsRules`](jane_web_collector.robots.md#клас-robotsrules) | dataclass | `jane_web_collector.robots` |
| [`RulesLoader`](jane_web_collector.rules.md#клас-rulesloader) | клас | `jane_web_collector.rules` |
| [`RunDeps`](jane_web_collector.crawler.md#клас-rundeps) | dataclass | `jane_web_collector.crawler` |
| [`Scope`](jane_web_collector.urls.md#клас-scope) | dataclass (незмінний) | `jane_web_collector.urls` |
| [`SeedListStrategy`](jane_web_collector.discovery.builtin.md#клас-seedliststrategy) | клас | `jane_web_collector.discovery.builtin` |
| [`ServiceLimits`](jane_web_collector.settings.md#клас-servicelimits) | клас | `jane_web_collector.settings` |
| [`ServiceProcess`](jane_web_collector.testing.md#клас-serviceprocess) | dataclass | `jane_web_collector.testing` |
| [`Settings`](jane_web_collector.settings.md#клас-settings) | модель Pydantic | `jane_web_collector.settings` |
| [`SharedHosts`](jane_web_collector.shared_hosts.md#клас-sharedhosts) | клас | `jane_web_collector.shared_hosts` |
| [`Site`](jane_web_collector.testing.md#клас-site) | dataclass | `jane_web_collector.testing` |
| [`SqliteIdempotencyStore`](jane_web_collector.stores.md#клас-sqliteidempotencystore) | клас | `jane_web_collector.stores` |
| [`SqliteJobStore`](jane_web_collector.stores.md#клас-sqlitejobstore) | клас | `jane_web_collector.stores` |
| [`start`](jane_web_collector.testing.md#функція-start) | функція | `jane_web_collector.testing` |
| [`start_timeout_s`](jane_web_collector.testing.md#функція-start_timeout_s) | функція | `jane_web_collector.testing` |
| [`state_store_busy`](jane_web_collector.app.md#функція-state_store_busy) | функція | `jane_web_collector.app` |
| [`StateStore`](jane_web_collector.state.md#клас-statestore) | клас | `jane_web_collector.state` |
| [`StrategyContext`](jane_web_collector.crawler.md#клас-strategycontext) | клас | `jane_web_collector.crawler` |
| [`system_resolve`](jane_web_collector.egress.md#функція-system_resolve) | функція | `jane_web_collector.egress` |
| [`Timeouts`](jane_web_collector.settings.md#клас-timeouts) | клас | `jane_web_collector.settings` |
| [`to_contract`](jane_web_collector.settings.md#функція-to_contract) | функція | `jane_web_collector.settings` |
| [`Transfer`](jane_web_collector.settings.md#клас-transfer) | клас | `jane_web_collector.settings` |
| [`TransitStore`](jane_web_collector.materials.md#клас-transitstore) | клас | `jane_web_collector.materials` |
| [`UrlPattern`](jane_web_collector.urls.md#клас-urlpattern) | dataclass (незмінний) | `jane_web_collector.urls` |
| [`validate_rules`](jane_web_collector.rules.md#функція-validate_rules) | функція | `jane_web_collector.rules` |
| [`wait_done`](jane_web_collector.testing.md#функція-wait_done) | функція | `jane_web_collector.testing` |
| [`wait_timeout_s`](jane_web_collector.testing.md#функція-wait_timeout_s) | функція | `jane_web_collector.testing` |
| [`web_rules`](jane_web_collector.testing.md#функція-web_rules) | функція | `jane_web_collector.testing` |
