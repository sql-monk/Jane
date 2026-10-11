# Модуль `jane_extractor_sdk.entities`

> Згенеровано `scripts/docs_reference.py` з [libs/extractor-sdk/src/jane_extractor_sdk/entities.py](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/entities.py). Не редагуйте вручну.

Turning extractor entities into ``EntityRecord`` documents (shared by the runtime and local test runs).

## Функції

### Функція `build_key`

```python
def build_key(
    fields: Mapping[str, Any],
    key_fields: Sequence[str],
    scope: str,
) -> dict[str, Any] | None: ...
```

``EntityKey`` from ``key_fields``; ``None`` if a key field is missing or not a scalar.

Код: [entities.py:32](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/entities.py#L32).

### Функція `observation_of`

```python
def observation_of(material: Mapping[str, Any] | None) -> dict[str, Any] | None: ...
```

``ObservationOrder`` of a material: observed_at = fetched_at, sequence = revision.sequence.

Код: [entities.py:14](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/entities.py#L14).

### Функція `to_entity_record`

```python
def to_entity_record(
    raw: Mapping[str, Any],
    *,
    key_fields: Sequence[str],
    material: Mapping[str, Any] | None,
    schema_ref: str | None = None,
    provenance: Mapping[str, Any] | None = None,
) -> dict[str, Any]: ...
```

Add what the runtime owns: ``key`` (if missing), ``observation``, ``schema``, ``provenance``.

Код: [entities.py:43](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/entities.py#L43).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `DEFAULT_SCOPE` | — | `'local'` | Key scope when the material has no ``source.source_id`` (standalone run). |
