# Модуль `jane_orchestrator.routing`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/routing.py](../../../../../services/orchestrator/src/jane_orchestrator/routing.py). Не редагуйте вручну.

Fan-out of the stage DAG: which items a material or a handler result creates downstream (pure logic).

Item keys are deterministic so a repeated delivery never creates a second item (``UNIQUE (run_id, stage_id, item_key)``):

* a material from the collect stage (or a reprocessed stored RAW): ``observation_id`` — a collector re-delivering the same observation hits the same item and the same ``delivery_key``;
* anything derived from a handler result: ``<upstream item_id>#<edge index>``.

Inputs are passed **by reference**: a Material carries its ``ContentRef`` (inline or blob) as received; entities/data are passed as returned (``entities_ref``/``data_ref`` stay references).

## Зміст

- [Клас `NewItem`](#клас-newitem)
- [Клас `UnknownDecision`](#клас-unknowndecision)
- [Функція `collect_stage_id`](#функція-collect_stage_id)
- [Функція `material_of`](#функція-material_of)
- [Функція `result_context`](#функція-result_context)
- [Функція `route_material`](#функція-route_material)
- [Функція `route_result`](#функція-route_result)

## Класи

### Клас `NewItem`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_orchestrator.routing` |
| Код | [routing.py:34](../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L34) |

```python
@dataclass
class NewItem: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `stage_id` | `str` | — | читання й запис |  |
| `item_key` | `str` | — | читання й запис |  |
| `inputs` | `list[dict[str, Any]]` | — | читання й запис |  |
| `material` | `dict[str, Any] \| None` | `None` | читання й запис |  |
| `upstream_item_id` | `str \| None` | `None` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `UnknownDecision`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_orchestrator.routing` |
| Код | [routing.py:43](../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L43) |

```python
@dataclass
class UnknownDecision: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `unknown` | `bool` | — | читання й запис |  |
| `forwarded` | `bool` | — | читання й запис |  |
| `reason` | `str` | `''` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `collect_stage_id`

```python
def collect_stage_id(config: Mapping[str, Any]) -> str: ...
```

Код: [routing.py:55](../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L55).

### Функція `material_of`

```python
def material_of(inputs: Sequence[Mapping[str, Any]] | None) -> dict[str, Any] | None: ...
```

The material an item is about (MaterialInput, or the material attached to EntitiesInput).

Код: [routing.py:59](../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L59).

### Функція `result_context`

```python
def result_context(result: Mapping[str, Any]) -> dict[str, Any]: ...
```

Код: [routing.py:128](../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L128).

### Функція `route_material`

```python
def route_material(
    config: Mapping[str, Any],
    source_id: str,
    material: dict[str, Any],
    forward_unknown: bool,
    from_stage: str | None = None,
) -> MaterialRouting: ...
```

Items for a material emitted by the collect stage (or injected at ``from_stage`` on reprocessing).

Код: [routing.py:67](../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L67).

### Функція `route_result`

```python
def route_result(
    config: Mapping[str, Any],
    source_id: str,
    stage_id: str,
    upstream_item_id: str,
    inputs: Sequence[Mapping[str, Any]] | None,
    result: Mapping[str, Any],
) -> list[NewItem]: ...
```

Items created by a completed handler item with ``result`` (HandlerResult).

Код: [routing.py:147](../../../../../services/orchestrator/src/jane_orchestrator/routing.py#L147).
