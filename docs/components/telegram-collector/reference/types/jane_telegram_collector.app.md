# Модуль `jane_telegram_collector.app`

> Згенеровано `scripts/docs_reference.py` з [services/telegram-collector/src/jane_telegram_collector/app.py](../../../../../services/telegram-collector/src/jane_telegram_collector/app.py). Не редагуйте вручну.

HTTP API ``collector.v1`` of the Telegram Collector (``contracts/openapi/collector.v1.yaml``).

``/v1/health``, ``/v1/info``, ``/metrics`` and ``/v1/jobs/*`` come from jane-kit; the rest is here. The service is autonomous: rules inline, from a local package or from the registry; materials are pulled with a cursor; nothing calls the orchestrator.

## Функції

### Функція `state_store_busy`

```python
def state_store_busy(exc: BaseException) -> bool: ...
```

SQLite could not take its lock within ``STATE_BUSY_TIMEOUT_MS`` (another instance holds it).

Код: [app.py:67](../../../../../services/telegram-collector/src/jane_telegram_collector/app.py#L67).

### Функція `build_app`

```python
def build_app(settings: Settings | None = None) -> FastAPI: ...
```

Винятки в коді функції: `NotFound`, `JaneError`, `ValidationFailed`.

Код: [app.py:73](../../../../../services/telegram-collector/src/jane_telegram_collector/app.py#L73).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `log` | — | `logging.getLogger(__name__)` |  |
| `CURSOR_RE` | — | `re.compile('^c_(\\d{1,18})$')` |  |
| `TERMINAL` | — | `{'succeeded', 'failed', 'cancelled'}` |  |
