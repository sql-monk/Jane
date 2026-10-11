# Модуль `jane_assistant.content`

> Згенеровано `scripts/docs_reference.py` з [services/assistant/src/jane_assistant/content.py](../../../../../services/assistant/src/jane_assistant/content.py). Не редагуйте вручну.

Material content helpers: read ``ContentRef`` (inline / blob) under the ContentRef policy, URL shapes, truncation.

Material content is untrusted data. It is only ever placed in ``data`` parts of LLM requests (``llm.v1`` ``DataPart``) and in package test fixtures, never in instructions.

Reading (WP-01h) goes through ``jane_kit.content.ContentReader``: ``file://`` only inside ``JANE_ASSISTANT_BLOB_ROOTS``, ``download_url`` only to ``JANE_ASSISTANT_DOWNLOAD_HOST_ALLOWLIST`` hosts (both empty by default), no redirects, size and timeouts from ``limits.content``. The app installs its :class:`MaterialContent` with :class:`MaterialContentScope` for every request, so the jobs a request starts (onboarding sampling, improvement samples, unknown materials) read with it; outside an app (or without a scope) :func:`material_bytes` reads inline content only.

## Зміст

- [Клас `MaterialContent`](#клас-materialcontent)
- [Клас `MaterialContentScope`](#клас-materialcontentscope)
- [Функція `decode_text`](#функція-decode_text)
- [Функція `host_of`](#функція-host_of)
- [Функція `material_bytes`](#функція-material_bytes)
- [Функція `material_label`](#функція-material_label)
- [Функція `truncate`](#функція-truncate)
- [Функція `url_shape`](#функція-url_shape)

## Класи

### Клас `MaterialContent`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_assistant.content` |
| Код | [content.py:51](../../../../../services/assistant/src/jane_assistant/content.py#L51) |

```python
@dataclass(frozen=True)
class MaterialContent: ...
```

Reads ``material.content`` with the assistant's ContentRef policy and ``limits.content``.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `reader` | `ContentReader` | — | читання |  |
| `max_bytes` | `int` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `MaterialContent.from_settings`

```python
@classmethod
def from_settings(cls, settings: Settings, limits: ServiceLimits) -> MaterialContent: ...
```

Код: [content.py:58](../../../../../services/assistant/src/jane_assistant/content.py#L58).

#### Метод `MaterialContent.read`

```python
async def read(self, material: Mapping[str, Any]) -> bytes: ...
```

Винятки в коді методу: `ValidationFailed`.

Код: [content.py:70](../../../../../services/assistant/src/jane_assistant/content.py#L70).

### Клас `MaterialContentScope`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.content` |
| Код | [content.py:83](../../../../../services/assistant/src/jane_assistant/content.py#L83) |

```python
class MaterialContentScope: ...
```

ASGI middleware: a request of the app, and every job it starts (tasks copy the context), reads material content with ``content``.

#### Конструктор `MaterialContentScope.__init__`

```python
def __init__(self, app: ASGIApp, content: MaterialContent) -> None: ...
```

Код: [content.py:87](../../../../../services/assistant/src/jane_assistant/content.py#L87).

#### Метод `MaterialContentScope.__call__`

```python
async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...
```

Код: [content.py:91](../../../../../services/assistant/src/jane_assistant/content.py#L91).

## Функції

### Функція `decode_text`

```python
def decode_text(raw: bytes, charset: str | None = None) -> str: ...
```

Код: [content.py:105](../../../../../services/assistant/src/jane_assistant/content.py#L105).

### Функція `host_of`

```python
def host_of(url: str | None) -> str | None: ...
```

Код: [content.py:118](../../../../../services/assistant/src/jane_assistant/content.py#L118).

### Функція `material_bytes`

```python
async def material_bytes(
    material: Mapping[str, Any],
    content: MaterialContent | None = None,
) -> bytes: ...
```

Bytes of ``material.content`` (``sha256`` verified when present). ``content`` defaults to the reader of the current app (:class:`MaterialContentScope`), else inline only.

Код: [content.py:99](../../../../../services/assistant/src/jane_assistant/content.py#L99).

### Функція `material_label`

```python
def material_label(material: dict[str, Any]) -> str: ...
```

Код: [content.py:156](../../../../../services/assistant/src/jane_assistant/content.py#L156).

### Функція `truncate`

```python
def truncate(text: str, max_chars: int) -> str: ...
```

Код: [content.py:112](../../../../../services/assistant/src/jane_assistant/content.py#L112).

### Функція `url_shape`

```python
def url_shape(material: dict[str, Any]) -> str: ...
```

Structural signature of a material's URL (``host/product/*``) used to diversify samples: variable path segments (numbers, hashes, slugs, prefixed ids) collapse to ``*``, parameter-like segments (``producer=asus``, ``page=2``, ``a=1;b=2`` - filters and pagination embedded in the path, as query parameters are) to ``*=*``, and any query string to ``?q``.

Код: [content.py:136](../../../../../services/assistant/src/jane_assistant/content.py#L136).
