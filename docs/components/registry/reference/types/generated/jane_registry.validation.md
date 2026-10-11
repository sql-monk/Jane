# jane_registry.validation

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_registry.validation.Issue](#jane_registryvalidationissue)
- [jane_registry.validation.Issue.__init__](#jane_registryvalidationissue__init__)
- [jane_registry.validation.Issue.pointer](#jane_registryvalidationissuepointer)
- [jane_registry.validation.Issue.message](#jane_registryvalidationissuemessage)
- [jane_registry.validation.Issue.code](#jane_registryvalidationissuecode)
- [jane_registry.validation.find_contracts_dir](#jane_registryvalidationfind_contracts_dir)
- [jane_registry.validation.ContractSchemas](#jane_registryvalidationcontractschemas)
- [jane_registry.validation.ContractSchemas.__init__](#jane_registryvalidationcontractschemas__init__)
- [jane_registry.validation.ContractSchemas.issues](#jane_registryvalidationcontractschemasissues)
- [jane_registry.validation.PackageValidator](#jane_registryvalidationpackagevalidator)
- [jane_registry.validation.PackageValidator.__init__](#jane_registryvalidationpackagevalidator__init__)
- [jane_registry.validation.PackageValidator.schemas](#jane_registryvalidationpackagevalidatorschemas)
- [jane_registry.validation.PackageValidator.require_tests](#jane_registryvalidationpackagevalidatorrequire_tests)
- [jane_registry.validation.PackageValidator.referenced_paths](#jane_registryvalidationpackagevalidatorreferenced_paths)
- [jane_registry.validation.PackageValidator.manifest_issues](#jane_registryvalidationpackagevalidatormanifest_issues)
- [jane_registry.validation.PackageValidator.package_issues](#jane_registryvalidationpackagevalidatorpackage_issues)

## jane_registry.validation.Issue

**Клас.** Код: [services/registry/src/jane_registry/validation.py:29](../../../../../../services/registry/src/jane_registry/validation.py#L29).

```python
class Issue:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [pointer](jane_registry.validation.md#jane_registryvalidationissuepointer) | Поле | ні |
| [message](jane_registry.validation.md#jane_registryvalidationissuemessage) | Поле | ні |
| [code](jane_registry.validation.md#jane_registryvalidationissuecode) | Поле | ні |
| [__init__](jane_registry.validation.md#jane_registryvalidationissue__init__) | Конструктор dataclass | ні |

## jane_registry.validation.Issue.__init__

**Конструктор dataclass.** Код: [services/registry/src/jane_registry/validation.py:29](../../../../../../services/registry/src/jane_registry/validation.py#L29).

```python
def __init__(self, pointer: str, message: str, code: str | None = None) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `pointer` | `str` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |
| `code` | `str \| None` | `None` | positional-or-keyword |

Результат: `None`.

## jane_registry.validation.Issue.pointer

**Поле.** Код: [services/registry/src/jane_registry/validation.py:30](../../../../../../services/registry/src/jane_registry/validation.py#L30).

```python
pointer: str
```

Доступ: читання — так; запис — ні.

## jane_registry.validation.Issue.message

**Поле.** Код: [services/registry/src/jane_registry/validation.py:31](../../../../../../services/registry/src/jane_registry/validation.py#L31).

```python
message: str
```

Доступ: читання — так; запис — ні.

## jane_registry.validation.Issue.code

**Поле.** Код: [services/registry/src/jane_registry/validation.py:32](../../../../../../services/registry/src/jane_registry/validation.py#L32).

```python
code: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_registry.validation.find_contracts_dir

**Функція.** Код: [services/registry/src/jane_registry/validation.py:35](../../../../../../services/registry/src/jane_registry/validation.py#L35).

```python
def find_contracts_dir(configured: Path | None) -> Path:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `configured` | `Path \| None` | `—` | positional-or-keyword |

Результат: `Path`.

Явні `raise` у тілі: `FileNotFoundError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
``contracts/`` from settings, ``JANE_CONTRACTS_DIR``, the checkout, or ``/app/contracts`` (image).
```

## jane_registry.validation.ContractSchemas

**Клас.** Код: [services/registry/src/jane_registry/validation.py:52](../../../../../../services/registry/src/jane_registry/validation.py#L52).

```python
class ContractSchemas(KitSchemas):
```

Базові типи / інтерфейси: `KitSchemas`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_registry.validation.md#jane_registryvalidationcontractschemas__init__) | Конструктор | ні |
| [issues](jane_registry.validation.md#jane_registryvalidationcontractschemasissues) | Метод | ні |
| [root](../../../../jane-kit/reference/types/generated/jane_kit.schemas.md#jane_kitschemascontractschemasroot) | Поле екземпляра | так |
| [schemas_dir](../../../../jane-kit/reference/types/generated/jane_kit.schemas.md#jane_kitschemascontractschemasschemas_dir) | Поле екземпляра | так |
| [spec](../../../../jane-kit/reference/types/generated/jane_kit.schemas.md#jane_kitschemascontractschemasspec) | Поле екземпляра | так |
| [registry](../../../../jane-kit/reference/types/generated/jane_kit.schemas.md#jane_kitschemascontractschemasregistry) | Поле екземпляра | так |
| [format_checker](../../../../jane-kit/reference/types/generated/jane_kit.schemas.md#jane_kitschemascontractschemasformat_checker) | Поле екземпляра | так |
| [locate](../../../../jane-kit/reference/types/generated/jane_kit.schemas.md#jane_kitschemascontractschemaslocate) | Метод | так |
| [uri](../../../../jane-kit/reference/types/generated/jane_kit.schemas.md#jane_kitschemascontractschemasuri) | Метод | так |
| [component](../../../../jane-kit/reference/types/generated/jane_kit.schemas.md#jane_kitschemascontractschemascomponent) | Метод | так |
| [request_schema_uri](../../../../jane-kit/reference/types/generated/jane_kit.schemas.md#jane_kitschemascontractschemasrequest_schema_uri) | Метод | так |
| [validator](../../../../jane-kit/reference/types/generated/jane_kit.schemas.md#jane_kitschemascontractschemasvalidator) | Метод | так |
| [iter_errors](../../../../jane-kit/reference/types/generated/jane_kit.schemas.md#jane_kitschemascontractschemasiter_errors) | Метод | так |
| [field_errors](../../../../jane-kit/reference/types/generated/jane_kit.schemas.md#jane_kitschemascontractschemasfield_errors) | Метод | так |
| [validate](../../../../jane-kit/reference/types/generated/jane_kit.schemas.md#jane_kitschemascontractschemasvalidate) | Метод | так |

### Опис із вихідного коду

```text
jane-kit's shared contract validators (R17; ``format`` is checked, as before) with the registry's issues.
```

## jane_registry.validation.ContractSchemas.__init__

**Конструктор.** Код: [services/registry/src/jane_registry/validation.py:55](../../../../../../services/registry/src/jane_registry/validation.py#L55).

```python
def __init__(self, contracts: Path) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `contracts` | `Path` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.validation.ContractSchemas.issues

**Метод.** Код: [services/registry/src/jane_registry/validation.py:58](../../../../../../services/registry/src/jane_registry/validation.py#L58).

```python
def issues(self, relative: str, instance: Any, prefix: str, fragment: str='') -> list[Issue]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `relative` | `str` | `—` | positional-or-keyword |
| `instance` | `Any` | `—` | positional-or-keyword |
| `prefix` | `str` | `—` | positional-or-keyword |
| `fragment` | `str` | `''` | positional-or-keyword |

Результат: `list[Issue]`.

## jane_registry.validation.PackageValidator

**Клас.** Код: [services/registry/src/jane_registry/validation.py:81](../../../../../../services/registry/src/jane_registry/validation.py#L81).

```python
class PackageValidator:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_registry.validation.md#jane_registryvalidationpackagevalidator__init__) | Конструктор | ні |
| [schemas](jane_registry.validation.md#jane_registryvalidationpackagevalidatorschemas) | Поле екземпляра | ні |
| [require_tests](jane_registry.validation.md#jane_registryvalidationpackagevalidatorrequire_tests) | Поле екземпляра | ні |
| [referenced_paths](jane_registry.validation.md#jane_registryvalidationpackagevalidatorreferenced_paths) | Метод | ні |
| [manifest_issues](jane_registry.validation.md#jane_registryvalidationpackagevalidatormanifest_issues) | Метод | ні |
| [package_issues](jane_registry.validation.md#jane_registryvalidationpackagevalidatorpackage_issues) | Метод | ні |

## jane_registry.validation.PackageValidator.__init__

**Конструктор.** Код: [services/registry/src/jane_registry/validation.py:82](../../../../../../services/registry/src/jane_registry/validation.py#L82).

```python
def __init__(self, schemas: ContractSchemas, *, require_tests: bool=True) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `schemas` | `ContractSchemas` | `—` | positional-or-keyword |
| `require_tests` | `bool` | `True` | keyword-only |

Результат: `None`.

## jane_registry.validation.PackageValidator.schemas

**Поле екземпляра.** Код: [services/registry/src/jane_registry/validation.py:83](../../../../../../services/registry/src/jane_registry/validation.py#L83).

```python
self.schemas = schemas
```

## jane_registry.validation.PackageValidator.require_tests

**Поле екземпляра.** Код: [services/registry/src/jane_registry/validation.py:84](../../../../../../services/registry/src/jane_registry/validation.py#L84).

```python
self.require_tests = require_tests
```

## jane_registry.validation.PackageValidator.referenced_paths

**Метод.** Код: [services/registry/src/jane_registry/validation.py:104](../../../../../../services/registry/src/jane_registry/validation.py#L104).

```python
def referenced_paths(manifest: Mapping[str, Any]) -> Iterator[tuple[str, str]]:
```

Декоратори: `staticmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `manifest` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `Iterator[tuple[str, str]]`.

### Опис із вихідного коду

```text
``(JSON pointer in the manifest, package path)`` of every file the manifest refers to.
```

## jane_registry.validation.PackageValidator.manifest_issues

**Метод.** Код: [services/registry/src/jane_registry/validation.py:132](../../../../../../services/registry/src/jane_registry/validation.py#L132).

```python
def manifest_issues(self, manifest: Any, prefix: str='/manifest') -> list[Issue]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `manifest` | `Any` | `—` | positional-or-keyword |
| `prefix` | `str` | `'/manifest'` | positional-or-keyword |

Результат: `list[Issue]`.

## jane_registry.validation.PackageValidator.package_issues

**Метод.** Код: [services/registry/src/jane_registry/validation.py:137](../../../../../../services/registry/src/jane_registry/validation.py#L137).

```python
def package_issues(self, manifest: Mapping[str, Any], files: Mapping[str, bytes], prefix: str) -> list[Issue]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `manifest` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `files` | `Mapping[str, bytes]` | `—` | positional-or-keyword |
| `prefix` | `str` | `—` | positional-or-keyword |

Результат: `list[Issue]`.

### Опис із вихідного коду

```text
Checks beyond the JSON Schema. ``manifest`` is already schema-valid.
```
