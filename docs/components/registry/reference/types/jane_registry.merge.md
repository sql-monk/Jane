# Модуль `jane_registry.merge`

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry/merge.py](../../../../../services/registry/src/jane_registry/merge.py). Не редагуйте вручну.

Three-way merge for an explicit upstream port (``POST /v1/packages/{id}/upstream-ports``).

* **base** - files of the parent version last ported into the fork (``fork_of.version`` or the latest ``provenance.upstream_port.parent_version`` of the fork's history up to ``base_version``);
* **theirs** - files of the requested parent version;
* **ours** - files of the fork's ``base_version``.

Files: unchanged on one side -> the other side wins; the same change on both sides -> taken once; both sides changed a text file -> line-based merge (merge3 over ``difflib`` matching blocks); overlapping changes, binary changes on both sides, or modify/delete -> conflict.

The manifest is merged as JSON (objects key by key, other values whole). Fork-specific keys (``package_id``, ``version``, ``fork_of``, ``provenance``) always come from the fork and are set by the registry afterwards. Nothing is applied when any conflict exists.

## Зміст

- [Клас `MergeConflict`](#клас-mergeconflict)
- [Клас `MergeResult`](#клас-mergeresult)
- [Функція `merge3_lines`](#функція-merge3_lines)
- [Функція `merge_packages`](#функція-merge_packages)

## Класи

### Клас `MergeConflict`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_registry.merge` |
| Код | [merge.py:35](../../../../../services/registry/src/jane_registry/merge.py#L35) |

```python
@dataclass(frozen=True)
class MergeConflict: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `path` | `str` | — | читання |  |
| `reason` | `str` | — | читання |  |
| `pointer` | `str \| None` | `None` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `MergeConflict.wire`

```python
def wire(self) -> dict[str, str]: ...
```

Код: [merge.py:40](../../../../../services/registry/src/jane_registry/merge.py#L40).

### Клас `MergeResult`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_registry.merge` |
| Код | [merge.py:48](../../../../../services/registry/src/jane_registry/merge.py#L48) |

```python
@dataclass
class MergeResult: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `files` | `dict[str, bytes]` | `field(default_factory=dict)` | читання й запис |  |
| `manifest` | `dict[str, Any]` | `field(default_factory=dict)` | читання й запис |  |
| `conflicts` | `list[MergeConflict]` | `field(default_factory=list)` | читання й запис |  |
| `changed_paths` | `list[str]` | `field(default_factory=list)` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `merge3_lines`

```python
def merge3_lines(
    base: Sequence[str],
    ours: Sequence[str],
    theirs: Sequence[str],
) -> tuple[list[str], int]: ...
```

Merged lines and the number of conflicting hunks (0 = clean).

Код: [merge.py:105](../../../../../services/registry/src/jane_registry/merge.py#L105).

### Функція `merge_packages`

```python
def merge_packages(
    base: Mapping[str, bytes],
    ours: Mapping[str, bytes],
    theirs: Mapping[str, bytes],
    *,
    max_merge_file_bytes: int,
) -> MergeResult: ...
```

Код: [merge.py:158](../../../../../services/registry/src/jane_registry/merge.py#L158).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `FORK_OWNED_KEYS` | — | `frozenset({'package_id', 'version', 'fork_of', 'provenance'})` |  |
