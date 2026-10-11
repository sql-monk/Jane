# jane_handler_runtime.testrun

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_handler_runtime.testrun.CaseSpec](#jane_handler_runtimetestruncasespec)
- [jane_handler_runtime.testrun.select_cases](#jane_handler_runtimetestrunselect_cases)
- [jane_handler_runtime.testrun.run_tests](#jane_handler_runtimetestrunrun_tests)

## jane_handler_runtime.testrun.CaseSpec

**Змінна.** Код: [services/handler-runtime/src/jane_handler_runtime/testrun.py:22](../../../../../../services/handler-runtime/src/jane_handler_runtime/testrun.py#L22).

```python
CaseSpec = dict[str, Any]
```

### Опис із вихідного коду

```text
``{"name", "input": HandlerInput, "params", "expected_status", "expected": HandlerOutput | None, "compare"}``
```

## jane_handler_runtime.testrun.select_cases

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/testrun.py:26](../../../../../../services/handler-runtime/src/jane_handler_runtime/testrun.py#L26).

```python
def select_cases(package: LoadedPackage, tests: str | Sequence[str] | None='all', extra_cases: Sequence[Mapping[str, Any]]=()) -> list[CaseSpec]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `package` | `LoadedPackage` | `—` | positional-or-keyword |
| `tests` | `str \| Sequence[str] \| None` | `'all'` | positional-or-keyword |
| `extra_cases` | `Sequence[Mapping[str, Any]]` | `()` | positional-or-keyword |

Результат: `list[CaseSpec]`.

Явні `raise` у тілі: `NotFound`, `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Manifest tests (``all`` / ``none`` / names) + extra cases, with inputs and expected outputs loaded.
```

## jane_handler_runtime.testrun.run_tests

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/testrun.py:79](../../../../../../services/handler-runtime/src/jane_handler_runtime/testrun.py#L79).

```python
async def run_tests(executor: Executor, package: LoadedPackage, cases: Sequence[CaseSpec], *, params: Mapping[str, Any] | None=None, limits: Mapping[str, Any] | None=None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `executor` | `Executor` | `—` | positional-or-keyword |
| `package` | `LoadedPackage` | `—` | positional-or-keyword |
| `cases` | `Sequence[CaseSpec]` | `—` | positional-or-keyword |
| `params` | `Mapping[str, Any] \| None` | `None` | keyword-only |
| `limits` | `Mapping[str, Any] \| None` | `None` | keyword-only |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `повторний raise`. Винятки викликаних залежностей описуються у ручному довіднику.
