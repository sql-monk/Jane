# jane_telegram_collector.settings

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_telegram_collector.settings.ENV_PREFIX](#jane_telegram_collectorsettingsenv_prefix)
- [jane_telegram_collector.settings.LIMITS_ENV_PREFIX](#jane_telegram_collectorsettingslimits_env_prefix)
- [jane_telegram_collector.settings.log](#jane_telegram_collectorsettingslog)
- [jane_telegram_collector.settings.Settings](#jane_telegram_collectorsettingssettings)
- [jane_telegram_collector.settings.Settings.model_config](#jane_telegram_collectorsettingssettingsmodel_config)
- [jane_telegram_collector.settings.Settings.service_name](#jane_telegram_collectorsettingssettingsservice_name)
- [jane_telegram_collector.settings.Settings.port](#jane_telegram_collectorsettingssettingsport)
- [jane_telegram_collector.settings.Settings.state_dir](#jane_telegram_collectorsettingssettingsstate_dir)
- [jane_telegram_collector.settings.Settings.client_backend](#jane_telegram_collectorsettingssettingsclient_backend)
- [jane_telegram_collector.settings.Settings.recordings_dir](#jane_telegram_collectorsettingssettingsrecordings_dir)
- [jane_telegram_collector.settings.Settings.default_account_connection_id](#jane_telegram_collectorsettingssettingsdefault_account_connection_id)
- [jane_telegram_collector.settings.Settings.transit_dir](#jane_telegram_collectorsettingssettingstransit_dir)
- [jane_telegram_collector.settings.Settings.rules_dir](#jane_telegram_collectorsettingssettingsrules_dir)
- [jane_telegram_collector.settings.Settings.registry_url](#jane_telegram_collectorsettingssettingsregistry_url)
- [jane_telegram_collector.settings.Settings.registry_token_env](#jane_telegram_collectorsettingssettingsregistry_token_env)
- [jane_telegram_collector.settings.Settings.contracts_dir](#jane_telegram_collectorsettingssettingscontracts_dir)
- [jane_telegram_collector.settings.Settings.secret_env_prefix](#jane_telegram_collectorsettingssettingssecret_env_prefix)
- [jane_telegram_collector.settings.Settings.secret_files_dir](#jane_telegram_collectorsettingssettingssecret_files_dir)
- [jane_telegram_collector.settings.Settings.telegram_host_allowlist](#jane_telegram_collectorsettingssettingstelegram_host_allowlist)
- [jane_telegram_collector.settings.Settings.lease_seconds](#jane_telegram_collectorsettingssettingslease_seconds)
- [jane_telegram_collector.settings.Settings.heartbeat_interval_ms](#jane_telegram_collectorsettingssettingsheartbeat_interval_ms)
- [jane_telegram_collector.settings.Settings.state_busy_timeout_ms](#jane_telegram_collectorsettingssettingsstate_busy_timeout_ms)
- [jane_telegram_collector.settings.Settings.idempotency_lease_ms](#jane_telegram_collectorsettingssettingsidempotency_lease_ms)
- [jane_telegram_collector.settings.Settings.connection_policy](#jane_telegram_collectorsettingssettingsconnection_policy)
- [jane_telegram_collector.settings.Rate](#jane_telegram_collectorsettingsrate)
- [jane_telegram_collector.settings.Rate.min_delay_ms_per_host](#jane_telegram_collectorsettingsratemin_delay_ms_per_host)
- [jane_telegram_collector.settings.Timeouts](#jane_telegram_collectorsettingstimeouts)
- [jane_telegram_collector.settings.Timeouts.connect_timeout_ms](#jane_telegram_collectorsettingstimeoutsconnect_timeout_ms)
- [jane_telegram_collector.settings.Timeouts.request_timeout_ms](#jane_telegram_collectorsettingstimeoutsrequest_timeout_ms)
- [jane_telegram_collector.settings.Retries](#jane_telegram_collectorsettingsretries)
- [jane_telegram_collector.settings.Retries.max_attempts](#jane_telegram_collectorsettingsretriesmax_attempts)
- [jane_telegram_collector.settings.Retries.initial_backoff_ms](#jane_telegram_collectorsettingsretriesinitial_backoff_ms)
- [jane_telegram_collector.settings.Retries.max_backoff_ms](#jane_telegram_collectorsettingsretriesmax_backoff_ms)
- [jane_telegram_collector.settings.Retries.backoff_multiplier](#jane_telegram_collectorsettingsretriesbackoff_multiplier)
- [jane_telegram_collector.settings.Retries.jitter](#jane_telegram_collectorsettingsretriesjitter)
- [jane_telegram_collector.settings.Queue](#jane_telegram_collectorsettingsqueue)
- [jane_telegram_collector.settings.Queue.max_unacked_materials](#jane_telegram_collectorsettingsqueuemax_unacked_materials)
- [jane_telegram_collector.settings.Transfer](#jane_telegram_collectorsettingstransfer)
- [jane_telegram_collector.settings.Transfer.inline_max_bytes](#jane_telegram_collectorsettingstransferinline_max_bytes)
- [jane_telegram_collector.settings.Transfer.transit_ttl_seconds](#jane_telegram_collectorsettingstransfertransit_ttl_seconds)
- [jane_telegram_collector.settings.Telegram](#jane_telegram_collectorsettingstelegram)
- [jane_telegram_collector.settings.Telegram.max_messages_per_run](#jane_telegram_collectorsettingstelegrammax_messages_per_run)
- [jane_telegram_collector.settings.Telegram.max_media_bytes](#jane_telegram_collectorsettingstelegrammax_media_bytes)
- [jane_telegram_collector.settings.Telegram.max_flood_wait_seconds](#jane_telegram_collectorsettingstelegrammax_flood_wait_seconds)
- [jane_telegram_collector.settings.Collector](#jane_telegram_collectorsettingscollector)
- [jane_telegram_collector.settings.Collector.history_page_size](#jane_telegram_collectorsettingscollectorhistory_page_size)
- [jane_telegram_collector.settings.Collector.changes_page_size](#jane_telegram_collectorsettingscollectorchanges_page_size)
- [jane_telegram_collector.settings.Collector.max_wait_ms](#jane_telegram_collectorsettingscollectormax_wait_ms)
- [jane_telegram_collector.settings.Collector.long_poll_interval_ms](#jane_telegram_collectorsettingscollectorlong_poll_interval_ms)
- [jane_telegram_collector.settings.Collector.backpressure_poll_ms](#jane_telegram_collectorsettingscollectorbackpressure_poll_ms)
- [jane_telegram_collector.settings.Collector.gc_interval_seconds](#jane_telegram_collectorsettingscollectorgc_interval_seconds)
- [jane_telegram_collector.settings.ServiceLimits](#jane_telegram_collectorsettingsservicelimits)
- [jane_telegram_collector.settings.ServiceLimits.rate](#jane_telegram_collectorsettingsservicelimitsrate)
- [jane_telegram_collector.settings.ServiceLimits.timeouts](#jane_telegram_collectorsettingsservicelimitstimeouts)
- [jane_telegram_collector.settings.ServiceLimits.retries](#jane_telegram_collectorsettingsservicelimitsretries)
- [jane_telegram_collector.settings.ServiceLimits.queue](#jane_telegram_collectorsettingsservicelimitsqueue)
- [jane_telegram_collector.settings.ServiceLimits.transfer](#jane_telegram_collectorsettingsservicelimitstransfer)
- [jane_telegram_collector.settings.ServiceLimits.telegram](#jane_telegram_collectorsettingsservicelimitstelegram)
- [jane_telegram_collector.settings.ServiceLimits.jobs](#jane_telegram_collectorsettingsservicelimitsjobs)
- [jane_telegram_collector.settings.ServiceLimits.idempotency](#jane_telegram_collectorsettingsservicelimitsidempotency)
- [jane_telegram_collector.settings.ServiceLimits.page](#jane_telegram_collectorsettingsservicelimitspage)
- [jane_telegram_collector.settings.ServiceLimits.collector](#jane_telegram_collectorsettingsservicelimitscollector)
- [jane_telegram_collector.settings.contract_layer](#jane_telegram_collectorsettingscontract_layer)
- [jane_telegram_collector.settings.to_contract](#jane_telegram_collectorsettingsto_contract)
- [jane_telegram_collector.settings.platform_layers](#jane_telegram_collectorsettingsplatform_layers)
- [jane_telegram_collector.settings.resolve_service_limits](#jane_telegram_collectorsettingsresolve_service_limits)

## jane_telegram_collector.settings.ENV_PREFIX

**Константа.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:39](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L39).

```python
ENV_PREFIX = 'JANE_TELEGRAM_COLLECTOR_'
```

## jane_telegram_collector.settings.LIMITS_ENV_PREFIX

**Константа.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:40](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L40).

```python
LIMITS_ENV_PREFIX = f'{ENV_PREFIX}LIMITS__'
```

## jane_telegram_collector.settings.log

**Змінна.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:42](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L42).

```python
log = logging.getLogger(__name__)
```

## jane_telegram_collector.settings.Settings

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:45](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L45).

```python
class Settings(JaneSettings):
```

Базові типи / інтерфейси: `JaneSettings`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_config](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingsmodel_config) | Поле | ні |
| [service_name](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingsservice_name) | Поле | ні |
| [port](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingsport) | Поле | ні |
| [state_dir](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingsstate_dir) | Поле | ні |
| [client_backend](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingsclient_backend) | Поле | ні |
| [recordings_dir](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingsrecordings_dir) | Поле | ні |
| [default_account_connection_id](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingsdefault_account_connection_id) | Поле | ні |
| [transit_dir](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingstransit_dir) | Поле | ні |
| [rules_dir](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingsrules_dir) | Поле | ні |
| [registry_url](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingsregistry_url) | Поле | ні |
| [registry_token_env](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingsregistry_token_env) | Поле | ні |
| [contracts_dir](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingscontracts_dir) | Поле | ні |
| [secret_env_prefix](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingssecret_env_prefix) | Поле | ні |
| [secret_files_dir](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingssecret_files_dir) | Поле | ні |
| [telegram_host_allowlist](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingstelegram_host_allowlist) | Поле | ні |
| [lease_seconds](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingslease_seconds) | Поле | ні |
| [heartbeat_interval_ms](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingsheartbeat_interval_ms) | Поле | ні |
| [state_busy_timeout_ms](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingsstate_busy_timeout_ms) | Поле | ні |
| [idempotency_lease_ms](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingsidempotency_lease_ms) | Поле | ні |
| [connection_policy](jane_telegram_collector.settings.md#jane_telegram_collectorsettingssettingsconnection_policy) | Метод | ні |
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

## jane_telegram_collector.settings.Settings.model_config

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:46](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L46).

```python
model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra='ignore', env_nested_delimiter='__')
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.settings.Settings.service_name

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:48](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L48).

```python
service_name: str = 'telegram-collector'
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.settings.Settings.port

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:49](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L49).

```python
port: int = 8102
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.settings.Settings.state_dir

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:51](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L51).

```python
state_dir: Path = Path('.jane/telegram-collector')
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Own state store (SQLite ``state.db``): runs, channel cursors, seen revisions, buffer, jobs.
```

## jane_telegram_collector.settings.Settings.client_backend

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:53](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L53).

```python
client_backend: str = 'recorded'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Telegram client: ``recorded`` (JSON recordings, tests/demos), ``telethon`` (optional extra) or
    ``<module>:<factory>`` returning a :class:`~jane_telegram_collector.client.ClientFactory`.
```

## jane_telegram_collector.settings.Settings.recordings_dir

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:56](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L56).

```python
recordings_dir: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``recorded`` backend: directory with ``<username or channel_id>.json`` recordings.
```

### Приклади з тестів

Контекст і передумови: [services/telegram-collector/tests/conftest.py:55](../../../../../../services/telegram-collector/tests/conftest.py#L55).

```python
assert settings.recordings_dir is not None
```

## jane_telegram_collector.settings.Settings.default_account_connection_id

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:58](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L58).

```python
default_account_connection_id: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Connection (``kind=telegram_account``) used when rules name none (e.g. ``/v1/fetches`` without rules).
```

## jane_telegram_collector.settings.Settings.transit_dir

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:60](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L60).

```python
transit_dir: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Transit blob store for large content and media (``file://`` ContentRef). Unset: inline only.
```

## jane_telegram_collector.settings.Settings.rules_dir

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:62](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L62).

```python
rules_dir: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Local collector-rules packages for ``rules_ref`` without a registry (``<package_id>/<version>/``).
```

## jane_telegram_collector.settings.Settings.registry_url

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:64](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L64).

```python
registry_url: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
registry.v1 base URL for ``rules_ref``; checked after ``rules_dir``.
```

## jane_telegram_collector.settings.Settings.registry_token_env

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:66](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L66).

```python
registry_token_env: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Name of the environment variable holding the bearer token for the registry (never the value).
```

## jane_telegram_collector.settings.Settings.contracts_dir

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:68](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L68).

```python
contracts_dir: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``contracts/`` with the JSON Schemas; default: ``JANE_CONTRACTS_DIR`` or the checkout's contracts.
```

## jane_telegram_collector.settings.Settings.secret_env_prefix

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:70](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L70).

```python
secret_env_prefix: str = 'JANE_SECRET_'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``env:`` secret references may name only variables with this prefix.
```

## jane_telegram_collector.settings.Settings.secret_files_dir

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:72](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L72).

```python
secret_files_dir: Path | None = Path('/run/secrets')
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``file:`` secret references must point inside this directory (unset: ``file:`` disabled).
```

## jane_telegram_collector.settings.Settings.telegram_host_allowlist

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:74](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L74).

```python
telegram_host_allowlist: list[str] = Field(default_factory=list)
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
Hosts allowed in host-like connection params (``server``, ``proxy_host``...); default: none.
```

## jane_telegram_collector.settings.Settings.lease_seconds

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:76](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L76).

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

## jane_telegram_collector.settings.Settings.heartbeat_interval_ms

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:78](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L78).

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
How often the owner renews the lease and checks for cancellation requested through other instances.
```

## jane_telegram_collector.settings.Settings.state_busy_timeout_ms

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:80](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L80).

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

## jane_telegram_collector.settings.Settings.idempotency_lease_ms

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:82](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L82).

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

## jane_telegram_collector.settings.Settings.connection_policy

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:86](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L86).

```python
def connection_policy(self) -> ConnectionPolicy:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `ConnectionPolicy`.

## jane_telegram_collector.settings.Rate

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:107](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L107).

```python
class Rate(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [min_delay_ms_per_host](jane_telegram_collector.settings.md#jane_telegram_collectorsettingsratemin_delay_ms_per_host) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_telegram_collector.settings.Rate.min_delay_ms_per_host

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:108](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L108).

```python
min_delay_ms_per_host: int = Field(default=200, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "200",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Minimum interval between two Telegram API calls of one run (the API is the only "host").
```

## jane_telegram_collector.settings.Timeouts

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:112](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L112).

```python
class Timeouts(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [connect_timeout_ms](jane_telegram_collector.settings.md#jane_telegram_collectorsettingstimeoutsconnect_timeout_ms) | Поле | ні |
| [request_timeout_ms](jane_telegram_collector.settings.md#jane_telegram_collectorsettingstimeoutsrequest_timeout_ms) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_telegram_collector.settings.Timeouts.connect_timeout_ms

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:113](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L113).

```python
connect_timeout_ms: int = Field(default=15000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "15000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Opening the Telegram client (connect + authorization check).
```

## jane_telegram_collector.settings.Timeouts.request_timeout_ms

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:115](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L115).

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

### Опис із вихідного коду

```text
One Telegram API call (history page, difference, message, media download).
```

## jane_telegram_collector.settings.Retries

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:119](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L119).

```python
class Retries(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_attempts](jane_telegram_collector.settings.md#jane_telegram_collectorsettingsretriesmax_attempts) | Поле | ні |
| [initial_backoff_ms](jane_telegram_collector.settings.md#jane_telegram_collectorsettingsretriesinitial_backoff_ms) | Поле | ні |
| [max_backoff_ms](jane_telegram_collector.settings.md#jane_telegram_collectorsettingsretriesmax_backoff_ms) | Поле | ні |
| [backoff_multiplier](jane_telegram_collector.settings.md#jane_telegram_collectorsettingsretriesbackoff_multiplier) | Поле | ні |
| [jitter](jane_telegram_collector.settings.md#jane_telegram_collectorsettingsretriesjitter) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_telegram_collector.settings.Retries.max_attempts

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:120](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L120).

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

## jane_telegram_collector.settings.Retries.initial_backoff_ms

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:121](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L121).

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

## jane_telegram_collector.settings.Retries.max_backoff_ms

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:122](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L122).

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

## jane_telegram_collector.settings.Retries.backoff_multiplier

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:123](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L123).

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

## jane_telegram_collector.settings.Retries.jitter

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:124](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L124).

```python
jitter: bool = True
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.settings.Queue

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:127](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L127).

```python
class Queue(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_unacked_materials](jane_telegram_collector.settings.md#jane_telegram_collectorsettingsqueuemax_unacked_materials) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_telegram_collector.settings.Queue.max_unacked_materials

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:128](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L128).

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

## jane_telegram_collector.settings.Transfer

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:131](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L131).

```python
class Transfer(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [inline_max_bytes](jane_telegram_collector.settings.md#jane_telegram_collectorsettingstransferinline_max_bytes) | Поле | ні |
| [transit_ttl_seconds](jane_telegram_collector.settings.md#jane_telegram_collectorsettingstransfertransit_ttl_seconds) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_telegram_collector.settings.Transfer.inline_max_bytes

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:132](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L132).

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

## jane_telegram_collector.settings.Transfer.transit_ttl_seconds

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:133](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L133).

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

## jane_telegram_collector.settings.Telegram

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:136](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L136).

```python
class Telegram(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_messages_per_run](jane_telegram_collector.settings.md#jane_telegram_collectorsettingstelegrammax_messages_per_run) | Поле | ні |
| [max_media_bytes](jane_telegram_collector.settings.md#jane_telegram_collectorsettingstelegrammax_media_bytes) | Поле | ні |
| [max_flood_wait_seconds](jane_telegram_collector.settings.md#jane_telegram_collectorsettingstelegrammax_flood_wait_seconds) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_telegram_collector.settings.Telegram.max_messages_per_run

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:137](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L137).

```python
max_messages_per_run: int = Field(default=10000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10000",
  "ge": "1"
}
```

## jane_telegram_collector.settings.Telegram.max_media_bytes

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:138](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L138).

```python
max_media_bytes: int = Field(default=20 * 1024 ** 2, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "20 * 1024 ** 2",
  "ge": "0"
}
```

## jane_telegram_collector.settings.Telegram.max_flood_wait_seconds

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:139](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L139).

```python
max_flood_wait_seconds: int = Field(default=300, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "300",
  "ge": "0"
}
```

## jane_telegram_collector.settings.Collector

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:142](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L142).

```python
class Collector(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [history_page_size](jane_telegram_collector.settings.md#jane_telegram_collectorsettingscollectorhistory_page_size) | Поле | ні |
| [changes_page_size](jane_telegram_collector.settings.md#jane_telegram_collectorsettingscollectorchanges_page_size) | Поле | ні |
| [max_wait_ms](jane_telegram_collector.settings.md#jane_telegram_collectorsettingscollectormax_wait_ms) | Поле | ні |
| [long_poll_interval_ms](jane_telegram_collector.settings.md#jane_telegram_collectorsettingscollectorlong_poll_interval_ms) | Поле | ні |
| [backpressure_poll_ms](jane_telegram_collector.settings.md#jane_telegram_collectorsettingscollectorbackpressure_poll_ms) | Поле | ні |
| [gc_interval_seconds](jane_telegram_collector.settings.md#jane_telegram_collectorsettingscollectorgc_interval_seconds) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Service-specific limits (not in the contract; visible in the start-up log).
```

## jane_telegram_collector.settings.Collector.history_page_size

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:145](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L145).

```python
history_page_size: int = Field(default=100, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "100",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Messages per history request (Telegram returns at most 100).
```

## jane_telegram_collector.settings.Collector.changes_page_size

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:147](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L147).

```python
changes_page_size: int = Field(default=100, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "100",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Updates per ``getChannelDifference`` request.
```

## jane_telegram_collector.settings.Collector.max_wait_ms

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:149](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L149).

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

## jane_telegram_collector.settings.Collector.long_poll_interval_ms

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:151](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L151).

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

## jane_telegram_collector.settings.Collector.backpressure_poll_ms

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:153](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L153).

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

## jane_telegram_collector.settings.Collector.gc_interval_seconds

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:155](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L155).

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

## jane_telegram_collector.settings.ServiceLimits

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:159](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L159).

```python
class ServiceLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [rate](jane_telegram_collector.settings.md#jane_telegram_collectorsettingsservicelimitsrate) | Поле | ні |
| [timeouts](jane_telegram_collector.settings.md#jane_telegram_collectorsettingsservicelimitstimeouts) | Поле | ні |
| [retries](jane_telegram_collector.settings.md#jane_telegram_collectorsettingsservicelimitsretries) | Поле | ні |
| [queue](jane_telegram_collector.settings.md#jane_telegram_collectorsettingsservicelimitsqueue) | Поле | ні |
| [transfer](jane_telegram_collector.settings.md#jane_telegram_collectorsettingsservicelimitstransfer) | Поле | ні |
| [telegram](jane_telegram_collector.settings.md#jane_telegram_collectorsettingsservicelimitstelegram) | Поле | ні |
| [jobs](jane_telegram_collector.settings.md#jane_telegram_collectorsettingsservicelimitsjobs) | Поле | ні |
| [idempotency](jane_telegram_collector.settings.md#jane_telegram_collectorsettingsservicelimitsidempotency) | Поле | ні |
| [page](jane_telegram_collector.settings.md#jane_telegram_collectorsettingsservicelimitspage) | Поле | ні |
| [collector](jane_telegram_collector.settings.md#jane_telegram_collectorsettingsservicelimitscollector) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Limits of the Telegram Collector; group and field names follow ``limits.schema.json``.
```

### Приклади з тестів

Контекст і передумови: [services/telegram-collector/tests/test_limits_profile.py:98](../../../../../../services/telegram-collector/tests/test_limits_profile.py#L98).

```python
assert set(to_contract(ServiceLimits())) == {
        "rate",
        "timeouts",
        "retries",
        "queue",
        "transfer",
        "telegram",
    }
```

Контекст і передумови: [services/telegram-collector/tests/test_limits_profile.py:106](../../../../../../services/telegram-collector/tests/test_limits_profile.py#L106).

```python
assert to_contract(ServiceLimits())["transfer"]["job_retention_seconds"] == 86_400
```

## jane_telegram_collector.settings.ServiceLimits.rate

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:162](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L162).

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

## jane_telegram_collector.settings.ServiceLimits.timeouts

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:163](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L163).

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

## jane_telegram_collector.settings.ServiceLimits.retries

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:164](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L164).

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

## jane_telegram_collector.settings.ServiceLimits.queue

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:165](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L165).

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

## jane_telegram_collector.settings.ServiceLimits.transfer

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:166](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L166).

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

## jane_telegram_collector.settings.ServiceLimits.telegram

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:167](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L167).

```python
telegram: Telegram = contract_field('telegram', Telegram())
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'telegram'"
}
```

## jane_telegram_collector.settings.ServiceLimits.jobs

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:168](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L168).

```python
jobs: JobLimits = JobLimits()
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.settings.ServiceLimits.idempotency

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:169](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L169).

```python
idempotency: IdempotencyLimits = IdempotencyLimits()
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.settings.ServiceLimits.page

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:170](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L170).

```python
page: PageLimits = PageLimits()
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.settings.ServiceLimits.collector

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:171](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L171).

```python
collector: Collector = Collector()
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.settings.contract_layer

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:183](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L183).

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
A contract-shaped ``Limits`` document (``rules.limits``, request ``limits``) as a jane-kit layer: contract
paths go to the fields that declare them (``transfer.job_retention_seconds`` -> ``jobs.job_retention_seconds``),
contract limits the collector does not have are ignored, anything else is a
:class:`~jane_kit.config.LimitError` - exactly as for the platform profile.
```

## jane_telegram_collector.settings.to_contract

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:191](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L191).

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

Контекст і передумови: [services/telegram-collector/tests/test_limits_profile.py:98](../../../../../../services/telegram-collector/tests/test_limits_profile.py#L98).

```python
assert set(to_contract(ServiceLimits())) == {
        "rate",
        "timeouts",
        "retries",
        "queue",
        "transfer",
        "telegram",
    }
```

Контекст і передумови: [services/telegram-collector/tests/test_limits_profile.py:106](../../../../../../services/telegram-collector/tests/test_limits_profile.py#L106).

```python
assert to_contract(ServiceLimits())["transfer"]["job_retention_seconds"] == 86_400
```

## jane_telegram_collector.settings.platform_layers

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:199](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L199).

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

## jane_telegram_collector.settings.resolve_service_limits

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/settings.py:204](../../../../../../services/telegram-collector/src/jane_telegram_collector/settings.py#L204).

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
Defaults <- platform file (``..._LIMITS_FILE``) <- ``JANE_TELEGRAM_COLLECTOR_LIMITS__*`` <- ``extra``
(source/request layers, contract-shaped). Invalid limits raise :class:`~jane_kit.config.LimitError`.
```

### Приклади з тестів

Контекст і передумови: [services/telegram-collector/tests/test_limits_profile.py:48](../../../../../../services/telegram-collector/tests/test_limits_profile.py#L48).

```python
resolved = resolve_service_limits(make_settings(tmp_path, limits_file=path))
```

Контекст і передумови: [services/telegram-collector/tests/test_limits_profile.py:76](../../../../../../services/telegram-collector/tests/test_limits_profile.py#L76).

```python
resolved = resolve_service_limits(make_settings(tmp_path))
```
