# Модуль `jane_kit.content`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/content.py](../../../../../libs/jane-kit/src/jane_kit/content.py). Не редагуйте вручну.

Reading ``ContentRef`` values (ADR-0004) under an explicit operator policy.

A ``ContentRef`` arrives in a request, so every reference is untrusted input. :class:`ContentReader` reads:

* ``inline`` - ``data`` as ``utf-8`` text (default) or strict ``base64`` (RFC 4648);
* ``blob`` with ``download_url`` - only ``http``/``https`` to a host on the allowlist (``hostname`` = any port, ``hostname:port`` = that port; empty by default, so downloads are disabled). Hosts are compared in their ASCII (wire) form - an internationalized name is allowed by its punycode ``xn--...`` entry, the host actually connected to; a URL with non-ASCII characters is refused. Redirects are not followed, proxies and ``.netrc`` of the environment are ignored (``trust_env=False``), only an unencoded body is accepted (``Accept-Encoding: identity``), the size limit is enforced while streaming and the whole download is bounded by the timeout;
* ``blob`` ``file:///...`` - only strictly inside one of the configured roots (none by default, so ``file://`` is disabled). The path is resolved first (``..`` and symlinks), the *resolved* path is checked against the resolved roots and the resolved file is the one opened (``O_NOFOLLOW`` where the platform has it; on POSIX the opened file must be the checked one). Only regular files are read; ``file://host/...`` and UNC paths are refused;
* other blobs (``s3://`` without ``download_url``) - refused: the reader holds no storage credentials (ADR-0006).

The checks after reading: ``size_bytes`` of a blob must match (it is also checked against the limit before reading), ``sha256`` must match when given (contract: every consumer verifies it).

Errors are :class:`~jane_kit.errors.JaneError` (codes of ``contracts/docs/errors.md``); ``detail`` never carries a file path, a resolved path or content:

* invalid reference, refused by the policy, ``sha256``/``size_bytes`` mismatch - ``422 validation_failed``;
* larger than the limit - ``422 limit_exceeded`` (``details.path`` = name of the limit, ``details.limit`` = bytes);
* missing file, ``download_url`` answered 404/410 - ``404 not_found``;
* download failed (network, timeout, HTTP 5xx/408/429, I/O error) - ``502 upstream_unavailable``, retryable; redirect, other HTTP 4xx, encoded body - ``502 upstream_unavailable``, not retryable.

Settings of a service (env prefix ``JANE_<SERVICE>_``): ``BLOB_ROOTS`` (JSON list of directories) and ``DOWNLOAD_HOST_ALLOWLIST`` (JSON list of ``hostname[:port]``); validate the allowlist with :func:`parse_host_allowlist` so that a typo stops the service at start.

**Writing** (the producer part of ADR-0004, R18):

* :func:`inline_ref` - an ``inline`` reference (``utf-8`` text when asked and decodable, else ``base64``) with ``size_bytes`` and ``sha256``;
* :class:`FileTransitStore` - transit blobs of one producer on a local/shared directory (``<root>/<producer>/<YYYY>/<MM>/<DD>/<name><ext>``, written atomically, ``file://`` URIs, single node or a shared volume) and the producer's cleaner (:meth:`FileTransitStore.cleanup`: files older than ``limits.transfer.transit_ttl_seconds``);
* :class:`ContentWriter` - the delivery decision of a producer: ``auto`` (inline up to ``limits.transfer.inline_max_bytes``, else a transit blob with ``store: transit`` and ``expires_at``), ``inline`` (larger content is :class:`ContentTooLarge`, ``limit_exceeded``) or ``blob`` (always transit). Without a transit store a blob cannot be written: :class:`ContentTooLarge` with a hint to configure one (ADR-0004 §7).

Persistent objects (``store: persistent``) are written only by the storage handler with its adapters; S3/MinIO transit (bucket lifecycle) is not implemented by this module.

## Зміст

- [Клас `ContentReader`](#клас-contentreader)
- [Клас `ContentTooLarge`](#клас-contenttoolarge)
- [Клас `ContentWriter`](#клас-contentwriter)
- [Клас `FileTransitStore`](#клас-filetransitstore)
- [Функція `inline_ref`](#функція-inline_ref)
- [Функція `parse_host_allowlist`](#функція-parse_host_allowlist)

## Класи

### Клас `ContentReader`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.content` |
| Код | [content.py:112](../../../../../libs/jane-kit/src/jane_kit/content.py#L112) |

```python
class ContentReader: ...
```

Reads ``ContentRef`` values under the policy of one service (see the module docstring).

``timeout_ms`` bounds a whole download (and each network operation); ``connect_timeout_ms`` (default: the same) bounds establishing the connection. ``settings_prefix`` (``"JANE_LLM_"``) only names the settings in error messages. ``transport`` replaces the network in tests.

#### Конструктор `ContentReader.__init__`

```python
def __init__(
    self,
    *,
    timeout_ms: int,
    blob_roots: Iterable[Path | str] = (),
    download_host_allowlist: Iterable[str] = (),
    connect_timeout_ms: int | None = None,
    settings_prefix: str = '',
    transport: httpx.AsyncBaseTransport | None = None,
) -> None: ...
```

Винятки в коді методу: `ValueError`.

Код: [content.py:120](../../../../../libs/jane-kit/src/jane_kit/content.py#L120).

#### Метод `ContentReader.read`

```python
async def read(
    self,
    ref: Mapping[str, Any],
    *,
    max_bytes: int,
    limit: str = 'max_bytes',
) -> bytes: ...
```

Bytes of ``ref``; ``max_bytes`` comes from the service's limits, ``limit`` is its name for errors.

Винятки в коді методу: `ValidationFailed`.

Код: [content.py:140](../../../../../libs/jane-kit/src/jane_kit/content.py#L140).

### Клас `ContentTooLarge`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.content` |
| Успадкування | `LimitExceeded` |
| Код | [content.py:364](../../../../../libs/jane-kit/src/jane_kit/content.py#L364) |

```python
class ContentTooLarge(LimitExceeded): ...
```

Content cannot be delivered: larger than ``transfer.inline_max_bytes`` with inline delivery, or a blob is needed and no transit store is configured (``limit_exceeded``, ADR-0004 §7).

### Клас `ContentWriter`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_kit.content` |
| Код | [content.py:463](../../../../../libs/jane-kit/src/jane_kit/content.py#L463) |

```python
@dataclass
class ContentWriter: ...
```

Delivery of a producer's content as ContentRef (see the module docstring).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `mode` | `Literal['auto', 'inline', 'blob']` | — | читання й запис |  |
| `inline_max_bytes` | `int` | — | читання й запис |  |
| `transit_ttl_seconds` | `int` | — | читання й запис |  |
| `store` | `FileTransitStore \| None` | — | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `ContentWriter.ref`

```python
def ref(
    self,
    body: bytes,
    media_type: str,
    name: str,
    now: datetime | None = None,
    *,
    text: bool = False,
    charset: str | None = None,
    reuse: bool = False,
) -> dict[str, Any]: ...
```

ContentRef of ``body``; ``name`` names the transit blob if one is written (unique per content; ``reuse`` - the name is content-addressed, an existing blob is kept, see :meth:`FileTransitStore.put`).

Винятки в коді методу: `ContentTooLarge`.

Код: [content.py:471](../../../../../libs/jane-kit/src/jane_kit/content.py#L471).

#### Метод `ContentWriter.blob`

```python
def blob(
    self,
    body: bytes,
    media_type: str,
    name: str,
    now: datetime,
    *,
    charset: str | None = None,
    reuse: bool = False,
) -> dict[str, Any]: ...
```

A transit blob of ``body`` (the store must be configured).

Винятки в коді методу: `ContentTooLarge`.

Код: [content.py:503](../../../../../libs/jane-kit/src/jane_kit/content.py#L503).

### Клас `FileTransitStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.content` |
| Код | [content.py:394](../../../../../libs/jane-kit/src/jane_kit/content.py#L394) |

```python
class FileTransitStore: ...
```

Transit blobs of one producer under ``<root>/<producer>/`` (``file://`` URIs; one node or a shared volume).

The consumers read them only inside their configured ``BLOB_ROOTS`` (:class:`ContentReader`); the producer removes them after the TTL (:meth:`cleanup`, run by the producer's own periodic task).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `base` | `Path` | — | читання (властивість) |  |

#### Конструктор `FileTransitStore.__init__`

```python
def __init__(self, root: Path, producer: str) -> None: ...
```

Винятки в коді методу: `ValueError`.

Код: [content.py:401](../../../../../libs/jane-kit/src/jane_kit/content.py#L401).

#### Метод `FileTransitStore.put`

```python
def put(
    self,
    name: str,
    body: bytes,
    media_type: str,
    now: datetime,
    *,
    reuse: bool = False,
) -> Path: ...
```

Write ``body`` atomically as ``<base>/<YYYY>/<MM>/<DD>/<name><ext>``.

``reuse`` (only for a content-addressed ``name``): an existing file of the same size is kept and only its time is refreshed, so the cleaner keeps it for another TTL.

Винятки в коді методу: `AssertionError`, `ValueError`.

Код: [content.py:411](../../../../../libs/jane-kit/src/jane_kit/content.py#L411).

#### Метод `FileTransitStore.cleanup`

```python
def cleanup(self, ttl_seconds: float) -> int: ...
```

Remove this producer's transit files older than ``ttl_seconds`` (and empty day folders); returns the number of files removed. Files being written are newer than the TTL, so they are never touched.

Код: [content.py:442](../../../../../libs/jane-kit/src/jane_kit/content.py#L442).

## Функції

### Функція `inline_ref`

```python
def inline_ref(
    body: bytes,
    media_type: str,
    *,
    text: bool = False,
    charset: str | None = None,
) -> dict[str, Any]: ...
```

``inline`` ContentRef of ``body``: ``utf-8`` data when ``text`` and the bytes decode, else ``base64``.

Код: [content.py:373](../../../../../libs/jane-kit/src/jane_kit/content.py#L373).

### Функція `parse_host_allowlist`

```python
def parse_host_allowlist(entries: Iterable[str]) -> frozenset[tuple[str, int | None]]: ...
```

``hostname`` (any port) or ``hostname:port`` entries; anything else raises ``ValueError``.

Винятки в коді функції: `ValueError`.

Код: [content.py:101](../../../../../libs/jane-kit/src/jane_kit/content.py#L101).
