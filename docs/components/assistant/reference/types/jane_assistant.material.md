# Модуль `jane_assistant.material`

> Згенеровано `scripts/docs_reference.py` з [services/assistant/src/jane_assistant/material.py](../../../../../services/assistant/src/jane_assistant/material.py). Не редагуйте вручну.

Large HTML materials: what the model sees and what tests run on.

Real pages are large (a shop category page is 0.5-3 MB) and their first kilobytes are usually scripts and styles; the informative part - schema.org JSON-LD, microdata, head tags, visible text - is further down. So:

* :func:`reduce_material` - once a material is read, HTML above ``material.max_fixture_bytes`` is reduced: executable scripts, styles, SVG, ``noscript`` and comments are removed, then data scripts other than JSON-LD (largest first), then the end of the body (cut at a tag; JSON-LD blocks from the cut part are kept while they fit). The page is read as HTML is: a ``<script>``, ``<style>``, ``<svg>``, ``<noscript>`` element or a comment is one opaque block from its start to its end, the earliest first, so ``"<!--"`` or ``"<style"`` inside a script is just script text. What is kept is byte-identical to the page, but the reduced page is **not** the real page: the removed scripts and the cut end of the body are still there on the real one, so an extractor that searches the whole page text (a price pattern that a script also contains) can pass on the reduced page and fail on the real one. Extractors are told so, and a proposal names the risk when its extractor was tested on reduced pages. The reduced page is the material of the sample: the model sees it, extractors are tested on it and packages keep it as their test fixture (``content.sha256``/``size_bytes``/``revision.content_sha256`` describe the reduced content). The full page cannot be the fixture: it does not fit ``transfer.inline_max_bytes``.
* :func:`material_text` - the text of a material for the model: small or non-HTML content as is (cut to the budget); larger HTML as a *digest* of the same size: head tags, structured data (JSON-LD with long lists shortened to their first items and the number of the rest stated, microdata types), visible text and the start of the body markup, in shares of the budget (``material.*_share``).
* evidence helpers for proposals: the declared ``rel=canonical`` of a page, its links, link patterns and pagination-like URL templates (read outside scripts and comments).

Content is untrusted data: it only ever goes into ``data`` parts of model requests and into test fixtures.

## Зміст

