# jane_llm.packages

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_llm.packages.MANIFEST](#jane_llmpackagesmanifest)
- [jane_llm.packages.DigestMismatch](#jane_llmpackagesdigestmismatch)
- [jane_llm.packages.DigestMismatch.code](#jane_llmpackagesdigestmismatchcode)
- [jane_llm.packages.LoadedPackage](#jane_llmpackagesloadedpackage)
- [jane_llm.packages.LoadedPackage.__init__](#jane_llmpackagesloadedpackage__init__)
- [jane_llm.packages.LoadedPackage.manifest](#jane_llmpackagesloadedpackagemanifest)
- [jane_llm.packages.LoadedPackage.files](#jane_llmpackagesloadedpackagefiles)
- [jane_llm.packages.LoadedPackage.digest](#jane_llmpackagesloadedpackagedigest)
- [jane_llm.packages.LoadedPackage.package_id](#jane_llmpackagesloadedpackagepackage_id)
- [jane_llm.packages.LoadedPackage.version](#jane_llmpackagesloadedpackageversion)
- [jane_llm.packages.LoadedPackage.text](#jane_llmpackagesloadedpackagetext)
- [jane_llm.packages.LoadedPackage.json](#jane_llmpackagesloadedpackagejson)
- [jane_llm.packages.build_archive](#jane_llmpackagesbuild_archive)
- [jane_llm.packages.read_dir](#jane_llmpackagesread_dir)
- [jane_llm.packages.digest_of](#jane_llmpackagesdigest_of)
- [jane_llm.packages.unpack](#jane_llmpackagesunpack)
- [jane_llm.packages.check_llm_manifest](#jane_llmpackagescheck_llm_manifest)
- [jane_llm.packages.PackageLoader](#jane_llmpackagespackageloader)
- [jane_llm.packages.PackageLoader.__init__](#jane_llmpackagespackageloader__init__)
- [jane_llm.packages.PackageLoader.transport](#jane_llmpackagespackageloadertransport)
- [jane_llm.packages.PackageLoader.limits](#jane_llmpackagespackageloaderlimits)
- [jane_llm.packages.PackageLoader.content](#jane_llmpackagespackageloadercontent)
- [jane_llm.packages.PackageLoader.packages_dir](#jane_llmpackagespackageloaderpackages_dir)
- [jane_llm.packages.PackageLoader.registry_url](#jane_llmpackagespackageloaderregistry_url)
- [jane_llm.packages.PackageLoader.registry_limits](#jane_llmpackagespackageloaderregistry_limits)
- [jane_llm.packages.PackageLoader.registry_token](#jane_llmpackagespackageloaderregistry_token)
- [jane_llm.packages.PackageLoader.load](#jane_llmpackagespackageloaderload)
- [jane_llm.packages.publish_request](#jane_llmpackagespublish_request)
- [jane_llm.packages.publish](#jane_llmpackagespublish)
- [jane_llm.packages.main](#jane_llmpackagesmain)

## jane_llm.packages.MANIFEST

**Константа.** Код: [services/llm/src/jane_llm/packages.py:27](../../../../../../services/llm/src/jane_llm/packages.py#L27).

```python
MANIFEST = 'jane-package.json'
```

## jane_llm.packages.DigestMismatch

**Клас.** Код: [services/llm/src/jane_llm/packages.py:31](../../../../../../services/llm/src/jane_llm/packages.py#L31).

```python
class DigestMismatch(JaneError):
```

Базові типи / інтерфейси: `JaneError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_llm.packages.md#jane_llmpackagesdigestmismatchcode) | Поле | ні |
| [__init__](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](../../../../jane-kit/reference/types/generated/jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

## jane_llm.packages.DigestMismatch.code

**Поле.** Код: [services/llm/src/jane_llm/packages.py:32](../../../../../../services/llm/src/jane_llm/packages.py#L32).

```python
code = 'digest_mismatch'
```

Доступ: читання — так; запис — так.

## jane_llm.packages.LoadedPackage

**Клас.** Код: [services/llm/src/jane_llm/packages.py:36](../../../../../../services/llm/src/jane_llm/packages.py#L36).

```python
class LoadedPackage:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [manifest](jane_llm.packages.md#jane_llmpackagesloadedpackagemanifest) | Поле | ні |
| [files](jane_llm.packages.md#jane_llmpackagesloadedpackagefiles) | Поле | ні |
| [digest](jane_llm.packages.md#jane_llmpackagesloadedpackagedigest) | Поле | ні |
| [package_id](jane_llm.packages.md#jane_llmpackagesloadedpackagepackage_id) | Властивість | ні |
| [version](jane_llm.packages.md#jane_llmpackagesloadedpackageversion) | Властивість | ні |
| [text](jane_llm.packages.md#jane_llmpackagesloadedpackagetext) | Метод | ні |
| [json](jane_llm.packages.md#jane_llmpackagesloadedpackagejson) | Метод | ні |
| [__init__](jane_llm.packages.md#jane_llmpackagesloadedpackage__init__) | Конструктор dataclass | ні |

## jane_llm.packages.LoadedPackage.__init__

**Конструктор dataclass.** Код: [services/llm/src/jane_llm/packages.py:36](../../../../../../services/llm/src/jane_llm/packages.py#L36).

```python
def __init__(self, manifest: dict[str, Any], files: dict[str, bytes], digest: str) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `manifest` | `dict[str, Any]` | `—` | positional-or-keyword |
| `files` | `dict[str, bytes]` | `—` | positional-or-keyword |
| `digest` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_llm.packages.LoadedPackage.manifest

**Поле.** Код: [services/llm/src/jane_llm/packages.py:37](../../../../../../services/llm/src/jane_llm/packages.py#L37).

```python
manifest: dict[str, Any]
```

Доступ: читання — так; запис — ні.

## jane_llm.packages.LoadedPackage.files

**Поле.** Код: [services/llm/src/jane_llm/packages.py:38](../../../../../../services/llm/src/jane_llm/packages.py#L38).

```python
files: dict[str, bytes]
```

Доступ: читання — так; запис — ні.

## jane_llm.packages.LoadedPackage.digest

**Поле.** Код: [services/llm/src/jane_llm/packages.py:39](../../../../../../services/llm/src/jane_llm/packages.py#L39).

```python
digest: str
```

Доступ: читання — так; запис — ні.

## jane_llm.packages.LoadedPackage.package_id

**Властивість.** Код: [services/llm/src/jane_llm/packages.py:42](../../../../../../services/llm/src/jane_llm/packages.py#L42).

```python
def package_id(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## jane_llm.packages.LoadedPackage.version

**Властивість.** Код: [services/llm/src/jane_llm/packages.py:46](../../../../../../services/llm/src/jane_llm/packages.py#L46).

```python
def version(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## jane_llm.packages.LoadedPackage.text

**Метод.** Код: [services/llm/src/jane_llm/packages.py:49](../../../../../../services/llm/src/jane_llm/packages.py#L49).

```python
def text(self, path: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |

Результат: `str`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_llm.packages.LoadedPackage.json

**Метод.** Код: [services/llm/src/jane_llm/packages.py:54](../../../../../../services/llm/src/jane_llm/packages.py#L54).

```python
def json(self, path: str) -> Any:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |

Результат: `Any`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_llm.packages.build_archive

**Функція.** Код: [services/llm/src/jane_llm/packages.py:66](../../../../../../services/llm/src/jane_llm/packages.py#L66).

```python
def build_archive(files: dict[str, bytes]) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `files` | `dict[str, bytes]` | `—` | positional-or-keyword |

Результат: `bytes`.

### Опис із вихідного коду

```text
Canonical zip: sorted paths, fixed timestamps and permissions, deflate.
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_content_policy.py:160](../../../../../../services/llm/tests/test_content_policy.py#L160).

```python
archive = build_archive(read_dir(PACKAGE_DIR))
```

Контекст і передумови: [services/llm/tests/test_contract.py:162](../../../../../../services/llm/tests/test_contract.py#L162).

```python
archive = build_archive(read_dir(PACKAGE_DIR))
```

## jane_llm.packages.read_dir

**Функція.** Код: [services/llm/src/jane_llm/packages.py:78](../../../../../../services/llm/src/jane_llm/packages.py#L78).

```python
def read_dir(root: Path) -> dict[str, bytes]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `root` | `Path` | `—` | positional-or-keyword |

Результат: `dict[str, bytes]`.

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_content_policy.py:160](../../../../../../services/llm/tests/test_content_policy.py#L160).

```python
archive = build_archive(read_dir(PACKAGE_DIR))
```

Контекст і передумови: [services/llm/tests/test_contract.py:162](../../../../../../services/llm/tests/test_contract.py#L162).

```python
archive = build_archive(read_dir(PACKAGE_DIR))
```

## jane_llm.packages.digest_of

**Функція.** Код: [services/llm/src/jane_llm/packages.py:86](../../../../../../services/llm/src/jane_llm/packages.py#L86).

```python
def digest_of(data: bytes) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `data` | `bytes` | `—` | positional-or-keyword |

Результат: `str`.

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_service.py:499](../../../../../../services/llm/tests/test_service.py#L499).

```python
d101 = digest_of(v101)
```

Контекст і передумови: [services/llm/tests/test_service.py:177](../../../../../../services/llm/tests/test_service.py#L177).

```python
assert res["handler"]["digest"] == digest_of(build_archive(read_dir(PACKAGE_DIR)))
```

## jane_llm.packages.unpack

**Функція.** Код: [services/llm/src/jane_llm/packages.py:90](../../../../../../services/llm/src/jane_llm/packages.py#L90).

```python
def unpack(archive: bytes, max_total_bytes: int, max_files: int) -> dict[str, bytes]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `archive` | `bytes` | `—` | positional-or-keyword |
| `max_total_bytes` | `int` | `—` | positional-or-keyword |
| `max_files` | `int` | `—` | positional-or-keyword |

Результат: `dict[str, bytes]`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Files of a package zip; rejects archives above ``max_files`` or ``max_total_bytes`` uncompressed.
```

## jane_llm.packages.check_llm_manifest

**Функція.** Код: [services/llm/src/jane_llm/packages.py:116](../../../../../../services/llm/src/jane_llm/packages.py#L116).

```python
def check_llm_manifest(manifest: dict[str, Any], ref: dict[str, Any] | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `manifest` | `dict[str, Any]` | `—` | positional-or-keyword |
| `ref` | `dict[str, Any] \| None` | `None` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_llm.packages.PackageLoader

**Клас.** Код: [services/llm/src/jane_llm/packages.py:134](../../../../../../services/llm/src/jane_llm/packages.py#L134).

```python
class PackageLoader:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_llm.packages.md#jane_llmpackagespackageloader__init__) | Конструктор | ні |
| [transport](jane_llm.packages.md#jane_llmpackagespackageloadertransport) | Поле екземпляра | ні |
| [limits](jane_llm.packages.md#jane_llmpackagespackageloaderlimits) | Поле екземпляра | ні |
| [content](jane_llm.packages.md#jane_llmpackagespackageloadercontent) | Поле екземпляра | ні |
| [packages_dir](jane_llm.packages.md#jane_llmpackagespackageloaderpackages_dir) | Поле екземпляра | ні |
| [registry_url](jane_llm.packages.md#jane_llmpackagespackageloaderregistry_url) | Поле екземпляра | ні |
| [registry_limits](jane_llm.packages.md#jane_llmpackagespackageloaderregistry_limits) | Поле екземпляра | ні |
| [registry_token](jane_llm.packages.md#jane_llmpackagespackageloaderregistry_token) | Поле екземпляра | ні |
| [load](jane_llm.packages.md#jane_llmpackagespackageloaderload) | Метод | ні |

### Опис із вихідного коду

```text
Finds LLM packages: request archive -> local directory -> registry. Caches by digest.

The caches only save fetching and unpacking; a load gives the same answer on a cold and a warm loader:

* ``package_archive`` of the request is read and verified every time; ``_archives`` (digest of the archive
  bytes -> package) only skips unpacking the same bytes again;
* a reference without an archive reuses ``_found`` (packages found in the local directory or the registry)
  only for exactly its ``package_id@version`` and digest. A digest of another package or version, or a
  package seen only in some request's archive, goes the cold way and gets its ``digest_mismatch`` /
  ``not_found``.

``package_archive`` is read by ``content`` (``jane_kit.content.ContentReader`` under ``JANE_LLM_BLOB_ROOTS`` /
``JANE_LLM_DOWNLOAD_HOST_ALLOWLIST``); without it only inline archives can be read.
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_service.py:381](../../../../../../services/llm/tests/test_service.py#L381).

```python
loader = PackageLoader(
        None,
        "http://registry",
        ClientLimits(),
        limits=GatewayLimits(),
        transport=httpx.ASGITransport(app=registry),
    )
```

Контекст і передумови: [services/llm/tests/test_service.py:452](../../../../../../services/llm/tests/test_service.py#L452).

```python
loader = PackageLoader(
        None,
        "http://registry",
        ClientLimits(),
        limits=GatewayLimits(),
        transport=httpx.ASGITransport(app=registry),
    )
```

## jane_llm.packages.PackageLoader.__init__

**Конструктор.** Код: [services/llm/src/jane_llm/packages.py:150](../../../../../../services/llm/src/jane_llm/packages.py#L150).

```python
def __init__(self, packages_dir: Path | None, registry_url: str | None, registry_limits: ClientLimits, registry_token: str | None=None, *, limits: GatewayLimits, transport: httpx.AsyncBaseTransport | None=None, content: ContentReader | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `packages_dir` | `Path \| None` | `—` | positional-or-keyword |
| `registry_url` | `str \| None` | `—` | positional-or-keyword |
| `registry_limits` | `ClientLimits` | `—` | positional-or-keyword |
| `registry_token` | `str \| None` | `None` | positional-or-keyword |
| `limits` | `GatewayLimits` | `—` | keyword-only |
| `transport` | `httpx.AsyncBaseTransport \| None` | `None` | keyword-only |
| `content` | `ContentReader \| None` | `None` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_service.py:381](../../../../../../services/llm/tests/test_service.py#L381).

```python
loader = PackageLoader(
        None,
        "http://registry",
        ClientLimits(),
        limits=GatewayLimits(),
        transport=httpx.ASGITransport(app=registry),
    )
```

Контекст і передумови: [services/llm/tests/test_service.py:452](../../../../../../services/llm/tests/test_service.py#L452).

```python
loader = PackageLoader(
        None,
        "http://registry",
        ClientLimits(),
        limits=GatewayLimits(),
        transport=httpx.ASGITransport(app=registry),
    )
```

## jane_llm.packages.PackageLoader.transport

**Поле екземпляра.** Код: [services/llm/src/jane_llm/packages.py:161](../../../../../../services/llm/src/jane_llm/packages.py#L161).

```python
self.transport = transport
```

## jane_llm.packages.PackageLoader.limits

**Поле екземпляра.** Код: [services/llm/src/jane_llm/packages.py:162](../../../../../../services/llm/src/jane_llm/packages.py#L162).

```python
self.limits = limits
```

## jane_llm.packages.PackageLoader.content

**Поле екземпляра.** Код: [services/llm/src/jane_llm/packages.py:163](../../../../../../services/llm/src/jane_llm/packages.py#L163).

```python
self.content = content or ContentReader(timeout_ms=limits.content_fetch_timeout_ms)
```

## jane_llm.packages.PackageLoader.packages_dir

**Поле екземпляра.** Код: [services/llm/src/jane_llm/packages.py:164](../../../../../../services/llm/src/jane_llm/packages.py#L164).

```python
self.packages_dir = packages_dir
```

## jane_llm.packages.PackageLoader.registry_url

**Поле екземпляра.** Код: [services/llm/src/jane_llm/packages.py:165](../../../../../../services/llm/src/jane_llm/packages.py#L165).

```python
self.registry_url = registry_url
```

## jane_llm.packages.PackageLoader.registry_limits

**Поле екземпляра.** Код: [services/llm/src/jane_llm/packages.py:166](../../../../../../services/llm/src/jane_llm/packages.py#L166).

```python
self.registry_limits = registry_limits
```

## jane_llm.packages.PackageLoader.registry_token

**Поле екземпляра.** Код: [services/llm/src/jane_llm/packages.py:167](../../../../../../services/llm/src/jane_llm/packages.py#L167).

```python
self.registry_token = registry_token
```

## jane_llm.packages.PackageLoader.load

**Метод.** Код: [services/llm/src/jane_llm/packages.py:221](../../../../../../services/llm/src/jane_llm/packages.py#L221).

```python
async def load(self, ref: dict[str, Any], archive_ref: dict[str, Any] | None) -> LoadedPackage:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `dict[str, Any]` | `—` | positional-or-keyword |
| `archive_ref` | `dict[str, Any] \| None` | `—` | positional-or-keyword |

Результат: `LoadedPackage`.

Явні `raise` у тілі: `DigestMismatch`, `NotFound`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_service.py:389](../../../../../../services/llm/tests/test_service.py#L389).

```python
pkg = asyncio.run(loader.load(ref, None))
```

Контекст і передумови: [services/llm/tests/test_service.py:469](../../../../../../services/llm/tests/test_service.py#L469).

```python
pkg = asyncio.run(loader.load({"package_id": CACHE_PKG, "version": "1.0.1", "digest": d101}, None))
```

## jane_llm.packages.publish_request

**Функція.** Код: [services/llm/src/jane_llm/packages.py:263](../../../../../../services/llm/src/jane_llm/packages.py#L263).

```python
def publish_request(root: Path) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `root` | `Path` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
``registry.v1`` ``PublishRequest`` body for a package directory (manifest + files).
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_service.py:363](../../../../../../services/llm/tests/test_service.py#L363).

```python
body = publish_request(PACKAGE_DIR)
```

## jane_llm.packages.publish

**Функція.** Код: [services/llm/src/jane_llm/packages.py:276](../../../../../../services/llm/src/jane_llm/packages.py#L276).

```python
async def publish(root: Path, registry_url: str, limits: ClientLimits | None=None, token: str | None=None, transport: httpx.AsyncBaseTransport | None=None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `root` | `Path` | `—` | positional-or-keyword |
| `registry_url` | `str` | `—` | positional-or-keyword |
| `limits` | `ClientLimits \| None` | `None` | positional-or-keyword |
| `token` | `str \| None` | `None` | positional-or-keyword |
| `transport` | `httpx.AsyncBaseTransport \| None` | `None` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `повторний raise`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Create the package (if needed) and publish its version in the registry (``registry.v1``).
```

### Приклади з тестів

Контекст і передумови: [services/llm/tests/test_service.py:365](../../../../../../services/llm/tests/test_service.py#L365).

```python
result = asyncio.run(publish(PACKAGE_DIR, "http://registry", transport=httpx.ASGITransport(app=app)))
```

## jane_llm.packages.main

**Функція.** Код: [services/llm/src/jane_llm/packages.py:303](../../../../../../services/llm/src/jane_llm/packages.py#L303).

```python
def main(argv: list[str] | None=None) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `argv` | `list[str] \| None` | `None` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
``python -m jane_llm.packages {digest|publish} <dir> [--registry URL]``.

The registry token is read from the environment variable ``JANE_LLM_REGISTRY_TOKEN``.
```
