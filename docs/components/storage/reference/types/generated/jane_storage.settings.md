# jane_storage.settings

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage.settings.ENV_PREFIX](#jane_storagesettingsenv_prefix)
- [jane_storage.settings.LEGACY_RETRIES](#jane_storagesettingslegacy_retries)
- [jane_storage.settings.log](#jane_storagesettingslog)
- [jane_storage.settings.Settings](#jane_storagesettingssettings)
- [jane_storage.settings.Settings.model_config](#jane_storagesettingssettingsmodel_config)
- [jane_storage.settings.Settings.service_name](#jane_storagesettingssettingsservice_name)
- [jane_storage.settings.Settings.port](#jane_storagesettingssettingsport)
- [jane_storage.settings.Settings.connections_file](#jane_storagesettingssettingsconnections_file)
- [jane_storage.settings.Settings.transit_connection_id](#jane_storagesettingssettingstransit_connection_id)
- [jane_storage.settings.Settings.package_dirs](#jane_storagesettingssettingspackage_dirs)
- [jane_storage.settings.Settings.validate_requests](#jane_storagesettingssettingsvalidate_requests)
- [jane_storage.settings.Settings.secret_env_prefix](#jane_storagesettingssettingssecret_env_prefix)
- [jane_storage.settings.Settings.secret_files_dir](#jane_storagesettingssettingssecret_files_dir)
- [jane_storage.settings.Settings.connection_host_allowlist](#jane_storagesettingssettingsconnection_host_allowlist)
- [jane_storage.settings.Settings.content_files_dir](#jane_storagesettingssettingscontent_files_dir)
- [jane_storage.settings.Settings.transit_dir](#jane_storagesettingssettingstransit_dir)
- [jane_storage.settings.Settings.download_host_allowlist](#jane_storagesettingssettingsdownload_host_allowlist)
- [jane_storage.settings.Settings.registry_url](#jane_storagesettingssettingsregistry_url)
- [jane_storage.settings.Settings.registry_token](#jane_storagesettingssettingsregistry_token)
- [jane_storage.settings.Settings.connection_policy](#jane_storagesettingssettingsconnection_policy)
- [jane_storage.settings.Timeouts](#jane_storagesettingstimeouts)
- [jane_storage.settings.Timeouts.sync_response_max_ms](#jane_storagesettingstimeoutssync_response_max_ms)
- [jane_storage.settings.Timeouts.request_timeout_ms](#jane_storagesettingstimeoutsrequest_timeout_ms)
- [jane_storage.settings.Transfer](#jane_storagesettingstransfer)
- [jane_storage.settings.Transfer.max_request_body_bytes](#jane_storagesettingstransfermax_request_body_bytes)
- [jane_storage.settings.Transfer.inline_max_bytes](#jane_storagesettingstransferinline_max_bytes)
- [jane_storage.settings.Transfer.transit_ttl_seconds](#jane_storagesettingstransfertransit_ttl_seconds)
- [jane_storage.settings.Transfer.transit_cleanup_interval_seconds](#jane_storagesettingstransfertransit_cleanup_interval_seconds)
- [jane_storage.settings.Objects](#jane_storagesettingsobjects)
- [jane_storage.settings.Objects.max_object_bytes](#jane_storagesettingsobjectsmax_object_bytes)
- [jane_storage.settings.Objects.max_filter_material_ids](#jane_storagesettingsobjectsmax_filter_material_ids)
- [jane_storage.settings.Adapters](#jane_storagesettingsadapters)
- [jane_storage.settings.Adapters.lock_timeout_ms](#jane_storagesettingsadapterslock_timeout_ms)
- [jane_storage.settings.Adapters.lock_stale_ms](#jane_storagesettingsadapterslock_stale_ms)
- [jane_storage.settings.Adapters.lock_poll_ms](#jane_storagesettingsadapterslock_poll_ms)
- [jane_storage.settings.Adapters.replace_retry_ms](#jane_storagesettingsadaptersreplace_retry_ms)
- [jane_storage.settings.Adapters.pool_min_size](#jane_storagesettingsadapterspool_min_size)
- [jane_storage.settings.Adapters.pool_max_size](#jane_storagesettingsadapterspool_max_size)
- [jane_storage.settings.Adapters.connect_timeout_ms](#jane_storagesettingsadaptersconnect_timeout_ms)
- [jane_storage.settings.Adapters.command_timeout_ms](#jane_storagesettingsadapterscommand_timeout_ms)
- [jane_storage.settings.Adapters.chunk_bytes](#jane_storagesettingsadapterschunk_bytes)
- [jane_storage.settings.Adapters.retry_max_attempts](#jane_storagesettingsadaptersretry_max_attempts)
- [jane_storage.settings.CONNECTION_FIRST_OPTIONS](#jane_storagesettingsconnection_first_options)
- [jane_storage.settings.ConflictRetries](#jane_storagesettingsconflictretries)
- [jane_storage.settings.Invocations](#jane_storagesettingsinvocations)
- [jane_storage.settings.Invocations.max_results_in_memory](#jane_storagesettingsinvocationsmax_results_in_memory)
- [jane_storage.settings.PackageLimits](#jane_storagesettingspackagelimits)
- [jane_storage.settings.PackageLimits.max_archive_bytes](#jane_storagesettingspackagelimitsmax_archive_bytes)
- [jane_storage.settings.PackageLimits.max_unpacked_bytes](#jane_storagesettingspackagelimitsmax_unpacked_bytes)
- [jane_storage.settings.PackageLimits.max_files](#jane_storagesettingspackagelimitsmax_files)
- [jane_storage.settings.PackageLimits.cache_max_entries](#jane_storagesettingspackagelimitscache_max_entries)
- [jane_storage.settings.PackageLimits.registry_connect_timeout_ms](#jane_storagesettingspackagelimitsregistry_connect_timeout_ms)
- [jane_storage.settings.PackageLimits.registry_request_timeout_ms](#jane_storagesettingspackagelimitsregistry_request_timeout_ms)
- [jane_storage.settings.PackageLimits.archive_limits](#jane_storagesettingspackagelimitsarchive_limits)
- [jane_storage.settings.ServiceLimits](#jane_storagesettingsservicelimits)
- [jane_storage.settings.ServiceLimits.jobs](#jane_storagesettingsservicelimitsjobs)
- [jane_storage.settings.ServiceLimits.idempotency](#jane_storagesettingsservicelimitsidempotency)
- [jane_storage.settings.ServiceLimits.conflict_retries](#jane_storagesettingsservicelimitsconflict_retries)
- [jane_storage.settings.ServiceLimits.timeouts](#jane_storagesettingsservicelimitstimeouts)
- [jane_storage.settings.ServiceLimits.transfer](#jane_storagesettingsservicelimitstransfer)
- [jane_storage.settings.ServiceLimits.objects](#jane_storagesettingsservicelimitsobjects)
- [jane_storage.settings.ServiceLimits.adapters](#jane_storagesettingsservicelimitsadapters)
- [jane_storage.settings.ServiceLimits.pages](#jane_storagesettingsservicelimitspages)
- [jane_storage.settings.ServiceLimits.invocations](#jane_storagesettingsservicelimitsinvocations)
- [jane_storage.settings.ServiceLimits.packages](#jane_storagesettingsservicelimitspackages)
- [jane_storage.settings.resolve_service_limits](#jane_storagesettingsresolve_service_limits)

## jane_storage.settings.ENV_PREFIX

**Константа.** Код: [services/storage/src/jane_storage/settings.py:23](../../../../../../services/storage/src/jane_storage/settings.py#L23).

```python
ENV_PREFIX = 'JANE_STORAGE_'
```

## jane_storage.settings.LEGACY_RETRIES

**Константа.** Код: [services/storage/src/jane_storage/settings.py:24](../../../../../../services/storage/src/jane_storage/settings.py#L24).

```python
LEGACY_RETRIES = 'retries'
```

### Опис із вихідного коду

```text
Before WP-17 the core's CONFLICT retries were ``limits.retries``; in the service's own (non-shared) layers the
old group is a deprecated alias of ``conflict_retries`` (``JANE_STORAGE_LIMITS__RETRIES__*``).
```

## jane_storage.settings.log

**Змінна.** Код: [services/storage/src/jane_storage/settings.py:28](../../../../../../services/storage/src/jane_storage/settings.py#L28).

```python
log = logging.getLogger(__name__)
```

## jane_storage.settings.Settings

**Клас.** Код: [services/storage/src/jane_storage/settings.py:32](../../../../../../services/storage/src/jane_storage/settings.py#L32).

```python
class Settings(JaneSettings):
```

Базові типи / інтерфейси: `JaneSettings`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_config](jane_storage.settings.md#jane_storagesettingssettingsmodel_config) | Поле | ні |
| [service_name](jane_storage.settings.md#jane_storagesettingssettingsservice_name) | Поле | ні |
| [port](jane_storage.settings.md#jane_storagesettingssettingsport) | Поле | ні |
| [connections_file](jane_storage.settings.md#jane_storagesettingssettingsconnections_file) | Поле | ні |
| [transit_connection_id](jane_storage.settings.md#jane_storagesettingssettingstransit_connection_id) | Поле | ні |
| [package_dirs](jane_storage.settings.md#jane_storagesettingssettingspackage_dirs) | Поле | ні |
| [validate_requests](jane_storage.settings.md#jane_storagesettingssettingsvalidate_requests) | Поле | ні |
| [secret_env_prefix](jane_storage.settings.md#jane_storagesettingssettingssecret_env_prefix) | Поле | ні |
| [secret_files_dir](jane_storage.settings.md#jane_storagesettingssettingssecret_files_dir) | Поле | ні |
| [connection_host_allowlist](jane_storage.settings.md#jane_storagesettingssettingsconnection_host_allowlist) | Поле | ні |
| [content_files_dir](jane_storage.settings.md#jane_storagesettingssettingscontent_files_dir) | Поле | ні |
| [transit_dir](jane_storage.settings.md#jane_storagesettingssettingstransit_dir) | Поле | ні |
| [download_host_allowlist](jane_storage.settings.md#jane_storagesettingssettingsdownload_host_allowlist) | Поле | ні |
| [registry_url](jane_storage.settings.md#jane_storagesettingssettingsregistry_url) | Поле | ні |
| [registry_token](jane_storage.settings.md#jane_storagesettingssettingsregistry_token) | Поле | ні |
| [connection_policy](jane_storage.settings.md#jane_storagesettingssettingsconnection_policy) | Метод | ні |
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

Контекст і передумови: [services/storage/tests/conftest.py:120](../../../../../../services/storage/tests/conftest.py#L120).

```python
return Settings(log_format="console", connections_file=conn_file)
```

Контекст і передумови: [services/storage/tests/test_adapter_swap.py:187](../../../../../../services/storage/tests/test_adapter_swap.py#L187).

```python
settings = Settings(
        log_format="console",
        connections_file=conns,
        connection_host_allowlist=[f"{pg['host']}:{pg['port']}"],
    )
```

## jane_storage.settings.Settings.model_config

**Поле.** Код: [services/storage/src/jane_storage/settings.py:33](../../../../../../services/storage/src/jane_storage/settings.py#L33).

```python
model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra='ignore', env_nested_delimiter='__')
```

Доступ: читання — так; запис — так.

## jane_storage.settings.Settings.service_name

**Поле.** Код: [services/storage/src/jane_storage/settings.py:35](../../../../../../services/storage/src/jane_storage/settings.py#L35).

```python
service_name: str = 'storage'
```

Доступ: читання — так; запис — так.

## jane_storage.settings.Settings.port

**Поле.** Код: [services/storage/src/jane_storage/settings.py:36](../../../../../../services/storage/src/jane_storage/settings.py#L36).

```python
port: int = 8107
```

Доступ: читання — так; запис — так.

## jane_storage.settings.Settings.connections_file

**Поле.** Код: [services/storage/src/jane_storage/settings.py:37](../../../../../../services/storage/src/jane_storage/settings.py#L37).

```python
connections_file: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
JSON/YAML with ``{"connections": [Connection, ...]}`` (secret values only as ``secret_refs``).
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_registry_packages.py:358](../../../../../../services/storage/tests/test_registry_packages.py#L358).

```python
authorized = Settings(
        log_format="console",
        connections_file=settings.connections_file,
        registry_url=REGISTRY_URL + "/",
        registry_token=TOKEN,
    )
```

## jane_storage.settings.Settings.transit_connection_id

**Поле.** Код: [services/storage/src/jane_storage/settings.py:39](../../../../../../services/storage/src/jane_storage/settings.py#L39).

```python
transit_connection_id: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Connection (kind ``s3``/``minio``) used to read ``s3://`` blobs of materials (ADR-0004).
```

## jane_storage.settings.Settings.package_dirs

**Поле.** Код: [services/storage/src/jane_storage/settings.py:41](../../../../../../services/storage/src/jane_storage/settings.py#L41).

```python
package_dirs: list[Path] = Field(default_factory=list)
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
Extra storage package directories besides the installed adapter distributions.
```

## jane_storage.settings.Settings.validate_requests

**Поле.** Код: [services/storage/src/jane_storage/settings.py:43](../../../../../../services/storage/src/jane_storage/settings.py#L43).

```python
validate_requests: bool = True
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Validate invocations against ``contracts/schemas`` when the contracts directory is available.
```

## jane_storage.settings.Settings.secret_env_prefix

**Поле.** Код: [services/storage/src/jane_storage/settings.py:45](../../../../../../services/storage/src/jane_storage/settings.py#L45).

```python
secret_env_prefix: str = 'JANE_SECRET_'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``env:`` secret references may name only variables with this prefix (empty: ``env:`` disabled).
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_secret_policy.py:446](../../../../../../services/storage/tests/test_secret_policy.py#L446).

```python
assert defaults.secret_env_prefix == "JANE_SECRET_"
```

## jane_storage.settings.Settings.secret_files_dir

**Поле.** Код: [services/storage/src/jane_storage/settings.py:47](../../../../../../services/storage/src/jane_storage/settings.py#L47).

```python
secret_files_dir: Path | None = Path('/run/secrets')
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``file:`` secret references must point inside this directory (empty: ``file:`` disabled).
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_secret_policy.py:447](../../../../../../services/storage/tests/test_secret_policy.py#L447).

```python
assert defaults.secret_files_dir == Path("/run/secrets")
```

## jane_storage.settings.Settings.connection_host_allowlist

**Поле.** Код: [services/storage/src/jane_storage/settings.py:49](../../../../../../services/storage/src/jane_storage/settings.py#L49).

```python
connection_host_allowlist: list[str] = Field(default_factory=list)
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
``hostname`` / ``hostname:port`` a connection may contact (JSON list); default none: connections with
    a network address are rejected.
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_secret_policy.py:448](../../../../../../services/storage/tests/test_secret_policy.py#L448).

```python
assert defaults.connection_host_allowlist == []
```

## jane_storage.settings.Settings.content_files_dir

**Поле.** Код: [services/storage/src/jane_storage/settings.py:52](../../../../../../services/storage/src/jane_storage/settings.py#L52).

```python
content_files_dir: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Only ``file:///`` ContentRef blobs below this directory may be read; None disables local blobs.
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_content_policy.py:124](../../../../../../services/storage/tests/test_content_policy.py#L124).

```python
assert settings.content_files_dir == tmp_path
```

## jane_storage.settings.Settings.transit_dir

**Поле.** Код: [services/storage/src/jane_storage/settings.py:54](../../../../../../services/storage/src/jane_storage/settings.py#L54).

```python
transit_dir: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Transit blob store of this service (ADR-0004, R18): a RAW larger than ``transfer.inline_max_bytes`` whose
    adapter has no persistent URI is returned by ``GET /v1/objects/{id}`` as a transit ``file://`` blob written under
    ``<transit_dir>/storage/`` (kept ``transfer.transit_ttl_seconds``, removed by this service). The consumers read it
    within their ``BLOB_ROOTS``; this service also reads its own transit blobs. None: such a RAW has no ``material``.
```

## jane_storage.settings.Settings.download_host_allowlist

**Поле.** Код: [services/storage/src/jane_storage/settings.py:59](../../../../../../services/storage/src/jane_storage/settings.py#L59).

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
``hostname`` or ``hostname:port`` allowed for ContentRef download_url; empty disables downloads.
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_content_policy.py:125](../../../../../../services/storage/tests/test_content_policy.py#L125).

```python
assert settings.download_host_allowlist == ["cdn.internal:443"]
```

## jane_storage.settings.Settings.registry_url

**Поле.** Код: [services/storage/src/jane_storage/settings.py:61](../../../../../../services/storage/src/jane_storage/settings.py#L61).

```python
registry_url: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Base URL of the handler registry (``registry.v1``, e.g. ``http://registry:8000``): a storage package that is
    neither built in nor given as ``package_archive`` is downloaded from it (ADR-0009 §4). Operator configuration
    only (never taken from a request); empty: no registry, such a package is ``404 not_found``.
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_registry_packages.py:485](../../../../../../services/storage/tests/test_registry_packages.py#L485).

```python
assert s.registry_url == "https://registry.example.test:8443/jane"
```

## jane_storage.settings.Settings.registry_token

**Поле.** Код: [services/storage/src/jane_storage/settings.py:65](../../../../../../services/storage/src/jane_storage/settings.py#L65).

```python
registry_token: SecretStr | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Bearer token for the registry (environment only; never logged, sent only to ``registry_url``). Not an
    ``env:JANE_SECRET_*`` variable, so a connection's ``secret_refs`` cannot reference it.
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_registry_packages.py:486](../../../../../../services/storage/tests/test_registry_packages.py#L486).

```python
assert s.registry_token is not None and TOKEN not in repr(s)
```

## jane_storage.settings.Settings.connection_policy

**Метод.** Код: [services/storage/src/jane_storage/settings.py:91](../../../../../../services/storage/src/jane_storage/settings.py#L91).

```python
def connection_policy(self) -> ConnectionPolicy:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `ConnectionPolicy`.

## jane_storage.settings.Timeouts

**Клас.** Код: [services/storage/src/jane_storage/settings.py:99](../../../../../../services/storage/src/jane_storage/settings.py#L99).

```python
class Timeouts(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [sync_response_max_ms](jane_storage.settings.md#jane_storagesettingstimeoutssync_response_max_ms) | Поле | ні |
| [request_timeout_ms](jane_storage.settings.md#jane_storagesettingstimeoutsrequest_timeout_ms) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_storage.settings.Timeouts.sync_response_max_ms

**Поле.** Код: [services/storage/src/jane_storage/settings.py:100](../../../../../../services/storage/src/jane_storage/settings.py#L100).

```python
sync_response_max_ms: int = contract_field('timeouts.sync_response_max_ms', 30000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'timeouts.sync_response_max_ms'",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Contract ``limits.timeouts.sync_response_max_ms``: a sync invocation not done by then → 202 + Job.
```

## jane_storage.settings.Timeouts.request_timeout_ms

**Поле.** Код: [services/storage/src/jane_storage/settings.py:102](../../../../../../services/storage/src/jane_storage/settings.py#L102).

```python
request_timeout_ms: int = contract_field('timeouts.request_timeout_ms', 30000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'timeouts.request_timeout_ms'",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Reading blob content (``download_url``, ``s3://``).
```

## jane_storage.settings.Transfer

**Клас.** Код: [services/storage/src/jane_storage/settings.py:106](../../../../../../services/storage/src/jane_storage/settings.py#L106).

```python
class Transfer(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_request_body_bytes](jane_storage.settings.md#jane_storagesettingstransfermax_request_body_bytes) | Поле | ні |
| [inline_max_bytes](jane_storage.settings.md#jane_storagesettingstransferinline_max_bytes) | Поле | ні |
| [transit_ttl_seconds](jane_storage.settings.md#jane_storagesettingstransfertransit_ttl_seconds) | Поле | ні |
| [transit_cleanup_interval_seconds](jane_storage.settings.md#jane_storagesettingstransfertransit_cleanup_interval_seconds) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_storage.settings.Transfer.max_request_body_bytes

**Поле.** Код: [services/storage/src/jane_storage/settings.py:107](../../../../../../services/storage/src/jane_storage/settings.py#L107).

```python
max_request_body_bytes: int = contract_field('transfer.max_request_body_bytes', 16 * 1024 * 1024, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'transfer.max_request_body_bytes'",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Contract ``limits.transfer.max_request_body_bytes``: larger bodies → 413 (send blobs instead).
```

## jane_storage.settings.Transfer.inline_max_bytes

**Поле.** Код: [services/storage/src/jane_storage/settings.py:109](../../../../../../services/storage/src/jane_storage/settings.py#L109).

```python
inline_max_bytes: int = contract_field('transfer.inline_max_bytes', 1024 * 1024, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'transfer.inline_max_bytes'",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Contract ``limits.transfer.inline_max_bytes``: stored content up to this size is returned inline
    in ``GET /v1/objects/{id}`` when the adapter has no persistent URI for it.
```

## jane_storage.settings.Transfer.transit_ttl_seconds

**Поле.** Код: [services/storage/src/jane_storage/settings.py:112](../../../../../../services/storage/src/jane_storage/settings.py#L112).

```python
transit_ttl_seconds: int = contract_field('transfer.transit_ttl_seconds', 604800, ge=60)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'transfer.transit_ttl_seconds'",
  "ge": "60"
}
```

### Опис із вихідного коду

```text
Contract ``limits.transfer.transit_ttl_seconds``: how long a transit blob of this service is kept.
```

## jane_storage.settings.Transfer.transit_cleanup_interval_seconds

**Поле.** Код: [services/storage/src/jane_storage/settings.py:114](../../../../../../services/storage/src/jane_storage/settings.py#L114).

```python
transit_cleanup_interval_seconds: int = Field(default=600, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "600",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
How often this service removes its expired transit blobs (``transit_dir``).
```

## jane_storage.settings.Objects

**Клас.** Код: [services/storage/src/jane_storage/settings.py:118](../../../../../../services/storage/src/jane_storage/settings.py#L118).

```python
class Objects(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_object_bytes](jane_storage.settings.md#jane_storagesettingsobjectsmax_object_bytes) | Поле | ні |
| [max_filter_material_ids](jane_storage.settings.md#jane_storagesettingsobjectsmax_filter_material_ids) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_storage.settings.Objects.max_object_bytes

**Поле.** Код: [services/storage/src/jane_storage/settings.py:119](../../../../../../services/storage/src/jane_storage/settings.py#L119).

```python
max_object_bytes: int = Field(default=100 * 1024 * 1024, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "100 * 1024 * 1024",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Largest RAW / result document the service stores (content read into memory).
```

## jane_storage.settings.Objects.max_filter_material_ids

**Поле.** Код: [services/storage/src/jane_storage/settings.py:121](../../../../../../services/storage/src/jane_storage/settings.py#L121).

```python
max_filter_material_ids: int = Field(default=200, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "200",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Most ``material_id`` values one ``GET /v1/objects`` may filter by (``material_id`` + ``material_ids``).
```

## jane_storage.settings.Adapters

**Клас.** Код: [services/storage/src/jane_storage/settings.py:125](../../../../../../services/storage/src/jane_storage/settings.py#L125).

```python
class Adapters(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [lock_timeout_ms](jane_storage.settings.md#jane_storagesettingsadapterslock_timeout_ms) | Поле | ні |
| [lock_stale_ms](jane_storage.settings.md#jane_storagesettingsadapterslock_stale_ms) | Поле | ні |
| [lock_poll_ms](jane_storage.settings.md#jane_storagesettingsadapterslock_poll_ms) | Поле | ні |
| [replace_retry_ms](jane_storage.settings.md#jane_storagesettingsadaptersreplace_retry_ms) | Поле | ні |
| [pool_min_size](jane_storage.settings.md#jane_storagesettingsadapterspool_min_size) | Поле | ні |
| [pool_max_size](jane_storage.settings.md#jane_storagesettingsadapterspool_max_size) | Поле | ні |
| [connect_timeout_ms](jane_storage.settings.md#jane_storagesettingsadaptersconnect_timeout_ms) | Поле | ні |
| [command_timeout_ms](jane_storage.settings.md#jane_storagesettingsadapterscommand_timeout_ms) | Поле | ні |
| [chunk_bytes](jane_storage.settings.md#jane_storagesettingsadapterschunk_bytes) | Поле | ні |
| [retry_max_attempts](jane_storage.settings.md#jane_storagesettingsadaptersretry_max_attempts) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Options passed to every adapter's ``open`` (each adapter uses the ones it knows).
```

## jane_storage.settings.Adapters.lock_timeout_ms

**Поле.** Код: [services/storage/src/jane_storage/settings.py:128](../../../../../../services/storage/src/jane_storage/settings.py#L128).

```python
lock_timeout_ms: int = Field(default=30000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "30000",
  "ge": "1"
}
```

## jane_storage.settings.Adapters.lock_stale_ms

**Поле.** Код: [services/storage/src/jane_storage/settings.py:129](../../../../../../services/storage/src/jane_storage/settings.py#L129).

```python
lock_stale_ms: int = Field(default=120000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "120000",
  "ge": "1"
}
```

## jane_storage.settings.Adapters.lock_poll_ms

**Поле.** Код: [services/storage/src/jane_storage/settings.py:130](../../../../../../services/storage/src/jane_storage/settings.py#L130).

```python
lock_poll_ms: int = Field(default=10, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10",
  "ge": "1"
}
```

## jane_storage.settings.Adapters.replace_retry_ms

**Поле.** Код: [services/storage/src/jane_storage/settings.py:131](../../../../../../services/storage/src/jane_storage/settings.py#L131).

```python
replace_retry_ms: int = Field(default=5000, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5000",
  "ge": "0"
}
```

## jane_storage.settings.Adapters.pool_min_size

**Поле.** Код: [services/storage/src/jane_storage/settings.py:132](../../../../../../services/storage/src/jane_storage/settings.py#L132).

```python
pool_min_size: int = Field(default=1, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1",
  "ge": "0"
}
```

## jane_storage.settings.Adapters.pool_max_size

**Поле.** Код: [services/storage/src/jane_storage/settings.py:133](../../../../../../services/storage/src/jane_storage/settings.py#L133).

```python
pool_max_size: int = Field(default=10, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "10",
  "ge": "1"
}
```

## jane_storage.settings.Adapters.connect_timeout_ms

**Поле.** Код: [services/storage/src/jane_storage/settings.py:134](../../../../../../services/storage/src/jane_storage/settings.py#L134).

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

## jane_storage.settings.Adapters.command_timeout_ms

**Поле.** Код: [services/storage/src/jane_storage/settings.py:135](../../../../../../services/storage/src/jane_storage/settings.py#L135).

```python
command_timeout_ms: int = Field(default=30000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "30000",
  "ge": "1"
}
```

## jane_storage.settings.Adapters.chunk_bytes

**Поле.** Код: [services/storage/src/jane_storage/settings.py:136](../../../../../../services/storage/src/jane_storage/settings.py#L136).

```python
chunk_bytes: int | None = Field(default=None, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
MongoDB: size of one RAW chunk document for every connection that does not set ``params.chunk_bytes``
    (unset: the adapter's own default, 4 MiB; the adapter rejects values above 15 MiB).
```

## jane_storage.settings.Adapters.retry_max_attempts

**Поле.** Код: [services/storage/src/jane_storage/settings.py:139](../../../../../../services/storage/src/jane_storage/settings.py#L139).

```python
retry_max_attempts: int | None = Field(default=None, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
MinIO/S3: botocore attempts per request for every connection that does not set
    ``params.retry_max_attempts`` (unset: the adapter's own default, 3).
```

## jane_storage.settings.CONNECTION_FIRST_OPTIONS

**Константа.** Код: [services/storage/src/jane_storage/settings.py:144](../../../../../../services/storage/src/jane_storage/settings.py#L144).

```python
CONNECTION_FIRST_OPTIONS = frozenset({'chunk_bytes', 'retry_max_attempts'})
```

### Опис із вихідного коду

```text
Service-wide adapter defaults that a connection's own ``params`` override (the other ``adapters.*`` options
are applied over the connection params).
```

## jane_storage.settings.ConflictRetries

**Клас.** Код: [services/storage/src/jane_storage/settings.py:149](../../../../../../services/storage/src/jane_storage/settings.py#L149).

```python
class ConflictRetries(RetryPolicy):
```

Базові типи / інтерфейси: `RetryPolicy`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_attempts](../../../../jane-kit/reference/types/generated/jane_kit.clients.md#jane_kitclientsretrypolicymax_attempts) | Поле | так |
| [initial_backoff_ms](../../../../jane-kit/reference/types/generated/jane_kit.clients.md#jane_kitclientsretrypolicyinitial_backoff_ms) | Поле | так |
| [max_backoff_ms](../../../../jane-kit/reference/types/generated/jane_kit.clients.md#jane_kitclientsretrypolicymax_backoff_ms) | Поле | так |
| [backoff_multiplier](../../../../jane-kit/reference/types/generated/jane_kit.clients.md#jane_kitclientsretrypolicybackoff_multiplier) | Поле | так |
| [jitter](../../../../jane-kit/reference/types/generated/jane_kit.clients.md#jane_kitclientsretrypolicyjitter) | Поле | так |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Retries of the core on ``CONFLICT`` (a concurrent writer changed the entity version first).

Not the contract ``limits.retries``: that policy is the caller's (re-sending a request with the same
``Idempotency-Key``), so neither a platform profile nor ``HandlerInvocation.limits`` changes this backoff.
The defaults are those that applied before the split (``RetryPolicy`` of jane-kit).
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_limits_profile.py:50](../../../../../../services/storage/tests/test_limits_profile.py#L50).

```python
assert lim.conflict_retries == ConflictRetries()
```

Контекст і передумови: [services/storage/tests/test_reprocess_reads.py:291](../../../../../../services/storage/tests/test_reprocess_reads.py#L291).

```python
policy = ConflictRetries(max_attempts=5, initial_backoff_ms=10, max_backoff_ms=25, jitter=False)
```

## jane_storage.settings.Invocations

**Клас.** Код: [services/storage/src/jane_storage/settings.py:157](../../../../../../services/storage/src/jane_storage/settings.py#L157).

```python
class Invocations(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_results_in_memory](jane_storage.settings.md#jane_storagesettingsinvocationsmax_results_in_memory) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_storage.settings.Invocations.max_results_in_memory

**Поле.** Код: [services/storage/src/jane_storage/settings.py:158](../../../../../../services/storage/src/jane_storage/settings.py#L158).

```python
max_results_in_memory: int = Field(default=10000, ge=1)
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
How many recent HandlerResults ``GET /v1/invocations/{id}`` keeps (per instance).
```

## jane_storage.settings.PackageLimits

**Клас.** Код: [services/storage/src/jane_storage/settings.py:162](../../../../../../services/storage/src/jane_storage/settings.py#L162).

```python
class PackageLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_archive_bytes](jane_storage.settings.md#jane_storagesettingspackagelimitsmax_archive_bytes) | Поле | ні |
| [max_unpacked_bytes](jane_storage.settings.md#jane_storagesettingspackagelimitsmax_unpacked_bytes) | Поле | ні |
| [max_files](jane_storage.settings.md#jane_storagesettingspackagelimitsmax_files) | Поле | ні |
| [cache_max_entries](jane_storage.settings.md#jane_storagesettingspackagelimitscache_max_entries) | Поле | ні |
| [registry_connect_timeout_ms](jane_storage.settings.md#jane_storagesettingspackagelimitsregistry_connect_timeout_ms) | Поле | ні |
| [registry_request_timeout_ms](jane_storage.settings.md#jane_storagesettingspackagelimitsregistry_request_timeout_ms) | Поле | ні |
| [archive_limits](jane_storage.settings.md#jane_storagesettingspackagelimitsarchive_limits) | Метод | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Storage packages that are not built in: ``package_archive`` and registry downloads (untrusted archives).

The size defaults equal the registry's own ``packages`` limits, so every version it accepts can be loaded.
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_registry_packages.py:432](../../../../../../services/storage/tests/test_registry_packages.py#L432).

```python
packages = RegistryPackages(REGISTRY_URL, PackageLimits(), transport=httpx.MockTransport(answer))
```

Контекст і передумови: [services/storage/tests/test_registry_packages.py:450](../../../../../../services/storage/tests/test_registry_packages.py#L450).

```python
packages = RegistryPackages(
        REGISTRY_URL, PackageLimits(cache_max_entries=2), transport=httpx.MockTransport(answer)
    )
```

## jane_storage.settings.PackageLimits.max_archive_bytes

**Поле.** Код: [services/storage/src/jane_storage/settings.py:167](../../../../../../services/storage/src/jane_storage/settings.py#L167).

```python
max_archive_bytes: int = Field(default=20 * 1024 * 1024, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "20 * 1024 * 1024",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Largest package archive; a registry download stops as soon as it is passed.
```

## jane_storage.settings.PackageLimits.max_unpacked_bytes

**Поле.** Код: [services/storage/src/jane_storage/settings.py:169](../../../../../../services/storage/src/jane_storage/settings.py#L169).

```python
max_unpacked_bytes: int = Field(default=50 * 1024 * 1024, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "50 * 1024 * 1024",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Total size of the files of one package.
```

## jane_storage.settings.PackageLimits.max_files

**Поле.** Код: [services/storage/src/jane_storage/settings.py:171](../../../../../../services/storage/src/jane_storage/settings.py#L171).

```python
max_files: int = Field(default=2000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2000",
  "ge": "1"
}
```

## jane_storage.settings.PackageLimits.cache_max_entries

**Поле.** Код: [services/storage/src/jane_storage/settings.py:172](../../../../../../services/storage/src/jane_storage/settings.py#L172).

```python
cache_max_entries: int = Field(default=128, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "128",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Registry packages kept in memory per instance (LRU by digest).
```

## jane_storage.settings.PackageLimits.registry_connect_timeout_ms

**Поле.** Код: [services/storage/src/jane_storage/settings.py:174](../../../../../../services/storage/src/jane_storage/settings.py#L174).

```python
registry_connect_timeout_ms: int = Field(default=5000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5000",
  "ge": "1"
}
```

## jane_storage.settings.PackageLimits.registry_request_timeout_ms

**Поле.** Код: [services/storage/src/jane_storage/settings.py:175](../../../../../../services/storage/src/jane_storage/settings.py#L175).

```python
registry_request_timeout_ms: int = Field(default=30000, ge=1)
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
Whole archive download from the registry (connect + response + body).
```

## jane_storage.settings.PackageLimits.archive_limits

**Метод.** Код: [services/storage/src/jane_storage/settings.py:178](../../../../../../services/storage/src/jane_storage/settings.py#L178).

```python
def archive_limits(self) -> ArchiveLimits:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `ArchiveLimits`.

## jane_storage.settings.ServiceLimits

**Клас.** Код: [services/storage/src/jane_storage/settings.py:182](../../../../../../services/storage/src/jane_storage/settings.py#L182).

```python
class ServiceLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [jobs](jane_storage.settings.md#jane_storagesettingsservicelimitsjobs) | Поле | ні |
| [idempotency](jane_storage.settings.md#jane_storagesettingsservicelimitsidempotency) | Поле | ні |
| [conflict_retries](jane_storage.settings.md#jane_storagesettingsservicelimitsconflict_retries) | Поле | ні |
| [timeouts](jane_storage.settings.md#jane_storagesettingsservicelimitstimeouts) | Поле | ні |
| [transfer](jane_storage.settings.md#jane_storagesettingsservicelimitstransfer) | Поле | ні |
| [objects](jane_storage.settings.md#jane_storagesettingsservicelimitsobjects) | Поле | ні |
| [adapters](jane_storage.settings.md#jane_storagesettingsservicelimitsadapters) | Поле | ні |
| [pages](jane_storage.settings.md#jane_storagesettingsservicelimitspages) | Поле | ні |
| [invocations](jane_storage.settings.md#jane_storagesettingsservicelimitsinvocations) | Поле | ні |
| [packages](jane_storage.settings.md#jane_storagesettingsservicelimitspackages) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Limits of this service. Contract names (``limits.schema.json``) where the limit exists there.
```

## jane_storage.settings.ServiceLimits.jobs

**Поле.** Код: [services/storage/src/jane_storage/settings.py:185](../../../../../../services/storage/src/jane_storage/settings.py#L185).

```python
jobs: JobLimits = JobLimits()
```

Доступ: читання — так; запис — так.

## jane_storage.settings.ServiceLimits.idempotency

**Поле.** Код: [services/storage/src/jane_storage/settings.py:186](../../../../../../services/storage/src/jane_storage/settings.py#L186).

```python
idempotency: IdempotencyLimits = IdempotencyLimits()
```

Доступ: читання — так; запис — так.

## jane_storage.settings.ServiceLimits.conflict_retries

**Поле.** Код: [services/storage/src/jane_storage/settings.py:187](../../../../../../services/storage/src/jane_storage/settings.py#L187).

```python
conflict_retries: ConflictRetries = ConflictRetries()
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Retries of the core on ``CONFLICT`` (``JANE_STORAGE_LIMITS__CONFLICT_RETRIES__*``); the contract
    ``limits.retries`` of a profile or an invocation is not used by storage (it is the caller's policy).
```

## jane_storage.settings.ServiceLimits.timeouts

**Поле.** Код: [services/storage/src/jane_storage/settings.py:190](../../../../../../services/storage/src/jane_storage/settings.py#L190).

```python
timeouts: Timeouts = Timeouts()
```

Доступ: читання — так; запис — так.

## jane_storage.settings.ServiceLimits.transfer

**Поле.** Код: [services/storage/src/jane_storage/settings.py:191](../../../../../../services/storage/src/jane_storage/settings.py#L191).

```python
transfer: Transfer = Transfer()
```

Доступ: читання — так; запис — так.

## jane_storage.settings.ServiceLimits.objects

**Поле.** Код: [services/storage/src/jane_storage/settings.py:192](../../../../../../services/storage/src/jane_storage/settings.py#L192).

```python
objects: Objects = Objects()
```

Доступ: читання — так; запис — так.

## jane_storage.settings.ServiceLimits.adapters

**Поле.** Код: [services/storage/src/jane_storage/settings.py:193](../../../../../../services/storage/src/jane_storage/settings.py#L193).

```python
adapters: Adapters = Adapters()
```

Доступ: читання — так; запис — так.

## jane_storage.settings.ServiceLimits.pages

**Поле.** Код: [services/storage/src/jane_storage/settings.py:194](../../../../../../services/storage/src/jane_storage/settings.py#L194).

```python
pages: PageLimits = PageLimits()
```

Доступ: читання — так; запис — так.

## jane_storage.settings.ServiceLimits.invocations

**Поле.** Код: [services/storage/src/jane_storage/settings.py:195](../../../../../../services/storage/src/jane_storage/settings.py#L195).

```python
invocations: Invocations = Invocations()
```

Доступ: читання — так; запис — так.

## jane_storage.settings.ServiceLimits.packages

**Поле.** Код: [services/storage/src/jane_storage/settings.py:196](../../../../../../services/storage/src/jane_storage/settings.py#L196).

```python
packages: PackageLimits = PackageLimits()
```

Доступ: читання — так; запис — так.

## jane_storage.settings.resolve_service_limits

**Функція.** Код: [services/storage/src/jane_storage/settings.py:227](../../../../../../services/storage/src/jane_storage/settings.py#L227).

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
Defaults <- platform file (``..._LIMITS_FILE``) <- ``JANE_STORAGE_LIMITS__*`` <- ``extra``
(request layer from ``HandlerInvocation.limits``).

The platform file may be a whole platform profile (``deploy/profiles/<profile>.json``): contract limits
storage does not have are ignored (``ResolvedLimits.ignored``, start-up log); typos fail. The old
``JANE_STORAGE_LIMITS__RETRIES__*`` (and ``HARD_CAPS__RETRIES__*``) still configure the CONFLICT retries, with a
deprecation warning (:func:`_legacy_retries`).
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_limits_profile.py:39](../../../../../../services/storage/tests/test_limits_profile.py#L39).

```python
resolved = resolve_service_limits(Settings(log_format="console", limits_file=path))
```

Контекст і передумови: [services/storage/tests/test_limits_profile.py:79](../../../../../../services/storage/tests/test_limits_profile.py#L79).

```python
resolve_service_limits(settings, LimitLayer("request", {"timeouts": {"sync_response_max": 1}}))
```
