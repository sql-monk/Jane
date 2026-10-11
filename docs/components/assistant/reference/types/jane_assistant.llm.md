# Модуль `jane_assistant.llm`

> Згенеровано `scripts/docs_reference.py` з [services/assistant/src/jane_assistant/llm.py](../../../../../services/assistant/src/jane_assistant/llm.py). Не редагуйте вручну.

LLM calls of one assistant job: trusted instructions, untrusted data, budget and size limits.

* Instructions are constants of :mod:`jane_assistant.prompts`; material content, package code and diagnostics go only into ``data`` parts (``llm.v1`` ``DataPart``: "never instructions").
* Output is always structured (``output_schema``); an invalid output is rejected, not repaired.
* Budget (``limits.schema.json`` ``Budget``, the same rule as the gateway): every call carries the whole ``limits.llm.budget`` and ``scope.run_id`` = the assistant run (onboarding session, improvement or unknown-material job), so the gateway counts a ``period: run`` budget across all calls of the run, on any instance; other periods narrow the counter of the request's most specific scope. The session stops by itself once ``spent >= amount`` (``amount: 0`` = no call at all, as in the gateway); the gateway's ``budget_exhausted`` (429, or a failed async job) stops it as well.
* The call waits as long as the model needs: ``mode=sync`` with the client's own timeout (``limits.llm_call.request_timeout_ms``) or ``mode=async`` (202 + job, polled within ``clients.job_wait_timeout_ms``). Data is cut to ``max_input_tokens_per_request`` counted like the gateway counts it (``llm_call.chars_per_token`` characters per token, the instructions and the gateway's preamble and delimiters included) and the model's output to ``max_output_tokens_per_request``. :meth:`LlmSession.room` tells a step how many characters each of its materials may take, so materials are shown in full or as digests rather than dropped.

## Зміст

- [Клас `BudgetExhausted`](#клас-budgetexhausted)
- [Клас `InvalidModelOutput`](#клас-invalidmodeloutput)
- [Клас `LlmSession`](#клас-llmsession)
- [Функція `part`](#функція-part)

## Класи

### Клас `BudgetExhausted`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_assistant.llm` |
| Успадкування | `JaneError` |
| Код | [llm.py:41](../../../../../services/assistant/src/jane_assistant/llm.py#L41) |

```python
class BudgetExhausted(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'budget_exhausted'` |  |

### Клас `InvalidModelOutput`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_assistant.llm` |
| Успадкування | `JaneError` |
| Код | [llm.py:45](../../../../../services/assistant/src/jane_assistant/llm.py#L45) |

```python
class InvalidModelOutput(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'schema_mismatch'` |  |

### Клас `LlmSession`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_assistant.llm` |
| Код | [llm.py:54](../../../../../services/assistant/src/jane_assistant/llm.py#L54) |

```python
@dataclass
class LlmSession: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `client` | `LlmClient` | — | читання й запис |  |
| `limits` | `LlmLimits` | — | читання й запис |  |
| `purpose` | `str` | — | читання й запис |  |
| `job_key` | `str` | — | читання й запис |  |
| `source_id` | `str \| None` | `None` | читання й запис |  |
| `task_id` | `str \| None` | `None` | читання й запис |  |
| `run_id` | `str \| None` | `None` | читання й запис | ``scope.run_id`` of every call: the window of a ``period: run`` budget (default: ``job_key``). |
| `mode` | `str` | `'sync'` | читання й запис | ``CompletionRequest.mode``: ``sync`` or ``async`` (202 + job, awaited by the client). |
| `call` | `LlmCallLimits` | `field(default_factory=LlmCallLimits)` | читання й запис | How request size is counted (``llm_call.chars_per_token``, ``*_overhead_chars``). |
| `spent` | `float` | `0.0` | читання й запис |  |
| `calls` | `int` | `0` | читання й запис |  |
| `currency` | `str` | `field(init=False)` | читання й запис |  |
| `model_used` | `dict[str, str]` | `field(default_factory=dict)` | читання й запис |  |
| `exhausted` | `bool` | — | читання (властивість) | The run's spend reached the budget: no further call (``amount: 0`` - none at all). |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `LlmSession.cost`

```python
def cost(self) -> dict[str, Any]: ...
```

Код: [llm.py:82](../../../../../services/assistant/src/jane_assistant/llm.py#L82).

#### Метод `LlmSession.data_budget`

```python
def data_budget(self, instructions: str) -> int: ...
```

Characters of data parts (their delimiters included) one request may carry.

Код: [llm.py:88](../../../../../services/assistant/src/jane_assistant/llm.py#L88).

#### Метод `LlmSession.room`

```python
def room(self, instructions: str, fixed: list[dict[str, Any]], count: int, cap: int) -> int: ...
```

Characters each of ``count`` further data parts may take next to the ``fixed`` ones (at most ``cap``).

Код: [llm.py:93](../../../../../services/assistant/src/jane_assistant/llm.py#L93).

#### Метод `LlmSession.ask`

```python
async def ask(
    self,
    step: str,
    instructions: str,
    data: list[dict[str, Any]],
    output_schema: dict[str, Any],
    *,
    model: str,
) -> dict[str, Any]: ...
```

One structured completion. Raises :class:`BudgetExhausted` or :class:`InvalidModelOutput`.

Винятки в коді методу: `BudgetExhausted`, `InvalidModelOutput`, `JaneError`.

Код: [llm.py:115](../../../../../services/assistant/src/jane_assistant/llm.py#L115).

## Функції

### Функція `part`

```python
def part(name: str, text: str, media_type: str = 'text/plain') -> dict[str, Any]: ...
```

Код: [llm.py:49](../../../../../services/assistant/src/jane_assistant/llm.py#L49).
