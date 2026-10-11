# jane_kit.config

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.config.LEVELS](#jane_kitconfiglevels)
- [jane_kit.config.CONTRACT_LIMIT_PATHS](#jane_kitconfigcontract_limit_paths)
- [jane_kit.config.LimitError](#jane_kitconfiglimiterror)
- [jane_kit.config.Limits](#jane_kitconfiglimits)
- [jane_kit.config.Limits.model_config](#jane_kitconfiglimitsmodel_config)
- [jane_kit.config.LimitLayer](#jane_kitconfiglimitlayer)
- [jane_kit.config.LimitLayer.__init__](#jane_kitconfiglimitlayer__init__)
- [jane_kit.config.LimitLayer.level](#jane_kitconfiglimitlayerlevel)
- [jane_kit.config.LimitLayer.values](#jane_kitconfiglimitlayervalues)
- [jane_kit.config.LimitLayer.hard_caps](#jane_kitconfiglimitlayerhard_caps)
- [jane_kit.config.LimitLayer.name](#jane_kitconfiglimitlayername)
- [jane_kit.config.LimitLayer.profile](#jane_kitconfiglimitlayerprofile)
- [jane_kit.config.LimitLayer.shared](#jane_kitconfiglimitlayershared)
- [jane_kit.config.LimitLayer.label](#jane_kitconfiglimitlayerlabel)
- [jane_kit.config.ResolvedLimits](#jane_kitconfigresolvedlimits)
- [jane_kit.config.ResolvedLimits.__init__](#jane_kitconfigresolvedlimits__init__)
- [jane_kit.config.ResolvedLimits.limits](#jane_kitconfigresolvedlimitslimits)
- [jane_kit.config.ResolvedLimits.origin](#jane_kitconfigresolvedlimitsorigin)
- [jane_kit.config.ResolvedLimits.clamped](#jane_kitconfigresolvedlimitsclamped)
- [jane_kit.config.ResolvedLimits.hard_caps](#jane_kitconfigresolvedlimitshard_caps)
- [jane_kit.config.ResolvedLimits.profile](#jane_kitconfigresolvedlimitsprofile)
- [jane_kit.config.ResolvedLimits.ignored](#jane_kitconfigresolvedlimitsignored)
- [jane_kit.config.ResolvedLimits.ignored_hard_caps](#jane_kitconfigresolvedlimitsignored_hard_caps)
- [jane_kit.config.ResolvedLimits.platform_limits](#jane_kitconfigresolvedlimitsplatform_limits)
- [jane_kit.config.ResolvedLimits.provenance](#jane_kitconfigresolvedlimitsprovenance)
- [jane_kit.config.ResolvedLimits.effective](#jane_kitconfigresolvedlimitseffective)
- [jane_kit.config.ResolvedLimits.explain](#jane_kitconfigresolvedlimitsexplain)
- [jane_kit.config.contract_field](#jane_kitconfigcontract_field)
- [jane_kit.config.resolve_limits](#jane_kitconfigresolve_limits)
- [jane_kit.config.load_layer](#jane_kitconfigload_layer)
- [jane_kit.config.layer_from_env](#jane_kitconfiglayer_from_env)
- [jane_kit.config.JaneSettings](#jane_kitconfigjanesettings)
- [jane_kit.config.JaneSettings.model_config](#jane_kitconfigjanesettingsmodel_config)
- [jane_kit.config.JaneSettings.service_name](#jane_kitconfigjanesettingsservice_name)
- [jane_kit.config.JaneSettings.instance_id](#jane_kitconfigjanesettingsinstance_id)
- [jane_kit.config.JaneSettings.host](#jane_kitconfigjanesettingshost)
- [jane_kit.config.JaneSettings.port](#jane_kitconfigjanesettingsport)
- [jane_kit.config.JaneSettings.log_level](#jane_kitconfigjanesettingslog_level)
- [jane_kit.config.JaneSettings.log_format](#jane_kitconfigjanesettingslog_format)
- [jane_kit.config.JaneSettings.metrics_enabled](#jane_kitconfigjanesettingsmetrics_enabled)
- [jane_kit.config.JaneSettings.health_check_timeout_ms](#jane_kitconfigjanesettingshealth_check_timeout_ms)
- [jane_kit.config.JaneSettings.limits_file](#jane_kitconfigjanesettingslimits_file)
- [jane_kit.config.JaneSettings.platform_layers](#jane_kitconfigjanesettingsplatform_layers)
- [jane_kit.config.JaneSettings.with_overrides](#jane_kitconfigjanesettingswith_overrides)

## jane_kit.config.LEVELS

**Константа.** Код: [libs/jane-kit/src/jane_kit/config.py:57](../../../../../../libs/jane-kit/src/jane_kit/config.py#L57).

```python
LEVELS: tuple[str, ...] = ('platform', 'source', 'task', 'stage', 'request')
```

### Опис із вихідного коду

```text
Levels of ``LimitLevel`` in the contract, least specific first (plus ``hard_cap`` in provenance).
```

## jane_kit.config.CONTRACT_LIMIT_PATHS

**Константа.** Код: [libs/jane-kit/src/jane_kit/config.py:118](../../../../../../libs/jane-kit/src/jane_kit/config.py#L118).

```python
CONTRACT_LIMIT_PATHS: frozenset[str] = frozenset((f'{group}.{name}' for group, names in _CONTRACT_LIMITS.items() for name in names))
```

### Опис із вихідного коду

```text
Leaf paths of ``limits.schema.json`` (``Limits``). A copy, because services run without ``contracts/``;
``tests/test_wp00_contracts.py`` keeps it equal to the schema.
```

## jane_kit.config.LimitError

**Клас.** Код: [libs/jane-kit/src/jane_kit/config.py:125](../../../../../../libs/jane-kit/src/jane_kit/config.py#L125).

```python
class LimitError(ValueError):
```

Базові типи / інтерфейси: `ValueError`.

### Опис із вихідного коду

```text
Invalid limit configuration (unknown field, wrong type, loosened hard cap).
```

## jane_kit.config.Limits

**Клас.** Код: [libs/jane-kit/src/jane_kit/config.py:129](../../../../../../libs/jane-kit/src/jane_kit/config.py#L129).

```python
class Limits(BaseModel):
```

Базові типи / інтерфейси: `BaseModel`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_config](jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | ні |

### Опис із вихідного коду

```text
Base class for a service's limits. Subclasses must give every field a default.

Use the field names of ``limits.schema.json`` where the limit exists there
(``timeouts.request_timeout_ms``, ``transfer.idempotency_ttl_seconds``...). Nested groups are
fields whose type is another :class:`Limits` subclass with a default instance.
```

## jane_kit.config.Limits.model_config

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:137](../../../../../../libs/jane-kit/src/jane_kit/config.py#L137).

```python
model_config = ConfigDict(extra='forbid', frozen=True, validate_default=True)
```

Доступ: читання — так; запис — так.

## jane_kit.config.LimitLayer

**Клас.** Код: [libs/jane-kit/src/jane_kit/config.py:150](../../../../../../libs/jane-kit/src/jane_kit/config.py#L150).

```python
class LimitLayer:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [level](jane_kit.config.md#jane_kitconfiglimitlayerlevel) | Поле | ні |
| [values](jane_kit.config.md#jane_kitconfiglimitlayervalues) | Поле | ні |
| [hard_caps](jane_kit.config.md#jane_kitconfiglimitlayerhard_caps) | Поле | ні |
| [name](jane_kit.config.md#jane_kitconfiglimitlayername) | Поле | ні |
| [profile](jane_kit.config.md#jane_kitconfiglimitlayerprofile) | Поле | ні |
| [shared](jane_kit.config.md#jane_kitconfiglimitlayershared) | Поле | ні |
| [label](jane_kit.config.md#jane_kitconfiglimitlayerlabel) | Властивість | ні |
| [__init__](jane_kit.config.md#jane_kitconfiglimitlayer__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
One level of configuration (platform, source ``shop``, task ``prices``, stage ``extract``...).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_config.py:87](../../../../../../libs/jane-kit/tests/test_config.py#L87).

```python
r = resolve_limits(
        CollectorLimits,
        LimitLayer(
            "platform",
            {"concurrency": {"max_parallel_fetches": 8}, "timeouts": {"request_timeout_ms": 20_000}},
        ),
        LimitLayer("source", {"crawl": {"max_depth": 10}}, name="shop"),
        LimitLayer("task", {"concurrency": {"max_parallel_fetches": 2}}, name="prices"),
        LimitLayer("stage", {"timeouts": {"request_timeout_ms": 5_000}}, name="fetch"),
    )
```

Контекст і передумови: [libs/jane-kit/tests/test_config.py:114](../../../../../../libs/jane-kit/tests/test_config.py#L114).

```python
r = resolve_limits(
        CollectorLimits,
        LimitLayer("platform", hard_caps={"concurrency": {"max_parallel_fetches": 6}}),
        LimitLayer("task", {"concurrency": {"max_parallel_fetches": 50}}),
    )
```

## jane_kit.config.LimitLayer.__init__

**Конструктор dataclass.** Код: [libs/jane-kit/src/jane_kit/config.py:150](../../../../../../libs/jane-kit/src/jane_kit/config.py#L150).

```python
def __init__(self, level: str, values: Mapping[str, Any] = <factory dict>, hard_caps: Mapping[str, Any] = <factory dict>, name: str | None = None, profile: str | None = None, shared: bool = False) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `level` | `str` | `—` | positional-or-keyword |
| `values` | `Mapping[str, Any]` | `factory: dict` | positional-or-keyword |
| `hard_caps` | `Mapping[str, Any]` | `factory: dict` | positional-or-keyword |
| `name` | `str \| None` | `None` | positional-or-keyword |
| `profile` | `str \| None` | `None` | positional-or-keyword |
| `shared` | `bool` | `False` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_config.py:87](../../../../../../libs/jane-kit/tests/test_config.py#L87).

```python
r = resolve_limits(
        CollectorLimits,
        LimitLayer(
            "platform",
            {"concurrency": {"max_parallel_fetches": 8}, "timeouts": {"request_timeout_ms": 20_000}},
        ),
        LimitLayer("source", {"crawl": {"max_depth": 10}}, name="shop"),
        LimitLayer("task", {"concurrency": {"max_parallel_fetches": 2}}, name="prices"),
        LimitLayer("stage", {"timeouts": {"request_timeout_ms": 5_000}}, name="fetch"),
    )
```

Контекст і передумови: [libs/jane-kit/tests/test_config.py:114](../../../../../../libs/jane-kit/tests/test_config.py#L114).

```python
r = resolve_limits(
        CollectorLimits,
        LimitLayer("platform", hard_caps={"concurrency": {"max_parallel_fetches": 6}}),
        LimitLayer("task", {"concurrency": {"max_parallel_fetches": 50}}),
    )
```

## jane_kit.config.LimitLayer.level

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:153](../../../../../../libs/jane-kit/src/jane_kit/config.py#L153).

```python
level: str
```

Доступ: читання — так; запис — ні.

## jane_kit.config.LimitLayer.values

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:154](../../../../../../libs/jane-kit/src/jane_kit/config.py#L154).

```python
values: Mapping[str, Any] = field(default_factory=dict)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_kit.config.LimitLayer.hard_caps

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:155](../../../../../../libs/jane-kit/src/jane_kit/config.py#L155).

```python
hard_caps: Mapping[str, Any] = field(default_factory=dict)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_kit.config.LimitLayer.name

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:156](../../../../../../libs/jane-kit/src/jane_kit/config.py#L156).

```python
name: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_kit.config.LimitLayer.profile

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:157](../../../../../../libs/jane-kit/src/jane_kit/config.py#L157).

```python
profile: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_kit.config.LimitLayer.shared

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:158](../../../../../../libs/jane-kit/src/jane_kit/config.py#L158).

```python
shared: bool = False
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
Contract-shaped document shared by all services (a platform file): contract paths map to the fields
    that declare them, contract paths the model does not declare are ignored (``ResolvedLimits.ignored``).
    Paths unknown to the contract and to the model are still rejected.
```

## jane_kit.config.LimitLayer.label

**Властивість.** Код: [libs/jane-kit/src/jane_kit/config.py:164](../../../../../../libs/jane-kit/src/jane_kit/config.py#L164).

```python
def label(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## jane_kit.config.ResolvedLimits

**Клас.** Код: [libs/jane-kit/src/jane_kit/config.py:169](../../../../../../libs/jane-kit/src/jane_kit/config.py#L169).

```python
class ResolvedLimits:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [limits](jane_kit.config.md#jane_kitconfigresolvedlimitslimits) | Поле | ні |
| [origin](jane_kit.config.md#jane_kitconfigresolvedlimitsorigin) | Поле | ні |
| [clamped](jane_kit.config.md#jane_kitconfigresolvedlimitsclamped) | Поле | ні |
| [hard_caps](jane_kit.config.md#jane_kitconfigresolvedlimitshard_caps) | Поле | ні |
| [profile](jane_kit.config.md#jane_kitconfigresolvedlimitsprofile) | Поле | ні |
| [ignored](jane_kit.config.md#jane_kitconfigresolvedlimitsignored) | Поле | ні |
| [ignored_hard_caps](jane_kit.config.md#jane_kitconfigresolvedlimitsignored_hard_caps) | Поле | ні |
| [platform_limits](jane_kit.config.md#jane_kitconfigresolvedlimitsplatform_limits) | Метод | ні |
| [provenance](jane_kit.config.md#jane_kitconfigresolvedlimitsprovenance) | Метод | ні |
| [effective](jane_kit.config.md#jane_kitconfigresolvedlimitseffective) | Метод | ні |
| [explain](jane_kit.config.md#jane_kitconfigresolvedlimitsexplain) | Метод | ні |
| [__init__](jane_kit.config.md#jane_kitconfigresolvedlimits__init__) | Конструктор dataclass | ні |

## jane_kit.config.ResolvedLimits.__init__

**Конструктор dataclass.** Код: [libs/jane-kit/src/jane_kit/config.py:169](../../../../../../libs/jane-kit/src/jane_kit/config.py#L169).

```python
def __init__(self, limits: L, origin: dict[str, str], clamped: dict[str, str], hard_caps: dict[str, Any] = <factory dict>, profile: str | None = None, ignored: dict[str, str] = <factory dict>, ignored_hard_caps: dict[str, str] = <factory dict>) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `limits` | `L` | `—` | positional-or-keyword |
| `origin` | `dict[str, str]` | `—` | positional-or-keyword |
| `clamped` | `dict[str, str]` | `—` | positional-or-keyword |
| `hard_caps` | `dict[str, Any]` | `factory: dict` | positional-or-keyword |
| `profile` | `str \| None` | `None` | positional-or-keyword |
| `ignored` | `dict[str, str]` | `factory: dict` | positional-or-keyword |
| `ignored_hard_caps` | `dict[str, str]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

## jane_kit.config.ResolvedLimits.limits

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:170](../../../../../../libs/jane-kit/src/jane_kit/config.py#L170).

```python
limits: L
```

Доступ: читання — так; запис — ні.

## jane_kit.config.ResolvedLimits.origin

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:171](../../../../../../libs/jane-kit/src/jane_kit/config.py#L171).

```python
origin: dict[str, str]
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
Dotted leaf path -> label of the layer that set it (``default`` = the model's default).
```

## jane_kit.config.ResolvedLimits.clamped

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:173](../../../../../../libs/jane-kit/src/jane_kit/config.py#L173).

```python
clamped: dict[str, str]
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
Dotted leaf path -> label of the layer whose hard cap reduced the value.
```

## jane_kit.config.ResolvedLimits.hard_caps

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:175](../../../../../../libs/jane-kit/src/jane_kit/config.py#L175).

```python
hard_caps: dict[str, Any] = field(default_factory=dict)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

### Опис із вихідного коду

```text
Dotted leaf path -> effective hard cap (the tightest one of all layers).
```

## jane_kit.config.ResolvedLimits.profile

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:177](../../../../../../libs/jane-kit/src/jane_kit/config.py#L177).

```python
profile: str | None = None
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
Name of the platform limits profile, if a PlatformLimits file declared one.
```

## jane_kit.config.ResolvedLimits.ignored

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:179](../../../../../../libs/jane-kit/src/jane_kit/config.py#L179).

```python
ignored: dict[str, str] = field(default_factory=dict)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

### Опис із вихідного коду

```text
Contract path -> label of the shared layer whose value was not applied: this service has no such limit.
```

## jane_kit.config.ResolvedLimits.ignored_hard_caps

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:181](../../../../../../libs/jane-kit/src/jane_kit/config.py#L181).

```python
ignored_hard_caps: dict[str, str] = field(default_factory=dict)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

### Опис із вихідного коду

```text
Same for ``hard_caps`` of shared layers.
```

## jane_kit.config.ResolvedLimits.platform_limits

**Метод.** Код: [libs/jane-kit/src/jane_kit/config.py:184](../../../../../../libs/jane-kit/src/jane_kit/config.py#L184).

```python
def platform_limits(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
``PlatformLimits`` document for ``/v1/info`` (WP-00 ``ServiceInfo.limits``).

Only fields that map to ``limits.schema.json`` (declared with :func:`contract_field` or nested
under a group with a contract path) are included; service-specific limits stay internal because
the contract schema is strict (``additionalProperties: false``).
```

## jane_kit.config.ResolvedLimits.provenance

**Метод.** Код: [libs/jane-kit/src/jane_kit/config.py:202](../../../../../../libs/jane-kit/src/jane_kit/config.py#L202).

```python
def provenance(self) -> dict[str, str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, str]`.

### Опис із вихідного коду

```text
Leaf path -> contract ``LimitLevel`` (model defaults count as ``platform``).
```

## jane_kit.config.ResolvedLimits.effective

**Метод.** Код: [libs/jane-kit/src/jane_kit/config.py:214](../../../../../../libs/jane-kit/src/jane_kit/config.py#L214).

```python
def effective(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
``EffectiveLimits`` document: ``{"limits": {...}, "provenance": {...}}``.
```

## jane_kit.config.ResolvedLimits.explain

**Метод.** Код: [libs/jane-kit/src/jane_kit/config.py:218](../../../../../../libs/jane-kit/src/jane_kit/config.py#L218).

```python
def explain(self) -> list[tuple[str, Any, str]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `list[tuple[str, Any, str]]`.

### Опис із вихідного коду

```text
Rows ``(path, value, origin)`` for logs and diagnostics.
```

## jane_kit.config.contract_field

**Функція.** Код: [libs/jane-kit/src/jane_kit/config.py:255](../../../../../../libs/jane-kit/src/jane_kit/config.py#L255).

```python
def contract_field(path: str, default: Any, **kwargs: Any) -> Any:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `path` | `str` | `—` | positional-or-keyword |
| `default` | `Any` | `—` | positional-or-keyword |
| `kwargs` | `Any` | `—` | var-keyword |

Результат: `Any`.

### Опис із вихідного коду

```text
``Field`` for a limit that exists in ``limits.schema.json`` under dotted ``path``
(e.g. ``"transfer.idempotency_ttl_seconds"``). For a nested group, ``path`` is the group
(``"retries"``) and its fields map to ``retries.<name>``.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_config.py:42](../../../../../../libs/jane-kit/tests/test_config.py#L42).

```python
crawl_depth: int = contract_field("crawl.max_depth", 3, ge=0)
```

## jane_kit.config.resolve_limits

**Функція.** Код: [libs/jane-kit/src/jane_kit/config.py:344](../../../../../../libs/jane-kit/src/jane_kit/config.py#L344).

```python
def resolve_limits[L: Limits](model: type[L], *layers: LimitLayer, on_exceed: Literal['clamp', 'error']='clamp') -> ResolvedLimits[L]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `model` | `type[L]` | `—` | positional-or-keyword |
| `layers` | `LimitLayer` | `—` | var-positional |
| `on_exceed` | `Literal['clamp', 'error']` | `'clamp'` | keyword-only |

Результат: `ResolvedLimits[L]`.

Явні `raise` у тілі: `LimitError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Merge ``layers`` (least specific first) over the defaults of ``model`` and apply hard caps.

``on_exceed='clamp'`` lowers a value above a hard cap to the cap (recorded in ``clamped``,
provenance ``hard_cap``); ``'error'`` raises :class:`LimitError` instead (useful to reject a
request that asks for more than allowed with ``limit_exceeded``).

A ``shared`` layer (platform file) may carry limits of other services: see :attr:`LimitLayer.shared`;
what it set but this model lacks is listed in ``ignored`` / ``ignored_hard_caps`` of the result.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_config.py:80](../../../../../../libs/jane-kit/tests/test_config.py#L80).

```python
r = resolve_limits(CollectorLimits)
```

Контекст і передумови: [libs/jane-kit/tests/test_config.py:87](../../../../../../libs/jane-kit/tests/test_config.py#L87).

```python
r = resolve_limits(
        CollectorLimits,
        LimitLayer(
            "platform",
            {"concurrency": {"max_parallel_fetches": 8}, "timeouts": {"request_timeout_ms": 20_000}},
        ),
        LimitLayer("source", {"crawl": {"max_depth": 10}}, name="shop"),
        LimitLayer("task", {"concurrency": {"max_parallel_fetches": 2}}, name="prices"),
        LimitLayer("stage", {"timeouts": {"request_timeout_ms": 5_000}}, name="fetch"),
    )
```

## jane_kit.config.load_layer

**Функція.** Код: [libs/jane-kit/src/jane_kit/config.py:442](../../../../../../libs/jane-kit/src/jane_kit/config.py#L442).

```python
def load_layer(path: str | Path, level: str='platform', *, name: str | None=None) -> LimitLayer:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `path` | `str \| Path` | `—` | positional-or-keyword |
| `level` | `str` | `'platform'` | positional-or-keyword |
| `name` | `str \| None` | `None` | keyword-only |

Результат: `LimitLayer`.

Явні `raise` у тілі: `LimitError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Read a layer file. ``level='platform'`` expects ``PlatformLimits`` (``defaults``/``hard_caps``/``profile``)
and gives a ``shared`` layer (one profile for every service); other levels expect a plain Limits object.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_config.py:185](../../../../../../libs/jane-kit/tests/test_config.py#L185).

```python
layer = load_layer(f)
```

Контекст і передумови: [libs/jane-kit/tests/test_config.py:255](../../../../../../libs/jane-kit/tests/test_config.py#L255).

```python
layer = load_layer(write_profile(tmp_path, SHARED_PROFILE))
```

## jane_kit.config.layer_from_env

**Функція.** Код: [libs/jane-kit/src/jane_kit/config.py:463](../../../../../../libs/jane-kit/src/jane_kit/config.py#L463).

```python
def layer_from_env(prefix: str='JANE_LIMITS__', level: str='platform', environ: Mapping[str, str] | None=None) -> LimitLayer:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `prefix` | `str` | `'JANE_LIMITS__'` | positional-or-keyword |
| `level` | `str` | `'platform'` | positional-or-keyword |
| `environ` | `Mapping[str, str] \| None` | `None` | positional-or-keyword |

Результат: `LimitLayer`.

### Опис із вихідного коду

```text
Layer from environment variables; ``__`` separates nesting, ``HARD_CAPS__`` marks a hard cap.

Values stay strings; pydantic coerces them to the declared types.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_config.py:167](../../../../../../libs/jane-kit/tests/test_config.py#L167).

```python
r = resolve_limits(CollectorLimits, layer_from_env("X_LIMITS__", environ=env))
```

Контекст і передумови: [libs/jane-kit/tests/test_config.py:363](../../../../../../libs/jane-kit/tests/test_config.py#L363).

```python
layer_from_env("X_LIMITS__", environ={"X_LIMITS__SANDBOX__MEMORY_MB": "512"})
```

## jane_kit.config.JaneSettings

**Клас.** Код: [libs/jane-kit/src/jane_kit/config.py:487](../../../../../../libs/jane-kit/src/jane_kit/config.py#L487).

```python
class JaneSettings(BaseSettings, AuthSettings):
```

Базові типи / інтерфейси: `BaseSettings`, `AuthSettings`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_config](jane_kit.config.md#jane_kitconfigjanesettingsmodel_config) | Поле | ні |
| [service_name](jane_kit.config.md#jane_kitconfigjanesettingsservice_name) | Поле | ні |
| [instance_id](jane_kit.config.md#jane_kitconfigjanesettingsinstance_id) | Поле | ні |
| [host](jane_kit.config.md#jane_kitconfigjanesettingshost) | Поле | ні |
| [port](jane_kit.config.md#jane_kitconfigjanesettingsport) | Поле | ні |
| [log_level](jane_kit.config.md#jane_kitconfigjanesettingslog_level) | Поле | ні |
| [log_format](jane_kit.config.md#jane_kitconfigjanesettingslog_format) | Поле | ні |
| [metrics_enabled](jane_kit.config.md#jane_kitconfigjanesettingsmetrics_enabled) | Поле | ні |
| [health_check_timeout_ms](jane_kit.config.md#jane_kitconfigjanesettingshealth_check_timeout_ms) | Поле | ні |
| [limits_file](jane_kit.config.md#jane_kitconfigjanesettingslimits_file) | Поле | ні |
| [platform_layers](jane_kit.config.md#jane_kitconfigjanesettingsplatform_layers) | Метод | ні |
| [with_overrides](jane_kit.config.md#jane_kitconfigjanesettingswith_overrides) | Метод | ні |
| [auth_mode](jane_kit.auth.md#jane_kitauthauthsettingsauth_mode) | Поле | так |
| [auth_none_allow_remote](jane_kit.auth.md#jane_kitauthauthsettingsauth_none_allow_remote) | Поле | так |
| [api_keys](jane_kit.auth.md#jane_kitauthauthsettingsapi_keys) | Поле | так |
| [api_keys_file](jane_kit.auth.md#jane_kitauthauthsettingsapi_keys_file) | Поле | так |
| [jwt_jwks_url](jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_url) | Поле | так |
| [jwt_issuer](jane_kit.auth.md#jane_kitauthauthsettingsjwt_issuer) | Поле | так |
| [jwt_audience](jane_kit.auth.md#jane_kitauthauthsettingsjwt_audience) | Поле | так |
| [jwt_algorithms](jane_kit.auth.md#jane_kitauthauthsettingsjwt_algorithms) | Поле | так |
| [jwt_scope_claim](jane_kit.auth.md#jane_kitauthauthsettingsjwt_scope_claim) | Поле | так |
| [jwt_leeway_seconds](jane_kit.auth.md#jane_kitauthauthsettingsjwt_leeway_seconds) | Поле | так |
| [jwt_jwks_cache_ttl_seconds](jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_cache_ttl_seconds) | Поле | так |
| [jwt_jwks_timeout_ms](jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_timeout_ms) | Поле | так |
| [jwt_jwks_refresh_cooldown_seconds](jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_refresh_cooldown_seconds) | Поле | так |
| [jwt_jwks_max_bytes](jane_kit.auth.md#jane_kitauthauthsettingsjwt_jwks_max_bytes) | Поле | так |
| [auth_max_token_bytes](jane_kit.auth.md#jane_kitauthauthsettingsauth_max_token_bytes) | Поле | так |
| [metrics_public](jane_kit.auth.md#jane_kitauthauthsettingsmetrics_public) | Поле | так |

### Опис із вихідного коду

```text
Common process settings. A service subclasses it and sets its own ``env_prefix``.

Only process-level knobs live here; operational limits belong in a :class:`Limits` model.
Authentication fields (``auth_mode``, ``api_keys``, ``jwt_*``...) come from
:class:`jane_kit.auth.AuthSettings` (ADR-0005); ``create_app`` enforces them.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_auth.py:59](../../../../../../libs/jane-kit/tests/test_auth.py#L59).

```python
return JaneSettings(service_name="svc", instance_id="i-1", **kw)
```

Контекст і передумови: [libs/jane-kit/tests/test_config.py:30](../../../../../../libs/jane-kit/tests/test_config.py#L30).

```python
first = JaneSettings().instance_id
```

## jane_kit.config.JaneSettings.model_config

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:495](../../../../../../libs/jane-kit/src/jane_kit/config.py#L495).

```python
model_config = SettingsConfigDict(env_prefix='JANE_', extra='ignore', env_nested_delimiter='__')
```

Доступ: читання — так; запис — так.

## jane_kit.config.JaneSettings.service_name

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:497](../../../../../../libs/jane-kit/src/jane_kit/config.py#L497).

```python
service_name: str = 'jane-service'
```

Доступ: читання — так; запис — так.

## jane_kit.config.JaneSettings.instance_id

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:498](../../../../../../libs/jane-kit/src/jane_kit/config.py#L498).

```python
instance_id: str = Field(default_factory=lambda: f'{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex}')
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "lambda: f'{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex}'"
}
```

### Опис із вихідного коду

```text
Unique to this process start, including a restart that reuses the container hostname and PID.
```

## jane_kit.config.JaneSettings.host

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:502](../../../../../../libs/jane-kit/src/jane_kit/config.py#L502).

```python
host: str = '127.0.0.1'
```

Доступ: читання — так; запис — так.

## jane_kit.config.JaneSettings.port

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:503](../../../../../../libs/jane-kit/src/jane_kit/config.py#L503).

```python
port: int = 8000
```

Доступ: читання — так; запис — так.

## jane_kit.config.JaneSettings.log_level

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:504](../../../../../../libs/jane-kit/src/jane_kit/config.py#L504).

```python
log_level: str = 'INFO'
```

Доступ: читання — так; запис — так.

## jane_kit.config.JaneSettings.log_format

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:505](../../../../../../libs/jane-kit/src/jane_kit/config.py#L505).

```python
log_format: Literal['json', 'console'] = 'json'
```

Доступ: читання — так; запис — так.

## jane_kit.config.JaneSettings.metrics_enabled

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:506](../../../../../../libs/jane-kit/src/jane_kit/config.py#L506).

```python
metrics_enabled: bool = True
```

Доступ: читання — так; запис — так.

## jane_kit.config.JaneSettings.health_check_timeout_ms

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:507](../../../../../../libs/jane-kit/src/jane_kit/config.py#L507).

```python
health_check_timeout_ms: int = Field(default=2000, ge=1)
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
Time box of every ``/v1/health`` check (env ``<PREFIX>HEALTH_CHECK_TIMEOUT_MS``).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_service.py:184](../../../../../../libs/jane-kit/tests/test_service.py#L184).

```python
assert settings.health_check_timeout_ms == 40
```

## jane_kit.config.JaneSettings.limits_file

**Поле.** Код: [libs/jane-kit/src/jane_kit/config.py:509](../../../../../../libs/jane-kit/src/jane_kit/config.py#L509).

```python
limits_file: Path | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
Platform limits file (``PlatformLimits`` shape, e.g. a whole ``deploy/profiles/<profile>.json``: limits
    this service does not have are ignored, typos are errors); env ``<PREFIX>LIMITS__*`` overrides it.
```

## jane_kit.config.JaneSettings.platform_layers

**Метод.** Код: [libs/jane-kit/src/jane_kit/config.py:513](../../../../../../libs/jane-kit/src/jane_kit/config.py#L513).

```python
def platform_layers(self, env_prefix: str='JANE_LIMITS__') -> list[LimitLayer]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `env_prefix` | `str` | `'JANE_LIMITS__'` | positional-or-keyword |

Результат: `list[LimitLayer]`.

### Опис із вихідного коду

```text
Platform layers in order: limits file, then environment overrides.
```

## jane_kit.config.JaneSettings.with_overrides

**Метод.** Код: [libs/jane-kit/src/jane_kit/config.py:523](../../../../../../libs/jane-kit/src/jane_kit/config.py#L523).

```python
def with_overrides(self, **values: Any) -> Self:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `values` | `Any` | `—` | var-keyword |

Результат: `Self`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_auth.py:61](../../../../../../services/assistant/tests/test_auth.py#L61).

```python
Neighbours.from_settings(
            s.with_overrides(llm_token_ref="env:JANE_TEST_ASSISTANT_UNSET"), ClientLimits()
        )
```

Контекст і передумови: [services/handler-runtime/tests/test_auth.py:23](../../../../../../services/handler-runtime/tests/test_auth.py#L23).

```python
s = subprocess_settings.with_overrides(auth_mode="api_key", api_keys=KEYS)
```
