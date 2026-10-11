# Модуль `jane_registry.semver`

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry/semver.py](../../../../../services/registry/src/jane_registry/semver.py). Не редагуйте вручну.

Semantic Versioning 2.0.0 ordering (``SemVer`` of the contracts: exact versions, no ranges).

## Зміст

- [Клас `SemVer`](#клас-semver)
- [Функція `is_semver`](#функція-is_semver)
- [Функція `max_version`](#функція-max_version)
- [Функція `sort_versions`](#функція-sort_versions)

## Класи

### Клас `SemVer`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.semver` |
| Код | [semver.py:42](../../../../../services/registry/src/jane_registry/semver.py#L42) |

```python
@total_ordering
class SemVer: ...
```

Parsed version; build metadata is ignored for ordering (SemVer §10).

#### Конструктор `SemVer.__init__`

```python
def __init__(self, raw: str) -> None: ...
```

Винятки в коді методу: `ValueError`.

Код: [semver.py:47](../../../../../services/registry/src/jane_registry/semver.py#L47).

## Функції

### Функція `is_semver`

```python
def is_semver(raw: str) -> bool: ...
```

Код: [semver.py:73](../../../../../services/registry/src/jane_registry/semver.py#L73).

### Функція `max_version`

```python
def max_version(versions: list[str]) -> str | None: ...
```

Код: [semver.py:81](../../../../../services/registry/src/jane_registry/semver.py#L81).

### Функція `sort_versions`

```python
def sort_versions(versions: list[str], *, reverse: bool = False) -> list[str]: ...
```

Код: [semver.py:77](../../../../../services/registry/src/jane_registry/semver.py#L77).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `SEMVER_RE` | — | `re.compile('^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-([0-9A-Za-z.` |  |
