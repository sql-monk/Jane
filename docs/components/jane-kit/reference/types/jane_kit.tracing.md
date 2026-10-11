# Модуль `jane_kit.tracing`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/tracing.py](../../../../../libs/jane-kit/src/jane_kit/tracing.py). Не редагуйте вручну.

W3C Trace Context (``traceparent``): continue the caller's trace, pass it on (skill jane-contracts §11).

## Функції

### Функція `child_traceparent`

```python
def child_traceparent(trace_id: str) -> str: ...
```

``traceparent`` for an outgoing call within ``trace_id`` (new span id, sampled).

Код: [tracing.py:28](../../../../../libs/jane-kit/src/jane_kit/tracing.py#L28).

### Функція `new_trace_id`

```python
def new_trace_id() -> str: ...
```

Код: [tracing.py:14](../../../../../libs/jane-kit/src/jane_kit/tracing.py#L14).

### Функція `parse_traceparent`

```python
def parse_traceparent(value: str | None) -> str | None: ...
```

Trace id from a valid ``traceparent`` header, else ``None``.

Код: [tracing.py:18](../../../../../libs/jane-kit/src/jane_kit/tracing.py#L18).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `TRACEPARENT` | — | `'traceparent'` |  |
