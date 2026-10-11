# jane_storage.keys

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage.keys.NO_SOURCE](#jane_storagekeysno_source)
- [jane_storage.keys.canonical_key](#jane_storagekeyscanonical_key)
- [jane_storage.keys.key_digest](#jane_storagekeyskey_digest)
- [jane_storage.keys.safe_segment](#jane_storagekeyssafe_segment)
- [jane_storage.keys.object_key](#jane_storagekeysobject_key)
- [jane_storage.keys.object_id_for](#jane_storagekeysobject_id_for)
- [jane_storage.keys.entity_delivery_key](#jane_storagekeysentity_delivery_key)
- [jane_storage.keys.object_delivery_key](#jane_storagekeysobject_delivery_key)

## jane_storage.keys.NO_SOURCE

**Константа.** Код: [services/storage/src/jane_storage/keys.py:31](../../../../../../services/storage/src/jane_storage/keys.py#L31).

```python
NO_SOURCE = '_standalone'
```

### Опис із вихідного коду

```text
Source segment of object keys for materials without ``source.source_id`` (standalone use).
```

## jane_storage.keys.canonical_key

**Функція.** Код: [services/storage/src/jane_storage/keys.py:45](../../../../../../services/storage/src/jane_storage/keys.py#L45).

```python
def canonical_key(key: Mapping[str, Any]) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `key` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
``shop-example|{"sku":"A-100"}`` for ``{"scope": "shop-example", "natural": {"sku": "A-100"}}``.
```

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/files/tests/test_files_adapter.py:35](../../../../../../services/storage/adapters/files/tests/test_files_adapter.py#L35).

```python
KEY = canonical_key({"scope": "s", "natural": {"sku": "A"}})
```

Контекст і передумови: [services/storage/adapters/mongodb/tests/test_recovery.py:57](../../../../../../services/storage/adapters/mongodb/tests/test_recovery.py#L57).

```python
key = canonical_key(record()["key"])
```

## jane_storage.keys.key_digest

**Функція.** Код: [services/storage/src/jane_storage/keys.py:51](../../../../../../services/storage/src/jane_storage/keys.py#L51).

```python
def key_digest(value: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
sha256 hex of a key; used for file/object names that must not depend on key characters.
```

### Приклади з тестів

Контекст і передумови: [services/storage/adapters/files/tests/test_compat.py:57](../../../../../../services/storage/adapters/files/tests/test_compat.py#L57).

```python
digest = key_digest(canonical_key)
```

Контекст і передумови: [services/storage/adapters/files/tests/test_compat.py:50](../../../../../../services/storage/adapters/files/tests/test_compat.py#L50).

```python
path = self._root(options) / "entities" / entity_type / f"{key_digest(canonical_key)}.json"
```

## jane_storage.keys.safe_segment

**Функція.** Код: [services/storage/src/jane_storage/keys.py:56](../../../../../../services/storage/src/jane_storage/keys.py#L56).

```python
def safe_segment(value: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
One path segment that is valid on Windows and Linux.
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_core.py:60](../../../../../../services/storage/tests/test_core.py#L60).

```python
assert safe_segment("con") == "_con"
```

Контекст і передумови: [services/storage/tests/test_core.py:61](../../../../../../services/storage/tests/test_core.py#L61).

```python
assert safe_segment('a<>:"|?*b') == "a_______b"
```

## jane_storage.keys.object_key

**Функція.** Код: [services/storage/src/jane_storage/keys.py:64](../../../../../../services/storage/src/jane_storage/keys.py#L64).

```python
def object_key(*, material_id: str, observation_id: str, source_id: str | None, fetched_at: datetime, ext: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `material_id` | `str` | `—` | keyword-only |
| `observation_id` | `str` | `—` | keyword-only |
| `source_id` | `str \| None` | `—` | keyword-only |
| `fetched_at` | `datetime` | `—` | keyword-only |
| `ext` | `str` | `—` | keyword-only |

Результат: `str`.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_core.py:52](../../../../../../services/storage/tests/test_core.py#L52).

```python
key = object_key(
        material_id="web:3704326c",
        observation_id="obs_1",
        source_id="shop-example",
        fetched_at=parse_ts("2026-09-27T23:30:00-03:00"),
        ext="html",
    )
```

## jane_storage.keys.object_id_for

**Функція.** Код: [services/storage/src/jane_storage/keys.py:80](../../../../../../services/storage/src/jane_storage/keys.py#L80).

```python
def object_id_for(object_key_: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `object_key_` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Deterministic ``object_id`` (``Id`` pattern) of an object key; the same in every adapter.
```

## jane_storage.keys.entity_delivery_key

**Функція.** Код: [services/storage/src/jane_storage/keys.py:85](../../../../../../services/storage/src/jane_storage/keys.py#L85).

```python
def entity_delivery_key(delivery_key: str, index: int) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `delivery_key` | `str` | `—` | positional-or-keyword |
| `index` | `int` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Delivery key of the ``index``-th entity (0-based, across all inputs) of an invocation.
```

## jane_storage.keys.object_delivery_key

**Функція.** Код: [services/storage/src/jane_storage/keys.py:90](../../../../../../services/storage/src/jane_storage/keys.py#L90).

```python
def object_delivery_key(delivery_key: str, index: int, kind: str='raw') -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `delivery_key` | `str` | `—` | positional-or-keyword |
| `index` | `int` | `—` | positional-or-keyword |
| `kind` | `str` | `'raw'` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Delivery key of the ``index``-th object write: the first RAW uses the invocation key itself.
```

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_core.py:62](../../../../../../services/storage/tests/test_core.py#L62).

```python
assert object_delivery_key("dk", 0) == "dk"
```

Контекст і передумови: [services/storage/tests/test_core.py:63](../../../../../../services/storage/tests/test_core.py#L63).

```python
assert object_delivery_key("dk", 1) == "dk#raw1"
```
