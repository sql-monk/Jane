# Модуль `jane_extractor_sdk.runner`

> Згенеровано `scripts/docs_reference.py` з [libs/extractor-sdk/src/jane_extractor_sdk/runner.py](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/runner.py). Не редагуйте вручну.

In-sandbox runner: ``python -I -m jane_extractor_sdk.runner <workdir>``.

Protocol (version 1) between handler-runtime and the sandbox, all files inside ``<workdir>`` (read-only):

``request.json``::

    {"protocol": 1,
     "entry": {"module": "product_extractor.main", "callable": "extract"},
     "package_dir": "package",                  # unpacked package; &lt;package_dir>/src is put on sys.path
     "params": {...}, "test_mode": false,
     "inputs": [{"input": &lt;HandlerInput>, "content_file": "inputs/0.bin" | null}]}

The runner writes exactly one JSON document to the original stdout (user ``print`` goes to stderr)::

    {"protocol": 1,
     "results": [&lt;ExtractResult> | {"error": {"type", "message", "traceback", "stage"}}],   # one per input
     "violations": [{"kind": "network" | "process", "event": "...", "detail": "...", "input": 0}],
     "metrics": {"cpu_ms": 12, "peak_memory_mb": 31.5}}

Violations are *recorded* through an audit hook for diagnostics only; the boundary itself is the sandbox (no network namespace, read-only FS, limits). The runner never raises for extractor errors: the runtime decides the final status (``failed`` with ``execution_error`` / ``sandbox_violation`` / ``schema_mismatch``).

## Функції

### Функція `execute`

```python
def execute(
    request: Mapping[str, Any],
    workdir: Path,
    *,
    recorder: _Recorder | None = None,
) -> dict[str, Any]: ...
```

Run the entry callable for every input of ``request``; return the protocol response.

Винятки в коді функції: `TypeError`.

Код: [runner.py:120](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/runner.py#L120).

### Функція `main`

```python
def main(argv: list[str] | None = None) -> int: ...
```

Винятки в коді функції: `ValueError`.

Код: [runner.py:178](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/runner.py#L178).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `PROTOCOL_VERSION` | — | `1` |  |
