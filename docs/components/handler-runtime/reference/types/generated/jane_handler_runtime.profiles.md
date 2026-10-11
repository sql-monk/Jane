# jane_handler_runtime.profiles

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_handler_runtime.profiles.RuntimeProfile](#jane_handler_runtimeprofilesruntimeprofile)
- [jane_handler_runtime.profiles.RuntimeProfile.__init__](#jane_handler_runtimeprofilesruntimeprofile__init__)
- [jane_handler_runtime.profiles.RuntimeProfile.name](#jane_handler_runtimeprofilesruntimeprofilename)
- [jane_handler_runtime.profiles.RuntimeProfile.python](#jane_handler_runtimeprofilesruntimeprofilepython)
- [jane_handler_runtime.profiles.RuntimeProfile.libraries](#jane_handler_runtimeprofilesruntimeprofilelibraries)
- [jane_handler_runtime.profiles.RuntimeProfile.document](#jane_handler_runtimeprofilesruntimeprofiledocument)
- [jane_handler_runtime.profiles.RuntimeProfile.marker_environment](#jane_handler_runtimeprofilesruntimeprofilemarker_environment)
- [jane_handler_runtime.profiles.RuntimeProfile.version_of](#jane_handler_runtimeprofilesruntimeprofileversion_of)
- [jane_handler_runtime.profiles.DependencyProblem](#jane_handler_runtimeprofilesdependencyproblem)
- [jane_handler_runtime.profiles.DependencyProblem.__init__](#jane_handler_runtimeprofilesdependencyproblem__init__)
- [jane_handler_runtime.profiles.DependencyProblem.requirement](#jane_handler_runtimeprofilesdependencyproblemrequirement)
- [jane_handler_runtime.profiles.DependencyProblem.message](#jane_handler_runtimeprofilesdependencyproblemmessage)
- [jane_handler_runtime.profiles.load_profiles](#jane_handler_runtimeprofilesload_profiles)
- [jane_handler_runtime.profiles.check_dependencies](#jane_handler_runtimeprofilescheck_dependencies)

## jane_handler_runtime.profiles.RuntimeProfile

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py:25](../../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L25).

```python
class RuntimeProfile:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_handler_runtime.profiles.md#jane_handler_runtimeprofilesruntimeprofilename) | Поле | ні |
| [python](jane_handler_runtime.profiles.md#jane_handler_runtimeprofilesruntimeprofilepython) | Поле | ні |
| [libraries](jane_handler_runtime.profiles.md#jane_handler_runtimeprofilesruntimeprofilelibraries) | Поле | ні |
| [document](jane_handler_runtime.profiles.md#jane_handler_runtimeprofilesruntimeprofiledocument) | Поле | ні |
| [marker_environment](jane_handler_runtime.profiles.md#jane_handler_runtimeprofilesruntimeprofilemarker_environment) | Метод | ні |
| [version_of](jane_handler_runtime.profiles.md#jane_handler_runtimeprofilesruntimeprofileversion_of) | Метод | ні |
| [__init__](jane_handler_runtime.profiles.md#jane_handler_runtimeprofilesruntimeprofile__init__) | Конструктор dataclass | ні |

## jane_handler_runtime.profiles.RuntimeProfile.__init__

**Конструктор dataclass.** Код: [services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py:25](../../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L25).

```python
def __init__(self, name: str, python: str, libraries: Mapping[str, str], document: Mapping[str, Any]) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `name` | `str` | `—` | positional-or-keyword |
| `python` | `str` | `—` | positional-or-keyword |
| `libraries` | `Mapping[str, str]` | `—` | positional-or-keyword |
| `document` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_handler_runtime.profiles.RuntimeProfile.name

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py:26](../../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L26).

```python
name: str
```

Доступ: читання — так; запис — ні.

## jane_handler_runtime.profiles.RuntimeProfile.python

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py:27](../../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L27).

```python
python: str
```

Доступ: читання — так; запис — ні.

## jane_handler_runtime.profiles.RuntimeProfile.libraries

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py:28](../../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L28).

```python
libraries: Mapping[str, str]
```

Доступ: читання — так; запис — ні.

## jane_handler_runtime.profiles.RuntimeProfile.document

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py:29](../../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L29).

```python
document: Mapping[str, Any]
```

Доступ: читання — так; запис — ні.

## jane_handler_runtime.profiles.RuntimeProfile.marker_environment

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py:31](../../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L31).

```python
def marker_environment(self) -> dict[str, str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, str]`.

### Опис із вихідного коду

```text
PEP 508 marker values of the sandbox (Linux container), not of the host running the runtime.
```

## jane_handler_runtime.profiles.RuntimeProfile.version_of

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py:43](../../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L43).

```python
def version_of(self, distribution: str) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `distribution` | `str` | `—` | positional-or-keyword |

Результат: `str | None`.

## jane_handler_runtime.profiles.DependencyProblem

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py:52](../../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L52).

```python
class DependencyProblem:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [requirement](jane_handler_runtime.profiles.md#jane_handler_runtimeprofilesdependencyproblemrequirement) | Поле | ні |
| [message](jane_handler_runtime.profiles.md#jane_handler_runtimeprofilesdependencyproblemmessage) | Поле | ні |
| [__init__](jane_handler_runtime.profiles.md#jane_handler_runtimeprofilesdependencyproblem__init__) | Конструктор dataclass | ні |

## jane_handler_runtime.profiles.DependencyProblem.__init__

**Конструктор dataclass.** Код: [services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py:52](../../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L52).

```python
def __init__(self, requirement: str, message: str) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `requirement` | `str` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_handler_runtime.profiles.DependencyProblem.requirement

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py:53](../../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L53).

```python
requirement: str
```

Доступ: читання — так; запис — ні.

## jane_handler_runtime.profiles.DependencyProblem.message

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py:54](../../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L54).

```python
message: str
```

Доступ: читання — так; запис — ні.

## jane_handler_runtime.profiles.load_profiles

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py:58](../../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L58).

```python
def load_profiles() -> dict[str, RuntimeProfile]:
```

Декоратори: `cache`.

Результат: `dict[str, RuntimeProfile]`.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_isolation.py:234](../../../../../../services/handler-runtime/tests/test_isolation.py#L234).

```python
libraries = dict(load_profiles()["python-extractor@1"].libraries)
```

Контекст і передумови: [services/handler-runtime/tests/test_units.py:20](../../../../../../services/handler-runtime/tests/test_units.py#L20).

```python
profile = load_profiles()["python-extractor@1"]
```

## jane_handler_runtime.profiles.check_dependencies

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py:67](../../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L67).

```python
def check_dependencies(profile: RuntimeProfile, requirements: Sequence[str]) -> list[DependencyProblem]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `profile` | `RuntimeProfile` | `—` | positional-or-keyword |
| `requirements` | `Sequence[str]` | `—` | positional-or-keyword |

Результат: `list[DependencyProblem]`.

### Опис із вихідного коду

```text
PEP 508 requirements of a manifest vs the exact versions of the profile.
```

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_units.py:46](../../../../../../services/handler-runtime/tests/test_units.py#L46).

```python
problems = check_dependencies(load_profiles()["python-extractor@1"], [requirement])
```
