# Модуль `jane_extractor_sdk.result`

> Згенеровано `scripts/docs_reference.py` з [libs/extractor-sdk/src/jane_extractor_sdk/result.py](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/result.py). Не редагуйте вручну.

Helpers that build :class:`~jane_extractor_sdk.types.ExtractResult` values (the four states of TZ §9).

``success`` / ``empty`` / ``unrecognized`` are returned; ``failed`` happens when the callable raises.

## Зміст

- [Функція `empty`](#функція-empty)
- [Функція `entity`](#функція-entity)
- [Функція `success`](#функція-success)
- [Функція `unrecognized`](#функція-unrecognized)

## Функції

### Функція `empty`

```python
def empty(*, diagnostics: Iterable[Diagnostic] | None = None) -> ExtractResult: ...
```

The material is understood and correctly contains none of the requested entities.

Код: [result.py:66](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/result.py#L66).

### Функція `entity`

```python
def entity(
    entity_type: str,
    fields: Mapping[str, Any],
    *,
    key: EntityKey | None = None,
    cleared: Iterable[str] | None = None,
    completeness: Literal['full', 'partial'] | None = None,
    confidence: float | None = None,
) -> EntityOut: ...
```

One entity. Fields whose value is ``None`` are dropped: a value that is absent from the material is *not* sent (a missing field never means "delete it"); explicit clearing goes to ``cleared``.

``key`` may be omitted: the runtime builds it from ``key_fields`` of the package output contract and the material's ``source.source_id`` (``"local"`` in standalone runs).

Код: [result.py:16](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/result.py#L16).

### Функція `success`

```python
def success(
    entities: Iterable[EntityOut] | None = None,
    *,
    data: Any = None,
    diagnostics: Iterable[Diagnostic] | None = None,
) -> ExtractResult: ...
```

Successful processing: entities (extractor) and/or ``data`` (transform).

Код: [result.py:53](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/result.py#L53).

### Функція `unrecognized`

```python
def unrecognized(
    reason: str,
    *,
    signature: str | None = None,
    entities: Iterable[EntityOut] | None = None,
    diagnostics: Iterable[Diagnostic] | None = None,
) -> ExtractResult: ...
```

Unknown or partially parsed format. Entities parsed so far (if any) make it ``partial``.

``signature`` is a short fingerprint of the problem used to group problem samples (e.g. ``"missing-selector:.price"``).

Код: [result.py:71](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/result.py#L71).
