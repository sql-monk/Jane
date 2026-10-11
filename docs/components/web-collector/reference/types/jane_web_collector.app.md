# Модуль `jane_web_collector.app`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/app.py](../../../../../services/web-collector/src/jane_web_collector/app.py). Не редагуйте вручну.

HTTP API ``collector.v1`` of the Web Collector (``contracts/openapi/collector.v1.yaml``).

``/v1/health``, ``/v1/info``, ``/metrics`` and ``/v1/jobs/*`` come from jane-kit; the rest is here. The service is autonomous: rules inline, from a local package or from the registry; materials are pulled with a cursor; no call to the orchestrator exists.

## Зміст

- [Функція `state_store_busy`](#функція-state_store_busy)
- [Функція `build_app`](#функція-build_app)
- [Функція `rfc3339_ts`](#функція-rfc3339_ts)
- [Функція `rfc3339_now`](#функція-rfc3339_now)

## Функції

### Функція `state_store_busy`

```python
def state_store_busy(exc: BaseException) -> bool: ...
```

SQLite could not take its lock within ``STATE_BUSY_TIMEOUT_MS`` (another instance holds it).

Код: [app.py:63](../../../../../services/web-collector/src/jane_web_collector/app.py#L63).

### Функція `build_app`

```python
def build_app(settings: Settings | None = None) -> FastAPI: ...
```

Винятки в коді функції: `NotFound`, `JaneError`, `ValidationFailed`.

Код: [app.py:69](../../../../../services/web-collector/src/jane_web_collector/app.py#L69).

### Функція `rfc3339_ts`

```python
def rfc3339_ts(ts: float) -> str: ...
```

Код: [app.py:353](../../../../../services/web-collector/src/jane_web_collector/app.py#L353).

### Функція `rfc3339_now`

```python
def rfc3339_now() -> str: ...
```

Код: [app.py:357](../../../../../services/web-collector/src/jane_web_collector/app.py#L357).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `log` | — | `logging.getLogger(__name__)` |  |
| `CURSOR_RE` | — | `re.compile('^c_(\\d{1,18})$')` |  |
| `TERMINAL` | — | `{'succeeded', 'failed', 'cancelled'}` |  |
