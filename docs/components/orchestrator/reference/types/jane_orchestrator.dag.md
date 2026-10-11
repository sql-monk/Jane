# Модуль `jane_orchestrator.dag`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/dag.py](../../../../../services/orchestrator/src/jane_orchestrator/dag.py). Не редагуйте вручну.

Semantic validation of ``TaskConfig`` beyond the JSON Schema (task-config.schema.json description): exactly one ``collect`` stage, acyclic graph, every ``from`` refers to an existing stage, every handler stage has an input; plus orchestrator checks (``select`` fits the upstream kind, regexes compile, connections exist, the «unknown pages» flag warning).

## Зміст

- [Функція `effective_forward_unknown`](#функція-effective_forward_unknown)
- [Функція `stage_map`](#функція-stage_map)
- [Функція `topo_order`](#функція-topo_order)
- [Функція `validate_task`](#функція-validate_task)

## Функції

### Функція `effective_forward_unknown`

```python
def effective_forward_unknown(
    task: Mapping[str, Any],
    source: Mapping[str, Any] | None,
) -> bool: ...
```

«Передавати в LLM невідомі сторінки»: task value, else source value, else false.

Код: [dag.py:39](../../../../../services/orchestrator/src/jane_orchestrator/dag.py#L39).

### Функція `stage_map`

```python
def stage_map(task: Mapping[str, Any]) -> dict[str, dict[str, Any]]: ...
```

Код: [dag.py:17](../../../../../services/orchestrator/src/jane_orchestrator/dag.py#L17).

### Функція `topo_order`

```python
def topo_order(task: Mapping[str, Any]) -> list[str] | None: ...
```

Stage ids in topological order, or ``None`` if the graph has a cycle.

Код: [dag.py:21](../../../../../services/orchestrator/src/jane_orchestrator/dag.py#L21).

### Функція `validate_task`

```python
def validate_task(
    task: Mapping[str, Any],
    source: Mapping[str, Any] | None,
    known_connections: set[str] | None = None,
) -> tuple[list[FieldError], list[FieldError]]: ...
```

``(errors, warnings)`` for a schema-valid TaskConfig.

Код: [dag.py:52](../../../../../services/orchestrator/src/jane_orchestrator/dag.py#L52).
