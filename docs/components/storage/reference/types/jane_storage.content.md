# Модуль `jane_storage.content`

> Згенеровано `scripts/docs_reference.py` з [services/storage/src/jane_storage/content.py](../../../../../services/storage/src/jane_storage/content.py). Не редагуйте вручну.

Reading ``ContentRef`` (inline / blob) with sha256 and size checks (ADR-0004).

* ``inline`` — ``utf-8`` or ``base64`` data;
* ``blob`` ``file:///…`` — local file below the configured transit directory;
* ``blob`` ``s3://bucket/key`` — through the configured transit connection (kind ``s3``/``minio``);
* otherwise ``download_url`` (pre-signed HTTP(S) link on the configured allowlist).

## Класи

### Клас `ContentError`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_storage.content` |
| Успадкування | `Exception` |
| Код | [content.py:30](../../../../../services/storage/src/jane_storage/content.py#L30) |

```python
class ContentError(Exception): ...
```

Content cannot be read or is inconsistent. ``retryable`` — worth retrying later.

#### Конструктор `ContentError.__init__`

```python
def __init__(self, message: str, *, retryable: bool, kind: str = 'execution_error') -> None: ...
```

Код: [content.py:33](../../../../../services/storage/src/jane_storage/content.py#L33).

### Клас `ContentReader`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_storage.content` |
| Код | [content.py:42](../../../../../services/storage/src/jane_storage/content.py#L42) |

```python
class ContentReader: ...
```

#### Конструктор `ContentReader.__init__`

```python
def __init__(
    self,
    *,
    max_bytes: int,
    request_timeout_ms: int,
    transit: TransitResolver | None = None,
    files_dir: Path | None = None,
    download_host_allowlist: list[str] | tuple[str, ...] = (),
    extra_files_dirs: Sequence[Path] = (),
) -> None: ...
```

Код: [content.py:43](../../../../../services/storage/src/jane_storage/content.py#L43).

#### Метод `ContentReader.read`

```python
async def read(self, ref: Mapping[str, Any]) -> bytes: ...
```

Винятки в коді методу: `ContentError`.

Код: [content.py:61](../../../../../services/storage/src/jane_storage/content.py#L61).
