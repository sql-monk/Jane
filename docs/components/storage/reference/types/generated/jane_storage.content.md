# jane_storage.content

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage.content.ContentError](#jane_storagecontentcontenterror)
- [jane_storage.content.ContentError.__init__](#jane_storagecontentcontenterror__init__)
- [jane_storage.content.ContentError.retryable](#jane_storagecontentcontenterrorretryable)
- [jane_storage.content.ContentError.kind](#jane_storagecontentcontenterrorkind)
- [jane_storage.content.ContentReader](#jane_storagecontentcontentreader)
- [jane_storage.content.ContentReader.__init__](#jane_storagecontentcontentreader__init__)
- [jane_storage.content.ContentReader.max_bytes](#jane_storagecontentcontentreadermax_bytes)
- [jane_storage.content.ContentReader.request_timeout_ms](#jane_storagecontentcontentreaderrequest_timeout_ms)
- [jane_storage.content.ContentReader.read](#jane_storagecontentcontentreaderread)

## jane_storage.content.ContentError

**Клас.** Код: [services/storage/src/jane_storage/content.py:30](../../../../../../services/storage/src/jane_storage/content.py#L30).

```python
class ContentError(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_storage.content.md#jane_storagecontentcontenterror__init__) | Конструктор | ні |
| [retryable](jane_storage.content.md#jane_storagecontentcontenterrorretryable) | Поле екземпляра | ні |
| [kind](jane_storage.content.md#jane_storagecontentcontenterrorkind) | Поле екземпляра | ні |

### Опис із вихідного коду

```text
Content cannot be read or is inconsistent. ``retryable`` — worth retrying later.
```

## jane_storage.content.ContentError.__init__

**Конструктор.** Код: [services/storage/src/jane_storage/content.py:33](../../../../../../services/storage/src/jane_storage/content.py#L33).

```python
def __init__(self, message: str, *, retryable: bool, kind: str='execution_error') -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |
| `retryable` | `bool` | `—` | keyword-only |
| `kind` | `str` | `'execution_error'` | keyword-only |

Результат: `None`.

## jane_storage.content.ContentError.retryable

**Поле екземпляра.** Код: [services/storage/src/jane_storage/content.py:35](../../../../../../services/storage/src/jane_storage/content.py#L35).

```python
self.retryable = retryable
```

## jane_storage.content.ContentError.kind

**Поле екземпляра.** Код: [services/storage/src/jane_storage/content.py:36](../../../../../../services/storage/src/jane_storage/content.py#L36).

```python
self.kind = kind
```

## jane_storage.content.ContentReader

**Клас.** Код: [services/storage/src/jane_storage/content.py:42](../../../../../../services/storage/src/jane_storage/content.py#L42).

```python
class ContentReader:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_storage.content.md#jane_storagecontentcontentreader__init__) | Конструктор | ні |
| [max_bytes](jane_storage.content.md#jane_storagecontentcontentreadermax_bytes) | Поле екземпляра | ні |
| [request_timeout_ms](jane_storage.content.md#jane_storagecontentcontentreaderrequest_timeout_ms) | Поле екземпляра | ні |
| [read](jane_storage.content.md#jane_storagecontentcontentreaderread) | Метод | ні |

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_content_policy.py:19](../../../../../../services/storage/tests/test_content_policy.py#L19).

```python
return ContentReader(
        max_bytes=1024,
        request_timeout_ms=1000,
        files_dir=files_dir,
        download_host_allowlist=hosts,
    )
```

## jane_storage.content.ContentReader.__init__

**Конструктор.** Код: [services/storage/src/jane_storage/content.py:43](../../../../../../services/storage/src/jane_storage/content.py#L43).

```python
def __init__(self, *, max_bytes: int, request_timeout_ms: int, transit: TransitResolver | None=None, files_dir: Path | None=None, download_host_allowlist: list[str] | tuple[str, ...]=(), extra_files_dirs: Sequence[Path]=()) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `max_bytes` | `int` | `—` | keyword-only |
| `request_timeout_ms` | `int` | `—` | keyword-only |
| `transit` | `TransitResolver \| None` | `None` | keyword-only |
| `files_dir` | `Path \| None` | `None` | keyword-only |
| `download_host_allowlist` | `list[str] \| tuple[str, ...]` | `()` | keyword-only |
| `extra_files_dirs` | `Sequence[Path]` | `()` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_content_policy.py:19](../../../../../../services/storage/tests/test_content_policy.py#L19).

```python
return ContentReader(
        max_bytes=1024,
        request_timeout_ms=1000,
        files_dir=files_dir,
        download_host_allowlist=hosts,
    )
```

## jane_storage.content.ContentReader.max_bytes

**Поле екземпляра.** Код: [services/storage/src/jane_storage/content.py:53](../../../../../../services/storage/src/jane_storage/content.py#L53).

```python
self.max_bytes = max_bytes
```

## jane_storage.content.ContentReader.request_timeout_ms

**Поле екземпляра.** Код: [services/storage/src/jane_storage/content.py:54](../../../../../../services/storage/src/jane_storage/content.py#L54).

```python
self.request_timeout_ms = request_timeout_ms
```

## jane_storage.content.ContentReader.read

**Метод.** Код: [services/storage/src/jane_storage/content.py:61](../../../../../../services/storage/src/jane_storage/content.py#L61).

```python
async def read(self, ref: Mapping[str, Any]) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `bytes`.

Явні `raise` у тілі: `ContentError`. Винятки викликаних залежностей описуються у ручному довіднику.
