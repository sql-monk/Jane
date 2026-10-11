# jane_registry.semver

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_registry.semver.SEMVER_RE](#jane_registrysemversemver_re)
- [jane_registry.semver.SemVer](#jane_registrysemversemver)
- [jane_registry.semver.SemVer.__init__](#jane_registrysemversemver__init__)
- [jane_registry.semver.SemVer.raw](#jane_registrysemversemverraw)
- [jane_registry.semver.SemVer.core](#jane_registrysemversemvercore)
- [jane_registry.semver.SemVer.pre](#jane_registrysemversemverpre)
- [jane_registry.semver.SemVer.build](#jane_registrysemversemverbuild)
- [jane_registry.semver.SemVer.__eq__](#jane_registrysemversemver__eq__)
- [jane_registry.semver.SemVer.__hash__](#jane_registrysemversemver__hash__)
- [jane_registry.semver.SemVer.__str__](#jane_registrysemversemver__str__)
- [jane_registry.semver.is_semver](#jane_registrysemveris_semver)
- [jane_registry.semver.sort_versions](#jane_registrysemversort_versions)
- [jane_registry.semver.max_version](#jane_registrysemvermax_version)

## jane_registry.semver.SEMVER_RE

**Константа.** Код: [services/registry/src/jane_registry/semver.py:10](../../../../../../services/registry/src/jane_registry/semver.py#L10).

```python
SEMVER_RE = re.compile('^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)(?:-([0-9A-Za-z.-]+))?(?:\\+([0-9A-Za-z.-]+))?$')
```

## jane_registry.semver.SemVer

**Клас.** Код: [services/registry/src/jane_registry/semver.py:42](../../../../../../services/registry/src/jane_registry/semver.py#L42).

```python
class SemVer:
```

Декоратори: `total_ordering`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_registry.semver.md#jane_registrysemversemver__init__) | Конструктор | ні |
| [raw](jane_registry.semver.md#jane_registrysemversemverraw) | Поле екземпляра | ні |
| [core](jane_registry.semver.md#jane_registrysemversemvercore) | Поле екземпляра | ні |
| [pre](jane_registry.semver.md#jane_registrysemversemverpre) | Поле екземпляра | ні |
| [build](jane_registry.semver.md#jane_registrysemversemverbuild) | Поле екземпляра | ні |
| [__eq__](jane_registry.semver.md#jane_registrysemversemver__eq__) | Метод | ні |
| [__hash__](jane_registry.semver.md#jane_registrysemversemver__hash__) | Метод | ні |
| [__str__](jane_registry.semver.md#jane_registrysemversemver__str__) | Метод | ні |

### Опис із вихідного коду

```text
Parsed version; build metadata is ignored for ordering (SemVer §10).
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_units.py:398](../../../../../../services/registry/tests/test_units.py#L398).

```python
assert SemVer("1.0.0+a") == SemVer("1.0.0+b")
```

Контекст і передумови: [services/registry/tests/test_units.py:400](../../../../../../services/registry/tests/test_units.py#L400).

```python
SemVer("latest")
```

## jane_registry.semver.SemVer.__init__

**Конструктор.** Код: [services/registry/src/jane_registry/semver.py:47](../../../../../../services/registry/src/jane_registry/semver.py#L47).

```python
def __init__(self, raw: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `raw` | `str` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_units.py:398](../../../../../../services/registry/tests/test_units.py#L398).

```python
assert SemVer("1.0.0+a") == SemVer("1.0.0+b")
```

Контекст і передумови: [services/registry/tests/test_units.py:400](../../../../../../services/registry/tests/test_units.py#L400).

```python
SemVer("latest")
```

## jane_registry.semver.SemVer.raw

**Поле екземпляра.** Код: [services/registry/src/jane_registry/semver.py:51](../../../../../../services/registry/src/jane_registry/semver.py#L51).

```python
self.raw = raw
```

## jane_registry.semver.SemVer.core

**Поле екземпляра.** Код: [services/registry/src/jane_registry/semver.py:52](../../../../../../services/registry/src/jane_registry/semver.py#L52).

```python
self.core = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
```

## jane_registry.semver.SemVer.pre

**Поле екземпляра.** Код: [services/registry/src/jane_registry/semver.py:53](../../../../../../services/registry/src/jane_registry/semver.py#L53).

```python
self.pre = tuple((_Ident(p) for p in m.group(4).split('.'))) if m.group(4) else ()
```

## jane_registry.semver.SemVer.build

**Поле екземпляра.** Код: [services/registry/src/jane_registry/semver.py:54](../../../../../../services/registry/src/jane_registry/semver.py#L54).

```python
self.build = m.group(5)
```

## jane_registry.semver.SemVer.__eq__

**Метод.** Код: [services/registry/src/jane_registry/semver.py:60](../../../../../../services/registry/src/jane_registry/semver.py#L60).

```python
def __eq__(self, other: object) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `other` | `object` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_registry.semver.SemVer.__hash__

**Метод.** Код: [services/registry/src/jane_registry/semver.py:63](../../../../../../services/registry/src/jane_registry/semver.py#L63).

```python
def __hash__(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

## jane_registry.semver.SemVer.__str__

**Метод.** Код: [services/registry/src/jane_registry/semver.py:69](../../../../../../services/registry/src/jane_registry/semver.py#L69).

```python
def __str__(self) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

## jane_registry.semver.is_semver

**Функція.** Код: [services/registry/src/jane_registry/semver.py:73](../../../../../../services/registry/src/jane_registry/semver.py#L73).

```python
def is_semver(raw: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `raw` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_registry.semver.sort_versions

**Функція.** Код: [services/registry/src/jane_registry/semver.py:77](../../../../../../services/registry/src/jane_registry/semver.py#L77).

```python
def sort_versions(versions: list[str], *, reverse: bool=False) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `versions` | `list[str]` | `—` | positional-or-keyword |
| `reverse` | `bool` | `False` | keyword-only |

Результат: `list[str]`.

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_units.py:386](../../../../../../services/registry/tests/test_units.py#L386).

```python
assert sort_versions(versions) == [
        "0.9.9",
        "1.0.0-alpha",
        "1.0.0-alpha.1",
        "1.0.0-beta.2",
        "1.0.0-beta.11",
        "1.0.0-rc.1",
        "1.0.0",
        "1.2.0+build",
        "1.10.0",
    ]
```

## jane_registry.semver.max_version

**Функція.** Код: [services/registry/src/jane_registry/semver.py:81](../../../../../../services/registry/src/jane_registry/semver.py#L81).

```python
def max_version(versions: list[str]) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `versions` | `list[str]` | `—` | positional-or-keyword |

Результат: `str | None`.

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_units.py:397](../../../../../../services/registry/tests/test_units.py#L397).

```python
assert max_version(["1.2.0", "1.10.0", "1.9.9"]) == "1.10.0"
```
