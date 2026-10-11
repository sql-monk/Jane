# jane_assistant.improvement

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_assistant.improvement.ProblemCase](#jane_assistantimprovementproblemcase)
- [jane_assistant.improvement.ProblemCase.__init__](#jane_assistantimprovementproblemcase__init__)
- [jane_assistant.improvement.ProblemCase.name](#jane_assistantimprovementproblemcasename)
- [jane_assistant.improvement.ProblemCase.material](#jane_assistantimprovementproblemcasematerial)
- [jane_assistant.improvement.ProblemCase.text](#jane_assistantimprovementproblemcasetext)
- [jane_assistant.improvement.ProblemCase.diagnostics](#jane_assistantimprovementproblemcasediagnostics)
- [jane_assistant.improvement.ProblemCase.result](#jane_assistantimprovementproblemcaseresult)
- [jane_assistant.improvement.ProblemCase.signature](#jane_assistantimprovementproblemcasesignature)
- [jane_assistant.improvement.ProblemCase.source_id](#jane_assistantimprovementproblemcasesource_id)
- [jane_assistant.improvement.signature_of](#jane_assistantimprovementsignature_of)
- [jane_assistant.improvement.group_problems](#jane_assistantimprovementgroup_problems)
- [jane_assistant.improvement.ImproveOutcome](#jane_assistantimprovementimproveoutcome)
- [jane_assistant.improvement.ImproveOutcome.__init__](#jane_assistantimprovementimproveoutcome__init__)
- [jane_assistant.improvement.ImproveOutcome.draft](#jane_assistantimprovementimproveoutcomedraft)
- [jane_assistant.improvement.ImproveOutcome.outcomes](#jane_assistantimprovementimproveoutcomeoutcomes)
- [jane_assistant.improvement.ImproveOutcome.attempts](#jane_assistantimprovementimproveoutcomeattempts)
- [jane_assistant.improvement.ImproveOutcome.schema_change](#jane_assistantimprovementimproveoutcomeschema_change)
- [jane_assistant.improvement.ImproveOutcome.suggested](#jane_assistantimprovementimproveoutcomesuggested)
- [jane_assistant.improvement.ImproveOutcome.change_summary](#jane_assistantimprovementimproveoutcomechange_summary)
- [jane_assistant.improvement.ImproveOutcome.reason](#jane_assistantimprovementimproveoutcomereason)
- [jane_assistant.improvement.ImproveOutcome.other_bindings_failed](#jane_assistantimprovementimproveoutcomeother_bindings_failed)
- [jane_assistant.improvement.improve_draft](#jane_assistantimprovementimprove_draft)
- [jane_assistant.improvement.run_improvement](#jane_assistantimprovementrun_improvement)

## jane_assistant.improvement.ProblemCase

**Клас.** Код: [services/assistant/src/jane_assistant/improvement.py:55](../../../../../../services/assistant/src/jane_assistant/improvement.py#L55).

```python
class ProblemCase:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_assistant.improvement.md#jane_assistantimprovementproblemcasename) | Поле | ні |
| [material](jane_assistant.improvement.md#jane_assistantimprovementproblemcasematerial) | Поле | ні |
| [text](jane_assistant.improvement.md#jane_assistantimprovementproblemcasetext) | Поле | ні |
| [diagnostics](jane_assistant.improvement.md#jane_assistantimprovementproblemcasediagnostics) | Поле | ні |
| [result](jane_assistant.improvement.md#jane_assistantimprovementproblemcaseresult) | Поле | ні |
| [signature](jane_assistant.improvement.md#jane_assistantimprovementproblemcasesignature) | Поле | ні |
| [source_id](jane_assistant.improvement.md#jane_assistantimprovementproblemcasesource_id) | Поле | ні |
| [__init__](jane_assistant.improvement.md#jane_assistantimprovementproblemcase__init__) | Конструктор dataclass | ні |

## jane_assistant.improvement.ProblemCase.__init__

**Конструктор dataclass.** Код: [services/assistant/src/jane_assistant/improvement.py:55](../../../../../../services/assistant/src/jane_assistant/improvement.py#L55).

```python
def __init__(self, name: str, material: dict[str, Any], text: str, diagnostics: list[dict[str, Any]] = <factory list>, result: dict[str, Any] | None = None, signature: str = 'unknown', source_id: str | None = None) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `name` | `str` | `—` | positional-or-keyword |
| `material` | `dict[str, Any]` | `—` | positional-or-keyword |
| `text` | `str` | `—` | positional-or-keyword |
| `diagnostics` | `list[dict[str, Any]]` | `factory: list` | positional-or-keyword |
| `result` | `dict[str, Any] \| None` | `None` | positional-or-keyword |
| `signature` | `str` | `'unknown'` | positional-or-keyword |
| `source_id` | `str \| None` | `None` | positional-or-keyword |

Результат: `None`.

## jane_assistant.improvement.ProblemCase.name

**Поле.** Код: [services/assistant/src/jane_assistant/improvement.py:56](../../../../../../services/assistant/src/jane_assistant/improvement.py#L56).

```python
name: str
```

Доступ: читання — так; запис — так.

## jane_assistant.improvement.ProblemCase.material

**Поле.** Код: [services/assistant/src/jane_assistant/improvement.py:57](../../../../../../services/assistant/src/jane_assistant/improvement.py#L57).

```python
material: dict[str, Any]
```

Доступ: читання — так; запис — так.

## jane_assistant.improvement.ProblemCase.text

**Поле.** Код: [services/assistant/src/jane_assistant/improvement.py:58](../../../../../../services/assistant/src/jane_assistant/improvement.py#L58).

```python
text: str
```

Доступ: читання — так; запис — так.

## jane_assistant.improvement.ProblemCase.diagnostics

**Поле.** Код: [services/assistant/src/jane_assistant/improvement.py:59](../../../../../../services/assistant/src/jane_assistant/improvement.py#L59).

```python
diagnostics: list[dict[str, Any]] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_assistant.improvement.ProblemCase.result

**Поле.** Код: [services/assistant/src/jane_assistant/improvement.py:60](../../../../../../services/assistant/src/jane_assistant/improvement.py#L60).

```python
result: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.improvement.ProblemCase.signature

**Поле.** Код: [services/assistant/src/jane_assistant/improvement.py:61](../../../../../../services/assistant/src/jane_assistant/improvement.py#L61).

```python
signature: str = 'unknown'
```

Доступ: читання — так; запис — так.

## jane_assistant.improvement.ProblemCase.source_id

**Поле.** Код: [services/assistant/src/jane_assistant/improvement.py:62](../../../../../../services/assistant/src/jane_assistant/improvement.py#L62).

```python
source_id: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.improvement.signature_of

**Функція.** Код: [services/assistant/src/jane_assistant/improvement.py:65](../../../../../../services/assistant/src/jane_assistant/improvement.py#L65).

```python
def signature_of(result: dict[str, Any] | None, diagnostics: list[dict[str, Any]]) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `result` | `dict[str, Any] \| None` | `—` | positional-or-keyword |
| `diagnostics` | `list[dict[str, Any]]` | `—` | positional-or-keyword |

Результат: `str`.

## jane_assistant.improvement.group_problems

**Функція.** Код: [services/assistant/src/jane_assistant/improvement.py:84](../../../../../../services/assistant/src/jane_assistant/improvement.py#L84).

```python
def group_problems(cases: list[ProblemCase]) -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cases` | `list[ProblemCase]` | `—` | positional-or-keyword |

Результат: `list[dict[str, Any]]`.

## jane_assistant.improvement.ImproveOutcome

**Клас.** Код: [services/assistant/src/jane_assistant/improvement.py:122](../../../../../../services/assistant/src/jane_assistant/improvement.py#L122).

```python
class ImproveOutcome:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [draft](jane_assistant.improvement.md#jane_assistantimprovementimproveoutcomedraft) | Поле | ні |
| [outcomes](jane_assistant.improvement.md#jane_assistantimprovementimproveoutcomeoutcomes) | Поле | ні |
| [attempts](jane_assistant.improvement.md#jane_assistantimprovementimproveoutcomeattempts) | Поле | ні |
| [schema_change](jane_assistant.improvement.md#jane_assistantimprovementimproveoutcomeschema_change) | Поле | ні |
| [suggested](jane_assistant.improvement.md#jane_assistantimprovementimproveoutcomesuggested) | Поле | ні |
| [change_summary](jane_assistant.improvement.md#jane_assistantimprovementimproveoutcomechange_summary) | Поле | ні |
| [reason](jane_assistant.improvement.md#jane_assistantimprovementimproveoutcomereason) | Поле | ні |
| [other_bindings_failed](jane_assistant.improvement.md#jane_assistantimprovementimproveoutcomeother_bindings_failed) | Поле | ні |
| [__init__](jane_assistant.improvement.md#jane_assistantimprovementimproveoutcome__init__) | Конструктор dataclass | ні |

## jane_assistant.improvement.ImproveOutcome.__init__

**Конструктор dataclass.** Код: [services/assistant/src/jane_assistant/improvement.py:122](../../../../../../services/assistant/src/jane_assistant/improvement.py#L122).

```python
def __init__(self, draft: PackageDraft | None, outcomes: list[TestOutcome], attempts: int, schema_change: str = 'none', suggested: list[str] = <factory list>, change_summary: str = '', reason: str | None = None, other_bindings_failed: bool = False) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `draft` | `PackageDraft \| None` | `—` | positional-or-keyword |
| `outcomes` | `list[TestOutcome]` | `—` | positional-or-keyword |
| `attempts` | `int` | `—` | positional-or-keyword |
| `schema_change` | `str` | `'none'` | positional-or-keyword |
| `suggested` | `list[str]` | `factory: list` | positional-or-keyword |
| `change_summary` | `str` | `''` | positional-or-keyword |
| `reason` | `str \| None` | `None` | positional-or-keyword |
| `other_bindings_failed` | `bool` | `False` | positional-or-keyword |

Результат: `None`.

## jane_assistant.improvement.ImproveOutcome.draft

**Поле.** Код: [services/assistant/src/jane_assistant/improvement.py:123](../../../../../../services/assistant/src/jane_assistant/improvement.py#L123).

```python
draft: PackageDraft | None
```

Доступ: читання — так; запис — так.

## jane_assistant.improvement.ImproveOutcome.outcomes

**Поле.** Код: [services/assistant/src/jane_assistant/improvement.py:124](../../../../../../services/assistant/src/jane_assistant/improvement.py#L124).

```python
outcomes: list[TestOutcome]
```

Доступ: читання — так; запис — так.

## jane_assistant.improvement.ImproveOutcome.attempts

**Поле.** Код: [services/assistant/src/jane_assistant/improvement.py:125](../../../../../../services/assistant/src/jane_assistant/improvement.py#L125).

```python
attempts: int
```

Доступ: читання — так; запис — так.

## jane_assistant.improvement.ImproveOutcome.schema_change

**Поле.** Код: [services/assistant/src/jane_assistant/improvement.py:126](../../../../../../services/assistant/src/jane_assistant/improvement.py#L126).

```python
schema_change: str = 'none'
```

Доступ: читання — так; запис — так.

## jane_assistant.improvement.ImproveOutcome.suggested

**Поле.** Код: [services/assistant/src/jane_assistant/improvement.py:127](../../../../../../services/assistant/src/jane_assistant/improvement.py#L127).

```python
suggested: list[str] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_assistant.improvement.ImproveOutcome.change_summary

**Поле.** Код: [services/assistant/src/jane_assistant/improvement.py:128](../../../../../../services/assistant/src/jane_assistant/improvement.py#L128).

```python
change_summary: str = ''
```

Доступ: читання — так; запис — так.

## jane_assistant.improvement.ImproveOutcome.reason

**Поле.** Код: [services/assistant/src/jane_assistant/improvement.py:129](../../../../../../services/assistant/src/jane_assistant/improvement.py#L129).

```python
reason: str | None = None
```

Доступ: читання — так; запис — так.

## jane_assistant.improvement.ImproveOutcome.other_bindings_failed

**Поле.** Код: [services/assistant/src/jane_assistant/improvement.py:130](../../../../../../services/assistant/src/jane_assistant/improvement.py#L130).

```python
other_bindings_failed: bool = False
```

Доступ: читання — так; запис — так.

## jane_assistant.improvement.improve_draft

**Функція.** Код: [services/assistant/src/jane_assistant/improvement.py:189](../../../../../../services/assistant/src/jane_assistant/improvement.py#L189).

```python
async def improve_draft(*, nb: Neighbours, llm: LlmSession, settings: Settings, limits: ServiceLimits, validator: SchemaValidator, base: PackageDraft, version_after: Any, problems: list[ProblemCase], successes: list[ProblemCase], bindings: list[BindingContext], attempts: int, job_key: str, job_id: str, reason: str='improvement', retry_on_other_failure: bool=True) -> ImproveOutcome:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `nb` | `Neighbours` | `—` | keyword-only |
| `llm` | `LlmSession` | `—` | keyword-only |
| `settings` | `Settings` | `—` | keyword-only |
| `limits` | `ServiceLimits` | `—` | keyword-only |
| `validator` | `SchemaValidator` | `—` | keyword-only |
| `base` | `PackageDraft` | `—` | keyword-only |
| `version_after` | `Any` | `—` | keyword-only |
| `problems` | `list[ProblemCase]` | `—` | keyword-only |
| `successes` | `list[ProblemCase]` | `—` | keyword-only |
| `bindings` | `list[BindingContext]` | `—` | keyword-only |
| `attempts` | `int` | `—` | keyword-only |
| `job_key` | `str` | `—` | keyword-only |
| `job_id` | `str` | `—` | keyword-only |
| `reason` | `str` | `'improvement'` | keyword-only |
| `retry_on_other_failure` | `bool` | `True` | keyword-only |

Результат: `ImproveOutcome`.

### Опис із вихідного коду

```text
Ask the model for a fixed version until one passes all checks or attempts run out.

``version_after(schema_change) -> str`` picks the new version number (SemVer part by change).
```

## jane_assistant.improvement.run_improvement

**Функція.** Код: [services/assistant/src/jane_assistant/improvement.py:419](../../../../../../services/assistant/src/jane_assistant/improvement.py#L419).

```python
async def run_improvement(*, nb: Neighbours, req: dict[str, Any], settings: Settings, limits: ServiceLimits, validator: SchemaValidator, job_id: str, progress: Any) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `nb` | `Neighbours` | `—` | keyword-only |
| `req` | `dict[str, Any]` | `—` | keyword-only |
| `settings` | `Settings` | `—` | keyword-only |
| `limits` | `ServiceLimits` | `—` | keyword-only |
| `validator` | `SchemaValidator` | `—` | keyword-only |
| `job_id` | `str` | `—` | keyword-only |
| `progress` | `Any` | `—` | keyword-only |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.
