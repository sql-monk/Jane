# jane_registry.export

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_registry.export.EXPORT_FORMAT](#jane_registryexportexport_format)
- [jane_registry.export.INDEX_NAME](#jane_registryexportindex_name)
- [jane_registry.export.ExportError](#jane_registryexportexporterror)
- [jane_registry.export.export_package](#jane_registryexportexport_package)
- [jane_registry.export.VerifyReport](#jane_registryexportverifyreport)
- [jane_registry.export.VerifyReport.__init__](#jane_registryexportverifyreport__init__)
- [jane_registry.export.VerifyReport.path](#jane_registryexportverifyreportpath)
- [jane_registry.export.VerifyReport.digest](#jane_registryexportverifyreportdigest)
- [jane_registry.export.VerifyReport.package](#jane_registryexportverifyreportpackage)
- [jane_registry.export.VerifyReport.errors](#jane_registryexportverifyreporterrors)
- [jane_registry.export.VerifyReport.checks](#jane_registryexportverifyreportchecks)
- [jane_registry.export.VerifyReport.ok](#jane_registryexportverifyreportok)
- [jane_registry.export.VerifyReport.wire](#jane_registryexportverifyreportwire)
- [jane_registry.export.verify_archive](#jane_registryexportverify_archive)

## jane_registry.export.EXPORT_FORMAT

**Константа.** Код: [services/registry/src/jane_registry/export.py:35](../../../../../../services/registry/src/jane_registry/export.py#L35).

```python
EXPORT_FORMAT = 'jane-export@1'
```

## jane_registry.export.INDEX_NAME

**Константа.** Код: [services/registry/src/jane_registry/export.py:36](../../../../../../services/registry/src/jane_registry/export.py#L36).

```python
INDEX_NAME = 'jane-export.json'
```

## jane_registry.export.ExportError

**Клас.** Код: [services/registry/src/jane_registry/export.py:39](../../../../../../services/registry/src/jane_registry/export.py#L39).

```python
class ExportError(RuntimeError):
```

Базові типи / інтерфейси: `RuntimeError`.

## jane_registry.export.export_package

**Функція.** Код: [services/registry/src/jane_registry/export.py:49](../../../../../../services/registry/src/jane_registry/export.py#L49).

```python
def export_package(client: httpx.Client, package_id: str, version: str, out: Path, *, with_dependencies: bool=True, max_packages: int) -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `httpx.Client` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |
| `out` | `Path` | `—` | positional-or-keyword |
| `with_dependencies` | `bool` | `True` | keyword-only |
| `max_packages` | `int` | `—` | keyword-only |

Результат: `list[dict[str, Any]]`.

Явні `raise` у тілі: `ExportError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Download and verify; returns the index entries (also written to ``out/jane-export.json``).
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_runtime_compat.py:110](../../../../../../services/registry/tests/test_runtime_compat.py#L110).

```python
export_package(c, pid, version, out, max_packages=10)
```

## jane_registry.export.VerifyReport

**Клас.** Код: [services/registry/src/jane_registry/export.py:112](../../../../../../services/registry/src/jane_registry/export.py#L112).

```python
class VerifyReport:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [path](jane_registry.export.md#jane_registryexportverifyreportpath) | Поле | ні |
| [digest](jane_registry.export.md#jane_registryexportverifyreportdigest) | Поле | ні |
| [package](jane_registry.export.md#jane_registryexportverifyreportpackage) | Поле | ні |
| [errors](jane_registry.export.md#jane_registryexportverifyreporterrors) | Поле | ні |
| [checks](jane_registry.export.md#jane_registryexportverifyreportchecks) | Поле | ні |
| [ok](jane_registry.export.md#jane_registryexportverifyreportok) | Властивість | ні |
| [wire](jane_registry.export.md#jane_registryexportverifyreportwire) | Метод | ні |
| [__init__](jane_registry.export.md#jane_registryexportverifyreport__init__) | Конструктор dataclass | ні |

## jane_registry.export.VerifyReport.__init__

**Конструктор dataclass.** Код: [services/registry/src/jane_registry/export.py:112](../../../../../../services/registry/src/jane_registry/export.py#L112).

```python
def __init__(self, path: str, digest: str | None = None, package: dict[str, Any] | None = None, errors: list[str] = <factory list>, checks: dict[str, bool] = <factory dict>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `path` | `str` | `—` | positional-or-keyword |
| `digest` | `str \| None` | `None` | positional-or-keyword |
| `package` | `dict[str, Any] \| None` | `None` | positional-or-keyword |
| `errors` | `list[str]` | `factory: list` | positional-or-keyword |
| `checks` | `dict[str, bool]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

## jane_registry.export.VerifyReport.path

**Поле.** Код: [services/registry/src/jane_registry/export.py:113](../../../../../../services/registry/src/jane_registry/export.py#L113).

```python
path: str
```

Доступ: читання — так; запис — так.

## jane_registry.export.VerifyReport.digest

**Поле.** Код: [services/registry/src/jane_registry/export.py:114](../../../../../../services/registry/src/jane_registry/export.py#L114).

```python
digest: str | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.export.VerifyReport.package

**Поле.** Код: [services/registry/src/jane_registry/export.py:115](../../../../../../services/registry/src/jane_registry/export.py#L115).

```python
package: dict[str, Any] | None = None
```

Доступ: читання — так; запис — так.

## jane_registry.export.VerifyReport.errors

**Поле.** Код: [services/registry/src/jane_registry/export.py:116](../../../../../../services/registry/src/jane_registry/export.py#L116).

```python
errors: list[str] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_registry.export.VerifyReport.checks

**Поле.** Код: [services/registry/src/jane_registry/export.py:117](../../../../../../services/registry/src/jane_registry/export.py#L117).

```python
checks: dict[str, bool] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_registry.export.VerifyReport.ok

**Властивість.** Код: [services/registry/src/jane_registry/export.py:120](../../../../../../services/registry/src/jane_registry/export.py#L120).

```python
def ok(self) -> bool:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

Доступ: читання — так; запис — ні.

## jane_registry.export.VerifyReport.wire

**Метод.** Код: [services/registry/src/jane_registry/export.py:123](../../../../../../services/registry/src/jane_registry/export.py#L123).

```python
def wire(self) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_registry.export.verify_archive

**Функція.** Код: [services/registry/src/jane_registry/export.py:145](../../../../../../services/registry/src/jane_registry/export.py#L145).

```python
def verify_archive(archive: Path, *, expected_digest: str | None=None, contracts: Path | None=None, package_limits: PackageLimits | None=None, secret_limits: SecretScanLimits | None=None) -> VerifyReport:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `archive` | `Path` | `—` | positional-or-keyword |
| `expected_digest` | `str \| None` | `None` | keyword-only |
| `contracts` | `Path \| None` | `None` | keyword-only |
| `package_limits` | `PackageLimits \| None` | `None` | keyword-only |
| `secret_limits` | `SecretScanLimits \| None` | `None` | keyword-only |

Результат: `VerifyReport`.
