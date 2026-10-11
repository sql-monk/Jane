# Модуль `jane_llm.providers.anthropic`

> Згенеровано `scripts/docs_reference.py` з [services/llm/src/jane_llm/providers/anthropic.py](../../../../../services/llm/src/jane_llm/providers/anthropic.py). Не редагуйте вручну.

Anthropic Messages API adapter (``POST {api_base}/v1/messages`` over httpx).

The official ``anthropic`` SDK is not used on purpose: its 1.x line depends on ``httpx2``, and installing that into the shared uv workspace switches Starlette's ``TestClient`` of every service to ``httpx2`` (breaking jane-kit's typed contract helpers). The wire format follows the Messages API docs.

Connection (``kind: llm_provider``): ``params.api_base`` (optional, default the public API), ``params.anthropic_version`` (optional), ``secret_refs.api_key`` (required). The key is resolved by this service and never leaves it. Structured output uses ``output_config.format`` (JSON Schema) when the model is marked ``supports_structured_output``; the gateway validates the reply against the schema in any case. Timeouts and retries (429, 5xx, connection errors) come from ``limits.provider``.

## Класи

### Клас `AnthropicProvider`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.providers.anthropic` |
| Код | [anthropic.py:116](../../../../../services/llm/src/jane_llm/providers/anthropic.py#L116) |

```python
class AnthropicProvider: ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `kind` | `'anthropic'` |  |

#### Конструктор `AnthropicProvider.__init__`

```python
def __init__(self, transport: httpx.AsyncBaseTransport | None = None) -> None: ...
```

Код: [anthropic.py:119](../../../../../services/llm/src/jane_llm/providers/anthropic.py#L119).

#### Метод `AnthropicProvider.complete`

```python
async def complete(
    self,
    request: ProviderRequest,
    connection: ResolvedConnection | None,
    limits: ServiceLimits,
) -> ProviderResponse: ...
```

Винятки в коді методу: `ProviderError`.

Код: [anthropic.py:122](../../../../../services/llm/src/jane_llm/providers/anthropic.py#L122).

## Функції

### Функція `api_schema`

```python
def api_schema(schema: dict[str, Any]) -> dict[str, Any] | None: ...
```

``schema`` in the subset ``output_config.format`` accepts, or ``None`` when it cannot be expressed there (a free-form object - no ``properties`` or ``additionalProperties`` other than ``false`` - or an unsupported keyword such as ``oneOf`` or ``patternProperties``).

Код: [anthropic.py:71](../../../../../services/llm/src/jane_llm/providers/anthropic.py#L71).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `DEFAULT_API_BASE` | — | `'https://api.anthropic.com'` |  |
| `DEFAULT_VERSION` | — | `'2023-06-01'` |  |
