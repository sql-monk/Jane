# Модуль `jane_llm.packages`

> Згенеровано `scripts/docs_reference.py` з [services/llm/src/jane_llm/packages.py](../../../../../services/llm/src/jane_llm/packages.py). Не редагуйте вручну.

LLM packages (``kind: llm``): loading from an archive, the registry or a local directory.

A package is a manifest (``jane-package.json``) plus prompts and schemas; no code. The executor verifies ``handler.digest`` when given (``sha256:`` of the archive bytes; for a local directory — of the canonical archive built by :func:`build_archive`).

## Зміст

- [Клас `DigestMismatch`](#клас-digestmismatch)
- [Клас `LoadedPackage`](#клас-loadedpackage)
- [Клас `PackageLoader`](#клас-packageloader)
- [Функція `build_archive`](#функція-build_archive)
- [Функція `read_dir`](#функція-read_dir)
- [Функція `digest_of`](#функція-digest_of)
- [Функція `unpack`](#функція-unpack)
- [Функція `check_llm_manifest`](#функція-check_llm_manifest)
- [Функція `publish_request`](#функція-publish_request)
- [Функція `publish`](#функція-publish)
- [Функція `main`](#функція-main)

## Класи

### Клас `DigestMismatch`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_llm.packages` |
| Успадкування | `JaneError` |
| Код | [packages.py:31](../../../../../services/llm/src/jane_llm/packages.py#L31) |

```python
class DigestMismatch(JaneError): ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `code` | `'digest_mismatch'` |  |

### Клас `LoadedPackage`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_llm.packages` |
| Код | [packages.py:36](../../../../../services/llm/src/jane_llm/packages.py#L36) |

```python
@dataclass(frozen=True)
class LoadedPackage: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `manifest` | `dict[str, Any]` | — | читання |  |
| `files` | `dict[str, bytes]` | — | читання |  |
| `digest` | `str` | — | читання |  |
| `package_id` | `str` | — | читання (властивість) |  |
| `version` | `str` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `LoadedPackage.text`

```python
def text(self, path: str) -> str: ...
```

Винятки в коді методу: `ValidationFailed`.

Код: [packages.py:49](../../../../../services/llm/src/jane_llm/packages.py#L49).

#### Метод `LoadedPackage.json`

```python
def json(self, path: str) -> Any: ...
```

Винятки в коді методу: `ValidationFailed`.

Код: [packages.py:54](../../../../../services/llm/src/jane_llm/packages.py#L54).

### Клас `PackageLoader`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_llm.packages` |
| Код | [packages.py:134](../../../../../services/llm/src/jane_llm/packages.py#L134) |

```python
class PackageLoader: ...
```

Finds LLM packages: request archive -> local directory -> registry. Caches by digest.

The caches only save fetching and unpacking; a load gives the same answer on a cold and a warm loader:

* ``package_archive`` of the request is read and verified every time; ``_archives`` (digest of the archive bytes -> package) only skips unpacking the same bytes again;
* a reference without an archive reuses ``_found`` (packages found in the local directory or the registry) only for exactly its ``package_id@version`` and digest. A digest of another package or version, or a package seen only in some request's archive, goes the cold way and gets its ``digest_mismatch`` / ``not_found``.

``package_archive`` is read by ``content`` (``jane_kit.content.ContentReader`` under ``JANE_LLM_BLOB_ROOTS`` / ``JANE_LLM_DOWNLOAD_HOST_ALLOWLIST``); without it only inline archives can be read.

#### Конструктор `PackageLoader.__init__`

```python
def __init__(
    self,
    packages_dir: Path | None,
    registry_url: str | None,
    registry_limits: ClientLimits,
    registry_token: str | None = None,
    *,
    limits: GatewayLimits,
    transport: httpx.AsyncBaseTransport | None = None,
    content: ContentReader | None = None,
) -> None: ...
```

Код: [packages.py:150](../../../../../services/llm/src/jane_llm/packages.py#L150).

#### Метод `PackageLoader.load`

```python
async def load(self, ref: dict[str, Any], archive_ref: dict[str, Any] | None) -> LoadedPackage: ...
```

Винятки в коді методу: `NotFound`, `DigestMismatch`.

Код: [packages.py:221](../../../../../services/llm/src/jane_llm/packages.py#L221).

## Функції

### Функція `build_archive`

```python
def build_archive(files: dict[str, bytes]) -> bytes: ...
```

Canonical zip: sorted paths, fixed timestamps and permissions, deflate.

Код: [packages.py:66](../../../../../services/llm/src/jane_llm/packages.py#L66).

### Функція `read_dir`

```python
def read_dir(root: Path) -> dict[str, bytes]: ...
```

Код: [packages.py:78](../../../../../services/llm/src/jane_llm/packages.py#L78).

### Функція `digest_of`

```python
def digest_of(data: bytes) -> str: ...
```

Код: [packages.py:86](../../../../../services/llm/src/jane_llm/packages.py#L86).

### Функція `unpack`

```python
def unpack(archive: bytes, max_total_bytes: int, max_files: int) -> dict[str, bytes]: ...
```

Files of a package zip; rejects archives above ``max_files`` or ``max_total_bytes`` uncompressed.

Винятки в коді функції: `ValidationFailed`.

Код: [packages.py:90](../../../../../services/llm/src/jane_llm/packages.py#L90).

### Функція `check_llm_manifest`

```python
def check_llm_manifest(manifest: dict[str, Any], ref: dict[str, Any] | None = None) -> None: ...
```

Винятки в коді функції: `ValidationFailed`.

Код: [packages.py:116](../../../../../services/llm/src/jane_llm/packages.py#L116).

### Функція `publish_request`

```python
def publish_request(root: Path) -> dict[str, Any]: ...
```

``registry.v1`` ``PublishRequest`` body for a package directory (manifest + files).

Код: [packages.py:263](../../../../../services/llm/src/jane_llm/packages.py#L263).

### Функція `publish`

```python
async def publish(
    root: Path,
    registry_url: str,
    limits: ClientLimits | None = None,
    token: str | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> dict[str, Any]: ...
```

Create the package (if needed) and publish its version in the registry (``registry.v1``).

Код: [packages.py:276](../../../../../services/llm/src/jane_llm/packages.py#L276).

### Функція `main`

```python
def main(argv: list[str] | None = None) -> int: ...
```

``python -m jane_llm.packages {digest|publish} <dir> [--registry URL]``.

The registry token is read from the environment variable ``JANE_LLM_REGISTRY_TOKEN``.

Код: [packages.py:303](../../../../../services/llm/src/jane_llm/packages.py#L303).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `MANIFEST` | — | `'jane-package.json'` |  |
