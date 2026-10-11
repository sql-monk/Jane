# jane_llm.handler

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_llm.handler.render_template](#jane_llmhandlerrender_template)
- [jane_llm.handler.HandlerFailure](#jane_llmhandlerhandlerfailure)
- [jane_llm.handler.HandlerFailure.__init__](#jane_llmhandlerhandlerfailure__init__)
- [jane_llm.handler.LlmHandler](#jane_llmhandlerllmhandler)
- [jane_llm.handler.LlmHandler.__init__](#jane_llmhandlerllmhandler__init__)
- [jane_llm.handler.LlmHandler.gateway](#jane_llmhandlerllmhandlergateway)
- [jane_llm.handler.LlmHandler.loader](#jane_llmhandlerllmhandlerloader)
- [jane_llm.handler.LlmHandler.content](#jane_llmhandlerllmhandlercontent)
- [jane_llm.handler.LlmHandler.invoke](#jane_llmhandlerllmhandlerinvoke)

## jane_llm.handler.render_template

**Функція.** Код: [services/llm/src/jane_llm/handler.py:53](../../../../../../services/llm/src/jane_llm/handler.py#L53).

```python
def render_template(template: str, context: dict[str, Any]) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `template` | `str` | `—` | positional-or-keyword |
| `context` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
``{{path.to.value}}`` placeholders; values are JSON for non-strings, empty for missing.
```

## jane_llm.handler.HandlerFailure

**Клас.** Код: [services/llm/src/jane_llm/handler.py:65](../../../../../../services/llm/src/jane_llm/handler.py#L65).

```python
class HandlerFailure(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_llm.handler.md#jane_llmhandlerhandlerfailure__init__) | Конструктор | ні |

## jane_llm.handler.HandlerFailure.__init__

**Конструктор.** Код: [services/llm/src/jane_llm/handler.py:66](../../../../../../services/llm/src/jane_llm/handler.py#L66).

```python
def __init__(self, kind: str, message: str, *, retryable: bool=False, details: dict[str, Any] | None=None):
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `kind` | `str` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |
| `retryable` | `bool` | `False` | keyword-only |
| `details` | `dict[str, Any] \| None` | `None` | keyword-only |

## jane_llm.handler.LlmHandler

**Клас.** Код: [services/llm/src/jane_llm/handler.py:73](../../../../../../services/llm/src/jane_llm/handler.py#L73).

```python
class LlmHandler:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_llm.handler.md#jane_llmhandlerllmhandler__init__) | Конструктор | ні |
| [gateway](jane_llm.handler.md#jane_llmhandlerllmhandlergateway) | Поле екземпляра | ні |
| [loader](jane_llm.handler.md#jane_llmhandlerllmhandlerloader) | Поле екземпляра | ні |
| [content](jane_llm.handler.md#jane_llmhandlerllmhandlercontent) | Поле екземпляра | ні |
| [invoke](jane_llm.handler.md#jane_llmhandlerllmhandlerinvoke) | Метод | ні |

## jane_llm.handler.LlmHandler.__init__

**Конструктор.** Код: [services/llm/src/jane_llm/handler.py:74](../../../../../../services/llm/src/jane_llm/handler.py#L74).

```python
def __init__(self, gateway: Gateway, loader: PackageLoader, content: ContentReader | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `gateway` | `Gateway` | `—` | positional-or-keyword |
| `loader` | `PackageLoader` | `—` | positional-or-keyword |
| `content` | `ContentReader \| None` | `None` | positional-or-keyword |

Результат: `None`.

## jane_llm.handler.LlmHandler.gateway

**Поле екземпляра.** Код: [services/llm/src/jane_llm/handler.py:75](../../../../../../services/llm/src/jane_llm/handler.py#L75).

```python
self.gateway = gateway
```

## jane_llm.handler.LlmHandler.loader

**Поле екземпляра.** Код: [services/llm/src/jane_llm/handler.py:76](../../../../../../services/llm/src/jane_llm/handler.py#L76).

```python
self.loader = loader
```

## jane_llm.handler.LlmHandler.content

**Поле екземпляра.** Код: [services/llm/src/jane_llm/handler.py:77](../../../../../../services/llm/src/jane_llm/handler.py#L77).

```python
self.content = content or loader.content
```

## jane_llm.handler.LlmHandler.invoke

**Метод.** Код: [services/llm/src/jane_llm/handler.py:202](../../../../../../services/llm/src/jane_llm/handler.py#L202).

```python
async def invoke(self, inv: dict[str, Any], *, invocation_id: str | None=None, force_test_mode: bool=False) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `inv` | `dict[str, Any]` | `—` | positional-or-keyword |
| `invocation_id` | `str \| None` | `None` | keyword-only |
| `force_test_mode` | `bool` | `False` | keyword-only |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
Run one invocation; returns ``HandlerResult`` (never raises for handler failures).
```
