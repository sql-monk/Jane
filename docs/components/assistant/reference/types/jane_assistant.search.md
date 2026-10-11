# Модуль `jane_assistant.search`

> Згенеровано `scripts/docs_reference.py` з [services/assistant/src/jane_assistant/search.py](../../../../../services/assistant/src/jane_assistant/search.py). Не редагуйте вручну.

Source search: turn a site/channel name into candidates (plan.md WP-11, ТЗ §8, §13.1 п.2).

A direct URL, ``@username`` or ``t.me/<name>`` needs no search. Otherwise the configured provider is asked:

* ``static`` - a JSON catalogue of known sources (offline, for closed environments and dev);
* ``http_json`` - an HTTP search endpoint returning JSON (field paths are configurable);
* tests inject their own :class:`SearchProvider`.

Candidates carry a confidence in ``[0, 1]``; the onboarding flow auto-selects only a clear winner (``limits.onboarding.auto_select_confidence`` and ``auto_select_margin``), otherwise it asks the user (``needs_disambiguation``).

## Зміст

- [Клас `Candidate`](#клас-candidate)
- [Клас `HttpJsonSearchProvider`](#клас-httpjsonsearchprovider)
- [Клас `NoSearchProvider`](#клас-nosearchprovider)
- [Клас `SearchProvider`](#клас-searchprovider)
- [Клас `StaticSearchProvider`](#клас-staticsearchprovider)
- [Функція `direct_candidate`](#функція-direct_candidate)
- [Функція `score`](#функція-score)

## Класи

### Клас `Candidate`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_assistant.search` |
| Код | [search.py:45](../../../../../services/assistant/src/jane_assistant/search.py#L45) |

```python
@dataclass(frozen=True)
class Candidate: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `title` | `str` | — | читання |  |
| `url` | `str \| None` | `None` | читання |  |
| `telegram_username` | `str \| None` | `None` | читання |  |
| `description` | `str \| None` | `None` | читання |  |
| `confidence` | `float` | `0.0` | читання |  |
| `source_kind` | `str` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `Candidate.wire`

```python
def wire(self, candidate_id: str) -> dict[str, Any]: ...
```

Код: [search.py:56](../../../../../services/assistant/src/jane_assistant/search.py#L56).

### Клас `HttpJsonSearchProvider`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.search` |
| Код | [search.py:138](../../../../../services/assistant/src/jane_assistant/search.py#L138) |

```python
class HttpJsonSearchProvider: ...
```

#### Конструктор `HttpJsonSearchProvider.__init__`

```python
def __init__(
    self,
    url_template: str,
    *,
    items_path: str = 'results',
    title_field: str = 'title',
    url_field: str = 'url',
    description_field: str = 'description',
    http: httpx.AsyncClient | None = None,
    limits: SearchLimits | None = None,
) -> None: ...
```

Винятки в коді методу: `ValueError`.

Код: [search.py:139](../../../../../services/assistant/src/jane_assistant/search.py#L139).

#### Метод `HttpJsonSearchProvider.search`

```python
async def search(self, query: str, source_kind: str | None, limit: int) -> list[Candidate]: ...
```

Винятки в коді методу: `JaneError`.

Код: [search.py:162](../../../../../services/assistant/src/jane_assistant/search.py#L162).

### Клас `NoSearchProvider`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.search` |
| Код | [search.py:99](../../../../../services/assistant/src/jane_assistant/search.py#L99) |

```python
class NoSearchProvider: ...
```

#### Метод `NoSearchProvider.search`

```python
async def search(self, query: str, source_kind: str | None, limit: int) -> list[Candidate]: ...
```

Винятки в коді методу: `JaneError`.

Код: [search.py:100](../../../../../services/assistant/src/jane_assistant/search.py#L100).

### Клас `SearchProvider`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_assistant.search` |
| Успадкування | `Protocol` |
| Код | [search.py:65](../../../../../services/assistant/src/jane_assistant/search.py#L65) |

```python
class SearchProvider(Protocol): ...
```

#### Метод `SearchProvider.search`

```python
async def search(self, query: str, source_kind: str | None, limit: int) -> list[Candidate]: ...
```

Код: [search.py:66](../../../../../services/assistant/src/jane_assistant/search.py#L66).

### Клас `StaticSearchProvider`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_assistant.search` |
| Код | [search.py:106](../../../../../services/assistant/src/jane_assistant/search.py#L106) |

```python
class StaticSearchProvider: ...
```

Catalogue file: ``[{"title", "url"?, "telegram_username"?, "description"?, "aliases"?: []}]``.

#### Конструктор `StaticSearchProvider.__init__`

```python
def __init__(self, entries: list[dict[str, Any]]) -> None: ...
```

Код: [search.py:109](../../../../../services/assistant/src/jane_assistant/search.py#L109).

#### Метод `StaticSearchProvider.from_file`

```python
@classmethod
def from_file(cls, path: Path) -> StaticSearchProvider: ...
```

Винятки в коді методу: `ValueError`.

Код: [search.py:113](../../../../../services/assistant/src/jane_assistant/search.py#L113).

#### Метод `StaticSearchProvider.search`

```python
async def search(self, query: str, source_kind: str | None, limit: int) -> list[Candidate]: ...
```

Код: [search.py:119](../../../../../services/assistant/src/jane_assistant/search.py#L119).

## Функції

### Функція `direct_candidate`

```python
def direct_candidate(query: str, source_kind: str | None) -> Candidate | None: ...
```

``https://…`` / ``@channel`` / ``t.me/channel`` -> a single certain candidate.

Код: [search.py:69](../../../../../services/assistant/src/jane_assistant/search.py#L69).

### Функція `score`

```python
def score(query: str, *texts: str | None) -> float: ...
```

Share of query words found in the candidate's texts (title, aliases, url, description).

Код: [search.py:87](../../../../../services/assistant/src/jane_assistant/search.py#L87).
