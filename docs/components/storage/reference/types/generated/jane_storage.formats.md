# jane_storage.formats

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_storage.formats.InvalidFormat](#jane_storageformatsinvalidformat)
- [jane_storage.formats.extension_for](#jane_storageformatsextension_for)
- [jane_storage.formats.raw_format](#jane_storageformatsraw_format)
- [jane_storage.formats.entities_format](#jane_storageformatsentities_format)
- [jane_storage.formats.material_metadata](#jane_storageformatsmaterial_metadata)
- [jane_storage.formats.build_raw_object](#jane_storageformatsbuild_raw_object)
- [jane_storage.formats.build_data_object](#jane_storageformatsbuild_data_object)

## jane_storage.formats.InvalidFormat

**Клас.** Код: [services/storage/src/jane_storage/formats.py:65](../../../../../../services/storage/src/jane_storage/formats.py#L65).

```python
class InvalidFormat(ValueError):
```

Базові типи / інтерфейси: `ValueError`.

## jane_storage.formats.extension_for

**Функція.** Код: [services/storage/src/jane_storage/formats.py:73](../../../../../../services/storage/src/jane_storage/formats.py#L73).

```python
def extension_for(media_type: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `media_type` | `str` | `—` | positional-or-keyword |

Результат: `str`.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_core.py:154](../../../../../../services/storage/tests/test_core.py#L154).

```python
assert extension_for("application/vnd.x+json") == "json"
```

Контекст і передумови: [services/storage/tests/test_core.py:155](../../../../../../services/storage/tests/test_core.py#L155).

```python
assert extension_for("application/octet-stream") == "bin"
```

## jane_storage.formats.raw_format

**Функція.** Код: [services/storage/src/jane_storage/formats.py:84](../../../../../../services/storage/src/jane_storage/formats.py#L84).

```python
def raw_format(params: Mapping[str, Any], entry: Mapping[str, Any]) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `params` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `entry` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `str`.

## jane_storage.formats.entities_format

**Функція.** Код: [services/storage/src/jane_storage/formats.py:93](../../../../../../services/storage/src/jane_storage/formats.py#L93).

```python
def entities_format(params: Mapping[str, Any], entry: Mapping[str, Any]) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `params` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `entry` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `str`.

## jane_storage.formats.material_metadata

**Функція.** Код: [services/storage/src/jane_storage/formats.py:100](../../../../../../services/storage/src/jane_storage/formats.py#L100).

```python
def material_metadata(material: Mapping[str, Any]) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `material` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
Material without inline content data (kept next to the object for reprocessing).
```

## jane_storage.formats.build_raw_object

**Функція.** Код: [services/storage/src/jane_storage/formats.py:109](../../../../../../services/storage/src/jane_storage/formats.py#L109).

```python
def build_raw_object(material: Mapping[str, Any], content: bytes, fmt: str) -> RawObject:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `material` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `content` | `bytes` | `—` | positional-or-keyword |
| `fmt` | `str` | `—` | positional-or-keyword |

Результат: `RawObject`.

Явні `raise` у тілі: `InvalidFormat`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/storage/tests/test_core.py:137](../../../../../../services/storage/tests/test_core.py#L137).

```python
html = build_raw_object(material("text/html; charset=utf-8", b"<html/>"), b"<html/>", "original")
```

Контекст і передумови: [services/storage/tests/test_core.py:142](../../../../../../services/storage/tests/test_core.py#L142).

```python
as_json = build_raw_object(material("text/html", b"<html/>"), b"<html/>", "json")
```

## jane_storage.formats.build_data_object

**Функція.** Код: [services/storage/src/jane_storage/formats.py:152](../../../../../../services/storage/src/jane_storage/formats.py#L152).

```python
def build_data_object(data: Any, *, delivery_key_digest: str, index: int, source_id: str | None) -> RawObject:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `data` | `Any` | `—` | positional-or-keyword |
| `delivery_key_digest` | `str` | `—` | keyword-only |
| `index` | `int` | `—` | keyword-only |
| `source_id` | `str \| None` | `—` | keyword-only |

Результат: `RawObject`.

### Опис із вихідного коду

```text
JSON result document of ``writes: data`` (e.g. an LLM output); the key depends only on the delivery.
```
