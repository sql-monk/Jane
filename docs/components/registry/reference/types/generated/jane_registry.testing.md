# jane_registry.testing

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_registry.testing.TEST_PROFILE](#jane_registrytestingtest_profile)
- [jane_registry.testing.extractor_manifest](#jane_registrytestingextractor_manifest)
- [jane_registry.testing.extractor_files](#jane_registrytestingextractor_files)
- [jane_registry.testing.publish_body](#jane_registrytestingpublish_body)
- [jane_registry.testing.zip_of](#jane_registrytestingzip_of)
- [jane_registry.testing.run_extractor_from_archive](#jane_registrytestingrun_extractor_from_archive)

## jane_registry.testing.TEST_PROFILE

**Константа.** Код: [services/registry/src/jane_registry/testing.py:30](../../../../../../services/registry/src/jane_registry/testing.py#L30).

```python
TEST_PROFILE: dict[str, Any] = {'profile': 'python-extractor@1', 'description': 'Test copy of the profile format published by handler-runtime (WP-06).', 'python': '3.12', 'libraries': {'lxml': '6.1.3', 'selectolax': '0.3.34', 'beautifulsoup4': '4.15.0'}, 'stdlib': True, 'network': 'none'}
```

## jane_registry.testing.extractor_manifest

**Функція.** Код: [services/registry/src/jane_registry/testing.py:64](../../../../../../services/registry/src/jane_registry/testing.py#L64).

```python
def extractor_manifest(package_id: str, version: str='1.0.0', **overrides: Any) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `package_id` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `'1.0.0'` | positional-or-keyword |
| `overrides` | `Any` | `—` | var-keyword |

Результат: `dict[str, Any]`.

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_api.py:95](../../../../../../services/registry/tests/test_api.py#L95).

```python
manifest_b = extractor_manifest(b)
```

Контекст і передумови: [services/registry/tests/test_api.py:40](../../../../../../services/registry/tests/test_api.py#L40).

```python
body = publish_body(extractor_manifest(package_id, version, **mf), files or extractor_files())
```

## jane_registry.testing.extractor_files

**Функція.** Код: [services/registry/src/jane_registry/testing.py:101](../../../../../../services/registry/src/jane_registry/testing.py#L101).

```python
def extractor_files(main_py: str=MAIN_PY, extra: dict[str, bytes] | None=None) -> dict[str, bytes]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `main_py` | `str` | `MAIN_PY` | positional-or-keyword |
| `extra` | `dict[str, bytes] \| None` | `None` | positional-or-keyword |

Результат: `dict[str, bytes]`.

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_api.py:91](../../../../../../services/registry/tests/test_api.py#L91).

```python
files = extractor_files()
```

Контекст і передумови: [services/registry/tests/test_api.py:189](../../../../../../services/registry/tests/test_api.py#L189).

```python
files = extractor_files()
```

## jane_registry.testing.publish_body

**Функція.** Код: [services/registry/src/jane_registry/testing.py:123](../../../../../../services/registry/src/jane_registry/testing.py#L123).

```python
def publish_body(manifest: dict[str, Any], files: dict[str, bytes]) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `manifest` | `dict[str, Any]` | `—` | positional-or-keyword |
| `files` | `dict[str, bytes]` | `—` | positional-or-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
``PublishRequest`` (registry.v1) from a manifest and files.
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_api.py:40](../../../../../../services/registry/tests/test_api.py#L40).

```python
body = publish_body(extractor_manifest(package_id, version, **mf), files or extractor_files())
```

Контекст і передумови: [services/registry/tests/test_api.py:121](../../../../../../services/registry/tests/test_api.py#L121).

```python
body = publish_body(extractor_manifest(pid), extractor_files())
```

## jane_registry.testing.zip_of

**Функція.** Код: [services/registry/src/jane_registry/testing.py:134](../../../../../../services/registry/src/jane_registry/testing.py#L134).

```python
def zip_of(manifest: dict[str, Any], files: dict[str, bytes], *, deflate: bool=True) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `manifest` | `dict[str, Any]` | `—` | positional-or-keyword |
| `files` | `dict[str, bytes]` | `—` | positional-or-keyword |
| `deflate` | `bool` | `True` | keyword-only |

Результат: `bytes`.

### Опис із вихідного коду

```text
A non-canonical zip as an author might build it (deflated, directory entries, current time).
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_api.py:96](../../../../../../services/registry/tests/test_api.py#L96).

```python
z = client.post(
        f"/v1/packages/{b}/versions",
        content=zip_of(manifest_b, files),
        headers={"Content-Type": "application/zip", **key(f"z-{b}")},
    )
```

Контекст і передумови: [services/registry/tests/test_api.py:200](../../../../../../services/registry/tests/test_api.py#L200).

```python
traversal = client.post(
        f"/v1/packages/{pid}/versions",
        content=zip_of(extractor_manifest(pid), {**extractor_files(), "../evil.py": b"x"}),
        headers={"Content-Type": "application/zip", **key(f"trav-{pid}")},
    )
```

## jane_registry.testing.run_extractor_from_archive

**Функція.** Код: [services/registry/src/jane_registry/testing.py:160](../../../../../../services/registry/src/jane_registry/testing.py#L160).

```python
def run_extractor_from_archive(archive: Path, html: str, timeout_s: float=60.0) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `archive` | `Path` | `—` | positional-or-keyword |
| `html` | `str` | `—` | positional-or-keyword |
| `timeout_s` | `float` | `60.0` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `RuntimeError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Unpack an exported archive and call its entry point in an isolated interpreter (``python -I``):
no registry, no Jane packages on ``sys.path`` - only the archive itself.
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_export.py:153](../../../../../../services/registry/tests/test_export.py#L153).

```python
ran = run_extractor_from_archive(archive, page)
```

Контекст і передумови: [services/registry/tests/test_export.py:161](../../../../../../services/registry/tests/test_export.py#L161).

```python
assert run_extractor_from_archive(archive, "<html>nothing</html>")["result"]["status"] == "empty"
```
