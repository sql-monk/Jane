# Модуль `jane_kit.config`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/config.py](../../../../../libs/jane-kit/src/jane_kit/config.py). Не редагуйте вручну.

Service settings and limits inherited across levels: platform -> source -> task -> stage (-> request).

Follows ``contracts/schemas/common/limits.schema.json`` (WP-00):

* Every numeric limit lives in a :class:`Limits` model of the service and **must** declare a safe default there (those defaults are the service's platform defaults); code never hard-codes a limit.
* A layer overrides any subset of fields (deep merge); a missing field is inherited; ``null`` is not a value (to inherit, omit the field).
* ``hard_caps`` (platform level; a more specific layer may only tighten them) bound every value after merging: effective = min(value, hard cap).
* The result keeps the provenance of every leaf (``EffectiveLimits`` in the contract).

Files: a platform file has the ``PlatformLimits`` shape ``{"profile", "defaults", "hard_caps"}`` (TOML/JSON/YAML); other levels are plain Limits objects. Environment variables: ``<PREFIX>CRAWL__MAX_DEPTH=5`` (value), ``<PREFIX>HARD_CAPS__CRAWL__MAX_DEPTH=10`` (hard cap).

A platform file is one profile shared by all services (ТЗ §12, criterion 13), so its layer is ``shared``: a path of the contract (:data:`CONTRACT_LIMIT_PATHS`) goes to the model fields that declare it (:func:`contract_field`, or a field at the same path), a contract path no field declares is ignored and recorded in :attr:`ResolvedLimits.ignored`, and a path unknown to both the model and the contract (a typo) is still a :class:`LimitError`. Other layers (env, source, task, request) accept model paths only.

## Зміст

- [Клас `JaneSettings`](#клас-janesettings)
- [Клас `LimitError`](#клас-limiterror)
- [Клас `LimitLayer`](#клас-limitlayer)
- [Клас `Limits`](#клас-limits)
- [Клас `ResolvedLimits`](#клас-resolvedlimits)
- [Функція `contract_field`](#функція-contract_field)
- [Функція `layer_from_env`](#функція-layer_from_env)
- [Функція `load_layer`](#функція-load_layer)
- [Функція `resolve_limits`](#функція-resolve_limits)

## Класи

### Клас `JaneSettings`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_kit.config` |
| Успадкування | `BaseSettings`, `AuthSettings` |
| Код | [config.py:497](../../../../../libs/jane-kit/src/jane_kit/config.py#L497) |

```python
class JaneSettings(BaseSettings, AuthSettings): ...
```

Common process settings. A service subclasses it and sets its own ``env_prefix``.

Only process-level knobs live here; operational limits belong in a :class:`Limits` model. Authentication fields (``auth_mode``, ``api_keys``, ``jwt_*``...) come from :class:`jane_kit.auth.AuthSettings` (ADR-0005); ``create_app`` enforces them.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `service_name` | `str` | `'jane-service'` | читання й запис |  |
| `instance_id` | `str` | `Field(default_factory=lambda: f'{socket.gethostname()}-{os.getpid()}-{uuid.uuid4` | читання й запис | Unique to this process start, including a restart that reuses the container hostname and PID. |
| `host` | `str` | `'127.0.0.1'` | читання й запис |  |
| `port` | `int` | `8000` | читання й запис |  |
| `log_level` | `str` | `'INFO'` | читання й запис |  |
| `log_format` | `Literal['json', 'console']` | `'json'` | читання й запис |  |
| `metrics_enabled` | `bool` | `True` | читання й запис |  |
| `health_check_timeout_ms` | `int` | `Field(default=2000, ge=1)` | читання й запис | Time box of every ``/v1/health`` check (env ``<PREFIX>HEALTH_CHECK_TIMEOUT_MS``). |
| `limits_file` | `Path \| None` | `None` | читання й запис | Platform limits file (``PlatformLimits`` shape, e.g. a whole ``deploy/profiles/<profile>.json``: limits this service does not have are ignored, typos are errors); env ``<PREFIX>LIMITS__*`` overrides it. |
| `operations_dir` | `Path \| None` | `None` | читання й запис | Own durable telemetry/configuration directory; default .jane/operations/&lt;service>. |
| `operations_sample_interval_seconds` | `float` | `Field(default=5, ge=1, le=300)` | читання й запис |  |
| `operations_retention_seconds` | `int` | `Field(default=86400, ge=60, le=604800)` | читання й запис |  |
| `operations_max_points` | `int` | `Field(default=720, ge=2, le=10000)` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `SettingsConfigDict(env_prefix='JANE_', extra='ignore', env_nested_delimiter='__'` |  |

#### Метод `JaneSettings.model_post_init`

```python
def model_post_init(self, context: Any) -> None: ...
```

Код: [config.py:529](../../../../../libs/jane-kit/src/jane_kit/config.py#L529).

#### Метод `JaneSettings.validate_configuration`

```python
def validate_configuration(self, values: dict[str, Any]) -> Self: ...
```

Код: [config.py:545](../../../../../libs/jane-kit/src/jane_kit/config.py#L545).

#### Метод `JaneSettings.platform_layers`

```python
def platform_layers(self, env_prefix: str = 'JANE_LIMITS__') -> list[LimitLayer]: ...
```

Platform layers in order: limits file, then environment overrides.

Код: [config.py:552](../../../../../libs/jane-kit/src/jane_kit/config.py#L552).

#### Метод `JaneSettings.with_overrides`

```python
def with_overrides(self, **values: Any) -> Self: ...
```

Код: [config.py:567](../../../../../libs/jane-kit/src/jane_kit/config.py#L567).

### Клас `LimitError`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_kit.config` |
| Успадкування | `ValueError` |
| Код | [config.py:127](../../../../../libs/jane-kit/src/jane_kit/config.py#L127) |

```python
class LimitError(ValueError): ...
```

Invalid limit configuration (unknown field, wrong type, loosened hard cap).

### Клас `LimitLayer`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_kit.config` |
| Код | [config.py:152](../../../../../libs/jane-kit/src/jane_kit/config.py#L152) |

```python
@dataclass(frozen=True)
class LimitLayer: ...
```

One level of configuration (platform, source ``shop``, task ``prices``, stage ``extract``...).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `level` | `str` | — | читання |  |
| `values` | `Mapping[str, Any]` | `field(default_factory=dict)` | читання |  |
| `hard_caps` | `Mapping[str, Any]` | `field(default_factory=dict)` | читання |  |
| `name` | `str \| None` | `None` | читання |  |
| `profile` | `str \| None` | `None` | читання |  |
| `shared` | `bool` | `False` | читання | Contract-shaped document shared by all services (a platform file): contract paths map to the fields that declare them, contract paths the model does not declare are ignored (``ResolvedLimits.ignored``). Paths unknown to the contract and to the model are still rejected. |
| `label` | `str` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `Limits`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_kit.config` |
| Успадкування | `BaseModel` |
| Код | [config.py:131](../../../../../libs/jane-kit/src/jane_kit/config.py#L131) |

```python
class Limits(BaseModel): ...
```

Base class for a service's limits. Subclasses must give every field a default.

Use the field names of ``limits.schema.json`` where the limit exists there (``timeouts.request_timeout_ms``, ``transfer.idempotency_ttl_seconds``...). Nested groups are fields whose type is another :class:`Limits` subclass with a default instance.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `ConfigDict(extra='forbid', frozen=True, validate_default=True)` |  |

### Клас `ResolvedLimits`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_kit.config` |
| Код | [config.py:171](../../../../../libs/jane-kit/src/jane_kit/config.py#L171) |

```python
@dataclass(frozen=True)
class ResolvedLimits: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `limits` | `L` | — | читання |  |
| `origin` | `dict[str, str]` | — | читання | Dotted leaf path -> label of the layer that set it (``default`` = the model's default). |
| `clamped` | `dict[str, str]` | — | читання | Dotted leaf path -> label of the layer whose hard cap reduced the value. |
| `hard_caps` | `dict[str, Any]` | `field(default_factory=dict)` | читання | Dotted leaf path -> effective hard cap (the tightest one of all layers). |
| `profile` | `str \| None` | `None` | читання | Name of the platform limits profile, if a PlatformLimits file declared one. |
| `ignored` | `dict[str, str]` | `field(default_factory=dict)` | читання | Contract path -> label of the shared layer whose value was not applied: this service has no such limit. |
| `ignored_hard_caps` | `dict[str, str]` | `field(default_factory=dict)` | читання |  |
| `module_baseline` | `dict[str, Any]` | `field(default_factory=dict)` | читання | Same for ``hard_caps`` of shared layers. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `ResolvedLimits.platform_limits`

```python
def platform_limits(self) -> dict[str, Any]: ...
```

``PlatformLimits`` document for ``/v1/info`` (WP-00 ``ServiceInfo.limits``).

Only fields that map to ``limits.schema.json`` (declared with :func:`contract_field` or nested under a group with a contract path) are included; service-specific limits stay internal because the contract schema is strict (``additionalProperties: false``).

Код: [config.py:187](../../../../../libs/jane-kit/src/jane_kit/config.py#L187).

#### Метод `ResolvedLimits.provenance`

```python
def provenance(self) -> dict[str, str]: ...
```

Leaf path -> contract ``LimitLevel`` (model defaults count as ``platform``).

Код: [config.py:205](../../../../../libs/jane-kit/src/jane_kit/config.py#L205).

#### Метод `ResolvedLimits.effective`

```python
def effective(self) -> dict[str, Any]: ...
```

``EffectiveLimits`` document: ``{"limits": {...}, "provenance": {...}}``.

Код: [config.py:217](../../../../../libs/jane-kit/src/jane_kit/config.py#L217).

#### Метод `ResolvedLimits.explain`

```python
def explain(self) -> list[tuple[str, Any, str]]: ...
```

Rows ``(path, value, origin)`` for logs and diagnostics.

Код: [config.py:221](../../../../../libs/jane-kit/src/jane_kit/config.py#L221).

## Функції

### Функція `contract_field`

```python
def contract_field(path: str, default: Any, **kwargs: Any) -> Any: ...
```

``Field`` for a limit that exists in ``limits.schema.json`` under dotted ``path`` (e.g. ``"transfer.idempotency_ttl_seconds"``). For a nested group, ``path`` is the group (``"retries"``) and its fields map to ``retries.<name>``.

Код: [config.py:258](../../../../../libs/jane-kit/src/jane_kit/config.py#L258).

### Функція `layer_from_env`

```python
def layer_from_env(
    prefix: str = 'JANE_LIMITS__',
    level: str = 'platform',
    environ: Mapping[str, str] | None = None,
) -> LimitLayer: ...
```

Layer from environment variables; ``__`` separates nesting, ``HARD_CAPS__`` marks a hard cap.

Values stay strings; pydantic coerces them to the declared types.

Код: [config.py:473](../../../../../libs/jane-kit/src/jane_kit/config.py#L473).

### Функція `load_layer`

```python
def load_layer(
    path: str | Path,
    level: str = 'platform',
    *,
    name: str | None = None,
) -> LimitLayer: ...
```

Read a layer file. ``level='platform'`` expects ``PlatformLimits`` (``defaults``/``hard_caps``/``profile``) and gives a ``shared`` layer (one profile for every service); other levels expect a plain Limits object.

Винятки в коді функції: `LimitError`.

Код: [config.py:452](../../../../../libs/jane-kit/src/jane_kit/config.py#L452).

### Функція `resolve_limits`

```python
def resolve_limits(
    model: type[L],
    *layers: LimitLayer,
    on_exceed: Literal['clamp', 'error'] = 'clamp',
) -> ResolvedLimits[L]: ...
```

Merge ``layers`` (least specific first) over the defaults of ``model`` and apply hard caps.

``on_exceed='clamp'`` lowers a value above a hard cap to the cap (recorded in ``clamped``, provenance ``hard_cap``); ``'error'`` raises :class:`LimitError` instead (useful to reject a request that asks for more than allowed with ``limit_exceeded``).

A ``shared`` layer (platform file) may carry limits of other services: see :attr:`LimitLayer.shared`; what it set but this model lacks is listed in ``ignored`` / ``ignored_hard_caps`` of the result.

Винятки в коді функції: `LimitError`.

Код: [config.py:347](../../../../../libs/jane-kit/src/jane_kit/config.py#L347).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `CONTRACT_LIMIT_PATHS` | `frozenset[str]` | `frozenset((f'{group}.{name}' for group, names in _CONTRACT_LIMITS.items() for na` | Leaf paths of ``limits.schema.json`` (``Limits``). A copy, because services run without ``contracts/``; ``tests/test_wp00_contracts.py`` keeps it equal to the schema. |
| `LEVELS` | `tuple[str, ...]` | `('platform', 'source', 'task', 'stage', 'request')` |  |
