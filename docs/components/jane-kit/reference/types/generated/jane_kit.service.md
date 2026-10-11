# jane_kit.service

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.service.REQUEST_ID_HEADER](#jane_kitservicerequest_id_header)
- [jane_kit.service.create_app](#jane_kitservicecreate_app)
- [jane_kit.service.run](#jane_kitservicerun)

## jane_kit.service.REQUEST_ID_HEADER

**Константа.** Код: [libs/jane-kit/src/jane_kit/service.py:31](../../../../../../libs/jane-kit/src/jane_kit/service.py#L31).

```python
REQUEST_ID_HEADER = 'X-Request-ID'
```

## jane_kit.service.create_app

**Функція.** Код: [libs/jane-kit/src/jane_kit/service.py:38](../../../../../../libs/jane-kit/src/jane_kit/service.py#L38).

```python
def create_app(settings: JaneSettings, *, title: str | None=None, version: str='0.1.0', api_versions: tuple[str, ...]=('v1',), capabilities: Mapping[str, Any] | Callable[[], Mapping[str, Any]] | None=None, lifespan: Lifespan | None=None, limits: ResolvedLimits[Any] | None=None, configure_logs: bool=True, auth_scopes: ScopeTable | None=None, authenticator: Authenticator | None=None, **fastapi_kwargs: Any) -> FastAPI:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `JaneSettings` | `—` | positional-or-keyword |
| `title` | `str \| None` | `None` | keyword-only |
| `version` | `str` | `'0.1.0'` | keyword-only |
| `api_versions` | `tuple[str, ...]` | `('v1',)` | keyword-only |
| `capabilities` | `Mapping[str, Any] \| Callable[[], Mapping[str, Any]] \| None` | `None` | keyword-only |
| `lifespan` | `Lifespan \| None` | `None` | keyword-only |
| `limits` | `ResolvedLimits[Any] \| None` | `None` | keyword-only |
| `configure_logs` | `bool` | `True` | keyword-only |
| `auth_scopes` | `ScopeTable \| None` | `None` | keyword-only |
| `authenticator` | `Authenticator \| None` | `None` | keyword-only |
| `fastapi_kwargs` | `Any` | `—` | var-keyword |

Результат: `FastAPI`.

### Опис із вихідного коду

```text
Build a FastAPI app. ``app.state.health`` and ``app.state.metrics`` are ready to extend.

``limits`` (the service's resolved platform limits) is published in ``/v1/info`` as ``limits``
(``PlatformLimits``: contract-mapped defaults and hard caps, WP-00 ``ServiceInfo``); limits of a shared
platform profile that the service does not have (``ResolvedLimits.ignored``) are logged at start.

Authentication follows ``settings.auth_mode`` (:func:`jane_kit.auth.install_auth`; an incomplete
configuration raises :class:`~jane_kit.auth.AuthConfigError` here). ``auth_scopes`` maps every route
``"METHOD /path"`` to its scope (checked at start); without it handlers check scopes themselves
(:func:`jane_kit.auth.require`). ``authenticator`` replaces the one built from settings (tests).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_auth.py:63](../../../../../../libs/jane-kit/tests/test_auth.py#L63).

```python
app = create_app(s, configure_logs=False, auth_scopes=scopes, authenticator=authenticator)
```

Контекст і передумови: [libs/jane-kit/tests/test_auth.py:231](../../../../../../libs/jane-kit/tests/test_auth.py#L231).

```python
app = create_app(settings(auth_mode="api_key", api_keys=keys_doc()), configure_logs=False)
```

## jane_kit.service.run

**Функція.** Код: [libs/jane-kit/src/jane_kit/service.py:143](../../../../../../libs/jane-kit/src/jane_kit/service.py#L143).

```python
def run(app: FastAPI | str, settings: JaneSettings, **uvicorn_kwargs: Any) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `app` | `FastAPI \| str` | `—` | positional-or-keyword |
| `settings` | `JaneSettings` | `—` | positional-or-keyword |
| `uvicorn_kwargs` | `Any` | `—` | var-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Run with uvicorn using host/port from settings (logging stays ours).
```
