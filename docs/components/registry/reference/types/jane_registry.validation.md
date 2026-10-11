# Модуль `jane_registry.validation`

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry/validation.py](../../../../../services/registry/src/jane_registry/validation.py). Не редагуйте вручну.

Validation of a package before publication: manifest schema, kind &lt;-> entry, referenced files, schemas, collector rules, tests (ADR-0002, contracts/docs/handler-packages.md).

Schemas are the contract files (``contracts/schemas``); the registry never keeps its own copy.

## Зміст

- [Клас `ContractSchemas`](#клас-contractschemas)
- [Клас `Issue`](#клас-issue)
- [Клас `PackageValidator`](#клас-packagevalidator)
- [Функція `find_contracts_dir`](#функція-find_contracts_dir)

## Класи

### Клас `ContractSchemas`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.validation` |
| Успадкування | `KitSchemas` |
| Код | [validation.py:52](../../../../../services/registry/src/jane_registry/validation.py#L52) |

```python
class ContractSchemas(KitSchemas): ...
```

jane-kit's shared contract validators (R17; ``format`` is checked, as before) with the registry's issues.

#### Конструктор `ContractSchemas.__init__`

```python
def __init__(self, contracts: Path) -> None: ...
```

Код: [validation.py:55](../../../../../services/registry/src/jane_registry/validation.py#L55).

#### Метод `ContractSchemas.issues`

```python
def issues(self, relative: str, instance: Any, prefix: str, fragment: str = '') -> list[Issue]: ...
```

Код: [validation.py:58](../../../../../services/registry/src/jane_registry/validation.py#L58).

### Клас `Issue`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_registry.validation` |
| Код | [validation.py:29](../../../../../services/registry/src/jane_registry/validation.py#L29) |

```python
@dataclass(frozen=True)
class Issue: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `pointer` | `str` | — | читання |  |
| `message` | `str` | — | читання |  |
| `code` | `str \| None` | `None` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `PackageValidator`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.validation` |
| Код | [validation.py:81](../../../../../services/registry/src/jane_registry/validation.py#L81) |

```python
class PackageValidator: ...
```

#### Конструктор `PackageValidator.__init__`

```python
def __init__(self, schemas: ContractSchemas, *, require_tests: bool = True) -> None: ...
```

Код: [validation.py:82](../../../../../services/registry/src/jane_registry/validation.py#L82).

#### Метод `PackageValidator.referenced_paths`

```python
@staticmethod
def referenced_paths(manifest: Mapping[str, Any]) -> Iterator[tuple[str, str]]: ...
```

``(JSON pointer in the manifest, package path)`` of every file the manifest refers to.

Код: [validation.py:104](../../../../../services/registry/src/jane_registry/validation.py#L104).

#### Метод `PackageValidator.manifest_issues`

```python
def manifest_issues(self, manifest: Any, prefix: str = '/manifest') -> list[Issue]: ...
```

Код: [validation.py:132](../../../../../services/registry/src/jane_registry/validation.py#L132).

#### Метод `PackageValidator.package_issues`

```python
def package_issues(
    self,
    manifest: Mapping[str, Any],
    files: Mapping[str, bytes],
    prefix: str,
) -> list[Issue]: ...
```

Checks beyond the JSON Schema. ``manifest`` is already schema-valid.

Код: [validation.py:137](../../../../../services/registry/src/jane_registry/validation.py#L137).

## Функції

### Функція `find_contracts_dir`

```python
def find_contracts_dir(configured: Path | None) -> Path: ...
```

``contracts/`` from settings, ``JANE_CONTRACTS_DIR``, the checkout, or ``/app/contracts`` (image).

Винятки в коді функції: `FileNotFoundError`.

Код: [validation.py:35](../../../../../services/registry/src/jane_registry/validation.py#L35).
