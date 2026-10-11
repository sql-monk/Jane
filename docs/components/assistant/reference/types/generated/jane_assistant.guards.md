# jane_assistant.guards

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_assistant.guards.ALLOWED_STRATEGIES](#jane_assistantguardsallowed_strategies)
- [jane_assistant.guards.RulesCheck](#jane_assistantguardsrulescheck)
- [jane_assistant.guards.RulesCheck.__init__](#jane_assistantguardsrulescheck__init__)
- [jane_assistant.guards.RulesCheck.rules](#jane_assistantguardsrulescheckrules)
- [jane_assistant.guards.RulesCheck.rejected](#jane_assistantguardsrulescheckrejected)
- [jane_assistant.guards.sanitize_web_rules](#jane_assistantguardssanitize_web_rules)
- [jane_assistant.guards.CodeCheck](#jane_assistantguardscodecheck)
- [jane_assistant.guards.CodeCheck.__init__](#jane_assistantguardscodecheck__init__)
- [jane_assistant.guards.CodeCheck.ok](#jane_assistantguardscodecheckok)
- [jane_assistant.guards.CodeCheck.problems](#jane_assistantguardscodecheckproblems)
- [jane_assistant.guards.check_code](#jane_assistantguardscheck_code)
- [jane_assistant.guards.SchemaValidator](#jane_assistantguardsschemavalidator)
- [jane_assistant.guards.SchemaValidator.__init__](#jane_assistantguardsschemavalidator__init__)
- [jane_assistant.guards.SchemaValidator.schemas_dir](#jane_assistantguardsschemavalidatorschemas_dir)
- [jane_assistant.guards.SchemaValidator.locate](#jane_assistantguardsschemavalidatorlocate)
- [jane_assistant.guards.SchemaValidator.available](#jane_assistantguardsschemavalidatoravailable)
- [jane_assistant.guards.SchemaValidator.errors](#jane_assistantguardsschemavalidatorerrors)

## jane_assistant.guards.ALLOWED_STRATEGIES

**Константа.** Код: [services/assistant/src/jane_assistant/guards.py:41](../../../../../../services/assistant/src/jane_assistant/guards.py#L41).

```python
ALLOWED_STRATEGIES: dict[str, set[str]] = {'seed_list': {'urls', 'section', 'priority', 'strategy_id'}, 'recursive': {'seeds', 'follow', 'link_sources', 'section', 'priority', 'strategy_id'}, 'sitemap': {'urls', 'use_robots_txt', 'section', 'priority', 'strategy_id'}, 'feed': {'urls', 'autodiscover', 'section', 'priority', 'strategy_id'}, 'listing': {'start_urls', 'item_links', 'next_page', 'page_param', 'search', 'section', 'priority', 'strategy_id'}, 'url_template': {'template', 'variables', 'stop_after_consecutive_misses', 'section', 'priority', 'strategy_id'}, 'api_feed': {'url', 'items_path', 'url_path', 'lastmod_path', 'pagination', 'section', 'priority', 'strategy_id'}}
```

## jane_assistant.guards.RulesCheck

**Клас.** Код: [services/assistant/src/jane_assistant/guards.py:104](../../../../../../services/assistant/src/jane_assistant/guards.py#L104).

```python
class RulesCheck:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [rules](jane_assistant.guards.md#jane_assistantguardsrulescheckrules) | Поле | ні |
| [rejected](jane_assistant.guards.md#jane_assistantguardsrulescheckrejected) | Поле | ні |
| [__init__](jane_assistant.guards.md#jane_assistantguardsrulescheck__init__) | Конструктор dataclass | ні |

## jane_assistant.guards.RulesCheck.__init__

**Конструктор dataclass.** Код: [services/assistant/src/jane_assistant/guards.py:104](../../../../../../services/assistant/src/jane_assistant/guards.py#L104).

```python
def __init__(self, rules: dict[str, Any] | None, rejected: list[str] = <factory list>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `rules` | `dict[str, Any] \| None` | `—` | positional-or-keyword |
| `rejected` | `list[str]` | `factory: list` | positional-or-keyword |

Результат: `None`.

## jane_assistant.guards.RulesCheck.rules

**Поле.** Код: [services/assistant/src/jane_assistant/guards.py:105](../../../../../../services/assistant/src/jane_assistant/guards.py#L105).

```python
rules: dict[str, Any] | None
```

Доступ: читання — так; запис — так.

## jane_assistant.guards.RulesCheck.rejected

**Поле.** Код: [services/assistant/src/jane_assistant/guards.py:106](../../../../../../services/assistant/src/jane_assistant/guards.py#L106).

```python
rejected: list[str] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_assistant.guards.sanitize_web_rules

**Функція.** Код: [services/assistant/src/jane_assistant/guards.py:109](../../../../../../services/assistant/src/jane_assistant/guards.py#L109).

```python
def sanitize_web_rules(proposal: dict[str, Any], allowed_domains: list[str], hints: dict[str, Any] | None=None) -> RulesCheck:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `proposal` | `dict[str, Any]` | `—` | positional-or-keyword |
| `allowed_domains` | `list[str]` | `—` | positional-or-keyword |
| `hints` | `dict[str, Any] \| None` | `None` | positional-or-keyword |

Результат: `RulesCheck`.

### Опис із вихідного коду

```text
Build ``WebRules`` from a model proposal keeping only what stays inside ``allowed_domains``.
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:65](../../../../../../services/assistant/tests/test_units.py#L65).

```python
check = sanitize_web_rules(proposal, ["shop.example.test"], {"scope": {"include_subdomains": True}})
```

Контекст і передумови: [services/assistant/tests/test_units.py:97](../../../../../../services/assistant/tests/test_units.py#L97).

```python
rules = sanitize_web_rules({"strategies": [{"type": "sitemap"}]}, ["shop.example.test"]).rules
```

## jane_assistant.guards.CodeCheck

**Клас.** Код: [services/assistant/src/jane_assistant/guards.py:200](../../../../../../services/assistant/src/jane_assistant/guards.py#L200).

```python
class CodeCheck:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [ok](jane_assistant.guards.md#jane_assistantguardscodecheckok) | Поле | ні |
| [problems](jane_assistant.guards.md#jane_assistantguardscodecheckproblems) | Поле | ні |
| [__init__](jane_assistant.guards.md#jane_assistantguardscodecheck__init__) | Конструктор dataclass | ні |

## jane_assistant.guards.CodeCheck.__init__

**Конструктор dataclass.** Код: [services/assistant/src/jane_assistant/guards.py:200](../../../../../../services/assistant/src/jane_assistant/guards.py#L200).

```python
def __init__(self, ok: bool, problems: list[str] = <factory list>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `ok` | `bool` | `—` | positional-or-keyword |
| `problems` | `list[str]` | `factory: list` | positional-or-keyword |

Результат: `None`.

## jane_assistant.guards.CodeCheck.ok

**Поле.** Код: [services/assistant/src/jane_assistant/guards.py:201](../../../../../../services/assistant/src/jane_assistant/guards.py#L201).

```python
ok: bool
```

Доступ: читання — так; запис — так.

## jane_assistant.guards.CodeCheck.problems

**Поле.** Код: [services/assistant/src/jane_assistant/guards.py:202](../../../../../../services/assistant/src/jane_assistant/guards.py#L202).

```python
problems: list[str] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_assistant.guards.check_code

**Функція.** Код: [services/assistant/src/jane_assistant/guards.py:205](../../../../../../services/assistant/src/jane_assistant/guards.py#L205).

```python
def check_code(source: str, callable_name: str, allowed_modules: Iterable[str]) -> CodeCheck:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `source` | `str` | `—` | positional-or-keyword |
| `callable_name` | `str` | `—` | positional-or-keyword |
| `allowed_modules` | `Iterable[str]` | `—` | positional-or-keyword |

Результат: `CodeCheck`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:103](../../../../../../services/assistant/tests/test_units.py#L103).

```python
ok = check_code("import re\n\ndef extract(material, params, ctx):\n    return {}\n", "extract", ["re"])
```

Контекст і передумови: [services/assistant/tests/test_units.py:105](../../../../../../services/assistant/tests/test_units.py#L105).

```python
bad = check_code(
        "import socket\nfrom os import path\n\ndef run():\n    eval('1')\n    return ().__class__\n",
        "extract",
        ["re"],
    )
```

## jane_assistant.guards.SchemaValidator

**Клас.** Код: [services/assistant/src/jane_assistant/guards.py:232](../../../../../../services/assistant/src/jane_assistant/guards.py#L232).

```python
class SchemaValidator:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_assistant.guards.md#jane_assistantguardsschemavalidator__init__) | Конструктор | ні |
| [schemas_dir](jane_assistant.guards.md#jane_assistantguardsschemavalidatorschemas_dir) | Поле екземпляра | ні |
| [locate](jane_assistant.guards.md#jane_assistantguardsschemavalidatorlocate) | Метод | ні |
| [available](jane_assistant.guards.md#jane_assistantguardsschemavalidatoravailable) | Властивість | ні |
| [errors](jane_assistant.guards.md#jane_assistantguardsschemavalidatorerrors) | Метод | ні |

### Опис із вихідного коду

```text
Validates documents against ``contracts/schemas/*.schema.json`` when they are available.
```

## jane_assistant.guards.SchemaValidator.__init__

**Конструктор.** Код: [services/assistant/src/jane_assistant/guards.py:235](../../../../../../services/assistant/src/jane_assistant/guards.py#L235).

```python
def __init__(self, schemas_dir: Path | None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `schemas_dir` | `Path \| None` | `—` | positional-or-keyword |

Результат: `None`.

## jane_assistant.guards.SchemaValidator.schemas_dir

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/guards.py:236](../../../../../../services/assistant/src/jane_assistant/guards.py#L236).

```python
self.schemas_dir = schemas_dir if schemas_dir and schemas_dir.is_dir() else None
```

## jane_assistant.guards.SchemaValidator.locate

**Метод.** Код: [services/assistant/src/jane_assistant/guards.py:239](../../../../../../services/assistant/src/jane_assistant/guards.py#L239).

```python
def locate(cls, configured: Path | None) -> SchemaValidator:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `configured` | `Path \| None` | `—` | positional-or-keyword |

Результат: `SchemaValidator`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:95](../../../../../../services/assistant/tests/test_units.py#L95).

```python
v = SchemaValidator.locate(contracts)
```

## jane_assistant.guards.SchemaValidator.available

**Властивість.** Код: [services/assistant/src/jane_assistant/guards.py:251](../../../../../../services/assistant/src/jane_assistant/guards.py#L251).

```python
def available(self) -> bool:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

Доступ: читання — так; запис — ні.

## jane_assistant.guards.SchemaValidator.errors

**Метод.** Код: [services/assistant/src/jane_assistant/guards.py:254](../../../../../../services/assistant/src/jane_assistant/guards.py#L254).

```python
def errors(self, schema_file: str, instance: Any) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `schema_file` | `str` | `—` | positional-or-keyword |
| `instance` | `Any` | `—` | positional-or-keyword |

Результат: `list[str]`.
