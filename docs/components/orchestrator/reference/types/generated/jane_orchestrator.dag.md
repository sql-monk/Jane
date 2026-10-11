# jane_orchestrator.dag

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.dag.stage_map](#jane_orchestratordagstage_map)
- [jane_orchestrator.dag.topo_order](#jane_orchestratordagtopo_order)
- [jane_orchestrator.dag.effective_forward_unknown](#jane_orchestratordageffective_forward_unknown)
- [jane_orchestrator.dag.validate_task](#jane_orchestratordagvalidate_task)

## jane_orchestrator.dag.stage_map

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/dag.py:17](../../../../../../services/orchestrator/src/jane_orchestrator/dag.py#L17).

```python
def stage_map(task: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `task` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `dict[str, dict[str, Any]]`.

## jane_orchestrator.dag.topo_order

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/dag.py:21](../../../../../../services/orchestrator/src/jane_orchestrator/dag.py#L21).

```python
def topo_order(task: Mapping[str, Any]) -> list[str] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `task` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `list[str] | None`.

### Опис із вихідного коду

```text
Stage ids in topological order, or ``None`` if the graph has a cycle.
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:43](../../../../../../services/orchestrator/tests/test_logic.py#L43).

```python
order = topo_order(catalog_task())
```

## jane_orchestrator.dag.effective_forward_unknown

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/dag.py:39](../../../../../../services/orchestrator/src/jane_orchestrator/dag.py#L39).

```python
def effective_forward_unknown(task: Mapping[str, Any], source: Mapping[str, Any] | None) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `task` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `source` | `Mapping[str, Any] \| None` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
«Передавати в LLM невідомі сторінки»: task value, else source value, else false.
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:72](../../../../../../services/orchestrator/tests/test_logic.py#L72).

```python
assert effective_forward_unknown(catalog_task(), source_doc(forward_unknown=True)) is True
```

Контекст і передумови: [services/orchestrator/tests/test_logic.py:73](../../../../../../services/orchestrator/tests/test_logic.py#L73).

```python
assert (
        effective_forward_unknown(
            catalog_task(forward_unknown_to_llm=False), source_doc(forward_unknown=True)
        )
        is False
    )
```

## jane_orchestrator.dag.validate_task

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/dag.py:52](../../../../../../services/orchestrator/src/jane_orchestrator/dag.py#L52).

```python
def validate_task(task: Mapping[str, Any], source: Mapping[str, Any] | None, known_connections: set[str] | None=None) -> tuple[list[FieldError], list[FieldError]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `task` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `source` | `Mapping[str, Any] \| None` | `—` | positional-or-keyword |
| `known_connections` | `set[str] \| None` | `None` | positional-or-keyword |

Результат: `tuple[list[FieldError], list[FieldError]]`.

### Опис із вихідного коду

```text
``(errors, warnings)`` for a schema-valid TaskConfig.
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:50](../../../../../../services/orchestrator/tests/test_logic.py#L50).

```python
errors, _ = validate_task(t, source_doc())
```

Контекст і передумови: [services/orchestrator/tests/test_logic.py:54](../../../../../../services/orchestrator/tests/test_logic.py#L54).

```python
errors, _ = validate_task(t, source_doc())
```
