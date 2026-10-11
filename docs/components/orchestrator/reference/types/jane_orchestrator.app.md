# Модуль `jane_orchestrator.app`

> Згенеровано `scripts/docs_reference.py` з [services/orchestrator/src/jane_orchestrator/app.py](../../../../../services/orchestrator/src/jane_orchestrator/app.py). Не редагуйте вручну.

HTTP API of the orchestrator (``contracts/openapi/orchestrator.v1.yaml``).

``/v1/health``, ``/v1/info`` and ``/metrics`` come from jane-kit; everything else is implemented here. Request bodies are validated against the contract schemas; responses follow the contract (checked by ``tests/test_contract.py``). Worker threads (feed, items, schedules, connection sync) start with the app unless ``JANE_ORCHESTRATOR_RUN_WORKERS=false`` (then run ``python -m jane_orchestrator worker``).

## Функції

### Функція `build_app`

```python
def build_app(settings: Settings | None = None) -> FastAPI: ...
```

Винятки в коді функції: `RuntimeError`, `BadRequest`, `NotFound`.

Код: [app.py:45](../../../../../services/orchestrator/src/jane_orchestrator/app.py#L45).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `log` | — | `logging.getLogger(__name__)` |  |
| `T` | — | `TypeVar('T')` |  |
