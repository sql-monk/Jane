# Модуль `jane_registry.testing`

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry/testing.py](../../../../../services/registry/src/jane_registry/testing.py). Не редагуйте вручну.

Helpers for tests of the registry and of its clients: sample packages and a test runtime profile.

The sample extractor has no dependency on the extractor SDK, so an exported archive can be executed by a plain Python interpreter (``run_extractor_from_archive``) without the registry or other Jane services.

## Зміст

- [Функція `extractor_files`](#функція-extractor_files)
- [Функція `extractor_manifest`](#функція-extractor_manifest)
- [Функція `publish_body`](#функція-publish_body)
- [Функція `run_extractor_from_archive`](#функція-run_extractor_from_archive)
- [Функція `zip_of`](#функція-zip_of)

## Функції

### Функція `extractor_files`

```python
def extractor_files(
    main_py: str = MAIN_PY,
    extra: dict[str, bytes] | None = None,
) -> dict[str, bytes]: ...
```

Код: [testing.py:101](../../../../../services/registry/src/jane_registry/testing.py#L101).

### Функція `extractor_manifest`

```python
def extractor_manifest(
    package_id: str,
    version: str = '1.0.0',
    **overrides: Any,
) -> dict[str, Any]: ...
```

Код: [testing.py:64](../../../../../services/registry/src/jane_registry/testing.py#L64).

### Функція `publish_body`

```python
def publish_body(manifest: dict[str, Any], files: dict[str, bytes]) -> dict[str, Any]: ...
```

``PublishRequest`` (registry.v1) from a manifest and files.

Код: [testing.py:123](../../../../../services/registry/src/jane_registry/testing.py#L123).

### Функція `run_extractor_from_archive`

```python
def run_extractor_from_archive(
    archive: Path,
    html: str,
    timeout_s: float = 60.0,
) -> dict[str, Any]: ...
```

Unpack an exported archive and call its entry point in an isolated interpreter (``python -I``): no registry, no Jane packages on ``sys.path`` - only the archive itself.

Винятки в коді функції: `RuntimeError`.

Код: [testing.py:160](../../../../../services/registry/src/jane_registry/testing.py#L160).

### Функція `zip_of`

```python
def zip_of(manifest: dict[str, Any], files: dict[str, bytes], *, deflate: bool = True) -> bytes: ...
```

A non-canonical zip as an author might build it (deflated, directory entries, current time).

Код: [testing.py:134](../../../../../services/registry/src/jane_registry/testing.py#L134).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `TEST_PROFILE` | `dict[str, Any]` | `{'profile': 'python-extractor@1', 'description': 'Test copy of the profile forma` |  |
