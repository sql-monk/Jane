# Модуль `jane_llm.testing`

> Згенеровано `scripts/docs_reference.py` з [services/llm/src/jane_llm/testing.py](../../../../../services/llm/src/jane_llm/testing.py). Не редагуйте вручну.

``POST /v1/test-runs``: package tests without writing to working data (always ``test_mode``).

## Функції

### Функція `differences`

```python
def differences(
    expected: Any,
    actual: Any,
    mode: str,
    pointer: str = '',
) -> list[dict[str, Any]]: ...
```

``exact`` — equal; ``subset`` — every expected value present (extra fields allowed).

Код: [testing.py:29](../../../../../services/llm/src/jane_llm/testing.py#L29).

### Функція `run_tests`

```python
async def run_tests(handler: LlmHandler, request: dict[str, Any]) -> dict[str, Any]: ...
```

Винятки в коді функції: `NotFound`.

Код: [testing.py:81](../../../../../services/llm/src/jane_llm/testing.py#L81).
