# jane_registry.merge

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_registry.merge.FORK_OWNED_KEYS](#jane_registrymergefork_owned_keys)
- [jane_registry.merge.MergeConflict](#jane_registrymergemergeconflict)
- [jane_registry.merge.MergeConflict.__init__](#jane_registrymergemergeconflict__init__)
- [jane_registry.merge.MergeConflict.path](#jane_registrymergemergeconflictpath)
- [jane_registry.merge.MergeConflict.reason](#jane_registrymergemergeconflictreason)
- [jane_registry.merge.MergeConflict.pointer](#jane_registrymergemergeconflictpointer)
- [jane_registry.merge.MergeConflict.wire](#jane_registrymergemergeconflictwire)
- [jane_registry.merge.MergeResult](#jane_registrymergemergeresult)
- [jane_registry.merge.MergeResult.__init__](#jane_registrymergemergeresult__init__)
- [jane_registry.merge.MergeResult.files](#jane_registrymergemergeresultfiles)
- [jane_registry.merge.MergeResult.manifest](#jane_registrymergemergeresultmanifest)
- [jane_registry.merge.MergeResult.conflicts](#jane_registrymergemergeresultconflicts)
- [jane_registry.merge.MergeResult.changed_paths](#jane_registrymergemergeresultchanged_paths)
- [jane_registry.merge.merge3_lines](#jane_registrymergemerge3_lines)
- [jane_registry.merge.merge_packages](#jane_registrymergemerge_packages)

## jane_registry.merge.FORK_OWNED_KEYS

**Константа.** Код: [services/registry/src/jane_registry/merge.py:30](../../../../../../services/registry/src/jane_registry/merge.py#L30).

```python
FORK_OWNED_KEYS = frozenset({'package_id', 'version', 'fork_of', 'provenance'})
```

## jane_registry.merge.MergeConflict

**Клас.** Код: [services/registry/src/jane_registry/merge.py:35](../../../../../../services/registry/src/jane_registry/merge.py#L35).

```python
class MergeConflict:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [path](jane_registry.merge.md#jane_registrymergemergeconflictpath) | Поле | ні |
| [reason](jane_registry.merge.md#jane_registrymergemergeconflictreason) | Поле | ні |
| [pointer](jane_registry.merge.md#jane_registrymergemergeconflictpointer) | Поле | ні |
| [wire](jane_registry.merge.md#jane_registrymergemergeconflictwire) | Метод | ні |
| [__init__](jane_registry.merge.md#jane_registrymergemergeconflict__init__) | Конструктор dataclass | ні |

## jane_registry.merge.MergeConflict.__init__

**Конструктор dataclass.** Код: [services/registry/src/jane_registry/merge.py:35](../../../../../../services/registry/src/jane_registry/merge.py#L35).

```python
def __init__(self, path: str, reason: str, pointer: str | None = None) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `path` | `str` | `—` | positional-or-keyword |
| `reason` | `str` | `—` | positional-or-keyword |
| `pointer` | `str \| None` | `None` | positional-or-keyword |

Результат: `None`.

## jane_registry.merge.MergeConflict.path

**Поле.** Код: [services/registry/src/jane_registry/merge.py:36](../../../../../../services/registry/src/jane_registry/merge.py#L36).

```python
path: str
```

Доступ: читання — так; запис — ні.

## jane_registry.merge.MergeConflict.reason

**Поле.** Код: [services/registry/src/jane_registry/merge.py:37](../../../../../../services/registry/src/jane_registry/merge.py#L37).

```python
reason: str
```

Доступ: читання — так; запис — ні.

## jane_registry.merge.MergeConflict.pointer

**Поле.** Код: [services/registry/src/jane_registry/merge.py:38](../../../../../../services/registry/src/jane_registry/merge.py#L38).

```python
pointer: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_registry.merge.MergeConflict.wire

**Метод.** Код: [services/registry/src/jane_registry/merge.py:40](../../../../../../services/registry/src/jane_registry/merge.py#L40).

```python
def wire(self) -> dict[str, str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, str]`.

## jane_registry.merge.MergeResult

**Клас.** Код: [services/registry/src/jane_registry/merge.py:48](../../../../../../services/registry/src/jane_registry/merge.py#L48).

```python
class MergeResult:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [files](jane_registry.merge.md#jane_registrymergemergeresultfiles) | Поле | ні |
| [manifest](jane_registry.merge.md#jane_registrymergemergeresultmanifest) | Поле | ні |
| [conflicts](jane_registry.merge.md#jane_registrymergemergeresultconflicts) | Поле | ні |
| [changed_paths](jane_registry.merge.md#jane_registrymergemergeresultchanged_paths) | Поле | ні |
| [__init__](jane_registry.merge.md#jane_registrymergemergeresult__init__) | Конструктор dataclass | ні |

## jane_registry.merge.MergeResult.__init__

**Конструктор dataclass.** Код: [services/registry/src/jane_registry/merge.py:48](../../../../../../services/registry/src/jane_registry/merge.py#L48).

```python
def __init__(self, files: dict[str, bytes] = <factory dict>, manifest: dict[str, Any] = <factory dict>, conflicts: list[MergeConflict] = <factory list>, changed_paths: list[str] = <factory list>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `files` | `dict[str, bytes]` | `factory: dict` | positional-or-keyword |
| `manifest` | `dict[str, Any]` | `factory: dict` | positional-or-keyword |
| `conflicts` | `list[MergeConflict]` | `factory: list` | positional-or-keyword |
| `changed_paths` | `list[str]` | `factory: list` | positional-or-keyword |

Результат: `None`.

## jane_registry.merge.MergeResult.files

**Поле.** Код: [services/registry/src/jane_registry/merge.py:49](../../../../../../services/registry/src/jane_registry/merge.py#L49).

```python
files: dict[str, bytes] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_registry.merge.MergeResult.manifest

**Поле.** Код: [services/registry/src/jane_registry/merge.py:50](../../../../../../services/registry/src/jane_registry/merge.py#L50).

```python
manifest: dict[str, Any] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_registry.merge.MergeResult.conflicts

**Поле.** Код: [services/registry/src/jane_registry/merge.py:51](../../../../../../services/registry/src/jane_registry/merge.py#L51).

```python
conflicts: list[MergeConflict] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_registry.merge.MergeResult.changed_paths

**Поле.** Код: [services/registry/src/jane_registry/merge.py:52](../../../../../../services/registry/src/jane_registry/merge.py#L52).

```python
changed_paths: list[str] = field(default_factory=list)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "list"
}
```

## jane_registry.merge.merge3_lines

**Функція.** Код: [services/registry/src/jane_registry/merge.py:105](../../../../../../services/registry/src/jane_registry/merge.py#L105).

```python
def merge3_lines(base: Sequence[str], ours: Sequence[str], theirs: Sequence[str]) -> tuple[list[str], int]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `base` | `Sequence[str]` | `—` | positional-or-keyword |
| `ours` | `Sequence[str]` | `—` | positional-or-keyword |
| `theirs` | `Sequence[str]` | `—` | positional-or-keyword |

Результат: `tuple[list[str], int]`.

### Опис із вихідного коду

```text
Merged lines and the number of conflicting hunks (0 = clean).
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_units.py:307](../../../../../../services/registry/tests/test_units.py#L307).

```python
assert merge3_lines(base, ours, theirs) == (["a\n", "B\n", "c\n", "D\n"], 0)
```

Контекст і передумови: [services/registry/tests/test_units.py:308](../../../../../../services/registry/tests/test_units.py#L308).

```python
assert merge3_lines(base, ours, ours) == (ours, 0)
```

## jane_registry.merge.merge_packages

**Функція.** Код: [services/registry/src/jane_registry/merge.py:158](../../../../../../services/registry/src/jane_registry/merge.py#L158).

```python
def merge_packages(base: Mapping[str, bytes], ours: Mapping[str, bytes], theirs: Mapping[str, bytes], *, max_merge_file_bytes: int) -> MergeResult:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `base` | `Mapping[str, bytes]` | `—` | positional-or-keyword |
| `ours` | `Mapping[str, bytes]` | `—` | positional-or-keyword |
| `theirs` | `Mapping[str, bytes]` | `—` | positional-or-keyword |
| `max_merge_file_bytes` | `int` | `—` | keyword-only |

Результат: `MergeResult`.

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_units.py:336](../../../../../../services/registry/tests/test_units.py#L336).

```python
r = merge_packages(base, ours, theirs, max_merge_file_bytes=1000)
```

Контекст і передумови: [services/registry/tests/test_units.py:341](../../../../../../services/registry/tests/test_units.py#L341).

```python
conflict = merge_packages(
        base,
        _pkg(m, src__a=b"3\n", src__bin=b"\0\2", src__gone=b"changed"),
        _pkg({**m, "title": "X"}, src__a=b"4\n", src__bin=b"\0\3"),
        max_merge_file_bytes=1000,
    )
```
