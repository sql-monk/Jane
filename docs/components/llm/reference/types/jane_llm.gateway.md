# Модуль `jane_llm.gateway`

> Згенеровано `scripts/docs_reference.py` з [services/llm/src/jane_llm/gateway.py](../../../../../services/llm/src/jane_llm/gateway.py). Не редагуйте вручну.

LLM gateway core: model resolution, prompt assembly, budgets and rates, provider call, schema validation.

Budget semantics (``llm.v1``: platform -> source -> task; ``limits.schema.json`` ``Budget``):

* the platform budget is the stored ``BudgetDefinition`` ``platform/platform`` or, if none, the configured ``limits.llm.budget``; source and task budgets exist only when defined (``PUT /v1/budgets``);
* ``limits.llm.budget`` of a request is one more budget of the **most specific scope of the request** (``task`` if ``scope.task_id``, else ``source`` if ``scope.source_id``, else ``platform``). It only narrows: it never replaces a stored or platform budget. With the same currency and period as the stored budget of that scope both use one counter and the smaller amount applies; otherwise both are checked;
* a counter is ``(scope, currency, window)``; the window of ``day``/``week``/``month`` is the UTC calendar period, ``total`` has one window, ``run`` counts per ``scope.run_id`` and, without a ``run_id``, per this completion (all its schema retries) - a budget is never skipped;
* every applicable budget is checked before **each** provider call with a worst-case reservation (estimated input tokens + ``max_output_tokens`` at the model's price): the call happens only if ``spent < limit`` and ``spent + reserved + estimate <= limit`` for every budget, atomically in the shared store; after the call the reservation is replaced by the actual cost. So ``amount: 0`` allows no call at all (not even a zero-priced model), ``exhausted`` (``spent >= limit``) means no further call in the window, and a refused call never reaches the provider (429 ``budget_exhausted``);
* ``max_requests_per_minute`` is enforced per scope (platform, source, task and provider) the same way.

## Зміст

- [Клас `BudgetExhausted`](#клас-budgetexhausted)
- [Клас `Scope`](#клас-scope)
- [Клас `ResolvedModel`](#клас-resolvedmodel)
- [Клас `Gateway`](#клас-gateway)
- [Функція `budget_key`](#функція-budget_key)
- [Функція `window`](#функція-window)
- [Функція `validate_output`](#функція-validate_output)

## Класи

### Клас `BudgetExhausted`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_llm.gateway` |
| Успадкування | `JaneError` |
| Код | [gateway.py:66](../../../../../services/llm/src/jane_llm/gateway.py#L66) |

```python
class BudgetExhausted(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'budget_exhausted'` |  |

### Клас `Scope`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_llm.gateway` |
| Код | [gateway.py:94](../../../../../services/llm/src/jane_llm/gateway.py#L94) |

```python
@dataclass(frozen=True)
class Scope: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `source_id` | `str \| None` | — | читання |  |
| `task_id` | `str \| None` | — | читання |  |
| `run_id` | `str \| None` | — | читання |  |
| `purpose` | `str` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `Scope.levels`

```python
def levels(self) -> list[tuple[str, str]]: ...
```

Код: [gateway.py:100](../../../../../services/llm/src/jane_llm/gateway.py#L100).

### Клас `ResolvedModel`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_llm.gateway` |
| Код | [gateway.py:110](../../../../../services/llm/src/jane_llm/gateway.py#L110) |

```python
@dataclass(frozen=True)
class ResolvedModel: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `provider` | `Provider` | — | читання |  |
| `model` | `ModelInfo` | — | читання |  |
| `adapter` | `ProviderAdapter` | — | читання |  |
| `connection` | `ResolvedConnection \| None` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `Gateway`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.gateway` |
| Код | [gateway.py:145](../../../../../services/llm/src/jane_llm/gateway.py#L145) |

```python
class Gateway: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `limits` | `ServiceLimits` | — | читання (властивість) |  |

#### Конструктор `Gateway.__init__`

```python
def __init__(
    self,
    store: Store,
    settings: Settings,
    limits: ResolvedLimits[ServiceLimits],
    *,
    adapters: dict[str, ProviderAdapter] | None = None,
    nonce_factory: NonceFactory = new_nonce,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    metrics: Any = None,
) -> None: ...
```

Код: [gateway.py:146](../../../../../services/llm/src/jane_llm/gateway.py#L146).

#### Метод `Gateway.resolve_model`

```python
async def resolve_model(self, name: str | None) -> ResolvedModel: ...
```

Винятки в коді методу: `NotFound`, `ValidationFailed`.

Код: [gateway.py:173](../../../../../services/llm/src/jane_llm/gateway.py#L173).

#### Метод `Gateway.budget_definitions`

```python
async def budget_definitions(
    self,
    scope: Scope,
) -> list[tuple[str, str, BudgetDefinition | None]]: ...
```

Код: [gateway.py:206](../../../../../services/llm/src/jane_llm/gateway.py#L206).

#### Метод `Gateway.budget_status`

```python
async def budget_status(self, checks: list[BudgetCheck]) -> list[dict[str, Any]]: ...
```

``BudgetStatus`` per check: ``spent`` is the settled cost in the counter's window (reservations of calls in flight are not included); ``exhausted`` = ``spent >= limit`` - no further call in this window until it resets or the budget is raised (a call is refused earlier when its estimate does not fit).

Код: [gateway.py:278](../../../../../services/llm/src/jane_llm/gateway.py#L278).

#### Метод `Gateway.effective_limits`

```python
def effective_limits(self, request_limits: LlmLimitsIn | None) -> ServiceLimits: ...
```

Request limits over the platform ones, bounded by hard caps (budget and rpm handled separately).

Код: [gateway.py:299](../../../../../services/llm/src/jane_llm/gateway.py#L299).

#### Метод `Gateway.complete`

```python
async def complete(
    self,
    req: CompletionRequest,
    *,
    extra_data: list[DataBlock] | None = None,
) -> dict[str, Any]: ...
```

Винятки в коді методу: `ValidationFailed`, `LimitExceeded`, `RateLimited`, `UpstreamUnavailable`.

Код: [gateway.py:311](../../../../../services/llm/src/jane_llm/gateway.py#L311).

## Функції

### Функція `budget_key`

```python
def budget_key(scope_type: str, scope_id: str) -> str: ...
```

Код: [gateway.py:70](../../../../../services/llm/src/jane_llm/gateway.py#L70).

### Функція `window`

```python
def window(
    period: str,
    now: datetime,
    run_id: str | None,
) -> tuple[str, datetime | None] | None: ...
```

Counter window of a budget period and when it resets (``None`` for ``total`` and ``run``).

Винятки в коді функції: `ValueError`.

Код: [gateway.py:74](../../../../../services/llm/src/jane_llm/gateway.py#L74).

### Функція `validate_output`

```python
def validate_output(
    schema: dict[str, Any],
    text: str,
) -> tuple[Any, list[dict[str, str]], list[tuple[str, str]]]: ...
```

Parse and validate model output.

Returns ``(output, errors for the caller, hints)``. Errors for the caller carry instance pointers; the hints for a schema retry go to the trusted channel, so they are built **only from the schema** (``schema_path`` and the violated keyword) — instance paths may contain keys chosen by the model or the data (``additionalProperties``, ``patternProperties``) and must never reach the system prompt.

Код: [gateway.py:122](../../../../../services/llm/src/jane_llm/gateway.py#L122).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `log` | — | `logging.getLogger(__name__)` |  |
