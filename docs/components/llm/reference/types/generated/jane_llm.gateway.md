# jane_llm.gateway

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_llm.gateway.log](#jane_llmgatewaylog)
- [jane_llm.gateway.BudgetExhausted](#jane_llmgatewaybudgetexhausted)
- [jane_llm.gateway.BudgetExhausted.code](#jane_llmgatewaybudgetexhaustedcode)
- [jane_llm.gateway.budget_key](#jane_llmgatewaybudget_key)
- [jane_llm.gateway.window](#jane_llmgatewaywindow)
- [jane_llm.gateway.Scope](#jane_llmgatewayscope)
- [jane_llm.gateway.Scope.__init__](#jane_llmgatewayscope__init__)
- [jane_llm.gateway.Scope.source_id](#jane_llmgatewayscopesource_id)
- [jane_llm.gateway.Scope.task_id](#jane_llmgatewayscopetask_id)
- [jane_llm.gateway.Scope.run_id](#jane_llmgatewayscoperun_id)
- [jane_llm.gateway.Scope.purpose](#jane_llmgatewayscopepurpose)
- [jane_llm.gateway.Scope.levels](#jane_llmgatewayscopelevels)
- [jane_llm.gateway.ResolvedModel](#jane_llmgatewayresolvedmodel)
- [jane_llm.gateway.ResolvedModel.__init__](#jane_llmgatewayresolvedmodel__init__)
- [jane_llm.gateway.ResolvedModel.provider](#jane_llmgatewayresolvedmodelprovider)
- [jane_llm.gateway.ResolvedModel.model](#jane_llmgatewayresolvedmodelmodel)
- [jane_llm.gateway.ResolvedModel.adapter](#jane_llmgatewayresolvedmodeladapter)
- [jane_llm.gateway.ResolvedModel.connection](#jane_llmgatewayresolvedmodelconnection)
- [jane_llm.gateway.validate_output](#jane_llmgatewayvalidate_output)
- [jane_llm.gateway.Gateway](#jane_llmgatewaygateway)
- [jane_llm.gateway.Gateway.__init__](#jane_llmgatewaygateway__init__)
- [jane_llm.gateway.Gateway.store](#jane_llmgatewaygatewaystore)
- [jane_llm.gateway.Gateway.settings](#jane_llmgatewaygatewaysettings)
- [jane_llm.gateway.Gateway.resolved](#jane_llmgatewaygatewayresolved)
- [jane_llm.gateway.Gateway.adapters](#jane_llmgatewaygatewayadapters)
- [jane_llm.gateway.Gateway.nonce_factory](#jane_llmgatewaygatewaynonce_factory)
- [jane_llm.gateway.Gateway.clock](#jane_llmgatewaygatewayclock)
- [jane_llm.gateway.Gateway.metrics](#jane_llmgatewaygatewaymetrics)
- [jane_llm.gateway.Gateway.limits](#jane_llmgatewaygatewaylimits)
- [jane_llm.gateway.Gateway.resolve_model](#jane_llmgatewaygatewayresolve_model)
- [jane_llm.gateway.Gateway.budget_definitions](#jane_llmgatewaygatewaybudget_definitions)
- [jane_llm.gateway.Gateway.budget_status](#jane_llmgatewaygatewaybudget_status)
- [jane_llm.gateway.Gateway.effective_limits](#jane_llmgatewaygatewayeffective_limits)
- [jane_llm.gateway.Gateway.complete](#jane_llmgatewaygatewaycomplete)

## jane_llm.gateway.log

**Змінна.** Код: [services/llm/src/jane_llm/gateway.py:63](../../../../../../services/llm/src/jane_llm/gateway.py#L63).

```python
log = logging.getLogger(__name__)
```

## jane_llm.gateway.BudgetExhausted

**Клас.** Код: [services/llm/src/jane_llm/gateway.py:66](../../../../../../services/llm/src/jane_llm/gateway.py#L66).

```python
class BudgetExhausted(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_llm.gateway.md#jane_llmgatewaybudgetexhaustedcode) | Поле | ні |
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

## jane_llm.gateway.BudgetExhausted.code

**Поле.** Код: [services/llm/src/jane_llm/gateway.py:67](../../../../../../services/llm/src/jane_llm/gateway.py#L67).

```python
code = 'budget_exhausted'
```

Доступ: читання — так; запис — так.

## jane_llm.gateway.budget_key

**Функція.** Код: [services/llm/src/jane_llm/gateway.py:70](../../../../../../services/llm/src/jane_llm/gateway.py#L70).

```python
def budget_key(scope_type: str, scope_id: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `scope_type` | `str` | `—` | positional-or-keyword |
| `scope_id` | `str` | `—` | positional-or-keyword |

Результат: `str`.

## jane_llm.gateway.window

**Функція.** Код: [services/llm/src/jane_llm/gateway.py:74](../../../../../../services/llm/src/jane_llm/gateway.py#L74).

```python
def window(period: str, now: datetime, run_id: str | None) -> tuple[str, datetime | None] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `period` | `str` | `—` | positional-or-keyword |
| `now` | `datetime` | `—` | positional-or-keyword |
| `run_id` | `str \| None` | `—` | positional-or-keyword |

Результат: `tuple[str, datetime | None] | None`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Counter window of a budget period and when it resets (``None`` for ``total`` and ``run``).
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_units.py:100](../../../../../../services/llm/tests/test_units.py#L100).

```python
assert window("day", now, None) == ("day:2026-09-27", datetime(2026, 9, 28, tzinfo=UTC))
```

Контекст і передумови: [services/llm/tests/test_units.py:101](../../../../../../services/llm/tests/test_units.py#L101).

```python
assert window("week", now, None) == ("week:2026-W39", datetime(2026, 9, 28, tzinfo=UTC))
```

## jane_llm.gateway.Scope

**Клас.** Код: [services/llm/src/jane_llm/gateway.py:94](../../../../../../services/llm/src/jane_llm/gateway.py#L94).

```python
class Scope:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [source_id](jane_llm.gateway.md#jane_llmgatewayscopesource_id) | Поле | ні |
| [task_id](jane_llm.gateway.md#jane_llmgatewayscopetask_id) | Поле | ні |
| [run_id](jane_llm.gateway.md#jane_llmgatewayscoperun_id) | Поле | ні |
| [purpose](jane_llm.gateway.md#jane_llmgatewayscopepurpose) | Поле | ні |
| [levels](jane_llm.gateway.md#jane_llmgatewayscopelevels) | Метод | ні |
| [__init__](jane_llm.gateway.md#jane_llmgatewayscope__init__) | Конструктор dataclass | ні |

## jane_llm.gateway.Scope.__init__

**Конструктор dataclass.** Код: [services/llm/src/jane_llm/gateway.py:94](../../../../../../services/llm/src/jane_llm/gateway.py#L94).

```python
def __init__(self, source_id: str | None, task_id: str | None, run_id: str | None, purpose: str) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `source_id` | `str \| None` | `—` | positional-or-keyword |
| `task_id` | `str \| None` | `—` | positional-or-keyword |
| `run_id` | `str \| None` | `—` | positional-or-keyword |
| `purpose` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.gateway.Scope.source_id

**Поле.** Код: [services/llm/src/jane_llm/gateway.py:95](../../../../../../services/llm/src/jane_llm/gateway.py#L95).

```python
source_id: str | None
```

Доступ: читання — так; запис — ні.

## jane_llm.gateway.Scope.task_id

**Поле.** Код: [services/llm/src/jane_llm/gateway.py:96](../../../../../../services/llm/src/jane_llm/gateway.py#L96).

```python
task_id: str | None
```

Доступ: читання — так; запис — ні.

## jane_llm.gateway.Scope.run_id

**Поле.** Код: [services/llm/src/jane_llm/gateway.py:97](../../../../../../services/llm/src/jane_llm/gateway.py#L97).

```python
run_id: str | None
```

Доступ: читання — так; запис — ні.

## jane_llm.gateway.Scope.purpose

**Поле.** Код: [services/llm/src/jane_llm/gateway.py:98](../../../../../../services/llm/src/jane_llm/gateway.py#L98).

```python
purpose: str
```

Доступ: читання — так; запис — ні.

## jane_llm.gateway.Scope.levels

**Метод.** Код: [services/llm/src/jane_llm/gateway.py:100](../../../../../../services/llm/src/jane_llm/gateway.py#L100).

```python
def levels(self) -> list[tuple[str, str]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `list[tuple[str, str]]`.

## jane_llm.gateway.ResolvedModel

**Клас.** Код: [services/llm/src/jane_llm/gateway.py:110](../../../../../../services/llm/src/jane_llm/gateway.py#L110).

```python
class ResolvedModel:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [provider](jane_llm.gateway.md#jane_llmgatewayresolvedmodelprovider) | Поле | ні |
| [model](jane_llm.gateway.md#jane_llmgatewayresolvedmodelmodel) | Поле | ні |
| [adapter](jane_llm.gateway.md#jane_llmgatewayresolvedmodeladapter) | Поле | ні |
| [connection](jane_llm.gateway.md#jane_llmgatewayresolvedmodelconnection) | Поле | ні |
| [__init__](jane_llm.gateway.md#jane_llmgatewayresolvedmodel__init__) | Конструктор dataclass | ні |

## jane_llm.gateway.ResolvedModel.__init__

**Конструктор dataclass.** Код: [services/llm/src/jane_llm/gateway.py:110](../../../../../../services/llm/src/jane_llm/gateway.py#L110).

```python
def __init__(self, provider: Provider, model: ModelInfo, adapter: ProviderAdapter, connection: ResolvedConnection | None) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `provider` | `Provider` | `—` | positional-or-keyword |
| `model` | `ModelInfo` | `—` | positional-or-keyword |
| `adapter` | `ProviderAdapter` | `—` | positional-or-keyword |
| `connection` | `ResolvedConnection \| None` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.gateway.ResolvedModel.provider

**Поле.** Код: [services/llm/src/jane_llm/gateway.py:111](../../../../../../services/llm/src/jane_llm/gateway.py#L111).

```python
provider: Provider
```

Доступ: читання — так; запис — ні.

## jane_llm.gateway.ResolvedModel.model

**Поле.** Код: [services/llm/src/jane_llm/gateway.py:112](../../../../../../services/llm/src/jane_llm/gateway.py#L112).

```python
model: ModelInfo
```

Доступ: читання — так; запис — ні.

## jane_llm.gateway.ResolvedModel.adapter

**Поле.** Код: [services/llm/src/jane_llm/gateway.py:113](../../../../../../services/llm/src/jane_llm/gateway.py#L113).

```python
adapter: ProviderAdapter
```

Доступ: читання — так; запис — ні.

## jane_llm.gateway.ResolvedModel.connection

**Поле.** Код: [services/llm/src/jane_llm/gateway.py:114](../../../../../../services/llm/src/jane_llm/gateway.py#L114).

```python
connection: ResolvedConnection | None
```

Доступ: читання — так; запис — ні.

## jane_llm.gateway.validate_output

**Функція.** Код: [services/llm/src/jane_llm/gateway.py:122](../../../../../../services/llm/src/jane_llm/gateway.py#L122).

```python
def validate_output(schema: dict[str, Any], text: str) -> tuple[Any, list[dict[str, str]], list[tuple[str, str]]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `schema` | `dict[str, Any]` | `—` | positional-or-keyword |
| `text` | `str` | `—` | positional-or-keyword |

Результат: `tuple[Any, list[dict[str, str]], list[tuple[str, str]]]`.

### Опис із вихідного коду

```text
Parse and validate model output.

Returns ``(output, errors for the caller, hints)``. Errors for the caller carry instance pointers; the
hints for a schema retry go to the trusted channel, so they are built **only from the schema**
(``schema_path`` and the violated keyword) — instance paths may contain keys chosen by the model or
the data (``additionalProperties``, ``patternProperties``) and must never reach the system prompt.
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_units.py:62](../../../../../../services/llm/tests/test_units.py#L62).

```python
_, errors, _ = validate_output(schema, json.dumps(value))
```

Контекст і передумови: [services/llm/tests/test_units.py:91](../../../../../../services/llm/tests/test_units.py#L91).

````python
out, errors, hints = validate_output(schema, '```json\n{"n": "x"}\n```')
````

## jane_llm.gateway.Gateway

**Клас.** Код: [services/llm/src/jane_llm/gateway.py:145](../../../../../../services/llm/src/jane_llm/gateway.py#L145).

```python
class Gateway:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_llm.gateway.md#jane_llmgatewaygateway__init__) | Конструктор | ні |
| [store](jane_llm.gateway.md#jane_llmgatewaygatewaystore) | Поле екземпляра | ні |
| [settings](jane_llm.gateway.md#jane_llmgatewaygatewaysettings) | Поле екземпляра | ні |
| [resolved](jane_llm.gateway.md#jane_llmgatewaygatewayresolved) | Поле екземпляра | ні |
| [adapters](jane_llm.gateway.md#jane_llmgatewaygatewayadapters) | Поле екземпляра | ні |
| [nonce_factory](jane_llm.gateway.md#jane_llmgatewaygatewaynonce_factory) | Поле екземпляра | ні |
| [clock](jane_llm.gateway.md#jane_llmgatewaygatewayclock) | Поле екземпляра | ні |
| [metrics](jane_llm.gateway.md#jane_llmgatewaygatewaymetrics) | Поле екземпляра | ні |
| [limits](jane_llm.gateway.md#jane_llmgatewaygatewaylimits) | Властивість | ні |
| [resolve_model](jane_llm.gateway.md#jane_llmgatewaygatewayresolve_model) | Метод | ні |
| [budget_definitions](jane_llm.gateway.md#jane_llmgatewaygatewaybudget_definitions) | Метод | ні |
| [budget_status](jane_llm.gateway.md#jane_llmgatewaygatewaybudget_status) | Метод | ні |
| [effective_limits](jane_llm.gateway.md#jane_llmgatewaygatewayeffective_limits) | Метод | ні |
| [complete](jane_llm.gateway.md#jane_llmgatewaygatewaycomplete) | Метод | ні |

## jane_llm.gateway.Gateway.__init__

**Конструктор.** Код: [services/llm/src/jane_llm/gateway.py:146](../../../../../../services/llm/src/jane_llm/gateway.py#L146).

```python
def __init__(self, store: Store, settings: Settings, limits: ResolvedLimits[ServiceLimits], *, adapters: dict[str, ProviderAdapter] | None=None, nonce_factory: NonceFactory=new_nonce, clock: Callable[[], datetime]=lambda: datetime.now(UTC), metrics: Any=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `store` | `Store` | `—` | positional-or-keyword |
| `settings` | `Settings` | `—` | positional-or-keyword |
| `limits` | `ResolvedLimits[ServiceLimits]` | `—` | positional-or-keyword |
| `adapters` | `dict[str, ProviderAdapter] \| None` | `None` | keyword-only |
| `nonce_factory` | `NonceFactory` | `new_nonce` | keyword-only |
| `clock` | `Callable[[], datetime]` | `lambda: datetime.now(UTC)` | keyword-only |
| `metrics` | `Any` | `None` | keyword-only |

Результат: `None`.

## jane_llm.gateway.Gateway.store

**Поле екземпляра.** Код: [services/llm/src/jane_llm/gateway.py:157](../../../../../../services/llm/src/jane_llm/gateway.py#L157).

```python
self.store = store
```

## jane_llm.gateway.Gateway.settings

**Поле екземпляра.** Код: [services/llm/src/jane_llm/gateway.py:158](../../../../../../services/llm/src/jane_llm/gateway.py#L158).

```python
self.settings = settings
```

## jane_llm.gateway.Gateway.resolved

**Поле екземпляра.** Код: [services/llm/src/jane_llm/gateway.py:159](../../../../../../services/llm/src/jane_llm/gateway.py#L159).

```python
self.resolved = limits
```

## jane_llm.gateway.Gateway.adapters

**Поле екземпляра.** Код: [services/llm/src/jane_llm/gateway.py:160](../../../../../../services/llm/src/jane_llm/gateway.py#L160).

```python
self.adapters = adapters or ADAPTERS
```

## jane_llm.gateway.Gateway.nonce_factory

**Поле екземпляра.** Код: [services/llm/src/jane_llm/gateway.py:161](../../../../../../services/llm/src/jane_llm/gateway.py#L161).

```python
self.nonce_factory = nonce_factory
```

## jane_llm.gateway.Gateway.clock

**Поле екземпляра.** Код: [services/llm/src/jane_llm/gateway.py:162](../../../../../../services/llm/src/jane_llm/gateway.py#L162).

```python
self.clock = clock
```

## jane_llm.gateway.Gateway.metrics

**Поле екземпляра.** Код: [services/llm/src/jane_llm/gateway.py:163](../../../../../../services/llm/src/jane_llm/gateway.py#L163).

```python
self.metrics = metrics
```

## jane_llm.gateway.Gateway.limits

**Властивість.** Код: [services/llm/src/jane_llm/gateway.py:166](../../../../../../services/llm/src/jane_llm/gateway.py#L166).

```python
def limits(self) -> ServiceLimits:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `ServiceLimits`.

Доступ: читання — так; запис — ні.

## jane_llm.gateway.Gateway.resolve_model

**Метод.** Код: [services/llm/src/jane_llm/gateway.py:173](../../../../../../services/llm/src/jane_llm/gateway.py#L173).

```python
async def resolve_model(self, name: str | None) -> ResolvedModel:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `name` | `str \| None` | `—` | positional-or-keyword |

Результат: `ResolvedModel`.

Явні `raise` у тілі: `NotFound`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_llm.gateway.Gateway.budget_definitions

**Метод.** Код: [services/llm/src/jane_llm/gateway.py:206](../../../../../../services/llm/src/jane_llm/gateway.py#L206).

```python
async def budget_definitions(self, scope: Scope) -> list[tuple[str, str, BudgetDefinition | None]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `scope` | `Scope` | `—` | positional-or-keyword |

Результат: `list[tuple[str, str, BudgetDefinition | None]]`.

## jane_llm.gateway.Gateway.budget_status

**Метод.** Код: [services/llm/src/jane_llm/gateway.py:278](../../../../../../services/llm/src/jane_llm/gateway.py#L278).

```python
async def budget_status(self, checks: list[BudgetCheck]) -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `checks` | `list[BudgetCheck]` | `—` | positional-or-keyword |

Результат: `list[dict[str, Any]]`.

### Опис із вихідного коду

```text
``BudgetStatus`` per check: ``spent`` is the settled cost in the counter's window (reservations of
calls in flight are not included); ``exhausted`` = ``spent >= limit`` - no further call in this window
until it resets or the budget is raised (a call is refused earlier when its estimate does not fit).
```

## jane_llm.gateway.Gateway.effective_limits

**Метод.** Код: [services/llm/src/jane_llm/gateway.py:299](../../../../../../services/llm/src/jane_llm/gateway.py#L299).

```python
def effective_limits(self, request_limits: LlmLimitsIn | None) -> ServiceLimits:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `request_limits` | `LlmLimitsIn \| None` | `—` | positional-or-keyword |

Результат: `ServiceLimits`.

### Опис із вихідного коду

```text
Request limits over the platform ones, bounded by hard caps (budget and rpm handled separately).
```

## jane_llm.gateway.Gateway.complete

**Метод.** Код: [services/llm/src/jane_llm/gateway.py:311](../../../../../../services/llm/src/jane_llm/gateway.py#L311).

```python
async def complete(self, req: CompletionRequest, *, extra_data: list[DataBlock] | None=None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `req` | `CompletionRequest` | `—` | positional-or-keyword |
| `extra_data` | `list[DataBlock] \| None` | `None` | keyword-only |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `LimitExceeded`, `RateLimited`, `UpstreamUnavailable`, `ValidationFailed`, `self._budget_error`, `повторний raise`. Винятки викликаних залежностей описуються у ручному довіднику.
