# Модуль `jane_handler_runtime.packages`

> Згенеровано `scripts/docs_reference.py` з [services/handler-runtime/src/jane_handler_runtime/packages.py](../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py). Не редагуйте вручну.

Getting a package: a local directory or zip (CLI), ``package_archive`` (ContentRef) or the registry.

Every archive is verified: ``handler.digest`` (``sha256:`` of the archive bytes) must match when given, ``ContentRef.sha256``/``size_bytes`` must match for blobs, and the registry ``ETag`` must match the bytes. Unpacking is bounded by ``PackageLimits``; verified packages are cached by digest.

## Зміст

- [Клас `ContentFetcher`](#клас-contentfetcher)
- [Клас `LoadedPackage`](#клас-loadedpackage)
- [Клас `PackageStore`](#клас-packagestore)
- [Функція `digest_mismatch`](#функція-digest_mismatch)

## Класи

### Клас `ContentFetcher`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_handler_runtime.packages` |
| Код | [packages.py:59](../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L59) |

```python
class ContentFetcher: ...
```

Reads ``ContentRef`` values with ``jane_kit.content.ContentReader``: inline, ``file://`` only strictly inside ``JANE_HANDLER_RUNTIME_BLOB_ROOTS`` (resolved path, no ``..``/symlink escape), ``download_url`` only to hosts of ``JANE_HANDLER_RUNTIME_DOWNLOAD_HOST_ALLOWLIST`` without redirects; ``size_bytes`` and ``sha256`` are verified.

``s3://`` without ``download_url`` is not readable: the runtime holds no storage credentials (ADR-0004/0006).

#### Конструктор `ContentFetcher.__init__`

```python
def __init__(
    self,
    settings: Settings,
    request_timeout_ms: int,
    transport: httpx.AsyncBaseTransport | None = None,
): ...
```

Код: [packages.py:67](../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L67).

#### Метод `ContentFetcher.read`

```python
async def read(
    self,
    ref: Mapping[str, Any],
    limit: int,
    *,
    limit_name: str = 'packages.max_input_bytes',
) -> bytes: ...
```

Код: [packages.py:78](../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L78).

### Клас `LoadedPackage`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_handler_runtime.packages` |
| Код | [packages.py:44](../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L44) |

```python
@dataclass(frozen=True)
class LoadedPackage: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `root` | `Path` | — | читання |  |
| `manifest` | `dict[str, Any]` | — | читання |  |
| `digest` | `str` | — | читання |  |
| `source` | `str` | — | читання |  |
| `ref` | `dict[str, str]` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `PackageStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_handler_runtime.packages` |
| Код | [packages.py:84](../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L84) |

```python
class PackageStore: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `unpack_limits` | `UnpackLimits` | — | читання (властивість) |  |

#### Конструктор `PackageStore.__init__`

```python
def __init__(
    self,
    settings: Settings,
    limits: PackageLimits,
    fetcher: ContentFetcher,
    *,
    registry_transport: httpx.AsyncBaseTransport | None = None,
    request_timeout_s: float = 30.0,
) -> None: ...
```

Код: [packages.py:85](../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L85).

#### Метод `PackageStore.close`

```python
def close(self) -> None: ...
```

Код: [packages.py:115](../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L115).

#### Метод `PackageStore.load_local`

```python
def load_local(self, path: Path) -> LoadedPackage: ...
```

A package directory or zip on disk (CLI, trusted location). Digest = canonical archive.

Винятки в коді методу: `ValidationFailed`.

Код: [packages.py:152](../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L152).

#### Метод `PackageStore.load`

```python
async def load(
    self,
    handler: Mapping[str, Any],
    archive_ref: Mapping[str, Any] | None,
) -> LoadedPackage: ...
```

Винятки в коді методу: `ValidationFailed`.

Код: [packages.py:160](../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L160).

## Функції

### Функція `digest_mismatch`

```python
def digest_mismatch(detail: str) -> JaneError: ...
```

Код: [packages.py:39](../../../../../services/handler-runtime/src/jane_handler_runtime/packages.py#L39).
