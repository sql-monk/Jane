# jane_extractor_sdk.result

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_extractor_sdk.result.entity](#jane_extractor_sdkresultentity)
- [jane_extractor_sdk.result.success](#jane_extractor_sdkresultsuccess)
- [jane_extractor_sdk.result.empty](#jane_extractor_sdkresultempty)
- [jane_extractor_sdk.result.unrecognized](#jane_extractor_sdkresultunrecognized)

## jane_extractor_sdk.result.entity

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/result.py:16](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/result.py#L16).

```python
def entity(entity_type: str, fields: Mapping[str, Any], *, key: EntityKey | None=None, cleared: Iterable[str] | None=None, completeness: Literal['full', 'partial'] | None=None, confidence: float | None=None) -> EntityOut:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `entity_type` | `str` | `—` | positional-or-keyword |
| `fields` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `key` | `EntityKey \| None` | `None` | keyword-only |
| `cleared` | `Iterable[str] \| None` | `None` | keyword-only |
| `completeness` | `Literal['full', 'partial'] \| None` | `None` | keyword-only |
| `confidence` | `float \| None` | `None` | keyword-only |

Результат: `EntityOut`.

### Опис із вихідного коду

```text
One entity. Fields whose value is ``None`` are dropped: a value that is absent from the material is
*not* sent (a missing field never means "delete it"); explicit clearing goes to ``cleared``.

``key`` may be omitted: the runtime builds it from ``key_fields`` of the package output contract and the
material's ``source.source_id`` (``"local"`` in standalone runs).
```

## jane_extractor_sdk.result.success

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/result.py:53](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/result.py#L53).

```python
def success(entities: Iterable[EntityOut] | None=None, *, data: Any=None, diagnostics: Iterable[Diagnostic] | None=None) -> ExtractResult:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `entities` | `Iterable[EntityOut] \| None` | `None` | positional-or-keyword |
| `data` | `Any` | `None` | keyword-only |
| `diagnostics` | `Iterable[Diagnostic] \| None` | `None` | keyword-only |

Результат: `ExtractResult`.

### Опис із вихідного коду

```text
Successful processing: entities (extractor) and/or ``data`` (transform).
```

## jane_extractor_sdk.result.empty

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/result.py:66](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/result.py#L66).

```python
def empty(*, diagnostics: Iterable[Diagnostic] | None=None) -> ExtractResult:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `diagnostics` | `Iterable[Diagnostic] \| None` | `None` | keyword-only |

Результат: `ExtractResult`.

### Опис із вихідного коду

```text
The material is understood and correctly contains none of the requested entities.
```

## jane_extractor_sdk.result.unrecognized

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/result.py:71](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/result.py#L71).

```python
def unrecognized(reason: str, *, signature: str | None=None, entities: Iterable[EntityOut] | None=None, diagnostics: Iterable[Diagnostic] | None=None) -> ExtractResult:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `reason` | `str` | `—` | positional-or-keyword |
| `signature` | `str \| None` | `None` | keyword-only |
| `entities` | `Iterable[EntityOut] \| None` | `None` | keyword-only |
| `diagnostics` | `Iterable[Diagnostic] \| None` | `None` | keyword-only |

Результат: `ExtractResult`.

### Опис із вихідного коду

```text
Unknown or partially parsed format. Entities parsed so far (if any) make it ``partial``.

``signature`` is a short fingerprint of the problem used to group problem samples
(e.g. ``"missing-selector:.price"``).
```
