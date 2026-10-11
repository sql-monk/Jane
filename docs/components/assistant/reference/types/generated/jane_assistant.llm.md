# jane_assistant.llm

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_assistant.llm.BudgetExhausted](#jane_assistantllmbudgetexhausted)
- [jane_assistant.llm.BudgetExhausted.code](#jane_assistantllmbudgetexhaustedcode)
- [jane_assistant.llm.InvalidModelOutput](#jane_assistantllminvalidmodeloutput)
- [jane_assistant.llm.InvalidModelOutput.code](#jane_assistantllminvalidmodeloutputcode)
- [jane_assistant.llm.part](#jane_assistantllmpart)
- [jane_assistant.llm.LlmSession](#jane_assistantllmllmsession)
- [jane_assistant.llm.LlmSession.__init__](#jane_assistantllmllmsession__init__)
- [jane_assistant.llm.LlmSession.client](#jane_assistantllmllmsessionclient)
- [jane_assistant.llm.LlmSession.limits](#jane_assistantllmllmsessionlimits)
- [jane_assistant.llm.LlmSession.purpose](#jane_assistantllmllmsessionpurpose)
- [jane_assistant.llm.LlmSession.job_key](#jane_assistantllmllmsessionjob_key)
- [jane_assistant.llm.LlmSession.source_id](#jane_assistantllmllmsessionsource_id)
- [jane_assistant.llm.LlmSession.task_id](#jane_assistantllmllmsessiontask_id)
- [jane_assistant.llm.LlmSession.run_id](#jane_assistantllmllmsessionrun_id)
- [jane_assistant.llm.LlmSession.mode](#jane_assistantllmllmsessionmode)
- [jane_assistant.llm.LlmSession.call](#jane_assistantllmllmsessioncall)
- [jane_assistant.llm.LlmSession.spent](#jane_assistantllmllmsessionspent)
- [jane_assistant.llm.LlmSession.calls](#jane_assistantllmllmsessioncalls)
- [jane_assistant.llm.LlmSession.currency](#jane_assistantllmllmsessioncurrency)
- [jane_assistant.llm.LlmSession.model_used](#jane_assistantllmllmsessionmodel_used)
- [jane_assistant.llm.LlmSession.exhausted](#jane_assistantllmllmsessionexhausted)
- [jane_assistant.llm.LlmSession.cost](#jane_assistantllmllmsessioncost)
- [jane_assistant.llm.LlmSession.data_budget](#jane_assistantllmllmsessiondata_budget)
- [jane_assistant.llm.LlmSession.room](#jane_assistantllmllmsessionroom)
- [jane_assistant.llm.LlmSession.ask](#jane_assistantllmllmsessionask)

## jane_assistant.llm.BudgetExhausted

**Клас.** Код: [services/assistant/src/jane_assistant/llm.py:41](../../../../../../services/assistant/src/jane_assistant/llm.py#L41).

```python
class BudgetExhausted(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_assistant.llm.md#jane_assistantllmbudgetexhaustedcode) | Поле | ні |
| [__init__](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

## jane_assistant.llm.BudgetExhausted.code

**Поле.** Код: [services/assistant/src/jane_assistant/llm.py:42](../../../../../../services/assistant/src/jane_assistant/llm.py#L42).

```python
code = 'budget_exhausted'
```

Доступ: читання — так; запис — так.

## jane_assistant.llm.InvalidModelOutput

**Клас.** Код: [services/assistant/src/jane_assistant/llm.py:45](../../../../../../services/assistant/src/jane_assistant/llm.py#L45).

```python
class InvalidModelOutput(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_assistant.llm.md#jane_assistantllminvalidmodeloutputcode) | Поле | ні |
| [__init__](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

## jane_assistant.llm.InvalidModelOutput.code

**Поле.** Код: [services/assistant/src/jane_assistant/llm.py:46](../../../../../../services/assistant/src/jane_assistant/llm.py#L46).

```python
code = 'schema_mismatch'
```

Доступ: читання — так; запис — так.

## jane_assistant.llm.part

**Функція.** Код: [services/assistant/src/jane_assistant/llm.py:49](../../../../../../services/assistant/src/jane_assistant/llm.py#L49).

```python
def part(name: str, text: str, media_type: str='text/plain') -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `name` | `str` | `—` | positional-or-keyword |
| `text` | `str` | `—` | positional-or-keyword |
| `media_type` | `str` | `'text/plain'` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_llm_budget.py:114](../../../../../../services/assistant/tests/test_llm_budget.py#L114).

```python
return llm.ask("probe", "Answer with the schema.", [part("page", text)], SCHEMA, model="default")
```

## jane_assistant.llm.LlmSession

**Клас.** Код: [services/assistant/src/jane_assistant/llm.py:54](../../../../../../services/assistant/src/jane_assistant/llm.py#L54).

```python
class LlmSession:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [client](jane_assistant.llm.md#jane_assistantllmllmsessionclient) | Поле | ні |
| [limits](jane_assistant.llm.md#jane_assistantllmllmsessionlimits) | Поле | ні |
| [purpose](jane_assistant.llm.md#jane_assistantllmllmsessionpurpose) | Поле | ні |
| [job_key](jane_assistant.llm.md#jane_assistantllmllmsessionjob_key) | Поле | ні |
| [source_id](jane_assistant.llm.md#jane_assistantllmllmsessionsource_id) | Поле | ні |
| [task_id](jane_assistant.llm.md#jane_assistantllmllmsessiontask_id) | Поле | ні |
| [run_id](jane_assistant.llm.md#jane_assistantllmllmsessionrun_id) | Поле | ні |
| [mode](jane_assistant.llm.md#jane_assistantllmllmsessionmode) | Поле | ні |
| [call](jane_assistant.llm.md#jane_assistantllmllmsessioncall) | Поле | ні |
| [spent](jane_assistant.llm.md#jane_assistantllmllmsessionspent) | Поле | ні |
| [calls](jane_assistant.llm.md#jane_assistantllmllmsessioncalls) | Поле | ні |
| [currency](jane_assistant.llm.md#jane_assistantllmllmsessioncurrency) | Поле | ні |
| [model_used](jane_assistant.llm.md#jane_assistantllmllmsessionmodel_used) | Поле | ні |
| [exhausted](jane_assistant.llm.md#jane_assistantllmllmsessionexhausted) | Властивість | ні |
| [cost](jane_assistant.llm.md#jane_assistantllmllmsessioncost) | Метод | ні |
| [data_budget](jane_assistant.llm.md#jane_assistantllmllmsessiondata_budget) | Метод | ні |
| [room](jane_assistant.llm.md#jane_assistantllmllmsessionroom) | Метод | ні |
| [ask](jane_assistant.llm.md#jane_assistantllmllmsessionask) | Метод | ні |
| [__init__](jane_assistant.llm.md#jane_assistantllmllmsession__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_llm_budget.py:104](../../../../../../services/assistant/tests/test_llm_budget.py#L104).

```python
return LlmSession(client, limits, "onboarding", job, run_id=run, mode=mode)
```

Контекст і передумови: [services/assistant/tests/test_units.py:214](../../../../../../services/assistant/tests/test_units.py#L214).

```python
return LlmSession(client, LlmLimits(**limits), "onboarding", "job_1")
```

## jane_assistant.llm.LlmSession.__init__

**Конструктор dataclass.** Код: [services/assistant/src/jane_assistant/llm.py:54](../../../../../../services/assistant/src/jane_assistant/llm.py#L54).

```python
def __init__(self, client: LlmClient, limits: LlmLimits, purpose: str, job_key: str, source_id: str | None = None, task_id: str | None = None, run_id: str | None = None, mode: str = 'sync', call: LlmCallLimits = <factory LlmCallLimits>, spent: float = 0.0, calls: int = 0, model_used: dict[str, str] = <factory dict>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `LlmClient` | `—` | positional-or-keyword |
| `limits` | `LlmLimits` | `—` | positional-or-keyword |
| `purpose` | `str` | `—` | positional-or-keyword |
| `job_key` | `str` | `—` | positional-or-keyword |
| `source_id` | `str \| None` | `None` | positional-or-keyword |
| `task_id` | `str \| None` | `None` | positional-or-keyword |
| `run_id` | `str \| None` | `None` | positional-or-keyword |
| `mode` | `str` | `'sync'` | positional-or-keyword |
| `call` | `LlmCallLimits` | `factory: LlmCallLimits` | positional-or-keyword |
| `spent` | `float` | `0.0` | positional-or-keyword |
| `calls` | `int` | `0` | positional-or-keyword |
| `model_used` | `dict[str, str]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_llm_budget.py:104](../../../../../../services/assistant/tests/test_llm_budget.py#L104).

```python
return LlmSession(client, limits, "onboarding", job, run_id=run, mode=mode)
```

Контекст і передумови: [services/assistant/tests/test_units.py:214](../../../../../../services/assistant/tests/test_units.py#L214).

```python
return LlmSession(client, LlmLimits(**limits), "onboarding", "job_1")
```

## jane_assistant.llm.LlmSession.client

**Поле.** Код: [services/assistant/src/jane_assistant/llm.py:55](../../../../../../services/assistant/src/jane_assistant/llm.py#L55).

```python
client: LlmClient
```

Доступ: читання — так; запис — так.

## jane_assistant.llm.LlmSession.limits

**Поле.** Код: [services/assistant/src/jane_assistant/llm.py:56](../../../../../../services/assistant/src/jane_assistant/llm.py#L56).

```python
limits: LlmLimits
```

Доступ: читання — так; запис — так.

## jane_assistant.llm.LlmSession.purpose

**Поле.** Код: [services/assistant/src/jane_assistant/llm.py:57](../../../../../../services/assistant/src/jane_assistant/llm.py#L57).

```python
purpose: str
```

Доступ: читання — так; запис — так.

## jane_assistant.llm.LlmSession.job_key

**Поле.** Код: [services/assistant/src/jane_assistant/llm.py:58](../../../../../../services/assistant/src/jane_assistant/llm.py#L58).

```python
job_key: str
```

Доступ: читання — так; запис — так.

## jane_assistant.llm.LlmSession.source_id

**Поле.** Код: [services/assistant/src/jane_assistant/llm.py:59](../../../../../../services/assistant/src/jane_assistant/llm.py#L59).

```python
source_id: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.llm.LlmSession.task_id

**Поле.** Код: [services/assistant/src/jane_assistant/llm.py:60](../../../../../../services/assistant/src/jane_assistant/llm.py#L60).

```python
task_id: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.llm.LlmSession.run_id

**Поле.** Код: [services/assistant/src/jane_assistant/llm.py:61](../../../../../../services/assistant/src/jane_assistant/llm.py#L61).

```python
run_id: str | None = None
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``scope.run_id`` of every call: the window of a ``period: run`` budget (default: ``job_key``).
```

## jane_assistant.llm.LlmSession.mode

**Поле.** Код: [services/assistant/src/jane_assistant/llm.py:63](../../../../../../services/assistant/src/jane_assistant/llm.py#L63).

```python
mode: str = 'sync'
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``CompletionRequest.mode``: ``sync`` or ``async`` (202 + job, awaited by the client).
```

## jane_assistant.llm.LlmSession.call

**Поле.** Код: [services/assistant/src/jane_assistant/llm.py:65](../../../../../../services/assistant/src/jane_assistant/llm.py#L65).

```python
call: LlmCallLimits = field(default_factory=LlmCallLimits)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "LlmCallLimits"
}
```

### Опис із вихідного коду

```text
How request size is counted (``llm_call.chars_per_token``, ``*_overhead_chars``).
```

## jane_assistant.llm.LlmSession.spent

**Поле.** Код: [services/assistant/src/jane_assistant/llm.py:67](../../../../../../services/assistant/src/jane_assistant/llm.py#L67).

```python
spent: float = 0.0
```

Доступ: читання — так; запис — так.

## jane_assistant.llm.LlmSession.calls

**Поле.** Код: [services/assistant/src/jane_assistant/llm.py:68](../../../../../../services/assistant/src/jane_assistant/llm.py#L68).

```python
calls: int = 0
```

Доступ: читання — так; запис — так.

## jane_assistant.llm.LlmSession.currency

**Поле.** Код: [services/assistant/src/jane_assistant/llm.py:69](../../../../../../services/assistant/src/jane_assistant/llm.py#L69).

```python
currency: str = field(init=False)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "init": "False"
}
```

## jane_assistant.llm.LlmSession.model_used

**Поле.** Код: [services/assistant/src/jane_assistant/llm.py:70](../../../../../../services/assistant/src/jane_assistant/llm.py#L70).

```python
model_used: dict[str, str] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_assistant.llm.LlmSession.exhausted

**Властивість.** Код: [services/assistant/src/jane_assistant/llm.py:78](../../../../../../services/assistant/src/jane_assistant/llm.py#L78).

```python
def exhausted(self) -> bool:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
The run's spend reached the budget: no further call (``amount: 0`` - none at all).
```

## jane_assistant.llm.LlmSession.cost

**Метод.** Код: [services/assistant/src/jane_assistant/llm.py:82](../../../../../../services/assistant/src/jane_assistant/llm.py#L82).

```python
def cost(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_assistant.llm.LlmSession.data_budget

**Метод.** Код: [services/assistant/src/jane_assistant/llm.py:88](../../../../../../services/assistant/src/jane_assistant/llm.py#L88).

```python
def data_budget(self, instructions: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `instructions` | `str` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Characters of data parts (their delimiters included) one request may carry.
```

## jane_assistant.llm.LlmSession.room

**Метод.** Код: [services/assistant/src/jane_assistant/llm.py:93](../../../../../../services/assistant/src/jane_assistant/llm.py#L93).

```python
def room(self, instructions: str, fixed: list[dict[str, Any]], count: int, cap: int) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `instructions` | `str` | `—` | positional-or-keyword |
| `fixed` | `list[dict[str, Any]]` | `—` | positional-or-keyword |
| `count` | `int` | `—` | positional-or-keyword |
| `cap` | `int` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Characters each of ``count`` further data parts may take next to the ``fixed`` ones (at most ``cap``).
```

## jane_assistant.llm.LlmSession.ask

**Метод.** Код: [services/assistant/src/jane_assistant/llm.py:115](../../../../../../services/assistant/src/jane_assistant/llm.py#L115).

```python
async def ask(self, step: str, instructions: str, data: list[dict[str, Any]], output_schema: dict[str, Any], *, model: str) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `step` | `str` | `—` | positional-or-keyword |
| `instructions` | `str` | `—` | positional-or-keyword |
| `data` | `list[dict[str, Any]]` | `—` | positional-or-keyword |
| `output_schema` | `dict[str, Any]` | `—` | positional-or-keyword |
| `model` | `str` | `—` | keyword-only |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `BudgetExhausted`, `InvalidModelOutput`, `JaneError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
One structured completion. Raises :class:`BudgetExhausted` or :class:`InvalidModelOutput`.
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_llm_budget.py:114](../../../../../../services/assistant/tests/test_llm_budget.py#L114).

```python
return llm.ask("probe", "Answer with the schema.", [part("page", text)], SCHEMA, model="default")
```
