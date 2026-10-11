# jane_llm.providers.anthropic

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_llm.providers.anthropic.DEFAULT_API_BASE](#jane_llmprovidersanthropicdefault_api_base)
- [jane_llm.providers.anthropic.DEFAULT_VERSION](#jane_llmprovidersanthropicdefault_version)
- [jane_llm.providers.anthropic.api_schema](#jane_llmprovidersanthropicapi_schema)
- [jane_llm.providers.anthropic.AnthropicProvider](#jane_llmprovidersanthropicanthropicprovider)
- [jane_llm.providers.anthropic.AnthropicProvider.kind](#jane_llmprovidersanthropicanthropicproviderkind)
- [jane_llm.providers.anthropic.AnthropicProvider.__init__](#jane_llmprovidersanthropicanthropicprovider__init__)
- [jane_llm.providers.anthropic.AnthropicProvider.transport](#jane_llmprovidersanthropicanthropicprovidertransport)
- [jane_llm.providers.anthropic.AnthropicProvider.complete](#jane_llmprovidersanthropicanthropicprovidercomplete)

## jane_llm.providers.anthropic.DEFAULT_API_BASE

**Константа.** Код: [services/llm/src/jane_llm/providers/anthropic.py:29](../../../../../../services/llm/src/jane_llm/providers/anthropic.py#L29).

```python
DEFAULT_API_BASE = 'https://api.anthropic.com'
```

## jane_llm.providers.anthropic.DEFAULT_VERSION

**Константа.** Код: [services/llm/src/jane_llm/providers/anthropic.py:30](../../../../../../services/llm/src/jane_llm/providers/anthropic.py#L30).

```python
DEFAULT_VERSION = '2023-06-01'
```

## jane_llm.providers.anthropic.api_schema

**Функція.** Код: [services/llm/src/jane_llm/providers/anthropic.py:71](../../../../../../services/llm/src/jane_llm/providers/anthropic.py#L71).

```python
def api_schema(schema: dict[str, Any]) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `schema` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

### Опис із вихідного коду

```text
``schema`` in the subset ``output_config.format`` accepts, or ``None`` when it cannot be expressed
there (a free-form object - no ``properties`` or ``additionalProperties`` other than ``false`` - or an
unsupported keyword such as ``oneOf`` or ``patternProperties``).
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_service.py:687](../../../../../../services/llm/tests/test_service.py#L687).

```python
assert api_schema(schema) == {
        "title": "classify",
        "type": "object",
        "required": ["items"],
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "confidence"],
                    "properties": {
                        "name": {"type": "string"},
                        "confidence": {"type": "number"},
                        "kind": {"type": "string", "enum": ["a", "b"], "format": "uri"},
                    },
                    "additionalProperties": False,
                },
            }
        },
        "additionalProperties": False,
    }
```

Контекст і передумови: [services/llm/tests/test_service.py:709](../../../../../../services/llm/tests/test_service.py#L709).

```python
assert api_schema({"type": "object", "properties": {"minimum": {"type": "integer"}}}) == {
        "type": "object",
        "properties": {"minimum": {"type": "integer"}},
        "additionalProperties": False,
    }
```

## jane_llm.providers.anthropic.AnthropicProvider

**Клас.** Код: [services/llm/src/jane_llm/providers/anthropic.py:116](../../../../../../services/llm/src/jane_llm/providers/anthropic.py#L116).

```python
class AnthropicProvider:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [kind](jane_llm.providers.anthropic.md#jane_llmprovidersanthropicanthropicproviderkind) | Поле | ні |
| [__init__](jane_llm.providers.anthropic.md#jane_llmprovidersanthropicanthropicprovider__init__) | Конструктор | ні |
| [transport](jane_llm.providers.anthropic.md#jane_llmprovidersanthropicanthropicprovidertransport) | Поле екземпляра | ні |
| [complete](jane_llm.providers.anthropic.md#jane_llmprovidersanthropicanthropicprovidercomplete) | Метод | ні |

## jane_llm.providers.anthropic.AnthropicProvider.kind

**Поле.** Код: [services/llm/src/jane_llm/providers/anthropic.py:117](../../../../../../services/llm/src/jane_llm/providers/anthropic.py#L117).

```python
kind = 'anthropic'
```

Доступ: читання — так; запис — так.

## jane_llm.providers.anthropic.AnthropicProvider.__init__

**Конструктор.** Код: [services/llm/src/jane_llm/providers/anthropic.py:119](../../../../../../services/llm/src/jane_llm/providers/anthropic.py#L119).

```python
def __init__(self, transport: httpx.AsyncBaseTransport | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `transport` | `httpx.AsyncBaseTransport \| None` | `None` | positional-or-keyword |

Результат: `None`.

## jane_llm.providers.anthropic.AnthropicProvider.transport

**Поле екземпляра.** Код: [services/llm/src/jane_llm/providers/anthropic.py:120](../../../../../../services/llm/src/jane_llm/providers/anthropic.py#L120).

```python
self.transport = transport
```

## jane_llm.providers.anthropic.AnthropicProvider.complete

**Метод.** Код: [services/llm/src/jane_llm/providers/anthropic.py:122](../../../../../../services/llm/src/jane_llm/providers/anthropic.py#L122).

```python
async def complete(self, request: ProviderRequest, connection: ResolvedConnection | None, limits: ServiceLimits) -> ProviderResponse:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `request` | `ProviderRequest` | `—` | positional-or-keyword |
| `connection` | `ResolvedConnection \| None` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |

Результат: `ProviderResponse`.

Явні `raise` у тілі: `ProviderError`. Винятки викликаних залежностей описуються у ручному довіднику.
