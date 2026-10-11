# jane_llm.providers.base

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_llm.providers.base.ResolvedConnection](#jane_llmprovidersbaseresolvedconnection)
- [jane_llm.providers.base.ResolvedConnection.__init__](#jane_llmprovidersbaseresolvedconnection__init__)
- [jane_llm.providers.base.ResolvedConnection.connection_id](#jane_llmprovidersbaseresolvedconnectionconnection_id)
- [jane_llm.providers.base.ResolvedConnection.kind](#jane_llmprovidersbaseresolvedconnectionkind)
- [jane_llm.providers.base.ResolvedConnection.params](#jane_llmprovidersbaseresolvedconnectionparams)
- [jane_llm.providers.base.ResolvedConnection.secrets](#jane_llmprovidersbaseresolvedconnectionsecrets)
- [jane_llm.providers.base.ProviderRequest](#jane_llmprovidersbaseproviderrequest)
- [jane_llm.providers.base.ProviderRequest.__init__](#jane_llmprovidersbaseproviderrequest__init__)
- [jane_llm.providers.base.ProviderRequest.model_id](#jane_llmprovidersbaseproviderrequestmodel_id)
- [jane_llm.providers.base.ProviderRequest.system](#jane_llmprovidersbaseproviderrequestsystem)
- [jane_llm.providers.base.ProviderRequest.user](#jane_llmprovidersbaseproviderrequestuser)
- [jane_llm.providers.base.ProviderRequest.max_output_tokens](#jane_llmprovidersbaseproviderrequestmax_output_tokens)
- [jane_llm.providers.base.ProviderRequest.output_schema](#jane_llmprovidersbaseproviderrequestoutput_schema)
- [jane_llm.providers.base.ProviderRequest.temperature](#jane_llmprovidersbaseproviderrequesttemperature)
- [jane_llm.providers.base.ProviderRequest.structured_output](#jane_llmprovidersbaseproviderrequeststructured_output)
- [jane_llm.providers.base.ProviderResponse](#jane_llmprovidersbaseproviderresponse)
- [jane_llm.providers.base.ProviderResponse.__init__](#jane_llmprovidersbaseproviderresponse__init__)
- [jane_llm.providers.base.ProviderResponse.text](#jane_llmprovidersbaseproviderresponsetext)
- [jane_llm.providers.base.ProviderResponse.input_tokens](#jane_llmprovidersbaseproviderresponseinput_tokens)
- [jane_llm.providers.base.ProviderResponse.output_tokens](#jane_llmprovidersbaseproviderresponseoutput_tokens)
- [jane_llm.providers.base.ProviderResponse.finish_reason](#jane_llmprovidersbaseproviderresponsefinish_reason)
- [jane_llm.providers.base.ProviderError](#jane_llmprovidersbaseprovidererror)
- [jane_llm.providers.base.ProviderError.__init__](#jane_llmprovidersbaseprovidererror__init__)
- [jane_llm.providers.base.ProviderError.retryable](#jane_llmprovidersbaseprovidererrorretryable)
- [jane_llm.providers.base.ProviderAdapter](#jane_llmprovidersbaseprovideradapter)
- [jane_llm.providers.base.ProviderAdapter.kind](#jane_llmprovidersbaseprovideradapterkind)
- [jane_llm.providers.base.ProviderAdapter.complete](#jane_llmprovidersbaseprovideradaptercomplete)

## jane_llm.providers.base.ResolvedConnection

**Клас.** Код: [services/llm/src/jane_llm/providers/base.py:13](../../../../../../services/llm/src/jane_llm/providers/base.py#L13).

```python
class ResolvedConnection:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [connection_id](jane_llm.providers.base.md#jane_llmprovidersbaseresolvedconnectionconnection_id) | Поле | ні |
| [kind](jane_llm.providers.base.md#jane_llmprovidersbaseresolvedconnectionkind) | Поле | ні |
| [params](jane_llm.providers.base.md#jane_llmprovidersbaseresolvedconnectionparams) | Поле | ні |
| [secrets](jane_llm.providers.base.md#jane_llmprovidersbaseresolvedconnectionsecrets) | Поле | ні |
| [__init__](jane_llm.providers.base.md#jane_llmprovidersbaseresolvedconnection__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
A managed connection with secret values resolved in this service's environment (never logged).
```

## jane_llm.providers.base.ResolvedConnection.__init__

**Конструктор dataclass.** Код: [services/llm/src/jane_llm/providers/base.py:13](../../../../../../services/llm/src/jane_llm/providers/base.py#L13).

```python
def __init__(self, connection_id: str, kind: str, params: dict[str, Any] = <factory dict>, secrets: dict[str, str] = <factory dict>) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `connection_id` | `str` | `—` | positional-or-keyword |
| `kind` | `str` | `—` | positional-or-keyword |
| `params` | `dict[str, Any]` | `factory: dict` | positional-or-keyword |
| `secrets` | `dict[str, str]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

## jane_llm.providers.base.ResolvedConnection.connection_id

**Поле.** Код: [services/llm/src/jane_llm/providers/base.py:16](../../../../../../services/llm/src/jane_llm/providers/base.py#L16).

```python
connection_id: str
```

Доступ: читання — так; запис — ні.

## jane_llm.providers.base.ResolvedConnection.kind

**Поле.** Код: [services/llm/src/jane_llm/providers/base.py:17](../../../../../../services/llm/src/jane_llm/providers/base.py#L17).

```python
kind: str
```

Доступ: читання — так; запис — ні.

## jane_llm.providers.base.ResolvedConnection.params

**Поле.** Код: [services/llm/src/jane_llm/providers/base.py:18](../../../../../../services/llm/src/jane_llm/providers/base.py#L18).

```python
params: dict[str, Any] = field(default_factory=dict)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_llm.providers.base.ResolvedConnection.secrets

**Поле.** Код: [services/llm/src/jane_llm/providers/base.py:19](../../../../../../services/llm/src/jane_llm/providers/base.py#L19).

```python
secrets: dict[str, str] = field(default_factory=dict, repr=False)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict",
  "repr": "False"
}
```

## jane_llm.providers.base.ProviderRequest

**Клас.** Код: [services/llm/src/jane_llm/providers/base.py:23](../../../../../../services/llm/src/jane_llm/providers/base.py#L23).

```python
class ProviderRequest:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_id](jane_llm.providers.base.md#jane_llmprovidersbaseproviderrequestmodel_id) | Поле | ні |
| [system](jane_llm.providers.base.md#jane_llmprovidersbaseproviderrequestsystem) | Поле | ні |
| [user](jane_llm.providers.base.md#jane_llmprovidersbaseproviderrequestuser) | Поле | ні |
| [max_output_tokens](jane_llm.providers.base.md#jane_llmprovidersbaseproviderrequestmax_output_tokens) | Поле | ні |
| [output_schema](jane_llm.providers.base.md#jane_llmprovidersbaseproviderrequestoutput_schema) | Поле | ні |
| [temperature](jane_llm.providers.base.md#jane_llmprovidersbaseproviderrequesttemperature) | Поле | ні |
| [structured_output](jane_llm.providers.base.md#jane_llmprovidersbaseproviderrequeststructured_output) | Поле | ні |
| [__init__](jane_llm.providers.base.md#jane_llmprovidersbaseproviderrequest__init__) | Конструктор dataclass | ні |

## jane_llm.providers.base.ProviderRequest.__init__

**Конструктор dataclass.** Код: [services/llm/src/jane_llm/providers/base.py:23](../../../../../../services/llm/src/jane_llm/providers/base.py#L23).

```python
def __init__(self, model_id: str, system: str, user: str, max_output_tokens: int, output_schema: dict[str, Any] | None = None, temperature: float | None = None, structured_output: bool = False) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `model_id` | `str` | `—` | positional-or-keyword |
| `system` | `str` | `—` | positional-or-keyword |
| `user` | `str` | `—` | positional-or-keyword |
| `max_output_tokens` | `int` | `—` | positional-or-keyword |
| `output_schema` | `dict[str, Any] \| None` | `None` | positional-or-keyword |
| `temperature` | `float \| None` | `None` | positional-or-keyword |
| `structured_output` | `bool` | `False` | positional-or-keyword |

Результат: `None`.

## jane_llm.providers.base.ProviderRequest.model_id

**Поле.** Код: [services/llm/src/jane_llm/providers/base.py:24](../../../../../../services/llm/src/jane_llm/providers/base.py#L24).

```python
model_id: str
```

Доступ: читання — так; запис — ні.

## jane_llm.providers.base.ProviderRequest.system

**Поле.** Код: [services/llm/src/jane_llm/providers/base.py:25](../../../../../../services/llm/src/jane_llm/providers/base.py#L25).

```python
system: str
```

Доступ: читання — так; запис — ні.

## jane_llm.providers.base.ProviderRequest.user

**Поле.** Код: [services/llm/src/jane_llm/providers/base.py:26](../../../../../../services/llm/src/jane_llm/providers/base.py#L26).

```python
user: str
```

Доступ: читання — так; запис — ні.

## jane_llm.providers.base.ProviderRequest.max_output_tokens

**Поле.** Код: [services/llm/src/jane_llm/providers/base.py:27](../../../../../../services/llm/src/jane_llm/providers/base.py#L27).

```python
max_output_tokens: int
```

Доступ: читання — так; запис — ні.

## jane_llm.providers.base.ProviderRequest.output_schema

**Поле.** Код: [services/llm/src/jane_llm/providers/base.py:28](../../../../../../services/llm/src/jane_llm/providers/base.py#L28).

```python
output_schema: dict[str, Any] | None = None
```

Доступ: читання — так; запис — ні.

## jane_llm.providers.base.ProviderRequest.temperature

**Поле.** Код: [services/llm/src/jane_llm/providers/base.py:29](../../../../../../services/llm/src/jane_llm/providers/base.py#L29).

```python
temperature: float | None = None
```

Доступ: читання — так; запис — ні.

## jane_llm.providers.base.ProviderRequest.structured_output

**Поле.** Код: [services/llm/src/jane_llm/providers/base.py:30](../../../../../../services/llm/src/jane_llm/providers/base.py#L30).

```python
structured_output: bool = False
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
The model supports native structured output (``supports_structured_output``).
```

## jane_llm.providers.base.ProviderResponse

**Клас.** Код: [services/llm/src/jane_llm/providers/base.py:35](../../../../../../services/llm/src/jane_llm/providers/base.py#L35).

```python
class ProviderResponse:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [text](jane_llm.providers.base.md#jane_llmprovidersbaseproviderresponsetext) | Поле | ні |
| [input_tokens](jane_llm.providers.base.md#jane_llmprovidersbaseproviderresponseinput_tokens) | Поле | ні |
| [output_tokens](jane_llm.providers.base.md#jane_llmprovidersbaseproviderresponseoutput_tokens) | Поле | ні |
| [finish_reason](jane_llm.providers.base.md#jane_llmprovidersbaseproviderresponsefinish_reason) | Поле | ні |
| [__init__](jane_llm.providers.base.md#jane_llmprovidersbaseproviderresponse__init__) | Конструктор dataclass | ні |

## jane_llm.providers.base.ProviderResponse.__init__

**Конструктор dataclass.** Код: [services/llm/src/jane_llm/providers/base.py:35](../../../../../../services/llm/src/jane_llm/providers/base.py#L35).

```python
def __init__(self, text: str, input_tokens: int, output_tokens: int, finish_reason: str = 'stop') -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `text` | `str` | `—` | positional-or-keyword |
| `input_tokens` | `int` | `—` | positional-or-keyword |
| `output_tokens` | `int` | `—` | positional-or-keyword |
| `finish_reason` | `str` | `'stop'` | positional-or-keyword |

Результат: `None`.

## jane_llm.providers.base.ProviderResponse.text

**Поле.** Код: [services/llm/src/jane_llm/providers/base.py:36](../../../../../../services/llm/src/jane_llm/providers/base.py#L36).

```python
text: str
```

Доступ: читання — так; запис — ні.

## jane_llm.providers.base.ProviderResponse.input_tokens

**Поле.** Код: [services/llm/src/jane_llm/providers/base.py:37](../../../../../../services/llm/src/jane_llm/providers/base.py#L37).

```python
input_tokens: int
```

Доступ: читання — так; запис — ні.

## jane_llm.providers.base.ProviderResponse.output_tokens

**Поле.** Код: [services/llm/src/jane_llm/providers/base.py:38](../../../../../../services/llm/src/jane_llm/providers/base.py#L38).

```python
output_tokens: int
```

Доступ: читання — так; запис — ні.

## jane_llm.providers.base.ProviderResponse.finish_reason

**Поле.** Код: [services/llm/src/jane_llm/providers/base.py:39](../../../../../../services/llm/src/jane_llm/providers/base.py#L39).

```python
finish_reason: str = 'stop'
```

Доступ: читання — так; запис — ні.

## jane_llm.providers.base.ProviderError

**Клас.** Код: [services/llm/src/jane_llm/providers/base.py:42](../../../../../../services/llm/src/jane_llm/providers/base.py#L42).

```python
class ProviderError(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_llm.providers.base.md#jane_llmprovidersbaseprovidererror__init__) | Конструктор | ні |
| [retryable](jane_llm.providers.base.md#jane_llmprovidersbaseprovidererrorretryable) | Поле екземпляра | ні |

### Опис із вихідного коду

```text
The provider call did not produce a response.
```

## jane_llm.providers.base.ProviderError.__init__

**Конструктор.** Код: [services/llm/src/jane_llm/providers/base.py:45](../../../../../../services/llm/src/jane_llm/providers/base.py#L45).

```python
def __init__(self, message: str, *, retryable: bool) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |
| `retryable` | `bool` | `—` | keyword-only |

Результат: `None`.

## jane_llm.providers.base.ProviderError.retryable

**Поле екземпляра.** Код: [services/llm/src/jane_llm/providers/base.py:47](../../../../../../services/llm/src/jane_llm/providers/base.py#L47).

```python
self.retryable = retryable
```

## jane_llm.providers.base.ProviderAdapter

**Клас.** Код: [services/llm/src/jane_llm/providers/base.py:50](../../../../../../services/llm/src/jane_llm/providers/base.py#L50).

```python
class ProviderAdapter(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [kind](jane_llm.providers.base.md#jane_llmprovidersbaseprovideradapterkind) | Поле | ні |
| [complete](jane_llm.providers.base.md#jane_llmprovidersbaseprovideradaptercomplete) | Метод | ні |

## jane_llm.providers.base.ProviderAdapter.kind

**Поле.** Код: [services/llm/src/jane_llm/providers/base.py:51](../../../../../../services/llm/src/jane_llm/providers/base.py#L51).

```python
kind: str
```

Доступ: читання — так; запис — так.

## jane_llm.providers.base.ProviderAdapter.complete

**Метод.** Код: [services/llm/src/jane_llm/providers/base.py:53](../../../../../../services/llm/src/jane_llm/providers/base.py#L53).

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
