# jane_kit.tracing

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.tracing.TRACEPARENT](#jane_kittracingtraceparent)
- [jane_kit.tracing.new_trace_id](#jane_kittracingnew_trace_id)
- [jane_kit.tracing.parse_traceparent](#jane_kittracingparse_traceparent)
- [jane_kit.tracing.child_traceparent](#jane_kittracingchild_traceparent)

## jane_kit.tracing.TRACEPARENT

**Константа.** Код: [libs/jane-kit/src/jane_kit/tracing.py:10](../../../../../../libs/jane-kit/src/jane_kit/tracing.py#L10).

```python
TRACEPARENT = 'traceparent'
```

## jane_kit.tracing.new_trace_id

**Функція.** Код: [libs/jane-kit/src/jane_kit/tracing.py:14](../../../../../../libs/jane-kit/src/jane_kit/tracing.py#L14).

```python
def new_trace_id() -> str:
```

Результат: `str`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_tracing_pagination.py:11](../../../../../../libs/jane-kit/tests/test_tracing_pagination.py#L11).

```python
trace = new_trace_id()
```

## jane_kit.tracing.parse_traceparent

**Функція.** Код: [libs/jane-kit/src/jane_kit/tracing.py:18](../../../../../../libs/jane-kit/src/jane_kit/tracing.py#L18).

```python
def parse_traceparent(value: str | None) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `str \| None` | `—` | positional-or-keyword |

Результат: `str | None`.

### Опис із вихідного коду

```text
Trace id from a valid ``traceparent`` header, else ``None``.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_clients.py:59](../../../../../../libs/jane-kit/tests/test_clients.py#L59).

```python
assert parse_traceparent(seen[0].headers["traceparent"]) == "4bf92f3577b34da6a3ce929d0e0e4736"
```

Контекст і передумови: [libs/jane-kit/tests/test_tracing_pagination.py:13](../../../../../../libs/jane-kit/tests/test_tracing_pagination.py#L13).

```python
assert parse_traceparent(header) == trace
```

## jane_kit.tracing.child_traceparent

**Функція.** Код: [libs/jane-kit/src/jane_kit/tracing.py:28](../../../../../../libs/jane-kit/src/jane_kit/tracing.py#L28).

```python
def child_traceparent(trace_id: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `trace_id` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
``traceparent`` for an outgoing call within ``trace_id`` (new span id, sampled).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_tracing_pagination.py:12](../../../../../../libs/jane-kit/tests/test_tracing_pagination.py#L12).

```python
header = child_traceparent(trace)
```