- [Функція `declared_canonical`](#функція-declared_canonical)
- [Функція `empty_shell`](#функція-empty_shell)
- [Функція `html_digest`](#функція-html_digest)
- [Функція `inline_bytes`](#функція-inline_bytes)
- [Функція `inline_text`](#функція-inline_text)
- [Функція `is_html`](#функція-is_html)
- [Функція `lean_html`](#функція-lean_html)
- [Функція `link_pattern`](#функція-link_pattern)
- [Функція `material_text`](#функція-material_text)
- [Функція `outside_blocks`](#функція-outside_blocks)
- [Функція `page_links`](#функція-page_links)
- [Функція `pagination_templates`](#функція-pagination_templates)
- [Функція `reduce_material`](#функція-reduce_material)
- [Функція `same_url`](#функція-same_url)
- [Функція `with_content`](#функція-with_content)

## Функції

### Функція `declared_canonical`

```python
def declared_canonical(page: str, base_url: str) -> str | None: ...
```

Absolute URL of the first ``<link rel="canonical">`` of the page (outside scripts and comments).

Код: [material.py:424](../../../../../services/assistant/src/jane_assistant/material.py#L424).

### Функція `empty_shell`

```python
def empty_shell(material: Mapping[str, Any]) -> dict[str, Any]: ...
```

The same material as an empty page of its site: its ``<title>`` and an empty body - a negative example when a sample holds one material type only.

Код: [material.py:247](../../../../../services/assistant/src/jane_assistant/material.py#L247).

### Функція `html_digest`

```python
def html_digest(
    page: str,
    max_chars: int,
    limits: MaterialLimits,
    *,
    size_bytes: int | None = None,
) -> str: ...
```

A digest of ``page`` of at most ``max_chars`` characters (see the module docstring).

Код: [material.py:361](../../../../../services/assistant/src/jane_assistant/material.py#L361).

### Функція `inline_bytes`

```python
def inline_bytes(material: Mapping[str, Any]) -> bytes | None: ...
```

Bytes of an inline ``material.content`` (``None`` for blob content).

Код: [material.py:200](../../../../../services/assistant/src/jane_assistant/material.py#L200).

### Функція `inline_text`

```python
def inline_text(material: Mapping[str, Any], fallback: str = '') -> str: ...
```

Text of an inline ``material.content`` (``fallback`` for content given by reference).

Код: [material.py:209](../../../../../services/assistant/src/jane_assistant/material.py#L209).

### Функція `is_html`

```python
def is_html(media_type: str | None) -> bool: ...
```

Код: [material.py:94](../../../../../services/assistant/src/jane_assistant/material.py#L94).

### Функція `lean_html`

```python
def lean_html(page: str, max_bytes: int) -> str: ...
```

``page`` reduced to about ``max_bytes`` UTF-8 bytes (see the module docstring); unchanged if it fits.

Код: [material.py:140](../../../../../services/assistant/src/jane_assistant/material.py#L140).

### Функція `link_pattern`

```python
def link_pattern(url: str) -> str: ...
```

``host/path`` with variable parts as ``*``; ``key=value`` path segments and query parameters keep the key (``page=*``, ``?page=*``), so pagination and filter links stay apart.

Код: [material.py:454](../../../../../services/assistant/src/jane_assistant/material.py#L454).

### Функція `material_text`

```python
def material_text(
    text: str,
    media_type: str | None,
    max_chars: int,
    limits: MaterialLimits,
) -> str: ...
```

Text of a material for the model, at most ``max_chars`` characters: as is when it fits; HTML as a digest; anything else cut (with a marker when there is room for it).

Код: [material.py:395](../../../../../services/assistant/src/jane_assistant/material.py#L395).

### Функція `outside_blocks`

```python
def outside_blocks(page: str) -> str: ...
```

``page`` without scripts, styles, SVG, noscript and comments (each replaced by a space): the markup a browser shows, where tags and links are read.

Код: [material.py:129](../../../../../services/assistant/src/jane_assistant/material.py#L129).

### Функція `page_links`

```python
def page_links(page: str, base_url: str, hosts: Iterable[str] | None = None) -> list[str]: ...
```

Absolute http(s) links of ``<a href>`` outside scripts and comments (unique, in page order), optionally only on ``hosts``.

Код: [material.py:435](../../../../../services/assistant/src/jane_assistant/material.py#L435).

### Функція `pagination_templates`

```python
def pagination_templates(links: Iterable[str]) -> dict[str, list[int]]: ...
```

Pagination-like URL templates among ``links``: one number in the path or query replaced by ``{n}`` that takes at least two values, the smallest of them at most ``_PAGINATION_START_MAX`` (``.../page=2/``).

Код: [material.py:473](../../../../../services/assistant/src/jane_assistant/material.py#L473).

### Функція `reduce_material`

```python
def reduce_material(
    material: Mapping[str, Any],
    raw: bytes,
    text: str,
    limits: MaterialLimits,
    *,
    inline: bool = True,
) -> dict[str, Any]: ...
```

The material of a sample (see the module docstring): HTML above ``max_fixture_bytes`` reduced; with ``inline`` content given by reference also becomes inline (so tests and fixtures need no further reads).

Код: [material.py:261](../../../../../services/assistant/src/jane_assistant/material.py#L261).

### Функція `same_url`

```python
def same_url(a: str, b: str) -> bool: ...
```

URLs equal up to the host case, the fragment, a default port and a trailing slash.

Код: [material.py:410](../../../../../services/assistant/src/jane_assistant/material.py#L410).

### Функція `with_content`

```python
def with_content(
    material: Mapping[str, Any],
    raw: bytes,
    *,
    text: str | None = None,
) -> dict[str, Any]: ...
```

Copy of ``material`` with ``raw`` as its inline content (``text`` - the same bytes decoded, if known).

Код: [material.py:223](../../../../../services/assistant/src/jane_assistant/material.py#L223).
