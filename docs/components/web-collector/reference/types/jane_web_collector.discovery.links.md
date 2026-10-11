# Модуль `jane_web_collector.discovery.links`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/discovery/links.py](../../../../../services/web-collector/src/jane_web_collector/discovery/links.py). Не редагуйте вручну.

Link extraction from HTML (lxml): ``a[href]`` by default, CSS / XPath / ``rel`` selectors, ``<base href>``.

## Зміст

- [Функція `extract_hrefs`](#функція-extract_hrefs)
- [Функція `html_meta`](#функція-html_meta)
- [Функція `is_html`](#функція-is_html)
- [Функція `parse_html`](#функція-parse_html)

## Функції

### Функція `extract_hrefs`

```python
def extract_hrefs(
    doc: Any,
    *,
    selector_type: str | None = None,
    selector: str | None = None,
    attribute: str = 'href',
    sources: Iterable[str] = ('a_href',),
) -> list[str]: ...
```

Raw (not yet resolved) link values in document order.

Код: [links.py:120](../../../../../services/web-collector/src/jane_web_collector/discovery/links.py#L120).

### Функція `html_meta`

```python
def html_meta(doc: Any) -> dict[str, str]: ...
```

``title``, ``article:published_time``, ``article:modified_time`` if present.

Код: [links.py:150](../../../../../services/web-collector/src/jane_web_collector/discovery/links.py#L150).

### Функція `is_html`

```python
def is_html(media_type: str) -> bool: ...
```

Код: [links.py:33](../../../../../services/web-collector/src/jane_web_collector/discovery/links.py#L33).

### Функція `parse_html`

```python
def parse_html(body: bytes, charset: str | None = None) -> Any | None: ...
```

Код: [links.py:66](../../../../../services/web-collector/src/jane_web_collector/discovery/links.py#L66).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `HTML_TYPES` | — | `frozenset({'text/html', 'application/xhtml+xml'})` |  |
| `LINK_SOURCES` | `dict[str, Callable[[Any], Iterable[str]]]` | `{'a_href': _a_href, 'link_rel': _link_rel, 'canonical': _canonical, 'pagination_` |  |
