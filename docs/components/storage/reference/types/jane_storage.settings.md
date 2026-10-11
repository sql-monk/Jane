# Модуль `jane_storage.settings`

> Згенеровано `scripts/docs_reference.py` з [services/storage/src/jane_storage/settings.py](../../../../../services/storage/src/jane_storage/settings.py). Не редагуйте вручну.

Settings and limits of the service. Every limit has a safe default documented in README.md.

## Зміст

- [Клас `Settings`](#клас-settings)
- [Клас `Timeouts`](#клас-timeouts)
- [Клас `Transfer`](#клас-transfer)
- [Клас `Objects`](#клас-objects)
- [Клас `Adapters`](#клас-adapters)
- [Клас `ConflictRetries`](#клас-conflictretries)
- [Клас `Invocations`](#клас-invocations)
- [Клас `PackageLimits`](#клас-packagelimits)
- [Клас `ServiceLimits`](#клас-servicelimits)
- [Функція `resolve_service_limits`](#функція-resolve_service_limits)

## Класи

### Клас `Settings`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_storage.settings` |
| Успадкування | `JaneSettings` |
| Код | [settings.py:32](../../../../../services/storage/src/jane_storage/settings.py#L32) |

```python
class Settings(JaneSettings): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `service_name` | `str` | `'storage'` | читання й запис |  |
| `port` | `int` | `8107` | читання й запис |  |
| `connections_file` | `Path \| None` | `None` | читання й запис | JSON/YAML with ``{"connections": [Connection, ...]}`` (secret values only as ``secret_refs``). |
| `transit_connection_id` | `str \| None` | `None` | читання й запис | Connection (kind ``s3``/``minio``) used to read ``s3://`` blobs of materials (ADR-0004). |
| `package_dirs` | `list[Path]` | `Field(default_factory=list)` | читання й запис | Extra storage package directories besides the installed adapter distributions. |
| `validate_requests` | `bool` | `True` | читання й запис | Validate invocations against ``contracts/schemas`` when the contracts directory is available. |
| `secret_env_prefix` | `str` | `'JANE_SECRET_'` | читання й запис | ``env:`` secret references may name only variables with this prefix (empty: ``env:`` disabled). |
| `secret_files_dir` | `Path \| None` | `Path('/run/secrets')` | читання й запис | ``file:`` secret references must point inside this directory (empty: ``file:`` disabled). |
| `connection_host_allowlist` | `list[str]` | `Field(default_factory=list)` | читання й запис | ``hostname`` / ``hostname:port`` a connection may contact (JSON list); default none: connections with a network address are rejected. |
| `content_files_dir` | `Path \| None` | `None` | читання й запис | Only ``file:///`` ContentRef blobs below this directory may be read; None disables local blobs. |
| `transit_dir` | `Path \| None` | `None` | читання й запис | Transit blob store of this service (ADR-0004, R18): a RAW larger than ``transfer.inline_max_bytes`` whose adapter has no persistent URI is returned by ``GET /v1/objects/{id}`` as a transit ``file://`` blob written under ``<transit_dir>/storage/`` (kept ``transfer.transit_ttl_seconds``, removed by this service). The consumers read it within their ``BLOB_ROOTS``; this service also reads its own transit blobs. None: such a RAW has no ``material``. |
| `download_host_allowlist` | `list[str]` | `Field(default_factory=list)` | читання й запис | ``hostname`` or ``hostname:port`` allowed for ContentRef download_url; empty disables downloads. |
| `registry_url` | `str \| None` | `None` | читання й запис | Base URL of the handler registry (``registry.v1``, e.g. ``http://registry:8000``): a storage package that is neither built in nor given as ``package_archive`` is downloaded from it (ADR-0009 §4). Operator configuration only (never taken from a request); empty: no registry, such a package is ``404 not_found``. |
| `registry_token` | `SecretStr \| None` | `None` | читання й запис | Bearer token for the registry (environment only; never logged, sent only to ``registry_url``). Not an ``env:JANE_SECRET_*`` variable, so a connection's ``secret_refs`` cannot reference it. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `SettingsConfigDict(env_prefix=ENV_PREFIX, extra='ignore', env_nested_delimiter='` |  |

#### Метод `Settings.connection_policy`

```python
def connection_policy(self) -> ConnectionPolicy: ...
```

Код: [settings.py:91](../../../../../services/storage/src/jane_storage/settings.py#L91).

### Клас `Timeouts`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:99](../../../../../services/storage/src/jane_storage/settings.py#L99) |

```python
class Timeouts(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `sync_response_max_ms` | `int` | `contract_field('timeouts.sync_response_max_ms', 30000, ge=1)` | читання й запис | Contract ``limits.timeouts.sync_response_max_ms``: a sync invocation not done by then → 202 + Job. |
| `request_timeout_ms` | `int` | `contract_field('timeouts.request_timeout_ms', 30000, ge=1)` | читання й запис | Reading blob content (``download_url``, ``s3://``). |

### Клас `Transfer`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:106](../../../../../services/storage/src/jane_storage/settings.py#L106) |

```python
class Transfer(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_request_body_bytes` | `int` | `contract_field('transfer.max_request_body_bytes', 16 * 1024 * 1024, ge=1)` | читання й запис | Contract ``limits.transfer.max_request_body_bytes``: larger bodies → 413 (send blobs instead). |
| `inline_max_bytes` | `int` | `contract_field('transfer.inline_max_bytes', 1024 * 1024, ge=0)` | читання й запис | Contract ``limits.transfer.inline_max_bytes``: stored content up to this size is returned inline in ``GET /v1/objects/{id}`` when the adapter has no persistent URI for it. |
| `transit_ttl_seconds` | `int` | `contract_field('transfer.transit_ttl_seconds', 604800, ge=60)` | читання й запис | Contract ``limits.transfer.transit_ttl_seconds``: how long a transit blob of this service is kept. |
| `transit_cleanup_interval_seconds` | `int` | `Field(default=600, ge=1)` | читання й запис | How often this service removes its expired transit blobs (``transit_dir``). |

### Клас `Objects`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:118](../../../../../services/storage/src/jane_storage/settings.py#L118) |

```python
class Objects(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_object_bytes` | `int` | `Field(default=100 * 1024 * 1024, ge=1)` | читання й запис | Largest RAW / result document the service stores (content read into memory). |
| `max_filter_material_ids` | `int` | `Field(default=200, ge=1)` | читання й запис | Most ``material_id`` values one ``GET /v1/objects`` may filter by (``material_id`` + ``material_ids``). |

### Клас `Adapters`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:125](../../../../../services/storage/src/jane_storage/settings.py#L125) |

```python
class Adapters(Limits): ...
```

Options passed to every adapter's ``open`` (each adapter uses the ones it knows).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `lock_timeout_ms` | `int` | `Field(default=30000, ge=1)` | читання й запис |  |
| `lock_stale_ms` | `int` | `Field(default=120000, ge=1)` | читання й запис |  |
| `lock_poll_ms` | `int` | `Field(default=10, ge=1)` | читання й запис |  |
| `replace_retry_ms` | `int` | `Field(default=5000, ge=0)` | читання й запис |  |
| `pool_min_size` | `int` | `Field(default=1, ge=0)` | читання й запис |  |
| `pool_max_size` | `int` | `Field(default=10, ge=1)` | читання й запис |  |
| `connect_timeout_ms` | `int` | `Field(default=10000, ge=1)` | читання й запис |  |
| `command_timeout_ms` | `int` | `Field(default=30000, ge=1)` | читання й запис |  |
| `chunk_bytes` | `int \| None` | `Field(default=None, ge=1)` | читання й запис | MongoDB: size of one RAW chunk document for every connection that does not set ``params.chunk_bytes`` (unset: the adapter's own default, 4 MiB; the adapter rejects values above 15 MiB). |
| `retry_max_attempts` | `int \| None` | `Field(default=None, ge=1)` | читання й запис | MinIO/S3: botocore attempts per request for every connection that does not set ``params.retry_max_attempts`` (unset: the adapter's own default, 3). |

### Клас `ConflictRetries`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.settings` |
| Успадкування | `RetryPolicy` |
| Код | [settings.py:149](../../../../../services/storage/src/jane_storage/settings.py#L149) |

```python
class ConflictRetries(RetryPolicy): ...
```

Retries of the core on ``CONFLICT`` (a concurrent writer changed the entity version first).

Not the contract ``limits.retries``: that policy is the caller's (re-sending a request with the same ``Idempotency-Key``), so neither a platform profile nor ``HandlerInvocation.limits`` changes this backoff. The defaults are those that applied before the split (``RetryPolicy`` of jane-kit).

### Клас `Invocations`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:157](../../../../../services/storage/src/jane_storage/settings.py#L157) |

```python
class Invocations(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_results_in_memory` | `int` | `Field(default=10000, ge=1)` | читання й запис | How many recent HandlerResults ``GET /v1/invocations/{id}`` keeps (per instance). |

### Клас `PackageLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:162](../../../../../services/storage/src/jane_storage/settings.py#L162) |

```python
class PackageLimits(Limits): ...
```

Storage packages that are not built in: ``package_archive`` and registry downloads (untrusted archives).

The size defaults equal the registry's own ``packages`` limits, so every version it accepts can be loaded.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_archive_bytes` | `int` | `Field(default=20 * 1024 * 1024, ge=1)` | читання й запис | Largest package archive; a registry download stops as soon as it is passed. |
| `max_unpacked_bytes` | `int` | `Field(default=50 * 1024 * 1024, ge=1)` | читання й запис | Total size of the files of one package. |
| `max_files` | `int` | `Field(default=2000, ge=1)` | читання й запис |  |
| `cache_max_entries` | `int` | `Field(default=128, ge=1)` | читання й запис | Registry packages kept in memory per instance (LRU by digest). |
| `registry_connect_timeout_ms` | `int` | `Field(default=5000, ge=1)` | читання й запис |  |
| `registry_request_timeout_ms` | `int` | `Field(default=30000, ge=1)` | читання й запис | Whole archive download from the registry (connect + response + body). |

#### Метод `PackageLimits.archive_limits`

```python
def archive_limits(self) -> ArchiveLimits: ...
```

Код: [settings.py:178](../../../../../services/storage/src/jane_storage/settings.py#L178).

### Клас `ServiceLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:182](../../../../../services/storage/src/jane_storage/settings.py#L182) |

```python
class ServiceLimits(Limits): ...
```

Limits of this service. Contract names (``limits.schema.json``) where the limit exists there.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `jobs` | `JobLimits` | `JobLimits()` | читання й запис |  |
| `idempotency` | `IdempotencyLimits` | `IdempotencyLimits()` | читання й запис |  |
| `conflict_retries` | `ConflictRetries` | `ConflictRetries()` | читання й запис | Retries of the core on ``CONFLICT`` (``JANE_STORAGE_LIMITS__CONFLICT_RETRIES__*``); the contract ``limits.retries`` of a profile or an invocation is not used by storage (it is the caller's policy). |
| `timeouts` | `Timeouts` | `Timeouts()` | читання й запис |  |
| `transfer` | `Transfer` | `Transfer()` | читання й запис |  |
| `objects` | `Objects` | `Objects()` | читання й запис |  |
| `adapters` | `Adapters` | `Adapters()` | читання й запис |  |
| `pages` | `PageLimits` | `PageLimits()` | читання й запис |  |
| `invocations` | `Invocations` | `Invocations()` | читання й запис |  |
| `packages` | `PackageLimits` | `PackageLimits()` | читання й запис |  |

## Функції

### Функція `resolve_service_limits`

```python
def resolve_service_limits(
    settings: Settings,
    *extra: LimitLayer,
) -> ResolvedLimits[ServiceLimits]: ...
```

Defaults &lt;- platform file (``..._LIMITS_FILE``) &lt;- ``JANE_STORAGE_LIMITS__*`` &lt;- ``extra`` (request layer from ``HandlerInvocation.limits``).

The platform file may be a whole platform profile (``deploy/profiles/<profile>.json``): contract limits storage does not have are ignored (``ResolvedLimits.ignored``, start-up log); typos fail. The old ``JANE_STORAGE_LIMITS__RETRIES__*`` (and ``HARD_CAPS__RETRIES__*``) still configure the CONFLICT retries, with a deprecation warning (:func:`_legacy_retries`).

Код: [settings.py:227](../../../../../services/storage/src/jane_storage/settings.py#L227).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `ENV_PREFIX` | — | `'JANE_STORAGE_'` |  |
| `LEGACY_RETRIES` | — | `'retries'` | Before WP-17 the core's CONFLICT retries were ``limits.retries``; in the service's own (non-shared) layers the old group is a deprecated alias of ``conflict_retries`` (``JANE_STORAGE_LIMITS__RETRIES__*``). |
| `log` | — | `logging.getLogger(__name__)` |  |
| `CONNECTION_FIRST_OPTIONS` | — | `frozenset({'chunk_bytes', 'retry_max_attempts'})` | Service-wide adapter defaults that a connection's own ``params`` override (the other ``adapters.*`` options are applied over the connection params). |
