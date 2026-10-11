# Модуль `jane_handler_runtime.settings`

> Згенеровано `scripts/docs_reference.py` з [services/handler-runtime/src/jane_handler_runtime/settings.py](../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py). Не редагуйте вручну.

Settings and limits of the service. Every limit has a safe default documented in README.md.

## Зміст

- [Клас `Settings`](#клас-settings)
- [Клас `SandboxLimits`](#клас-sandboxlimits)
- [Клас `TimeoutLimits`](#клас-timeoutlimits)
- [Клас `ConcurrencyLimits`](#клас-concurrencylimits)
- [Клас `PackageLimits`](#клас-packagelimits)
- [Клас `StateLimits`](#клас-statelimits)
- [Клас `ServiceLimits`](#клас-servicelimits)
- [Функція `request_layer`](#функція-request_layer)
- [Функція `resolve_service_limits`](#функція-resolve_service_limits)

## Класи

### Клас `Settings`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_handler_runtime.settings` |
| Успадкування | `JaneSettings` |
| Код | [settings.py:28](../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L28) |

```python
class Settings(JaneSettings): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `service_name` | `str` | `'handler-runtime'` | читання й запис |  |
| `sandbox_backend` | `Literal['docker', 'subprocess']` | `'docker'` | читання й запис | ``docker`` (default, ADR-0003) or ``subprocess`` - no isolation, trusted local packages only. |
| `allow_unsafe_subprocess` | `bool` | `False` | читання й запис | The ``subprocess`` backend refuses to run unless this is true (never in production). |
| `docker_host` | `str \| None` | `None` | читання й запис | Docker/Podman API endpoint; default: ``DOCKER_HOST`` or the platform socket / named pipe. |
| `docker_runtime` | `str \| None` | `None` | читання й запис | OCI runtime of sandbox containers, e.g. ``runsc`` (gVisor). |
| `sandbox_user` | `str` | `'65534:65534'` | читання й запис | Non-root uid:gid inside the sandbox. |
| `sandbox_labels` | `dict[str, str]` | `Field(default_factory=dict)` | читання й запис | Extra labels on sandbox containers (e.g. to find and clean them up in a test stack). |
| `profile_images` | `dict[str, str]` | `Field(default_factory=lambda: {DEFAULT_PROFILE: 'jane/python-extractor:1'})` | читання й запис | Runtime profile -> sandbox image (pin by digest in production: ``repo@sha256:...``). |
| `registry_url` | `str \| None` | `None` | читання й запис | Base URL of the handler repository (registry.v1); packages without ``package_archive`` come from it. |
| `registry_token` | `SecretStr \| None` | `None` | читання й запис | Bearer token for the registry (from the environment, never logged). |
| `package_cache_dir` | `Path \| None` | `None` | читання й запис | Where verified packages are cached by digest; default: a temporary directory. |
| `blob_roots` | `list[Path]` | `Field(default_factory=list)` | читання й запис | Directories from which ``file://`` blobs (package archives, material content) may be read. Empty = ``file://`` blobs are refused (the service must not read arbitrary host files). |
| `download_host_allowlist` | `list[str]` | `Field(default_factory=list)` | читання й запис | ``hostname`` (any port) or ``hostname:port`` a ContentRef ``download_url`` may point to (JSON list). Empty (default): downloads are refused. Redirects are never followed. |
| `state_dsn` | `SecretStr \| None` | `None` | читання й запис | PostgreSQL DSN of the service's own state (idempotency keys, jobs, results) shared by instances. Unset: in-memory state - only for a single standalone instance and the CLI (lost on restart). |
| `state_schema` | `str` | `Field(default='jane_handler_runtime', pattern='^[a-z_][a-z0-9_]{0,62}$')` | читання й запис | Schema of the state tables (created if missing). |
| `contracts_dir` | `Path \| None` | `None` | читання й запис | ``contracts/`` with the JSON Schemas; default: found upwards from the package (repo checkout). |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `SettingsConfigDict(env_prefix=ENV_PREFIX, extra='ignore', env_nested_delimiter='` |  |

### Клас `SandboxLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_handler_runtime.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:77](../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L77) |

```python
class SandboxLimits(Limits): ...
```

``limits.sandbox`` of the contract (ADR-0003).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `cpu_cores` | `float` | `Field(default=1.0, gt=0)` | читання й запис |  |
| `memory_mb` | `int` | `Field(default=512, ge=16)` | читання й запис |  |
| `wall_time_ms` | `int` | `Field(default=30000, ge=1)` | читання й запис |  |
| `max_output_bytes` | `int` | `Field(default=4194304, ge=1)` | читання й запис |  |
| `max_processes` | `int` | `Field(default=16, ge=1)` | читання й запис |  |
| `tmpfs_mb` | `int` | `Field(default=64, ge=0)` | читання й запис |  |

### Клас `TimeoutLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_handler_runtime.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:88](../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L88) |

```python
class TimeoutLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `invocation_timeout_ms` | `int` | `contract_field('timeouts.invocation_timeout_ms', 60000, ge=1)` | читання й запис |  |
| `sync_response_max_ms` | `int` | `contract_field('timeouts.sync_response_max_ms', 25000, ge=1)` | читання й запис |  |
| `request_timeout_ms` | `int` | `contract_field('timeouts.request_timeout_ms', 30000, ge=1)` | читання й запис | Registry calls and blob downloads (a whole ``download_url`` download, connection included). |

### Клас `ConcurrencyLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_handler_runtime.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:95](../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L95) |

```python
class ConcurrencyLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_parallel_invocations` | `int` | `contract_field('concurrency.max_parallel_invocations', 2, ge=1)` | читання й запис | Sandboxes running at the same time in one instance. |

### Клас `PackageLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_handler_runtime.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:100](../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L100) |

```python
class PackageLimits(Limits): ...
```

Service-specific bounds for untrusted package archives and inputs (not in the contract).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_archive_bytes` | `int` | `Field(default=50 * 2 ** 20, ge=1)` | читання й запис |  |
| `max_unpacked_bytes` | `int` | `Field(default=200 * 2 ** 20, ge=1)` | читання й запис |  |
| `max_files` | `int` | `Field(default=5000, ge=1)` | читання й запис |  |
| `cache_max_entries` | `int` | `Field(default=64, ge=1)` | читання й запис |  |
| `max_input_bytes` | `int` | `Field(default=64 * 2 ** 20, ge=1)` | читання й запис | Content of one material (inline or blob). |
| `max_stored_results` | `int` | `Field(default=10000, ge=1)` | читання й запис | ``GET /v1/invocations/{id}`` keeps at most this many results (in memory, per instance). |
| `docker_api_timeout_ms` | `int` | `Field(default=60000, ge=1)` | читання й запис |  |
| `max_stderr_in_result_bytes` | `int` | `Field(default=16000, ge=0)` | читання й запис | Tail of the sandbox stderr put into ``diagnostics.logs_ref`` (inline). |
| `unavailable_retry_after_seconds` | `int` | `Field(default=5, ge=0)` | читання й запис | ``Retry-After`` of 503 when the container engine is not reachable. |
| `kill_grace_ms` | `int` | `Field(default=2000, ge=0)` | читання й запис | In-container ``timeout -s KILL`` fires at wall_time_ms + this (safety net if the runtime dies). |

### Клас `StateLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_handler_runtime.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:120](../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L120) |

```python
class StateLimits(Limits): ...
```

Shared PostgreSQL state (``state_dsn``).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `pool_max_size` | `int` | `Field(default=10, ge=1)` | читання й запис |  |
| `connect_timeout_ms` | `int` | `Field(default=10000, ge=1)` | читання й запис |  |
| `in_progress_lease_ms` | `int` | `Field(default=900000, ge=1)` | читання й запис | An in-progress idempotency claim of a crashed instance can be taken over after this. |
| `job_lease_ms` | `int` | `Field(default=30000, ge=1)` | читання й запис | A job whose owner stops renewing this lease is marked failed when read. |
| `heartbeat_interval_ms` | `int` | `Field(default=5000, ge=1)` | читання й запис | How often this instance renews leases for its unfinished jobs. |

### Клас `ServiceLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_handler_runtime.settings` |
| Успадкування | `Limits` |
| Код | [settings.py:133](../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L133) |

```python
class ServiceLimits(Limits): ...
```

Limits of this service. Contract names (``limits.schema.json``) where the limit exists there.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `sandbox` | `SandboxLimits` | `contract_field('sandbox', SandboxLimits())` | читання й запис |  |
| `timeouts` | `TimeoutLimits` | `TimeoutLimits()` | читання й запис |  |
| `concurrency` | `ConcurrencyLimits` | `ConcurrencyLimits()` | читання й запис |  |
| `packages` | `PackageLimits` | `PackageLimits()` | читання й запис |  |
| `state` | `StateLimits` | `StateLimits()` | читання й запис |  |
| `jobs` | `JobLimits` | `JobLimits()` | читання й запис |  |
| `idempotency` | `IdempotencyLimits` | `IdempotencyLimits()` | читання й запис |  |

## Функції

### Функція `request_layer`

```python
def request_layer(limits: Mapping[str, Any] | None) -> LimitLayer | None: ...
```

``HandlerInvocation.limits`` -> request layer with only the fields this service models.

Код: [settings.py:192](../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L192).

### Функція `resolve_service_limits`

```python
def resolve_service_limits(
    settings: Settings,
    *extra: LimitLayer | None,
) -> ResolvedLimits[ServiceLimits]: ...
```

Defaults &lt;- service default caps &lt;- platform file (``..._LIMITS_FILE``) &lt;- ``JANE_HANDLER_RUNTIME_LIMITS__*`` &lt;- ``extra`` (request layer). Values above a hard cap are clamped (``min(request, hard_caps)``).

The platform file may be a whole platform profile (``deploy/profiles/<profile>.json``): contract limits the runtime does not have are ignored (``ResolvedLimits.ignored``, start-up log); typos fail.

Код: [settings.py:203](../../../../../services/handler-runtime/src/jane_handler_runtime/settings.py#L203).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `ENV_PREFIX` | — | `'JANE_HANDLER_RUNTIME_'` |  |
| `DEFAULT_PROFILE` | — | `'python-extractor@1'` |  |
| `DEFAULT_HARD_CAPS` | `dict[str, Any]` | `{'sandbox': {'cpu_cores': 4.0, 'memory_mb': 4096, 'wall_time_ms': 600000, 'max_o` | Service-level ceilings for values a request may ask for (a request can never raise a limit above these). A platform file or env hard cap for the same field replaces the default. |
| `REQUEST_GROUPS` | — | `('sandbox', 'timeouts')` | Groups of ``HandlerInvocation.limits`` this service applies (other groups belong to other services). |
