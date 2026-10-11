# jane_registry.secrets

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_registry.secrets.SecretFinding](#jane_registrysecretssecretfinding)
- [jane_registry.secrets.SecretFinding.__init__](#jane_registrysecretssecretfinding__init__)
- [jane_registry.secrets.SecretFinding.path](#jane_registrysecretssecretfindingpath)
- [jane_registry.secrets.SecretFinding.code](#jane_registrysecretssecretfindingcode)
- [jane_registry.secrets.SecretFinding.message](#jane_registrysecretssecretfindingmessage)
- [jane_registry.secrets.SecretFinding.line](#jane_registrysecretssecretfindingline)
- [jane_registry.secrets.SecretFinding.pointer](#jane_registrysecretssecretfindingpointer)
- [jane_registry.secrets.ScanBudgetExceeded](#jane_registrysecretsscanbudgetexceeded)
- [jane_registry.secrets.ScanBudgetExceeded.__init__](#jane_registrysecretsscanbudgetexceeded__init__)
- [jane_registry.secrets.ScanBudgetExceeded.budget_ms](#jane_registrysecretsscanbudgetexceededbudget_ms)
- [jane_registry.secrets.ScanBudgetExceeded.path](#jane_registrysecretsscanbudgetexceededpath)
- [jane_registry.secrets.oversized_files](#jane_registrysecretsoversized_files)
- [jane_registry.secrets.scan_files](#jane_registrysecretsscan_files)

## jane_registry.secrets.SecretFinding

**Клас.** Код: [services/registry/src/jane_registry/secrets.py:46](../../../../../../services/registry/src/jane_registry/secrets.py#L46).

```python
class SecretFinding:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [path](jane_registry.secrets.md#jane_registrysecretssecretfindingpath) | Поле | ні |
| [code](jane_registry.secrets.md#jane_registrysecretssecretfindingcode) | Поле | ні |
| [message](jane_registry.secrets.md#jane_registrysecretssecretfindingmessage) | Поле | ні |
| [line](jane_registry.secrets.md#jane_registrysecretssecretfindingline) | Поле | ні |
| [pointer](jane_registry.secrets.md#jane_registrysecretssecretfindingpointer) | Властивість | ні |
| [__init__](jane_registry.secrets.md#jane_registrysecretssecretfinding__init__) | Конструктор dataclass | ні |

## jane_registry.secrets.SecretFinding.__init__

**Конструктор dataclass.** Код: [services/registry/src/jane_registry/secrets.py:46](../../../../../../services/registry/src/jane_registry/secrets.py#L46).

```python
def __init__(self, path: str, code: str, message: str, line: int | None = None) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `path` | `str` | `—` | positional-or-keyword |
| `code` | `str` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |
| `line` | `int \| None` | `None` | positional-or-keyword |

Результат: `None`.

## jane_registry.secrets.SecretFinding.path

**Поле.** Код: [services/registry/src/jane_registry/secrets.py:47](../../../../../../services/registry/src/jane_registry/secrets.py#L47).

```python
path: str
```

Доступ: читання — так; запис — ні.

## jane_registry.secrets.SecretFinding.code

**Поле.** Код: [services/registry/src/jane_registry/secrets.py:48](../../../../../../services/registry/src/jane_registry/secrets.py#L48).

```python
code: str
```

Доступ: читання — так; запис — ні.

## jane_registry.secrets.SecretFinding.message

**Поле.** Код: [services/registry/src/jane_registry/secrets.py:49](../../../../../../services/registry/src/jane_registry/secrets.py#L49).

```python
message: str
```

Доступ: читання — так; запис — ні.

## jane_registry.secrets.SecretFinding.line

**Поле.** Код: [services/registry/src/jane_registry/secrets.py:50](../../../../../../services/registry/src/jane_registry/secrets.py#L50).

```python
line: int | None = None
```

Доступ: читання — так; запис — ні.

## jane_registry.secrets.SecretFinding.pointer

**Властивість.** Код: [services/registry/src/jane_registry/secrets.py:53](../../../../../../services/registry/src/jane_registry/secrets.py#L53).

```python
def pointer(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## jane_registry.secrets.ScanBudgetExceeded

**Клас.** Код: [services/registry/src/jane_registry/secrets.py:57](../../../../../../services/registry/src/jane_registry/secrets.py#L57).

```python
class ScanBudgetExceeded(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_registry.secrets.md#jane_registrysecretsscanbudgetexceeded__init__) | Конструктор | ні |
| [budget_ms](jane_registry.secrets.md#jane_registrysecretsscanbudgetexceededbudget_ms) | Поле екземпляра | ні |
| [path](jane_registry.secrets.md#jane_registrysecretsscanbudgetexceededpath) | Поле екземпляра | ні |

### Опис із вихідного коду

```text
Scanning took longer than ``secrets.scan_time_budget_ms`` (the publish is refused).
```

## jane_registry.secrets.ScanBudgetExceeded.__init__

**Конструктор.** Код: [services/registry/src/jane_registry/secrets.py:60](../../../../../../services/registry/src/jane_registry/secrets.py#L60).

```python
def __init__(self, budget_ms: int, path: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `budget_ms` | `int` | `—` | positional-or-keyword |
| `path` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.secrets.ScanBudgetExceeded.budget_ms

**Поле екземпляра.** Код: [services/registry/src/jane_registry/secrets.py:62](../../../../../../services/registry/src/jane_registry/secrets.py#L62).

```python
self.budget_ms = budget_ms
```

## jane_registry.secrets.ScanBudgetExceeded.path

**Поле екземпляра.** Код: [services/registry/src/jane_registry/secrets.py:63](../../../../../../services/registry/src/jane_registry/secrets.py#L63).

```python
self.path = path
```

## jane_registry.secrets.oversized_files

**Функція.** Код: [services/registry/src/jane_registry/secrets.py:456](../../../../../../services/registry/src/jane_registry/secrets.py#L456).

```python
def oversized_files(files: Mapping[str, bytes], limits: SecretScanLimits) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `files` | `Mapping[str, bytes]` | `—` | positional-or-keyword |
| `limits` | `SecretScanLimits` | `—` | positional-or-keyword |

Результат: `list[str]`.

### Опис із вихідного коду

```text
Files the scanner would not read completely (the publish must be refused).
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_units.py:239](../../../../../../services/registry/tests/test_units.py#L239).

```python
assert oversized_files(files, limits) == ["src/pad.py"]
```

## jane_registry.secrets.scan_files

**Функція.** Код: [services/registry/src/jane_registry/secrets.py:461](../../../../../../services/registry/src/jane_registry/secrets.py#L461).

```python
def scan_files(files: Mapping[str, bytes], limits: SecretScanLimits) -> list[SecretFinding]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `files` | `Mapping[str, bytes]` | `—` | positional-or-keyword |
| `limits` | `SecretScanLimits` | `—` | positional-or-keyword |

Результат: `list[SecretFinding]`.

### Опис із вихідного коду

```text
All findings, sorted by path and line. Callers reject :func:`oversized_files` first.

Raises :class:`ScanBudgetExceeded` when the whole scan takes longer than ``secrets.scan_time_budget_ms``
(checked between detectors and every few hundred matches - a safeguard on top of the linear patterns).
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_units.py:169](../../../../../../services/registry/tests/test_units.py#L169).

```python
assert scan_files(files, SecretScanLimits()) == []
```

Контекст і передумови: [services/registry/tests/test_units.py:409](../../../../../../services/registry/tests/test_units.py#L409).

```python
scan_files({path: data}, limits)
```
