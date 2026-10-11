# Модуль `jane_orchestrator.common`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/common.py](../../../../../services/orchestrator/src/jane_orchestrator/common.py). Не редагуйте вручну.

Small helpers shared by the orchestrator modules: ids, time, hashing, JSON pointers.

## Зміст

- [Функція `delivery_key`](#функція-delivery_key)
- [Функція `etag`](#функція-etag)
- [Функція `get_path`](#функція-get_path)
- [Функція `new_id`](#функція-new_id)
- [Функція `now`](#функція-now)
- [Функція `parse_etag`](#функція-parse_etag)
- [Функція `rfc3339`](#функція-rfc3339)

## Функції

### Функція `delivery_key`

```python
def delivery_key(run_id: str, stage_id: str, item_key: str) -> str: ...
```

Deterministic delivery key (handler-invocation.schema.json ``Delivery``, ADR-0008 §5): ``sha256(run_id | stage_id | item_key)``. A retry of the same delivery has the same key.

Код: [common.py:37](../../../../../services/orchestrator/src/jane_orchestrator/common.py#L37).

### Функція `etag`

```python
def etag(version: int) -> str: ...
```

Код: [common.py:43](../../../../../services/orchestrator/src/jane_orchestrator/common.py#L43).

### Функція `get_path`

```python
def get_path(doc: Any, dotted: str) -> tuple[bool, Any]: ...
```

``(found, value)`` for a dotted path in nested dicts (``format.media_type``).

Код: [common.py:60](../../../../../services/orchestrator/src/jane_orchestrator/common.py#L60).

### Функція `new_id`

```python
def new_id(prefix: str) -> str: ...
```

Time-ordered opaque id (ULID layout: 48-bit ms timestamp + 80 random bits), e.g. ``run_01J9...``.

Код: [common.py:16](../../../../../services/orchestrator/src/jane_orchestrator/common.py#L16).

### Функція `now`

```python
def now() -> datetime: ...
```

Код: [common.py:26](../../../../../services/orchestrator/src/jane_orchestrator/common.py#L26).

### Функція `parse_etag`

```python
def parse_etag(value: str | None) -> int | None: ...
```

``"v7"`` / ``W/"v7"`` / ``v7`` -> 7; anything else -> None (never matches).

Код: [common.py:47](../../../../../services/orchestrator/src/jane_orchestrator/common.py#L47).

### Функція `rfc3339`

```python
def rfc3339(value: datetime | None) -> str | None: ...
```

RFC 3339 UTC with ``Z`` (contract convention).

Код: [common.py:30](../../../../../services/orchestrator/src/jane_orchestrator/common.py#L30).
