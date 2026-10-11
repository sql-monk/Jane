# Модуль `jane_kit.rules`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/rules.py](../../../../../libs/jane-kit/src/jane_kit/rules.py). Не редагуйте вручну.

Collector rules: schema validation and loading by ``rules_ref`` (shared by the collectors, R17).

* :class:`CollectorSchemas` - JSON Schemas of ``collector.v1`` (request components) and ``collector-rules.schema.json``; a failed ``oneOf`` over strategies or rules is re-validated against the branch named by its discriminator (``type`` / ``collector``), so the errors point at the real field;
* :class:`RulesReport` - ``valid`` / ``supported`` + errors and warnings (``RulesValidation`` of the contract);
* :class:`RulesLoader` - rules of a ``rules_ref`` (``PackageRef``), in order:

  1. a local package directory ``<rules_dir>/<package_id>/<version>/`` or an exported archive
     ``<rules_dir>/<package_id>-<version>.zip`` / ``<rules_dir>/<package_id>/<version>.zip``
     (``jane-package.json`` + the file named by ``entry.rules``);
  2. the package registry (``registry.v1``): ``GET /v1/packages/{id}/versions/{v}`` (manifest, digest, file list),
     then ``GET .../file?path=<entry.rules>``; the file must match ``files[].sha256`` of the immutable version.

  A ``digest`` of the reference must equal the registry's version digest (``digest_mismatch``); for a local archive it is compared with ``sha256`` of the archive file (an unpacked directory cannot be verified: refused). The registry token comes from the environment variable the operator names; a value that is not a valid HTTP header is refused, and error details never carry transport errors (URLs, hosts).

## Зміст

- [Клас `CollectorSchemas`](#клас-collectorschemas)
- [Клас `RulesLoader`](#клас-rulesloader)
- [Клас `RulesReport`](#клас-rulesreport)
- [Функція `header_value_safe`](#функція-header_value_safe)

## Класи

### Клас `CollectorSchemas`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.rules` |
| Успадкування | `ContractSchemas` |
| Код | [rules.py:71](../../../../../libs/jane-kit/src/jane_kit/rules.py#L71) |

```python
class CollectorSchemas(ContractSchemas): ...
```

``collector.v1`` and ``collector-rules.schema.json`` validators (see the module docstring).

#### Конструктор `CollectorSchemas.__init__`

```python
def __init__(
    self,
    root: Path,
    *,
    openapi: str | None = 'collector.v1.yaml',
    format_check: bool = False,
) -> None: ...
```

Код: [rules.py:74](../../../../../libs/jane-kit/src/jane_kit/rules.py#L74).

#### Метод `CollectorSchemas.locate_collector`

```python
@classmethod
def locate_collector(
    cls,
    configured: Path | None,
    *,
    setting: str,
    start: Path | None = None,
) -> Self: ...
```

Код: [rules.py:81](../../../../../libs/jane-kit/src/jane_kit/rules.py#L81).

#### Метод `CollectorSchemas.errors`

```python
def errors(self, uri: str, instance: Any, prefix: Sequence[Any] = ()) -> list[FieldError]: ...
```

Field errors with the pointer ``prefix`` + instance path (empty for the root).

Код: [rules.py:84](../../../../../libs/jane-kit/src/jane_kit/rules.py#L84).

#### Метод `CollectorSchemas.rules_errors`

```python
def rules_errors(self, rules: Any, prefix: Sequence[Any] = ()) -> list[FieldError]: ...
```

Код: [rules.py:107](../../../../../libs/jane-kit/src/jane_kit/rules.py#L107).

### Клас `RulesLoader`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.rules` |
| Код | [rules.py:133](../../../../../libs/jane-kit/src/jane_kit/rules.py#L133) |

```python
class RulesLoader: ...
```

Rules of a ``rules_ref`` (see the module docstring); ``settings_prefix`` (``JANE_WEB_COLLECTOR_``) names the settings in error messages.

#### Конструктор `RulesLoader.__init__`

```python
def __init__(
    self,
    *,
    rules_dir: Path | None,
    registry_url: str | None,
    registry_token_env: str | None,
    timeout_s: float,
    settings_prefix: str = '',
) -> None: ...
```

Код: [rules.py:137](../../../../../libs/jane-kit/src/jane_kit/rules.py#L137).

#### Метод `RulesLoader.sources`

```python
def sources(self) -> list[str]: ...
```

Код: [rules.py:152](../../../../../libs/jane-kit/src/jane_kit/rules.py#L152).

#### Метод `RulesLoader.load`

```python
async def load(self, ref: Mapping[str, Any]) -> dict[str, Any]: ...
```

Винятки в коді методу: `ValidationFailed`.

Код: [rules.py:160](../../../../../libs/jane-kit/src/jane_kit/rules.py#L160).

### Клас `RulesReport`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_kit.rules` |
| Код | [rules.py:112](../../../../../libs/jane-kit/src/jane_kit/rules.py#L112) |

```python
@dataclass
class RulesReport: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `valid` | `bool` | — | читання й запис |  |
| `supported` | `bool` | — | читання й запис |  |
| `errors` | `list[FieldError]` | — | читання й запис |  |
| `warnings` | `list[FieldError]` | — | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `RulesReport.wire`

```python
def wire(self) -> dict[str, Any]: ...
```

Код: [rules.py:118](../../../../../libs/jane-kit/src/jane_kit/rules.py#L118).

## Функції

### Функція `header_value_safe`

```python
def header_value_safe(value: object) -> bool: ...
```

HTTP header values must be visible ASCII, with no control characters to reach error text.

Код: [rules.py:61](../../../../../libs/jane-kit/src/jane_kit/rules.py#L61).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `STRATEGY_DEFS` | — | `{'seed_list': 'SeedListStrategy', 'recursive': 'RecursiveStrategy', 'sitemap': '` | ``strategies[].type`` -> ``$defs`` branch of ``collector-rules.schema.json``. |
