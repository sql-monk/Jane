# Модуль `jane_orchestrator.contract`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/contract.py](../../../../../services/orchestrator/src/jane_orchestrator/contract.py). Не редагуйте вручну.

Request validation against ``contracts/openapi/orchestrator.v1.yaml`` (the source of truth).

The orchestrator does not re-declare contract documents (Source, TaskConfig, Connection, PlatformLimits…) as its own models: request bodies are validated with the JSON Schemas of the contract, and violations become ``422 validation_failed`` with JSON-pointer ``errors``. The validators are jane-kit's shared :class:`jane_kit.schemas.ContractSchemas` (R17); pointers follow RFC 6901.

## Класи

### Клас `ContractSchemas`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_orchestrator.contract` |
| Успадкування | `KitSchemas` |
| Код | [contract.py:23](../../../../../services/orchestrator/src/jane_orchestrator/contract.py#L23) |

```python
class ContractSchemas(KitSchemas): ...
```

#### Конструктор `ContractSchemas.__init__`

```python
def __init__(self, directory: Path | None = None) -> None: ...
```

Винятки в коді методу: `RuntimeError`.

Код: [contract.py:24](../../../../../services/orchestrator/src/jane_orchestrator/contract.py#L24).

#### Метод `ContractSchemas.schema_uri`

```python
def schema_uri(self, relative: str) -> str: ...
```

URI of a schema relative to ``contracts/schemas`` (``source.schema.json``, ``x.json#/$defs/Y``).

Код: [contract.py:37](../../../../../services/orchestrator/src/jane_orchestrator/contract.py#L37).

#### Метод `ContractSchemas.check`

```python
def check(self, uri: str, instance: Any, prefix: str = '') -> list[FieldError]: ...
```

Код: [contract.py:41](../../../../../services/orchestrator/src/jane_orchestrator/contract.py#L41).

#### Метод `ContractSchemas.validate`

```python
def validate(
    self,
    ref: str,
    instance: Any,
    prefix: str = '',
    *,
    detail: str = 'request body does not match the contract',
    **options: Any,
) -> None: ...
```

Код: [contract.py:44](../../../../../services/orchestrator/src/jane_orchestrator/contract.py#L44).

#### Метод `ContractSchemas.validate_request`

```python
def validate_request(
    self,
    method: str,
    path: str,
    body: Any,
    media: str = 'application/json',
) -> None: ...
```

Код: [contract.py:57](../../../../../services/orchestrator/src/jane_orchestrator/contract.py#L57).
