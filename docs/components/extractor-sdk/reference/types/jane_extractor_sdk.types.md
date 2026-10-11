# Модуль `jane_extractor_sdk.types`

> Згенеровано `scripts/docs_reference.py` з [libs/extractor-sdk/src/jane_extractor_sdk/types.py](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py). Не редагуйте вручну.

Types of the extractor protocol (what the ``entry.callable`` of a package receives and returns).

The callable has the signature ``extract(material, params, ctx) -> ExtractResult``:

* ``material`` - a ``Material`` document (``contracts/schemas/material.schema.json``); for ``entities`` or ``data`` inputs (transform packages) it is the ``HandlerInput`` object itself;
* ``params`` - stage parameters, already validated against ``params_schema`` of the package (defaults applied);
* ``ctx`` - :class:`jane_extractor_sdk.context.Context` (content access, diagnostics, test mode).

The runtime turns an :class:`ExtractResult` into a ``HandlerResult``: it validates entity fields against the package schemas (``schema_mismatch`` -> ``failed``), fills ``key`` from ``key_fields`` when it is missing, and adds ``observation``, ``provenance`` and ``schema``. ``failed`` is never returned by the callable: raising an exception is the way to fail.

## Зміст

- [Клас `Diagnostic`](#клас-diagnostic)
- [Клас `EntityKey`](#клас-entitykey)
- [Клас `EntityOut`](#клас-entityout)
- [Клас `ExtractResult`](#клас-extractresult)
- [Клас `Unrecognized`](#клас-unrecognized)

## Класи

### Клас `Diagnostic`

| Властивість | Значення |
|---|---|
| Вид | TypedDict |
| Модуль | `jane_extractor_sdk.types` |
| Успадкування | `TypedDict` |
| Код | [types.py:60](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L60) |

```python
class Diagnostic(TypedDict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `level` | `DiagnosticLevel` | — | читання й запис |  |
| `message` | `str` | — | читання й запис |  |
| `code` | `NotRequired[str]` | — | читання й запис |  |
| `pointer` | `NotRequired[str]` | — | читання й запис |  |
| `selector` | `NotRequired[str]` | — | читання й запис |  |
| `material_id` | `NotRequired[str]` | — | читання й запис |  |

### Клас `EntityKey`

| Властивість | Значення |
|---|---|
| Вид | TypedDict |
| Модуль | `jane_extractor_sdk.types` |
| Успадкування | `TypedDict` |
| Код | [types.py:38](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L38) |

```python
class EntityKey(TypedDict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `scope` | `str` | — | читання й запис |  |
| `natural` | `dict[str, str \| int \| float \| bool]` | — | читання й запис |  |

### Клас `EntityOut`

| Властивість | Значення |
|---|---|
| Вид | TypedDict |
| Модуль | `jane_extractor_sdk.types` |
| Успадкування | `TypedDict` |
| Код | [types.py:43](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L43) |

```python
class EntityOut(TypedDict): ...
```

An entity as returned by an extractor (a subset of ``EntityRecord``).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `entity_type` | `str` | — | читання й запис |  |
| `fields` | `dict[str, Any]` | — | читання й запис |  |
| `key` | `NotRequired[EntityKey]` | — | читання й запис |  |
| `cleared` | `NotRequired[list[str]]` | — | читання й запис |  |
| `completeness` | `NotRequired[Literal['full', 'partial']]` | — | читання й запис |  |
| `confidence` | `NotRequired[float]` | — | читання й запис |  |

### Клас `ExtractResult`

| Властивість | Значення |
|---|---|
| Вид | TypedDict |
| Модуль | `jane_extractor_sdk.types` |
| Успадкування | `TypedDict` |
| Код | [types.py:69](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L69) |

```python
class ExtractResult(TypedDict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `status` | `ExtractStatus` | — | читання й запис |  |
| `entities` | `NotRequired[list[EntityOut]]` | — | читання й запис |  |
| `data` | `NotRequired[Any]` | — | читання й запис |  |
| `unrecognized` | `NotRequired[Unrecognized]` | — | читання й запис |  |
| `diagnostics` | `NotRequired[list[Diagnostic]]` | — | читання й запис |  |

### Клас `Unrecognized`

| Властивість | Значення |
|---|---|
| Вид | TypedDict |
| Модуль | `jane_extractor_sdk.types` |
| Успадкування | `TypedDict` |
| Код | [types.py:54](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L54) |

```python
class Unrecognized(TypedDict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `partial` | `bool` | — | читання й запис |  |
| `reason` | `NotRequired[str]` | — | читання й запис |  |
| `signature` | `NotRequired[str]` | — | читання й запис |  |

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `DiagnosticLevel` | — | `Literal['debug', 'info', 'warning', 'error']` |  |
| `ExtractStatus` | — | `Literal['success', 'empty', 'unrecognized']` |  |
| `Material` | — | `dict[str, Any]` | A ``Material`` document as JSON (open object, see ``material.schema.json``). |
