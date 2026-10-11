# Модуль `jane_llm.models`

> Згенеровано `scripts/docs_reference.py` з [services/llm/src/jane_llm/models.py](../../../../../services/llm/src/jane_llm/models.py). Не редагуйте вручну.

Pydantic models of ``contracts/openapi/llm.v1.yaml`` and the shared ``Connection`` schema.

Configuration documents are strict (``extra='forbid'``) like the contract; results are built as dicts.

## Зміст

- [Клас `Strict`](#клас-strict)
- [Клас `Pricing`](#клас-pricing)
- [Клас `ModelInfo`](#клас-modelinfo)
- [Клас `Budget`](#клас-budget)
- [Клас `LlmLimitsIn`](#клас-llmlimitsin)
- [Клас `Provider`](#клас-provider)
- [Клас `ModelAlias`](#клас-modelalias)
- [Клас `DataPart`](#клас-datapart)
- [Клас `CompletionScope`](#клас-completionscope)
- [Клас `CompletionRequest`](#клас-completionrequest)
- [Клас `BudgetDefinition`](#клас-budgetdefinition)
- [Клас `Connection`](#клас-connection)

## Класи

### Клас `Strict`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_llm.models` |
| Успадкування | `BaseModel` |
| Код | [models.py:19](../../../../../services/llm/src/jane_llm/models.py#L19) |

```python
class Strict(BaseModel): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `model_config` | `ConfigDict(extra='forbid')` |  |

### Клас `Pricing`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.models` |
| Успадкування | `Strict` |
| Код | [models.py:23](../../../../../services/llm/src/jane_llm/models.py#L23) |

```python
class Pricing(Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `input_per_mtok` | `float` | `Field(ge=0)` | читання й запис |  |
| `output_per_mtok` | `float` | `Field(ge=0)` | читання й запис |  |
| `currency` | `str` | `Field(pattern=CURRENCY)` | читання й запис |  |

### Клас `ModelInfo`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.models` |
| Успадкування | `Strict` |
| Код | [models.py:29](../../../../../services/llm/src/jane_llm/models.py#L29) |

```python
class ModelInfo(Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `model_id` | `str` | — | читання й запис |  |
| `max_context_tokens` | `int \| None` | `Field(default=None, ge=1)` | читання й запис |  |
| `supports_structured_output` | `bool \| None` | `None` | читання й запис |  |
| `pricing` | `Pricing \| None` | `None` | читання й запис |  |

### Клас `Budget`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.models` |
| Успадкування | `Strict` |
| Код | [models.py:36](../../../../../services/llm/src/jane_llm/models.py#L36) |

```python
class Budget(Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `amount` | `float` | `Field(ge=0)` | читання й запис |  |
| `currency` | `str` | `Field(pattern=CURRENCY)` | читання й запис |  |
| `period` | `Period` | — | читання й запис |  |

### Клас `LlmLimitsIn`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.models` |
| Успадкування | `Strict` |
| Код | [models.py:42](../../../../../services/llm/src/jane_llm/models.py#L42) |

```python
class LlmLimitsIn(Strict): ...
```

Contract ``limits.llm`` as sent in requests and provider definitions.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `max_requests_per_minute` | `int \| None` | `Field(default=None, ge=1)` | читання й запис |  |
| `max_input_tokens_per_request` | `int \| None` | `Field(default=None, ge=1)` | читання й запис |  |
| `max_output_tokens_per_request` | `int \| None` | `Field(default=None, ge=1)` | читання й запис |  |
| `budget` | `Budget \| None` | `None` | читання й запис |  |
| `max_improvement_attempts` | `int \| None` | `Field(default=None, ge=0)` | читання й запис |  |
| `max_onboarding_samples` | `int \| None` | `Field(default=None, ge=1)` | читання й запис |  |
| `min_onboarding_confidence` | `float \| None` | `Field(default=None, gt=0, le=1)` | читання й запис | The assistant's limit; accepted (the contract allows it in any ``limits.llm``), not used by the gateway. |

### Клас `Provider`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.models` |
| Успадкування | `Strict` |
| Код | [models.py:55](../../../../../services/llm/src/jane_llm/models.py#L55) |

```python
class Provider(Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `provider_id` | `str` | `Field(pattern=SLUG)` | читання й запис |  |
| `kind` | `str` | — | читання й запис |  |
| `connection_id` | `str \| None` | `Field(default=None, pattern=SLUG)` | читання й запис |  |
| `enabled` | `bool` | — | читання й запис |  |
| `models` | `list[ModelInfo]` | — | читання й запис |  |
| `limits` | `LlmLimitsIn \| None` | `None` | читання й запис |  |

#### Метод `Provider.model`

```python
def model(self, model_id: str) -> ModelInfo | None: ...
```

Код: [models.py:63](../../../../../services/llm/src/jane_llm/models.py#L63).

### Клас `ModelAlias`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.models` |
| Успадкування | `Strict` |
| Код | [models.py:67](../../../../../services/llm/src/jane_llm/models.py#L67) |

```python
class ModelAlias(Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `alias` | `str` | — | читання й запис |  |
| `provider_id` | `str` | — | читання й запис |  |
| `model_id` | `str` | — | читання й запис |  |

### Клас `DataPart`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.models` |
| Успадкування | `Strict` |
| Код | [models.py:73](../../../../../services/llm/src/jane_llm/models.py#L73) |

```python
class DataPart(Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `name` | `str` | — | читання й запис |  |
| `media_type` | `str \| None` | `None` | читання й запис |  |
| `text` | `str \| None` | `None` | читання й запис |  |
| `content` | `dict[str, Any] \| None` | `None` | читання й запис |  |

### Клас `CompletionScope`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.models` |
| Успадкування | `Strict` |
| Код | [models.py:80](../../../../../services/llm/src/jane_llm/models.py#L80) |

```python
class CompletionScope(Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `source_id` | `str \| None` | `None` | читання й запис |  |
| `task_id` | `str \| None` | `None` | читання й запис |  |
| `run_id` | `str \| None` | `None` | читання й запис |  |
| `purpose` | `Literal['handler', 'onboarding', 'improvement', 'unknown_material', 'other']` | — | читання й запис |  |

### Клас `CompletionRequest`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.models` |
| Успадкування | `Strict` |
| Код | [models.py:87](../../../../../services/llm/src/jane_llm/models.py#L87) |

```python
class CompletionRequest(Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `model` | `str \| None` | `None` | читання й запис |  |
| `instructions` | `str` | — | читання й запис |  |
| `data` | `list[DataPart]` | `Field(default_factory=list)` | читання й запис |  |
| `output_schema` | `dict[str, Any] \| None` | `None` | читання й запис |  |
| `max_output_tokens` | `int \| None` | `Field(default=None, ge=1)` | читання й запис |  |
| `temperature` | `float \| None` | `Field(default=None, ge=0, le=2)` | читання й запис |  |
| `max_schema_retries` | `int \| None` | `Field(default=None, ge=0)` | читання й запис |  |
| `scope` | `CompletionScope` | — | читання й запис |  |
| `limits` | `LlmLimitsIn \| None` | `None` | читання й запис |  |
| `test_mode` | `bool \| None` | `None` | читання й запис |  |
| `mode` | `Literal['sync', 'async']` | `'sync'` | читання й запис |  |

### Клас `BudgetDefinition`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.models` |
| Успадкування | `Strict` |
| Код | [models.py:101](../../../../../services/llm/src/jane_llm/models.py#L101) |

```python
class BudgetDefinition(Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `scope_type` | `ScopeType` | — | читання й запис |  |
| `scope_id` | `str` | — | читання й запис |  |
| `budget` | `Budget \| None` | `None` | читання й запис |  |
| `max_requests_per_minute` | `int \| None` | `Field(default=None, ge=1)` | читання й запис |  |
| `status` | `dict[str, Any] \| None` | `None` | читання й запис |  |

### Клас `Connection`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.models` |
| Успадкування | `Strict` |
| Код | [models.py:114](../../../../../services/llm/src/jane_llm/models.py#L114) |

```python
class Connection(Strict): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `connection_id` | `str` | `Field(pattern=SLUG)` | читання й запис |  |
| `kind` | `str` | `Field(pattern='^[a-z][a-z0-9_]{1,31}$')` | читання й запис |  |
| `title` | `str \| None` | `Field(default=None, max_length=200)` | читання й запис |  |
| `params` | `dict[str, Any] \| None` | `None` | читання й запис |  |
| `secret_refs` | `dict[str, str] \| None` | `None` | читання й запис |  |
| `labels` | `dict[str, str] \| None` | `None` | читання й запис |  |

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `SLUG` | — | `'^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$'` |  |
| `CURRENCY` | — | `'^[A-Z]{3}$'` |  |
| `ScopeType` | — | `Literal['platform', 'source', 'task']` |  |
| `Period` | — | `Literal['run', 'day', 'week', 'month', 'total']` |  |
| `SECRET_REF_PATTERN` | — | `'^(env:[A-Z_][A-Z0-9_]{0,127}\|file:.{1,512}\|vault:[^#]{1,512}#[A-Za-z0-9_.-]{1,1` |  |
| `NAME_PATTERN` | — | `'^[a-z][a-z0-9_]{0,63}$'` |  |
