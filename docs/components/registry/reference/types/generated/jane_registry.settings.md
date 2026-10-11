# jane_registry.settings

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_registry.settings.ENV_PREFIX](#jane_registrysettingsenv_prefix)
- [jane_registry.settings.Settings](#jane_registrysettingssettings)
- [jane_registry.settings.Settings.model_config](#jane_registrysettingssettingsmodel_config)
- [jane_registry.settings.Settings.service_name](#jane_registrysettingssettingsservice_name)
- [jane_registry.settings.Settings.port](#jane_registrysettingssettingsport)
- [jane_registry.settings.Settings.db](#jane_registrysettingssettingsdb)
- [jane_registry.settings.Settings.db_url](#jane_registrysettingssettingsdb_url)
- [jane_registry.settings.Settings.db_schema](#jane_registrysettingssettingsdb_schema)
- [jane_registry.settings.Settings.blob](#jane_registrysettingssettingsblob)
- [jane_registry.settings.Settings.blob_bucket](#jane_registrysettingssettingsblob_bucket)
- [jane_registry.settings.Settings.blob_prefix](#jane_registrysettingssettingsblob_prefix)
- [jane_registry.settings.Settings.blob_root](#jane_registrysettingssettingsblob_root)
- [jane_registry.settings.Settings.s3_endpoint_url](#jane_registrysettingssettingss3_endpoint_url)
- [jane_registry.settings.Settings.s3_region](#jane_registrysettingssettingss3_region)
- [jane_registry.settings.Settings.s3_access_key](#jane_registrysettingssettingss3_access_key)
- [jane_registry.settings.Settings.s3_secret_key](#jane_registrysettingssettingss3_secret_key)
- [jane_registry.settings.Settings.s3_create_bucket](#jane_registrysettingssettingss3_create_bucket)
- [jane_registry.settings.Settings.contracts_dir](#jane_registrysettingssettingscontracts_dir)
- [jane_registry.settings.Settings.runtime_profiles](#jane_registrysettingssettingsruntime_profiles)
- [jane_registry.settings.Settings.require_tests](#jane_registrysettingssettingsrequire_tests)
- [jane_registry.settings.Settings.runtime_profiles_token_ref](#jane_registrysettingssettingsruntime_profiles_token_ref)
- [jane_registry.settings.PackageLimits](#jane_registrysettingspackagelimits)
- [jane_registry.settings.PackageLimits.max_archive_bytes](#jane_registrysettingspackagelimitsmax_archive_bytes)
- [jane_registry.settings.PackageLimits.max_unpacked_bytes](#jane_registrysettingspackagelimitsmax_unpacked_bytes)
- [jane_registry.settings.PackageLimits.max_files](#jane_registrysettingspackagelimitsmax_files)
- [jane_registry.settings.PackageLimits.max_versions_per_package](#jane_registrysettingspackagelimitsmax_versions_per_package)
- [jane_registry.settings.PackageLimits.archive_cache_bytes](#jane_registrysettingspackagelimitsarchive_cache_bytes)
- [jane_registry.settings.SecretScanLimits](#jane_registrysettingssecretscanlimits)
- [jane_registry.settings.SecretScanLimits.max_scan_bytes_per_file](#jane_registrysettingssecretscanlimitsmax_scan_bytes_per_file)
- [jane_registry.settings.SecretScanLimits.min_entropy_token_length](#jane_registrysettingssecretscanlimitsmin_entropy_token_length)
- [jane_registry.settings.SecretScanLimits.scan_time_budget_ms](#jane_registrysettingssecretscanlimitsscan_time_budget_ms)
- [jane_registry.settings.SecretScanLimits.max_findings_per_file](#jane_registrysettingssecretscanlimitsmax_findings_per_file)
- [jane_registry.settings.SecretScanLimits.entropy_threshold](#jane_registrysettingssecretscanlimitsentropy_threshold)
- [jane_registry.settings.DiffLimits](#jane_registrysettingsdifflimits)
- [jane_registry.settings.DiffLimits.max_context_lines](#jane_registrysettingsdifflimitsmax_context_lines)
- [jane_registry.settings.DiffLimits.max_diff_file_bytes](#jane_registrysettingsdifflimitsmax_diff_file_bytes)
- [jane_registry.settings.DiffLimits.max_merge_file_bytes](#jane_registrysettingsdifflimitsmax_merge_file_bytes)
- [jane_registry.settings.RequestLimits](#jane_registrysettingsrequestlimits)
- [jane_registry.settings.RequestLimits.max_request_body_bytes](#jane_registrysettingsrequestlimitsmax_request_body_bytes)
- [jane_registry.settings.ProfileLimits](#jane_registrysettingsprofilelimits)
- [jane_registry.settings.ProfileLimits.fetch_timeout_ms](#jane_registrysettingsprofilelimitsfetch_timeout_ms)
- [jane_registry.settings.ProfileLimits.refresh_seconds](#jane_registrysettingsprofilelimitsrefresh_seconds)
- [jane_registry.settings.DbLimits](#jane_registrysettingsdblimits)
- [jane_registry.settings.DbLimits.pool_min_size](#jane_registrysettingsdblimitspool_min_size)
- [jane_registry.settings.DbLimits.pool_max_size](#jane_registrysettingsdblimitspool_max_size)
- [jane_registry.settings.DbLimits.connect_timeout_ms](#jane_registrysettingsdblimitsconnect_timeout_ms)
- [jane_registry.settings.DbLimits.statement_timeout_ms](#jane_registrysettingsdblimitsstatement_timeout_ms)
- [jane_registry.settings.BlobLimits](#jane_registrysettingsbloblimits)
- [jane_registry.settings.BlobLimits.connect_timeout_ms](#jane_registrysettingsbloblimitsconnect_timeout_ms)
- [jane_registry.settings.BlobLimits.read_timeout_ms](#jane_registrysettingsbloblimitsread_timeout_ms)
- [jane_registry.settings.BlobLimits.max_attempts](#jane_registrysettingsbloblimitsmax_attempts)
- [jane_registry.settings.RecoveryLimits](#jane_registrysettingsrecoverylimits)
- [jane_registry.settings.RecoveryLimits.in_progress_lease_ms](#jane_registrysettingsrecoverylimitsin_progress_lease_ms)
- [jane_registry.settings.RecoveryLimits.job_lease_ms](#jane_registrysettingsrecoverylimitsjob_lease_ms)
- [jane_registry.settings.RecoveryLimits.job_heartbeat_ms](#jane_registrysettingsrecoverylimitsjob_heartbeat_ms)
- [jane_registry.settings.ServiceLimits](#jane_registrysettingsservicelimits)
- [jane_registry.settings.ServiceLimits.jobs](#jane_registrysettingsservicelimitsjobs)
- [jane_registry.settings.ServiceLimits.idempotency](#jane_registrysettingsservicelimitsidempotency)
- [jane_registry.settings.ServiceLimits.pages](#jane_registrysettingsservicelimitspages)
- [jane_registry.settings.ServiceLimits.packages](#jane_registrysettingsservicelimitspackages)
- [jane_registry.settings.ServiceLimits.secrets](#jane_registrysettingsservicelimitssecrets)
- [jane_registry.settings.ServiceLimits.diff](#jane_registrysettingsservicelimitsdiff)
- [jane_registry.settings.ServiceLimits.requests](#jane_registrysettingsservicelimitsrequests)
- [jane_registry.settings.ServiceLimits.profiles](#jane_registrysettingsservicelimitsprofiles)
- [jane_registry.settings.ServiceLimits.db](#jane_registrysettingsservicelimitsdb)
- [jane_registry.settings.ServiceLimits.blob](#jane_registrysettingsservicelimitsblob)
- [jane_registry.settings.ServiceLimits.recovery](#jane_registrysettingsservicelimitsrecovery)
- [jane_registry.settings.resolve_service_limits](#jane_registrysettingsresolve_service_limits)

## jane_registry.settings.ENV_PREFIX

**Константа.** Код: [services/registry/src/jane_registry/settings.py:16](../../../../../../services/registry/src/jane_registry/settings.py#L16).

```python
ENV_PREFIX = 'JANE_REGISTRY_'
```

## jane_registry.settings.Settings

**Клас.** Код: [services/registry/src/jane_registry/settings.py:19](../../../../../../services/registry/src/jane_registry/settings.py#L19).

```python
class Settings(JaneSettings):
```

Базові типи / інтерфейси: `JaneSettings`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_config](jane_registry.settings.md#jane_registrysettingssettingsmodel_config) | Поле | ні |
| [service_name](jane_registry.settings.md#jane_registrysettingssettingsservice_name) | Поле | ні |
| [port](jane_registry.settings.md#jane_registrysettingssettingsport) | Поле | ні |
| [db](jane_registry.settings.md#jane_registrysettingssettingsdb) | Поле | ні |
| [db_url](jane_registry.settings.md#jane_registrysettingssettingsdb_url) | Поле | ні |
| [db_schema](jane_registry.settings.md#jane_registrysettingssettingsdb_schema) | Поле | ні |
| [blob](jane_registry.settings.md#jane_registrysettingssettingsblob) | Поле | ні |
| [blob_bucket](jane_registry.settings.md#jane_registrysettingssettingsblob_bucket) | Поле | ні |
| [blob_prefix](jane_registry.settings.md#jane_registrysettingssettingsblob_prefix) | Поле | ні |
| [blob_root](jane_registry.settings.md#jane_registrysettingssettingsblob_root) | Поле | ні |
| [s3_endpoint_url](jane_registry.settings.md#jane_registrysettingssettingss3_endpoint_url) | Поле | ні |
| [s3_region](jane_registry.settings.md#jane_registrysettingssettingss3_region) | Поле | ні |
| [s3_access_key](jane_registry.settings.md#jane_registrysettingssettingss3_access_key) | Поле | ні |
| [s3_secret_key](jane_registry.settings.md#jane_registrysettingssettingss3_secret_key) | Поле | ні |
| [s3_create_bucket](jane_registry.settings.md#jane_registrysettingssettingss3_create_bucket) | Поле | ні |
| [contracts_dir](jane_registry.settings.md#jane_registrysettingssettingscontracts_dir) | Поле | ні |
| [runtime_profiles](jane_registry.settings.md#jane_registrysettingssettingsruntime_profiles) | Поле | ні |
| [require_tests](jane_registry.settings.md#jane_registrysettingssettingsrequire_tests) | Поле | ні |
| [runtime_profiles_token_ref](jane_registry.settings.md#jane_registrysettingssettingsruntime_profiles_token_ref) | Поле | ні |
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

Контекст і передумови: [services/registry/tests/conftest.py:55](../../../../../../services/registry/tests/conftest.py#L55).

```python
return Settings(**values)
```

Контекст і передумови: [services/registry/tests/conftest.py:113](../../../../../../services/registry/tests/conftest.py#L113).

```python
return Settings(
                db="memory", blob="filesystem", blob_root=tmp_path / "blobs", **{**common, **extra}
            )
```

## jane_registry.settings.Settings.model_config

**Поле.** Код: [services/registry/src/jane_registry/settings.py:20](../../../../../../services/registry/src/jane_registry/settings.py#L20).

```python
model_config = SettingsConfigDict(env_prefix=ENV_PREFIX, extra='ignore', env_nested_delimiter='__')
```

Доступ: читання — так; запис — так.

## jane_registry.settings.Settings.service_name

**Поле.** Код: [services/registry/src/jane_registry/settings.py:22](../../../../../../services/registry/src/jane_registry/settings.py#L22).

```python
service_name: str = 'registry'
```

Доступ: читання — так; запис — так.

## jane_registry.settings.Settings.port

**Поле.** Код: [services/registry/src/jane_registry/settings.py:23](../../../../../../services/registry/src/jane_registry/settings.py#L23).

```python
port: int = 8105
```

Доступ: читання — так; запис — так.

## jane_registry.settings.Settings.db

**Поле.** Код: [services/registry/src/jane_registry/settings.py:26](../../../../../../services/registry/src/jane_registry/settings.py#L26).

```python
db: Literal['postgres', 'memory'] = 'postgres'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``postgres`` - own PostgreSQL database (``jane_registry``); ``memory`` - one process, no persistence
    (local experiments and fast tests only).
```

## jane_registry.settings.Settings.db_url

**Поле.** Код: [services/registry/src/jane_registry/settings.py:29](../../../../../../services/registry/src/jane_registry/settings.py#L29).

```python
db_url: SecretStr | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
PostgreSQL DSN of the registry's own database, e.g. ``postgresql://jane_registry:...@host/jane_registry``.
    Passed through the environment (``JANE_REGISTRY_DB_URL``) or a secrets file, never committed.
```

## jane_registry.settings.Settings.db_schema

**Поле.** Код: [services/registry/src/jane_registry/settings.py:32](../../../../../../services/registry/src/jane_registry/settings.py#L32).

```python
db_schema: str = Field(default='public', pattern='^[a-z_][a-z0-9_]{0,62}$')
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "'public'",
  "pattern": "'^[a-z_][a-z0-9_]{0,62}$'"
}
```

## jane_registry.settings.Settings.blob

**Поле.** Код: [services/registry/src/jane_registry/settings.py:35](../../../../../../services/registry/src/jane_registry/settings.py#L35).

```python
blob: Literal['s3', 'filesystem'] = 's3'
```

Доступ: читання — так; запис — так.

## jane_registry.settings.Settings.blob_bucket

**Поле.** Код: [services/registry/src/jane_registry/settings.py:36](../../../../../../services/registry/src/jane_registry/settings.py#L36).

```python
blob_bucket: str = 'jane-registry'
```

Доступ: читання — так; запис — так.

## jane_registry.settings.Settings.blob_prefix

**Поле.** Код: [services/registry/src/jane_registry/settings.py:37](../../../../../../services/registry/src/jane_registry/settings.py#L37).

```python
blob_prefix: str = 'sha256/'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Object key = ``<prefix><sha256 hex>`` (content-addressed).
```

## jane_registry.settings.Settings.blob_root

**Поле.** Код: [services/registry/src/jane_registry/settings.py:39](../../../../../../services/registry/src/jane_registry/settings.py#L39).

```python
blob_root: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``filesystem``: directory that plays the role of the bucket (``<root>/<bucket>/<prefix><hex>``).
```

## jane_registry.settings.Settings.s3_endpoint_url

**Поле.** Код: [services/registry/src/jane_registry/settings.py:41](../../../../../../services/registry/src/jane_registry/settings.py#L41).

```python
s3_endpoint_url: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
MinIO / S3-compatible endpoint (``http://127.0.0.1:9000``); empty for AWS S3.
```

## jane_registry.settings.Settings.s3_region

**Поле.** Код: [services/registry/src/jane_registry/settings.py:43](../../../../../../services/registry/src/jane_registry/settings.py#L43).

```python
s3_region: str = 'us-east-1'
```

Доступ: читання — так; запис — так.

## jane_registry.settings.Settings.s3_access_key

**Поле.** Код: [services/registry/src/jane_registry/settings.py:44](../../../../../../services/registry/src/jane_registry/settings.py#L44).

```python
s3_access_key: SecretStr | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.settings.Settings.s3_secret_key

**Поле.** Код: [services/registry/src/jane_registry/settings.py:45](../../../../../../services/registry/src/jane_registry/settings.py#L45).

```python
s3_secret_key: SecretStr | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.settings.Settings.s3_create_bucket

**Поле.** Код: [services/registry/src/jane_registry/settings.py:46](../../../../../../services/registry/src/jane_registry/settings.py#L46).

```python
s3_create_bucket: bool = True
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Create the bucket on start if it does not exist (dev stack).
```

## jane_registry.settings.Settings.contracts_dir

**Поле.** Код: [services/registry/src/jane_registry/settings.py:50](../../../../../../services/registry/src/jane_registry/settings.py#L50).

```python
contracts_dir: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Directory with ``schemas/package-manifest.schema.json`` etc.; default - ``contracts/`` of the
    checkout (env ``JANE_CONTRACTS_DIR``) or ``/app/contracts`` in the image.
```

## jane_registry.settings.Settings.runtime_profiles

**Поле.** Код: [services/registry/src/jane_registry/settings.py:53](../../../../../../services/registry/src/jane_registry/settings.py#L53).

```python
runtime_profiles: list[str] = Field(default_factory=list)
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
Sources of runtime profile descriptions (``dependencies.runtime_profile``) published by
    handler-runtime (WP-06): file paths or http(s) URLs. A source may be one profile document, a list of
    them, ``{"runtime_profiles": {...}}`` or a ``ServiceInfo`` (``GET <runtime>/v1/info``). JSON list in env:
    ``JANE_REGISTRY_RUNTIME_PROFILES='["/etc/jane/python-extractor-1.json"]'``.
```

## jane_registry.settings.Settings.require_tests

**Поле.** Код: [services/registry/src/jane_registry/settings.py:58](../../../../../../services/registry/src/jane_registry/settings.py#L58).

```python
require_tests: bool = True
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
extractor/llm packages need at least one ``success`` and one ``empty|unrecognized`` test
    (contracts/docs/handler-packages.md).
```

## jane_registry.settings.Settings.runtime_profiles_token_ref

**Поле.** Код: [services/registry/src/jane_registry/settings.py:64](../../../../../../services/registry/src/jane_registry/settings.py#L64).

```python
runtime_profiles_token_ref: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Secret reference (``env:VAR`` / ``file:/path``, ADR-0006) of the registry's own token for http(s)
    ``runtime_profiles`` sources: ``GET <runtime>/v1/info`` needs a valid token of the runtime.
```

## jane_registry.settings.PackageLimits

**Клас.** Код: [services/registry/src/jane_registry/settings.py:69](../../../../../../services/registry/src/jane_registry/settings.py#L69).

```python
class PackageLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_archive_bytes](jane_registry.settings.md#jane_registrysettingspackagelimitsmax_archive_bytes) | Поле | ні |
| [max_unpacked_bytes](jane_registry.settings.md#jane_registrysettingspackagelimitsmax_unpacked_bytes) | Поле | ні |
| [max_files](jane_registry.settings.md#jane_registrysettingspackagelimitsmax_files) | Поле | ні |
| [max_versions_per_package](jane_registry.settings.md#jane_registrysettingspackagelimitsmax_versions_per_package) | Поле | ні |
| [archive_cache_bytes](jane_registry.settings.md#jane_registrysettingspackagelimitsarchive_cache_bytes) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_registry.settings.PackageLimits.max_archive_bytes

**Поле.** Код: [services/registry/src/jane_registry/settings.py:70](../../../../../../services/registry/src/jane_registry/settings.py#L70).

```python
max_archive_bytes: int = Field(default=20 * 1024 * 1024, ge=1024)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "20 * 1024 * 1024",
  "ge": "1024"
}
```

### Опис із вихідного коду

```text
Largest accepted package archive (uploaded zip or canonical archive of a JSON publish).
```

## jane_registry.settings.PackageLimits.max_unpacked_bytes

**Поле.** Код: [services/registry/src/jane_registry/settings.py:72](../../../../../../services/registry/src/jane_registry/settings.py#L72).

```python
max_unpacked_bytes: int = Field(default=50 * 1024 * 1024, ge=1024)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "50 * 1024 * 1024",
  "ge": "1024"
}
```

### Опис із вихідного коду

```text
Sum of file sizes in one package.
```

## jane_registry.settings.PackageLimits.max_files

**Поле.** Код: [services/registry/src/jane_registry/settings.py:74](../../../../../../services/registry/src/jane_registry/settings.py#L74).

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

### Опис із вихідного коду

```text
Files in one package.
```

## jane_registry.settings.PackageLimits.max_versions_per_package

**Поле.** Код: [services/registry/src/jane_registry/settings.py:76](../../../../../../services/registry/src/jane_registry/settings.py#L76).

```python
max_versions_per_package: int = Field(default=1000, ge=1)
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
Published versions of one package; beyond -> 422 ``limit_exceeded``.
```

## jane_registry.settings.PackageLimits.archive_cache_bytes

**Поле.** Код: [services/registry/src/jane_registry/settings.py:78](../../../../../../services/registry/src/jane_registry/settings.py#L78).

```python
archive_cache_bytes: int = Field(default=64 * 1024 * 1024, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "64 * 1024 * 1024",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
In-process LRU of archives read from the blob store (per instance).
```

## jane_registry.settings.SecretScanLimits

**Клас.** Код: [services/registry/src/jane_registry/settings.py:82](../../../../../../services/registry/src/jane_registry/settings.py#L82).

```python
class SecretScanLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_scan_bytes_per_file](jane_registry.settings.md#jane_registrysettingssecretscanlimitsmax_scan_bytes_per_file) | Поле | ні |
| [min_entropy_token_length](jane_registry.settings.md#jane_registrysettingssecretscanlimitsmin_entropy_token_length) | Поле | ні |
| [scan_time_budget_ms](jane_registry.settings.md#jane_registrysettingssecretscanlimitsscan_time_budget_ms) | Поле | ні |
| [max_findings_per_file](jane_registry.settings.md#jane_registrysettingssecretscanlimitsmax_findings_per_file) | Поле | ні |
| [entropy_threshold](jane_registry.settings.md#jane_registrysettingssecretscanlimitsentropy_threshold) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_units.py:237](../../../../../../services/registry/tests/test_units.py#L237).

```python
limits = SecretScanLimits(max_scan_bytes_per_file=1024)
```

Контекст і передумови: [services/registry/tests/test_units.py:243](../../../../../../services/registry/tests/test_units.py#L243).

```python
limits = SecretScanLimits(max_findings_per_file=3)
```

## jane_registry.settings.SecretScanLimits.max_scan_bytes_per_file

**Поле.** Код: [services/registry/src/jane_registry/settings.py:83](../../../../../../services/registry/src/jane_registry/settings.py#L83).

```python
max_scan_bytes_per_file: int = Field(default=2 * 1024 * 1024, ge=1024)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "2 * 1024 * 1024",
  "ge": "1024"
}
```

### Опис із вихідного коду

```text
Largest file the secret scanner reads; a package with a larger file is rejected with
    422 ``limit_exceeded`` (it is never accepted unscanned).
```

## jane_registry.settings.SecretScanLimits.min_entropy_token_length

**Поле.** Код: [services/registry/src/jane_registry/settings.py:86](../../../../../../services/registry/src/jane_registry/settings.py#L86).

```python
min_entropy_token_length: int = Field(default=32, ge=8)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "32",
  "ge": "8"
}
```

### Опис із вихідного коду

```text
Shortest quoted/assigned token checked for high entropy.
```

## jane_registry.settings.SecretScanLimits.scan_time_budget_ms

**Поле.** Код: [services/registry/src/jane_registry/settings.py:88](../../../../../../services/registry/src/jane_registry/settings.py#L88).

```python
scan_time_budget_ms: int = Field(default=20000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "20000",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Wall time of scanning one package; beyond it the publish fails with 422 ``limit_exceeded``
    (a safeguard - the patterns themselves are linear).
```

## jane_registry.settings.SecretScanLimits.max_findings_per_file

**Поле.** Код: [services/registry/src/jane_registry/settings.py:91](../../../../../../services/registry/src/jane_registry/settings.py#L91).

```python
max_findings_per_file: int = Field(default=20, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "20",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
Findings reported per file (one is enough to reject; the cap keeps responses and scans small).
```

## jane_registry.settings.SecretScanLimits.entropy_threshold

**Поле.** Код: [services/registry/src/jane_registry/settings.py:93](../../../../../../services/registry/src/jane_registry/settings.py#L93).

```python
entropy_threshold: float = Field(default=4.3, gt=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "4.3",
  "gt": "0"
}
```

### Опис із вихідного коду

```text
Shannon entropy (bits per character) above which a mixed-alphabet token counts as a secret.
```

## jane_registry.settings.DiffLimits

**Клас.** Код: [services/registry/src/jane_registry/settings.py:97](../../../../../../services/registry/src/jane_registry/settings.py#L97).

```python
class DiffLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_context_lines](jane_registry.settings.md#jane_registrysettingsdifflimitsmax_context_lines) | Поле | ні |
| [max_diff_file_bytes](jane_registry.settings.md#jane_registrysettingsdifflimitsmax_diff_file_bytes) | Поле | ні |
| [max_merge_file_bytes](jane_registry.settings.md#jane_registrysettingsdifflimitsmax_merge_file_bytes) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_registry.settings.DiffLimits.max_context_lines

**Поле.** Код: [services/registry/src/jane_registry/settings.py:98](../../../../../../services/registry/src/jane_registry/settings.py#L98).

```python
max_context_lines: int = Field(default=50, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "50",
  "ge": "0"
}
```

### Опис із вихідного коду

```text
Upper bound for the ``context_lines`` query parameter (larger values are clamped).
```

## jane_registry.settings.DiffLimits.max_diff_file_bytes

**Поле.** Код: [services/registry/src/jane_registry/settings.py:100](../../../../../../services/registry/src/jane_registry/settings.py#L100).

```python
max_diff_file_bytes: int = Field(default=1024 * 1024, ge=1024)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1024 * 1024",
  "ge": "1024"
}
```

### Опис із вихідного коду

```text
Files larger than this get ``status`` only, without ``unified_diff``.
```

## jane_registry.settings.DiffLimits.max_merge_file_bytes

**Поле.** Код: [services/registry/src/jane_registry/settings.py:102](../../../../../../services/registry/src/jane_registry/settings.py#L102).

```python
max_merge_file_bytes: int = Field(default=1024 * 1024, ge=1024)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "1024 * 1024",
  "ge": "1024"
}
```

### Опис із вихідного коду

```text
Text files larger than this are not merged line by line in an upstream port (conflict if both sides
    changed them).
```

## jane_registry.settings.RequestLimits

**Клас.** Код: [services/registry/src/jane_registry/settings.py:107](../../../../../../services/registry/src/jane_registry/settings.py#L107).

```python
class RequestLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_request_body_bytes](jane_registry.settings.md#jane_registrysettingsrequestlimitsmax_request_body_bytes) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_registry.settings.RequestLimits.max_request_body_bytes

**Поле.** Код: [services/registry/src/jane_registry/settings.py:108](../../../../../../services/registry/src/jane_registry/settings.py#L108).

```python
max_request_body_bytes: int = contract_field('transfer.max_request_body_bytes', 30 * 1024 * 1024, ge=1024)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "contract_key": "'transfer.max_request_body_bytes'",
  "ge": "1024"
}
```

### Опис із вихідного коду

```text
Contract ``limits.transfer.max_request_body_bytes``: larger bodies -> 413 ``payload_too_large``.
```

## jane_registry.settings.ProfileLimits

**Клас.** Код: [services/registry/src/jane_registry/settings.py:112](../../../../../../services/registry/src/jane_registry/settings.py#L112).

```python
class ProfileLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [fetch_timeout_ms](jane_registry.settings.md#jane_registrysettingsprofilelimitsfetch_timeout_ms) | Поле | ні |
| [refresh_seconds](jane_registry.settings.md#jane_registrysettingsprofilelimitsrefresh_seconds) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_auth.py:72](../../../../../../services/registry/tests/test_auth.py#L72).

```python
source = ProfileSource(
        ["http://runtime.test/v1/info"],
        ProfileLimits(),
        transport=httpx.MockTransport(handler),
        token="k-reg",
    )
```

Контекст і передумови: [services/registry/tests/test_service_ops.py:95](../../../../../../services/registry/tests/test_service_ops.py#L95).

```python
source = ProfileSource(
        ["http://runtime.test/v1/info"], ProfileLimits(), transport=httpx.MockTransport(handler)
    )
```

## jane_registry.settings.ProfileLimits.fetch_timeout_ms

**Поле.** Код: [services/registry/src/jane_registry/settings.py:113](../../../../../../services/registry/src/jane_registry/settings.py#L113).

```python
fetch_timeout_ms: int = Field(default=5000, ge=1)
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
Timeout of reading a runtime profile from a URL.
```

## jane_registry.settings.ProfileLimits.refresh_seconds

**Поле.** Код: [services/registry/src/jane_registry/settings.py:115](../../../../../../services/registry/src/jane_registry/settings.py#L115).

```python
refresh_seconds: int = Field(default=300, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "300",
  "ge": "1"
}
```

### Опис із вихідного коду

```text
How long loaded profiles are reused before the sources are read again.
```

## jane_registry.settings.DbLimits

**Клас.** Код: [services/registry/src/jane_registry/settings.py:119](../../../../../../services/registry/src/jane_registry/settings.py#L119).

```python
class DbLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [pool_min_size](jane_registry.settings.md#jane_registrysettingsdblimitspool_min_size) | Поле | ні |
| [pool_max_size](jane_registry.settings.md#jane_registrysettingsdblimitspool_max_size) | Поле | ні |
| [connect_timeout_ms](jane_registry.settings.md#jane_registrysettingsdblimitsconnect_timeout_ms) | Поле | ні |
| [statement_timeout_ms](jane_registry.settings.md#jane_registrysettingsdblimitsstatement_timeout_ms) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_registry.settings.DbLimits.pool_min_size

**Поле.** Код: [services/registry/src/jane_registry/settings.py:120](../../../../../../services/registry/src/jane_registry/settings.py#L120).

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

## jane_registry.settings.DbLimits.pool_max_size

**Поле.** Код: [services/registry/src/jane_registry/settings.py:121](../../../../../../services/registry/src/jane_registry/settings.py#L121).

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

## jane_registry.settings.DbLimits.connect_timeout_ms

**Поле.** Код: [services/registry/src/jane_registry/settings.py:122](../../../../../../services/registry/src/jane_registry/settings.py#L122).

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

## jane_registry.settings.DbLimits.statement_timeout_ms

**Поле.** Код: [services/registry/src/jane_registry/settings.py:123](../../../../../../services/registry/src/jane_registry/settings.py#L123).

```python
statement_timeout_ms: int = Field(default=30000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "30000",
  "ge": "1"
}
```

## jane_registry.settings.BlobLimits

**Клас.** Код: [services/registry/src/jane_registry/settings.py:126](../../../../../../services/registry/src/jane_registry/settings.py#L126).

```python
class BlobLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [connect_timeout_ms](jane_registry.settings.md#jane_registrysettingsbloblimitsconnect_timeout_ms) | Поле | ні |
| [read_timeout_ms](jane_registry.settings.md#jane_registrysettingsbloblimitsread_timeout_ms) | Поле | ні |
| [max_attempts](jane_registry.settings.md#jane_registrysettingsbloblimitsmax_attempts) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

## jane_registry.settings.BlobLimits.connect_timeout_ms

**Поле.** Код: [services/registry/src/jane_registry/settings.py:127](../../../../../../services/registry/src/jane_registry/settings.py#L127).

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

## jane_registry.settings.BlobLimits.read_timeout_ms

**Поле.** Код: [services/registry/src/jane_registry/settings.py:128](../../../../../../services/registry/src/jane_registry/settings.py#L128).

```python
read_timeout_ms: int = Field(default=60000, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "60000",
  "ge": "1"
}
```

## jane_registry.settings.BlobLimits.max_attempts

**Поле.** Код: [services/registry/src/jane_registry/settings.py:129](../../../../../../services/registry/src/jane_registry/settings.py#L129).

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

### Опис із вихідного коду

```text
Attempts of one S3 request (botocore standard retry mode).
```

## jane_registry.settings.RecoveryLimits

**Клас.** Код: [services/registry/src/jane_registry/settings.py:133](../../../../../../services/registry/src/jane_registry/settings.py#L133).

```python
class RecoveryLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [in_progress_lease_ms](jane_registry.settings.md#jane_registrysettingsrecoverylimitsin_progress_lease_ms) | Поле | ні |
| [job_lease_ms](jane_registry.settings.md#jane_registrysettingsrecoverylimitsjob_lease_ms) | Поле | ні |
| [job_heartbeat_ms](jane_registry.settings.md#jane_registrysettingsrecoverylimitsjob_heartbeat_ms) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Recovery after an instance crash (several instances share PostgreSQL).
```

## jane_registry.settings.RecoveryLimits.in_progress_lease_ms

**Поле.** Код: [services/registry/src/jane_registry/settings.py:136](../../../../../../services/registry/src/jane_registry/settings.py#L136).

```python
in_progress_lease_ms: int = Field(default=120000, ge=1000)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "120000",
  "ge": "1000"
}
```

### Опис із вихідного коду

```text
An ``Idempotency-Key`` claimed by a request that has not finished is released after this lease, so a
    retry on another instance is not blocked by a crashed one.
```

## jane_registry.settings.RecoveryLimits.job_lease_ms

**Поле.** Код: [services/registry/src/jane_registry/settings.py:139](../../../../../../services/registry/src/jane_registry/settings.py#L139).

```python
job_lease_ms: int = Field(default=60000, ge=1000)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "60000",
  "ge": "1000"
}
```

### Опис із вихідного коду

```text
A running job belongs to its instance while the instance renews this lease; an expired lease makes
    the job ``failed`` with a retryable error.
```

## jane_registry.settings.RecoveryLimits.job_heartbeat_ms

**Поле.** Код: [services/registry/src/jane_registry/settings.py:142](../../../../../../services/registry/src/jane_registry/settings.py#L142).

```python
job_heartbeat_ms: int = Field(default=15000, ge=100)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "15000",
  "ge": "100"
}
```

### Опис із вихідного коду

```text
How often an instance renews the leases of its running jobs (must be below ``job_lease_ms``).
```

## jane_registry.settings.ServiceLimits

**Клас.** Код: [services/registry/src/jane_registry/settings.py:146](../../../../../../services/registry/src/jane_registry/settings.py#L146).

```python
class ServiceLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [jobs](jane_registry.settings.md#jane_registrysettingsservicelimitsjobs) | Поле | ні |
| [idempotency](jane_registry.settings.md#jane_registrysettingsservicelimitsidempotency) | Поле | ні |
| [pages](jane_registry.settings.md#jane_registrysettingsservicelimitspages) | Поле | ні |
| [packages](jane_registry.settings.md#jane_registrysettingsservicelimitspackages) | Поле | ні |
| [secrets](jane_registry.settings.md#jane_registrysettingsservicelimitssecrets) | Поле | ні |
| [diff](jane_registry.settings.md#jane_registrysettingsservicelimitsdiff) | Поле | ні |
| [requests](jane_registry.settings.md#jane_registrysettingsservicelimitsrequests) | Поле | ні |
| [profiles](jane_registry.settings.md#jane_registrysettingsservicelimitsprofiles) | Поле | ні |
| [db](jane_registry.settings.md#jane_registrysettingsservicelimitsdb) | Поле | ні |
| [blob](jane_registry.settings.md#jane_registrysettingsservicelimitsblob) | Поле | ні |
| [recovery](jane_registry.settings.md#jane_registrysettingsservicelimitsrecovery) | Поле | ні |
| [model_config](../../../../jane-kit/reference/types/generated/jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Limits of the registry. Contract names (``limits.schema.json``) where the limit exists there.
```

## jane_registry.settings.ServiceLimits.jobs

**Поле.** Код: [services/registry/src/jane_registry/settings.py:149](../../../../../../services/registry/src/jane_registry/settings.py#L149).

```python
jobs: JobLimits = JobLimits()
```

Доступ: читання — так; запис — так.

## jane_registry.settings.ServiceLimits.idempotency

**Поле.** Код: [services/registry/src/jane_registry/settings.py:150](../../../../../../services/registry/src/jane_registry/settings.py#L150).

```python
idempotency: IdempotencyLimits = IdempotencyLimits()
```

Доступ: читання — так; запис — так.

## jane_registry.settings.ServiceLimits.pages

**Поле.** Код: [services/registry/src/jane_registry/settings.py:151](../../../../../../services/registry/src/jane_registry/settings.py#L151).

```python
pages: PageLimits = PageLimits()
```

Доступ: читання — так; запис — так.

## jane_registry.settings.ServiceLimits.packages

**Поле.** Код: [services/registry/src/jane_registry/settings.py:152](../../../../../../services/registry/src/jane_registry/settings.py#L152).

```python
packages: PackageLimits = PackageLimits()
```

Доступ: читання — так; запис — так.

## jane_registry.settings.ServiceLimits.secrets

**Поле.** Код: [services/registry/src/jane_registry/settings.py:153](../../../../../../services/registry/src/jane_registry/settings.py#L153).

```python
secrets: SecretScanLimits = SecretScanLimits()
```

Доступ: читання — так; запис — так.

## jane_registry.settings.ServiceLimits.diff

**Поле.** Код: [services/registry/src/jane_registry/settings.py:154](../../../../../../services/registry/src/jane_registry/settings.py#L154).

```python
diff: DiffLimits = DiffLimits()
```

Доступ: читання — так; запис — так.

## jane_registry.settings.ServiceLimits.requests

**Поле.** Код: [services/registry/src/jane_registry/settings.py:155](../../../../../../services/registry/src/jane_registry/settings.py#L155).

```python
requests: RequestLimits = RequestLimits()
```

Доступ: читання — так; запис — так.

## jane_registry.settings.ServiceLimits.profiles

**Поле.** Код: [services/registry/src/jane_registry/settings.py:156](../../../../../../services/registry/src/jane_registry/settings.py#L156).

```python
profiles: ProfileLimits = ProfileLimits()
```

Доступ: читання — так; запис — так.

## jane_registry.settings.ServiceLimits.db

**Поле.** Код: [services/registry/src/jane_registry/settings.py:157](../../../../../../services/registry/src/jane_registry/settings.py#L157).

```python
db: DbLimits = DbLimits()
```

Доступ: читання — так; запис — так.

## jane_registry.settings.ServiceLimits.blob

**Поле.** Код: [services/registry/src/jane_registry/settings.py:158](../../../../../../services/registry/src/jane_registry/settings.py#L158).

```python
blob: BlobLimits = BlobLimits()
```

Доступ: читання — так; запис — так.

## jane_registry.settings.ServiceLimits.recovery

**Поле.** Код: [services/registry/src/jane_registry/settings.py:159](../../../../../../services/registry/src/jane_registry/settings.py#L159).

```python
recovery: RecoveryLimits = RecoveryLimits()
```

Доступ: читання — так; запис — так.

## jane_registry.settings.resolve_service_limits

**Функція.** Код: [services/registry/src/jane_registry/settings.py:162](../../../../../../services/registry/src/jane_registry/settings.py#L162).

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
Defaults <- platform file (``JANE_REGISTRY_LIMITS_FILE``) <- ``JANE_REGISTRY_LIMITS__*`` <- ``extra``.

The platform file may be a whole platform profile (``deploy/profiles/<profile>.json``): contract limits
the registry does not have are ignored (``ResolvedLimits.ignored``, start-up log); typos fail.
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_limits_profile.py:53](../../../../../../services/registry/tests/test_limits_profile.py#L53).

```python
resolved = resolve_service_limits(settings)
```
