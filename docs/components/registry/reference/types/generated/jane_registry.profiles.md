# jane_registry.profiles

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_registry.profiles.RuntimeProfile](#jane_registryprofilesruntimeprofile)
- [jane_registry.profiles.RuntimeProfile.__init__](#jane_registryprofilesruntimeprofile__init__)
- [jane_registry.profiles.RuntimeProfile.name](#jane_registryprofilesruntimeprofilename)
- [jane_registry.profiles.RuntimeProfile.python](#jane_registryprofilesruntimeprofilepython)
- [jane_registry.profiles.RuntimeProfile.libraries](#jane_registryprofilesruntimeprofilelibraries)
- [jane_registry.profiles.RuntimeProfile.marker_environment](#jane_registryprofilesruntimeprofilemarker_environment)
- [jane_registry.profiles.RuntimeProfile.version_of](#jane_registryprofilesruntimeprofileversion_of)
- [jane_registry.profiles.DependencyProblem](#jane_registryprofilesdependencyproblem)
- [jane_registry.profiles.DependencyProblem.__init__](#jane_registryprofilesdependencyproblem__init__)
- [jane_registry.profiles.DependencyProblem.index](#jane_registryprofilesdependencyproblemindex)
- [jane_registry.profiles.DependencyProblem.requirement](#jane_registryprofilesdependencyproblemrequirement)
- [jane_registry.profiles.DependencyProblem.message](#jane_registryprofilesdependencyproblemmessage)
- [jane_registry.profiles.parse_profiles](#jane_registryprofilesparse_profiles)
- [jane_registry.profiles.ProfileSource](#jane_registryprofilesprofilesource)
- [jane_registry.profiles.ProfileSource.__init__](#jane_registryprofilesprofilesource__init__)
- [jane_registry.profiles.ProfileSource.sources](#jane_registryprofilesprofilesourcesources)
- [jane_registry.profiles.ProfileSource.limits](#jane_registryprofilesprofilesourcelimits)
- [jane_registry.profiles.ProfileSource.transport](#jane_registryprofilesprofilesourcetransport)
- [jane_registry.profiles.ProfileSource.errors](#jane_registryprofilesprofilesourceerrors)
- [jane_registry.profiles.ProfileSource.known](#jane_registryprofilesprofilesourceknown)
- [jane_registry.profiles.ProfileSource.profiles](#jane_registryprofilesprofilesourceprofiles)
- [jane_registry.profiles.check_dependencies](#jane_registryprofilescheck_dependencies)

## jane_registry.profiles.RuntimeProfile

**Клас.** Код: [services/registry/src/jane_registry/profiles.py:39](../../../../../../services/registry/src/jane_registry/profiles.py#L39).

```python
class RuntimeProfile:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_registry.profiles.md#jane_registryprofilesruntimeprofilename) | Поле | ні |
| [python](jane_registry.profiles.md#jane_registryprofilesruntimeprofilepython) | Поле | ні |
| [libraries](jane_registry.profiles.md#jane_registryprofilesruntimeprofilelibraries) | Поле | ні |
| [marker_environment](jane_registry.profiles.md#jane_registryprofilesruntimeprofilemarker_environment) | Метод | ні |
| [version_of](jane_registry.profiles.md#jane_registryprofilesruntimeprofileversion_of) | Метод | ні |
| [__init__](jane_registry.profiles.md#jane_registryprofilesruntimeprofile__init__) | Конструктор dataclass | ні |

## jane_registry.profiles.RuntimeProfile.__init__

**Конструктор dataclass.** Код: [services/registry/src/jane_registry/profiles.py:39](../../../../../../services/registry/src/jane_registry/profiles.py#L39).

```python
def __init__(self, name: str, python: str, libraries: Mapping[str, str]) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `name` | `str` | `—` | positional-or-keyword |
| `python` | `str` | `—` | positional-or-keyword |
| `libraries` | `Mapping[str, str]` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.profiles.RuntimeProfile.name

**Поле.** Код: [services/registry/src/jane_registry/profiles.py:40](../../../../../../services/registry/src/jane_registry/profiles.py#L40).

```python
name: str
```

Доступ: читання — так; запис — ні.

## jane_registry.profiles.RuntimeProfile.python

**Поле.** Код: [services/registry/src/jane_registry/profiles.py:41](../../../../../../services/registry/src/jane_registry/profiles.py#L41).

```python
python: str
```

Доступ: читання — так; запис — ні.

## jane_registry.profiles.RuntimeProfile.libraries

**Поле.** Код: [services/registry/src/jane_registry/profiles.py:42](../../../../../../services/registry/src/jane_registry/profiles.py#L42).

```python
libraries: Mapping[str, str]
```

Доступ: читання — так; запис — ні.

## jane_registry.profiles.RuntimeProfile.marker_environment

**Метод.** Код: [services/registry/src/jane_registry/profiles.py:44](../../../../../../services/registry/src/jane_registry/profiles.py#L44).

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
PEP 508 marker values of the sandbox (a Linux container), not of the registry host.
```

## jane_registry.profiles.RuntimeProfile.version_of

**Метод.** Код: [services/registry/src/jane_registry/profiles.py:56](../../../../../../services/registry/src/jane_registry/profiles.py#L56).

```python
def version_of(self, distribution: str) -> str | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `distribution` | `str` | `—` | positional-or-keyword |

Результат: `str | None`.

## jane_registry.profiles.DependencyProblem

**Клас.** Код: [services/registry/src/jane_registry/profiles.py:65](../../../../../../services/registry/src/jane_registry/profiles.py#L65).

```python
class DependencyProblem:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [index](jane_registry.profiles.md#jane_registryprofilesdependencyproblemindex) | Поле | ні |
| [requirement](jane_registry.profiles.md#jane_registryprofilesdependencyproblemrequirement) | Поле | ні |
| [message](jane_registry.profiles.md#jane_registryprofilesdependencyproblemmessage) | Поле | ні |
| [__init__](jane_registry.profiles.md#jane_registryprofilesdependencyproblem__init__) | Конструктор dataclass | ні |

## jane_registry.profiles.DependencyProblem.__init__

**Конструктор dataclass.** Код: [services/registry/src/jane_registry/profiles.py:65](../../../../../../services/registry/src/jane_registry/profiles.py#L65).

```python
def __init__(self, index: int, requirement: str, message: str) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `index` | `int` | `—` | positional-or-keyword |
| `requirement` | `str` | `—` | positional-or-keyword |
| `message` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.profiles.DependencyProblem.index

**Поле.** Код: [services/registry/src/jane_registry/profiles.py:66](../../../../../../services/registry/src/jane_registry/profiles.py#L66).

```python
index: int
```

Доступ: читання — так; запис — ні.

## jane_registry.profiles.DependencyProblem.requirement

**Поле.** Код: [services/registry/src/jane_registry/profiles.py:67](../../../../../../services/registry/src/jane_registry/profiles.py#L67).

```python
requirement: str
```

Доступ: читання — так; запис — ні.

## jane_registry.profiles.DependencyProblem.message

**Поле.** Код: [services/registry/src/jane_registry/profiles.py:68](../../../../../../services/registry/src/jane_registry/profiles.py#L68).

```python
message: str
```

Доступ: читання — так; запис — ні.

## jane_registry.profiles.parse_profiles

**Функція.** Код: [services/registry/src/jane_registry/profiles.py:75](../../../../../../services/registry/src/jane_registry/profiles.py#L75).

```python
def parse_profiles(doc: Any) -> dict[str, RuntimeProfile]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `doc` | `Any` | `—` | positional-or-keyword |

Результат: `dict[str, RuntimeProfile]`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Profiles from one source document (profile, list, ``runtime_profiles`` map or ``ServiceInfo``).
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_runtime_compat.py:47](../../../../../../services/registry/tests/test_runtime_compat.py#L47).

```python
ours = parse_profiles(doc)["python-extractor@1"]
```

Контекст і передумови: [services/registry/tests/test_units.py:283](../../../../../../services/registry/tests/test_units.py#L283).

```python
profile = parse_profiles(TEST_PROFILE)["python-extractor@1"]
```

## jane_registry.profiles.ProfileSource

**Клас.** Код: [services/registry/src/jane_registry/profiles.py:98](../../../../../../services/registry/src/jane_registry/profiles.py#L98).

```python
class ProfileSource:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_registry.profiles.md#jane_registryprofilesprofilesource__init__) | Конструктор | ні |
| [sources](jane_registry.profiles.md#jane_registryprofilesprofilesourcesources) | Поле екземпляра | ні |
| [limits](jane_registry.profiles.md#jane_registryprofilesprofilesourcelimits) | Поле екземпляра | ні |
| [transport](jane_registry.profiles.md#jane_registryprofilesprofilesourcetransport) | Поле екземпляра | ні |
| [errors](jane_registry.profiles.md#jane_registryprofilesprofilesourceerrors) | Поле екземпляра | ні |
| [known](jane_registry.profiles.md#jane_registryprofilesprofilesourceknown) | Метод | ні |
| [profiles](jane_registry.profiles.md#jane_registryprofilesprofilesourceprofiles) | Метод | ні |

### Опис із вихідного коду

```text
Loads profiles from the configured sources and caches them for ``refresh_seconds``.
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_auth.py:72](../../../../../../services/registry/tests/test_auth.py#L72).

```python
source = ProfileSource(
        ["http://runtime.test/v1/info"],
        ProfileLimits(),
        transport=httpx.MockTransport(handler),
        token="k-reg",
    )
```

Контекст і передумови: [services/registry/tests/test_service_ops.py:95](../../../../../../services/registry/tests/test_service_ops.py#L95).

```python
source = ProfileSource(
        ["http://runtime.test/v1/info"], ProfileLimits(), transport=httpx.MockTransport(handler)
    )
```

## jane_registry.profiles.ProfileSource.__init__

**Конструктор.** Код: [services/registry/src/jane_registry/profiles.py:101](../../../../../../services/registry/src/jane_registry/profiles.py#L101).

```python
def __init__(self, sources: Sequence[str], limits: ProfileLimits, transport: httpx.AsyncBaseTransport | None=None, token: str | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `sources` | `Sequence[str]` | `—` | positional-or-keyword |
| `limits` | `ProfileLimits` | `—` | positional-or-keyword |
| `transport` | `httpx.AsyncBaseTransport \| None` | `None` | positional-or-keyword |
| `token` | `str \| None` | `None` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_auth.py:72](../../../../../../services/registry/tests/test_auth.py#L72).

```python
source = ProfileSource(
        ["http://runtime.test/v1/info"],
        ProfileLimits(),
        transport=httpx.MockTransport(handler),
        token="k-reg",
    )
```

Контекст і передумови: [services/registry/tests/test_service_ops.py:95](../../../../../../services/registry/tests/test_service_ops.py#L95).

```python
source = ProfileSource(
        ["http://runtime.test/v1/info"], ProfileLimits(), transport=httpx.MockTransport(handler)
    )
```

## jane_registry.profiles.ProfileSource.sources

**Поле екземпляра.** Код: [services/registry/src/jane_registry/profiles.py:108](../../../../../../services/registry/src/jane_registry/profiles.py#L108).

```python
self.sources = list(sources)
```

## jane_registry.profiles.ProfileSource.limits

**Поле екземпляра.** Код: [services/registry/src/jane_registry/profiles.py:109](../../../../../../services/registry/src/jane_registry/profiles.py#L109).

```python
self.limits = limits
```

## jane_registry.profiles.ProfileSource.transport

**Поле екземпляра.** Код: [services/registry/src/jane_registry/profiles.py:110](../../../../../../services/registry/src/jane_registry/profiles.py#L110).

```python
self.transport = transport
```

## jane_registry.profiles.ProfileSource.errors

**Поле екземпляра.** Код: [services/registry/src/jane_registry/profiles.py:116](../../../../../../services/registry/src/jane_registry/profiles.py#L116).

```python
self.errors: list[str] = []
```

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_service_ops.py:109](../../../../../../services/registry/tests/test_service_ops.py#L109).

```python
assert broken.errors and "503" in broken.errors[0]
```

## jane_registry.profiles.ProfileSource.known

**Метод.** Код: [services/registry/src/jane_registry/profiles.py:118](../../../../../../services/registry/src/jane_registry/profiles.py#L118).

```python
def known(self) -> list[str]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `list[str]`.

### Опис із вихідного коду

```text
Names of the profiles loaded so far (``/v1/info``).
```

## jane_registry.profiles.ProfileSource.profiles

**Метод.** Код: [services/registry/src/jane_registry/profiles.py:133](../../../../../../services/registry/src/jane_registry/profiles.py#L133).

```python
async def profiles(self) -> dict[str, RuntimeProfile]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `dict[str, RuntimeProfile]`.

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_auth.py:78](../../../../../../services/registry/tests/test_auth.py#L78).

```python
assert set(await source.profiles()) == {"python-extractor@1"}
```

Контекст і передумови: [services/registry/tests/test_service_ops.py:99](../../../../../../services/registry/tests/test_service_ops.py#L99).

```python
await source.profiles()
```

## jane_registry.profiles.check_dependencies

**Функція.** Код: [services/registry/src/jane_registry/profiles.py:152](../../../../../../services/registry/src/jane_registry/profiles.py#L152).

```python
def check_dependencies(profile: RuntimeProfile, requirements: Sequence[str]) -> list[DependencyProblem]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `profile` | `RuntimeProfile` | `—` | positional-or-keyword |
| `requirements` | `Sequence[str]` | `—` | positional-or-keyword |

Результат: `list[DependencyProblem]`.

### Приклади з тестів

Контекст і передумови: [services/registry/tests/test_runtime_compat.py:62](../../../../../../services/registry/tests/test_runtime_compat.py#L62).

```python
our_bad = {p.requirement for p in check_dependencies(ours, requirements)}
```

Контекст і передумови: [services/registry/tests/test_units.py:292](../../../../../../services/registry/tests/test_units.py#L292).

```python
problems = check_dependencies(
        profile, ["requests", "lxml<6", "not a requirement !!", "lxml @ https://example.test/lxml.whl"]
    )
```
