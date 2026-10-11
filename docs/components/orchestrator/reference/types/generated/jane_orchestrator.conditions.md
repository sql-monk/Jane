# jane_orchestrator.conditions

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.conditions.glob_to_regex](#jane_orchestratorconditionsglob_to_regex)
- [jane_orchestrator.conditions.url_pattern_matches](#jane_orchestratorconditionsurl_pattern_matches)
- [jane_orchestrator.conditions.material_url](#jane_orchestratorconditionsmaterial_url)
- [jane_orchestrator.conditions.binding_matches](#jane_orchestratorconditionsbinding_matches)
- [jane_orchestrator.conditions.stage_bindings_match](#jane_orchestratorconditionsstage_bindings_match)
- [jane_orchestrator.conditions.evaluate](#jane_orchestratorconditionsevaluate)
- [jane_orchestrator.conditions.condition_uses_entity](#jane_orchestratorconditionscondition_uses_entity)

## jane_orchestrator.conditions.glob_to_regex

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/conditions.py:34](../../../../../../services/orchestrator/src/jane_orchestrator/conditions.py#L34).

```python
def glob_to_regex(pattern: str) -> re.Pattern[str]:
```

Декоратори: `lru_cache(maxsize=PATTERN_CACHE)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `pattern` | `str` | `—` | positional-or-keyword |

Результат: `re.Pattern[str]`.

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:94](../../../../../../services/orchestrator/tests/test_logic.py#L94).

```python
assert glob_to_regex(pattern).pattern.startswith("^")
```

## jane_orchestrator.conditions.url_pattern_matches

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/conditions.py:62](../../../../../../services/orchestrator/src/jane_orchestrator/conditions.py#L62).

```python
def url_pattern_matches(pattern: Mapping[str, Any], url: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `pattern` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:98](../../../../../../services/orchestrator/tests/test_logic.py#L98).

```python
assert url_pattern_matches(
        {"type": "regex", "value": r"^https://shop\.example\.test/product/"},
        "https://shop.example.test/product/x",
    )
```

Контекст і передумови: [services/orchestrator/tests/test_logic.py:93](../../../../../../services/orchestrator/tests/test_logic.py#L93).

```python
assert url_pattern_matches({"value": pattern}, url) is ok
```

## jane_orchestrator.conditions.material_url

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/conditions.py:70](../../../../../../services/orchestrator/src/jane_orchestrator/conditions.py#L70).

```python
def material_url(material: Mapping[str, Any]) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `material` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `str | None`.

## jane_orchestrator.conditions.binding_matches

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/conditions.py:78](../../../../../../services/orchestrator/src/jane_orchestrator/conditions.py#L78).

```python
def binding_matches(binding: Mapping[str, Any], material: Mapping[str, Any], task_source_id: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `binding` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `material` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `task_source_id` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_orchestrator.conditions.stage_bindings_match

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/conditions.py:102](../../../../../../services/orchestrator/src/jane_orchestrator/conditions.py#L102).

```python
def stage_bindings_match(bindings: Sequence[Mapping[str, Any]] | None, material: Mapping[str, Any], task_source_id: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `bindings` | `Sequence[Mapping[str, Any]] \| None` | `—` | positional-or-keyword |
| `material` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `task_source_id` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
A stage without bindings accepts everything from its inputs.
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:106](../../../../../../services/orchestrator/tests/test_logic.py#L106).

```python
assert stage_bindings_match(None, m, "shop-example")
```

Контекст і передумови: [services/orchestrator/tests/test_logic.py:107](../../../../../../services/orchestrator/tests/test_logic.py#L107).

```python
assert stage_bindings_match([{"sections": ["products"], "media_types": ["text/html"]}], m, "shop-example")
```

## jane_orchestrator.conditions.evaluate

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/conditions.py:155](../../../../../../services/orchestrator/src/jane_orchestrator/conditions.py#L155).

```python
def evaluate(cond: Mapping[str, Any] | None, ctx: Mapping[str, Any]) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cond` | `Mapping[str, Any] \| None` | `—` | positional-or-keyword |
| `ctx` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
Evaluate a Condition against ``{"material": …, "result": …, "entity": …}``. ``None`` → true.
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:126](../../../../../../services/orchestrator/tests/test_logic.py#L126).

```python
assert evaluate({"field": "material.format.media_type", "op": "eq", "value": "text/html"}, ctx)
```

Контекст і передумови: [services/orchestrator/tests/test_logic.py:127](../../../../../../services/orchestrator/tests/test_logic.py#L127).

```python
assert evaluate({"field": "result.status", "op": "in", "value": ["success", "unrecognized"]}, ctx)
```

## jane_orchestrator.conditions.condition_uses_entity

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/conditions.py:168](../../../../../../services/orchestrator/src/jane_orchestrator/conditions.py#L168).

```python
def condition_uses_entity(cond: Mapping[str, Any] | None) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cond` | `Mapping[str, Any] \| None` | `—` | positional-or-keyword |

Результат: `bool`.
