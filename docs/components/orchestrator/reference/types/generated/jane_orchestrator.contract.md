# jane_orchestrator.contract

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.contract.ContractSchemas](#jane_orchestratorcontractcontractschemas)
- [jane_orchestrator.contract.ContractSchemas.__init__](#jane_orchestratorcontractcontractschemas__init__)
- [jane_orchestrator.contract.ContractSchemas.schema_uri](#jane_orchestratorcontractcontractschemasschema_uri)
- [jane_orchestrator.contract.ContractSchemas.check](#jane_orchestratorcontractcontractschemascheck)
- [jane_orchestrator.contract.ContractSchemas.validate](#jane_orchestratorcontractcontractschemasvalidate)
- [jane_orchestrator.contract.ContractSchemas.validate_request](#jane_orchestratorcontractcontractschemasvalidate_request)

## jane_orchestrator.contract.ContractSchemas

**Клас.** Код: [services/orchestrator/src/jane_orchestrator/contract.py:23](../../../../../../services/orchestrator/src/jane_orchestrator/contract.py#L23).

```python
class ContractSchemas(KitSchemas):
```

Базові типи / інтерфейси: `KitSchemas`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_orchestrator.contract.md#jane_orchestratorcontractcontractschemas__init__) | Конструктор | ні |
| [schema_uri](jane_orchestrator.contract.md#jane_orchestratorcontractcontractschemasschema_uri) | Метод | ні |
| [check](jane_orchestrator.contract.md#jane_orchestratorcontractcontractschemascheck) | Метод | ні |
| [validate](jane_orchestrator.contract.md#jane_orchestratorcontractcontractschemasvalidate) | Метод | ні |
| [validate_request](jane_orchestrator.contract.md#jane_orchestratorcontractcontractschemasvalidate_request) | Метод | ні |
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

## jane_orchestrator.contract.ContractSchemas.__init__

**Конструктор.** Код: [services/orchestrator/src/jane_orchestrator/contract.py:24](../../../../../../services/orchestrator/src/jane_orchestrator/contract.py#L24).

```python
def __init__(self, directory: Path | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `directory` | `Path \| None` | `None` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `RuntimeError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_orchestrator.contract.ContractSchemas.schema_uri

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/contract.py:37](../../../../../../services/orchestrator/src/jane_orchestrator/contract.py#L37).

```python
def schema_uri(self, relative: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `relative` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
URI of a schema relative to ``contracts/schemas`` (``source.schema.json``, ``x.json#/$defs/Y``).
```

## jane_orchestrator.contract.ContractSchemas.check

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/contract.py:41](../../../../../../services/orchestrator/src/jane_orchestrator/contract.py#L41).

```python
def check(self, uri: str, instance: Any, prefix: str='') -> list[FieldError]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `uri` | `str` | `—` | positional-or-keyword |
| `instance` | `Any` | `—` | positional-or-keyword |
| `prefix` | `str` | `''` | positional-or-keyword |

Результат: `list[FieldError]`.

## jane_orchestrator.contract.ContractSchemas.validate

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/contract.py:44](../../../../../../services/orchestrator/src/jane_orchestrator/contract.py#L44).

```python
def validate(self, ref: str, instance: Any, prefix: str='', *, detail: str='request body does not match the contract', **options: Any) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `str` | `—` | positional-or-keyword |
| `instance` | `Any` | `—` | positional-or-keyword |
| `prefix` | `str` | `''` | positional-or-keyword |
| `detail` | `str` | `'request body does not match the contract'` | keyword-only |
| `options` | `Any` | `—` | var-keyword |

Результат: `None`.

## jane_orchestrator.contract.ContractSchemas.validate_request

**Метод.** Код: [services/orchestrator/src/jane_orchestrator/contract.py:57](../../../../../../services/orchestrator/src/jane_orchestrator/contract.py#L57).

```python
def validate_request(self, method: str, path: str, body: Any, media: str='application/json') -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `method` | `str` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |
| `body` | `Any` | `—` | positional-or-keyword |
| `media` | `str` | `'application/json'` | positional-or-keyword |

Результат: `None`.
