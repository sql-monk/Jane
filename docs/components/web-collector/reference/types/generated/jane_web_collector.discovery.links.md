# jane_web_collector.discovery.links

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.discovery.links.HTML_TYPES](#jane_web_collectordiscoverylinkshtml_types)
- [jane_web_collector.discovery.links.is_html](#jane_web_collectordiscoverylinksis_html)
- [jane_web_collector.discovery.links.parse_html](#jane_web_collectordiscoverylinksparse_html)
- [jane_web_collector.discovery.links.LINK_SOURCES](#jane_web_collectordiscoverylinkslink_sources)
- [jane_web_collector.discovery.links.extract_hrefs](#jane_web_collectordiscoverylinksextract_hrefs)
- [jane_web_collector.discovery.links.html_meta](#jane_web_collectordiscoverylinkshtml_meta)

## jane_web_collector.discovery.links.HTML_TYPES

**Константа.** Код: [services/web-collector/src/jane_web_collector/discovery/links.py:15](../../../../../../services/web-collector/src/jane_web_collector/discovery/links.py#L15).

```python
HTML_TYPES = frozenset({'text/html', 'application/xhtml+xml'})
```

## jane_web_collector.discovery.links.is_html

**Функція.** Код: [services/web-collector/src/jane_web_collector/discovery/links.py:33](../../../../../../services/web-collector/src/jane_web_collector/discovery/links.py#L33).

```python
def is_html(media_type: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `media_type` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_web_collector.discovery.links.parse_html

**Функція.** Код: [services/web-collector/src/jane_web_collector/discovery/links.py:66](../../../../../../services/web-collector/src/jane_web_collector/discovery/links.py#L66).

```python
def parse_html(body: bytes, charset: str | None=None) -> Any | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `body` | `bytes` | `—` | positional-or-keyword |
| `charset` | `str \| None` | `None` | positional-or-keyword |

Результат: `Any | None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_units.py:227](../../../../../../services/web-collector/tests/test_units.py#L227).

```python
assert html_meta(parse_html(body, charset))["title"] == "Ноутбуки"
```

## jane_web_collector.discovery.links.LINK_SOURCES

**Константа.** Код: [services/web-collector/src/jane_web_collector/discovery/links.py:105](../../../../../../services/web-collector/src/jane_web_collector/discovery/links.py#L105).

```python
LINK_SOURCES: dict[str, Callable[[Any], Iterable[str]]] = {'a_href': _a_href, 'link_rel': _link_rel, 'canonical': _canonical, 'pagination_rel': _pagination_rel}
```

## jane_web_collector.discovery.links.extract_hrefs

**Функція.** Код: [services/web-collector/src/jane_web_collector/discovery/links.py:120](../../../../../../services/web-collector/src/jane_web_collector/discovery/links.py#L120).

```python
def extract_hrefs(doc: Any, *, selector_type: str | None=None, selector: str | None=None, attribute: str='href', sources: Iterable[str]=('a_href',)) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `doc` | `Any` | `—` | positional-or-keyword |
| `selector_type` | `str \| None` | `None` | keyword-only |
| `selector` | `str \| None` | `None` | keyword-only |
| `attribute` | `str` | `'href'` | keyword-only |
| `sources` | `Iterable[str]` | `('a_href',)` | keyword-only |

Результат: `list[str]`.

### Опис із вихідного коду

```text
Raw (not yet resolved) link values in document order.
```

## jane_web_collector.discovery.links.html_meta

**Функція.** Код: [services/web-collector/src/jane_web_collector/discovery/links.py:150](../../../../../../services/web-collector/src/jane_web_collector/discovery/links.py#L150).

```python
def html_meta(doc: Any) -> dict[str, str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `doc` | `Any` | `—` | positional-or-keyword |

Результат: `dict[str, str]`.

### Опис із вихідного коду

```text
``title``, ``article:published_time``, ``article:modified_time`` if present.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_units.py:227](../../../../../../services/web-collector/tests/test_units.py#L227).

```python
assert html_meta(parse_html(body, charset))["title"] == "Ноутбуки"
```
