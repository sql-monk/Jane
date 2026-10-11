# jane_llm.models

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_llm.models.SLUG](#jane_llmmodelsslug)
- [jane_llm.models.CURRENCY](#jane_llmmodelscurrency)
- [jane_llm.models.ScopeType](#jane_llmmodelsscopetype)
- [jane_llm.models.Period](#jane_llmmodelsperiod)
- [jane_llm.models.Strict](#jane_llmmodelsstrict)
- [jane_llm.models.Strict.model_config](#jane_llmmodelsstrictmodel_config)
- [jane_llm.models.Pricing](#jane_llmmodelspricing)
- [jane_llm.models.Pricing.input_per_mtok](#jane_llmmodelspricinginput_per_mtok)
- [jane_llm.models.Pricing.output_per_mtok](#jane_llmmodelspricingoutput_per_mtok)
- [jane_llm.models.Pricing.currency](#jane_llmmodelspricingcurrency)
- [jane_llm.models.ModelInfo](#jane_llmmodelsmodelinfo)
- [jane_llm.models.ModelInfo.model_id](#jane_llmmodelsmodelinfomodel_id)
- [jane_llm.models.ModelInfo.max_context_tokens](#jane_llmmodelsmodelinfomax_context_tokens)
- [jane_llm.models.ModelInfo.supports_structured_output](#jane_llmmodelsmodelinfosupports_structured_output)
- [jane_llm.models.ModelInfo.pricing](#jane_llmmodelsmodelinfopricing)
- [jane_llm.models.Budget](#jane_llmmodelsbudget)
- [jane_llm.models.Budget.amount](#jane_llmmodelsbudgetamount)
- [jane_llm.models.Budget.currency](#jane_llmmodelsbudgetcurrency)
- [jane_llm.models.Budget.period](#jane_llmmodelsbudgetperiod)
- [jane_llm.models.LlmLimitsIn](#jane_llmmodelsllmlimitsin)
- [jane_llm.models.LlmLimitsIn.max_requests_per_minute](#jane_llmmodelsllmlimitsinmax_requests_per_minute)
- [jane_llm.models.LlmLimitsIn.max_input_tokens_per_request](#jane_llmmodelsllmlimitsinmax_input_tokens_per_request)
- [jane_llm.models.LlmLimitsIn.max_output_tokens_per_request](#jane_llmmodelsllmlimitsinmax_output_tokens_per_request)
- [jane_llm.models.LlmLimitsIn.budget](#jane_llmmodelsllmlimitsinbudget)
- [jane_llm.models.LlmLimitsIn.max_improvement_attempts](#jane_llmmodelsllmlimitsinmax_improvement_attempts)
- [jane_llm.models.LlmLimitsIn.max_onboarding_samples](#jane_llmmodelsllmlimitsinmax_onboarding_samples)
- [jane_llm.models.LlmLimitsIn.min_onboarding_confidence](#jane_llmmodelsllmlimitsinmin_onboarding_confidence)
- [jane_llm.models.Provider](#jane_llmmodelsprovider)
- [jane_llm.models.Provider.provider_id](#jane_llmmodelsproviderprovider_id)
- [jane_llm.models.Provider.kind](#jane_llmmodelsproviderkind)
- [jane_llm.models.Provider.connection_id](#jane_llmmodelsproviderconnection_id)
- [jane_llm.models.Provider.enabled](#jane_llmmodelsproviderenabled)
- [jane_llm.models.Provider.models](#jane_llmmodelsprovidermodels)
- [jane_llm.models.Provider.limits](#jane_llmmodelsproviderlimits)
- [jane_llm.models.Provider.model](#jane_llmmodelsprovidermodel)
- [jane_llm.models.ModelAlias](#jane_llmmodelsmodelalias)
- [jane_llm.models.ModelAlias.alias](#jane_llmmodelsmodelaliasalias)
- [jane_llm.models.ModelAlias.provider_id](#jane_llmmodelsmodelaliasprovider_id)
- [jane_llm.models.ModelAlias.model_id](#jane_llmmodelsmodelaliasmodel_id)
- [jane_llm.models.DataPart](#jane_llmmodelsdatapart)
- [jane_llm.models.DataPart.name](#jane_llmmodelsdatapartname)
- [jane_llm.models.DataPart.media_type](#jane_llmmodelsdatapartmedia_type)
- [jane_llm.models.DataPart.text](#jane_llmmodelsdataparttext)
- [jane_llm.models.DataPart.content](#jane_llmmodelsdatapartcontent)
- [jane_llm.models.CompletionScope](#jane_llmmodelscompletionscope)
- [jane_llm.models.CompletionScope.source_id](#jane_llmmodelscompletionscopesource_id)
- [jane_llm.models.CompletionScope.task_id](#jane_llmmodelscompletionscopetask_id)
- [jane_llm.models.CompletionScope.run_id](#jane_llmmodelscompletionscoperun_id)
- [jane_llm.models.CompletionScope.purpose](#jane_llmmodelscompletionscopepurpose)
- [jane_llm.models.CompletionRequest](#jane_llmmodelscompletionrequest)
- [jane_llm.models.CompletionRequest.model](#jane_llmmodelscompletionrequestmodel)
- [jane_llm.models.CompletionRequest.instructions](#jane_llmmodelscompletionrequestinstructions)
- [jane_llm.models.CompletionRequest.data](#jane_llmmodelscompletionrequestdata)
- [jane_llm.models.CompletionRequest.output_schema](#jane_llmmodelscompletionrequestoutput_schema)
- [jane_llm.models.CompletionRequest.max_output_tokens](#jane_llmmodelscompletionrequestmax_output_tokens)
- [jane_llm.models.CompletionRequest.temperature](#jane_llmmodelscompletionrequesttemperature)
- [jane_llm.models.CompletionRequest.max_schema_retries](#jane_llmmodelscompletionrequestmax_schema_retries)
- [jane_llm.models.CompletionRequest.scope](#jane_llmmodelscompletionrequestscope)
- [jane_llm.models.CompletionRequest.limits](#jane_llmmodelscompletionrequestlimits)
- [jane_llm.models.CompletionRequest.test_mode](#jane_llmmodelscompletionrequesttest_mode)
- [jane_llm.models.CompletionRequest.mode](#jane_llmmodelscompletionrequestmode)
- [jane_llm.models.BudgetDefinition](#jane_llmmodelsbudgetdefinition)
- [jane_llm.models.BudgetDefinition.scope_type](#jane_llmmodelsbudgetdefinitionscope_type)
- [jane_llm.models.BudgetDefinition.scope_id](#jane_llmmodelsbudgetdefinitionscope_id)
- [jane_llm.models.BudgetDefinition.budget](#jane_llmmodelsbudgetdefinitionbudget)
- [jane_llm.models.BudgetDefinition.max_requests_per_minute](#jane_llmmodelsbudgetdefinitionmax_requests_per_minute)
- [jane_llm.models.BudgetDefinition.status](#jane_llmmodelsbudgetdefinitionstatus)
- [jane_llm.models.SECRET_REF_PATTERN](#jane_llmmodelssecret_ref_pattern)
- [jane_llm.models.NAME_PATTERN](#jane_llmmodelsname_pattern)
- [jane_llm.models.Connection](#jane_llmmodelsconnection)
- [jane_llm.models.Connection.connection_id](#jane_llmmodelsconnectionconnection_id)
- [jane_llm.models.Connection.kind](#jane_llmmodelsconnectionkind)
- [jane_llm.models.Connection.title](#jane_llmmodelsconnectiontitle)
- [jane_llm.models.Connection.params](#jane_llmmodelsconnectionparams)
- [jane_llm.models.Connection.secret_refs](#jane_llmmodelsconnectionsecret_refs)
- [jane_llm.models.Connection.labels](#jane_llmmodelsconnectionlabels)

## jane_llm.models.SLUG

**Константа.** Код: [services/llm/src/jane_llm/models.py:13](../../../../../../services/llm/src/jane_llm/models.py#L13).

```python
SLUG = '^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$'
```

## jane_llm.models.CURRENCY

**Константа.** Код: [services/llm/src/jane_llm/models.py:14](../../../../../../services/llm/src/jane_llm/models.py#L14).

```python
CURRENCY = '^[A-Z]{3}$'
```

## jane_llm.models.ScopeType

**Змінна.** Код: [services/llm/src/jane_llm/models.py:15](../../../../../../services/llm/src/jane_llm/models.py#L15).

```python
ScopeType = Literal['platform', 'source', 'task']
```

## jane_llm.models.Period

**Змінна.** Код: [services/llm/src/jane_llm/models.py:16](../../../../../../services/llm/src/jane_llm/models.py#L16).

```python
Period = Literal['run', 'day', 'week', 'month', 'total']
```

## jane_llm.models.Strict

**Клас.** Код: [services/llm/src/jane_llm/models.py:19](../../../../../../services/llm/src/jane_llm/models.py#L19).

```python
class Strict(BaseModel):
```

Базові типи / інтерфейси: `BaseModel`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_config](jane_llm.models.md#jane_llmmodelsstrictmodel_config) | Поле | ні |

## jane_llm.models.Strict.model_config

**Поле.** Код: [services/llm/src/jane_llm/models.py:20](../../../../../../services/llm/src/jane_llm/models.py#L20).

```python
model_config = ConfigDict(extra='forbid')
```

Доступ: читання — так; запис — так.

## jane_llm.models.Pricing

**Клас.** Код: [services/llm/src/jane_llm/models.py:23](../../../../../../services/llm/src/jane_llm/models.py#L23).

```python
class Pricing(Strict):
```

Базові типи / інтерфейси: `Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [input_per_mtok](jane_llm.models.md#jane_llmmodelspricinginput_per_mtok) | Поле | ні |
| [output_per_mtok](jane_llm.models.md#jane_llmmodelspricingoutput_per_mtok) | Поле | ні |
| [currency](jane_llm.models.md#jane_llmmodelspricingcurrency) | Поле | ні |
| [model_config](jane_llm.models.md#jane_llmmodelsstrictmodel_config) | Поле | так |

## jane_llm.models.Pricing.input_per_mtok

**Поле.** Код: [services/llm/src/jane_llm/models.py:24](../../../../../../services/llm/src/jane_llm/models.py#L24).

```python
input_per_mtok: float = Field(ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "ge": "0"
}
```

## jane_llm.models.Pricing.output_per_mtok

**Поле.** Код: [services/llm/src/jane_llm/models.py:25](../../../../../../services/llm/src/jane_llm/models.py#L25).

```python
output_per_mtok: float = Field(ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "ge": "0"
}
```

## jane_llm.models.Pricing.currency

**Поле.** Код: [services/llm/src/jane_llm/models.py:26](../../../../../../services/llm/src/jane_llm/models.py#L26).

```python
currency: str = Field(pattern=CURRENCY)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "pattern": "CURRENCY"
}
```

## jane_llm.models.ModelInfo

**Клас.** Код: [services/llm/src/jane_llm/models.py:29](../../../../../../services/llm/src/jane_llm/models.py#L29).

```python
class ModelInfo(Strict):
```

Базові типи / інтерфейси: `Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model_id](jane_llm.models.md#jane_llmmodelsmodelinfomodel_id) | Поле | ні |
| [max_context_tokens](jane_llm.models.md#jane_llmmodelsmodelinfomax_context_tokens) | Поле | ні |
| [supports_structured_output](jane_llm.models.md#jane_llmmodelsmodelinfosupports_structured_output) | Поле | ні |
| [pricing](jane_llm.models.md#jane_llmmodelsmodelinfopricing) | Поле | ні |
| [model_config](jane_llm.models.md#jane_llmmodelsstrictmodel_config) | Поле | так |

## jane_llm.models.ModelInfo.model_id

**Поле.** Код: [services/llm/src/jane_llm/models.py:30](../../../../../../services/llm/src/jane_llm/models.py#L30).

```python
model_id: str
```

Доступ: читання — так; запис — так.

## jane_llm.models.ModelInfo.max_context_tokens

**Поле.** Код: [services/llm/src/jane_llm/models.py:31](../../../../../../services/llm/src/jane_llm/models.py#L31).

```python
max_context_tokens: int | None = Field(default=None, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "ge": "1"
}
```

## jane_llm.models.ModelInfo.supports_structured_output

**Поле.** Код: [services/llm/src/jane_llm/models.py:32](../../../../../../services/llm/src/jane_llm/models.py#L32).

```python
supports_structured_output: bool | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.ModelInfo.pricing

**Поле.** Код: [services/llm/src/jane_llm/models.py:33](../../../../../../services/llm/src/jane_llm/models.py#L33).

```python
pricing: Pricing | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.Budget

**Клас.** Код: [services/llm/src/jane_llm/models.py:36](../../../../../../services/llm/src/jane_llm/models.py#L36).

```python
class Budget(Strict):
```

Базові типи / інтерфейси: `Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [amount](jane_llm.models.md#jane_llmmodelsbudgetamount) | Поле | ні |
| [currency](jane_llm.models.md#jane_llmmodelsbudgetcurrency) | Поле | ні |
| [period](jane_llm.models.md#jane_llmmodelsbudgetperiod) | Поле | ні |
| [model_config](jane_llm.models.md#jane_llmmodelsstrictmodel_config) | Поле | так |

## jane_llm.models.Budget.amount

**Поле.** Код: [services/llm/src/jane_llm/models.py:37](../../../../../../services/llm/src/jane_llm/models.py#L37).

```python
amount: float = Field(ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "ge": "0"
}
```

## jane_llm.models.Budget.currency

**Поле.** Код: [services/llm/src/jane_llm/models.py:38](../../../../../../services/llm/src/jane_llm/models.py#L38).

```python
currency: str = Field(pattern=CURRENCY)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "pattern": "CURRENCY"
}
```

## jane_llm.models.Budget.period

**Поле.** Код: [services/llm/src/jane_llm/models.py:39](../../../../../../services/llm/src/jane_llm/models.py#L39).

```python
period: Period
```

Доступ: читання — так; запис — так.

## jane_llm.models.LlmLimitsIn

**Клас.** Код: [services/llm/src/jane_llm/models.py:42](../../../../../../services/llm/src/jane_llm/models.py#L42).

```python
class LlmLimitsIn(Strict):
```

Базові типи / інтерфейси: `Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [max_requests_per_minute](jane_llm.models.md#jane_llmmodelsllmlimitsinmax_requests_per_minute) | Поле | ні |
| [max_input_tokens_per_request](jane_llm.models.md#jane_llmmodelsllmlimitsinmax_input_tokens_per_request) | Поле | ні |
| [max_output_tokens_per_request](jane_llm.models.md#jane_llmmodelsllmlimitsinmax_output_tokens_per_request) | Поле | ні |
| [budget](jane_llm.models.md#jane_llmmodelsllmlimitsinbudget) | Поле | ні |
| [max_improvement_attempts](jane_llm.models.md#jane_llmmodelsllmlimitsinmax_improvement_attempts) | Поле | ні |
| [max_onboarding_samples](jane_llm.models.md#jane_llmmodelsllmlimitsinmax_onboarding_samples) | Поле | ні |
| [min_onboarding_confidence](jane_llm.models.md#jane_llmmodelsllmlimitsinmin_onboarding_confidence) | Поле | ні |
| [model_config](jane_llm.models.md#jane_llmmodelsstrictmodel_config) | Поле | так |

### Опис із вихідного коду

```text
Contract ``limits.llm`` as sent in requests and provider definitions.
```

## jane_llm.models.LlmLimitsIn.max_requests_per_minute

**Поле.** Код: [services/llm/src/jane_llm/models.py:45](../../../../../../services/llm/src/jane_llm/models.py#L45).

```python
max_requests_per_minute: int | None = Field(default=None, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "ge": "1"
}
```

## jane_llm.models.LlmLimitsIn.max_input_tokens_per_request

**Поле.** Код: [services/llm/src/jane_llm/models.py:46](../../../../../../services/llm/src/jane_llm/models.py#L46).

```python
max_input_tokens_per_request: int | None = Field(default=None, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "ge": "1"
}
```

## jane_llm.models.LlmLimitsIn.max_output_tokens_per_request

**Поле.** Код: [services/llm/src/jane_llm/models.py:47](../../../../../../services/llm/src/jane_llm/models.py#L47).

```python
max_output_tokens_per_request: int | None = Field(default=None, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "ge": "1"
}
```

## jane_llm.models.LlmLimitsIn.budget

**Поле.** Код: [services/llm/src/jane_llm/models.py:48](../../../../../../services/llm/src/jane_llm/models.py#L48).

```python
budget: Budget | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.LlmLimitsIn.max_improvement_attempts

**Поле.** Код: [services/llm/src/jane_llm/models.py:49](../../../../../../services/llm/src/jane_llm/models.py#L49).

```python
max_improvement_attempts: int | None = Field(default=None, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "ge": "0"
}
```

## jane_llm.models.LlmLimitsIn.max_onboarding_samples

**Поле.** Код: [services/llm/src/jane_llm/models.py:50](../../../../../../services/llm/src/jane_llm/models.py#L50).

```python
max_onboarding_samples: int | None = Field(default=None, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "ge": "1"
}
```

## jane_llm.models.LlmLimitsIn.min_onboarding_confidence

**Поле.** Код: [services/llm/src/jane_llm/models.py:51](../../../../../../services/llm/src/jane_llm/models.py#L51).

```python
min_onboarding_confidence: float | None = Field(default=None, gt=0, le=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "gt": "0",
  "le": "1"
}
```

### Опис із вихідного коду

```text
The assistant's limit; accepted (the contract allows it in any ``limits.llm``), not used by the gateway.
```

## jane_llm.models.Provider

**Клас.** Код: [services/llm/src/jane_llm/models.py:55](../../../../../../services/llm/src/jane_llm/models.py#L55).

```python
class Provider(Strict):
```

Базові типи / інтерфейси: `Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [provider_id](jane_llm.models.md#jane_llmmodelsproviderprovider_id) | Поле | ні |
| [kind](jane_llm.models.md#jane_llmmodelsproviderkind) | Поле | ні |
| [connection_id](jane_llm.models.md#jane_llmmodelsproviderconnection_id) | Поле | ні |
| [enabled](jane_llm.models.md#jane_llmmodelsproviderenabled) | Поле | ні |
| [models](jane_llm.models.md#jane_llmmodelsprovidermodels) | Поле | ні |
| [limits](jane_llm.models.md#jane_llmmodelsproviderlimits) | Поле | ні |
| [model](jane_llm.models.md#jane_llmmodelsprovidermodel) | Метод | ні |
| [model_config](jane_llm.models.md#jane_llmmodelsstrictmodel_config) | Поле | так |

## jane_llm.models.Provider.provider_id

**Поле.** Код: [services/llm/src/jane_llm/models.py:56](../../../../../../services/llm/src/jane_llm/models.py#L56).

```python
provider_id: str = Field(pattern=SLUG)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "pattern": "SLUG"
}
```

## jane_llm.models.Provider.kind

**Поле.** Код: [services/llm/src/jane_llm/models.py:57](../../../../../../services/llm/src/jane_llm/models.py#L57).

```python
kind: str
```

Доступ: читання — так; запис — так.

## jane_llm.models.Provider.connection_id

**Поле.** Код: [services/llm/src/jane_llm/models.py:58](../../../../../../services/llm/src/jane_llm/models.py#L58).

```python
connection_id: str | None = Field(default=None, pattern=SLUG)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "pattern": "SLUG"
}
```

## jane_llm.models.Provider.enabled

**Поле.** Код: [services/llm/src/jane_llm/models.py:59](../../../../../../services/llm/src/jane_llm/models.py#L59).

```python
enabled: bool
```

Доступ: читання — так; запис — так.

## jane_llm.models.Provider.models

**Поле.** Код: [services/llm/src/jane_llm/models.py:60](../../../../../../services/llm/src/jane_llm/models.py#L60).

```python
models: list[ModelInfo]
```

Доступ: читання — так; запис — так.

## jane_llm.models.Provider.limits

**Поле.** Код: [services/llm/src/jane_llm/models.py:61](../../../../../../services/llm/src/jane_llm/models.py#L61).

```python
limits: LlmLimitsIn | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.Provider.model

**Метод.** Код: [services/llm/src/jane_llm/models.py:63](../../../../../../services/llm/src/jane_llm/models.py#L63).

```python
def model(self, model_id: str) -> ModelInfo | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `model_id` | `str` | `—` | positional-or-keyword |

Результат: `ModelInfo | None`.

## jane_llm.models.ModelAlias

**Клас.** Код: [services/llm/src/jane_llm/models.py:67](../../../../../../services/llm/src/jane_llm/models.py#L67).

```python
class ModelAlias(Strict):
```

Базові типи / інтерфейси: `Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [alias](jane_llm.models.md#jane_llmmodelsmodelaliasalias) | Поле | ні |
| [provider_id](jane_llm.models.md#jane_llmmodelsmodelaliasprovider_id) | Поле | ні |
| [model_id](jane_llm.models.md#jane_llmmodelsmodelaliasmodel_id) | Поле | ні |
| [model_config](jane_llm.models.md#jane_llmmodelsstrictmodel_config) | Поле | так |

## jane_llm.models.ModelAlias.alias

**Поле.** Код: [services/llm/src/jane_llm/models.py:68](../../../../../../services/llm/src/jane_llm/models.py#L68).

```python
alias: str
```

Доступ: читання — так; запис — так.

## jane_llm.models.ModelAlias.provider_id

**Поле.** Код: [services/llm/src/jane_llm/models.py:69](../../../../../../services/llm/src/jane_llm/models.py#L69).

```python
provider_id: str
```

Доступ: читання — так; запис — так.

## jane_llm.models.ModelAlias.model_id

**Поле.** Код: [services/llm/src/jane_llm/models.py:70](../../../../../../services/llm/src/jane_llm/models.py#L70).

```python
model_id: str
```

Доступ: читання — так; запис — так.

## jane_llm.models.DataPart

**Клас.** Код: [services/llm/src/jane_llm/models.py:73](../../../../../../services/llm/src/jane_llm/models.py#L73).

```python
class DataPart(Strict):
```

Базові типи / інтерфейси: `Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_llm.models.md#jane_llmmodelsdatapartname) | Поле | ні |
| [media_type](jane_llm.models.md#jane_llmmodelsdatapartmedia_type) | Поле | ні |
| [text](jane_llm.models.md#jane_llmmodelsdataparttext) | Поле | ні |
| [content](jane_llm.models.md#jane_llmmodelsdatapartcontent) | Поле | ні |
| [model_config](jane_llm.models.md#jane_llmmodelsstrictmodel_config) | Поле | так |

## jane_llm.models.DataPart.name

**Поле.** Код: [services/llm/src/jane_llm/models.py:74](../../../../../../services/llm/src/jane_llm/models.py#L74).

```python
name: str
```

Доступ: читання — так; запис — так.

## jane_llm.models.DataPart.media_type

**Поле.** Код: [services/llm/src/jane_llm/models.py:75](../../../../../../services/llm/src/jane_llm/models.py#L75).

```python
media_type: str | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.DataPart.text

**Поле.** Код: [services/llm/src/jane_llm/models.py:76](../../../../../../services/llm/src/jane_llm/models.py#L76).

```python
text: str | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.DataPart.content

**Поле.** Код: [services/llm/src/jane_llm/models.py:77](../../../../../../services/llm/src/jane_llm/models.py#L77).

```python
content: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.CompletionScope

**Клас.** Код: [services/llm/src/jane_llm/models.py:80](../../../../../../services/llm/src/jane_llm/models.py#L80).

```python
class CompletionScope(Strict):
```

Базові типи / інтерфейси: `Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [source_id](jane_llm.models.md#jane_llmmodelscompletionscopesource_id) | Поле | ні |
| [task_id](jane_llm.models.md#jane_llmmodelscompletionscopetask_id) | Поле | ні |
| [run_id](jane_llm.models.md#jane_llmmodelscompletionscoperun_id) | Поле | ні |
| [purpose](jane_llm.models.md#jane_llmmodelscompletionscopepurpose) | Поле | ні |
| [model_config](jane_llm.models.md#jane_llmmodelsstrictmodel_config) | Поле | так |

## jane_llm.models.CompletionScope.source_id

**Поле.** Код: [services/llm/src/jane_llm/models.py:81](../../../../../../services/llm/src/jane_llm/models.py#L81).

```python
source_id: str | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.CompletionScope.task_id

**Поле.** Код: [services/llm/src/jane_llm/models.py:82](../../../../../../services/llm/src/jane_llm/models.py#L82).

```python
task_id: str | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.CompletionScope.run_id

**Поле.** Код: [services/llm/src/jane_llm/models.py:83](../../../../../../services/llm/src/jane_llm/models.py#L83).

```python
run_id: str | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.CompletionScope.purpose

**Поле.** Код: [services/llm/src/jane_llm/models.py:84](../../../../../../services/llm/src/jane_llm/models.py#L84).

```python
purpose: Literal['handler', 'onboarding', 'improvement', 'unknown_material', 'other']
```

Доступ: читання — так; запис — так.

## jane_llm.models.CompletionRequest

**Клас.** Код: [services/llm/src/jane_llm/models.py:87](../../../../../../services/llm/src/jane_llm/models.py#L87).

```python
class CompletionRequest(Strict):
```

Базові типи / інтерфейси: `Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [model](jane_llm.models.md#jane_llmmodelscompletionrequestmodel) | Поле | ні |
| [instructions](jane_llm.models.md#jane_llmmodelscompletionrequestinstructions) | Поле | ні |
| [data](jane_llm.models.md#jane_llmmodelscompletionrequestdata) | Поле | ні |
| [output_schema](jane_llm.models.md#jane_llmmodelscompletionrequestoutput_schema) | Поле | ні |
| [max_output_tokens](jane_llm.models.md#jane_llmmodelscompletionrequestmax_output_tokens) | Поле | ні |
| [temperature](jane_llm.models.md#jane_llmmodelscompletionrequesttemperature) | Поле | ні |
| [max_schema_retries](jane_llm.models.md#jane_llmmodelscompletionrequestmax_schema_retries) | Поле | ні |
| [scope](jane_llm.models.md#jane_llmmodelscompletionrequestscope) | Поле | ні |
| [limits](jane_llm.models.md#jane_llmmodelscompletionrequestlimits) | Поле | ні |
| [test_mode](jane_llm.models.md#jane_llmmodelscompletionrequesttest_mode) | Поле | ні |
| [mode](jane_llm.models.md#jane_llmmodelscompletionrequestmode) | Поле | ні |
| [model_config](jane_llm.models.md#jane_llmmodelsstrictmodel_config) | Поле | так |

## jane_llm.models.CompletionRequest.model

**Поле.** Код: [services/llm/src/jane_llm/models.py:88](../../../../../../services/llm/src/jane_llm/models.py#L88).

```python
model: str | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.CompletionRequest.instructions

**Поле.** Код: [services/llm/src/jane_llm/models.py:89](../../../../../../services/llm/src/jane_llm/models.py#L89).

```python
instructions: str
```

Доступ: читання — так; запис — так.

## jane_llm.models.CompletionRequest.data

**Поле.** Код: [services/llm/src/jane_llm/models.py:90](../../../../../../services/llm/src/jane_llm/models.py#L90).

```python
data: list[DataPart] = Field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_llm.models.CompletionRequest.output_schema

**Поле.** Код: [services/llm/src/jane_llm/models.py:91](../../../../../../services/llm/src/jane_llm/models.py#L91).

```python
output_schema: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.CompletionRequest.max_output_tokens

**Поле.** Код: [services/llm/src/jane_llm/models.py:92](../../../../../../services/llm/src/jane_llm/models.py#L92).

```python
max_output_tokens: int | None = Field(default=None, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "ge": "1"
}
```

## jane_llm.models.CompletionRequest.temperature

**Поле.** Код: [services/llm/src/jane_llm/models.py:93](../../../../../../services/llm/src/jane_llm/models.py#L93).

```python
temperature: float | None = Field(default=None, ge=0, le=2)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "ge": "0",
  "le": "2"
}
```

## jane_llm.models.CompletionRequest.max_schema_retries

**Поле.** Код: [services/llm/src/jane_llm/models.py:94](../../../../../../services/llm/src/jane_llm/models.py#L94).

```python
max_schema_retries: int | None = Field(default=None, ge=0)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "ge": "0"
}
```

## jane_llm.models.CompletionRequest.scope

**Поле.** Код: [services/llm/src/jane_llm/models.py:95](../../../../../../services/llm/src/jane_llm/models.py#L95).

```python
scope: CompletionScope
```

Доступ: читання — так; запис — так.

## jane_llm.models.CompletionRequest.limits

**Поле.** Код: [services/llm/src/jane_llm/models.py:96](../../../../../../services/llm/src/jane_llm/models.py#L96).

```python
limits: LlmLimitsIn | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.CompletionRequest.test_mode

**Поле.** Код: [services/llm/src/jane_llm/models.py:97](../../../../../../services/llm/src/jane_llm/models.py#L97).

```python
test_mode: bool | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.CompletionRequest.mode

**Поле.** Код: [services/llm/src/jane_llm/models.py:98](../../../../../../services/llm/src/jane_llm/models.py#L98).

```python
mode: Literal['sync', 'async'] = 'sync'
```

Доступ: читання — так; запис — так.

## jane_llm.models.BudgetDefinition

**Клас.** Код: [services/llm/src/jane_llm/models.py:101](../../../../../../services/llm/src/jane_llm/models.py#L101).

```python
class BudgetDefinition(Strict):
```

Базові типи / інтерфейси: `Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [scope_type](jane_llm.models.md#jane_llmmodelsbudgetdefinitionscope_type) | Поле | ні |
| [scope_id](jane_llm.models.md#jane_llmmodelsbudgetdefinitionscope_id) | Поле | ні |
| [budget](jane_llm.models.md#jane_llmmodelsbudgetdefinitionbudget) | Поле | ні |
| [max_requests_per_minute](jane_llm.models.md#jane_llmmodelsbudgetdefinitionmax_requests_per_minute) | Поле | ні |
| [status](jane_llm.models.md#jane_llmmodelsbudgetdefinitionstatus) | Поле | ні |
| [model_config](jane_llm.models.md#jane_llmmodelsstrictmodel_config) | Поле | так |

## jane_llm.models.BudgetDefinition.scope_type

**Поле.** Код: [services/llm/src/jane_llm/models.py:102](../../../../../../services/llm/src/jane_llm/models.py#L102).

```python
scope_type: ScopeType
```

Доступ: читання — так; запис — так.

## jane_llm.models.BudgetDefinition.scope_id

**Поле.** Код: [services/llm/src/jane_llm/models.py:103](../../../../../../services/llm/src/jane_llm/models.py#L103).

```python
scope_id: str
```

Доступ: читання — так; запис — так.

## jane_llm.models.BudgetDefinition.budget

**Поле.** Код: [services/llm/src/jane_llm/models.py:104](../../../../../../services/llm/src/jane_llm/models.py#L104).

```python
budget: Budget | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.BudgetDefinition.max_requests_per_minute

**Поле.** Код: [services/llm/src/jane_llm/models.py:105](../../../../../../services/llm/src/jane_llm/models.py#L105).

```python
max_requests_per_minute: int | None = Field(default=None, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "ge": "1"
}
```

## jane_llm.models.BudgetDefinition.status

**Поле.** Код: [services/llm/src/jane_llm/models.py:106](../../../../../../services/llm/src/jane_llm/models.py#L106).

```python
status: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.SECRET_REF_PATTERN

**Константа.** Код: [services/llm/src/jane_llm/models.py:110](../../../../../../services/llm/src/jane_llm/models.py#L110).

```python
SECRET_REF_PATTERN = '^(env:[A-Z_][A-Z0-9_]{0,127}|file:.{1,512}|vault:[^#]{1,512}#[A-Za-z0-9_.-]{1,128})$'
```

## jane_llm.models.NAME_PATTERN

**Константа.** Код: [services/llm/src/jane_llm/models.py:111](../../../../../../services/llm/src/jane_llm/models.py#L111).

```python
NAME_PATTERN = '^[a-z][a-z0-9_]{0,63}$'
```

## jane_llm.models.Connection

**Клас.** Код: [services/llm/src/jane_llm/models.py:114](../../../../../../services/llm/src/jane_llm/models.py#L114).

```python
class Connection(Strict):
```

Базові типи / інтерфейси: `Strict`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [connection_id](jane_llm.models.md#jane_llmmodelsconnectionconnection_id) | Поле | ні |
| [kind](jane_llm.models.md#jane_llmmodelsconnectionkind) | Поле | ні |
| [title](jane_llm.models.md#jane_llmmodelsconnectiontitle) | Поле | ні |
| [params](jane_llm.models.md#jane_llmmodelsconnectionparams) | Поле | ні |
| [secret_refs](jane_llm.models.md#jane_llmmodelsconnectionsecret_refs) | Поле | ні |
| [labels](jane_llm.models.md#jane_llmmodelsconnectionlabels) | Поле | ні |
| [model_config](jane_llm.models.md#jane_llmmodelsstrictmodel_config) | Поле | так |

## jane_llm.models.Connection.connection_id

**Поле.** Код: [services/llm/src/jane_llm/models.py:115](../../../../../../services/llm/src/jane_llm/models.py#L115).

```python
connection_id: str = Field(pattern=SLUG)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "pattern": "SLUG"
}
```

## jane_llm.models.Connection.kind

**Поле.** Код: [services/llm/src/jane_llm/models.py:116](../../../../../../services/llm/src/jane_llm/models.py#L116).

```python
kind: str = Field(pattern='^[a-z][a-z0-9_]{1,31}$')
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "pattern": "'^[a-z][a-z0-9_]{1,31}$'"
}
```

## jane_llm.models.Connection.title

**Поле.** Код: [services/llm/src/jane_llm/models.py:117](../../../../../../services/llm/src/jane_llm/models.py#L117).

```python
title: str | None = Field(default=None, max_length=200)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "None",
  "max_length": "200"
}
```

## jane_llm.models.Connection.params

**Поле.** Код: [services/llm/src/jane_llm/models.py:118](../../../../../../services/llm/src/jane_llm/models.py#L118).

```python
params: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.Connection.secret_refs

**Поле.** Код: [services/llm/src/jane_llm/models.py:119](../../../../../../services/llm/src/jane_llm/models.py#L119).

```python
secret_refs: dict[str, str] | None = None
```

Доступ: читання — так; запис — так.

## jane_llm.models.Connection.labels

**Поле.** Код: [services/llm/src/jane_llm/models.py:120](../../../../../../services/llm/src/jane_llm/models.py#L120).

```python
labels: dict[str, str] | None = None
```

Доступ: читання — так; запис — так.
