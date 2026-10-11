# jane_assistant.material

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_assistant.material.is_html](#jane_assistantmaterialis_html)
- [jane_assistant.material.outside_blocks](#jane_assistantmaterialoutside_blocks)
- [jane_assistant.material.lean_html](#jane_assistantmateriallean_html)
- [jane_assistant.material.inline_bytes](#jane_assistantmaterialinline_bytes)
- [jane_assistant.material.inline_text](#jane_assistantmaterialinline_text)
- [jane_assistant.material.with_content](#jane_assistantmaterialwith_content)
- [jane_assistant.material.empty_shell](#jane_assistantmaterialempty_shell)
- [jane_assistant.material.reduce_material](#jane_assistantmaterialreduce_material)
- [jane_assistant.material.html_digest](#jane_assistantmaterialhtml_digest)
- [jane_assistant.material.material_text](#jane_assistantmaterialmaterial_text)
- [jane_assistant.material.same_url](#jane_assistantmaterialsame_url)
- [jane_assistant.material.declared_canonical](#jane_assistantmaterialdeclared_canonical)
- [jane_assistant.material.page_links](#jane_assistantmaterialpage_links)
- [jane_assistant.material.link_pattern](#jane_assistantmateriallink_pattern)
- [jane_assistant.material.pagination_templates](#jane_assistantmaterialpagination_templates)

## jane_assistant.material.is_html

**Функція.** Код: [services/assistant/src/jane_assistant/material.py:94](../../../../../../services/assistant/src/jane_assistant/material.py#L94).

```python
def is_html(media_type: str | None) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `media_type` | `str \| None` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_assistant.material.outside_blocks

**Функція.** Код: [services/assistant/src/jane_assistant/material.py:129](../../../../../../services/assistant/src/jane_assistant/material.py#L129).

```python
def outside_blocks(page: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `page` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
``page`` without scripts, styles, SVG, noscript and comments (each replaced by a space): the markup a
browser shows, where tags and links are read.
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_material.py:288](../../../../../../services/assistant/tests/test_material.py#L288).

```python
assert outside_blocks('a<!-- <script>x</script> -->b<script>"-->"</script>c') == "a b c"
```

## jane_assistant.material.lean_html

**Функція.** Код: [services/assistant/src/jane_assistant/material.py:140](../../../../../../services/assistant/src/jane_assistant/material.py#L140).

```python
def lean_html(page: str, max_bytes: int) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `page` | `str` | `—` | positional-or-keyword |
| `max_bytes` | `int` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
``page`` reduced to about ``max_bytes`` UTF-8 bytes (see the module docstring); unchanged if it fits.
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_material.py:43](../../../../../../services/assistant/tests/test_material.py#L43).

```python
lean = lean_html(page, 64_000)
```

Контекст і передумови: [services/assistant/tests/test_material.py:50](../../../../../../services/assistant/tests/test_material.py#L50).

```python
tight = lean_html(page, 16_000)
```

## jane_assistant.material.inline_bytes

**Функція.** Код: [services/assistant/src/jane_assistant/material.py:200](../../../../../../services/assistant/src/jane_assistant/material.py#L200).

```python
def inline_bytes(material: Mapping[str, Any]) -> bytes | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `material` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `bytes | None`.

### Опис із вихідного коду

```text
Bytes of an inline ``material.content`` (``None`` for blob content).
```

## jane_assistant.material.inline_text

**Функція.** Код: [services/assistant/src/jane_assistant/material.py:209](../../../../../../services/assistant/src/jane_assistant/material.py#L209).

```python
def inline_text(material: Mapping[str, Any], fallback: str='') -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `material` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `fallback` | `str` | `''` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Text of an inline ``material.content`` (``fallback`` for content given by reference).
```

## jane_assistant.material.with_content

**Функція.** Код: [services/assistant/src/jane_assistant/material.py:223](../../../../../../services/assistant/src/jane_assistant/material.py#L223).

```python
def with_content(material: Mapping[str, Any], raw: bytes, *, text: str | None=None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `material` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `raw` | `bytes` | `—` | positional-or-keyword |
| `text` | `str \| None` | `None` | keyword-only |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
Copy of ``material`` with ``raw`` as its inline content (``text`` - the same bytes decoded, if known).
```

## jane_assistant.material.empty_shell

**Функція.** Код: [services/assistant/src/jane_assistant/material.py:247](../../../../../../services/assistant/src/jane_assistant/material.py#L247).

```python
def empty_shell(material: Mapping[str, Any]) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `material` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
The same material as an empty page of its site: its ``<title>`` and an empty body - a negative example
when a sample holds one material type only.
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_material.py:122](../../../../../../services/assistant/tests/test_material.py#L122).

```python
shell = empty_shell(reduced)
```

## jane_assistant.material.reduce_material

**Функція.** Код: [services/assistant/src/jane_assistant/material.py:261](../../../../../../services/assistant/src/jane_assistant/material.py#L261).

```python
def reduce_material(material: Mapping[str, Any], raw: bytes, text: str, limits: MaterialLimits, *, inline: bool=True) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `material` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `raw` | `bytes` | `—` | positional-or-keyword |
| `text` | `str` | `—` | positional-or-keyword |
| `limits` | `MaterialLimits` | `—` | positional-or-keyword |
| `inline` | `bool` | `True` | keyword-only |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
The material of a sample (see the module docstring): HTML above ``max_fixture_bytes`` reduced; with
``inline`` content given by reference also becomes inline (so tests and fixtures need no further reads).
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_material.py:103](../../../../../../services/assistant/tests/test_material.py#L103).

```python
reduced = reduce_material(original, page.encode(), page, limits)
```

Контекст і передумови: [services/assistant/tests/test_material.py:118](../../../../../../services/assistant/tests/test_material.py#L118).

```python
inlined = reduce_material(blob, b"<p>hi</p>", "<p>hi</p>", limits)
```

## jane_assistant.material.html_digest

**Функція.** Код: [services/assistant/src/jane_assistant/material.py:361](../../../../../../services/assistant/src/jane_assistant/material.py#L361).

```python
def html_digest(page: str, max_chars: int, limits: MaterialLimits, *, size_bytes: int | None=None) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `page` | `str` | `—` | positional-or-keyword |
| `max_chars` | `int` | `—` | positional-or-keyword |
| `limits` | `MaterialLimits` | `—` | positional-or-keyword |
| `size_bytes` | `int \| None` | `None` | keyword-only |

Результат: `str`.

### Опис із вихідного коду

```text
A digest of ``page`` of at most ``max_chars`` characters (see the module docstring).
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_material.py:86](../../../../../../services/assistant/tests/test_material.py#L86).

```python
tiny = html_digest(page, 1_500, limits)
```

Контекст і передумови: [services/assistant/tests/test_material.py:303](../../../../../../services/assistant/tests/test_material.py#L303).

```python
assert html_digest(page, 0, limits) == ""
```

## jane_assistant.material.material_text

**Функція.** Код: [services/assistant/src/jane_assistant/material.py:395](../../../../../../services/assistant/src/jane_assistant/material.py#L395).

```python
def material_text(text: str, media_type: str | None, max_chars: int, limits: MaterialLimits) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `text` | `str` | `—` | positional-or-keyword |
| `media_type` | `str \| None` | `—` | positional-or-keyword |
| `max_chars` | `int` | `—` | positional-or-keyword |
| `limits` | `MaterialLimits` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
Text of a material for the model, at most ``max_chars`` characters: as is when it fits; HTML as a digest;
anything else cut (with a marker when there is room for it).
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_material.py:75](../../../../../../services/assistant/tests/test_material.py#L75).

```python
text = material_text(page, "text/html; charset=utf-8", 6_000, limits)
```

Контекст і передумови: [services/assistant/tests/test_material.py:93](../../../../../../services/assistant/tests/test_material.py#L93).

```python
plain = material_text("y" * 7_000, "text/plain", 6_000, limits)
```

## jane_assistant.material.same_url

**Функція.** Код: [services/assistant/src/jane_assistant/material.py:410](../../../../../../services/assistant/src/jane_assistant/material.py#L410).

```python
def same_url(a: str, b: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `a` | `str` | `—` | positional-or-keyword |
| `b` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
URLs equal up to the host case, the fragment, a default port and a trailing slash.
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_material.py:162](../../../../../../services/assistant/tests/test_material.py#L162).

```python
assert same_url("https://Shop.example.test:443/catalog/c80004", BASE)
```

Контекст і передумови: [services/assistant/tests/test_material.py:163](../../../../../../services/assistant/tests/test_material.py#L163).

```python
assert not same_url(f"{BASE}page=2/", BASE)
```

## jane_assistant.material.declared_canonical

**Функція.** Код: [services/assistant/src/jane_assistant/material.py:424](../../../../../../services/assistant/src/jane_assistant/material.py#L424).

```python
def declared_canonical(page: str, base_url: str) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `page` | `str` | `—` | positional-or-keyword |
| `base_url` | `str` | `—` | positional-or-keyword |

Результат: `str | None`.

### Опис із вихідного коду

```text
Absolute URL of the first ``<link rel="canonical">`` of the page (outside scripts and comments).
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_material.py:161](../../../../../../services/assistant/tests/test_material.py#L161).

```python
assert declared_canonical(page, f"{BASE}page=2/") == BASE
```

Контекст і передумови: [services/assistant/tests/test_material.py:289](../../../../../../services/assistant/tests/test_material.py#L289).

```python
assert declared_canonical(
        '<script>"<link rel=canonical href=/x>"</script><link rel="canonical" href="/y">', BASE
    ) == ("https://shop.example.test/y")
```

## jane_assistant.material.page_links

**Функція.** Код: [services/assistant/src/jane_assistant/material.py:435](../../../../../../services/assistant/src/jane_assistant/material.py#L435).

```python
def page_links(page: str, base_url: str, hosts: Iterable[str] | None=None) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `page` | `str` | `—` | positional-or-keyword |
| `base_url` | `str` | `—` | positional-or-keyword |
| `hosts` | `Iterable[str] \| None` | `None` | positional-or-keyword |

Результат: `list[str]`.

### Опис із вихідного коду

```text
Absolute http(s) links of ``<a href>`` outside scripts and comments (unique, in page order), optionally
only on ``hosts``.
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_material.py:164](../../../../../../services/assistant/tests/test_material.py#L164).

```python
links = page_links(page, f"{BASE}page=2/", ["shop.example.test"])
```

Контекст і передумови: [services/assistant/tests/test_material.py:292](../../../../../../services/assistant/tests/test_material.py#L292).

```python
assert page_links(
        '<script>"<a href=/in-js>"</script><!-- <a href="/in-comment"> --><a href="/real">', BASE
    ) == ["https://shop.example.test/real"]
```

## jane_assistant.material.link_pattern

**Функція.** Код: [services/assistant/src/jane_assistant/material.py:454](../../../../../../services/assistant/src/jane_assistant/material.py#L454).

```python
def link_pattern(url: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `url` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Опис із вихідного коду

```text
``host/path`` with variable parts as ``*``; ``key=value`` path segments and query parameters keep the key
(``page=*``, ``?page=*``), so pagination and filter links stay apart.
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_material.py:138](../../../../../../services/assistant/tests/test_material.py#L138).

```python
assert link_pattern(f"{BASE}producer=asus;series=1/") == "shop.example.test/catalog/*/producer=*;series=*"
```

Контекст і передумови: [services/assistant/tests/test_material.py:139](../../../../../../services/assistant/tests/test_material.py#L139).

```python
assert (
        link_pattern("https://shop.example.test/list?page=2&sort=asc")
        == "shop.example.test/list?page=*&sort=*"
    )
```

## jane_assistant.material.pagination_templates

**Функція.** Код: [services/assistant/src/jane_assistant/material.py:473](../../../../../../services/assistant/src/jane_assistant/material.py#L473).

```python
def pagination_templates(links: Iterable[str]) -> dict[str, list[int]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `links` | `Iterable[str]` | `—` | positional-or-keyword |

Результат: `dict[str, list[int]]`.

### Опис із вихідного коду

```text
Pagination-like URL templates among ``links``: one number in the path or query replaced by ``{n}`` that
takes at least two values, the smallest of them at most ``_PAGINATION_START_MAX`` (``.../page=2/``).
```

### Приклади з тестів

Контекст і передумови: [services/assistant/tests/test_material.py:167](../../../../../../services/assistant/tests/test_material.py#L167).

```python
assert pagination_templates(
        ["https://shop.example.test/list?page=2", "https://shop.example.test/list?page=3"]
    )
```

Контекст і передумови: [services/assistant/tests/test_material.py:166](../../../../../../services/assistant/tests/test_material.py#L166).

```python
assert pagination_templates(links) == {f"{BASE}page={{n}}/": [2, 3, 67]}
```
