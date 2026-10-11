# jane_assistant.search

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_assistant.search.Candidate](#jane_assistantsearchcandidate)
- [jane_assistant.search.Candidate.__init__](#jane_assistantsearchcandidate__init__)
- [jane_assistant.search.Candidate.title](#jane_assistantsearchcandidatetitle)
- [jane_assistant.search.Candidate.url](#jane_assistantsearchcandidateurl)
- [jane_assistant.search.Candidate.telegram_username](#jane_assistantsearchcandidatetelegram_username)
- [jane_assistant.search.Candidate.description](#jane_assistantsearchcandidatedescription)
- [jane_assistant.search.Candidate.confidence](#jane_assistantsearchcandidateconfidence)
- [jane_assistant.search.Candidate.source_kind](#jane_assistantsearchcandidatesource_kind)
- [jane_assistant.search.Candidate.wire](#jane_assistantsearchcandidatewire)
- [jane_assistant.search.SearchProvider](#jane_assistantsearchsearchprovider)
- [jane_assistant.search.SearchProvider.search](#jane_assistantsearchsearchprovidersearch)
- [jane_assistant.search.direct_candidate](#jane_assistantsearchdirect_candidate)
- [jane_assistant.search.score](#jane_assistantsearchscore)
- [jane_assistant.search.NoSearchProvider](#jane_assistantsearchnosearchprovider)
- [jane_assistant.search.NoSearchProvider.search](#jane_assistantsearchnosearchprovidersearch)
- [jane_assistant.search.StaticSearchProvider](#jane_assistantsearchstaticsearchprovider)
- [jane_assistant.search.StaticSearchProvider.__init__](#jane_assistantsearchstaticsearchprovider__init__)
- [jane_assistant.search.StaticSearchProvider.entries](#jane_assistantsearchstaticsearchproviderentries)
- [jane_assistant.search.StaticSearchProvider.from_file](#jane_assistantsearchstaticsearchproviderfrom_file)
- [jane_assistant.search.StaticSearchProvider.search](#jane_assistantsearchstaticsearchprovidersearch)
- [jane_assistant.search.HttpJsonSearchProvider](#jane_assistantsearchhttpjsonsearchprovider)
- [jane_assistant.search.HttpJsonSearchProvider.__init__](#jane_assistantsearchhttpjsonsearchprovider__init__)
- [jane_assistant.search.HttpJsonSearchProvider.url_template](#jane_assistantsearchhttpjsonsearchproviderurl_template)
- [jane_assistant.search.HttpJsonSearchProvider.items_path](#jane_assistantsearchhttpjsonsearchprovideritems_path)
- [jane_assistant.search.HttpJsonSearchProvider.fields](#jane_assistantsearchhttpjsonsearchproviderfields)
- [jane_assistant.search.HttpJsonSearchProvider.http](#jane_assistantsearchhttpjsonsearchproviderhttp)
- [jane_assistant.search.HttpJsonSearchProvider.timeout](#jane_assistantsearchhttpjsonsearchprovidertimeout)
- [jane_assistant.search.HttpJsonSearchProvider.search](#jane_assistantsearchhttpjsonsearchprovidersearch)

## jane_assistant.search.Candidate

**Клас.** Код: [services/assistant/src/jane_assistant/search.py:45](../../../../../../services/assistant/src/jane_assistant/search.py#L45).

```python
class Candidate:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [title](jane_assistant.search.md#jane_assistantsearchcandidatetitle) | Поле | ні |
| [url](jane_assistant.search.md#jane_assistantsearchcandidateurl) | Поле | ні |
| [telegram_username](jane_assistant.search.md#jane_assistantsearchcandidatetelegram_username) | Поле | ні |
| [description](jane_assistant.search.md#jane_assistantsearchcandidatedescription) | Поле | ні |
| [confidence](jane_assistant.search.md#jane_assistantsearchcandidateconfidence) | Поле | ні |
| [source_kind](jane_assistant.search.md#jane_assistantsearchcandidatesource_kind) | Властивість | ні |
| [wire](jane_assistant.search.md#jane_assistantsearchcandidatewire) | Метод | ні |
| [__init__](jane_assistant.search.md#jane_assistantsearchcandidate__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/assistant_fakes/__init__.py:54](../../../../../../services/assistant/tests/assistant_fakes/__init__.py#L54).

```python
DEFAULT_SEARCH = {
    "Shop Example kettles": [
        Candidate("Shop Example", url="https://shop.example.test/", confidence=0.62),
        Candidate("Shop Example Outlet", url="https://outlet.shop.example.test/", confidence=0.35),
    ],
    "Shop Example store": [Candidate("Shop Example", url="https://shop.example.test/", confidence=0.95)],
}
```

Контекст і передумови: [services/assistant/tests/test_units.py:305](../../../../../../services/assistant/tests/test_units.py#L305).

```python
s = Session(
        "onb_1",
        "q",
        {"query": "q"},
        candidates=[Candidate("T", url="https://t.test/", confidence=0.5)],
        selected_candidate_id="cand_1",
        sample=sample,
        plans={"product": plan},
    )
```

## jane_assistant.search.Candidate.__init__

**Конструктор dataclass.** Код: [services/assistant/src/jane_assistant/search.py:45](../../../../../../services/assistant/src/jane_assistant/search.py#L45).

```python
def __init__(self, title: str, url: str | None = None, telegram_username: str | None = None, description: str | None = None, confidence: float = 0.0) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `title` | `str` | `—` | positional-or-keyword |
| `url` | `str \| None` | `None` | positional-or-keyword |
| `telegram_username` | `str \| None` | `None` | positional-or-keyword |
| `description` | `str \| None` | `None` | positional-or-keyword |
| `confidence` | `float` | `0.0` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/assistant_fakes/__init__.py:54](../../../../../../services/assistant/tests/assistant_fakes/__init__.py#L54).

```python
DEFAULT_SEARCH = {
    "Shop Example kettles": [
        Candidate("Shop Example", url="https://shop.example.test/", confidence=0.62),
        Candidate("Shop Example Outlet", url="https://outlet.shop.example.test/", confidence=0.35),
    ],
    "Shop Example store": [Candidate("Shop Example", url="https://shop.example.test/", confidence=0.95)],
}
```

Контекст і передумови: [services/assistant/tests/test_units.py:305](../../../../../../services/assistant/tests/test_units.py#L305).

```python
s = Session(
        "onb_1",
        "q",
        {"query": "q"},
        candidates=[Candidate("T", url="https://t.test/", confidence=0.5)],
        selected_candidate_id="cand_1",
        sample=sample,
        plans={"product": plan},
    )
```

## jane_assistant.search.Candidate.title

**Поле.** Код: [services/assistant/src/jane_assistant/search.py:46](../../../../../../services/assistant/src/jane_assistant/search.py#L46).

```python
title: str
```

Доступ: читання — так; запис — ні.

## jane_assistant.search.Candidate.url

**Поле.** Код: [services/assistant/src/jane_assistant/search.py:47](../../../../../../services/assistant/src/jane_assistant/search.py#L47).

```python
url: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_assistant.search.Candidate.telegram_username

**Поле.** Код: [services/assistant/src/jane_assistant/search.py:48](../../../../../../services/assistant/src/jane_assistant/search.py#L48).

```python
telegram_username: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_assistant.search.Candidate.description

**Поле.** Код: [services/assistant/src/jane_assistant/search.py:49](../../../../../../services/assistant/src/jane_assistant/search.py#L49).

```python
description: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_assistant.search.Candidate.confidence

**Поле.** Код: [services/assistant/src/jane_assistant/search.py:50](../../../../../../services/assistant/src/jane_assistant/search.py#L50).

```python
confidence: float = 0.0
```

Доступ: читання — так; запис — ні.

## jane_assistant.search.Candidate.source_kind

**Властивість.** Код: [services/assistant/src/jane_assistant/search.py:53](../../../../../../services/assistant/src/jane_assistant/search.py#L53).

```python
def source_kind(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## jane_assistant.search.Candidate.wire

**Метод.** Код: [services/assistant/src/jane_assistant/search.py:56](../../../../../../services/assistant/src/jane_assistant/search.py#L56).

```python
def wire(self, candidate_id: str) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `candidate_id` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

## jane_assistant.search.SearchProvider

**Клас.** Код: [services/assistant/src/jane_assistant/search.py:65](../../../../../../services/assistant/src/jane_assistant/search.py#L65).

```python
class SearchProvider(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [search](jane_assistant.search.md#jane_assistantsearchsearchprovidersearch) | Метод | ні |

## jane_assistant.search.SearchProvider.search

**Метод.** Код: [services/assistant/src/jane_assistant/search.py:66](../../../../../../services/assistant/src/jane_assistant/search.py#L66).

```python
async def search(self, query: str, source_kind: str | None, limit: int) -> list[Candidate]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `query` | `str` | `—` | positional-or-keyword |
| `source_kind` | `str \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `list[Candidate]`.

## jane_assistant.search.direct_candidate

**Функція.** Код: [services/assistant/src/jane_assistant/search.py:69](../../../../../../services/assistant/src/jane_assistant/search.py#L69).

```python
def direct_candidate(query: str, source_kind: str | None) -> Candidate | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `query` | `str` | `—` | positional-or-keyword |
| `source_kind` | `str \| None` | `—` | positional-or-keyword |

Результат: `Candidate | None`.

### Опис із вихідного коду

```text
``https://…`` / ``@channel`` / ``t.me/channel`` -> a single certain candidate.
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:156](../../../../../../services/assistant/tests/test_units.py#L156).

```python
assert direct_candidate("Shop Example", None) is None
```

Контекст і передумови: [services/assistant/tests/test_units.py:153](../../../../../../services/assistant/tests/test_units.py#L153).

```python
assert direct_candidate("https://shop.example.test/x", None).url == "https://shop.example.test/x"
```

## jane_assistant.search.score

**Функція.** Код: [services/assistant/src/jane_assistant/search.py:87](../../../../../../services/assistant/src/jane_assistant/search.py#L87).

```python
def score(query: str, *texts: str | None) -> float:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `query` | `str` | `—` | positional-or-keyword |
| `texts` | `str \| None` | `—` | var-positional |

Результат: `float`.

### Опис із вихідного коду

```text
Share of query words found in the candidate's texts (title, aliases, url, description).
```

## jane_assistant.search.NoSearchProvider

**Клас.** Код: [services/assistant/src/jane_assistant/search.py:99](../../../../../../services/assistant/src/jane_assistant/search.py#L99).

```python
class NoSearchProvider:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [search](jane_assistant.search.md#jane_assistantsearchnosearchprovidersearch) | Метод | ні |

## jane_assistant.search.NoSearchProvider.search

**Метод.** Код: [services/assistant/src/jane_assistant/search.py:100](../../../../../../services/assistant/src/jane_assistant/search.py#L100).

```python
async def search(self, query: str, source_kind: str | None, limit: int) -> list[Candidate]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `query` | `str` | `—` | positional-or-keyword |
| `source_kind` | `str \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `list[Candidate]`.

Явні `raise` у тілі: `JaneError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_assistant.search.StaticSearchProvider

**Клас.** Код: [services/assistant/src/jane_assistant/search.py:106](../../../../../../services/assistant/src/jane_assistant/search.py#L106).

```python
class StaticSearchProvider:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_assistant.search.md#jane_assistantsearchstaticsearchprovider__init__) | Конструктор | ні |
| [entries](jane_assistant.search.md#jane_assistantsearchstaticsearchproviderentries) | Поле екземпляра | ні |
| [from_file](jane_assistant.search.md#jane_assistantsearchstaticsearchproviderfrom_file) | Метод | ні |
| [search](jane_assistant.search.md#jane_assistantsearchstaticsearchprovidersearch) | Метод | ні |

### Опис із вихідного коду

```text
Catalogue file: ``[{"title", "url"?, "telegram_username"?, "description"?, "aliases"?: []}]``.
```

## jane_assistant.search.StaticSearchProvider.__init__

**Конструктор.** Код: [services/assistant/src/jane_assistant/search.py:109](../../../../../../services/assistant/src/jane_assistant/search.py#L109).

```python
def __init__(self, entries: list[dict[str, Any]]) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `entries` | `list[dict[str, Any]]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_assistant.search.StaticSearchProvider.entries

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/search.py:110](../../../../../../services/assistant/src/jane_assistant/search.py#L110).

```python
self.entries = entries
```

## jane_assistant.search.StaticSearchProvider.from_file

**Метод.** Код: [services/assistant/src/jane_assistant/search.py:113](../../../../../../services/assistant/src/jane_assistant/search.py#L113).

```python
def from_file(cls, path: Path) -> StaticSearchProvider:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `path` | `Path` | `—` | positional-or-keyword |

Результат: `StaticSearchProvider`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:167](../../../../../../services/assistant/tests/test_units.py#L167).

```python
static = StaticSearchProvider.from_file(f)
```

## jane_assistant.search.StaticSearchProvider.search

**Метод.** Код: [services/assistant/src/jane_assistant/search.py:119](../../../../../../services/assistant/src/jane_assistant/search.py#L119).

```python
async def search(self, query: str, source_kind: str | None, limit: int) -> list[Candidate]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `query` | `str` | `—` | positional-or-keyword |
| `source_kind` | `str \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `list[Candidate]`.

## jane_assistant.search.HttpJsonSearchProvider

**Клас.** Код: [services/assistant/src/jane_assistant/search.py:138](../../../../../../services/assistant/src/jane_assistant/search.py#L138).

```python
class HttpJsonSearchProvider:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_assistant.search.md#jane_assistantsearchhttpjsonsearchprovider__init__) | Конструктор | ні |
| [url_template](jane_assistant.search.md#jane_assistantsearchhttpjsonsearchproviderurl_template) | Поле екземпляра | ні |
| [items_path](jane_assistant.search.md#jane_assistantsearchhttpjsonsearchprovideritems_path) | Поле екземпляра | ні |
| [fields](jane_assistant.search.md#jane_assistantsearchhttpjsonsearchproviderfields) | Поле екземпляра | ні |
| [http](jane_assistant.search.md#jane_assistantsearchhttpjsonsearchproviderhttp) | Поле екземпляра | ні |
| [timeout](jane_assistant.search.md#jane_assistantsearchhttpjsonsearchprovidertimeout) | Поле екземпляра | ні |
| [search](jane_assistant.search.md#jane_assistantsearchhttpjsonsearchprovidersearch) | Метод | ні |

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:179](../../../../../../services/assistant/tests/test_units.py#L179).

```python
http = HttpJsonSearchProvider(
        "https://search.test/?q={query}",
        items_path="data.hits",
        title_field="name",
        url_field="link",
        http=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
```

## jane_assistant.search.HttpJsonSearchProvider.__init__

**Конструктор.** Код: [services/assistant/src/jane_assistant/search.py:139](../../../../../../services/assistant/src/jane_assistant/search.py#L139).

```python
def __init__(self, url_template: str, *, items_path: str='results', title_field: str='title', url_field: str='url', description_field: str='description', http: httpx.AsyncClient | None=None, limits: SearchLimits | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `url_template` | `str` | `—` | positional-or-keyword |
| `items_path` | `str` | `'results'` | keyword-only |
| `title_field` | `str` | `'title'` | keyword-only |
| `url_field` | `str` | `'url'` | keyword-only |
| `description_field` | `str` | `'description'` | keyword-only |
| `http` | `httpx.AsyncClient \| None` | `None` | keyword-only |
| `limits` | `SearchLimits \| None` | `None` | keyword-only |

Результат: `None`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:179](../../../../../../services/assistant/tests/test_units.py#L179).

```python
http = HttpJsonSearchProvider(
        "https://search.test/?q={query}",
        items_path="data.hits",
        title_field="name",
        url_field="link",
        http=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
```

## jane_assistant.search.HttpJsonSearchProvider.url_template

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/search.py:152](../../../../../../services/assistant/src/jane_assistant/search.py#L152).

```python
self.url_template = url_template
```

## jane_assistant.search.HttpJsonSearchProvider.items_path

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/search.py:153](../../../../../../services/assistant/src/jane_assistant/search.py#L153).

```python
self.items_path = items_path
```

## jane_assistant.search.HttpJsonSearchProvider.fields

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/search.py:154](../../../../../../services/assistant/src/jane_assistant/search.py#L154).

```python
self.fields = (title_field, url_field, description_field)
```

## jane_assistant.search.HttpJsonSearchProvider.http

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/search.py:155](../../../../../../services/assistant/src/jane_assistant/search.py#L155).

```python
self.http = http
```

## jane_assistant.search.HttpJsonSearchProvider.timeout

**Поле екземпляра.** Код: [services/assistant/src/jane_assistant/search.py:157](../../../../../../services/assistant/src/jane_assistant/search.py#L157).

```python
self.timeout = httpx.Timeout(limits.request_timeout_ms / 1000, connect=limits.connect_timeout_ms / 1000)
```

## jane_assistant.search.HttpJsonSearchProvider.search

**Метод.** Код: [services/assistant/src/jane_assistant/search.py:162](../../../../../../services/assistant/src/jane_assistant/search.py#L162).

```python
async def search(self, query: str, source_kind: str | None, limit: int) -> list[Candidate]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `query` | `str` | `—` | positional-or-keyword |
| `source_kind` | `str \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `list[Candidate]`.

Явні `raise` у тілі: `JaneError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_units.py:186](../../../../../../services/assistant/tests/test_units.py#L186).

```python
hits = asyncio.run(http.search("shop example", None, 5))
```
