# Модуль `jane_handler_runtime.testrun`

> Згенеровано `scripts/docs_reference.py` з [services/handler-runtime/src/jane_handler_runtime/testrun.py](../../../../../services/handler-runtime/src/jane_handler_runtime/testrun.py). Не редагуйте вручну.

Package test runs without writing to working data (``POST /v1/test-runs``, CLI ``test``).

Every case (manifest ``tests`` and ``extra_cases``) is a separate sandbox run in ``test_mode``; the result is a ``TestReport`` (``handler-result.schema.json#/$defs/TestReport``).

## Функції

### Функція `run_tests`

```python
async def run_tests(
    executor: Executor,
    package: LoadedPackage,
    cases: Sequence[CaseSpec],
    *,
    params: Mapping[str, Any] | None = None,
    limits: Mapping[str, Any] | None = None,
) -> dict[str, Any]: ...
```

Код: [testrun.py:79](../../../../../services/handler-runtime/src/jane_handler_runtime/testrun.py#L79).

### Функція `select_cases`

```python
def select_cases(
    package: LoadedPackage,
    tests: str | Sequence[str] | None = 'all',
    extra_cases: Sequence[Mapping[str, Any]] = (),
) -> list[CaseSpec]: ...
```

Manifest tests (``all`` / ``none`` / names) + extra cases, with inputs and expected outputs loaded.

Винятки в коді функції: `ValidationFailed`, `NotFound`.

Код: [testrun.py:26](../../../../../services/handler-runtime/src/jane_handler_runtime/testrun.py#L26).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `CaseSpec` | — | `dict[str, Any]` | ``{"name", "input": HandlerInput, "params", "expected_status", "expected": HandlerOutput \| None, "compare"}`` |
