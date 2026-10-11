# jane_handler_runtime.packages

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_handler_runtime.packages.digest_mismatch](#jane_handler_runtimepackagesdigest_mismatch)
- [jane_handler_runtime.packages.LoadedPackage](#jane_handler_runtimepackagesloadedpackage)
- [jane_handler_runtime.packages.LoadedPackage.__init__](#jane_handler_runtimepackagesloadedpackage__init__)
- [jane_handler_runtime.packages.LoadedPackage.root](#jane_handler_runtimepackagesloadedpackageroot)
- [jane_handler_runtime.packages.LoadedPackage.manifest](#jane_handler_runtimepackagesloadedpackagemanifest)
- [jane_handler_runtime.packages.LoadedPackage.digest](#jane_handler_runtimepackagesloadedpackagedigest)
- [jane_handler_runtime.packages.LoadedPackage.source](#jane_handler_runtimepackagesloadedpackagesource)
- [jane_handler_runtime.packages.LoadedPackage.ref](#jane_handler_runtimepackagesloadedpackageref)
- [jane_handler_runtime.packages.ContentFetcher](#jane_handler_runtimepackagescontentfetcher)
- [jane_handler_runtime.packages.ContentFetcher.__init__](#jane_handler_runtimepackagescontentfetcher__init__)
- [jane_handler_runtime.packages.ContentFetcher.reader](#jane_handler_runtimepackagescontentfetcherreader)
- [jane_handler_runtime.packages.ContentFetcher.read](#jane_handler_runtimepackagescontentfetcherread)
- [jane_handler_runtime.packages.PackageStore](#jane_handler_runtimepackagespackagestore)
- [jane_handler_runtime.packages.PackageStore.__init__](#jane_handler_runtimepackagespackagestore__init__)
- [jane_handler_runtime.packages.PackageStore.settings](#jane_handler_runtimepackagespackagestoresettings)
- [jane_handler_runtime.packages.PackageStore.limits](#jane_handler_runtimepackagespackagestorelimits)
- [jane_handler_runtime.packages.PackageStore.fetcher](#jane_handler_runtimepackagespackagestorefetcher)
- [jane_handler_runtime.packages.PackageStore.cache_dir](#jane_handler_runtimepackagespackagestorecache_dir)
- [jane_handler_runtime.packages.PackageStore.unpack_limits](#jane_handler_runtimepackagespackagestoreunpack_limits)
- [jane_handler_runtime.packages.PackageStore.close](#jane_handler_runtimepackagespackagestoreclose)
- [jane_handler_runtime.packages.PackageStore.load_local](#jane_handler_runtimepackagespackagestoreload_local)
- [jane_handler_runtime.packages.PackageStore.load](#jane_handler_runtimepackagespackagestoreload)

## jane_handler_runtime.packages.digest_mismatch

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:39](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L39).

```python
def digest_mismatch(detail: str) -> JaneError:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `detail` | `str` | `—` | positional-or-keyword |

Результат: `JaneError`.

## jane_handler_runtime.packages.LoadedPackage

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:44](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L44).

```python
class LoadedPackage:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [root](jane_handler_runtime.packages.md#jane_handler_runtimepackagesloadedpackageroot) | Поле | ні |
| [manifest](jane_handler_runtime.packages.md#jane_handler_runtimepackagesloadedpackagemanifest) | Поле | ні |
| [digest](jane_handler_runtime.packages.md#jane_handler_runtimepackagesloadedpackagedigest) | Поле | ні |
| [source](jane_handler_runtime.packages.md#jane_handler_runtimepackagesloadedpackagesource) | Поле | ні |
| [ref](jane_handler_runtime.packages.md#jane_handler_runtimepackagesloadedpackageref) | Властивість | ні |
| [__init__](jane_handler_runtime.packages.md#jane_handler_runtimepackagesloadedpackage__init__) | Конструктор dataclass | ні |

## jane_handler_runtime.packages.LoadedPackage.__init__

**Конструктор dataclass.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:44](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L44).

```python
def __init__(self, root: Path, manifest: dict[str, Any], digest: str, source: str) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `root` | `Path` | `—` | positional-or-keyword |
| `manifest` | `dict[str, Any]` | `—` | positional-or-keyword |
| `digest` | `str` | `—` | positional-or-keyword |
| `source` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_handler_runtime.packages.LoadedPackage.root

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:45](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L45).

```python
root: Path
```

Доступ: читання — так; запис — ні.

## jane_handler_runtime.packages.LoadedPackage.manifest

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:46](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L46).

```python
manifest: dict[str, Any]
```

Доступ: читання — так; запис — ні.

## jane_handler_runtime.packages.LoadedPackage.digest

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:47](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L47).

```python
digest: str
```

Доступ: читання — так; запис — ні.

## jane_handler_runtime.packages.LoadedPackage.source

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:48](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L48).

```python
source: str
```

Доступ: читання — так; запис — ні.

## jane_handler_runtime.packages.LoadedPackage.ref

**Властивість.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:51](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L51).

```python
def ref(self) -> dict[str, str]:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, str]`.

Доступ: читання — так; запис — ні.

## jane_handler_runtime.packages.ContentFetcher

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:59](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L59).

```python
class ContentFetcher:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_handler_runtime.packages.md#jane_handler_runtimepackagescontentfetcher__init__) | Конструктор | ні |
| [reader](jane_handler_runtime.packages.md#jane_handler_runtimepackagescontentfetcherreader) | Поле екземпляра | ні |
| [read](jane_handler_runtime.packages.md#jane_handler_runtimepackagescontentfetcherread) | Метод | ні |

### Опис із вихідного коду

```text
Reads ``ContentRef`` values with ``jane_kit.content.ContentReader``: inline, ``file://`` only strictly inside
``JANE_HANDLER_RUNTIME_BLOB_ROOTS`` (resolved path, no ``..``/symlink escape), ``download_url`` only to hosts of
``JANE_HANDLER_RUNTIME_DOWNLOAD_HOST_ALLOWLIST`` without redirects; ``size_bytes`` and ``sha256`` are verified.

``s3://`` without ``download_url`` is not readable: the runtime holds no storage credentials (ADR-0004/0006).
```

## jane_handler_runtime.packages.ContentFetcher.__init__

**Конструктор.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:67](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L67).

```python
def __init__(self, settings: Settings, request_timeout_ms: int, transport: httpx.AsyncBaseTransport | None=None):
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `settings` | `Settings` | `—` | positional-or-keyword |
| `request_timeout_ms` | `int` | `—` | positional-or-keyword |
| `transport` | `httpx.AsyncBaseTransport \| None` | `None` | positional-or-keyword |

## jane_handler_runtime.packages.ContentFetcher.reader

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:70](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L70).

```python
self.reader = ContentReader(timeout_ms=request_timeout_ms, blob_roots=settings.blob_roots, download_host_allowlist=settings.download_host_allowlist, settings_prefix='JANE_HANDLER_RUNTIME_', transport=transport)
```

## jane_handler_runtime.packages.ContentFetcher.read

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:78](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L78).

```python
async def read(self, ref: Mapping[str, Any], limit: int, *, limit_name: str='packages.max_input_bytes') -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |
| `limit_name` | `str` | `'packages.max_input_bytes'` | keyword-only |

Результат: `bytes`.

## jane_handler_runtime.packages.PackageStore

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:84](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L84).

```python
class PackageStore:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_handler_runtime.packages.md#jane_handler_runtimepackagespackagestore__init__) | Конструктор | ні |
| [settings](jane_handler_runtime.packages.md#jane_handler_runtimepackagespackagestoresettings) | Поле екземпляра | ні |
| [limits](jane_handler_runtime.packages.md#jane_handler_runtimepackagespackagestorelimits) | Поле екземпляра | ні |
| [fetcher](jane_handler_runtime.packages.md#jane_handler_runtimepackagespackagestorefetcher) | Поле екземпляра | ні |
| [cache_dir](jane_handler_runtime.packages.md#jane_handler_runtimepackagespackagestorecache_dir) | Поле екземпляра | ні |
| [unpack_limits](jane_handler_runtime.packages.md#jane_handler_runtimepackagespackagestoreunpack_limits) | Властивість | ні |
| [close](jane_handler_runtime.packages.md#jane_handler_runtimepackagespackagestoreclose) | Метод | ні |
| [load_local](jane_handler_runtime.packages.md#jane_handler_runtimepackagespackagestoreload_local) | Метод | ні |
| [load](jane_handler_runtime.packages.md#jane_handler_runtimepackagespackagestoreload) | Метод | ні |

## jane_handler_runtime.packages.PackageStore.__init__

**Конструктор.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:85](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L85).

```python
def __init__(self, settings: Settings, limits: PackageLimits, fetcher: ContentFetcher, *, registry_transport: httpx.AsyncBaseTransport | None=None, request_timeout_s: float=30.0) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `settings` | `Settings` | `—` | positional-or-keyword |
| `limits` | `PackageLimits` | `—` | positional-or-keyword |
| `fetcher` | `ContentFetcher` | `—` | positional-or-keyword |
| `registry_transport` | `httpx.AsyncBaseTransport \| None` | `None` | keyword-only |
| `request_timeout_s` | `float` | `30.0` | keyword-only |

Результат: `None`.

## jane_handler_runtime.packages.PackageStore.settings

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:94](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L94).

```python
self.settings = settings
```

## jane_handler_runtime.packages.PackageStore.limits

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:95](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L95).

```python
self.limits = limits
```

## jane_handler_runtime.packages.PackageStore.fetcher

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:96](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L96).

```python
self.fetcher = fetcher
```

## jane_handler_runtime.packages.PackageStore.cache_dir

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:100](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L100).

```python
self.cache_dir = settings.package_cache_dir
```

## jane_handler_runtime.packages.PackageStore.unpack_limits

**Властивість.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:110](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L110).

```python
def unpack_limits(self) -> UnpackLimits:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `UnpackLimits`.

Доступ: читання — так; запис — ні.

## jane_handler_runtime.packages.PackageStore.close

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:115](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L115).

```python
def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_handler_runtime.packages.PackageStore.load_local

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:152](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L152).

```python
def load_local(self, path: Path) -> LoadedPackage:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `path` | `Path` | `—` | positional-or-keyword |

Результат: `LoadedPackage`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
A package directory or zip on disk (CLI, trusted location). Digest = canonical archive.
```

## jane_handler_runtime.packages.PackageStore.load

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/packages.py:160](../../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L160).

```python
async def load(self, handler: Mapping[str, Any], archive_ref: Mapping[str, Any] | None) -> LoadedPackage:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `handler` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `archive_ref` | `Mapping[str, Any] \| None` | `—` | positional-or-keyword |

Результат: `LoadedPackage`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.
