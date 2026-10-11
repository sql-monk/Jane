# Модуль `jane_llm.app`

> Згенеровано `scripts/docs_reference.py` з [services/llm/src/jane_llm/app.py](../../../../../services/llm/src/jane_llm/app.py). Не редагуйте вручну.

HTTP API of the LLM service: ``llm.v1`` (gateway) + ``handler.v1`` (LLM handler).

``/v1/health``, ``/v1/info``, ``/metrics`` and ``/v1/jobs/*`` come from jane-kit.

## Зміст

- [Функція `make_store`](#функція-make_store)
- [Функція `etag`](#функція-etag)
- [Функція `seed`](#функція-seed)
- [Функція `build_app`](#функція-build_app)

## Функції

### Функція `make_store`

```python
def make_store(settings: Settings, limits: ServiceLimits | None = None) -> Store: ...
```

Винятки в коді функції: `RuntimeError`.

Код: [app.py:77](../../../../../services/llm/src/jane_llm/app.py#L77).

### Функція `etag`

```python
def etag(doc: dict[str, Any]) -> str: ...
```

Код: [app.py:99](../../../../../services/llm/src/jane_llm/app.py#L99).

### Функція `seed`

```python
def seed(store: Store, settings: Settings) -> None: ...
```

Винятки в коді функції: `RuntimeError`.

Код: [app.py:114](../../../../../services/llm/src/jane_llm/app.py#L114).

### Функція `build_app`

```python
def build_app(
    settings: Settings | None = None,
    *,
    store: Store | None = None,
    adapters: dict[str, ProviderAdapter] | None = None,
    nonce_factory: NonceFactory = new_nonce,
    clock: Callable[[], datetime] | None = None,
) -> FastAPI: ...
```

Винятки в коді функції: `NotFound`, `ValidationFailed`, `Conflict`, `JaneError`.

Код: [app.py:151](../../../../../services/llm/src/jane_llm/app.py#L151).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `log` | — | `logging.getLogger(__name__)` |  |
| `JSON_BODY` | — | `Body(...)` |  |
| `IF_MATCH` | — | `Header(default=None, alias='If-Match')` |  |
| `BUILTIN_PACKAGES` | — | `Path(__file__).resolve().parents[2] / 'packages'` |  |
| `FAKE_PROVIDER` | — | `{'provider_id': FAKE_PROVIDER_ID, 'kind': 'fake', 'enabled': True, 'models': [{'` |  |
