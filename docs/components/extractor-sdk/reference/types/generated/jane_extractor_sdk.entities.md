# jane_extractor_sdk.entities

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_extractor_sdk.entities.DEFAULT_SCOPE](#jane_extractor_sdkentitiesdefault_scope)
- [jane_extractor_sdk.entities.observation_of](#jane_extractor_sdkentitiesobservation_of)
- [jane_extractor_sdk.entities.build_key](#jane_extractor_sdkentitiesbuild_key)
- [jane_extractor_sdk.entities.to_entity_record](#jane_extractor_sdkentitiesto_entity_record)

## jane_extractor_sdk.entities.DEFAULT_SCOPE

**Константа.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/entities.py:10](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/entities.py#L10).

```python
DEFAULT_SCOPE = 'local'
```

### Опис із вихідного коду

```text
Key scope when the material has no ``source.source_id`` (standalone run).
```

## jane_extractor_sdk.entities.observation_of

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/entities.py:14](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/entities.py#L14).

```python
def observation_of(material: Mapping[str, Any] | None) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `material` | `Mapping[str, Any] \| None` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

### Опис із вихідного коду

```text
``ObservationOrder`` of a material: observed_at = fetched_at, sequence = revision.sequence.
```

## jane_extractor_sdk.entities.build_key

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/entities.py:32](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/entities.py#L32).

```python
def build_key(fields: Mapping[str, Any], key_fields: Sequence[str], scope: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `fields` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `key_fields` | `Sequence[str]` | `—` | positional-or-keyword |
| `scope` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

### Опис із вихідного коду

```text
``EntityKey`` from ``key_fields``; ``None`` if a key field is missing or not a scalar.
```

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:211](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L211).

```python
assert build_key({"sku": "A", "n": 1}, ["sku", "n"], "s") == {
        "scope": "s",
        "natural": {"sku": "A", "n": 1},
    }
```

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:215](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L215).

```python
assert build_key({"sku": {"x": 1}}, ["sku"], "s") is None
```

## jane_extractor_sdk.entities.to_entity_record

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/entities.py:43](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/entities.py#L43).

```python
def to_entity_record(raw: Mapping[str, Any], *, key_fields: Sequence[str], material: Mapping[str, Any] | None, schema_ref: str | None=None, provenance: Mapping[str, Any] | None=None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `raw` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `key_fields` | `Sequence[str]` | `—` | keyword-only |
| `material` | `Mapping[str, Any] \| None` | `—` | keyword-only |
| `schema_ref` | `str \| None` | `None` | keyword-only |
| `provenance` | `Mapping[str, Any] \| None` | `None` | keyword-only |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
Add what the runtime owns: ``key`` (if missing), ``observation``, ``schema``, ``provenance``.
```

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:217](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L217).

```python
rec = to_entity_record(
        {"entity_type": "t", "fields": {"id": "1"}}, key_fields=["id"], material=m, schema_ref="p@1#t"
    )
```
