# Модуль `jane_llm.providers.base`

> Згенеровано `scripts/docs_reference.py` з [services/llm/src/jane_llm/providers/base.py](../../../../../services/llm/src/jane_llm/providers/base.py). Не редагуйте вручну.

Provider adapter interface. Adapters receive fully rendered prompts and resolved connections.

## Зміст

- [Клас `ResolvedConnection`](#клас-resolvedconnection)
- [Клас `ProviderRequest`](#клас-providerrequest)
- [Клас `ProviderResponse`](#клас-providerresponse)
- [Клас `ProviderError`](#клас-providererror)
- [Клас `ProviderAdapter`](#клас-provideradapter)

## Класи

### Клас `ResolvedConnection`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_llm.providers.base` |
| Код | [base.py:13](../../../../../services/llm/src/jane_llm/providers/base.py#L13) |

```python
@dataclass(frozen=True)
class ResolvedConnection: ...
```

A managed connection with secret values resolved in this service's environment (never logged).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `connection_id` | `str` | — | читання |  |
| `kind` | `str` | — | читання |  |
| `params` | `dict[str, Any]` | `field(default_factory=dict)` | читання |  |
| `secrets` | `dict[str, str]` | `field(default_factory=dict, repr=False)` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `ProviderRequest`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_llm.providers.base` |
| Код | [base.py:23](../../../../../services/llm/src/jane_llm/providers/base.py#L23) |

```python
@dataclass(frozen=True)
class ProviderRequest: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `model_id` | `str` | — | читання |  |
| `system` | `str` | — | читання |  |
| `user` | `str` | — | читання |  |
| `max_output_tokens` | `int` | — | читання |  |
| `output_schema` | `dict[str, Any] \| None` | `None` | читання |  |
| `temperature` | `float \| None` | `None` | читання |  |
| `structured_output` | `bool` | `False` | читання | The model supports native structured output (``supports_structured_output``). |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `ProviderResponse`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_llm.providers.base` |
| Код | [base.py:35](../../../../../services/llm/src/jane_llm/providers/base.py#L35) |

```python
@dataclass(frozen=True)
class ProviderResponse: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `text` | `str` | — | читання |  |
| `input_tokens` | `int` | — | читання |  |
| `output_tokens` | `int` | — | читання |  |
| `finish_reason` | `str` | `'stop'` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `ProviderError`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_llm.providers.base` |
| Успадкування | `Exception` |
| Код | [base.py:42](../../../../../services/llm/src/jane_llm/providers/base.py#L42) |

```python
class ProviderError(Exception): ...
```

The provider call did not produce a response.

#### Конструктор `ProviderError.__init__`

```python
def __init__(self, message: str, *, retryable: bool) -> None: ...
```

Код: [base.py:45](../../../../../services/llm/src/jane_llm/providers/base.py#L45).

### Клас `ProviderAdapter`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_llm.providers.base` |
| Успадкування | `Protocol` |
| Код | [base.py:50](../../../../../services/llm/src/jane_llm/providers/base.py#L50) |

```python
class ProviderAdapter(Protocol): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `kind` | `str` | — | читання й запис |  |

#### Метод `ProviderAdapter.complete`

```python
async def complete(
    self,
    request: ProviderRequest,
    connection: ResolvedConnection | None,
    limits: ServiceLimits,
) -> ProviderResponse: ...
```

Код: [base.py:53](../../../../../services/llm/src/jane_llm/providers/base.py#L53).
