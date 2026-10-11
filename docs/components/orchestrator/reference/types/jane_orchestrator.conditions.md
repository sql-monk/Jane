# Модуль `jane_orchestrator.conditions`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/conditions.py](../../../../../services/orchestrator/src/jane_orchestrator/conditions.py). Не редагуйте вручну.

Transition conditions (``TaskConfig`` ``Condition``), URL patterns and extractor bindings.

* Condition fields: ``material.*`` (Material metadata), ``result.status``, ``result.failure.kind``, ``result.entities_count``, ``entity.entity_type``, ``entity.fields.<name>``.
* ``UrlPattern`` glob: ``*`` — within one path segment, ``**`` — any part, ``?`` — one character; matched against the canonical URL without the scheme. ``regex`` — against the whole canonical URL.
* A binding matches when **every** property it sets matches (AND); a stage matches when **any** of its bindings matches (OR). Empty ``source_ids`` means the task's source.

## Зміст

- [Функція `binding_matches`](#функція-binding_matches)
- [Функція `condition_uses_entity`](#функція-condition_uses_entity)
- [Функція `evaluate`](#функція-evaluate)
- [Функція `glob_to_regex`](#функція-glob_to_regex)
- [Функція `material_url`](#функція-material_url)
- [Функція `stage_bindings_match`](#функція-stage_bindings_match)
- [Функція `url_pattern_matches`](#функція-url_pattern_matches)

## Функції

### Функція `binding_matches`

```python
def binding_matches(
    binding: Mapping[str, Any],
    material: Mapping[str, Any],
    task_source_id: str,
) -> bool: ...
```

Код: [conditions.py:78](../../../../../services/orchestrator/src/jane_orchestrator/conditions.py#L78).

### Функція `condition_uses_entity`

```python
def condition_uses_entity(cond: Mapping[str, Any] | None) -> bool: ...
```

Код: [conditions.py:168](../../../../../services/orchestrator/src/jane_orchestrator/conditions.py#L168).

### Функція `evaluate`

```python
def evaluate(cond: Mapping[str, Any] | None, ctx: Mapping[str, Any]) -> bool: ...
```

Evaluate a Condition against ``{"material": …, "result": …, "entity": …}``. ``None`` → true.

Код: [conditions.py:155](../../../../../services/orchestrator/src/jane_orchestrator/conditions.py#L155).

### Функція `glob_to_regex`

```python
@lru_cache(maxsize=PATTERN_CACHE)
def glob_to_regex(pattern: str) -> re.Pattern[str]: ...
```

Код: [conditions.py:34](../../../../../services/orchestrator/src/jane_orchestrator/conditions.py#L34).

### Функція `material_url`

```python
def material_url(material: Mapping[str, Any]) -> str | None: ...
```

Код: [conditions.py:70](../../../../../services/orchestrator/src/jane_orchestrator/conditions.py#L70).

### Функція `stage_bindings_match`

```python
def stage_bindings_match(
    bindings: Sequence[Mapping[str, Any]] | None,
    material: Mapping[str, Any],
    task_source_id: str,
) -> bool: ...
```

A stage without bindings accepts everything from its inputs.

Код: [conditions.py:102](../../../../../services/orchestrator/src/jane_orchestrator/conditions.py#L102).

### Функція `url_pattern_matches`

```python
def url_pattern_matches(pattern: Mapping[str, Any], url: str) -> bool: ...
```

Код: [conditions.py:62](../../../../../services/orchestrator/src/jane_orchestrator/conditions.py#L62).
