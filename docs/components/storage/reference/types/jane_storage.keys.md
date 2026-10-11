# Модуль `jane_storage.keys`

> Згенеровано `scripts/docs_reference.py` з [services/storage/src/jane_storage/keys.py](../../../../../services/storage/src/jane_storage/keys.py). Не редагуйте вручну.

Deterministic keys built by the storage core (contracts/docs/storage-adapter.md).

* canonical entity key: ``scope + '|' + natural`` serialized as JSON with sorted keys, no spaces (``entity.schema.json#/$defs/EntityKey``);
* object key of a RAW/result document: ``<source_id>/<yyyy>/<mm>/<dd>/<material_id>/<observation_id>.<ext>`` — filesystem safe on Windows and Linux (every character outside ``[A-Za-z0-9._-]`` becomes ``_``);
* delivery keys of the parts of one invocation.

## Зміст

- [Функція `canonical_key`](#функція-canonical_key)
- [Функція `entity_delivery_key`](#функція-entity_delivery_key)
- [Функція `key_digest`](#функція-key_digest)
- [Функція `object_delivery_key`](#функція-object_delivery_key)
- [Функція `object_id_for`](#функція-object_id_for)
- [Функція `object_key`](#функція-object_key)
- [Функція `safe_segment`](#функція-safe_segment)

## Функції

### Функція `canonical_key`

```python
def canonical_key(key: Mapping[str, Any]) -> str: ...
```

``shop-example|{"sku":"A-100"}`` for ``{"scope": "shop-example", "natural": {"sku": "A-100"}}``.

Код: [keys.py:45](../../../../../services/storage/src/jane_storage/keys.py#L45).

### Функція `entity_delivery_key`

```python
def entity_delivery_key(delivery_key: str, index: int) -> str: ...
```

Delivery key of the ``index``-th entity (0-based, across all inputs) of an invocation.

Код: [keys.py:85](../../../../../services/storage/src/jane_storage/keys.py#L85).

### Функція `key_digest`

```python
def key_digest(value: str) -> str: ...
```

sha256 hex of a key; used for file/object names that must not depend on key characters.

Код: [keys.py:51](../../../../../services/storage/src/jane_storage/keys.py#L51).

### Функція `object_delivery_key`

```python
def object_delivery_key(delivery_key: str, index: int, kind: str = 'raw') -> str: ...
```

Delivery key of the ``index``-th object write: the first RAW uses the invocation key itself.

Код: [keys.py:90](../../../../../services/storage/src/jane_storage/keys.py#L90).

### Функція `object_id_for`

```python
def object_id_for(object_key_: str) -> str: ...
```

Deterministic ``object_id`` (``Id`` pattern) of an object key; the same in every adapter.

Код: [keys.py:80](../../../../../services/storage/src/jane_storage/keys.py#L80).

### Функція `object_key`

```python
def object_key(
    *,
    material_id: str,
    observation_id: str,
    source_id: str | None,
    fetched_at: datetime,
    ext: str,
) -> str: ...
```

Код: [keys.py:64](../../../../../services/storage/src/jane_storage/keys.py#L64).

### Функція `safe_segment`

```python
def safe_segment(value: str) -> str: ...
```

One path segment that is valid on Windows and Linux.

Код: [keys.py:56](../../../../../services/storage/src/jane_storage/keys.py#L56).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `NO_SOURCE` | — | `'_standalone'` | Source segment of object keys for materials without ``source.source_id`` (standalone use). |
