# Модуль `jane_kit.service`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/service.py](../../../../../libs/jane-kit/src/jane_kit/service.py). Не редагуйте вручну.

FastAPI application factory with the standard Jane wiring.

``create_app`` gives every service the same behaviour: JSON logs with ``trace_id``/``request_id``, W3C ``traceparent`` continuation, access log, Problem-details errors, Prometheus ``/metrics``, ``/v1/health`` and ``/v1/info`` (WP-00 ``common.yaml``) and bearer authentication with scopes (ADR-0005, :mod:`jane_kit.auth`).

## Функції

### Функція `create_app`

```python
def create_app(
    settings: JaneSettings,
    *,
    title: str | None = None,
    version: str = '0.1.0',
    api_versions: tuple[str, ...] = ('v1',),
    capabilities: Mapping[str, Any] | Callable[[], Mapping[str, Any]] | None = None,
    lifespan: Lifespan | None = None,
    limits: ResolvedLimits[Any] | None = None,
    configure_logs: bool = True,
    auth_scopes: ScopeTable | None = None,
    authenticator: Authenticator | None = None,
    **fastapi_kwargs: Any,
) -> FastAPI: ...
```

Build a FastAPI app. ``app.state.health`` and ``app.state.metrics`` are ready to extend.

``limits`` (the service's resolved platform limits) is published in ``/v1/info`` as ``limits`` (``PlatformLimits``: contract-mapped defaults and hard caps, WP-00 ``ServiceInfo``); limits of a shared platform profile that the service does not have (``ResolvedLimits.ignored``) are logged at start.

Authentication follows ``settings.auth_mode`` (:func:`jane_kit.auth.install_auth`; an incomplete configuration raises :class:`~jane_kit.auth.AuthConfigError` here). ``auth_scopes`` maps every route ``"METHOD /path"`` to its scope (checked at start); without it handlers check scopes themselves (:func:`jane_kit.auth.require`). ``authenticator`` replaces the one built from settings (tests).

Код: [service.py:39](../../../../../libs/jane-kit/src/jane_kit/service.py#L39).

### Функція `run`

```python
def run(app: FastAPI | str, settings: JaneSettings, **uvicorn_kwargs: Any) -> None: ...
```

Run with uvicorn using host/port from settings (logging stays ours).

Код: [service.py:146](../../../../../libs/jane-kit/src/jane_kit/service.py#L146).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `REQUEST_ID_HEADER` | — | `'X-Request-ID'` |  |
