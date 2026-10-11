# Модуль `jane_assistant.improvement`

> Згенеровано `scripts/docs_reference.py` з [services/assistant/src/jane_assistant/improvement.py](../../../../../services/assistant/src/jane_assistant/improvement.py). Не редагуйте вручну.

Improvement of an extractor on problem samples (ТЗ §9, plan.md WP-11 «Вдосконалення»).

1. Problem samples are grouped by source and character (unrecognized signature, failure kind or diagnostic codes); the model gets the grouped samples, the current code and schemas, the diagnostics and successful examples (which must keep working).
2. Each attempt produces a candidate version; it must pass the old tests, new tests made from the problem samples (``origin: problem_sample``) and regressions on successful examples, then the test suite with the params of every binding of a shared package (``listTasks?package_id=``).
3. A version that breaks bindings of other sources (or changes the schema incompatibly while the package is shared) becomes a fork for this source when ``policy.allow_fork``; otherwise the run is unresolved.
4. ``auto_changes_allowed = false`` -> proposal only, nothing is published; the result carries the proposal (``ImprovementResult.proposal``: changed files, manifest and diff against the improved version). ``policy.approval = auto_after_checks`` -> the version is approved and auto-activated on its bindings (the orchestrator re-checks the source policy); a partial activation is rolled back.
5. Attempts (``limits.llm.max_improvement_attempts``) and spend (``limits.llm.budget``) are bounded; an unresolved run is reported to the orchestrator's problem group (shown in the admin UI).

## Зміст

- [Клас `ImproveOutcome`](#клас-improveoutcome)
- [Клас `ProblemCase`](#клас-problemcase)
- [Функція `group_problems`](#функція-group_problems)
- [Функція `improve_draft`](#функція-improve_draft)
- [Функція `run_improvement`](#функція-run_improvement)
- [Функція `signature_of`](#функція-signature_of)

## Класи

### Клас `ImproveOutcome`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_assistant.improvement` |
| Код | [improvement.py:122](../../../../../services/assistant/src/jane_assistant/improvement.py#L122) |

```python
@dataclass
class ImproveOutcome: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `draft` | `PackageDraft \| None` | — | читання й запис |  |
| `outcomes` | `list[TestOutcome]` | — | читання й запис |  |
| `attempts` | `int` | — | читання й запис |  |
| `schema_change` | `str` | `'none'` | читання й запис |  |
| `suggested` | `list[str]` | `field(default_factory=list)` | читання й запис |  |
| `change_summary` | `str` | `''` | читання й запис |  |
| `reason` | `str \| None` | `None` | читання й запис |  |
| `other_bindings_failed` | `bool` | `False` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `ProblemCase`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_assistant.improvement` |
| Код | [improvement.py:55](../../../../../services/assistant/src/jane_assistant/improvement.py#L55) |

```python
@dataclass
class ProblemCase: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `name` | `str` | — | читання й запис |  |
| `material` | `dict[str, Any]` | — | читання й запис |  |
| `text` | `str` | — | читання й запис |  |
| `diagnostics` | `list[dict[str, Any]]` | `field(default_factory=list)` | читання й запис |  |
| `result` | `dict[str, Any] \| None` | `None` | читання й запис |  |
| `signature` | `str` | `'unknown'` | читання й запис |  |
| `source_id` | `str \| None` | `None` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `group_problems`

```python
def group_problems(cases: list[ProblemCase]) -> list[dict[str, Any]]: ...
```

Код: [improvement.py:84](../../../../../services/assistant/src/jane_assistant/improvement.py#L84).

### Функція `improve_draft`

```python
async def improve_draft(
    *,
    nb: Neighbours,
    llm: LlmSession,
    settings: Settings,
    limits: ServiceLimits,
    validator: SchemaValidator,
    base: PackageDraft,
    version_after: Any,
    problems: list[ProblemCase],
    successes: list[ProblemCase],
    bindings: list[BindingContext],
    attempts: int,
    job_key: str,
    job_id: str,
    reason: str = 'improvement',
    retry_on_other_failure: bool = True,
) -> ImproveOutcome: ...
```

Ask the model for a fixed version until one passes all checks or attempts run out.

``version_after(schema_change) -> str`` picks the new version number (SemVer part by change).

Код: [improvement.py:189](../../../../../services/assistant/src/jane_assistant/improvement.py#L189).

### Функція `run_improvement`

```python
async def run_improvement(
    *,
    nb: Neighbours,
    req: dict[str, Any],
    settings: Settings,
    limits: ServiceLimits,
    validator: SchemaValidator,
    job_id: str,
    progress: Any,
) -> dict[str, Any]: ...
```

Винятки в коді функції: `ValidationFailed`.

Код: [improvement.py:419](../../../../../services/assistant/src/jane_assistant/improvement.py#L419).

### Функція `signature_of`

```python
def signature_of(result: dict[str, Any] | None, diagnostics: list[dict[str, Any]]) -> str: ...
```

Код: [improvement.py:65](../../../../../services/assistant/src/jane_assistant/improvement.py#L65).
