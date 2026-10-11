# Модуль `jane_handler_runtime.schemas`

> Згенеровано `scripts/docs_reference.py` з [services/handler-runtime/src/jane_handler_runtime/schemas.py](../../../../../services/handler-runtime/src/jane_handler_runtime/schemas.py). Не редагуйте вручну.

JSON Schema validation against the WP-00 contracts (``contracts/schemas``) and package schemas.

The contract validators are jane-kit's shared :class:`jane_kit.schemas.ContractSchemas` (R17; ``format`` is checked, as before); this module keeps the runtime's error shape (``validation_errors`` items) and the validation of standalone package schemas.

## Зміст

- [Клас `ContractSchemas`](#клас-contractschemas)
- [Клас `SchemaError`](#клас-schemaerror)
- [Функція `find_contracts_dir`](#функція-find_contracts_dir)
- [Функція `validate_instance`](#функція-validate_instance)

## Класи

### Клас `ContractSchemas`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_handler_runtime.schemas` |
| Успадкування | `_KitSchemas` |
| Код | [schemas.py:57](../../../../../services/handler-runtime/src/jane_handler_runtime/schemas.py#L57) |

```python
class ContractSchemas(_KitSchemas): ...
```

All ``contracts/schemas/**.schema.json``, addressable by relative path (``handler-result.schema.json`` or ``handler-result.schema.json#/$defs/TestReport``).

#### Конструктор `ContractSchemas.__init__`

```python
def __init__(self, root: Path) -> None: ...
```

Код: [schemas.py:61](../../../../../services/handler-runtime/src/jane_handler_runtime/schemas.py#L61).

#### Метод `ContractSchemas.errors`

```python
def errors(self, ref: str, instance: Any) -> list[dict[str, str]]: ...
```

Код: [schemas.py:64](../../../../../services/handler-runtime/src/jane_handler_runtime/schemas.py#L64).

#### Метод `ContractSchemas.check`

```python
def check(self, ref: str, instance: Any) -> None: ...
```

Винятки в коді методу: `ValueError`.

Код: [schemas.py:70](../../../../../services/handler-runtime/src/jane_handler_runtime/schemas.py#L70).

### Клас `SchemaError`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_handler_runtime.schemas` |
| Успадкування | `ContractsNotFound` |
| Код | [schemas.py:25](../../../../../services/handler-runtime/src/jane_handler_runtime/schemas.py#L25) |

```python
class SchemaError(ContractsNotFound): ...
```

Contracts are not available (misconfigured deployment).

## Функції

### Функція `find_contracts_dir`

```python
def find_contracts_dir(configured: Path | None) -> Path: ...
```

Винятки в коді функції: `SchemaError`.

Код: [schemas.py:29](../../../../../services/handler-runtime/src/jane_handler_runtime/schemas.py#L29).

### Функція `validate_instance`

```python
def validate_instance(
    schema: Mapping[str, Any],
    instance: Any,
    prefix: str = '',
) -> list[dict[str, str]]: ...
```

Validate against a standalone (package) schema; returns ``validation_errors`` items.

Код: [schemas.py:44](../../../../../services/handler-runtime/src/jane_handler_runtime/schemas.py#L44).
