# Модуль `jane_extractor_sdk.testing`

> Згенеровано `scripts/docs_reference.py` з [libs/extractor-sdk/src/jane_extractor_sdk/testing.py](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py). Не редагуйте вручну.

Test utilities for extractor authors: run a package in-process, without the sandbox and without services.

This is a fast feedback loop for *trusted* code (your own package in pytest). It does not validate entity schemas and does not enforce limits or isolation; the authoritative check is the handler-runtime CLI::

    uv run --package jane-handler-runtime jane-handler-runtime test path/to/package

Example (pytest)::

    from pathlib import Path
    from jane_extractor_sdk.testing import assert_package_tests_pass, run_local

    PKG = Path(__file__).parents[1]

    def test_manifest_tests():
        assert_package_tests_pass(PKG)

    def test_one_page():
        result = run_local(PKG, file=PKG / "tests/product/page.html", media_type="text/html")
        assert result["status"] == "success"

## Зміст

- [Клас `LocalCaseResult`](#клас-localcaseresult)
- [Функція `apply_param_defaults`](#функція-apply_param_defaults)
- [Функція `assert_package_tests_pass`](#функція-assert_package_tests_pass)
- [Функція `run_local`](#функція-run_local)
- [Функція `run_package_tests`](#функція-run_package_tests)

## Класи

### Клас `LocalCaseResult`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_extractor_sdk.testing` |
| Код | [testing.py:133](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py#L133) |

```python
@dataclass
class LocalCaseResult: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `name` | `str` | — | читання й запис |  |
| `passed` | `bool` | — | читання й запис |  |
| `expected_status` | `str` | — | читання й запис |  |
| `actual_status` | `str` | — | читання й запис |  |
| `differences` | `list[dict[str, Any]]` | `field(default_factory=list)` | читання й запис |  |
| `result` | `dict[str, Any]` | `field(default_factory=dict)` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `apply_param_defaults`

```python
def apply_param_defaults(
    schema: Mapping[str, Any] | None,
    params: Mapping[str, Any] | None,
) -> dict[str, Any]: ...
```

Top-level ``default`` values of an object ``params_schema`` for parameters that were not given.

Код: [testing.py:46](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py#L46).

### Функція `assert_package_tests_pass`

```python
def assert_package_tests_pass(package_dir: Path, names: Iterable[str] | None = None) -> None: ...
```

Винятки в коді функції: `AssertionError`.

Код: [testing.py:166](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py#L166).

### Функція `run_local`

```python
def run_local(
    package_dir: Path,
    handler_input: Mapping[str, Any] | None = None,
    *,
    file: Path | None = None,
    media_type: str | None = None,
    url: str | None = None,
    params: Mapping[str, Any] | None = None,
    test_mode: bool = True,
) -> dict[str, Any]: ...
```

Run the entry callable in this process on one input; return a simplified result::

{"status": "success|empty|unrecognized|failed", "output": {"entities": [...]}, "unrecognized": {...}, "diagnostics": [...], "error": {...}}

Винятки в коді функції: `ValueError`.

Код: [testing.py:70](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py#L70).

### Функція `run_package_tests`

```python
def run_package_tests(
    package_dir: Path,
    names: Iterable[str] | None = None,
) -> list[LocalCaseResult]: ...
```

Run the manifest ``tests`` in-process and compare with the expected results.

Код: [testing.py:142](../../../../../libs/extractor-sdk/src/jane_extractor_sdk/testing.py#L142).
