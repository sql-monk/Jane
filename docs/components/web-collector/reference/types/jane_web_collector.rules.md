# Модуль `jane_web_collector.rules`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/rules.py](../../../../../services/web-collector/src/jane_web_collector/rules.py). Не редагуйте вручну.

Collector rules of the Web Collector: what this implementation supports, on top of the shared parts.

Schema validation (``collector.v1`` and ``collector-rules.schema.json``, ``oneOf`` errors explained by the discriminator) and loading by ``rules_ref`` (local package directory or archive, then the package registry, with ``digest`` and ``files[].sha256`` checks) are jane-kit's shared :mod:`jane_kit.rules` (R17).

## Класи

### Клас `ContractSchemas`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.rules` |
| Успадкування | `CollectorSchemas` |
| Код | [rules.py:26](../../../../../services/web-collector/src/jane_web_collector/rules.py#L26) |

```python
class ContractSchemas(CollectorSchemas): ...
```

JSON Schemas of ``collector.v1`` (with cross-file ``$ref``) for request and rules validation.

#### Метод `ContractSchemas.for_service`

```python
@classmethod
def for_service(cls, configured: Path | None) -> ContractSchemas: ...
```

Код: [rules.py:30](../../../../../services/web-collector/src/jane_web_collector/rules.py#L30).

### Клас `RulesLoader`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.rules` |
| Успадкування | `_KitRulesLoader` |
| Код | [rules.py:34](../../../../../services/web-collector/src/jane_web_collector/rules.py#L34) |

```python
class RulesLoader(_KitRulesLoader): ...
```

Rules of a ``rules_ref``: ``JANE_WEB_COLLECTOR_RULES_DIR``, then ``JANE_WEB_COLLECTOR_REGISTRY_URL``.

#### Конструктор `RulesLoader.__init__`

```python
def __init__(
    self,
    *,
    rules_dir: Path | None,
    registry_url: str | None,
    registry_token_env: str | None,
    timeout_s: float,
) -> None: ...
```

Код: [rules.py:37](../../../../../services/web-collector/src/jane_web_collector/rules.py#L37).

## Функції

### Функція `validate_rules`

```python
def validate_rules(schemas: ContractSchemas, registry: Registry, rules: Any) -> RulesReport: ...
```

Schema validation + what this implementation supports (unsupported strategies, telegram rules).

Код: [rules.py:54](../../../../../services/web-collector/src/jane_web_collector/rules.py#L54).

## Реекспорт

| Назва | Визначено в |
|---|---|
| `RulesReport` | `jane_kit.rules` |
