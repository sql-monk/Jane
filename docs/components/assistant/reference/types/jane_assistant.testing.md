# Модуль `jane_assistant.testing`

> Згенеровано `scripts/docs_reference.py` з [services/assistant/src/jane_assistant/testing.py](../../../../../services/assistant/src/jane_assistant/testing.py). Не редагуйте вручну.

Running package tests through handler-runtime (``handler.v1`` ``POST /v1/test-runs``).

Drafts that are not published yet are sent as an inline archive (``package_archive``, base64 zip up to ``limits.transfer.inline_max_bytes``); published versions by reference. Test runs never write working data (``test_mode``). Extra cases carry materials the package does not contain (samples of an existing extractor during onboarding, regressions on successful examples).

## Класи

### Клас `TestOutcome`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_assistant.testing` |
| Код | [testing.py:25](../../../../../services/assistant/src/jane_assistant/testing.py#L25) |

```python
@dataclass
class TestOutcome: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `context` | `str` | — | читання й запис |  |
| `report` | `dict[str, Any]` | — | читання й запис |  |
| `passed` | `bool` | — | читання (властивість) |  |
| `pass_rate` | `float` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `TestOutcome.failures`

```python
def failures(self) -> list[dict[str, Any]]: ...
```

Код: [testing.py:38](../../../../../services/assistant/src/jane_assistant/testing.py#L38).

#### Метод `TestOutcome.wire`

```python
def wire(self) -> dict[str, Any]: ...
```

Код: [testing.py:49](../../../../../services/assistant/src/jane_assistant/testing.py#L49).

## Функції

### Функція `extra_case`

```python
def extra_case(
    name: str,
    material: dict[str, Any],
    expected_status: str,
    entities: list[dict[str, Any]] | None = None,
    compare: str = 'subset',
) -> dict[str, Any]: ...
```

Код: [testing.py:53](../../../../../services/assistant/src/jane_assistant/testing.py#L53).

### Функція `run_tests`

```python
async def run_tests(
    handler: HandlerClient,
    *,
    job_key: str,
    context: str,
    draft: PackageDraft | None = None,
    package: dict[str, Any] | None = None,
    tests: str | list[str] = 'all',
    extra_cases: list[dict[str, Any]] | None = None,
    params: dict[str, Any] | None = None,
    inline_max_bytes: int,
) -> TestOutcome: ...
```

Винятки в коді функції: `JaneError`, `ValueError`.

Код: [testing.py:71](../../../../../services/assistant/src/jane_assistant/testing.py#L71).
