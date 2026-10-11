# Модуль `jane_registry.export`

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry/export.py](../../../../../services/registry/src/jane_registry/export.py). Не редагуйте вручну.

Export of package versions for autonomous use and their offline verification.

``export`` downloads the archive of ``package_id@version`` (and, recursively, of every ``dependencies.packages`` entry), checks that the bytes match the ``ETag`` and the version's ``digest``, and writes::

    &lt;out>/&lt;package_id>-&lt;version>.zip     exact canonical archive from the registry
    &lt;out>/jane-export.json               index: package, version, digest, file, size, status

``verify`` works without the registry: the archive is canonical, its digest matches the index (or ``--digest``), ``jane-package.json`` is valid (contract schema when ``contracts/`` is available), every file the manifest refers to is present, and no secrets are found. An exported archive is what handler-runtime runs locally (``jane-handler-runtime test <zip>``) or receives as ``HandlerInvocation.package_archive``.

## Зміст

- [Клас `ExportError`](#клас-exporterror)
- [Клас `VerifyReport`](#клас-verifyreport)
- [Функція `export_package`](#функція-export_package)
- [Функція `verify_archive`](#функція-verify_archive)

## Класи

### Клас `ExportError`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_registry.export` |
| Успадкування | `RuntimeError` |
| Код | [export.py:39](../../../../../services/registry/src/jane_registry/export.py#L39) |

```python
class ExportError(RuntimeError): ...
```

### Клас `VerifyReport`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_registry.export` |
| Код | [export.py:112](../../../../../services/registry/src/jane_registry/export.py#L112) |

```python
@dataclass
class VerifyReport: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `path` | `str` | — | читання й запис |  |
| `digest` | `str \| None` | `None` | читання й запис |  |
| `package` | `dict[str, Any] \| None` | `None` | читання й запис |  |
| `errors` | `list[str]` | `field(default_factory=list)` | читання й запис |  |
| `checks` | `dict[str, bool]` | `field(default_factory=dict)` | читання й запис |  |
| `ok` | `bool` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `VerifyReport.wire`

```python
def wire(self) -> dict[str, Any]: ...
```

Код: [export.py:123](../../../../../services/registry/src/jane_registry/export.py#L123).

## Функції

### Функція `export_package`

```python
def export_package(
    client: httpx.Client,
    package_id: str,
    version: str,
    out: Path,
    *,
    with_dependencies: bool = True,
    max_packages: int,
) -> list[dict[str, Any]]: ...
```

Download and verify; returns the index entries (also written to ``out/jane-export.json``).

Винятки в коді функції: `ExportError`.

Код: [export.py:49](../../../../../services/registry/src/jane_registry/export.py#L49).

### Функція `verify_archive`

```python
def verify_archive(
    archive: Path,
    *,
    expected_digest: str | None = None,
    contracts: Path | None = None,
    package_limits: PackageLimits | None = None,
    secret_limits: SecretScanLimits | None = None,
) -> VerifyReport: ...
```

Код: [export.py:145](../../../../../services/registry/src/jane_registry/export.py#L145).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `EXPORT_FORMAT` | — | `'jane-export@1'` |  |
| `INDEX_NAME` | — | `'jane-export.json'` |  |
