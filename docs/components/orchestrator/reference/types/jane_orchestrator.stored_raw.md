# Модуль `jane_orchestrator.stored_raw`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/stored_raw.py](../../../../../services/orchestrator/src/jane_orchestrator/stored_raw.py). Не редагуйте вручну.

RAW references recorded by the orchestrator itself; no reads of storage-owned tables.

## Функції

### Функція `stored_raw_id`

```python
def stored_raw_id(
    conn: Any,
    source_id: str,
    observation_id: str | None,
    *,
    run_id: str | None = None,
    invocation_id: str | None = None,
) -> str | None: ...
```

Return a known RAW id for this observation and run, never a different observation of its URL.

A problem sample identifies its run through the invocation. Missing provenance or several distinct RAW copies is not resolved by choosing an arbitrary object: the optional API field stays absent.

Код: [stored_raw.py:8](../../../../../services/orchestrator/src/jane_orchestrator/stored_raw.py#L8).
