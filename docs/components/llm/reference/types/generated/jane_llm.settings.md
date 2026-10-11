# jane_llm.settings

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_llm.settings.ENV_PREFIX](#jane_llmsettingsenv_prefix)
- [jane_llm.settings.Settings](#jane_llmsettingssettings)
- [jane_llm.settings.Settings.model_config](#jane_llmsettingssettingsmodel_config)
- [jane_llm.settings.Settings.service_name](#jane_llmsettingssettingsservice_name)
- [jane_llm.settings.Settings.port](#jane_llmsettingssettingsport)
- [jane_llm.settings.Settings.store](#jane_llmsettingssettingsstore)
- [jane_llm.settings.Settings.database_url](#jane_llmsettingssettingsdatabase_url)
- [jane_llm.settings.Settings.db_schema](#jane_llmsettingssettingsdb_schema)
- [jane_llm.settings.Settings.seed_file](#jane_llmsettingssettingsseed_file)
- [jane_llm.settings.Settings.fake_provider_enabled](#jane_llmsettingssettingsfake_provider_enabled)
- [jane_llm.settings.Settings.packages_dir](#jane_llmsettingssettingspackages_dir)
- [jane_llm.settings.Settings.registry_url](#jane_llmsettingssettingsregistry_url)
- [jane_llm.settings.Settings.registry_token](#jane_llmsettingssettingsregistry_token)
- [jane_llm.settings.Settings.db_pool_min_size](#jane_llmsettingssettingsdb_pool_min_size)
- [jane_llm.settings.Settings.db_pool_max_size](#jane_llmsettingssettingsdb_pool_max_size)
- [jane_llm.settings.Settings.secret_env_prefix](#jane_llmsettingssettingssecret_env_prefix)
- [jane_llm.settings.Settings.secret_files_dir](#jane_llmsettingssettingssecret_files_dir)
- [jane_llm.settings.Settings.provider_api_base_allowlist](#jane_llmsettingssettingsprovider_api_base_allowlist)
- [jane_llm.settings.Settings.blob_roots](#jane_llmsettingssettingsblob_roots)
- [jane_llm.settings.Settings.download_host_allowlist](#jane_llmsettingssettingsdownload_host_allowlist)
- [jane_llm.settings.Settings.connection_policy](#jane_llmsettingssettingsconnection_policy)
- [jane_llm.settings.Settings.content_reader](#jane_llmsettingssettingscontent_reader)
- [jane_llm.settings.LlmBudget](#jane_llmsettingsllmbudget)
- [jane_llm.settings.LlmBudget.amount](#jane_llmsettingsllmbudgetamount)
- [jane_llm.settings.LlmBudget.currency](#jane_llmsettingsllmbudgetcurrency)
- [jane_llm.settings.LlmBudget.period](#jane_llmsettingsllmbudgetperiod)
- [jane_llm.settings.LlmLimits](#jane_llmsettingsllmlimits)
- [jane_llm.settings.LlmLimits.max_requests_per_minute](#jane_llmsettingsllmlimitsmax_requests_per_minute)
- [jane_llm.settings.LlmLimits.max_input_tokens_per_request](#jane_llmsettingsllmlimitsmax_input_tokens_per_request)
- [jane_llm.settings.LlmLimits.max_output_tokens_per_request](#jane_llmsettingsllmlimitsmax_output_tokens_per_request)
- [jane_llm.settings.LlmLimits.budget](#jane_llmsettingsllmlimitsbudget)
- [jane_llm.settings.GatewayLimits](#jane_llmsettingsgatewaylimits)
- [jane_llm.settings.GatewayLimits.default_max_output_tokens](#jane_llmsettingsgatewaylimitsdefault_max_output_tokens)
- [jane_llm.settings.GatewayLimits.max_schema_retries](#jane_llmsettingsgatewaylimitsmax_schema_retries)
- [jane_llm.settings.GatewayLimits.chars_per_token_estimate](#jane_llmsettingsgatewaylimitschars_per_token_estimate)
- [jane_llm.settings.GatewayLimits.reservation_ttl_seconds](#jane_llmsettingsgatewaylimitsreservation_ttl_seconds)
- [jane_llm.settings.GatewayLimits.max_data_part_bytes](#jane_llmsettingsgatewaylimitsmax_data_part_bytes)
- [jane_llm.settings.GatewayLimits.content_fetch_timeout_ms](#jane_llmsettingsgatewaylimitscontent_fetch_timeout_ms)
- [jane_llm.settings.GatewayLimits.max_package_bytes](#jane_llmsettingsgatewaylimitsmax_package_bytes)
- [jane_llm.settings.GatewayLimits.max_package_files](#jane_llmsettingsgatewaylimitsmax_package_files)
- [jane_llm.settings.RegistryLimits](#jane_llmsettingsregistrylimits)
- [jane_llm.settings.RegistryLimits.connect_timeout_ms](#jane_llmsettingsregistrylimitsconnect_timeout_ms)
- [jane_llm.settings.RegistryLimits.request_timeout_ms](#jane_llmsettingsregistrylimitsrequest_timeout_ms)
- [jane_llm.settings.RegistryLimits.max_attempts](#jane_llmsettingsregistrylimitsmax_attempts)
- [jane_llm.settings.RegistryLimits.client_limits](#jane_llmsettingsregistrylimitsclient_limits)
- [jane_llm.settings.ProviderLimits](#jane_llmsettingsproviderlimits)
- [jane_llm.settings.ProviderLimits.connect_timeout_ms](#jane_llmsettingsproviderlimitsconnect_timeout_ms)
- [jane_llm.settings.ProviderLimits.request_timeout_ms](#jane_llmsettingsproviderlimitsrequest_timeout_ms)
- [jane_llm.settings.ProviderLimits.retries](#jane_llmsettingsproviderlimitsretries)
- [jane_llm.settings.FakeProviderLimits](#jane_llmsettingsfakeproviderlimits)
- [jane_llm.settings.FakeProviderLimits.max_delay_ms](#jane_llmsettingsfakeproviderlimitsmax_delay_ms)
- [jane_llm.settings.ServiceLimits](#jane_llmsettingsservicelimits)
- [jane_llm.settings.ServiceLimits.llm](#jane_llmsettingsservicelimitsllm)
- [jane_llm.settings.ServiceLimits.gateway](#jane_llmsettingsservicelimitsgateway)
- [jane_llm.settings.ServiceLimits.fake](#jane_llmsettingsservicelimitsfake)
- [jane_llm.settings.ServiceLimits.provider](#jane_llmsettingsservicelimitsprovider)
- [jane_llm.settings.ServiceLimits.registry](#jane_llmsettingsservicelimitsregistry)
- [jane_llm.settings.ServiceLimits.jobs](#jane_llmsettingsservicelimitsjobs)
- [jane_llm.settings.ServiceLimits.idempotency](#jane_llmsettingsservicelimitsidempotency)
- [jane_llm.settings.ServiceLimits.state](#jane_llmsettingsservicelimitsstate)
- [jane_llm.settings.resolve_service_limits](#jane_llmsettingsresolve_service_limits)

## jane_llm.settings.ENV_PREFIX

**Константа.** Код: [services/llm/src/jane_llm/settings.py:19](../../../../../../services/llm/src/jane_llm/settings.py#L19).

```python
ENV_PREFIX = 'JANE_LLM_'
```

## jane_llm.settings.Settings

**Клас.** Код: [services/llm/src/jane_llm/settings.py:22](../../../../../../services/llm/src/jane_llm/settings.py#L22).

```python
class Settings(JaneSettings):
```

Базові типи / інтерфейси: `JaneSettings`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_config](jane_llm.settings.md#jane_llmsettingssettingsmodel_config) | Поле | ні |
| [service_name](jane_llm.settings.md#jane_llmsettingssettingsservice_name) | Поле | ні |
| [port](jane_llm.settings.md#jane_llmsettingssettingsport) | Поле | ні |
| [store](jane_llm.settings.md#jane_llmsettingssettingsstore) | Поле | ні |
| [database_url](jane_llm.settings.md#jane_llmsettingssettingsdatabase_url) | Поле | ні |
| [db_schema](jane_llm.settings.md#jane_llmsettingssettingsdb_schema) | Поле | ні |
| [seed_file](jane_llm.settings.md#jane_llmsettingssettingsseed_file) | Поле | ні |
| [fake_provider_enabled](jane_llm.settings.md#jane_llmsettingssettingsfake_provider_enabled) | Поле | ні |
| [packages_dir](jane_llm.settings.md#jane_llmsettingssettingspackages_dir) | Поле | ні |
| [registry_url](jane_llm.settings.md#jane_llmsettingssettingsregistry_url) | Поле | ні |
| [registry_token](jane_llm.settings.md#jane_llmsettingssettingsregistry_token) | Поле | ні |
| [db_pool_min_size](jane_llm.settings.md#jane_llmsettingssettingsdb_pool_min_size) | Поле | ні |
| [db_pool_max_size](jane_llm.settings.md#jane_llmsettingssettingsdb_pool_max_size) | Поле | ні |
| [secret_env_prefix](jane_llm.settings.md#jane_llmsettingssettingssecret_env_prefix) | Поле | ні |
| [secret_files_dir](jane_llm.settings.md#jane_llmsettingssettingssecret_files_dir) | Поле | ні |
| [provider_api_base_allowlist](jane_llm.settings.md#jane_llmsettingssettingsprovider_api_base_allowlist) | Поле | ні |
| [blob_roots](jane_llm.settings.md#jane_llmsettingssettingsblob_roots) | Поле | ні |
| [download_host_allowlist](jane_llm.settings.md#jane_llmsettingssettingsdownload_host_allowlist) | Поле | ні |
| [connection_policy](jane_llm.settings.md#jane_llmsettingssettingsconnection_policy) | Метод | ні |
| [content_reader](jane_llm.settings.md#jane_llmsettingssettingscontent_reader) | Метод | ні |
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

Контекст і передумови: [services/assistant/tests/test_llm_budget.py:87](../../../../../../services/assistant/tests/test_llm_budget.py#L87).

```python
app = build_llm_app(
        LlmSettings(log_format="console", store="memory"),
        store=MemoryStore(),
        adapters={**ADAPTERS, "fake": provider},
    )
```

Контекст і передумови: [services/llm/tests/conftest.py:74](../../../../../../services/llm/tests/conftest.py#L74).

```python
defaults = Settings()
```

## jane_llm.settings.Settings.model_config

**Поле.** Код: [services/llm/src/jane_llm/settings.py:23](../../../../../../services/llm/src/jane_llm/settings.py#L23).

```python
model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra='ignore', env_nested_delimiter='__')
```

Доступ: читання — так; запис — так.

## jane_llm.settings.Settings.service_name

**Поле.** Код: [services/llm/src/jane_llm/settings.py:25](../../../../../../services/llm/src/jane_llm/settings.py#L25).

```python
service_name: str = 'llm'
```

Доступ: читання — так; запис — так.

## jane_llm.settings.Settings.port

**Поле.** Код: [services/llm/src/jane_llm/settings.py:26](../../../../../../services/llm/src/jane_llm/settings.py#L26).

```python
port: int = 8110
```

Доступ: читання — так; запис — так.

## jane_llm.settings.Settings.store

**Поле.** Код: [services/llm/src/jane_llm/settings.py:28](../../../../../../services/llm/src/jane_llm/settings.py#L28).

```python
store: Literal['postgres', 'memory'] = 'postgres'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Where budgets, usage, providers, connections, idempotency keys and jobs live.
    ``postgres`` (default) is shared between instances; ``memory`` is for tests and single-process demos.
```

## jane_llm.settings.Settings.database_url

**Поле.** Код: [services/llm/src/jane_llm/settings.py:31](../../../../../../services/llm/src/jane_llm/settings.py#L31).

```python
database_url: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
PostgreSQL DSN (``postgresql://user:pass@host:5432/db``); required for ``store=postgres``.
    Give the password through the environment (for example ``PGPASSWORD``), not in files.
```

## jane_llm.settings.Settings.db_schema

**Поле.** Код: [services/llm/src/jane_llm/settings.py:34](../../../../../../services/llm/src/jane_llm/settings.py#L34).

```python
db_schema: str = Field(default='llm', pattern='^[a-z_][a-z0-9_]{0,62}$')
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "'llm'",
  "pattern": "'^[a-z_][a-z0-9_]{0,62}$'"
}
```

### Опис із вихідного коду

```text
Own schema of the service in the database (the service never reads other services' tables).
```

## jane_llm.settings.Settings.seed_file

**Поле.** Код: [services/llm/src/jane_llm/settings.py:37](../../../../../../services/llm/src/jane_llm/settings.py#L37).

```python
seed_file: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
YAML/JSON with providers, model aliases, connections and budgets applied at startup
    (only entries that do not exist yet are created). See ``config/seed.example.yaml``.
```

## jane_llm.settings.Settings.fake_provider_enabled

**Поле.** Код: [services/llm/src/jane_llm/settings.py:40](../../../../../../services/llm/src/jane_llm/settings.py#L40).

```python
fake_provider_enabled: bool = True
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Register the deterministic ``fake`` provider and the ``default`` alias pointing to it.
```

## jane_llm.settings.Settings.packages_dir

**Поле.** Код: [services/llm/src/jane_llm/settings.py:42](../../../../../../services/llm/src/jane_llm/settings.py#L42).

```python
packages_dir: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Directory with unpacked LLM packages (``<dir>/<package_id>/jane-package.json``) usable without a
    registry. The built-in ``services/llm/packages`` is used when unset and present.
```

## jane_llm.settings.Settings.registry_url

**Поле.** Код: [services/llm/src/jane_llm/settings.py:45](../../../../../../services/llm/src/jane_llm/settings.py#L45).

```python
registry_url: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Base URL of the handler registry (``registry.v1``) for packages referenced by ``handler``.
```

## jane_llm.settings.Settings.registry_token

**Поле.** Код: [services/llm/src/jane_llm/settings.py:47](../../../../../../services/llm/src/jane_llm/settings.py#L47).

```python
registry_token: SecretStr | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
The gateway's own bearer token for the registry (ADR-0005 §5; give it through the environment,
    never logged).
```

## jane_llm.settings.Settings.db_pool_min_size

**Поле.** Код: [services/llm/src/jane_llm/settings.py:50](../../../../../../services/llm/src/jane_llm/settings.py#L50).

```python
db_pool_min_size: int = Field(default=1, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Minimum PostgreSQL connections per instance.
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/conftest.py:75](../../../../../../services/llm/tests/conftest.py#L75).

```python
store = PostgresStore(
            dsn, schema, min_size=defaults.db_pool_min_size, max_size=defaults.db_pool_max_size
        )
```

## jane_llm.settings.Settings.db_pool_max_size

**Поле.** Код: [services/llm/src/jane_llm/settings.py:52](../../../../../../services/llm/src/jane_llm/settings.py#L52).

```python
db_pool_max_size: int = Field(default=10, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Maximum PostgreSQL connections per instance (size it with ``jobs.max_concurrent_jobs`` and traffic).
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/conftest.py:75](../../../../../../services/llm/tests/conftest.py#L75).

```python
store = PostgresStore(
            dsn, schema, min_size=defaults.db_pool_min_size, max_size=defaults.db_pool_max_size
        )
```

## jane_llm.settings.Settings.secret_env_prefix

**Поле.** Код: [services/llm/src/jane_llm/settings.py:54](../../../../../../services/llm/src/jane_llm/settings.py#L54).

```python
secret_env_prefix: str = 'JANE_SECRET_'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``env:`` secret references may only name variables with this prefix.
```

## jane_llm.settings.Settings.secret_files_dir

**Поле.** Код: [services/llm/src/jane_llm/settings.py:56](../../../../../../services/llm/src/jane_llm/settings.py#L56).

```python
secret_files_dir: Path | None = Path('/run/secrets')
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``file:`` secret references may only point inside this directory (unset: ``file:`` disabled).
```

## jane_llm.settings.Settings.provider_api_base_allowlist

**Поле.** Код: [services/llm/src/jane_llm/settings.py:58](../../../../../../services/llm/src/jane_llm/settings.py#L58).

```python
provider_api_base_allowlist: list[str] = Field(default_factory=lambda: ['https://api.anthropic.com'])
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "lambda: ['https://api.anthropic.com']"
}
```

### Опис із вихідного коду

```text
Origins a connection's ``params.api_base`` may point to (JSON list in the environment).
```

## jane_llm.settings.Settings.blob_roots

**Поле.** Код: [services/llm/src/jane_llm/settings.py:60](../../../../../../services/llm/src/jane_llm/settings.py#L60).

```python
blob_roots: list[Path] = Field(default_factory=list)
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
Directories from which ``file://`` content (materials, entities/data refs, package archives) may be read
    (JSON list). Empty (default): ``file://`` content is refused - a request must not read arbitrary files.
```

## jane_llm.settings.Settings.download_host_allowlist

**Поле.** Код: [services/llm/src/jane_llm/settings.py:63](../../../../../../services/llm/src/jane_llm/settings.py#L63).

```python
download_host_allowlist: list[str] = Field(default_factory=list)
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
``hostname`` (any port) or ``hostname:port`` a ContentRef ``download_url`` may point to (JSON list).
    Empty (default): downloads are refused. Redirects are never followed.
```

## jane_llm.settings.Settings.connection_policy

**Метод.** Код: [services/llm/src/jane_llm/settings.py:73](../../../../../../services/llm/src/jane_llm/settings.py#L73).

```python
def connection_policy(self) -> ConnectionPolicy:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `ConnectionPolicy`.

## jane_llm.settings.Settings.content_reader

**Метод.** Код: [services/llm/src/jane_llm/settings.py:80](../../../../../../services/llm/src/jane_llm/settings.py#L80).

```python
def content_reader(self, limits: GatewayLimits) -> ContentReader:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `limits` | `GatewayLimits` | `—` | positional-or-keyword |

Результат: `ContentReader`.

### Опис із вихідного коду

```text
Reader of request ContentRefs under ``blob_roots`` / ``download_host_allowlist`` and the gateway
limits (``content_fetch_timeout_ms``; sizes are given per read).
```

## jane_llm.settings.LlmBudget

**Клас.** Код: [services/llm/src/jane_llm/settings.py:91](../../../../../../services/llm/src/jane_llm/settings.py#L91).

```python
class LlmBudget(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [amount](jane_llm.settings.md#jane_llmsettingsllmbudgetamount) | Поле | ні |
| [currency](jane_llm.settings.md#jane_llmsettingsllmbudgetcurrency) | Поле | ні |
| [period](jane_llm.settings.md#jane_llmsettingsllmbudgetperiod) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Contract ``limits.llm.budget`` (``Budget``): the platform budget when no stored definition exists.
```

## jane_llm.settings.LlmBudget.amount

**Поле.** Код: [services/llm/src/jane_llm/settings.py:94](../../../../../../services/llm/src/jane_llm/settings.py#L94).

```python
amount: float = Field(default=10.0, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10.0",
  "ge": "0"
}
```

## jane_llm.settings.LlmBudget.currency

**Поле.** Код: [services/llm/src/jane_llm/settings.py:95](../../../../../../services/llm/src/jane_llm/settings.py#L95).

```python
currency: str = Field(default='USD', pattern='^[A-Z]{3}$')
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "'USD'",
  "pattern": "'^[A-Z]{3}$'"
}
```

## jane_llm.settings.LlmBudget.period

**Поле.** Код: [services/llm/src/jane_llm/settings.py:96](../../../../../../services/llm/src/jane_llm/settings.py#L96).

```python
period: Literal['run', 'day', 'week', 'month', 'total'] = 'day'
```

Доступ: читання — так; запис — так.

## jane_llm.settings.LlmLimits

**Клас.** Код: [services/llm/src/jane_llm/settings.py:99](../../../../../../services/llm/src/jane_llm/settings.py#L99).

```python
class LlmLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_requests_per_minute](jane_llm.settings.md#jane_llmsettingsllmlimitsmax_requests_per_minute) | Поле | ні |
| [max_input_tokens_per_request](jane_llm.settings.md#jane_llmsettingsllmlimitsmax_input_tokens_per_request) | Поле | ні |
| [max_output_tokens_per_request](jane_llm.settings.md#jane_llmsettingsllmlimitsmax_output_tokens_per_request) | Поле | ні |
| [budget](jane_llm.settings.md#jane_llmsettingsllmlimitsbudget) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_llm.settings.LlmLimits.max_requests_per_minute

**Поле.** Код: [services/llm/src/jane_llm/settings.py:100](../../../../../../services/llm/src/jane_llm/settings.py#L100).

```python
max_requests_per_minute: int = contract_field('llm.max_requests_per_minute', 60, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'llm.max_requests_per_minute'",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Platform-wide provider calls per minute (all instances together).
```

## jane_llm.settings.LlmLimits.max_input_tokens_per_request

**Поле.** Код: [services/llm/src/jane_llm/settings.py:102](../../../../../../services/llm/src/jane_llm/settings.py#L102).

```python
max_input_tokens_per_request: int = contract_field('llm.max_input_tokens_per_request', 100000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'llm.max_input_tokens_per_request'",
  "ge": "1"
}
```

## jane_llm.settings.LlmLimits.max_output_tokens_per_request

**Поле.** Код: [services/llm/src/jane_llm/settings.py:103](../../../../../../services/llm/src/jane_llm/settings.py#L103).

```python
max_output_tokens_per_request: int = contract_field('llm.max_output_tokens_per_request', 4096, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'llm.max_output_tokens_per_request'",
  "ge": "1"
}
```

## jane_llm.settings.LlmLimits.budget

**Поле.** Код: [services/llm/src/jane_llm/settings.py:104](../../../../../../services/llm/src/jane_llm/settings.py#L104).

```python
budget: LlmBudget = contract_field('llm.budget', LlmBudget())
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'llm.budget'"
}
```

## jane_llm.settings.GatewayLimits

**Клас.** Код: [services/llm/src/jane_llm/settings.py:107](../../../../../../services/llm/src/jane_llm/settings.py#L107).

```python
class GatewayLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [default_max_output_tokens](jane_llm.settings.md#jane_llmsettingsgatewaylimitsdefault_max_output_tokens) | Поле | ні |
| [max_schema_retries](jane_llm.settings.md#jane_llmsettingsgatewaylimitsmax_schema_retries) | Поле | ні |
| [chars_per_token_estimate](jane_llm.settings.md#jane_llmsettingsgatewaylimitschars_per_token_estimate) | Поле | ні |
| [reservation_ttl_seconds](jane_llm.settings.md#jane_llmsettingsgatewaylimitsreservation_ttl_seconds) | Поле | ні |
| [max_data_part_bytes](jane_llm.settings.md#jane_llmsettingsgatewaylimitsmax_data_part_bytes) | Поле | ні |
| [content_fetch_timeout_ms](jane_llm.settings.md#jane_llmsettingsgatewaylimitscontent_fetch_timeout_ms) | Поле | ні |
| [max_package_bytes](jane_llm.settings.md#jane_llmsettingsgatewaylimitsmax_package_bytes) | Поле | ні |
| [max_package_files](jane_llm.settings.md#jane_llmsettingsgatewaylimitsmax_package_files) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Service-specific knobs (not in ``limits.schema.json``).
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_service.py:381](../../../../../../services/llm/tests/test_service.py#L381).

```python
loader = PackageLoader(
        None,
        "http://registry",
        ClientLimits(),
        limits=GatewayLimits(),
        transport=httpx.ASGITransport(app=registry),
    )
```

Контекст і передумови: [services/llm/tests/test_service.py:452](../../../../../../services/llm/tests/test_service.py#L452).

```python
loader = PackageLoader(
        None,
        "http://registry",
        ClientLimits(),
        limits=GatewayLimits(),
        transport=httpx.ASGITransport(app=registry),
    )
```

## jane_llm.settings.GatewayLimits.default_max_output_tokens

**Поле.** Код: [services/llm/src/jane_llm/settings.py:110](../../../../../../services/llm/src/jane_llm/settings.py#L110).

```python
default_max_output_tokens: int = Field(default=1024, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1024",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Used when neither the request nor the package gives ``max_output_tokens``.
```

## jane_llm.settings.GatewayLimits.max_schema_retries

**Поле.** Код: [services/llm/src/jane_llm/settings.py:112](../../../../../../services/llm/src/jane_llm/settings.py#L112).

```python
max_schema_retries: int = Field(default=1, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Default and upper bound of ``max_schema_retries`` (extra calls on output invalid for the schema).
```

## jane_llm.settings.GatewayLimits.chars_per_token_estimate

**Поле.** Код: [services/llm/src/jane_llm/settings.py:114](../../../../../../services/llm/src/jane_llm/settings.py#L114).

```python
chars_per_token_estimate: float = Field(default=2.0, gt=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2.0",
  "gt": "0"
}
```

### Опис із вихідного коду

```text
Conservative input-token estimate (characters per token) used to reserve budget before a call.
```

## jane_llm.settings.GatewayLimits.reservation_ttl_seconds

**Поле.** Код: [services/llm/src/jane_llm/settings.py:116](../../../../../../services/llm/src/jane_llm/settings.py#L116).

```python
reservation_ttl_seconds: int = Field(default=900, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "900",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
A reservation older than this (instance crashed mid-call) is charged at its estimate.
```

## jane_llm.settings.GatewayLimits.max_data_part_bytes

**Поле.** Код: [services/llm/src/jane_llm/settings.py:118](../../../../../../services/llm/src/jane_llm/settings.py#L118).

```python
max_data_part_bytes: int = Field(default=2000000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2000000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Largest single data part (material content) accepted from inline or blob content.
```

## jane_llm.settings.GatewayLimits.content_fetch_timeout_ms

**Поле.** Код: [services/llm/src/jane_llm/settings.py:120](../../../../../../services/llm/src/jane_llm/settings.py#L120).

```python
content_fetch_timeout_ms: int = Field(default=30000, ge=1)
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
Timeout of downloading blob content (``download_url``) of materials and package archives (the whole
    download, connection included).
```

## jane_llm.settings.GatewayLimits.max_package_bytes

**Поле.** Код: [services/llm/src/jane_llm/settings.py:123](../../../../../../services/llm/src/jane_llm/settings.py#L123).

```python
max_package_bytes: int = Field(default=20000000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "20000000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Largest package archive (compressed, and total uncompressed size) from a request or the registry.
```

## jane_llm.settings.GatewayLimits.max_package_files

**Поле.** Код: [services/llm/src/jane_llm/settings.py:125](../../../../../../services/llm/src/jane_llm/settings.py#L125).

```python
max_package_files: int = Field(default=1000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Most files in a package archive.
```

## jane_llm.settings.RegistryLimits

**Клас.** Код: [services/llm/src/jane_llm/settings.py:129](../../../../../../services/llm/src/jane_llm/settings.py#L129).

```python
class RegistryLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [connect_timeout_ms](jane_llm.settings.md#jane_llmsettingsregistrylimitsconnect_timeout_ms) | Поле | ні |
| [request_timeout_ms](jane_llm.settings.md#jane_llmsettingsregistrylimitsrequest_timeout_ms) | Поле | ні |
| [max_attempts](jane_llm.settings.md#jane_llmsettingsregistrylimitsmax_attempts) | Поле | ні |
| [client_limits](jane_llm.settings.md#jane_llmsettingsregistrylimitsclient_limits) | Метод | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Calls to the handler registry (internal; the contract fields are used by ``provider``).
```

## jane_llm.settings.RegistryLimits.connect_timeout_ms

**Поле.** Код: [services/llm/src/jane_llm/settings.py:132](../../../../../../services/llm/src/jane_llm/settings.py#L132).

```python
connect_timeout_ms: int = Field(default=5000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5000",
  "ge": "1"
}
```

## jane_llm.settings.RegistryLimits.request_timeout_ms

**Поле.** Код: [services/llm/src/jane_llm/settings.py:133](../../../../../../services/llm/src/jane_llm/settings.py#L133).

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

## jane_llm.settings.RegistryLimits.max_attempts

**Поле.** Код: [services/llm/src/jane_llm/settings.py:134](../../../../../../services/llm/src/jane_llm/settings.py#L134).

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

## jane_llm.settings.RegistryLimits.client_limits

**Метод.** Код: [services/llm/src/jane_llm/settings.py:136](../../../../../../services/llm/src/jane_llm/settings.py#L136).

```python
def client_limits(self) -> ClientLimits:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `ClientLimits`.

## jane_llm.settings.ProviderLimits

**Клас.** Код: [services/llm/src/jane_llm/settings.py:144](../../../../../../services/llm/src/jane_llm/settings.py#L144).

```python
class ProviderLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [connect_timeout_ms](jane_llm.settings.md#jane_llmsettingsproviderlimitsconnect_timeout_ms) | Поле | ні |
| [request_timeout_ms](jane_llm.settings.md#jane_llmsettingsproviderlimitsrequest_timeout_ms) | Поле | ні |
| [retries](jane_llm.settings.md#jane_llmsettingsproviderlimitsretries) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Calls of LLM providers (``providers/anthropic.py``).

Connection establishment and the retry policy are the platform's general HTTP limits (contract
``timeouts.connect_timeout_ms``, ``retries``: a platform profile sets them). The time of one model call is the
gateway's own limit: a generation of ``max_output_tokens_per_request`` takes minutes, while the contract's
``timeouts.request_timeout_ms`` is sized for web fetches and service calls (30 s in the profiles).
```

## jane_llm.settings.ProviderLimits.connect_timeout_ms

**Поле.** Код: [services/llm/src/jane_llm/settings.py:152](../../../../../../services/llm/src/jane_llm/settings.py#L152).

```python
connect_timeout_ms: int = contract_field('timeouts.connect_timeout_ms', 5000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'timeouts.connect_timeout_ms'",
  "ge": "1"
}
```

## jane_llm.settings.ProviderLimits.request_timeout_ms

**Поле.** Код: [services/llm/src/jane_llm/settings.py:153](../../../../../../services/llm/src/jane_llm/settings.py#L153).

```python
request_timeout_ms: int = Field(default=120000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "120000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
One provider HTTP call (waiting for the whole generation); not the contract's ``timeouts.request_timeout_ms``.
```

## jane_llm.settings.ProviderLimits.retries

**Поле.** Код: [services/llm/src/jane_llm/settings.py:155](../../../../../../services/llm/src/jane_llm/settings.py#L155).

```python
retries: RetryPolicy = contract_field('retries', RetryPolicy(max_attempts=2, initial_backoff_ms=500))
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'retries'"
}
```

## jane_llm.settings.FakeProviderLimits

**Клас.** Код: [services/llm/src/jane_llm/settings.py:158](../../../../../../services/llm/src/jane_llm/settings.py#L158).

```python
class FakeProviderLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_delay_ms](jane_llm.settings.md#jane_llmsettingsfakeproviderlimitsmax_delay_ms) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
The deterministic test provider ``fake`` (internal, not in ``limits.schema.json``).
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_fake_provider.py:98](../../../../../../services/llm/tests/test_fake_provider.py#L98).

```python
ask(fake, params, "x", ServiceLimits(fake=FakeProviderLimits(max_delay_ms=250)))
```

Контекст і передумови: [services/llm/tests/test_fake_provider.py:100](../../../../../../services/llm/tests/test_fake_provider.py#L100).

```python
ask(fake, params, "x", ServiceLimits(fake=FakeProviderLimits(max_delay_ms=0)))
```

## jane_llm.settings.FakeProviderLimits.max_delay_ms

**Поле.** Код: [services/llm/src/jane_llm/settings.py:161](../../../../../../services/llm/src/jane_llm/settings.py#L161).

```python
max_delay_ms: int = Field(default=30000, ge=0)
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
Upper bound of the delay a ``fake`` connection asks for (``params.delay_ms``,
    ``params.responses[].delay_ms``); a longer delay is shortened to it, ``0`` turns delays off.
```

## jane_llm.settings.ServiceLimits

**Клас.** Код: [services/llm/src/jane_llm/settings.py:166](../../../../../../services/llm/src/jane_llm/settings.py#L166).

```python
class ServiceLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [llm](jane_llm.settings.md#jane_llmsettingsservicelimitsllm) | Поле | ні |
| [gateway](jane_llm.settings.md#jane_llmsettingsservicelimitsgateway) | Поле | ні |
| [fake](jane_llm.settings.md#jane_llmsettingsservicelimitsfake) | Поле | ні |
| [provider](jane_llm.settings.md#jane_llmsettingsservicelimitsprovider) | Поле | ні |
| [registry](jane_llm.settings.md#jane_llmsettingsservicelimitsregistry) | Поле | ні |
| [jobs](jane_llm.settings.md#jane_llmsettingsservicelimitsjobs) | Поле | ні |
| [idempotency](jane_llm.settings.md#jane_llmsettingsservicelimitsidempotency) | Поле | ні |
| [state](jane_llm.settings.md#jane_llmsettingsservicelimitsstate) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_fake_provider.py:98](../../../../../../services/llm/tests/test_fake_provider.py#L98).

```python
ask(fake, params, "x", ServiceLimits(fake=FakeProviderLimits(max_delay_ms=250)))
```

Контекст і передумови: [services/llm/tests/test_fake_provider.py:100](../../../../../../services/llm/tests/test_fake_provider.py#L100).

```python
ask(fake, params, "x", ServiceLimits(fake=FakeProviderLimits(max_delay_ms=0)))
```

## jane_llm.settings.ServiceLimits.llm

**Поле.** Код: [services/llm/src/jane_llm/settings.py:167](../../../../../../services/llm/src/jane_llm/settings.py#L167).

```python
llm: LlmLimits = LlmLimits()
```

Доступ: читання — так; запис — так.

## jane_llm.settings.ServiceLimits.gateway

**Поле.** Код: [services/llm/src/jane_llm/settings.py:168](../../../../../../services/llm/src/jane_llm/settings.py#L168).

```python
gateway: GatewayLimits = GatewayLimits()
```

Доступ: читання — так; запис — так.

## jane_llm.settings.ServiceLimits.fake

**Поле.** Код: [services/llm/src/jane_llm/settings.py:169](../../../../../../services/llm/src/jane_llm/settings.py#L169).

```python
fake: FakeProviderLimits = FakeProviderLimits()
```

Доступ: читання — так; запис — так.

## jane_llm.settings.ServiceLimits.provider

**Поле.** Код: [services/llm/src/jane_llm/settings.py:170](../../../../../../services/llm/src/jane_llm/settings.py#L170).

```python
provider: ProviderLimits = ProviderLimits()
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Calls to LLM providers: own ``request_timeout_ms``; contract ``timeouts.connect_timeout_ms`` and ``retries``.
```

## jane_llm.settings.ServiceLimits.registry

**Поле.** Код: [services/llm/src/jane_llm/settings.py:172](../../../../../../services/llm/src/jane_llm/settings.py#L172).

```python
registry: RegistryLimits = RegistryLimits()
```

Доступ: читання — так; запис — так.

## jane_llm.settings.ServiceLimits.jobs

**Поле.** Код: [services/llm/src/jane_llm/settings.py:173](../../../../../../services/llm/src/jane_llm/settings.py#L173).

```python
jobs: JobLimits = JobLimits()
```

Доступ: читання — так; запис — так.

## jane_llm.settings.ServiceLimits.idempotency

**Поле.** Код: [services/llm/src/jane_llm/settings.py:174](../../../../../../services/llm/src/jane_llm/settings.py#L174).

```python
idempotency: IdempotencyLimits = IdempotencyLimits()
```

Доступ: читання — так; запис — так.

## jane_llm.settings.ServiceLimits.state

**Поле.** Код: [services/llm/src/jane_llm/settings.py:175](../../../../../../services/llm/src/jane_llm/settings.py#L175).

```python
state: LeaseLimits = LeaseLimits()
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Leases of the shared PostgreSQL state (R17): ``Idempotency-Key`` claims, jobs, heartbeat interval.
```

## jane_llm.settings.resolve_service_limits

**Функція.** Код: [services/llm/src/jane_llm/settings.py:179](../../../../../../services/llm/src/jane_llm/settings.py#L179).

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
Defaults <- platform file (``JANE_LLM_LIMITS_FILE``) <- ``JANE_LLM_LIMITS__*`` <- ``extra``
(request layer in autonomous mode).

The platform file may be a whole platform profile (``deploy/profiles/<profile>.json``): contract limits
this service does not have are ignored (``ResolvedLimits.ignored``, start-up log); typos fail. Its
``timeouts.connect_timeout_ms`` and ``retries`` reach ``provider``; ``timeouts.request_timeout_ms`` does not
(the model call timeout is ``provider.request_timeout_ms``, ``JANE_LLM_LIMITS__PROVIDER__REQUEST_TIMEOUT_MS``).
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_fake_provider.py:104](../../../../../../services/llm/tests/test_fake_provider.py#L104).

```python
configured = resolve_service_limits(Settings(log_format="console", store="memory")).limits
```

Контекст і передумови: [services/llm/tests/test_limits_profile.py:48](../../../../../../services/llm/tests/test_limits_profile.py#L48).

```python
resolved = resolve_service_limits(settings)
```
