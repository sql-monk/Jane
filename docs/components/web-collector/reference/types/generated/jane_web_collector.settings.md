# jane_web_collector.settings

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.settings.ENV_PREFIX](#jane_web_collectorsettingsenv_prefix)
- [jane_web_collector.settings.LIMITS_ENV_PREFIX](#jane_web_collectorsettingslimits_env_prefix)
- [jane_web_collector.settings.log](#jane_web_collectorsettingslog)
- [jane_web_collector.settings.Settings](#jane_web_collectorsettingssettings)
- [jane_web_collector.settings.Settings.model_config](#jane_web_collectorsettingssettingsmodel_config)
- [jane_web_collector.settings.Settings.service_name](#jane_web_collectorsettingssettingsservice_name)
- [jane_web_collector.settings.Settings.port](#jane_web_collectorsettingssettingsport)
- [jane_web_collector.settings.Settings.state_dir](#jane_web_collectorsettingssettingsstate_dir)
- [jane_web_collector.settings.Settings.transit_dir](#jane_web_collectorsettingssettingstransit_dir)
- [jane_web_collector.settings.Settings.rules_dir](#jane_web_collectorsettingssettingsrules_dir)
- [jane_web_collector.settings.Settings.registry_url](#jane_web_collectorsettingssettingsregistry_url)
- [jane_web_collector.settings.Settings.registry_token_env](#jane_web_collectorsettingssettingsregistry_token_env)
- [jane_web_collector.settings.Settings.secret_env_prefix](#jane_web_collectorsettingssettingssecret_env_prefix)
- [jane_web_collector.settings.Settings.secret_files_dir](#jane_web_collectorsettingssettingssecret_files_dir)
- [jane_web_collector.settings.Settings.connection_origin_allowlist](#jane_web_collectorsettingssettingsconnection_origin_allowlist)
- [jane_web_collector.settings.Settings.egress_deny_link_local](#jane_web_collectorsettingssettingsegress_deny_link_local)
- [jane_web_collector.settings.Settings.egress_deny_private](#jane_web_collectorsettingssettingsegress_deny_private)
- [jane_web_collector.settings.Settings.render_enabled](#jane_web_collectorsettingssettingsrender_enabled)
- [jane_web_collector.settings.Settings.render_wait_until](#jane_web_collectorsettingssettingsrender_wait_until)
- [jane_web_collector.settings.Settings.render_block_resource_types](#jane_web_collectorsettingssettingsrender_block_resource_types)
- [jane_web_collector.settings.Settings.render_browser_executable](#jane_web_collectorsettingssettingsrender_browser_executable)
- [jane_web_collector.settings.Settings.render_deny_private](#jane_web_collectorsettingssettingsrender_deny_private)
- [jane_web_collector.settings.Settings.contracts_dir](#jane_web_collectorsettingssettingscontracts_dir)
- [jane_web_collector.settings.Settings.discovery_path](#jane_web_collectorsettingssettingsdiscovery_path)
- [jane_web_collector.settings.Settings.user_agent](#jane_web_collectorsettingssettingsuser_agent)
- [jane_web_collector.settings.Settings.lease_seconds](#jane_web_collectorsettingssettingslease_seconds)
- [jane_web_collector.settings.Settings.heartbeat_interval_ms](#jane_web_collectorsettingssettingsheartbeat_interval_ms)
- [jane_web_collector.settings.Settings.state_busy_timeout_ms](#jane_web_collectorsettingssettingsstate_busy_timeout_ms)
- [jane_web_collector.settings.Settings.idempotency_lease_ms](#jane_web_collectorsettingssettingsidempotency_lease_ms)
- [jane_web_collector.settings.Settings.egress_policy](#jane_web_collectorsettingssettingsegress_policy)
- [jane_web_collector.settings.Settings.connection_policy](#jane_web_collectorsettingssettingsconnection_policy)
- [jane_web_collector.settings.Concurrency](#jane_web_collectorsettingsconcurrency)
- [jane_web_collector.settings.Concurrency.max_parallel_fetches](#jane_web_collectorsettingsconcurrencymax_parallel_fetches)
- [jane_web_collector.settings.Concurrency.max_parallel_fetches_per_host](#jane_web_collectorsettingsconcurrencymax_parallel_fetches_per_host)
- [jane_web_collector.settings.Rate](#jane_web_collectorsettingsrate)
- [jane_web_collector.settings.Rate.requests_per_second_per_host](#jane_web_collectorsettingsraterequests_per_second_per_host)
- [jane_web_collector.settings.Rate.min_delay_ms_per_host](#jane_web_collectorsettingsratemin_delay_ms_per_host)
- [jane_web_collector.settings.Rate.respect_crawl_delay](#jane_web_collectorsettingsraterespect_crawl_delay)
- [jane_web_collector.settings.Crawl](#jane_web_collectorsettingscrawl)
- [jane_web_collector.settings.Crawl.max_depth](#jane_web_collectorsettingscrawlmax_depth)
- [jane_web_collector.settings.Crawl.max_pages_per_run](#jane_web_collectorsettingscrawlmax_pages_per_run)
- [jane_web_collector.settings.Crawl.max_bytes_per_run](#jane_web_collectorsettingscrawlmax_bytes_per_run)
- [jane_web_collector.settings.Crawl.max_material_bytes](#jane_web_collectorsettingscrawlmax_material_bytes)
- [jane_web_collector.settings.Crawl.max_redirects](#jane_web_collectorsettingscrawlmax_redirects)
- [jane_web_collector.settings.Crawl.max_links_per_page](#jane_web_collectorsettingscrawlmax_links_per_page)
- [jane_web_collector.settings.Crawl.max_seed_urls](#jane_web_collectorsettingscrawlmax_seed_urls)
- [jane_web_collector.settings.Crawl.max_frontier_size](#jane_web_collectorsettingscrawlmax_frontier_size)
- [jane_web_collector.settings.Crawl.revisit_interval_seconds](#jane_web_collectorsettingscrawlrevisit_interval_seconds)
- [jane_web_collector.settings.Timeouts](#jane_web_collectorsettingstimeouts)
- [jane_web_collector.settings.Timeouts.connect_timeout_ms](#jane_web_collectorsettingstimeoutsconnect_timeout_ms)
- [jane_web_collector.settings.Timeouts.request_timeout_ms](#jane_web_collectorsettingstimeoutsrequest_timeout_ms)
- [jane_web_collector.settings.Retries](#jane_web_collectorsettingsretries)
- [jane_web_collector.settings.Retries.max_attempts](#jane_web_collectorsettingsretriesmax_attempts)
- [jane_web_collector.settings.Retries.initial_backoff_ms](#jane_web_collectorsettingsretriesinitial_backoff_ms)
- [jane_web_collector.settings.Retries.max_backoff_ms](#jane_web_collectorsettingsretriesmax_backoff_ms)
- [jane_web_collector.settings.Retries.backoff_multiplier](#jane_web_collectorsettingsretriesbackoff_multiplier)
- [jane_web_collector.settings.Retries.jitter](#jane_web_collectorsettingsretriesjitter)
- [jane_web_collector.settings.Queue](#jane_web_collectorsettingsqueue)
- [jane_web_collector.settings.Queue.max_unacked_materials](#jane_web_collectorsettingsqueuemax_unacked_materials)
- [jane_web_collector.settings.Transfer](#jane_web_collectorsettingstransfer)
- [jane_web_collector.settings.Transfer.inline_max_bytes](#jane_web_collectorsettingstransferinline_max_bytes)
- [jane_web_collector.settings.Transfer.transit_ttl_seconds](#jane_web_collectorsettingstransfertransit_ttl_seconds)
- [jane_web_collector.settings.Collector](#jane_web_collectorsettingscollector)
- [jane_web_collector.settings.Collector.max_wait_ms](#jane_web_collectorsettingscollectormax_wait_ms)
- [jane_web_collector.settings.Collector.robots_cache_ttl_seconds](#jane_web_collectorsettingscollectorrobots_cache_ttl_seconds)
- [jane_web_collector.settings.Collector.robots_max_bytes](#jane_web_collectorsettingscollectorrobots_max_bytes)
- [jane_web_collector.settings.Collector.max_retry_after_seconds](#jane_web_collectorsettingscollectormax_retry_after_seconds)
- [jane_web_collector.settings.Collector.backpressure_poll_ms](#jane_web_collectorsettingscollectorbackpressure_poll_ms)
- [jane_web_collector.settings.Collector.long_poll_interval_ms](#jane_web_collectorsettingscollectorlong_poll_interval_ms)
- [jane_web_collector.settings.Collector.gc_interval_seconds](#jane_web_collectorsettingscollectorgc_interval_seconds)
- [jane_web_collector.settings.Collector.host_state_prune_interval_seconds](#jane_web_collectorsettingscollectorhost_state_prune_interval_seconds)
- [jane_web_collector.settings.Collector.shared_host_limits](#jane_web_collectorsettingscollectorshared_host_limits)
- [jane_web_collector.settings.Collector.shared_host_poll_ms](#jane_web_collectorsettingscollectorshared_host_poll_ms)
- [jane_web_collector.settings.Collector.shared_host_ttl_seconds](#jane_web_collectorsettingscollectorshared_host_ttl_seconds)
- [jane_web_collector.settings.Collector.render_timeout_ms](#jane_web_collectorsettingscollectorrender_timeout_ms)
- [jane_web_collector.settings.Collector.render_extra_wait_ms](#jane_web_collectorsettingscollectorrender_extra_wait_ms)
- [jane_web_collector.settings.Collector.render_max_pages](#jane_web_collectorsettingscollectorrender_max_pages)
- [jane_web_collector.settings.Collector.render_max_transfer_bytes](#jane_web_collectorsettingscollectorrender_max_transfer_bytes)
- [jane_web_collector.settings.Collector.render_launch_timeout_ms](#jane_web_collectorsettingscollectorrender_launch_timeout_ms)
- [jane_web_collector.settings.Collector.render_close_timeout_ms](#jane_web_collectorsettingscollectorrender_close_timeout_ms)
- [jane_web_collector.settings.ServiceLimits](#jane_web_collectorsettingsservicelimits)
- [jane_web_collector.settings.ServiceLimits.concurrency](#jane_web_collectorsettingsservicelimitsconcurrency)
- [jane_web_collector.settings.ServiceLimits.rate](#jane_web_collectorsettingsservicelimitsrate)
- [jane_web_collector.settings.ServiceLimits.crawl](#jane_web_collectorsettingsservicelimitscrawl)
- [jane_web_collector.settings.ServiceLimits.timeouts](#jane_web_collectorsettingsservicelimitstimeouts)
- [jane_web_collector.settings.ServiceLimits.retries](#jane_web_collectorsettingsservicelimitsretries)
- [jane_web_collector.settings.ServiceLimits.queue](#jane_web_collectorsettingsservicelimitsqueue)
- [jane_web_collector.settings.ServiceLimits.transfer](#jane_web_collectorsettingsservicelimitstransfer)
- [jane_web_collector.settings.ServiceLimits.jobs](#jane_web_collectorsettingsservicelimitsjobs)
- [jane_web_collector.settings.ServiceLimits.idempotency](#jane_web_collectorsettingsservicelimitsidempotency)
- [jane_web_collector.settings.ServiceLimits.page](#jane_web_collectorsettingsservicelimitspage)
- [jane_web_collector.settings.ServiceLimits.collector](#jane_web_collectorsettingsservicelimitscollector)
- [jane_web_collector.settings.contract_layer](#jane_web_collectorsettingscontract_layer)
- [jane_web_collector.settings.to_contract](#jane_web_collectorsettingsto_contract)
- [jane_web_collector.settings.platform_layers](#jane_web_collectorsettingsplatform_layers)
- [jane_web_collector.settings.resolve_service_limits](#jane_web_collectorsettingsresolve_service_limits)

## jane_web_collector.settings.ENV_PREFIX

**Константа.** Код: [services/web-collector/src/jane_web_collector/settings.py:41](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L41).

```python
ENV_PREFIX = 'JANE_WEB_COLLECTOR_'
```

## jane_web_collector.settings.LIMITS_ENV_PREFIX

**Константа.** Код: [services/web-collector/src/jane_web_collector/settings.py:42](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L42).

```python
LIMITS_ENV_PREFIX = f'{ENV_PREFIX}LIMITS__'
```

## jane_web_collector.settings.log

**Змінна.** Код: [services/web-collector/src/jane_web_collector/settings.py:44](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L44).

```python
log = logging.getLogger(__name__)
```

## jane_web_collector.settings.Settings

**Клас.** Код: [services/web-collector/src/jane_web_collector/settings.py:47](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L47).

```python
class Settings(JaneSettings):
```

Базові типи / інтерфейси: `JaneSettings`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_config](jane_web_collector.settings.md#jane_web_collectorsettingssettingsmodel_config) | Поле | ні |
| [service_name](jane_web_collector.settings.md#jane_web_collectorsettingssettingsservice_name) | Поле | ні |
| [port](jane_web_collector.settings.md#jane_web_collectorsettingssettingsport) | Поле | ні |
| [state_dir](jane_web_collector.settings.md#jane_web_collectorsettingssettingsstate_dir) | Поле | ні |
| [transit_dir](jane_web_collector.settings.md#jane_web_collectorsettingssettingstransit_dir) | Поле | ні |
| [rules_dir](jane_web_collector.settings.md#jane_web_collectorsettingssettingsrules_dir) | Поле | ні |
| [registry_url](jane_web_collector.settings.md#jane_web_collectorsettingssettingsregistry_url) | Поле | ні |
| [registry_token_env](jane_web_collector.settings.md#jane_web_collectorsettingssettingsregistry_token_env) | Поле | ні |
| [secret_env_prefix](jane_web_collector.settings.md#jane_web_collectorsettingssettingssecret_env_prefix) | Поле | ні |
| [secret_files_dir](jane_web_collector.settings.md#jane_web_collectorsettingssettingssecret_files_dir) | Поле | ні |
| [connection_origin_allowlist](jane_web_collector.settings.md#jane_web_collectorsettingssettingsconnection_origin_allowlist) | Поле | ні |
| [egress_deny_link_local](jane_web_collector.settings.md#jane_web_collectorsettingssettingsegress_deny_link_local) | Поле | ні |
| [egress_deny_private](jane_web_collector.settings.md#jane_web_collectorsettingssettingsegress_deny_private) | Поле | ні |
| [render_enabled](jane_web_collector.settings.md#jane_web_collectorsettingssettingsrender_enabled) | Поле | ні |
| [render_wait_until](jane_web_collector.settings.md#jane_web_collectorsettingssettingsrender_wait_until) | Поле | ні |
| [render_block_resource_types](jane_web_collector.settings.md#jane_web_collectorsettingssettingsrender_block_resource_types) | Поле | ні |
| [render_browser_executable](jane_web_collector.settings.md#jane_web_collectorsettingssettingsrender_browser_executable) | Поле | ні |
| [render_deny_private](jane_web_collector.settings.md#jane_web_collectorsettingssettingsrender_deny_private) | Поле | ні |
| [contracts_dir](jane_web_collector.settings.md#jane_web_collectorsettingssettingscontracts_dir) | Поле | ні |
| [discovery_path](jane_web_collector.settings.md#jane_web_collectorsettingssettingsdiscovery_path) | Поле | ні |
| [user_agent](jane_web_collector.settings.md#jane_web_collectorsettingssettingsuser_agent) | Поле | ні |
| [lease_seconds](jane_web_collector.settings.md#jane_web_collectorsettingssettingslease_seconds) | Поле | ні |
| [heartbeat_interval_ms](jane_web_collector.settings.md#jane_web_collectorsettingssettingsheartbeat_interval_ms) | Поле | ні |
| [state_busy_timeout_ms](jane_web_collector.settings.md#jane_web_collectorsettingssettingsstate_busy_timeout_ms) | Поле | ні |
| [idempotency_lease_ms](jane_web_collector.settings.md#jane_web_collectorsettingssettingsidempotency_lease_ms) | Поле | ні |
| [egress_policy](jane_web_collector.settings.md#jane_web_collectorsettingssettingsegress_policy) | Метод | ні |
| [connection_policy](jane_web_collector.settings.md#jane_web_collectorsettingssettingsconnection_policy) | Метод | ні |
| [instance_id](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingsinstance_id) | Поле | так |
| [host](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingshost) | Поле | так |
| [log_level](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingslog_level) | Поле | так |
| [log_format](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingslog_format) | Поле | так |
| [metrics_enabled](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingsmetrics_enabled) | Поле | так |
| [health_check_timeout_ms](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingshealth_check_timeout_ms) | Поле | так |
| [limits_file](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingslimits_file) | Поле | так |
| [platform_layers](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingsplatform_layers) | Метод | так |
| [with_overrides](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingswith_overrides) | Метод | так |
| [auth_mode](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsauth_mode) | Поле | так |
| [auth_none_allow_remote](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsauth_none_allow_remote) | Поле | так |
| [api_keys](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsapi_keys) | Поле | так |
| [api_keys_file](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsapi_keys_file) | Поле | так |
| [jwt_jwks_url](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_url) | Поле | так |
| [jwt_issuer](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_issuer) | Поле | так |
| [jwt_audience](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_audience) | Поле | так |
| [jwt_algorithms](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_algorithms) | Поле | так |
| [jwt_scope_claim](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_scope_claim) | Поле | так |
| [jwt_leeway_seconds](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_leeway_seconds) | Поле | так |
| [jwt_jwks_cache_ttl_seconds](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_cache_ttl_seconds) | Поле | так |
| [jwt_jwks_timeout_ms](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_timeout_ms) | Поле | так |
| [jwt_jwks_refresh_cooldown_seconds](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_refresh_cooldown_seconds) | Поле | так |
| [jwt_jwks_max_bytes](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_max_bytes) | Поле | так |
| [auth_max_token_bytes](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsauth_max_token_bytes) | Поле | так |
| [metrics_public](../../../../jane-kit/reference/types/generated/jane_kit.auth.md#jane_kitauthauthsettingsmetrics_public) | Поле | так |

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_egress_policy.py:67](../../../../../../services/web-collector/tests/test_egress_policy.py#L67).

```python
assert Settings().egress_policy() == EgressPolicy(deny_link_local=True, deny_private=False)
```

Контекст і передумови: [services/web-collector/tests/test_egress_policy.py:70](../../../../../../services/web-collector/tests/test_egress_policy.py#L70).

```python
assert Settings().egress_policy() == EgressPolicy(deny_link_local=False, deny_private=True)
```

## jane_web_collector.settings.Settings.model_config

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:48](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L48).

```python
model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra='ignore', env_nested_delimiter='__')
```

Доступ: читання — так; запис — так.

## jane_web_collector.settings.Settings.service_name

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:50](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L50).

```python
service_name: str = 'web-collector'
```

Доступ: читання — так; запис — так.

## jane_web_collector.settings.Settings.port

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:51](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L51).

```python
port: int = 8101
```

Доступ: читання — так; запис — так.

## jane_web_collector.settings.Settings.state_dir

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:53](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L53).

```python
state_dir: Path = Path('.jane/web-collector')
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Own state store (SQLite ``state.db``): frontier, known URLs, strategy state, buffer, jobs.
```

## jane_web_collector.settings.Settings.transit_dir

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:55](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L55).

```python
transit_dir: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Transit blob store for large materials (``file://`` ContentRef). Unset: inline only.
```

## jane_web_collector.settings.Settings.rules_dir

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:57](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L57).

```python
rules_dir: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Local collector-rules packages for ``rules_ref`` without a registry (``<package_id>/<version>/``).
```

## jane_web_collector.settings.Settings.registry_url

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:59](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L59).

```python
registry_url: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
registry.v1 base URL for ``rules_ref``; checked after ``rules_dir``.
```

## jane_web_collector.settings.Settings.registry_token_env

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:61](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L61).

```python
registry_token_env: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Name of the environment variable holding the bearer token for the registry (never the value).
```

## jane_web_collector.settings.Settings.secret_env_prefix

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:63](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L63).

```python
secret_env_prefix: str = 'JANE_SECRET_'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Only env: references with this prefix may be resolved; empty disables env: references.
```

## jane_web_collector.settings.Settings.secret_files_dir

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:65](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L65).

```python
secret_files_dir: Path | None = Path('/run/secrets')
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Only file: references inside this directory may be resolved; empty disables file: references.
```

## jane_web_collector.settings.Settings.connection_origin_allowlist

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:67](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L67).

```python
connection_origin_allowlist: list[str] = Field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

### Опис із вихідного коду

```text
Exact HTTP(S) origins allowed to receive resolved connection credentials; empty denies all.
```

## jane_web_collector.settings.Settings.egress_deny_link_local

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:69](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L69).

```python
egress_deny_link_local: bool = True
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Outbound policy: never connect to link-local addresses (169.254.0.0/16 with the cloud metadata service,
    fe80::/10, fd00:ec2::254). Checked after DNS resolution for every connection, including redirect hops.
```

## jane_web_collector.settings.Settings.egress_deny_private

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:72](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L72).

```python
egress_deny_private: bool = False
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Outbound policy: also never connect to loopback, private and other non-public addresses. Off by default:
    the dev/e2e test site is in a private Docker network; turn it on where sources are public sites only.
```

## jane_web_collector.settings.Settings.render_enabled

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:75](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L75).

```python
render_enabled: bool = True
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``fetch.render_js`` of the rules is executed (headless Chromium through Playwright, the ``render`` extra).
    Off, or without Playwright/Chromium, such URLs fail with ``not_implemented``; nothing falls back to a plain
    fetch.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:112](../../../../../../services/web-collector/tests/test_render_js.py#L112).

```python
assert defaults.render_enabled is True and defaults.render_wait_until == "networkidle"
```

## jane_web_collector.settings.Settings.render_wait_until

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:79](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L79).

```python
render_wait_until: Literal['domcontentloaded', 'load', 'networkidle'] = 'networkidle'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
What a rendered page waits for before its DOM is taken (bounded by ``collector.render_timeout_ms``).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:112](../../../../../../services/web-collector/tests/test_render_js.py#L112).

```python
assert defaults.render_enabled is True and defaults.render_wait_until == "networkidle"
```

## jane_web_collector.settings.Settings.render_block_resource_types

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:81](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L81).

```python
render_block_resource_types: list[str] = Field(default_factory=lambda: ['image', 'media', 'font'])
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "lambda: ['image', 'media', 'font']"
}
```

### Опис із вихідного коду

```text
Playwright resource types the browser does not request at all (saves bandwidth; prices need none of them).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:113](../../../../../../services/web-collector/tests/test_render_js.py#L113).

```python
assert defaults.render_block_resource_types == ["image", "media", "font"]
```

## jane_web_collector.settings.Settings.render_browser_executable

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:83](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L83).

```python
render_browser_executable: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Chromium executable for rendering; default: the browser installed by ``playwright install chromium``.
```

## jane_web_collector.settings.Settings.render_deny_private

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:85](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L85).

```python
render_deny_private: bool = True
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Requests of the browser (page scripts) reach non-public addresses - loopback, RFC 1918, ``fc00::/7``... - only
    for the page's own host and the rules' ``scope.allowed_domains``: a page must not make the collector a proxy to
    internal services the caller did not choose. ``EGRESS_*`` applies on top for every host.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_render_js.py:118](../../../../../../services/web-collector/tests/test_render_js.py#L118).

```python
assert defaults.render_deny_private is True
```

## jane_web_collector.settings.Settings.contracts_dir

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:89](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L89).

```python
contracts_dir: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``contracts/`` with the JSON Schemas; default: ``JANE_CONTRACTS_DIR`` or the checkout's contracts.
```

## jane_web_collector.settings.Settings.discovery_path

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:91](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L91).

```python
discovery_path: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Directory of the WP-03 discovery package; default ``services/web-collector/strategies/discovery``.
```

## jane_web_collector.settings.Settings.user_agent

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:93](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L93).

```python
user_agent: str = 'JaneBot/0.1 (+https://github.com/jane)'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Default User-Agent; ``rules.fetch.user_agent`` overrides it. The robots token is its first word.
```

## jane_web_collector.settings.Settings.lease_seconds

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:95](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L95).

```python
lease_seconds: int = Field(default=30, ge=2)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "30",
  "ge": "2"
}
```

### Опис із вихідного коду

```text
A running collection is owned by one instance; after this long without a heartbeat another takes it.
```

## jane_web_collector.settings.Settings.heartbeat_interval_ms

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:97](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L97).

```python
heartbeat_interval_ms: int = Field(default=5000, ge=50)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5000",
  "ge": "50"
}
```

### Опис із вихідного коду

```text
How often the owner renews the lease and checks for cancellation from other instances.
```

## jane_web_collector.settings.Settings.state_busy_timeout_ms

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:99](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L99).

```python
state_busy_timeout_ms: int = Field(default=10000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
How long a write waits for another process holding the SQLite lock.
```

## jane_web_collector.settings.Settings.idempotency_lease_ms

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:101](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L101).

```python
idempotency_lease_ms: int = Field(default=900000, ge=1000)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "900000",
  "ge": "1000"
}
```

### Опис із вихідного коду

```text
An ``Idempotency-Key`` claim of a killed instance (not renewed for this long) can be claimed again; a live
    instance renews its claims in the resume loop (R17).
```

## jane_web_collector.settings.Settings.egress_policy

**Метод.** Код: [services/web-collector/src/jane_web_collector/settings.py:118](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L118).

```python
def egress_policy(self) -> EgressPolicy:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `EgressPolicy`.

## jane_web_collector.settings.Settings.connection_policy

**Метод.** Код: [services/web-collector/src/jane_web_collector/settings.py:123](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L123).

```python
def connection_policy(self) -> ConnectionPolicy:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `ConnectionPolicy`.

## jane_web_collector.settings.Concurrency

**Клас.** Код: [services/web-collector/src/jane_web_collector/settings.py:131](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L131).

```python
class Concurrency(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_parallel_fetches](jane_web_collector.settings.md#jane_web_collectorsettingsconcurrencymax_parallel_fetches) | Поле | ні |
| [max_parallel_fetches_per_host](jane_web_collector.settings.md#jane_web_collectorsettingsconcurrencymax_parallel_fetches_per_host) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_host_limiter.py:22](../../../../../../services/web-collector/tests/test_host_limiter.py#L22).

```python
return ServiceLimits(
        rate=Rate(
            requests_per_second_per_host=rps, min_delay_ms_per_host=0, respect_crawl_delay=respect_crawl_delay
        ),
        concurrency=Concurrency(max_parallel_fetches_per_host=parallel),
    )
```

## jane_web_collector.settings.Concurrency.max_parallel_fetches

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:132](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L132).

```python
max_parallel_fetches: int = Field(default=4, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "4",
  "ge": "1"
}
```

## jane_web_collector.settings.Concurrency.max_parallel_fetches_per_host

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:133](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L133).

```python
max_parallel_fetches_per_host: int = Field(default=2, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2",
  "ge": "1"
}
```

## jane_web_collector.settings.Rate

**Клас.** Код: [services/web-collector/src/jane_web_collector/settings.py:136](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L136).

```python
class Rate(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [requests_per_second_per_host](jane_web_collector.settings.md#jane_web_collectorsettingsraterequests_per_second_per_host) | Поле | ні |
| [min_delay_ms_per_host](jane_web_collector.settings.md#jane_web_collectorsettingsratemin_delay_ms_per_host) | Поле | ні |
| [respect_crawl_delay](jane_web_collector.settings.md#jane_web_collectorsettingsraterespect_crawl_delay) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:115](../../../../../../services/web-collector/tests/test_connection_policy.py#L115).

```python
limits = ServiceLimits(rate=Rate(requests_per_second_per_host=1000, min_delay_ms_per_host=0))
```

Контекст і передумови: [services/web-collector/tests/test_egress_policy.py:98](../../../../../../services/web-collector/tests/test_egress_policy.py#L98).

```python
LIMITS = ServiceLimits(
    rate=Rate(requests_per_second_per_host=1000, min_delay_ms_per_host=0),
    retries=Retries(max_attempts=3, initial_backoff_ms=0, max_backoff_ms=0),
)
```

## jane_web_collector.settings.Rate.requests_per_second_per_host

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:137](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L137).

```python
requests_per_second_per_host: float = Field(default=1.0, gt=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1.0",
  "gt": "0"
}
```

## jane_web_collector.settings.Rate.min_delay_ms_per_host

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:138](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L138).

```python
min_delay_ms_per_host: int = Field(default=500, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "500",
  "ge": "0"
}
```

## jane_web_collector.settings.Rate.respect_crawl_delay

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:139](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L139).

```python
respect_crawl_delay: bool = True
```

Доступ: читання — так; запис — так.

## jane_web_collector.settings.Crawl

**Клас.** Код: [services/web-collector/src/jane_web_collector/settings.py:142](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L142).

```python
class Crawl(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_depth](jane_web_collector.settings.md#jane_web_collectorsettingscrawlmax_depth) | Поле | ні |
| [max_pages_per_run](jane_web_collector.settings.md#jane_web_collectorsettingscrawlmax_pages_per_run) | Поле | ні |
| [max_bytes_per_run](jane_web_collector.settings.md#jane_web_collectorsettingscrawlmax_bytes_per_run) | Поле | ні |
| [max_material_bytes](jane_web_collector.settings.md#jane_web_collectorsettingscrawlmax_material_bytes) | Поле | ні |
| [max_redirects](jane_web_collector.settings.md#jane_web_collectorsettingscrawlmax_redirects) | Поле | ні |
| [max_links_per_page](jane_web_collector.settings.md#jane_web_collectorsettingscrawlmax_links_per_page) | Поле | ні |
| [max_seed_urls](jane_web_collector.settings.md#jane_web_collectorsettingscrawlmax_seed_urls) | Поле | ні |
| [max_frontier_size](jane_web_collector.settings.md#jane_web_collectorsettingscrawlmax_frontier_size) | Поле | ні |
| [revisit_interval_seconds](jane_web_collector.settings.md#jane_web_collectorsettingscrawlrevisit_interval_seconds) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_web_collector.settings.Crawl.max_depth

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:143](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L143).

```python
max_depth: int = Field(default=5, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5",
  "ge": "0"
}
```

## jane_web_collector.settings.Crawl.max_pages_per_run

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:144](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L144).

```python
max_pages_per_run: int = Field(default=5000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5000",
  "ge": "1"
}
```

## jane_web_collector.settings.Crawl.max_bytes_per_run

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:145](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L145).

```python
max_bytes_per_run: int = Field(default=2 * 1024 ** 3, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2 * 1024 ** 3",
  "ge": "1"
}
```

## jane_web_collector.settings.Crawl.max_material_bytes

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:146](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L146).

```python
max_material_bytes: int = Field(default=10 * 1024 ** 2, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10 * 1024 ** 2",
  "ge": "1"
}
```

## jane_web_collector.settings.Crawl.max_redirects

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:147](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L147).

```python
max_redirects: int = Field(default=5, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5",
  "ge": "0"
}
```

## jane_web_collector.settings.Crawl.max_links_per_page

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:148](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L148).

```python
max_links_per_page: int = Field(default=2000, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2000",
  "ge": "0"
}
```

## jane_web_collector.settings.Crawl.max_seed_urls

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:149](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L149).

```python
max_seed_urls: int = Field(default=100000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "100000",
  "ge": "1"
}
```

## jane_web_collector.settings.Crawl.max_frontier_size

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:150](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L150).

```python
max_frontier_size: int = Field(default=100000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "100000",
  "ge": "1"
}
```

## jane_web_collector.settings.Crawl.revisit_interval_seconds

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:151](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L151).

```python
revisit_interval_seconds: int = Field(default=86400, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "86400",
  "ge": "0"
}
```

## jane_web_collector.settings.Timeouts

**Клас.** Код: [services/web-collector/src/jane_web_collector/settings.py:154](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L154).

```python
class Timeouts(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [connect_timeout_ms](jane_web_collector.settings.md#jane_web_collectorsettingstimeoutsconnect_timeout_ms) | Поле | ні |
| [request_timeout_ms](jane_web_collector.settings.md#jane_web_collectorsettingstimeoutsrequest_timeout_ms) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_web_collector.settings.Timeouts.connect_timeout_ms

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:155](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L155).

```python
connect_timeout_ms: int = Field(default=10000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10000",
  "ge": "1"
}
```

## jane_web_collector.settings.Timeouts.request_timeout_ms

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:156](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L156).

```python
request_timeout_ms: int = Field(default=30000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "30000",
  "ge": "1"
}
```

## jane_web_collector.settings.Retries

**Клас.** Код: [services/web-collector/src/jane_web_collector/settings.py:159](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L159).

```python
class Retries(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_attempts](jane_web_collector.settings.md#jane_web_collectorsettingsretriesmax_attempts) | Поле | ні |
| [initial_backoff_ms](jane_web_collector.settings.md#jane_web_collectorsettingsretriesinitial_backoff_ms) | Поле | ні |
| [max_backoff_ms](jane_web_collector.settings.md#jane_web_collectorsettingsretriesmax_backoff_ms) | Поле | ні |
| [backoff_multiplier](jane_web_collector.settings.md#jane_web_collectorsettingsretriesbackoff_multiplier) | Поле | ні |
| [jitter](jane_web_collector.settings.md#jane_web_collectorsettingsretriesjitter) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:182](../../../../../../services/web-collector/tests/test_connection_policy.py#L182).

```python
limits = ServiceLimits(retries=Retries(max_attempts=1))
```

Контекст і передумови: [services/web-collector/tests/test_egress_policy.py:98](../../../../../../services/web-collector/tests/test_egress_policy.py#L98).

```python
LIMITS = ServiceLimits(
    rate=Rate(requests_per_second_per_host=1000, min_delay_ms_per_host=0),
    retries=Retries(max_attempts=3, initial_backoff_ms=0, max_backoff_ms=0),
)
```

## jane_web_collector.settings.Retries.max_attempts

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:160](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L160).

```python
max_attempts: int = Field(default=3, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "3",
  "ge": "1"
}
```

## jane_web_collector.settings.Retries.initial_backoff_ms

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:161](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L161).

```python
initial_backoff_ms: int = Field(default=1000, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1000",
  "ge": "0"
}
```

## jane_web_collector.settings.Retries.max_backoff_ms

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:162](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L162).

```python
max_backoff_ms: int = Field(default=60000, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "60000",
  "ge": "0"
}
```

## jane_web_collector.settings.Retries.backoff_multiplier

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:163](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L163).

```python
backoff_multiplier: float = Field(default=2.0, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2.0",
  "ge": "1"
}
```

## jane_web_collector.settings.Retries.jitter

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:164](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L164).

```python
jitter: bool = True
```

Доступ: читання — так; запис — так.

## jane_web_collector.settings.Queue

**Клас.** Код: [services/web-collector/src/jane_web_collector/settings.py:167](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L167).

```python
class Queue(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_unacked_materials](jane_web_collector.settings.md#jane_web_collectorsettingsqueuemax_unacked_materials) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_web_collector.settings.Queue.max_unacked_materials

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:168](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L168).

```python
max_unacked_materials: int = Field(default=500, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "500",
  "ge": "1"
}
```

## jane_web_collector.settings.Transfer

**Клас.** Код: [services/web-collector/src/jane_web_collector/settings.py:171](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L171).

```python
class Transfer(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [inline_max_bytes](jane_web_collector.settings.md#jane_web_collectorsettingstransferinline_max_bytes) | Поле | ні |
| [transit_ttl_seconds](jane_web_collector.settings.md#jane_web_collectorsettingstransfertransit_ttl_seconds) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_web_collector.settings.Transfer.inline_max_bytes

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:172](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L172).

```python
inline_max_bytes: int = Field(default=262144, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "262144",
  "ge": "0"
}
```

## jane_web_collector.settings.Transfer.transit_ttl_seconds

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:173](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L173).

```python
transit_ttl_seconds: int = Field(default=604800, ge=60)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "604800",
  "ge": "60"
}
```

## jane_web_collector.settings.Collector

**Клас.** Код: [services/web-collector/src/jane_web_collector/settings.py:176](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L176).

```python
class Collector(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_wait_ms](jane_web_collector.settings.md#jane_web_collectorsettingscollectormax_wait_ms) | Поле | ні |
| [robots_cache_ttl_seconds](jane_web_collector.settings.md#jane_web_collectorsettingscollectorrobots_cache_ttl_seconds) | Поле | ні |
| [robots_max_bytes](jane_web_collector.settings.md#jane_web_collectorsettingscollectorrobots_max_bytes) | Поле | ні |
| [max_retry_after_seconds](jane_web_collector.settings.md#jane_web_collectorsettingscollectormax_retry_after_seconds) | Поле | ні |
| [backpressure_poll_ms](jane_web_collector.settings.md#jane_web_collectorsettingscollectorbackpressure_poll_ms) | Поле | ні |
| [long_poll_interval_ms](jane_web_collector.settings.md#jane_web_collectorsettingscollectorlong_poll_interval_ms) | Поле | ні |
| [gc_interval_seconds](jane_web_collector.settings.md#jane_web_collectorsettingscollectorgc_interval_seconds) | Поле | ні |
| [host_state_prune_interval_seconds](jane_web_collector.settings.md#jane_web_collectorsettingscollectorhost_state_prune_interval_seconds) | Поле | ні |
| [shared_host_limits](jane_web_collector.settings.md#jane_web_collectorsettingscollectorshared_host_limits) | Поле | ні |
| [shared_host_poll_ms](jane_web_collector.settings.md#jane_web_collectorsettingscollectorshared_host_poll_ms) | Поле | ні |
| [shared_host_ttl_seconds](jane_web_collector.settings.md#jane_web_collectorsettingscollectorshared_host_ttl_seconds) | Поле | ні |
| [render_timeout_ms](jane_web_collector.settings.md#jane_web_collectorsettingscollectorrender_timeout_ms) | Поле | ні |
| [render_extra_wait_ms](jane_web_collector.settings.md#jane_web_collectorsettingscollectorrender_extra_wait_ms) | Поле | ні |
| [render_max_pages](jane_web_collector.settings.md#jane_web_collectorsettingscollectorrender_max_pages) | Поле | ні |
| [render_max_transfer_bytes](jane_web_collector.settings.md#jane_web_collectorsettingscollectorrender_max_transfer_bytes) | Поле | ні |
| [render_launch_timeout_ms](jane_web_collector.settings.md#jane_web_collectorsettingscollectorrender_launch_timeout_ms) | Поле | ні |
| [render_close_timeout_ms](jane_web_collector.settings.md#jane_web_collectorsettingscollectorrender_close_timeout_ms) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Service-specific limits (not in the contract; visible only in the start-up log).
```

## jane_web_collector.settings.Collector.max_wait_ms

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:179](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L179).

```python
max_wait_ms: int = Field(default=30000, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "30000",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Upper bound of ``wait_ms`` long-poll on ``/materials``.
```

## jane_web_collector.settings.Collector.robots_cache_ttl_seconds

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:181](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L181).

```python
robots_cache_ttl_seconds: int = Field(default=3600, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "3600",
  "ge": "0"
}
```

## jane_web_collector.settings.Collector.robots_max_bytes

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:182](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L182).

```python
robots_max_bytes: int = Field(default=512000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "512000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
robots.txt larger than this is truncated (RFC 9309 allows >= 500 KiB).
```

## jane_web_collector.settings.Collector.max_retry_after_seconds

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:184](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L184).

```python
max_retry_after_seconds: int = Field(default=300, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "300",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
A source asking to wait longer (Retry-After, Crawl-delay) makes the URL fail with ``rate_limited``.
```

## jane_web_collector.settings.Collector.backpressure_poll_ms

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:186](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L186).

```python
backpressure_poll_ms: int = Field(default=1000, ge=10)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1000",
  "ge": "10"
}
```

### Опис із вихідного коду

```text
While paused by backpressure: how often the buffer is re-checked (acks may arrive via another instance).
```

## jane_web_collector.settings.Collector.long_poll_interval_ms

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:188](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L188).

```python
long_poll_interval_ms: int = Field(default=100, ge=10)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "100",
  "ge": "10"
}
```

### Опис із вихідного коду

```text
``/materials?wait_ms=``: how often new materials are looked for while waiting.
```

## jane_web_collector.settings.Collector.gc_interval_seconds

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:190](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L190).

```python
gc_interval_seconds: int = Field(default=3600, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "3600",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
How often expired collections and transit files are cleaned up.
```

## jane_web_collector.settings.Collector.host_state_prune_interval_seconds

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:192](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L192).

```python
host_state_prune_interval_seconds: int = Field(default=60, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "60",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
How often the shared per-host limiter drops the state of hosts nobody uses any more.
```

## jane_web_collector.settings.Collector.shared_host_limits

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:194](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L194).

```python
shared_host_limits: bool = True
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Coordinate the per-host limits with the other instances that share the state store (R15).
```

## jane_web_collector.settings.Collector.shared_host_poll_ms

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:196](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L196).

```python
shared_host_poll_ms: int = Field(default=100, ge=10)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "100",
  "ge": "10"
}
```

### Опис із вихідного коду

```text
A request waiting for a host slot that other instances hold re-checks this often.
```

## jane_web_collector.settings.Collector.shared_host_ttl_seconds

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:198](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L198).

```python
shared_host_ttl_seconds: int = Field(default=120, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "120",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
How long the registration, slot or place in line of an instance that died keeps limiting the others. A live
    instance renews them every TTL / 3 (also during long downloads, Retry-After and Crawl-delay waits), so the TTL
    need not exceed them; start-up rule: TTL * 2/3 > ``STATE_BUSY_TIMEOUT_MS``.
```

## jane_web_collector.settings.Collector.render_timeout_ms

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:202](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L202).

```python
render_timeout_ms: int = Field(default=30000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "30000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
``fetch.render_js``: how long a page may load in the browser (navigation and ``RENDER_WAIT_UNTIL``); after
    that the DOM is taken as it is (diagnostic ``render_incomplete``). Taking the DOM has the same bound.
```

## jane_web_collector.settings.Collector.render_extra_wait_ms

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:205](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L205).

```python
render_extra_wait_ms: int = Field(default=0, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "0",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Extra pause after the wait condition, for scripts that fill the page late (within ``render_timeout_ms``).
```

## jane_web_collector.settings.Collector.render_max_pages

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:207](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L207).

```python
render_max_pages: int = Field(default=2, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Browser pages rendering at once in this process (every collection and fetch together); others wait.
```

## jane_web_collector.settings.Collector.render_max_transfer_bytes

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:209](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L209).

```python
render_max_transfer_bytes: int = Field(default=50 * 1024 ** 2, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "50 * 1024 ** 2",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Bytes the browser may download for one page (scripts, XHR, styles); then its connections are cut and the
    DOM is taken as it is (diagnostic ``render_budget_exceeded``).
```

## jane_web_collector.settings.Collector.render_launch_timeout_ms

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:212](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L212).

```python
render_launch_timeout_ms: int = Field(default=30000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "30000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
How long starting headless Chromium may take; longer counts as "no browser" (``not_implemented``).
```

## jane_web_collector.settings.Collector.render_close_timeout_ms

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:214](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L214).

```python
render_close_timeout_ms: int = Field(default=30000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "30000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
How long closing a page's browser context, and the browser and its driver on restart or stop, may take; a
    context that does not close in time makes the browser start again before the next page. Generous on purpose:
    Chromium on Windows sometimes needs several seconds to exit, and a browser given up on may be left running.
```

## jane_web_collector.settings.ServiceLimits

**Клас.** Код: [services/web-collector/src/jane_web_collector/settings.py:220](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L220).

```python
class ServiceLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [concurrency](jane_web_collector.settings.md#jane_web_collectorsettingsservicelimitsconcurrency) | Поле | ні |
| [rate](jane_web_collector.settings.md#jane_web_collectorsettingsservicelimitsrate) | Поле | ні |
| [crawl](jane_web_collector.settings.md#jane_web_collectorsettingsservicelimitscrawl) | Поле | ні |
| [timeouts](jane_web_collector.settings.md#jane_web_collectorsettingsservicelimitstimeouts) | Поле | ні |
| [retries](jane_web_collector.settings.md#jane_web_collectorsettingsservicelimitsretries) | Поле | ні |
| [queue](jane_web_collector.settings.md#jane_web_collectorsettingsservicelimitsqueue) | Поле | ні |
| [transfer](jane_web_collector.settings.md#jane_web_collectorsettingsservicelimitstransfer) | Поле | ні |
| [jobs](jane_web_collector.settings.md#jane_web_collectorsettingsservicelimitsjobs) | Поле | ні |
| [idempotency](jane_web_collector.settings.md#jane_web_collectorsettingsservicelimitsidempotency) | Поле | ні |
| [page](jane_web_collector.settings.md#jane_web_collectorsettingsservicelimitspage) | Поле | ні |
| [collector](jane_web_collector.settings.md#jane_web_collectorsettingsservicelimitscollector) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Limits of the Web Collector; group and field names follow ``limits.schema.json``.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:115](../../../../../../services/web-collector/tests/test_connection_policy.py#L115).

```python
limits = ServiceLimits(rate=Rate(requests_per_second_per_host=1000, min_delay_ms_per_host=0))
```

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:182](../../../../../../services/web-collector/tests/test_connection_policy.py#L182).

```python
limits = ServiceLimits(retries=Retries(max_attempts=1))
```

## jane_web_collector.settings.ServiceLimits.concurrency

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:223](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L223).

```python
concurrency: Concurrency = contract_field('concurrency', Concurrency())
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'concurrency'"
}
```

## jane_web_collector.settings.ServiceLimits.rate

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:224](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L224).

```python
rate: Rate = contract_field('rate', Rate())
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'rate'"
}
```

## jane_web_collector.settings.ServiceLimits.crawl

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:225](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L225).

```python
crawl: Crawl = contract_field('crawl', Crawl())
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'crawl'"
}
```

## jane_web_collector.settings.ServiceLimits.timeouts

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:226](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L226).

```python
timeouts: Timeouts = contract_field('timeouts', Timeouts())
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'timeouts'"
}
```

## jane_web_collector.settings.ServiceLimits.retries

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:227](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L227).

```python
retries: Retries = contract_field('retries', Retries())
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'retries'"
}
```

## jane_web_collector.settings.ServiceLimits.queue

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:228](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L228).

```python
queue: Queue = contract_field('queue', Queue())
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'queue'"
}
```

## jane_web_collector.settings.ServiceLimits.transfer

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:229](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L229).

```python
transfer: Transfer = contract_field('transfer', Transfer())
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'transfer'"
}
```

## jane_web_collector.settings.ServiceLimits.jobs

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:230](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L230).

```python
jobs: JobLimits = JobLimits()
```

Доступ: читання — так; запис — так.

## jane_web_collector.settings.ServiceLimits.idempotency

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:231](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L231).

```python
idempotency: IdempotencyLimits = IdempotencyLimits()
```

Доступ: читання — так; запис — так.

## jane_web_collector.settings.ServiceLimits.page

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:232](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L232).

```python
page: PageLimits = PageLimits()
```

Доступ: читання — так; запис — так.

## jane_web_collector.settings.ServiceLimits.collector

**Поле.** Код: [services/web-collector/src/jane_web_collector/settings.py:233](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L233).

```python
collector: Collector = Collector()
```

Доступ: читання — так; запис — так.

## jane_web_collector.settings.contract_layer

**Функція.** Код: [services/web-collector/src/jane_web_collector/settings.py:245](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L245).

```python
def contract_layer(layer: LimitLayer) -> LimitLayer:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `layer` | `LimitLayer` | `—` | positional-or-keyword |

Результат: `LimitLayer`.

### Опис із вихідного коду

```text
A contract-shaped ``Limits`` document (``rules.limits``, request ``limits``, ``strategies[].limits``) as a
jane-kit layer: contract paths go to the fields that declare them (``transfer.job_retention_seconds`` ->
``jobs.job_retention_seconds``), contract limits the collector does not have are ignored, anything else is a
:class:`~jane_kit.config.LimitError` - exactly as for the platform profile.
```

## jane_web_collector.settings.to_contract

**Функція.** Код: [services/web-collector/src/jane_web_collector/settings.py:253](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L253).

```python
def to_contract(limits: ServiceLimits) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
Model -> contract ``Limits`` document (only fields that exist in the contract), by jane-kit's mapping.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_limits_profile.py:97](../../../../../../services/web-collector/tests/test_limits_profile.py#L97).

```python
assert set(to_contract(ServiceLimits())) == {
        "concurrency",
        "rate",
        "crawl",
        "timeouts",
        "retries",
        "queue",
        "transfer",
    }
```

Контекст і передумови: [services/web-collector/tests/test_limits_profile.py:106](../../../../../../services/web-collector/tests/test_limits_profile.py#L106).

```python
assert to_contract(ServiceLimits())["transfer"]["job_retention_seconds"] == 86_400
```

## jane_web_collector.settings.platform_layers

**Функція.** Код: [services/web-collector/src/jane_web_collector/settings.py:261](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L261).

```python
def platform_layers(settings: Settings) -> list[LimitLayer]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings` | `—` | positional-or-keyword |

Результат: `list[LimitLayer]`.

### Опис із вихідного коду

```text
jane-kit's platform layers: the ``PlatformLimits`` file (shared profile) and the env overrides.
```

## jane_web_collector.settings.resolve_service_limits

**Функція.** Код: [services/web-collector/src/jane_web_collector/settings.py:266](../../../../../../services/web-collector/src/jane_web_collector/settings.py#L266).

```python
def resolve_service_limits(settings: Settings, *extra: LimitLayer) -> ResolvedLimits[ServiceLimits]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings` | `—` | positional-or-keyword |
| `extra` | `LimitLayer` | `—` | var-positional |

Результат: `ResolvedLimits[ServiceLimits]`.

### Опис із вихідного коду

```text
Defaults <- platform file (``..._LIMITS_FILE``) <- ``JANE_WEB_COLLECTOR_LIMITS__*`` <- ``extra``
(source/request/strategy layers, contract-shaped). Invalid limits raise :class:`~jane_kit.config.LimitError`.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_limits_profile.py:49](../../../../../../services/web-collector/tests/test_limits_profile.py#L49).

```python
resolved = resolve_service_limits(make_settings(tmp_path, limits_file=path))
```

Контекст і передумови: [services/web-collector/tests/test_limits_profile.py:76](../../../../../../services/web-collector/tests/test_limits_profile.py#L76).

```python
resolved = resolve_service_limits(make_settings(tmp_path))
```
