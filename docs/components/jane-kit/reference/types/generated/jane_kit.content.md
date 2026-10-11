# jane_kit.content

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.content.parse_host_allowlist](#jane_kitcontentparse_host_allowlist)
- [jane_kit.content.ContentReader](#jane_kitcontentcontentreader)
- [jane_kit.content.ContentReader.__init__](#jane_kitcontentcontentreader__init__)
- [jane_kit.content.ContentReader.blob_roots](#jane_kitcontentcontentreaderblob_roots)
- [jane_kit.content.ContentReader.download_hosts](#jane_kitcontentcontentreaderdownload_hosts)
- [jane_kit.content.ContentReader.timeout_s](#jane_kitcontentcontentreadertimeout_s)
- [jane_kit.content.ContentReader.connect_timeout_s](#jane_kitcontentcontentreaderconnect_timeout_s)
- [jane_kit.content.ContentReader.roots_setting](#jane_kitcontentcontentreaderroots_setting)
- [jane_kit.content.ContentReader.allowlist_setting](#jane_kitcontentcontentreaderallowlist_setting)
- [jane_kit.content.ContentReader.read](#jane_kitcontentcontentreaderread)
- [jane_kit.content.ContentTooLarge](#jane_kitcontentcontenttoolarge)
- [jane_kit.content.inline_ref](#jane_kitcontentinline_ref)
- [jane_kit.content.FileTransitStore](#jane_kitcontentfiletransitstore)
- [jane_kit.content.FileTransitStore.__init__](#jane_kitcontentfiletransitstore__init__)
- [jane_kit.content.FileTransitStore.root](#jane_kitcontentfiletransitstoreroot)
- [jane_kit.content.FileTransitStore.producer](#jane_kitcontentfiletransitstoreproducer)
- [jane_kit.content.FileTransitStore.base](#jane_kitcontentfiletransitstorebase)
- [jane_kit.content.FileTransitStore.put](#jane_kitcontentfiletransitstoreput)
- [jane_kit.content.FileTransitStore.cleanup](#jane_kitcontentfiletransitstorecleanup)
- [jane_kit.content.ContentWriter](#jane_kitcontentcontentwriter)
- [jane_kit.content.ContentWriter.__init__](#jane_kitcontentcontentwriter__init__)
- [jane_kit.content.ContentWriter.mode](#jane_kitcontentcontentwritermode)
- [jane_kit.content.ContentWriter.inline_max_bytes](#jane_kitcontentcontentwriterinline_max_bytes)
- [jane_kit.content.ContentWriter.transit_ttl_seconds](#jane_kitcontentcontentwritertransit_ttl_seconds)
- [jane_kit.content.ContentWriter.store](#jane_kitcontentcontentwriterstore)
- [jane_kit.content.ContentWriter.ref](#jane_kitcontentcontentwriterref)
- [jane_kit.content.ContentWriter.blob](#jane_kitcontentcontentwriterblob)

## jane_kit.content.parse_host_allowlist

**Функція.** Код: [libs/jane-kit/src/jane_kit/content.py:101](../../../../../../libs/jane-kit/src/jane_kit/content.py#L101).

```python
def parse_host_allowlist(entries: Iterable[str]) -> frozenset[tuple[str, int | None]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `entries` | `Iterable[str]` | `—` | positional-or-keyword |

Результат: `frozenset[tuple[str, int | None]]`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
``hostname`` (any port) or ``hostname:port`` entries; anything else raises ``ValueError``.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_content.py:380](../../../../../../libs/jane-kit/tests/test_content.py#L380).

```python
assert parse_host_allowlist(["Gate", "gate:8080"]) == {("gate", None), ("gate", 8080)}
```

Контекст і передумови: [libs/jane-kit/tests/test_content.py:383](../../../../../../libs/jane-kit/tests/test_content.py#L383).

```python
parse_host_allowlist([bad])
```

## jane_kit.content.ContentReader

**Клас.** Код: [libs/jane-kit/src/jane_kit/content.py:112](../../../../../../libs/jane-kit/src/jane_kit/content.py#L112).

```python
class ContentReader:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.content.md#jane_kitcontentcontentreader__init__) | Конструктор | ні |
| [blob_roots](jane_kit.content.md#jane_kitcontentcontentreaderblob_roots) | Поле екземпляра | ні |
| [download_hosts](jane_kit.content.md#jane_kitcontentcontentreaderdownload_hosts) | Поле екземпляра | ні |
| [timeout_s](jane_kit.content.md#jane_kitcontentcontentreadertimeout_s) | Поле екземпляра | ні |
| [connect_timeout_s](jane_kit.content.md#jane_kitcontentcontentreaderconnect_timeout_s) | Поле екземпляра | ні |
| [roots_setting](jane_kit.content.md#jane_kitcontentcontentreaderroots_setting) | Поле екземпляра | ні |
| [allowlist_setting](jane_kit.content.md#jane_kitcontentcontentreaderallowlist_setting) | Поле екземпляра | ні |
| [read](jane_kit.content.md#jane_kitcontentcontentreaderread) | Метод | ні |

### Опис із вихідного коду

```text
Reads ``ContentRef`` values under the policy of one service (see the module docstring).

``timeout_ms`` bounds a whole download (and each network operation); ``connect_timeout_ms`` (default: the
same) bounds establishing the connection. ``settings_prefix`` (``"JANE_LLM_"``) only names the settings in
error messages. ``transport`` replaces the network in tests.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_content.py:46](../../../../../../libs/jane-kit/tests/test_content.py#L46).

```python
return ContentReader(settings_prefix="JANE_TEST_", **kwargs)
```

Контекст і передумови: [libs/jane-kit/tests/test_content.py:385](../../../../../../libs/jane-kit/tests/test_content.py#L385).

```python
ContentReader(timeout_ms=0)
```

## jane_kit.content.ContentReader.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/content.py:120](../../../../../../libs/jane-kit/src/jane_kit/content.py#L120).

```python
def __init__(self, *, timeout_ms: int, blob_roots: Iterable[Path | str]=(), download_host_allowlist: Iterable[str]=(), connect_timeout_ms: int | None=None, settings_prefix: str='', transport: httpx.AsyncBaseTransport | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `timeout_ms` | `int` | `—` | keyword-only |
| `blob_roots` | `Iterable[Path \| str]` | `()` | keyword-only |
| `download_host_allowlist` | `Iterable[str]` | `()` | keyword-only |
| `connect_timeout_ms` | `int \| None` | `None` | keyword-only |
| `settings_prefix` | `str` | `''` | keyword-only |
| `transport` | `httpx.AsyncBaseTransport \| None` | `None` | keyword-only |

Результат: `None`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_content.py:46](../../../../../../libs/jane-kit/tests/test_content.py#L46).

```python
return ContentReader(settings_prefix="JANE_TEST_", **kwargs)
```

Контекст і передумови: [libs/jane-kit/tests/test_content.py:385](../../../../../../libs/jane-kit/tests/test_content.py#L385).

```python
ContentReader(timeout_ms=0)
```

## jane_kit.content.ContentReader.blob_roots

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/content.py:132](../../../../../../libs/jane-kit/src/jane_kit/content.py#L132).

```python
self.blob_roots = tuple((Path(root).resolve() for root in blob_roots))
```

## jane_kit.content.ContentReader.download_hosts

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/content.py:133](../../../../../../libs/jane-kit/src/jane_kit/content.py#L133).

```python
self.download_hosts = parse_host_allowlist(download_host_allowlist)
```

## jane_kit.content.ContentReader.timeout_s

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/content.py:134](../../../../../../libs/jane-kit/src/jane_kit/content.py#L134).

```python
self.timeout_s = timeout_ms / 1000
```

## jane_kit.content.ContentReader.connect_timeout_s

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/content.py:135](../../../../../../libs/jane-kit/src/jane_kit/content.py#L135).

```python
self.connect_timeout_s = min(connect_timeout_ms or timeout_ms, timeout_ms) / 1000
```

## jane_kit.content.ContentReader.roots_setting

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/content.py:136](../../../../../../libs/jane-kit/src/jane_kit/content.py#L136).

```python
self.roots_setting = f'{settings_prefix}BLOB_ROOTS'
```

## jane_kit.content.ContentReader.allowlist_setting

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/content.py:137](../../../../../../libs/jane-kit/src/jane_kit/content.py#L137).

```python
self.allowlist_setting = f'{settings_prefix}DOWNLOAD_HOST_ALLOWLIST'
```

## jane_kit.content.ContentReader.read

**Метод.** Код: [libs/jane-kit/src/jane_kit/content.py:140](../../../../../../libs/jane-kit/src/jane_kit/content.py#L140).

```python
async def read(self, ref: Mapping[str, Any], *, max_bytes: int, limit: str='max_bytes') -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ref` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `max_bytes` | `int` | `—` | keyword-only |
| `limit` | `str` | `'max_bytes'` | keyword-only |

Результат: `bytes`.

Явні `raise` у тілі: `ValidationFailed`, `_too_large`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Bytes of ``ref``; ``max_bytes`` comes from the service's limits, ``limit`` is its name for errors.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_content.py:51](../../../../../../libs/jane-kit/tests/test_content.py#L51).

```python
await r.read(ref, max_bytes=max_bytes, limit="test.max_bytes")
```

Контекст і передумови: [libs/jane-kit/tests/test_content.py:63](../../../../../../libs/jane-kit/tests/test_content.py#L63).

```python
assert await r.read(text, max_bytes=100) == "Ціна 1299".encode()
```

## jane_kit.content.ContentTooLarge

**Клас.** Код: [libs/jane-kit/src/jane_kit/content.py:364](../../../../../../libs/jane-kit/src/jane_kit/content.py#L364).

```python
class ContentTooLarge(LimitExceeded):
```

Базові типи / інтерфейси: `LimitExceeded`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [code](jane_kit.errors.md#jane_kiterrorslimitexceededcode) | Поле | так |
| [__init__](jane_kit.errors.md#jane_kiterrorsjaneerror__init__) | Конструктор | так |
| [error_code](jane_kit.errors.md#jane_kiterrorsjaneerrorerror_code) | Поле екземпляра | так |
| [status](jane_kit.errors.md#jane_kiterrorsjaneerrorstatus) | Поле екземпляра | так |
| [retryable](jane_kit.errors.md#jane_kiterrorsjaneerrorretryable) | Поле екземпляра | так |
| [title](jane_kit.errors.md#jane_kiterrorsjaneerrortitle) | Поле екземпляра | так |
| [detail](jane_kit.errors.md#jane_kiterrorsjaneerrordetail) | Поле екземпляра | так |
| [errors](jane_kit.errors.md#jane_kiterrorsjaneerrorerrors) | Поле екземпляра | так |
| [details](jane_kit.errors.md#jane_kiterrorsjaneerrordetails) | Поле екземпляра | так |
| [retry_after_seconds](jane_kit.errors.md#jane_kiterrorsjaneerrorretry_after_seconds) | Поле екземпляра | так |
| [headers](jane_kit.errors.md#jane_kiterrorsjaneerrorheaders) | Поле екземпляра | так |
| [to_problem](jane_kit.errors.md#jane_kiterrorsjaneerrorto_problem) | Метод | так |

### Опис із вихідного коду

```text
Content cannot be delivered: larger than ``transfer.inline_max_bytes`` with inline delivery, or a blob is
needed and no transit store is configured (``limit_exceeded``, ADR-0004 §7).
```

## jane_kit.content.inline_ref

**Функція.** Код: [libs/jane-kit/src/jane_kit/content.py:373](../../../../../../libs/jane-kit/src/jane_kit/content.py#L373).

```python
def inline_ref(body: bytes, media_type: str, *, text: bool=False, charset: str | None=None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `body` | `bytes` | `—` | positional-or-keyword |
| `media_type` | `str` | `—` | positional-or-keyword |
| `text` | `bool` | `False` | keyword-only |
| `charset` | `str \| None` | `None` | keyword-only |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
``inline`` ContentRef of ``body``: ``utf-8`` data when ``text`` and the bytes decode, else ``base64``.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_content_writer.py:21](../../../../../../libs/jane-kit/tests/test_content_writer.py#L21).

```python
text = inline_ref("ціна 1299".encode(), "text/plain", text=True, charset="utf-8")
```

Контекст і передумови: [libs/jane-kit/tests/test_content_writer.py:28](../../../../../../libs/jane-kit/tests/test_content_writer.py#L28).

```python
binary = inline_ref(raw, "text/plain", text=True)
```

## jane_kit.content.FileTransitStore

**Клас.** Код: [libs/jane-kit/src/jane_kit/content.py:394](../../../../../../libs/jane-kit/src/jane_kit/content.py#L394).

```python
class FileTransitStore:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_kit.content.md#jane_kitcontentfiletransitstore__init__) | Конструктор | ні |
| [root](jane_kit.content.md#jane_kitcontentfiletransitstoreroot) | Поле екземпляра | ні |
| [producer](jane_kit.content.md#jane_kitcontentfiletransitstoreproducer) | Поле екземпляра | ні |
| [base](jane_kit.content.md#jane_kitcontentfiletransitstorebase) | Властивість | ні |
| [put](jane_kit.content.md#jane_kitcontentfiletransitstoreput) | Метод | ні |
| [cleanup](jane_kit.content.md#jane_kitcontentfiletransitstorecleanup) | Метод | ні |

### Опис із вихідного коду

```text
Transit blobs of one producer under ``<root>/<producer>/`` (``file://`` URIs; one node or a shared volume).

The consumers read them only inside their configured ``BLOB_ROOTS`` (:class:`ContentReader`); the producer
removes them after the TTL (:meth:`cleanup`, run by the producer's own periodic task).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_content_writer.py:35](../../../../../../libs/jane-kit/tests/test_content_writer.py#L35).

```python
store = FileTransitStore(tmp_path / "transit", "web-collector")
```

Контекст і передумови: [libs/jane-kit/tests/test_content_writer.py:61](../../../../../../libs/jane-kit/tests/test_content_writer.py#L61).

```python
store = FileTransitStore(tmp_path, "storage")
```

## jane_kit.content.FileTransitStore.__init__

**Конструктор.** Код: [libs/jane-kit/src/jane_kit/content.py:401](../../../../../../libs/jane-kit/src/jane_kit/content.py#L401).

```python
def __init__(self, root: Path, producer: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `root` | `Path` | `—` | positional-or-keyword |
| `producer` | `str` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_content_writer.py:35](../../../../../../libs/jane-kit/tests/test_content_writer.py#L35).

```python
store = FileTransitStore(tmp_path / "transit", "web-collector")
```

Контекст і передумови: [libs/jane-kit/tests/test_content_writer.py:61](../../../../../../libs/jane-kit/tests/test_content_writer.py#L61).

```python
store = FileTransitStore(tmp_path, "storage")
```

## jane_kit.content.FileTransitStore.root

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/content.py:404](../../../../../../libs/jane-kit/src/jane_kit/content.py#L404).

```python
self.root = root.resolve()
```

## jane_kit.content.FileTransitStore.producer

**Поле екземпляра.** Код: [libs/jane-kit/src/jane_kit/content.py:405](../../../../../../libs/jane-kit/src/jane_kit/content.py#L405).

```python
self.producer = producer
```

## jane_kit.content.FileTransitStore.base

**Властивість.** Код: [libs/jane-kit/src/jane_kit/content.py:408](../../../../../../libs/jane-kit/src/jane_kit/content.py#L408).

```python
def base(self) -> Path:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Path`.

Доступ: читання — так; запис — ні.

## jane_kit.content.FileTransitStore.put

**Метод.** Код: [libs/jane-kit/src/jane_kit/content.py:411](../../../../../../libs/jane-kit/src/jane_kit/content.py#L411).

```python
def put(self, name: str, body: bytes, media_type: str, now: datetime, *, reuse: bool=False) -> Path:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |
| `body` | `bytes` | `—` | positional-or-keyword |
| `media_type` | `str` | `—` | positional-or-keyword |
| `now` | `datetime` | `—` | positional-or-keyword |
| `reuse` | `bool` | `False` | keyword-only |

Результат: `Path`.

Явні `raise` у тілі: `AssertionError`, `ValueError`, `повторний raise`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Write ``body`` atomically as ``<base>/<YYYY>/<MM>/<DD>/<name><ext>``.

``reuse`` (only for a content-addressed ``name``): an existing file of the same size is kept and only its
time is refreshed, so the cleaner keeps it for another TTL.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_content_writer.py:67](../../../../../../libs/jane-kit/tests/test_content_writer.py#L67).

```python
first = store.put("obj-abc", b"one", "text/plain", NOW, reuse=True)
```

Контекст і передумови: [libs/jane-kit/tests/test_content_writer.py:70](../../../../../../libs/jane-kit/tests/test_content_writer.py#L70).

```python
again = store.put("obj-abc", b"one", "text/plain", NOW, reuse=True)
```

## jane_kit.content.FileTransitStore.cleanup

**Метод.** Код: [libs/jane-kit/src/jane_kit/content.py:442](../../../../../../libs/jane-kit/src/jane_kit/content.py#L442).

```python
def cleanup(self, ttl_seconds: float) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `ttl_seconds` | `float` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Remove this producer's transit files older than ``ttl_seconds`` (and empty day folders); returns the
number of files removed. Files being written are newer than the TTL, so they are never touched.
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_content_writer.py:86](../../../../../../libs/jane-kit/tests/test_content_writer.py#L86).

```python
assert mine.cleanup(3600) == 1
```

## jane_kit.content.ContentWriter

**Клас.** Код: [libs/jane-kit/src/jane_kit/content.py:463](../../../../../../libs/jane-kit/src/jane_kit/content.py#L463).

```python
class ContentWriter:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [mode](jane_kit.content.md#jane_kitcontentcontentwritermode) | Поле | ні |
| [inline_max_bytes](jane_kit.content.md#jane_kitcontentcontentwriterinline_max_bytes) | Поле | ні |
| [transit_ttl_seconds](jane_kit.content.md#jane_kitcontentcontentwritertransit_ttl_seconds) | Поле | ні |
| [store](jane_kit.content.md#jane_kitcontentcontentwriterstore) | Поле | ні |
| [ref](jane_kit.content.md#jane_kitcontentcontentwriterref) | Метод | ні |
| [blob](jane_kit.content.md#jane_kitcontentcontentwriterblob) | Метод | ні |
| [__init__](jane_kit.content.md#jane_kitcontentcontentwriter__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Delivery of a producer's content as ContentRef (see the module docstring).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_content_writer.py:36](../../../../../../libs/jane-kit/tests/test_content_writer.py#L36).

```python
auto = ContentWriter("auto", inline_max_bytes=8, transit_ttl_seconds=3600, store=store)
```

Контекст і передумови: [libs/jane-kit/tests/test_content_writer.py:92](../../../../../../libs/jane-kit/tests/test_content_writer.py#L92).

```python
ref = ContentWriter("blob", 8, 60, FileTransitStore(tmp_path / "t", "assistant")).ref(
        b"data", "text/plain", "n1", NOW
    )
```

## jane_kit.content.ContentWriter.__init__

**Конструктор dataclass.** Код: [libs/jane-kit/src/jane_kit/content.py:463](../../../../../../libs/jane-kit/src/jane_kit/content.py#L463).

```python
def __init__(self, mode: Literal['auto', 'inline', 'blob'], inline_max_bytes: int, transit_ttl_seconds: int, store: FileTransitStore | None) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `mode` | `Literal['auto', 'inline', 'blob']` | `—` | positional-or-keyword |
| `inline_max_bytes` | `int` | `—` | positional-or-keyword |
| `transit_ttl_seconds` | `int` | `—` | positional-or-keyword |
| `store` | `FileTransitStore \| None` | `—` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_content_writer.py:36](../../../../../../libs/jane-kit/tests/test_content_writer.py#L36).

```python
auto = ContentWriter("auto", inline_max_bytes=8, transit_ttl_seconds=3600, store=store)
```

Контекст і передумови: [libs/jane-kit/tests/test_content_writer.py:92](../../../../../../libs/jane-kit/tests/test_content_writer.py#L92).

```python
ref = ContentWriter("blob", 8, 60, FileTransitStore(tmp_path / "t", "assistant")).ref(
        b"data", "text/plain", "n1", NOW
    )
```

## jane_kit.content.ContentWriter.mode

**Поле.** Код: [libs/jane-kit/src/jane_kit/content.py:466](../../../../../../libs/jane-kit/src/jane_kit/content.py#L466).

```python
mode: Literal['auto', 'inline', 'blob']
```

Доступ: читання — так; запис — так.

## jane_kit.content.ContentWriter.inline_max_bytes

**Поле.** Код: [libs/jane-kit/src/jane_kit/content.py:467](../../../../../../libs/jane-kit/src/jane_kit/content.py#L467).

```python
inline_max_bytes: int
```

Доступ: читання — так; запис — так.

## jane_kit.content.ContentWriter.transit_ttl_seconds

**Поле.** Код: [libs/jane-kit/src/jane_kit/content.py:468](../../../../../../libs/jane-kit/src/jane_kit/content.py#L468).

```python
transit_ttl_seconds: int
```

Доступ: читання — так; запис — так.

## jane_kit.content.ContentWriter.store

**Поле.** Код: [libs/jane-kit/src/jane_kit/content.py:469](../../../../../../libs/jane-kit/src/jane_kit/content.py#L469).

```python
store: FileTransitStore | None
```

Доступ: читання — так; запис — так.

## jane_kit.content.ContentWriter.ref

**Метод.** Код: [libs/jane-kit/src/jane_kit/content.py:471](../../../../../../libs/jane-kit/src/jane_kit/content.py#L471).

```python
def ref(self, body: bytes, media_type: str, name: str, now: datetime | None=None, *, text: bool=False, charset: str | None=None, reuse: bool=False) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `body` | `bytes` | `—` | positional-or-keyword |
| `media_type` | `str` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |
| `now` | `datetime \| None` | `None` | positional-or-keyword |
| `text` | `bool` | `False` | keyword-only |
| `charset` | `str \| None` | `None` | keyword-only |
| `reuse` | `bool` | `False` | keyword-only |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `ContentTooLarge`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
ContentRef of ``body``; ``name`` names the transit blob if one is written (unique per content;
``reuse`` - the name is content-addressed, an existing blob is kept, see :meth:`FileTransitStore.put`).
```

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_content_writer.py:37](../../../../../../libs/jane-kit/tests/test_content_writer.py#L37).

```python
small = auto.ref(b"tiny", "text/html", "obs_1", NOW, text=True)
```

Контекст і передумови: [libs/jane-kit/tests/test_content_writer.py:40](../../../../../../libs/jane-kit/tests/test_content_writer.py#L40).

```python
big = auto.ref(big_body, "text/html", "obs_2", NOW, text=True, charset="utf-8")
```

## jane_kit.content.ContentWriter.blob

**Метод.** Код: [libs/jane-kit/src/jane_kit/content.py:503](../../../../../../libs/jane-kit/src/jane_kit/content.py#L503).

```python
def blob(self, body: bytes, media_type: str, name: str, now: datetime, *, charset: str | None=None, reuse: bool=False) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `body` | `bytes` | `—` | positional-or-keyword |
| `media_type` | `str` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |
| `now` | `datetime` | `—` | positional-or-keyword |
| `charset` | `str \| None` | `None` | keyword-only |
| `reuse` | `bool` | `False` | keyword-only |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `ContentTooLarge`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
A transit blob of ``body`` (the store must be configured).
```
