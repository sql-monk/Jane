# jane_handler_runtime.schemas

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_handler_runtime.schemas.SchemaError](#jane_handler_runtimeschemasschemaerror)
- [jane_handler_runtime.schemas.find_contracts_dir](#jane_handler_runtimeschemasfind_contracts_dir)
- [jane_handler_runtime.schemas.validate_instance](#jane_handler_runtimeschemasvalidate_instance)
- [jane_handler_runtime.schemas.ContractSchemas](#jane_handler_runtimeschemascontractschemas)
- [jane_handler_runtime.schemas.ContractSchemas.__init__](#jane_handler_runtimeschemascontractschemas__init__)
- [jane_handler_runtime.schemas.ContractSchemas.errors](#jane_handler_runtimeschemascontractschemaserrors)
- [jane_handler_runtime.schemas.ContractSchemas.check](#jane_handler_runtimeschemascontractschemascheck)

## jane_handler_runtime.schemas.SchemaError

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/schemas.py:25](../../../../../../services/handler-runtime/src/jane_handler_runtime/schemas.py#L25).

```python
class SchemaError(ContractsNotFound):
```

Базові типи / інтерфейси: `ContractsNotFound`.

### Опис із вихідного коду

```text
Contracts are not available (misconfigured deployment).
```

## jane_handler_runtime.schemas.find_contracts_dir

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/schemas.py:29](../../../../../../services/handler-runtime/src/jane_handler_runtime/schemas.py#L29).

```python
def find_contracts_dir(configured: Path | None) -> Path:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `configured` | `Path \| None` | `—` | positional-or-keyword |

Результат: `Path`.

Явні `raise` у тілі: `SchemaError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_app.py:21](../../../../../../services/handler-runtime/tests/test_app.py#L21).

```python
SCHEMAS = ContractSchemas(find_contracts_dir(None))
```

Контекст і передумови: [services/handler-runtime/tests/test_classification.py:22](../../../../../../services/handler-runtime/tests/test_classification.py#L22).

```python
SCHEMAS = ContractSchemas(find_contracts_dir(None))
```

## jane_handler_runtime.schemas.validate_instance

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/schemas.py:44](../../../../../../services/handler-runtime/src/jane_handler_runtime/schemas.py#L44).

```python
def validate_instance(schema: Mapping[str, Any], instance: Any, prefix: str='') -> list[dict[str, str]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `schema` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `instance` | `Any` | `—` | positional-or-keyword |
| `prefix` | `str` | `''` | positional-or-keyword |

Результат: `list[dict[str, str]]`.

### Опис із вихідного коду

```text
Validate against a standalone (package) schema; returns ``validation_errors`` items.
```

## jane_handler_runtime.schemas.ContractSchemas

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/schemas.py:57](../../../../../../services/handler-runtime/src/jane_handler_runtime/schemas.py#L57).

```python
class ContractSchemas(_KitSchemas):
```

Базові типи / інтерфейси: `_KitSchemas`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_handler_runtime.schemas.md#jane_handler_runtimeschemascontractschemas__init__) | Конструктор | ні |
| [errors](jane_handler_runtime.schemas.md#jane_handler_runtimeschemascontractschemaserrors) | Метод | ні |
| [check](jane_handler_runtime.schemas.md#jane_handler_runtimeschemascontractschemascheck) | Метод | ні |
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
All ``contracts/schemas/**.schema.json``, addressable by relative path (``handler-result.schema.json`` or
``handler-result.schema.json#/$defs/TestReport``).
```

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_app.py:21](../../../../../../services/handler-runtime/tests/test_app.py#L21).

```python
SCHEMAS = ContractSchemas(find_contracts_dir(None))
```

Контекст і передумови: [services/handler-runtime/tests/test_classification.py:22](../../../../../../services/handler-runtime/tests/test_classification.py#L22).

```python
SCHEMAS = ContractSchemas(find_contracts_dir(None))
```

## jane_handler_runtime.schemas.ContractSchemas.__init__

**Конструктор.** Код: [services/handler-runtime/src/jane_handler_runtime/schemas.py:61](../../../../../../services/handler-runtime/src/jane_handler_runtime/schemas.py#L61).

```python
def __init__(self, root: Path) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `root` | `Path` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_app.py:21](../../../../../../services/handler-runtime/tests/test_app.py#L21).

```python
SCHEMAS = ContractSchemas(find_contracts_dir(None))
```

Контекст і передумови: [services/handler-runtime/tests/test_classification.py:22](../../../../../../services/handler-runtime/tests/test_classification.py#L22).

```python
SCHEMAS = ContractSchemas(find_contracts_dir(None))
```

## jane_handler_runtime.schemas.ContractSchemas.errors

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/schemas.py:64](../../../../../../services/handler-runtime/src/jane_handler_runtime/schemas.py#L64).

```python
def errors(self, ref: str, instance: Any) -> list[dict[str, str]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `str` | `—` | positional-or-keyword |
| `instance` | `Any` | `—` | positional-or-keyword |

Результат: `list[dict[str, str]]`.

## jane_handler_runtime.schemas.ContractSchemas.check

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/schemas.py:70](../../../../../../services/handler-runtime/src/jane_handler_runtime/schemas.py#L70).

```python
def check(self, ref: str, instance: Any) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `str` | `—` | positional-or-keyword |
| `instance` | `Any` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_app.py:69](../../../../../../services/handler-runtime/tests/test_app.py#L69).

```python
SCHEMAS.check("handler-result.schema.json", result)
```

Контекст і передумови: [services/handler-runtime/tests/test_app.py:126](../../../../../../services/handler-runtime/tests/test_app.py#L126).

```python
SCHEMAS.check("handler-result.schema.json", result)
```
