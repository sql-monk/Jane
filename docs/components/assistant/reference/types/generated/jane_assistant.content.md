# jane_assistant.content

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_assistant.content.MaterialContent](#jane_assistantcontentmaterialcontent)
- [jane_assistant.content.MaterialContent.__init__](#jane_assistantcontentmaterialcontent__init__)
- [jane_assistant.content.MaterialContent.reader](#jane_assistantcontentmaterialcontentreader)
- [jane_assistant.content.MaterialContent.max_bytes](#jane_assistantcontentmaterialcontentmax_bytes)
- [jane_assistant.content.MaterialContent.from_settings](#jane_assistantcontentmaterialcontentfrom_settings)
- [jane_assistant.content.MaterialContent.read](#jane_assistantcontentmaterialcontentread)
- [jane_assistant.content.MaterialContentScope](#jane_assistantcontentmaterialcontentscope)
- [jane_assistant.content.MaterialContentScope.__init__](#jane_assistantcontentmaterialcontentscope__init__)
- [jane_assistant.content.MaterialContentScope.app](#jane_assistantcontentmaterialcontentscopeapp)
- [jane_assistant.content.MaterialContentScope.content](#jane_assistantcontentmaterialcontentscopecontent)
- [jane_assistant.content.MaterialContentScope.__call__](#jane_assistantcontentmaterialcontentscope__call__)
- [jane_assistant.content.material_bytes](#jane_assistantcontentmaterial_bytes)
- [jane_assistant.content.decode_text](#jane_assistantcontentdecode_text)
- [jane_assistant.content.truncate](#jane_assistantcontenttruncate)
- [jane_assistant.content.host_of](#jane_assistantcontenthost_of)
- [jane_assistant.content.url_shape](#jane_assistantcontenturl_shape)
- [jane_assistant.content.material_label](#jane_assistantcontentmaterial_label)

## jane_assistant.content.MaterialContent

**Клас.** Код: [services/assistant/src/jane_assistant/content.py:51](../../../../../../services/assistant/src/jane_assistant/content.py#L51).

```python
class MaterialContent:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [reader](jane_assistant.content.md#jane_assistantcontentmaterialcontentreader) | Поле | ні |
| [max_bytes](jane_assistant.content.md#jane_assistantcontentmaterialcontentmax_bytes) | Поле | ні |
| [from_settings](jane_assistant.content.md#jane_assistantcontentmaterialcontentfrom_settings) | Метод | ні |
| [read](jane_assistant.content.md#jane_assistantcontentmaterialcontentread) | Метод | ні |
| [__init__](jane_assistant.content.md#jane_assistantcontentmaterialcontent__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Reads ``material.content`` with the assistant's ContentRef policy and ``limits.content``.
```

## jane_assistant.content.MaterialContent.__init__

**Конструктор dataclass.** Код: [services/assistant/src/jane_assistant/content.py:51](../../../../../../services/assistant/src/jane_assistant/content.py#L51).

```python
def __init__(self, reader: ContentReader, max_bytes: int) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `reader` | `ContentReader` | `—` | positional-or-keyword |
| `max_bytes` | `int` | `—` | positional-or-keyword |

Результат: `None`.

## jane_assistant.content.MaterialContent.reader

**Поле.** Код: [services/assistant/src/jane_assistant/content.py:54](../../../../../../services/assistant/src/jane_assistant/content.py#L54).

```python
reader: ContentReader
```

Доступ: читання — так; запис — ні.

## jane_assistant.content.MaterialContent.max_bytes

**Поле.** Код: [services/assistant/src/jane_assistant/content.py:55](../../../../../../services/assistant/src/jane_assistant/content.py#L55).

```python
max_bytes: int
```

Доступ: читання — так; запис — ні.

## jane_assistant.content.MaterialContent.from_settings

**Метод.** Код: [services/assistant/src/jane_assistant/content.py:58](../../../../../../services/assistant/src/jane_assistant/content.py#L58).

```python
def from_settings(cls, settings: Settings, limits: ServiceLimits) -> MaterialContent:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `settings` | `Settings` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |

Результат: `MaterialContent`.

## jane_assistant.content.MaterialContent.read

**Метод.** Код: [services/assistant/src/jane_assistant/content.py:70](../../../../../../services/assistant/src/jane_assistant/content.py#L70).

```python
async def read(self, material: Mapping[str, Any]) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `material` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `bytes`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_assistant.content.MaterialContentScope

**Клас.** Код: [services/assistant/src/jane_assistant/content.py:83](../../../../../../services/assistant/src/jane_assistant/content.py#L83).

```python
class MaterialContentScope:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_assistant.content.md#jane_assistantcontentmaterialcontentscope__init__) | Конструктор | ні |
| [app](jane_assistant.content.md#jane_assistantcontentmaterialcontentscopeapp) | Поле екземпляра | ні |
| [content](jane_assistant.content.md#jane_assistantcontentmaterialcontentscopecontent) | Поле екземпляра | ні |
| [__call__](jane_assistant.content.md#jane_assistantcontentmaterialcontentscope__call__) | Метод | ні |

### Опис із вихідного коду

```text
ASGI middleware: a request of the app, and every job it starts (tasks copy the context), reads material
content with ``content``.
```

## jane_assistant.content.MaterialContentScope.__init__

**Конструктор.** Код: [services/assistant/src/jane_assistant/content.py:87](../../../../../../services/assistant/src/jane_assistant/content.py#L87).

```python
def __init__(self, app: ASGIApp, content: MaterialContent) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `app` | `ASGIApp` | `—` | positional-or-keyword |
| `content` | `MaterialContent` | `—` | positional-or-keyword |

Результат: `None`.

## jane_assistant.content.MaterialContentScope.app

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/content.py:88](../../../../../../services/assistant/src/jane_assistant/content.py#L88).

```python
self.app = app
```

## jane_assistant.content.MaterialContentScope.content

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/content.py:89](../../../../../../services/assistant/src/jane_assistant/content.py#L89).

```python
self.content = content
```

## jane_assistant.content.MaterialContentScope.__call__

**Метод.** Код: [services/assistant/src/jane_assistant/content.py:91](../../../../../../services/assistant/src/jane_assistant/content.py#L91).

```python
async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `scope` | `Scope` | `—` | positional-or-keyword |
| `receive` | `Receive` | `—` | positional-or-keyword |
| `send` | `Send` | `—` | positional-or-keyword |

Результат: `None`.

## jane_assistant.content.material_bytes

**Функція.** Код: [services/assistant/src/jane_assistant/content.py:99](../../../../../../services/assistant/src/jane_assistant/content.py#L99).

```python
async def material_bytes(material: Mapping[str, Any], content: MaterialContent | None=None) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `material` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `content` | `MaterialContent \| None` | `None` | positional-or-keyword |

Результат: `bytes`.

### Опис із вихідного коду

```text
Bytes of ``material.content`` (``sha256`` verified when present). ``content`` defaults to the reader of
the current app (:class:`MaterialContentScope`), else inline only.
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_content_policy.py:201](../../../../../../services/assistant/tests/test_content_policy.py#L201).

```python
assert await material_bytes(inline) == b"x"
```

Контекст і передумови: [services/assistant/tests/test_content_policy.py:204](../../../../../../services/assistant/tests/test_content_policy.py#L204).

```python
await material_bytes({"content": content})
```

## jane_assistant.content.decode_text

**Функція.** Код: [services/assistant/src/jane_assistant/content.py:105](../../../../../../services/assistant/src/jane_assistant/content.py#L105).

```python
def decode_text(raw: bytes, charset: str | None=None) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `raw` | `bytes` | `—` | positional-or-keyword |
| `charset` | `str \| None` | `None` | positional-or-keyword |

Результат: `str`.

## jane_assistant.content.truncate

**Функція.** Код: [services/assistant/src/jane_assistant/content.py:112](../../../../../../services/assistant/src/jane_assistant/content.py#L112).

```python
def truncate(text: str, max_chars: int) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `text` | `str` | `—` | positional-or-keyword |
| `max_chars` | `int` | `—` | positional-or-keyword |

Результат: `str`.

## jane_assistant.content.host_of

**Функція.** Код: [services/assistant/src/jane_assistant/content.py:118](../../../../../../services/assistant/src/jane_assistant/content.py#L118).

```python
def host_of(url: str | None) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `url` | `str \| None` | `—` | positional-or-keyword |

Результат: `str | None`.

## jane_assistant.content.url_shape

**Функція.** Код: [services/assistant/src/jane_assistant/content.py:136](../../../../../../services/assistant/src/jane_assistant/content.py#L136).

```python
def url_shape(material: dict[str, Any]) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `material` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Structural signature of a material's URL (``host/product/*``) used to diversify samples:
variable path segments (numbers, hashes, slugs, prefixed ids) collapse to ``*``, parameter-like
segments (``producer=asus``, ``page=2``, ``a=1;b=2`` - filters and pagination embedded in the path, as
query parameters are) to ``*=*``, and any query string to ``?q``.
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_material.py:130](../../../../../../services/assistant/tests/test_material.py#L130).

```python
return url_shape({"locator": {"url": url}})
```

Контекст і передумови: [services/assistant/tests/test_onboarding.py:318](../../../../../../services/assistant/tests/test_onboarding.py#L318).

```python
assert url_shape(items[4]) == url_shape(items[8]) == url_shape(items[9])
```

## jane_assistant.content.material_label

**Функція.** Код: [services/assistant/src/jane_assistant/content.py:156](../../../../../../services/assistant/src/jane_assistant/content.py#L156).

```python
def material_label(material: dict[str, Any]) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `material` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `str`.
