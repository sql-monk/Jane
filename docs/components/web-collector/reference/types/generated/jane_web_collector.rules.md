# jane_web_collector.rules

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.rules.RulesReport](#jane_web_collectorrulesrulesreport)
- [jane_web_collector.rules.ContractSchemas](#jane_web_collectorrulescontractschemas)
- [jane_web_collector.rules.ContractSchemas.for_service](#jane_web_collectorrulescontractschemasfor_service)
- [jane_web_collector.rules.RulesLoader](#jane_web_collectorrulesrulesloader)
- [jane_web_collector.rules.RulesLoader.__init__](#jane_web_collectorrulesrulesloader__init__)
- [jane_web_collector.rules.validate_rules](#jane_web_collectorrulesvalidate_rules)

## jane_web_collector.rules.RulesReport

**Повторний експорт.** Код: [services/web-collector/src/jane_web_collector/rules.py:15](../../../../../../services/web-collector/src/jane_web_collector/rules.py#L15).

```python
from jane_kit.rules import RulesReport as RulesReport
```

Повторний експорт: [jane_kit.rules.RulesReport](../../../../jane-kit/reference/types/generated/jane_kit.rules.md#jane_kitrulesrulesreport).

## jane_web_collector.rules.ContractSchemas

**Клас.** Код: [services/web-collector/src/jane_web_collector/rules.py:26](../../../../../../services/web-collector/src/jane_web_collector/rules.py#L26).

```python
class ContractSchemas(CollectorSchemas):
```

Базові типи / інтерфейси: `CollectorSchemas`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [for_service](jane_web_collector.rules.md#jane_web_collectorrulescontractschemasfor_service) | Метод | ні |
| [__init__](../../../../jane-kit/reference/types/generated/jane_kit.rules.md#jane_kitrulescollectorschemas__init__) | Конструктор | так |
| [rules_uri](../../../../jane-kit/reference/types/generated/jane_kit.rules.md#jane_kitrulescollectorschemasrules_uri) | Поле екземпляра | так |
| [locate_collector](../../../../jane-kit/reference/types/generated/jane_kit.rules.md#jane_kitrulescollectorschemaslocate_collector) | Метод | так |
| [errors](../../../../jane-kit/reference/types/generated/jane_kit.rules.md#jane_kitrulescollectorschemaserrors) | Метод | так |
| [rules_errors](../../../../jane-kit/reference/types/generated/jane_kit.rules.md#jane_kitrulescollectorschemasrules_errors) | Метод | так |
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
JSON Schemas of ``collector.v1`` (with cross-file ``$ref``) for request and rules validation.
```

## jane_web_collector.rules.ContractSchemas.for_service

**Метод.** Код: [services/web-collector/src/jane_web_collector/rules.py:30](../../../../../../services/web-collector/src/jane_web_collector/rules.py#L30).

```python
def for_service(cls, configured: Path | None) -> ContractSchemas:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `configured` | `Path \| None` | `—` | positional-or-keyword |

Результат: `ContractSchemas`.

## jane_web_collector.rules.RulesLoader

**Клас.** Код: [services/web-collector/src/jane_web_collector/rules.py:34](../../../../../../services/web-collector/src/jane_web_collector/rules.py#L34).

```python
class RulesLoader(_KitRulesLoader):
```

Базові типи / інтерфейси: `_KitRulesLoader`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.rules.md#jane_web_collectorrulesrulesloader__init__) | Конструктор | ні |
| [rules_dir](../../../../jane-kit/reference/types/generated/jane_kit.rules.md#jane_kitrulesrulesloaderrules_dir) | Поле екземпляра | так |
| [registry_url](../../../../jane-kit/reference/types/generated/jane_kit.rules.md#jane_kitrulesrulesloaderregistry_url) | Поле екземпляра | так |
| [registry_token_env](../../../../jane-kit/reference/types/generated/jane_kit.rules.md#jane_kitrulesrulesloaderregistry_token_env) | Поле екземпляра | так |
| [timeout_s](../../../../jane-kit/reference/types/generated/jane_kit.rules.md#jane_kitrulesrulesloadertimeout_s) | Поле екземпляра | так |
| [settings_prefix](../../../../jane-kit/reference/types/generated/jane_kit.rules.md#jane_kitrulesrulesloadersettings_prefix) | Поле екземпляра | так |
| [sources](../../../../jane-kit/reference/types/generated/jane_kit.rules.md#jane_kitrulesrulesloadersources) | Метод | так |
| [load](../../../../jane-kit/reference/types/generated/jane_kit.rules.md#jane_kitrulesrulesloaderload) | Метод | так |

### Опис із вихідного коду

```text
Rules of a ``rules_ref``: ``JANE_WEB_COLLECTOR_RULES_DIR``, then ``JANE_WEB_COLLECTOR_REGISTRY_URL``.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:215](../../../../../../services/web-collector/tests/test_connection_policy.py#L215).

```python
loader = RulesLoader(
        rules_dir=None,
        registry_url="https://registry.test",
        registry_token_env="JANE_REGISTRY_TOKEN",
        timeout_s=1,
    )
```

## jane_web_collector.rules.RulesLoader.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/rules.py:37](../../../../../../services/web-collector/src/jane_web_collector/rules.py#L37).

```python
def __init__(self, *, rules_dir: Path | None, registry_url: str | None, registry_token_env: str | None, timeout_s: float) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `rules_dir` | `Path \| None` | `—` | keyword-only |
| `registry_url` | `str \| None` | `—` | keyword-only |
| `registry_token_env` | `str \| None` | `—` | keyword-only |
| `timeout_s` | `float` | `—` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:215](../../../../../../services/web-collector/tests/test_connection_policy.py#L215).

```python
loader = RulesLoader(
        rules_dir=None,
        registry_url="https://registry.test",
        registry_token_env="JANE_REGISTRY_TOKEN",
        timeout_s=1,
    )
```

## jane_web_collector.rules.validate_rules

**Функція.** Код: [services/web-collector/src/jane_web_collector/rules.py:54](../../../../../../services/web-collector/src/jane_web_collector/rules.py#L54).

```python
def validate_rules(schemas: ContractSchemas, registry: Registry, rules: Any) -> RulesReport:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `schemas` | `ContractSchemas` | `—` | positional-or-keyword |
| `registry` | `Registry` | `—` | positional-or-keyword |
| `rules` | `Any` | `—` | positional-or-keyword |

Результат: `RulesReport`.

### Опис із вихідного коду

```text
Schema validation + what this implementation supports (unsupported strategies, telegram rules).
```
