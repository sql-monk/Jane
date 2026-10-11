# jane_assistant.testing

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_assistant.testing.TestOutcome](#jane_assistanttestingtestoutcome)
- [jane_assistant.testing.TestOutcome.__init__](#jane_assistanttestingtestoutcome__init__)
- [jane_assistant.testing.TestOutcome.context](#jane_assistanttestingtestoutcomecontext)
- [jane_assistant.testing.TestOutcome.report](#jane_assistanttestingtestoutcomereport)
- [jane_assistant.testing.TestOutcome.passed](#jane_assistanttestingtestoutcomepassed)
- [jane_assistant.testing.TestOutcome.pass_rate](#jane_assistanttestingtestoutcomepass_rate)
- [jane_assistant.testing.TestOutcome.failures](#jane_assistanttestingtestoutcomefailures)
- [jane_assistant.testing.TestOutcome.wire](#jane_assistanttestingtestoutcomewire)
- [jane_assistant.testing.extra_case](#jane_assistanttestingextra_case)
- [jane_assistant.testing.run_tests](#jane_assistanttestingrun_tests)

## jane_assistant.testing.TestOutcome

**Клас.** Код: [services/assistant/src/jane_assistant/testing.py:25](../../../../../../services/assistant/src/jane_assistant/testing.py#L25).

```python
class TestOutcome:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [context](jane_assistant.testing.md#jane_assistanttestingtestoutcomecontext) | Поле | ні |
| [report](jane_assistant.testing.md#jane_assistanttestingtestoutcomereport) | Поле | ні |
| [passed](jane_assistant.testing.md#jane_assistanttestingtestoutcomepassed) | Властивість | ні |
| [pass_rate](jane_assistant.testing.md#jane_assistanttestingtestoutcomepass_rate) | Властивість | ні |
| [failures](jane_assistant.testing.md#jane_assistanttestingtestoutcomefailures) | Метод | ні |
| [wire](jane_assistant.testing.md#jane_assistanttestingtestoutcomewire) | Метод | ні |
| [__init__](jane_assistant.testing.md#jane_assistanttestingtestoutcome__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:296](../../../../../../services/assistant/tests/test_units.py#L296).

```python
plan = ExtractorPlan(
        "product",
        "product",
        "create",
        {"package_id": "a.b", "version": "1.0.0"},
        0.4,
        TestOutcome("ctx", {"passed": 1, "failed": 0}),
        draft,
    )
```

## jane_assistant.testing.TestOutcome.__init__

**Конструктор dataclass.** Код: [services/assistant/src/jane_assistant/testing.py:25](../../../../../../services/assistant/src/jane_assistant/testing.py#L25).

```python
def __init__(self, context: str, report: dict[str, Any]) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `context` | `str` | `—` | positional-or-keyword |
| `report` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:296](../../../../../../services/assistant/tests/test_units.py#L296).

```python
plan = ExtractorPlan(
        "product",
        "product",
        "create",
        {"package_id": "a.b", "version": "1.0.0"},
        0.4,
        TestOutcome("ctx", {"passed": 1, "failed": 0}),
        draft,
    )
```

## jane_assistant.testing.TestOutcome.context

**Поле.** Код: [services/assistant/src/jane_assistant/testing.py:26](../../../../../../services/assistant/src/jane_assistant/testing.py#L26).

```python
context: str
```

Доступ: читання — так; запис — так.

## jane_assistant.testing.TestOutcome.report

**Поле.** Код: [services/assistant/src/jane_assistant/testing.py:27](../../../../../../services/assistant/src/jane_assistant/testing.py#L27).

```python
report: dict[str, Any]
```

Доступ: читання — так; запис — так.

## jane_assistant.testing.TestOutcome.passed

**Властивість.** Код: [services/assistant/src/jane_assistant/testing.py:30](../../../../../../services/assistant/src/jane_assistant/testing.py#L30).

```python
def passed(self) -> bool:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

Доступ: читання — так; запис — ні.

## jane_assistant.testing.TestOutcome.pass_rate

**Властивість.** Код: [services/assistant/src/jane_assistant/testing.py:34](../../../../../../services/assistant/src/jane_assistant/testing.py#L34).

```python
def pass_rate(self) -> float:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `float`.

Доступ: читання — так; запис — ні.

## jane_assistant.testing.TestOutcome.failures

**Метод.** Код: [services/assistant/src/jane_assistant/testing.py:38](../../../../../../services/assistant/src/jane_assistant/testing.py#L38).

```python
def failures(self) -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `list[dict[str, Any]]`.

## jane_assistant.testing.TestOutcome.wire

**Метод.** Код: [services/assistant/src/jane_assistant/testing.py:49](../../../../../../services/assistant/src/jane_assistant/testing.py#L49).

```python
def wire(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_assistant.testing.extra_case

**Функція.** Код: [services/assistant/src/jane_assistant/testing.py:53](../../../../../../services/assistant/src/jane_assistant/testing.py#L53).

```python
def extra_case(name: str, material: dict[str, Any], expected_status: str, entities: list[dict[str, Any]] | None=None, compare: str='subset') -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `name` | `str` | `—` | positional-or-keyword |
| `material` | `dict[str, Any]` | `—` | positional-or-keyword |
| `expected_status` | `str` | `—` | positional-or-keyword |
| `entities` | `list[dict[str, Any]] \| None` | `None` | positional-or-keyword |
| `compare` | `str` | `'subset'` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_assistant.testing.run_tests

**Функція.** Код: [services/assistant/src/jane_assistant/testing.py:71](../../../../../../services/assistant/src/jane_assistant/testing.py#L71).

```python
async def run_tests(handler: HandlerClient, *, job_key: str, context: str, draft: PackageDraft | None=None, package: dict[str, Any] | None=None, tests: str | list[str]='all', extra_cases: list[dict[str, Any]] | None=None, params: dict[str, Any] | None=None, inline_max_bytes: int) -> TestOutcome:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `handler` | `HandlerClient` | `—` | positional-or-keyword |
| `job_key` | `str` | `—` | keyword-only |
| `context` | `str` | `—` | keyword-only |
| `draft` | `PackageDraft \| None` | `None` | keyword-only |
| `package` | `dict[str, Any] \| None` | `None` | keyword-only |
| `tests` | `str \| list[str]` | `'all'` | keyword-only |
| `extra_cases` | `list[dict[str, Any]] \| None` | `None` | keyword-only |
| `params` | `dict[str, Any] \| None` | `None` | keyword-only |
| `inline_max_bytes` | `int` | `—` | keyword-only |

Результат: `TestOutcome`.

Явні `raise` у тілі: `JaneError`, `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.
