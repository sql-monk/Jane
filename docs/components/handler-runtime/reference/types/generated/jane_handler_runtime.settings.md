# jane_handler_runtime.settings

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_handler_runtime.settings.ENV_PREFIX](#jane_handler_runtimesettingsenv_prefix)
- [jane_handler_runtime.settings.DEFAULT_PROFILE](#jane_handler_runtimesettingsdefault_profile)
- [jane_handler_runtime.settings.Settings](#jane_handler_runtimesettingssettings)
- [jane_handler_runtime.settings.Settings.model_config](#jane_handler_runtimesettingssettingsmodel_config)
- [jane_handler_runtime.settings.Settings.service_name](#jane_handler_runtimesettingssettingsservice_name)
- [jane_handler_runtime.settings.Settings.sandbox_backend](#jane_handler_runtimesettingssettingssandbox_backend)
- [jane_handler_runtime.settings.Settings.allow_unsafe_subprocess](#jane_handler_runtimesettingssettingsallow_unsafe_subprocess)
- [jane_handler_runtime.settings.Settings.docker_host](#jane_handler_runtimesettingssettingsdocker_host)
- [jane_handler_runtime.settings.Settings.docker_runtime](#jane_handler_runtimesettingssettingsdocker_runtime)
- [jane_handler_runtime.settings.Settings.sandbox_user](#jane_handler_runtimesettingssettingssandbox_user)
- [jane_handler_runtime.settings.Settings.sandbox_labels](#jane_handler_runtimesettingssettingssandbox_labels)
- [jane_handler_runtime.settings.Settings.profile_images](#jane_handler_runtimesettingssettingsprofile_images)
- [jane_handler_runtime.settings.Settings.registry_url](#jane_handler_runtimesettingssettingsregistry_url)
- [jane_handler_runtime.settings.Settings.registry_token](#jane_handler_runtimesettingssettingsregistry_token)
- [jane_handler_runtime.settings.Settings.package_cache_dir](#jane_handler_runtimesettingssettingspackage_cache_dir)
- [jane_handler_runtime.settings.Settings.blob_roots](#jane_handler_runtimesettingssettingsblob_roots)
- [jane_handler_runtime.settings.Settings.download_host_allowlist](#jane_handler_runtimesettingssettingsdownload_host_allowlist)
- [jane_handler_runtime.settings.Settings.state_dsn](#jane_handler_runtimesettingssettingsstate_dsn)
- [jane_handler_runtime.settings.Settings.state_schema](#jane_handler_runtimesettingssettingsstate_schema)
- [jane_handler_runtime.settings.Settings.contracts_dir](#jane_handler_runtimesettingssettingscontracts_dir)
- [jane_handler_runtime.settings.SandboxLimits](#jane_handler_runtimesettingssandboxlimits)
- [jane_handler_runtime.settings.SandboxLimits.cpu_cores](#jane_handler_runtimesettingssandboxlimitscpu_cores)
- [jane_handler_runtime.settings.SandboxLimits.memory_mb](#jane_handler_runtimesettingssandboxlimitsmemory_mb)
- [jane_handler_runtime.settings.SandboxLimits.wall_time_ms](#jane_handler_runtimesettingssandboxlimitswall_time_ms)
- [jane_handler_runtime.settings.SandboxLimits.max_output_bytes](#jane_handler_runtimesettingssandboxlimitsmax_output_bytes)
- [jane_handler_runtime.settings.SandboxLimits.max_processes](#jane_handler_runtimesettingssandboxlimitsmax_processes)
- [jane_handler_runtime.settings.SandboxLimits.tmpfs_mb](#jane_handler_runtimesettingssandboxlimitstmpfs_mb)
- [jane_handler_runtime.settings.TimeoutLimits](#jane_handler_runtimesettingstimeoutlimits)
- [jane_handler_runtime.settings.TimeoutLimits.invocation_timeout_ms](#jane_handler_runtimesettingstimeoutlimitsinvocation_timeout_ms)
- [jane_handler_runtime.settings.TimeoutLimits.sync_response_max_ms](#jane_handler_runtimesettingstimeoutlimitssync_response_max_ms)
- [jane_handler_runtime.settings.TimeoutLimits.request_timeout_ms](#jane_handler_runtimesettingstimeoutlimitsrequest_timeout_ms)
- [jane_handler_runtime.settings.ConcurrencyLimits](#jane_handler_runtimesettingsconcurrencylimits)
- [jane_handler_runtime.settings.ConcurrencyLimits.max_parallel_invocations](#jane_handler_runtimesettingsconcurrencylimitsmax_parallel_invocations)
- [jane_handler_runtime.settings.PackageLimits](#jane_handler_runtimesettingspackagelimits)
- [jane_handler_runtime.settings.PackageLimits.max_archive_bytes](#jane_handler_runtimesettingspackagelimitsmax_archive_bytes)
- [jane_handler_runtime.settings.PackageLimits.max_unpacked_bytes](#jane_handler_runtimesettingspackagelimitsmax_unpacked_bytes)
- [jane_handler_runtime.settings.PackageLimits.max_files](#jane_handler_runtimesettingspackagelimitsmax_files)
- [jane_handler_runtime.settings.PackageLimits.cache_max_entries](#jane_handler_runtimesettingspackagelimitscache_max_entries)
- [jane_handler_runtime.settings.PackageLimits.max_input_bytes](#jane_handler_runtimesettingspackagelimitsmax_input_bytes)
- [jane_handler_runtime.settings.PackageLimits.max_stored_results](#jane_handler_runtimesettingspackagelimitsmax_stored_results)
- [jane_handler_runtime.settings.PackageLimits.docker_api_timeout_ms](#jane_handler_runtimesettingspackagelimitsdocker_api_timeout_ms)
- [jane_handler_runtime.settings.PackageLimits.max_stderr_in_result_bytes](#jane_handler_runtimesettingspackagelimitsmax_stderr_in_result_bytes)
- [jane_handler_runtime.settings.PackageLimits.unavailable_retry_after_seconds](#jane_handler_runtimesettingspackagelimitsunavailable_retry_after_seconds)
- [jane_handler_runtime.settings.PackageLimits.kill_grace_ms](#jane_handler_runtimesettingspackagelimitskill_grace_ms)
- [jane_handler_runtime.settings.StateLimits](#jane_handler_runtimesettingsstatelimits)
- [jane_handler_runtime.settings.StateLimits.pool_max_size](#jane_handler_runtimesettingsstatelimitspool_max_size)
- [jane_handler_runtime.settings.StateLimits.connect_timeout_ms](#jane_handler_runtimesettingsstatelimitsconnect_timeout_ms)
- [jane_handler_runtime.settings.StateLimits.in_progress_lease_ms](#jane_handler_runtimesettingsstatelimitsin_progress_lease_ms)
- [jane_handler_runtime.settings.StateLimits.job_lease_ms](#jane_handler_runtimesettingsstatelimitsjob_lease_ms)
- [jane_handler_runtime.settings.StateLimits.heartbeat_interval_ms](#jane_handler_runtimesettingsstatelimitsheartbeat_interval_ms)
- [jane_handler_runtime.settings.ServiceLimits](#jane_handler_runtimesettingsservicelimits)
- [jane_handler_runtime.settings.ServiceLimits.sandbox](#jane_handler_runtimesettingsservicelimitssandbox)
- [jane_handler_runtime.settings.ServiceLimits.timeouts](#jane_handler_runtimesettingsservicelimitstimeouts)
- [jane_handler_runtime.settings.ServiceLimits.concurrency](#jane_handler_runtimesettingsservicelimitsconcurrency)
- [jane_handler_runtime.settings.ServiceLimits.packages](#jane_handler_runtimesettingsservicelimitspackages)
- [jane_handler_runtime.settings.ServiceLimits.state](#jane_handler_runtimesettingsservicelimitsstate)
- [jane_handler_runtime.settings.ServiceLimits.jobs](#jane_handler_runtimesettingsservicelimitsjobs)
- [jane_handler_runtime.settings.ServiceLimits.idempotency](#jane_handler_runtimesettingsservicelimitsidempotency)
- [jane_handler_runtime.settings.DEFAULT_HARD_CAPS](#jane_handler_runtimesettingsdefault_hard_caps)
- [jane_handler_runtime.settings.REQUEST_GROUPS](#jane_handler_runtimesettingsrequest_groups)
- [jane_handler_runtime.settings.request_layer](#jane_handler_runtimesettingsrequest_layer)
- [jane_handler_runtime.settings.resolve_service_limits](#jane_handler_runtimesettingsresolve_service_limits)

## jane_handler_runtime.settings.ENV_PREFIX

**Константа.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:24](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L24).

```python
ENV_PREFIX = 'JANE_HANDLER_RUNTIME_'
```

## jane_handler_runtime.settings.DEFAULT_PROFILE

**Константа.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:25](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L25).

```python
DEFAULT_PROFILE = 'python-extractor@1'
```

## jane_handler_runtime.settings.Settings

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:28](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L28).

```python
class Settings(JaneSettings):
```

Базові типи / інтерфейси: `JaneSettings`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_config](jane_handler_runtime.settings.md#jane_handler_runtimesettingssettingsmodel_config) | Поле | ні |
| [service_name](jane_handler_runtime.settings.md#jane_handler_runtimesettingssettingsservice_name) | Поле | ні |
| [sandbox_backend](jane_handler_runtime.settings.md#jane_handler_runtimesettingssettingssandbox_backend) | Поле | ні |
| [allow_unsafe_subprocess](jane_handler_runtime.settings.md#jane_handler_runtimesettingssettingsallow_unsafe_subprocess) | Поле | ні |
| [docker_host](jane_handler_runtime.settings.md#jane_handler_runtimesettingssettingsdocker_host) | Поле | ні |
| [docker_runtime](jane_handler_runtime.settings.md#jane_handler_runtimesettingssettingsdocker_runtime) | Поле | ні |
| [sandbox_user](jane_handler_runtime.settings.md#jane_handler_runtimesettingssettingssandbox_user) | Поле | ні |
| [sandbox_labels](jane_handler_runtime.settings.md#jane_handler_runtimesettingssettingssandbox_labels) | Поле | ні |
| [profile_images](jane_handler_runtime.settings.md#jane_handler_runtimesettingssettingsprofile_images) | Поле | ні |
| [registry_url](jane_handler_runtime.settings.md#jane_handler_runtimesettingssettingsregistry_url) | Поле | ні |
| [registry_token](jane_handler_runtime.settings.md#jane_handler_runtimesettingssettingsregistry_token) | Поле | ні |
| [package_cache_dir](jane_handler_runtime.settings.md#jane_handler_runtimesettingssettingspackage_cache_dir) | Поле | ні |
| [blob_roots](jane_handler_runtime.settings.md#jane_handler_runtimesettingssettingsblob_roots) | Поле | ні |
| [download_host_allowlist](jane_handler_runtime.settings.md#jane_handler_runtimesettingssettingsdownload_host_allowlist) | Поле | ні |
| [state_dsn](jane_handler_runtime.settings.md#jane_handler_runtimesettingssettingsstate_dsn) | Поле | ні |
| [state_schema](jane_handler_runtime.settings.md#jane_handler_runtimesettingssettingsstate_schema) | Поле | ні |
| [contracts_dir](jane_handler_runtime.settings.md#jane_handler_runtimesettingssettingscontracts_dir) | Поле | ні |
| [instance_id](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingsinstance_id) | Поле | так |
| [host](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingshost) | Поле | так |
| [port](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfigjanesettingsport) | Поле | так |
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

Контекст і передумови: [services/handler-runtime/tests/conftest.py:88](../../../../../../services/handler-runtime/tests/conftest.py#L88).

```python
return Settings(
        log_format="console",
        sandbox_backend="subprocess",
        allow_unsafe_subprocess=True,
        package_cache_dir=tmp_path / "cache",
    )
```

Контекст і передумови: [services/handler-runtime/tests/test_app.py:327](../../../../../../services/handler-runtime/tests/test_app.py#L327).

```python
settings = Settings(log_format="console", sandbox_backend="subprocess", package_cache_dir=tmp_path / "c")
```

## jane_handler_runtime.settings.Settings.model_config

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:29](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L29).

```python
model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra='ignore', env_nested_delimiter='__')
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.settings.Settings.service_name

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:31](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L31).

```python
service_name: str = 'handler-runtime'
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.settings.Settings.sandbox_backend

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:33](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L33).

```python
sandbox_backend: Literal['docker', 'subprocess'] = 'docker'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``docker`` (default, ADR-0003) or ``subprocess`` - no isolation, trusted local packages only.
```

## jane_handler_runtime.settings.Settings.allow_unsafe_subprocess

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:35](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L35).

```python
allow_unsafe_subprocess: bool = False
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
The ``subprocess`` backend refuses to run unless this is true (never in production).
```

## jane_handler_runtime.settings.Settings.docker_host

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:37](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L37).

```python
docker_host: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Docker/Podman API endpoint; default: ``DOCKER_HOST`` or the platform socket / named pipe.
```

## jane_handler_runtime.settings.Settings.docker_runtime

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:39](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L39).

```python
docker_runtime: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
OCI runtime of sandbox containers, e.g. ``runsc`` (gVisor).
```

## jane_handler_runtime.settings.Settings.sandbox_user

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:41](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L41).

```python
sandbox_user: str = '65534:65534'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Non-root uid:gid inside the sandbox.
```

## jane_handler_runtime.settings.Settings.sandbox_labels

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:43](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L43).

```python
sandbox_labels: dict[str, str] = Field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

### Опис із вихідного коду

```text
Extra labels on sandbox containers (e.g. to find and clean them up in a test stack).
```

## jane_handler_runtime.settings.Settings.profile_images

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:45](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L45).

```python
profile_images: dict[str, str] = Field(default_factory=lambda: {DEFAULT_PROFILE: 'jane/python-extractor:1'})
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "lambda: {DEFAULT_PROFILE: 'jane/python-extractor:1'}"
}
```

### Опис із вихідного коду

```text
Runtime profile -> sandbox image (pin by digest in production: ``repo@sha256:...``).
```

## jane_handler_runtime.settings.Settings.registry_url

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:50](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L50).

```python
registry_url: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Base URL of the handler repository (registry.v1); packages without ``package_archive`` come from it.
```

## jane_handler_runtime.settings.Settings.registry_token

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:52](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L52).

```python
registry_token: SecretStr | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Bearer token for the registry (from the environment, never logged).
```

## jane_handler_runtime.settings.Settings.package_cache_dir

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:54](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L54).

```python
package_cache_dir: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Where verified packages are cached by digest; default: a temporary directory.
```

## jane_handler_runtime.settings.Settings.blob_roots

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:56](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L56).

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
Directories from which ``file://`` blobs (package archives, material content) may be read.
    Empty = ``file://`` blobs are refused (the service must not read arbitrary host files).
```

## jane_handler_runtime.settings.Settings.download_host_allowlist

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:59](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L59).

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

## jane_handler_runtime.settings.Settings.state_dsn

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:62](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L62).

```python
state_dsn: SecretStr | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
PostgreSQL DSN of the service's own state (idempotency keys, jobs, results) shared by instances.
    Unset: in-memory state - only for a single standalone instance and the CLI (lost on restart).
```

## jane_handler_runtime.settings.Settings.state_schema

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:65](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L65).

```python
state_schema: str = Field(default='jane_handler_runtime', pattern='^[a-z_][a-z0-9_]{0,62}$')
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "'jane_handler_runtime'",
  "pattern": "'^[a-z_][a-z0-9_]{0,62}$'"
}
```

### Опис із вихідного коду

```text
Schema of the state tables (created if missing).
```

## jane_handler_runtime.settings.Settings.contracts_dir

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:67](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L67).

```python
contracts_dir: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``contracts/`` with the JSON Schemas; default: found upwards from the package (repo checkout).
```

## jane_handler_runtime.settings.SandboxLimits

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:77](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L77).

```python
class SandboxLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [cpu_cores](jane_handler_runtime.settings.md#jane_handler_runtimesettingssandboxlimitscpu_cores) | Поле | ні |
| [memory_mb](jane_handler_runtime.settings.md#jane_handler_runtimesettingssandboxlimitsmemory_mb) | Поле | ні |
| [wall_time_ms](jane_handler_runtime.settings.md#jane_handler_runtimesettingssandboxlimitswall_time_ms) | Поле | ні |
| [max_output_bytes](jane_handler_runtime.settings.md#jane_handler_runtimesettingssandboxlimitsmax_output_bytes) | Поле | ні |
| [max_processes](jane_handler_runtime.settings.md#jane_handler_runtimesettingssandboxlimitsmax_processes) | Поле | ні |
| [tmpfs_mb](jane_handler_runtime.settings.md#jane_handler_runtimesettingssandboxlimitstmpfs_mb) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
``limits.sandbox`` of the contract (ADR-0003).
```

## jane_handler_runtime.settings.SandboxLimits.cpu_cores

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:80](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L80).

```python
cpu_cores: float = Field(default=1.0, gt=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1.0",
  "gt": "0"
}
```

## jane_handler_runtime.settings.SandboxLimits.memory_mb

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:81](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L81).

```python
memory_mb: int = Field(default=512, ge=16)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "512",
  "ge": "16"
}
```

## jane_handler_runtime.settings.SandboxLimits.wall_time_ms

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:82](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L82).

```python
wall_time_ms: int = Field(default=30000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "30000",
  "ge": "1"
}
```

## jane_handler_runtime.settings.SandboxLimits.max_output_bytes

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:83](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L83).

```python
max_output_bytes: int = Field(default=4194304, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "4194304",
  "ge": "1"
}
```

## jane_handler_runtime.settings.SandboxLimits.max_processes

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:84](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L84).

```python
max_processes: int = Field(default=16, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "16",
  "ge": "1"
}
```

## jane_handler_runtime.settings.SandboxLimits.tmpfs_mb

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:85](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L85).

```python
tmpfs_mb: int = Field(default=64, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "64",
  "ge": "0"
}
```

## jane_handler_runtime.settings.TimeoutLimits

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:88](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L88).

```python
class TimeoutLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [invocation_timeout_ms](jane_handler_runtime.settings.md#jane_handler_runtimesettingstimeoutlimitsinvocation_timeout_ms) | Поле | ні |
| [sync_response_max_ms](jane_handler_runtime.settings.md#jane_handler_runtimesettingstimeoutlimitssync_response_max_ms) | Поле | ні |
| [request_timeout_ms](jane_handler_runtime.settings.md#jane_handler_runtimesettingstimeoutlimitsrequest_timeout_ms) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_handler_runtime.settings.TimeoutLimits.invocation_timeout_ms

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:89](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L89).

```python
invocation_timeout_ms: int = contract_field('timeouts.invocation_timeout_ms', 60000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'timeouts.invocation_timeout_ms'",
  "ge": "1"
}
```

## jane_handler_runtime.settings.TimeoutLimits.sync_response_max_ms

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:90](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L90).

```python
sync_response_max_ms: int = contract_field('timeouts.sync_response_max_ms', 25000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'timeouts.sync_response_max_ms'",
  "ge": "1"
}
```

## jane_handler_runtime.settings.TimeoutLimits.request_timeout_ms

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:91](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L91).

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
Registry calls and blob downloads (a whole ``download_url`` download, connection included).
```

## jane_handler_runtime.settings.ConcurrencyLimits

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:95](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L95).

```python
class ConcurrencyLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_parallel_invocations](jane_handler_runtime.settings.md#jane_handler_runtimesettingsconcurrencylimitsmax_parallel_invocations) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_handler_runtime.settings.ConcurrencyLimits.max_parallel_invocations

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:96](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L96).

```python
max_parallel_invocations: int = contract_field('concurrency.max_parallel_invocations', 2, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'concurrency.max_parallel_invocations'",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Sandboxes running at the same time in one instance.
```

## jane_handler_runtime.settings.PackageLimits

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:100](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L100).

```python
class PackageLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_archive_bytes](jane_handler_runtime.settings.md#jane_handler_runtimesettingspackagelimitsmax_archive_bytes) | Поле | ні |
| [max_unpacked_bytes](jane_handler_runtime.settings.md#jane_handler_runtimesettingspackagelimitsmax_unpacked_bytes) | Поле | ні |
| [max_files](jane_handler_runtime.settings.md#jane_handler_runtimesettingspackagelimitsmax_files) | Поле | ні |
| [cache_max_entries](jane_handler_runtime.settings.md#jane_handler_runtimesettingspackagelimitscache_max_entries) | Поле | ні |
| [max_input_bytes](jane_handler_runtime.settings.md#jane_handler_runtimesettingspackagelimitsmax_input_bytes) | Поле | ні |
| [max_stored_results](jane_handler_runtime.settings.md#jane_handler_runtimesettingspackagelimitsmax_stored_results) | Поле | ні |
| [docker_api_timeout_ms](jane_handler_runtime.settings.md#jane_handler_runtimesettingspackagelimitsdocker_api_timeout_ms) | Поле | ні |
| [max_stderr_in_result_bytes](jane_handler_runtime.settings.md#jane_handler_runtimesettingspackagelimitsmax_stderr_in_result_bytes) | Поле | ні |
| [unavailable_retry_after_seconds](jane_handler_runtime.settings.md#jane_handler_runtimesettingspackagelimitsunavailable_retry_after_seconds) | Поле | ні |
| [kill_grace_ms](jane_handler_runtime.settings.md#jane_handler_runtimesettingspackagelimitskill_grace_ms) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Service-specific bounds for untrusted package archives and inputs (not in the contract).
```

## jane_handler_runtime.settings.PackageLimits.max_archive_bytes

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:103](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L103).

```python
max_archive_bytes: int = Field(default=50 * 2 ** 20, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "50 * 2 ** 20",
  "ge": "1"
}
```

## jane_handler_runtime.settings.PackageLimits.max_unpacked_bytes

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:104](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L104).

```python
max_unpacked_bytes: int = Field(default=200 * 2 ** 20, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "200 * 2 ** 20",
  "ge": "1"
}
```

## jane_handler_runtime.settings.PackageLimits.max_files

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:105](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L105).

```python
max_files: int = Field(default=5000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5000",
  "ge": "1"
}
```

## jane_handler_runtime.settings.PackageLimits.cache_max_entries

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:106](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L106).

```python
cache_max_entries: int = Field(default=64, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "64",
  "ge": "1"
}
```

## jane_handler_runtime.settings.PackageLimits.max_input_bytes

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:107](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L107).

```python
max_input_bytes: int = Field(default=64 * 2 ** 20, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "64 * 2 ** 20",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Content of one material (inline or blob).
```

## jane_handler_runtime.settings.PackageLimits.max_stored_results

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:109](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L109).

```python
max_stored_results: int = Field(default=10000, ge=1)
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
``GET /v1/invocations/{id}`` keeps at most this many results (in memory, per instance).
```

## jane_handler_runtime.settings.PackageLimits.docker_api_timeout_ms

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:111](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L111).

```python
docker_api_timeout_ms: int = Field(default=60000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "60000",
  "ge": "1"
}
```

## jane_handler_runtime.settings.PackageLimits.max_stderr_in_result_bytes

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:112](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L112).

```python
max_stderr_in_result_bytes: int = Field(default=16000, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "16000",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Tail of the sandbox stderr put into ``diagnostics.logs_ref`` (inline).
```

## jane_handler_runtime.settings.PackageLimits.unavailable_retry_after_seconds

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:114](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L114).

```python
unavailable_retry_after_seconds: int = Field(default=5, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
``Retry-After`` of 503 when the container engine is not reachable.
```

## jane_handler_runtime.settings.PackageLimits.kill_grace_ms

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:116](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L116).

```python
kill_grace_ms: int = Field(default=2000, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2000",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
In-container ``timeout -s KILL`` fires at wall_time_ms + this (safety net if the runtime dies).
```

## jane_handler_runtime.settings.StateLimits

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:120](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L120).

```python
class StateLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [pool_max_size](jane_handler_runtime.settings.md#jane_handler_runtimesettingsstatelimitspool_max_size) | Поле | ні |
| [connect_timeout_ms](jane_handler_runtime.settings.md#jane_handler_runtimesettingsstatelimitsconnect_timeout_ms) | Поле | ні |
| [in_progress_lease_ms](jane_handler_runtime.settings.md#jane_handler_runtimesettingsstatelimitsin_progress_lease_ms) | Поле | ні |
| [job_lease_ms](jane_handler_runtime.settings.md#jane_handler_runtimesettingsstatelimitsjob_lease_ms) | Поле | ні |
| [heartbeat_interval_ms](jane_handler_runtime.settings.md#jane_handler_runtimesettingsstatelimitsheartbeat_interval_ms) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Shared PostgreSQL state (``state_dsn``).
```

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_state.py:338](../../../../../../services/handler-runtime/tests/test_state.py#L338).

```python
limits = ServiceLimits(state=StateLimits(job_lease_ms=800, heartbeat_interval_ms=100))
```

## jane_handler_runtime.settings.StateLimits.pool_max_size

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:123](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L123).

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

## jane_handler_runtime.settings.StateLimits.connect_timeout_ms

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:124](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L124).

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

## jane_handler_runtime.settings.StateLimits.in_progress_lease_ms

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:125](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L125).

```python
in_progress_lease_ms: int = Field(default=900000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "900000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
An in-progress idempotency claim of a crashed instance can be taken over after this.
```

## jane_handler_runtime.settings.StateLimits.job_lease_ms

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:127](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L127).

```python
job_lease_ms: int = Field(default=30000, ge=1)
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
A job whose owner stops renewing this lease is marked failed when read.
```

## jane_handler_runtime.settings.StateLimits.heartbeat_interval_ms

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:129](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L129).

```python
heartbeat_interval_ms: int = Field(default=5000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "5000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
How often this instance renews leases for its unfinished jobs.
```

## jane_handler_runtime.settings.ServiceLimits

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:133](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L133).

```python
class ServiceLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [sandbox](jane_handler_runtime.settings.md#jane_handler_runtimesettingsservicelimitssandbox) | Поле | ні |
| [timeouts](jane_handler_runtime.settings.md#jane_handler_runtimesettingsservicelimitstimeouts) | Поле | ні |
| [concurrency](jane_handler_runtime.settings.md#jane_handler_runtimesettingsservicelimitsconcurrency) | Поле | ні |
| [packages](jane_handler_runtime.settings.md#jane_handler_runtimesettingsservicelimitspackages) | Поле | ні |
| [state](jane_handler_runtime.settings.md#jane_handler_runtimesettingsservicelimitsstate) | Поле | ні |
| [jobs](jane_handler_runtime.settings.md#jane_handler_runtimesettingsservicelimitsjobs) | Поле | ні |
| [idempotency](jane_handler_runtime.settings.md#jane_handler_runtimesettingsservicelimitsidempotency) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Limits of this service. Contract names (``limits.schema.json``) where the limit exists there.
```

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_state.py:181](../../../../../../services/handler-runtime/tests/test_state.py#L181).

```python
a = PostgresState(dsn[0], dsn[1], ServiceLimits(), "dead-owner")
```

Контекст і передумови: [services/handler-runtime/tests/test_state.py:182](../../../../../../services/handler-runtime/tests/test_state.py#L182).

```python
b = PostgresState(dsn[0], dsn[1], ServiceLimits(), "new-owner")
```

## jane_handler_runtime.settings.ServiceLimits.sandbox

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:136](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L136).

```python
sandbox: SandboxLimits = contract_field('sandbox', SandboxLimits())
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'sandbox'"
}
```

## jane_handler_runtime.settings.ServiceLimits.timeouts

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:137](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L137).

```python
timeouts: TimeoutLimits = TimeoutLimits()
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.settings.ServiceLimits.concurrency

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:138](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L138).

```python
concurrency: ConcurrencyLimits = ConcurrencyLimits()
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.settings.ServiceLimits.packages

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:139](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L139).

```python
packages: PackageLimits = PackageLimits()
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.settings.ServiceLimits.state

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:140](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L140).

```python
state: StateLimits = StateLimits()
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.settings.ServiceLimits.jobs

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:141](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L141).

```python
jobs: JobLimits = JobLimits()
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.settings.ServiceLimits.idempotency

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:142](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L142).

```python
idempotency: IdempotencyLimits = IdempotencyLimits()
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.settings.DEFAULT_HARD_CAPS

**Константа.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:145](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L145).

```python
DEFAULT_HARD_CAPS: dict[str, Any] = {'sandbox': {'cpu_cores': 4.0, 'memory_mb': 4096, 'wall_time_ms': 600000, 'max_output_bytes': 64 * 2 ** 20, 'max_processes': 256, 'tmpfs_mb': 1024}, 'timeouts': {'invocation_timeout_ms': 900000}}
```

### Опис із вихідного коду

```text
Service-level ceilings for values a request may ask for (a request can never raise a limit above these).
A platform file or env hard cap for the same field replaces the default.
```

## jane_handler_runtime.settings.REQUEST_GROUPS

**Константа.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:159](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L159).

```python
REQUEST_GROUPS = ('sandbox', 'timeouts')
```

### Опис із вихідного коду

```text
Groups of ``HandlerInvocation.limits`` this service applies (other groups belong to other services).
```

## jane_handler_runtime.settings.request_layer

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:192](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L192).

```python
def request_layer(limits: Mapping[str, Any] | None) -> LimitLayer | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `limits` | `Mapping[str, Any] \| None` | `—` | positional-or-keyword |

Результат: `LimitLayer | None`.

### Опис із вихідного коду

```text
``HandlerInvocation.limits`` -> request layer with only the fields this service models.
```

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_limits_profile.py:73](../../../../../../services/handler-runtime/tests/test_limits_profile.py#L73).

```python
lim = resolve_service_limits(settings, request_layer(asked)).limits
```

Контекст і передумови: [services/handler-runtime/tests/test_units.py:55](../../../../../../services/handler-runtime/tests/test_units.py#L55).

```python
layer = request_layer(
        {"sandbox": {"memory_mb": 100_000, "wall_time_ms": 5000}, "crawl": {"max_depth": 3}}
    )
```

## jane_handler_runtime.settings.resolve_service_limits

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/settings.py:203](../../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L203).

```python
def resolve_service_limits(settings: Settings, *extra: LimitLayer | None) -> ResolvedLimits[ServiceLimits]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings` | `—` | positional-or-keyword |
| `extra` | `LimitLayer \| None` | `—` | var-positional |

Результат: `ResolvedLimits[ServiceLimits]`.

### Опис із вихідного коду

```text
Defaults <- service default caps <- platform file (``..._LIMITS_FILE``) <- ``JANE_HANDLER_RUNTIME_LIMITS__*``
<- ``extra`` (request layer). Values above a hard cap are clamped (``min(request, hard_caps)``).

The platform file may be a whole platform profile (``deploy/profiles/<profile>.json``): contract limits
the runtime does not have are ignored (``ResolvedLimits.ignored``, start-up log); typos fail.
```

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_limits_profile.py:46](../../../../../../services/handler-runtime/tests/test_limits_profile.py#L46).

```python
resolved = resolve_service_limits(settings)
```

Контекст і передумови: [services/handler-runtime/tests/test_limits_profile.py:73](../../../../../../services/handler-runtime/tests/test_limits_profile.py#L73).

```python
lim = resolve_service_limits(settings, request_layer(asked)).limits
```
