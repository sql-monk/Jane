# jane_extractor_sdk.types

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_extractor_sdk.types.ExtractStatus](#jane_extractor_sdktypesextractstatus)
- [jane_extractor_sdk.types.DiagnosticLevel](#jane_extractor_sdktypesdiagnosticlevel)
- [jane_extractor_sdk.types.Material](#jane_extractor_sdktypesmaterial)
- [jane_extractor_sdk.types.EntityKey](#jane_extractor_sdktypesentitykey)
- [jane_extractor_sdk.types.EntityKey.scope](#jane_extractor_sdktypesentitykeyscope)
- [jane_extractor_sdk.types.EntityKey.natural](#jane_extractor_sdktypesentitykeynatural)
- [jane_extractor_sdk.types.EntityOut](#jane_extractor_sdktypesentityout)
- [jane_extractor_sdk.types.EntityOut.entity_type](#jane_extractor_sdktypesentityoutentity_type)
- [jane_extractor_sdk.types.EntityOut.fields](#jane_extractor_sdktypesentityoutfields)
- [jane_extractor_sdk.types.EntityOut.key](#jane_extractor_sdktypesentityoutkey)
- [jane_extractor_sdk.types.EntityOut.cleared](#jane_extractor_sdktypesentityoutcleared)
- [jane_extractor_sdk.types.EntityOut.completeness](#jane_extractor_sdktypesentityoutcompleteness)
- [jane_extractor_sdk.types.EntityOut.confidence](#jane_extractor_sdktypesentityoutconfidence)
- [jane_extractor_sdk.types.Unrecognized](#jane_extractor_sdktypesunrecognized)
- [jane_extractor_sdk.types.Unrecognized.partial](#jane_extractor_sdktypesunrecognizedpartial)
- [jane_extractor_sdk.types.Unrecognized.reason](#jane_extractor_sdktypesunrecognizedreason)
- [jane_extractor_sdk.types.Unrecognized.signature](#jane_extractor_sdktypesunrecognizedsignature)
- [jane_extractor_sdk.types.Diagnostic](#jane_extractor_sdktypesdiagnostic)
- [jane_extractor_sdk.types.Diagnostic.level](#jane_extractor_sdktypesdiagnosticlevel)
- [jane_extractor_sdk.types.Diagnostic.message](#jane_extractor_sdktypesdiagnosticmessage)
- [jane_extractor_sdk.types.Diagnostic.code](#jane_extractor_sdktypesdiagnosticcode)
- [jane_extractor_sdk.types.Diagnostic.pointer](#jane_extractor_sdktypesdiagnosticpointer)
- [jane_extractor_sdk.types.Diagnostic.selector](#jane_extractor_sdktypesdiagnosticselector)
- [jane_extractor_sdk.types.Diagnostic.material_id](#jane_extractor_sdktypesdiagnosticmaterial_id)
- [jane_extractor_sdk.types.ExtractResult](#jane_extractor_sdktypesextractresult)
- [jane_extractor_sdk.types.ExtractResult.status](#jane_extractor_sdktypesextractresultstatus)
- [jane_extractor_sdk.types.ExtractResult.entities](#jane_extractor_sdktypesextractresultentities)
- [jane_extractor_sdk.types.ExtractResult.data](#jane_extractor_sdktypesextractresultdata)
- [jane_extractor_sdk.types.ExtractResult.unrecognized](#jane_extractor_sdktypesextractresultunrecognized)
- [jane_extractor_sdk.types.ExtractResult.diagnostics](#jane_extractor_sdktypesextractresultdiagnostics)

## jane_extractor_sdk.types.ExtractStatus

**Змінна.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:31](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L31).

```python
ExtractStatus = Literal['success', 'empty', 'unrecognized']
```

## jane_extractor_sdk.types.DiagnosticLevel

**Змінна.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:32](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L32).

```python
DiagnosticLevel = Literal['debug', 'info', 'warning', 'error']
```

## jane_extractor_sdk.types.Material

**Змінна.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:34](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L34).

```python
Material = dict[str, Any]
```

### Опис із вихідного коду

```text
A ``Material`` document as JSON (open object, see ``material.schema.json``).
```

## jane_extractor_sdk.types.EntityKey

**Клас.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:38](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L38).

```python
class EntityKey(TypedDict):
```

Базові типи / інтерфейси: `TypedDict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [scope](jane_extractor_sdk.types.md#jane_extractor_sdktypesentitykeyscope) | Поле | ні |
| [natural](jane_extractor_sdk.types.md#jane_extractor_sdktypesentitykeynatural) | Поле | ні |

## jane_extractor_sdk.types.EntityKey.scope

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:39](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L39).

```python
scope: str
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.EntityKey.natural

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:40](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L40).

```python
natural: dict[str, str | int | float | bool]
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.EntityOut

**Клас.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:43](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L43).

```python
class EntityOut(TypedDict):
```

Базові типи / інтерфейси: `TypedDict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [entity_type](jane_extractor_sdk.types.md#jane_extractor_sdktypesentityoutentity_type) | Поле | ні |
| [fields](jane_extractor_sdk.types.md#jane_extractor_sdktypesentityoutfields) | Поле | ні |
| [key](jane_extractor_sdk.types.md#jane_extractor_sdktypesentityoutkey) | Поле | ні |
| [cleared](jane_extractor_sdk.types.md#jane_extractor_sdktypesentityoutcleared) | Поле | ні |
| [completeness](jane_extractor_sdk.types.md#jane_extractor_sdktypesentityoutcompleteness) | Поле | ні |
| [confidence](jane_extractor_sdk.types.md#jane_extractor_sdktypesentityoutconfidence) | Поле | ні |

### Опис із вихідного коду

```text
An entity as returned by an extractor (a subset of ``EntityRecord``).
```

## jane_extractor_sdk.types.EntityOut.entity_type

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:46](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L46).

```python
entity_type: str
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.EntityOut.fields

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:47](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L47).

```python
fields: dict[str, Any]
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.EntityOut.key

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:48](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L48).

```python
key: NotRequired[EntityKey]
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.EntityOut.cleared

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:49](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L49).

```python
cleared: NotRequired[list[str]]
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.EntityOut.completeness

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:50](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L50).

```python
completeness: NotRequired[Literal['full', 'partial']]
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.EntityOut.confidence

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:51](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L51).

```python
confidence: NotRequired[float]
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.Unrecognized

**Клас.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:54](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L54).

```python
class Unrecognized(TypedDict):
```

Базові типи / інтерфейси: `TypedDict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [partial](jane_extractor_sdk.types.md#jane_extractor_sdktypesunrecognizedpartial) | Поле | ні |
| [reason](jane_extractor_sdk.types.md#jane_extractor_sdktypesunrecognizedreason) | Поле | ні |
| [signature](jane_extractor_sdk.types.md#jane_extractor_sdktypesunrecognizedsignature) | Поле | ні |

## jane_extractor_sdk.types.Unrecognized.partial

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:55](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L55).

```python
partial: bool
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.Unrecognized.reason

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:56](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L56).

```python
reason: NotRequired[str]
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.Unrecognized.signature

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:57](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L57).

```python
signature: NotRequired[str]
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.Diagnostic

**Клас.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:60](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L60).

```python
class Diagnostic(TypedDict):
```

Базові типи / інтерфейси: `TypedDict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [level](jane_extractor_sdk.types.md#jane_extractor_sdktypesdiagnosticlevel) | Поле | ні |
| [message](jane_extractor_sdk.types.md#jane_extractor_sdktypesdiagnosticmessage) | Поле | ні |
| [code](jane_extractor_sdk.types.md#jane_extractor_sdktypesdiagnosticcode) | Поле | ні |
| [pointer](jane_extractor_sdk.types.md#jane_extractor_sdktypesdiagnosticpointer) | Поле | ні |
| [selector](jane_extractor_sdk.types.md#jane_extractor_sdktypesdiagnosticselector) | Поле | ні |
| [material_id](jane_extractor_sdk.types.md#jane_extractor_sdktypesdiagnosticmaterial_id) | Поле | ні |

## jane_extractor_sdk.types.Diagnostic.level

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:61](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L61).

```python
level: DiagnosticLevel
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.Diagnostic.message

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:62](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L62).

```python
message: str
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.Diagnostic.code

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:63](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L63).

```python
code: NotRequired[str]
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.Diagnostic.pointer

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:64](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L64).

```python
pointer: NotRequired[str]
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.Diagnostic.selector

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:65](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L65).

```python
selector: NotRequired[str]
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.Diagnostic.material_id

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:66](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L66).

```python
material_id: NotRequired[str]
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.ExtractResult

**Клас.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:69](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L69).

```python
class ExtractResult(TypedDict):
```

Базові типи / інтерфейси: `TypedDict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [status](jane_extractor_sdk.types.md#jane_extractor_sdktypesextractresultstatus) | Поле | ні |
| [entities](jane_extractor_sdk.types.md#jane_extractor_sdktypesextractresultentities) | Поле | ні |
| [data](jane_extractor_sdk.types.md#jane_extractor_sdktypesextractresultdata) | Поле | ні |
| [unrecognized](jane_extractor_sdk.types.md#jane_extractor_sdktypesextractresultunrecognized) | Поле | ні |
| [diagnostics](jane_extractor_sdk.types.md#jane_extractor_sdktypesextractresultdiagnostics) | Поле | ні |

## jane_extractor_sdk.types.ExtractResult.status

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:70](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L70).

```python
status: ExtractStatus
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.ExtractResult.entities

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:71](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L71).

```python
entities: NotRequired[list[EntityOut]]
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.ExtractResult.data

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:72](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L72).

```python
data: NotRequired[Any]
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.ExtractResult.unrecognized

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:73](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L73).

```python
unrecognized: NotRequired[Unrecognized]
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.types.ExtractResult.diagnostics

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/types.py:74](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/types.py#L74).

```python
diagnostics: NotRequired[list[Diagnostic]]
```

Доступ: читання — так; запис — так.
