# jane_llm.app

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_llm.app.log](#jane_llmapplog)
- [jane_llm.app.JSON_BODY](#jane_llmappjson_body)
- [jane_llm.app.IF_MATCH](#jane_llmappif_match)
- [jane_llm.app.BUILTIN_PACKAGES](#jane_llmappbuiltin_packages)
- [jane_llm.app.FAKE_PROVIDER](#jane_llmappfake_provider)
- [jane_llm.app.make_store](#jane_llmappmake_store)
- [jane_llm.app.etag](#jane_llmappetag)
- [jane_llm.app.seed](#jane_llmappseed)
- [jane_llm.app.build_app](#jane_llmappbuild_app)

## jane_llm.app.log

**Змінна.** Код: [services/llm/src/jane_llm/app.py:56](../../../../../../services/llm/src/jane_llm/app.py#L56).

```python
log = logging.getLogger(__name__)
```

## jane_llm.app.JSON_BODY

**Константа.** Код: [services/llm/src/jane_llm/app.py:58](../../../../../../services/llm/src/jane_llm/app.py#L58).

```python
JSON_BODY = Body(...)
```

## jane_llm.app.IF_MATCH

**Константа.** Код: [services/llm/src/jane_llm/app.py:59](../../../../../../services/llm/src/jane_llm/app.py#L59).

```python
IF_MATCH = Header(default=None, alias='If-Match')
```

## jane_llm.app.BUILTIN_PACKAGES

**Константа.** Код: [services/llm/src/jane_llm/app.py:60](../../../../../../services/llm/src/jane_llm/app.py#L60).

```python
BUILTIN_PACKAGES = Path(__file__).resolve().parents[2] / 'packages'
```

## jane_llm.app.FAKE_PROVIDER

**Константа.** Код: [services/llm/src/jane_llm/app.py:62](../../../../../../services/llm/src/jane_llm/app.py#L62).

```python
FAKE_PROVIDER = {'provider_id': FAKE_PROVIDER_ID, 'kind': 'fake', 'enabled': True, 'models': [{'model_id': FAKE_MODEL_ID, 'max_context_tokens': 128000, 'supports_structured_output': True, 'pricing': {'input_per_mtok': 0, 'output_per_mtok': 0, 'currency': 'USD'}}]}
```

## jane_llm.app.make_store

**Функція.** Код: [services/llm/src/jane_llm/app.py:77](../../../../../../services/llm/src/jane_llm/app.py#L77).

```python
def make_store(settings: Settings, limits: ServiceLimits | None=None) -> Store:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits \| None` | `None` | positional-or-keyword |

Результат: `Store`.

Явні `raise` у тілі: `RuntimeError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_llm.app.etag

**Функція.** Код: [services/llm/src/jane_llm/app.py:99](../../../../../../services/llm/src/jane_llm/app.py#L99).

```python
def etag(doc: dict[str, Any]) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `doc` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `str`.

## jane_llm.app.seed

**Функція.** Код: [services/llm/src/jane_llm/app.py:114](../../../../../../services/llm/src/jane_llm/app.py#L114).

```python
def seed(store: Store, settings: Settings) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `store` | `Store` | `—` | positional-or-keyword |
| `settings` | `Settings` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `RuntimeError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_llm.app.build_app

**Функція.** Код: [services/llm/src/jane_llm/app.py:151](../../../../../../services/llm/src/jane_llm/app.py#L151).

```python
def build_app(settings: Settings | None=None, *, store: Store | None=None, adapters: dict[str, ProviderAdapter] | None=None, nonce_factory: NonceFactory=new_nonce, clock: Callable[[], datetime] | None=None) -> FastAPI:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings \| None` | `None` | positional-or-keyword |
| `store` | `Store \| None` | `None` | keyword-only |
| `adapters` | `dict[str, ProviderAdapter] \| None` | `None` | keyword-only |
| `nonce_factory` | `NonceFactory` | `new_nonce` | keyword-only |
| `clock` | `Callable[[], datetime] \| None` | `None` | keyword-only |

Результат: `FastAPI`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_llm_budget.py:87](../../../../../../services/assistant/tests/test_llm_budget.py#L87).

```python
app = build_llm_app(
        LlmSettings(log_format="console", store="memory"),
        store=MemoryStore(),
        adapters={**ADAPTERS, "fake": provider},
    )
```

Контекст і передумови: [services/llm/tests/conftest.py:102](../../../../../../services/llm/tests/conftest.py#L102).

```python
app = build_app(settings, store=store, adapters={**ADAPTERS, "fake": fake}, **kwargs)
```
