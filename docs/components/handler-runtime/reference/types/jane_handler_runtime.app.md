# Модуль `jane_handler_runtime.app`

> Згенеровано `scripts/docs_reference.py` з [services/handler-runtime/src/jane_handler_runtime/app.py](../../../../../services/handler-runtime/src/jane_handler_runtime/app.py). Не редагуйте вручну.

HTTP API: handler protocol ``contracts/openapi/handler.v1.yaml`` for Python extractors.

``POST /v1/invocations`` (sync / async, ``Idempotency-Key`` = ``delivery.delivery_key``), ``GET /v1/invocations/{id}``, ``POST /v1/test-runs`` (always ``test_mode``), ``/v1/jobs/*``; ``/v1/health``, ``/v1/info``, ``/metrics`` come from jane-kit.

## Функції

### Функція `build_state`

```python
def build_state(settings: Settings, runtime: Runtime) -> ServiceState: ...
```

PostgreSQL state when ``state_dsn`` is set (several instances), else in-memory (one instance).

Код: [app.py:84](../../../../../services/handler-runtime/src/jane_handler_runtime/app.py#L84).

### Функція `build_app`

```python
def build_app(
    settings: Settings | None = None,
    runtime: Runtime | None = None,
    state: ServiceState | None = None,
) -> FastAPI: ...
```

Винятки в коді функції: `JaneError`, `NotFound`, `ValidationFailed`.

Код: [app.py:96](../../../../../services/handler-runtime/src/jane_handler_runtime/app.py#L96).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `log` | — | `logging.getLogger(__name__)` |  |
