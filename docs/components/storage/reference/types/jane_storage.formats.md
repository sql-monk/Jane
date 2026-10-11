# Модуль `jane_storage.formats`

> Згенеровано `scripts/docs_reference.py` з [services/storage/src/jane_storage/formats.py](../../../../../services/storage/src/jane_storage/formats.py). Не редагуйте вручну.

Storage formats (TZ §5): RAW web pages as HTML by default, other results as JSON; overridable.

Format of a RAW material = ``params.format.raw`` → ``manifest.entry.format.raw`` → default (``auto``):

* default, no ``format.raw`` anywhere (``auto``): an HTML/XHTML web page is stored byte for byte as ``text/html`` (``.html``); any other RAW (Telegram message, JSON API, feed…) — as a JSON document of the Material with its content embedded (``.json``). This is TZ §5 / §13.1 item 4.
* ``original`` — bytes as received; the extension follows the media type;
* ``html`` — the page as ``text/html`` (only for HTML materials);
* ``json`` — the Material document with its content embedded (``content.encoding`` utf-8/base64).

Entities are JSON documents; ``format.entities: jsonl`` is passed to the adapter (``options["entities_format"]``), which may keep history as JSON Lines (filesystem adapter). Other result documents (``writes: data``) are JSON.

## Зміст

- [Клас `InvalidFormat`](#клас-invalidformat)
- [Функція `build_data_object`](#функція-build_data_object)
- [Функція `build_raw_object`](#функція-build_raw_object)
- [Функція `entities_format`](#функція-entities_format)
- [Функція `extension_for`](#функція-extension_for)
- [Функція `material_metadata`](#функція-material_metadata)
- [Функція `raw_format`](#функція-raw_format)

## Класи

### Клас `InvalidFormat`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_storage.formats` |
| Успадкування | `ValueError` |
| Код | [formats.py:65](../../../../../services/storage/src/jane_storage/formats.py#L65) |

```python
class InvalidFormat(ValueError): ...
```

## Функції

### Функція `build_data_object`

```python
def build_data_object(
    data: Any,
    *,
    delivery_key_digest: str,
    index: int,
    source_id: str | None,
) -> RawObject: ...
```

JSON result document of ``writes: data`` (e.g. an LLM output); the key depends only on the delivery.

Код: [formats.py:152](../../../../../services/storage/src/jane_storage/formats.py#L152).

### Функція `build_raw_object`

```python
def build_raw_object(material: Mapping[str, Any], content: bytes, fmt: str) -> RawObject: ...
```

Винятки в коді функції: `InvalidFormat`.

Код: [formats.py:109](../../../../../services/storage/src/jane_storage/formats.py#L109).

### Функція `entities_format`

```python
def entities_format(params: Mapping[str, Any], entry: Mapping[str, Any]) -> str: ...
```

Код: [formats.py:93](../../../../../services/storage/src/jane_storage/formats.py#L93).

### Функція `extension_for`

```python
def extension_for(media_type: str) -> str: ...
```

Код: [formats.py:73](../../../../../services/storage/src/jane_storage/formats.py#L73).

### Функція `material_metadata`

```python
def material_metadata(material: Mapping[str, Any]) -> dict[str, Any]: ...
```

Material without inline content data (kept next to the object for reprocessing).

Код: [formats.py:100](../../../../../services/storage/src/jane_storage/formats.py#L100).

### Функція `raw_format`

```python
def raw_format(params: Mapping[str, Any], entry: Mapping[str, Any]) -> str: ...
```

Код: [formats.py:84](../../../../../services/storage/src/jane_storage/formats.py#L84).
