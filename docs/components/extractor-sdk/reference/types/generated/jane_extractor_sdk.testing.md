# jane_extractor_sdk.testing

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_extractor_sdk.testing.apply_param_defaults](#jane_extractor_sdktestingapply_param_defaults)
- [jane_extractor_sdk.testing.run_local](#jane_extractor_sdktestingrun_local)
- [jane_extractor_sdk.testing.LocalCaseResult](#jane_extractor_sdktestinglocalcaseresult)
- [jane_extractor_sdk.testing.LocalCaseResult.__init__](#jane_extractor_sdktestinglocalcaseresult__init__)
- [jane_extractor_sdk.testing.LocalCaseResult.name](#jane_extractor_sdktestinglocalcaseresultname)
- [jane_extractor_sdk.testing.LocalCaseResult.passed](#jane_extractor_sdktestinglocalcaseresultpassed)
- [jane_extractor_sdk.testing.LocalCaseResult.expected_status](#jane_extractor_sdktestinglocalcaseresultexpected_status)
- [jane_extractor_sdk.testing.LocalCaseResult.actual_status](#jane_extractor_sdktestinglocalcaseresultactual_status)
- [jane_extractor_sdk.testing.LocalCaseResult.differences](#jane_extractor_sdktestinglocalcaseresultdifferences)
- [jane_extractor_sdk.testing.LocalCaseResult.result](#jane_extractor_sdktestinglocalcaseresultresult)
- [jane_extractor_sdk.testing.run_package_tests](#jane_extractor_sdktestingrun_package_tests)
- [jane_extractor_sdk.testing.assert_package_tests_pass](#jane_extractor_sdktestingassert_package_tests_pass)

## jane_extractor_sdk.testing.apply_param_defaults

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/testing.py:46](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py#L46).

```python
def apply_param_defaults(schema: Mapping[str, Any] | None, params: Mapping[str, Any] | None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `schema` | `Mapping[str, Any] \| None` | `—` | positional-or-keyword |
| `params` | `Mapping[str, Any] \| None` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
Top-level ``default`` values of an object ``params_schema`` for parameters that were not given.
```

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:312](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L312).

```python
assert apply_param_defaults(schema, {"b": "x"}) == {"a": 1, "b": "x"}
```

## jane_extractor_sdk.testing.run_local

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/testing.py:70](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py#L70).

```python
def run_local(package_dir: Path, handler_input: Mapping[str, Any] | None=None, *, file: Path | None=None, media_type: str | None=None, url: str | None=None, params: Mapping[str, Any] | None=None, test_mode: bool=True) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `package_dir` | `Path` | `—` | positional-or-keyword |
| `handler_input` | `Mapping[str, Any] \| None` | `None` | positional-or-keyword |
| `file` | `Path \| None` | `None` | keyword-only |
| `media_type` | `str \| None` | `None` | keyword-only |
| `url` | `str \| None` | `None` | keyword-only |
| `params` | `Mapping[str, Any] \| None` | `None` | keyword-only |
| `test_mode` | `bool` | `True` | keyword-only |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Run the entry callable in this process on one input; return a simplified result::

{"status": "success|empty|unrecognized|failed", "output": {"entities": [...]}, "unrecognized": {...},
 "diagnostics": [...], "error": {...}}
```

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:300](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L300).

```python
result = run_local(
        EXAMPLE,
        file=EXAMPLE / "tests" / "product-phone-gamma" / "page.html",
        media_type="text/html",
        params={"include_url": False},
    )
```

## jane_extractor_sdk.testing.LocalCaseResult

**Клас.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/testing.py:133](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py#L133).

```python
class LocalCaseResult:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_extractor_sdk.testing.md#jane_extractor_sdktestinglocalcaseresultname) | Поле | ні |
| [passed](jane_extractor_sdk.testing.md#jane_extractor_sdktestinglocalcaseresultpassed) | Поле | ні |
| [expected_status](jane_extractor_sdk.testing.md#jane_extractor_sdktestinglocalcaseresultexpected_status) | Поле | ні |
| [actual_status](jane_extractor_sdk.testing.md#jane_extractor_sdktestinglocalcaseresultactual_status) | Поле | ні |
| [differences](jane_extractor_sdk.testing.md#jane_extractor_sdktestinglocalcaseresultdifferences) | Поле | ні |
| [result](jane_extractor_sdk.testing.md#jane_extractor_sdktestinglocalcaseresultresult) | Поле | ні |
| [__init__](jane_extractor_sdk.testing.md#jane_extractor_sdktestinglocalcaseresult__init__) | Конструктор dataclass | ні |

## jane_extractor_sdk.testing.LocalCaseResult.__init__

**Конструктор dataclass.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/testing.py:133](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py#L133).

```python
def __init__(self, name: str, passed: bool, expected_status: str, actual_status: str, differences: list[dict[str, Any]] = <factory list>, result: dict[str, Any] = <factory dict>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `name` | `str` | `—` | positional-or-keyword |
| `passed` | `bool` | `—` | positional-or-keyword |
| `expected_status` | `str` | `—` | positional-or-keyword |
| `actual_status` | `str` | `—` | positional-or-keyword |
| `differences` | `list[dict[str, Any]]` | `factory: list` | positional-or-keyword |
| `result` | `dict[str, Any]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

## jane_extractor_sdk.testing.LocalCaseResult.name

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/testing.py:134](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py#L134).

```python
name: str
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.testing.LocalCaseResult.passed

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/testing.py:135](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py#L135).

```python
passed: bool
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.testing.LocalCaseResult.expected_status

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/testing.py:136](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py#L136).

```python
expected_status: str
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.testing.LocalCaseResult.actual_status

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/testing.py:137](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py#L137).

```python
actual_status: str
```

Доступ: читання — так; запис — так.

## jane_extractor_sdk.testing.LocalCaseResult.differences

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/testing.py:138](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py#L138).

```python
differences: list[dict[str, Any]] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_extractor_sdk.testing.LocalCaseResult.result

**Поле.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/testing.py:139](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py#L139).

```python
result: dict[str, Any] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_extractor_sdk.testing.run_package_tests

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/testing.py:142](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py#L142).

```python
def run_package_tests(package_dir: Path, names: Iterable[str] | None=None) -> list[LocalCaseResult]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `package_dir` | `Path` | `—` | positional-or-keyword |
| `names` | `Iterable[str] \| None` | `None` | positional-or-keyword |

Результат: `list[LocalCaseResult]`.

### Опис із вихідного коду

```text
Run the manifest ``tests`` in-process and compare with the expected results.
```

### Приклади з тестів

Контекст і передумови: [libs/extractor-sdk/tests/test_sdk.py:294](../../../../../../libs/extractor-sdk/tests/test_sdk.py#L294).

```python
results = run_package_tests(EXAMPLE)
```

## jane_extractor_sdk.testing.assert_package_tests_pass

**Функція.** Код: [libs/extractor-sdk/src/jane_extractor_sdk/testing.py:166](../../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py#L166).

```python
def assert_package_tests_pass(package_dir: Path, names: Iterable[str] | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `package_dir` | `Path` | `—` | positional-or-keyword |
| `names` | `Iterable[str] \| None` | `None` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `AssertionError`. Винятки викликаних залежностей описуються у ручному довіднику.
