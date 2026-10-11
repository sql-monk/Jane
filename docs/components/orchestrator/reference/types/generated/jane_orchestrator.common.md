# jane_orchestrator.common

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_orchestrator.common.new_id](#jane_orchestratorcommonnew_id)
- [jane_orchestrator.common.now](#jane_orchestratorcommonnow)
- [jane_orchestrator.common.rfc3339](#jane_orchestratorcommonrfc3339)
- [jane_orchestrator.common.delivery_key](#jane_orchestratorcommondelivery_key)
- [jane_orchestrator.common.etag](#jane_orchestratorcommonetag)
- [jane_orchestrator.common.parse_etag](#jane_orchestratorcommonparse_etag)
- [jane_orchestrator.common.get_path](#jane_orchestratorcommonget_path)

## jane_orchestrator.common.new_id

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/common.py:16](../../../../../../services/orchestrator/src/jane_orchestrator/common.py#L16).

```python
def new_id(prefix: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `prefix` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Time-ordered opaque id (ULID layout: 48-bit ms timestamp + 80 random bits), e.g. ``run_01J9...``.
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:329](../../../../../../services/orchestrator/tests/test_logic.py#L329).

```python
a, b = new_id("run"), new_id("run")
```

## jane_orchestrator.common.now

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/common.py:26](../../../../../../services/orchestrator/src/jane_orchestrator/common.py#L26).

```python
def now() -> datetime:
```

Результат: `datetime`.

## jane_orchestrator.common.rfc3339

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/common.py:30](../../../../../../services/orchestrator/src/jane_orchestrator/common.py#L30).

```python
def rfc3339(value: datetime | None) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `datetime \| None` | `—` | positional-or-keyword |

Результат: `str | None`.

### Опис із вихідного коду

```text
RFC 3339 UTC with ``Z`` (contract convention).
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:332](../../../../../../services/orchestrator/tests/test_logic.py#L332).

```python
assert rfc3339(T0) == "2026-09-27T10:00:00.000Z"
```

## jane_orchestrator.common.delivery_key

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/common.py:37](../../../../../../services/orchestrator/src/jane_orchestrator/common.py#L37).

```python
def delivery_key(run_id: str, stage_id: str, item_key: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `run_id` | `str` | `—` | positional-or-keyword |
| `stage_id` | `str` | `—` | positional-or-keyword |
| `item_key` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Deterministic delivery key (handler-invocation.schema.json ``Delivery``, ADR-0008 §5):
``sha256(run_id | stage_id | item_key)``. A retry of the same delivery has the same key.
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:323](../../../../../../services/orchestrator/tests/test_logic.py#L323).

```python
assert delivery_key("run_1", "s", "obs_1") == delivery_key("run_1", "s", "obs_1")
```

Контекст і передумови: [services/orchestrator/tests/test_logic.py:324](../../../../../../services/orchestrator/tests/test_logic.py#L324).

```python
assert delivery_key("run_1", "s", "obs_1") != delivery_key("run_2", "s", "obs_1")
```

## jane_orchestrator.common.etag

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/common.py:43](../../../../../../services/orchestrator/src/jane_orchestrator/common.py#L43).

```python
def etag(version: int) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `version` | `int` | `—` | positional-or-keyword |

Результат: `str`.

## jane_orchestrator.common.parse_etag

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/common.py:47](../../../../../../services/orchestrator/src/jane_orchestrator/common.py#L47).

```python
def parse_etag(value: str | None) -> int | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `str \| None` | `—` | positional-or-keyword |

Результат: `int | None`.

### Опис із вихідного коду

```text
``"v7"`` / ``W/"v7"`` / ``v7`` -> 7; anything else -> None (never matches).
```

### Приклади з тестів

Контекст і передумови: [services/orchestrator/tests/test_logic.py:331](../../../../../../services/orchestrator/tests/test_logic.py#L331).

```python
assert parse_etag('"v7"') == 7 and parse_etag('W/"v3"') == 3 and parse_etag("junk") == -1
```

## jane_orchestrator.common.get_path

**Функція.** Код: [services/orchestrator/src/jane_orchestrator/common.py:60](../../../../../../services/orchestrator/src/jane_orchestrator/common.py#L60).

```python
def get_path(doc: Any, dotted: str) -> tuple[bool, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `doc` | `Any` | `—` | positional-or-keyword |
| `dotted` | `str` | `—` | positional-or-keyword |

Результат: `tuple[bool, Any]`.

### Опис із вихідного коду

```text
``(found, value)`` for a dotted path in nested dicts (``format.media_type``).
```
