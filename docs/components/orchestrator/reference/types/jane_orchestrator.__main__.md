# Модуль `jane_orchestrator.__main__`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/__main__.py](../../../../../services/orchestrator/src/jane_orchestrator/__main__.py). Не редагуйте вручну.

Entry point.

* ``python -m jane_orchestrator`` — API (+ worker threads unless ``JANE_ORCHESTRATOR_RUN_WORKERS=false``); host/port from ``JANE_ORCHESTRATOR_HOST/PORT``.
* ``python -m jane_orchestrator worker`` — workers only (``..._LIMITS__ENGINE__WORKERS`` threads), no HTTP; run as many processes as needed, they share the queue in PostgreSQL.

## Функції

### Функція `run_workers`

```python
def run_workers(settings: Settings) -> None: ...
```

Код: [__main__.py:26](../../../../../services/orchestrator/src/jane_orchestrator/__main__.py#L26).

### Функція `main`

```python
def main(argv: list[str] | None = None) -> None: ...
```

Код: [__main__.py:55](../../../../../services/orchestrator/src/jane_orchestrator/__main__.py#L55).
