# Модуль `jane_registry.settings`

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry/settings.py](../../../../../services/registry/src/jane_registry/settings.py). Не редагуйте вручну.

Settings and limits of the registry. Every limit has a safe default documented in README.md.

## Зміст

- [Клас `Settings`](#клас-settings)
- [Клас `PackageLimits`](#клас-packagelimits)
- [Клас `SecretScanLimits`](#клас-secretscanlimits)
- [Клас `DiffLimits`](#клас-difflimits)
- [Клас `RequestLimits`](#клас-requestlimits)
- [Клас `ProfileLimits`](#клас-profilelimits)
- [Клас `DbLimits`](#клас-dblimits)
- [Клас `BlobLimits`](#клас-bloblimits)
- [Клас `RecoveryLimits`](#клас-recoverylimits)
- [Клас `ServiceLimits`](#клас-servicelimits)
- [Функція `resolve_service_limits`](#функція-resolve_service_limits)

## Класи

### Клас `Settings`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_registry.settings` |
| Успадкування | `JaneSettings` |
| Код | [settings.py:19](../../../../../services/registry/src/jane_registry/settings.py#L19) |

```python
class Settings(JaneSettings): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `service_name` | `str` | `'registry'` | читання й запис |  |
| `port` | `int` | `8105` | читання й запис |  |
| `db` | `Literal['postgres', 'memory']` | `'postgres'` | читання й запис | ``postgres`` - own PostgreSQL database (``jane_registry``); ``memory`` - one process, no persistence (local experiments and fast tests only). |
| `db_url` | `SecretStr \| None` | `None` | читання й запис | PostgreSQL DSN of the registry's own database, e.g. ``postgresql://jane_registry:...@host/jane_registry``. Passed through the environment (``JANE_REGISTRY_DB_URL``) or a secrets file, never committed. |
| `db_schema` | `str` | `Field(default='public', pattern='^[a-z_][a-z0-9_]{0,62}$')` | читання й запис |  |
| `blob` | `Literal['s3', 'filesystem']` | `'s3'` | читання й запис |  |
| `blob_bucket` | `str` | `'jane-registry'` | читання й запис |  |
| `blob_prefix` | `str` | `'sha256/'` | читання й запис | Object key = ``<prefix><sha256 hex>`` (content-addressed). |
| `blob_root` | `Path \| None` | `None` | читання й запис | ``filesystem``: directory that plays the role of the bucket (``<root>/<bucket>/<prefix><hex>``). |
| `s3_endpoint_url` | `str \| None` | `None` | читання й запис | MinIO / S3-compatible endpoint (``http://127.0.0.1:9000``); empty for AWS S3. |
| `s3_region` | `str` | `'us-east-1'` | читання й запис |  |
| `s3_access_key` | `SecretStr \| None` | `None` | читання й запис |  |
| `s3_secret_key` | `SecretStr \| None` | `None` | читання й запис |  |
| `s3_create_bucket` | `bool` | `True` | читання й запис | Create the bucket on start if it does not exist (dev stack). |
| `contracts_dir` | `Path \| None` | `None` | читання й запис | Directory with ``schemas/package-manifest.schema.json`` etc.; default - ``contracts/`` of the checkout (env ``JANE_CONTRACTS_DIR``) or ``/app/contracts`` in the image. |
| `runtime_profiles` | `list[str]` | `Field(default_factory=list)` | читання й запис | Sources of runtime profile descriptions (``dependencies.runtime_profile``) published by handler-runtime (WP-06): file paths or http(s) URLs. A source may be one profile document, a list of them, ``{"runtime_profiles": {...}}`` or a ``ServiceInfo`` (``GET <runtime>/v1/info``). JSON list in env: ``JANE_REGISTRY_RUNTIME_PROFILES='["/etc/jane/python-extractor-1.json"]'``. |
| `require_tests` | `bool` | `True` | читання й запис | extractor/llm packages need at least one ``success`` and one ``empty\|unrecognized`` test (contracts/docs/handler-packages.md). |
| `runtime_profiles_token_ref` | `str \| None` | `None` | читання й запис | Secret reference (``env:VAR`` / ``file:/path``, ADR-0006) of the registry's own token for http(s) ``runtime_profiles`` sources: ``GET <runtime>/v1/info`` needs a valid token of the runtime. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `SettingsConfigDict(env_prefix=ENV_PREFIX, extra='ignore', env_nested_delimiter='` |  |

### Клас `PackageLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:69](../../../../../services/registry/src/jane_registry/settings.py#L69) |

```python
class PackageLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_archive_bytes` | `int` | `Field(default=20 * 1024 * 1024, ge=1024)` | читання й запис | Largest accepted package archive (uploaded zip or canonical archive of a JSON publish). |
| `max_unpacked_bytes` | `int` | `Field(default=50 * 1024 * 1024, ge=1024)` | читання й запис | Sum of file sizes in one package. |
| `max_files` | `int` | `Field(default=2000, ge=1)` | читання й запис | Files in one package. |
| `max_versions_per_package` | `int` | `Field(default=1000, ge=1)` | читання й запис | Published versions of one package; beyond -> 422 ``limit_exceeded``. |
| `archive_cache_bytes` | `int` | `Field(default=64 * 1024 * 1024, ge=0)` | читання й запис | In-process LRU of archives read from the blob store (per instance). |

### Клас `SecretScanLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:82](../../../../../services/registry/src/jane_registry/settings.py#L82) |

```python
class SecretScanLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_scan_bytes_per_file` | `int` | `Field(default=2 * 1024 * 1024, ge=1024)` | читання й запис | Largest file the secret scanner reads; a package with a larger file is rejected with 422 ``limit_exceeded`` (it is never accepted unscanned). |
| `min_entropy_token_length` | `int` | `Field(default=32, ge=8)` | читання й запис | Shortest quoted/assigned token checked for high entropy. |
| `scan_time_budget_ms` | `int` | `Field(default=20000, ge=1)` | читання й запис | Wall time of scanning one package; beyond it the publish fails with 422 ``limit_exceeded`` (a safeguard - the patterns themselves are linear). |
| `max_findings_per_file` | `int` | `Field(default=20, ge=1)` | читання й запис | Findings reported per file (one is enough to reject; the cap keeps responses and scans small). |
| `entropy_threshold` | `float` | `Field(default=4.3, gt=0)` | читання й запис | Shannon entropy (bits per character) above which a mixed-alphabet token counts as a secret. |

### Клас `DiffLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:97](../../../../../services/registry/src/jane_registry/settings.py#L97) |

```python
class DiffLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_context_lines` | `int` | `Field(default=50, ge=0)` | читання й запис | Upper bound for the ``context_lines`` query parameter (larger values are clamped). |
| `max_diff_file_bytes` | `int` | `Field(default=1024 * 1024, ge=1024)` | читання й запис | Files larger than this get ``status`` only, without ``unified_diff``. |
| `max_merge_file_bytes` | `int` | `Field(default=1024 * 1024, ge=1024)` | читання й запис | Text files larger than this are not merged line by line in an upstream port (conflict if both sides changed them). |

### Клас `RequestLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:107](../../../../../services/registry/src/jane_registry/settings.py#L107) |

```python
class RequestLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_request_body_bytes` | `int` | `contract_field('transfer.max_request_body_bytes', 30 * 1024 * 1024, ge=1024)` | читання й запис | Contract ``limits.transfer.max_request_body_bytes``: larger bodies -> 413 ``payload_too_large``. |

### Клас `ProfileLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:112](../../../../../services/registry/src/jane_registry/settings.py#L112) |

```python
class ProfileLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `fetch_timeout_ms` | `int` | `Field(default=5000, ge=1)` | читання й запис | Timeout of reading a runtime profile from a URL. |
| `refresh_seconds` | `int` | `Field(default=300, ge=1)` | читання й запис | How long loaded profiles are reused before the sources are read again. |

### Клас `DbLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:119](../../../../../services/registry/src/jane_registry/settings.py#L119) |

```python
class DbLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `pool_min_size` | `int` | `Field(default=1, ge=0)` | читання й запис |  |
| `pool_max_size` | `int` | `Field(default=10, ge=1)` | читання й запис |  |
| `connect_timeout_ms` | `int` | `Field(default=5000, ge=1)` | читання й запис |  |
| `statement_timeout_ms` | `int` | `Field(default=30000, ge=1)` | читання й запис |  |

### Клас `BlobLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:126](../../../../../services/registry/src/jane_registry/settings.py#L126) |

```python
class BlobLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `connect_timeout_ms` | `int` | `Field(default=5000, ge=1)` | читання й запис |  |
| `read_timeout_ms` | `int` | `Field(default=60000, ge=1)` | читання й запис |  |
| `max_attempts` | `int` | `Field(default=3, ge=1)` | читання й запис | Attempts of one S3 request (botocore standard retry mode). |

### Клас `RecoveryLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:133](../../../../../services/registry/src/jane_registry/settings.py#L133) |

```python
class RecoveryLimits(Limits): ...
```

Recovery after an instance crash (several instances share PostgreSQL).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `in_progress_lease_ms` | `int` | `Field(default=120000, ge=1000)` | читання й запис | An ``Idempotency-Key`` claimed by a request that has not finished is released after this lease, so a retry on another instance is not blocked by a crashed one. |
| `job_lease_ms` | `int` | `Field(default=60000, ge=1000)` | читання й запис | A running job belongs to its instance while the instance renews this lease; an expired lease makes the job ``failed`` with a retryable error. |
| `job_heartbeat_ms` | `int` | `Field(default=15000, ge=100)` | читання й запис | How often an instance renews the leases of its running jobs (must be below ``job_lease_ms``). |

### Клас `ServiceLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:146](../../../../../services/registry/src/jane_registry/settings.py#L146) |

```python
class ServiceLimits(Limits): ...
```

Limits of the registry. Contract names (``limits.schema.json``) where the limit exists there.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `jobs` | `JobLimits` | `JobLimits()` | читання й запис |  |
| `idempotency` | `IdempotencyLimits` | `IdempotencyLimits()` | читання й запис |  |
| `pages` | `PageLimits` | `PageLimits()` | читання й запис |  |
| `packages` | `PackageLimits` | `PackageLimits()` | читання й запис |  |
| `secrets` | `SecretScanLimits` | `SecretScanLimits()` | читання й запис |  |
| `diff` | `DiffLimits` | `DiffLimits()` | читання й запис |  |
| `requests` | `RequestLimits` | `RequestLimits()` | читання й запис |  |
| `profiles` | `ProfileLimits` | `ProfileLimits()` | читання й запис |  |
| `db` | `DbLimits` | `DbLimits()` | читання й запис |  |
| `blob` | `BlobLimits` | `BlobLimits()` | читання й запис |  |
| `recovery` | `RecoveryLimits` | `RecoveryLimits()` | читання й запис |  |

## Функції

### Функція `resolve_service_limits`

```python
def resolve_service_limits(
    settings: Settings,
    *extra: LimitLayer,
) -> ResolvedLimits[ServiceLimits]: ...
```

Defaults &lt;- platform file (``JANE_REGISTRY_LIMITS_FILE``) &lt;- ``JANE_REGISTRY_LIMITS__*`` &lt;- ``extra``.

The platform file may be a whole platform profile (``deploy/profiles/<profile>.json``): contract limits the registry does not have are ignored (``ResolvedLimits.ignored``, start-up log); typos fail.

Код: [settings.py:162](../../../../../services/registry/src/jane_registry/settings.py#L162).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `ENV_PREFIX` | — | `'JANE_REGISTRY_'` |  |
