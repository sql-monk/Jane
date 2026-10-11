# Модуль `jane_telegram_collector.rules`

> Згенеровано `scripts/docs_reference.py` з [services/telegram-collector/src/jane_telegram_collector/rules.py](../../../../../services/telegram-collector/src/jane_telegram_collector/rules.py). Не редагуйте вручну.

Collector rules of the Telegram Collector: what this implementation supports, on top of the shared parts.

Schema validation (``collector.v1`` and ``collector-rules.schema.json``, ``oneOf`` errors explained by the discriminator) and loading by ``rules_ref`` (local package directory or archive, then the package registry, with ``digest`` and ``files[].sha256`` checks, a registry token that must be a valid HTTP header value, no transport details in errors) are jane-kit's shared :mod:`jane_kit.rules` (R17).

## Класи

### Клас `ContractSchemas`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.rules` |
| Успадкування | `CollectorSchemas` |
| Код | [rules.py:24](../../../../../services/telegram-collector/src/jane_telegram_collector/rules.py#L24) |

```python
class ContractSchemas(CollectorSchemas): ...
```

JSON Schemas of ``collector.v1`` (with cross-file ``$ref``) for request and rules validation.

#### Метод `ContractSchemas.for_service`

```python
@classmethod
def for_service(cls, configured: Path | None) -> ContractSchemas: ...
```

Код: [rules.py:28](../../../../../services/telegram-collector/src/jane_telegram_collector/rules.py#L28).

### Клас `RulesLoader`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.rules` |
| Успадкування | `_KitRulesLoader` |
| Код | [rules.py:32](../../../../../services/telegram-collector/src/jane_telegram_collector/rules.py#L32) |

```python
class RulesLoader(_KitRulesLoader): ...
```

Rules of a ``rules_ref``: ``JANE_TELEGRAM_COLLECTOR_RULES_DIR``, then ``..._REGISTRY_URL``.

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

Код: [rules.py:35](../../../../../services/telegram-collector/src/jane_telegram_collector/rules.py#L35).

## Функції

### Функція `validate_rules`

```python
def validate_rules(schemas: ContractSchemas, rules: Any) -> RulesReport: ...
```

Schema validation + what this implementation supports (web rules are valid but not executed here).

Код: [rules.py:52](../../../../../services/telegram-collector/src/jane_telegram_collector/rules.py#L52).

## Реекспорт

| Назва | Визначено в |
|---|---|
| `RulesReport` | `jane_kit.rules` |
