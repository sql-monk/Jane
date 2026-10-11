# Модуль `jane_registry.profiles`

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry/profiles.py](../../../../../services/registry/src/jane_registry/profiles.py). Не редагуйте вручну.

Runtime profiles and the check of ``dependencies.python`` (ADR-0002 §4, ADR-0003).

A profile (``python-extractor@1``) is published by handler-runtime (WP-06) as a JSON document::

    {"profile": "python-extractor@1", "python": "3.12", "libraries": {"lxml": "6.1.3", ...}, ...}

The registry does not hard-code profiles: it reads them from the configured sources (``JANE_REGISTRY_RUNTIME_PROFILES`` - files or URLs, e.g. ``<handler-runtime>/v1/info``). The check uses the same rules as the runtime: every requirement is PEP 508; direct URL requirements are not allowed; a requirement whose environment marker is false for the sandbox (Linux, the profile's Python) is skipped; otherwise the distribution must be in the profile and its exact version must satisfy the specifier (pre-releases allowed).

## Зміст

- [Клас `DependencyProblem`](#клас-dependencyproblem)
- [Клас `ProfileSource`](#клас-profilesource)
- [Клас `RuntimeProfile`](#клас-runtimeprofile)
- [Функція `check_dependencies`](#функція-check_dependencies)
- [Функція `parse_profiles`](#функція-parse_profiles)

## Класи

### Клас `DependencyProblem`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_registry.profiles` |
| Код | [profiles.py:65](../../../../../services/registry/src/jane_registry/profiles.py#L65) |

```python
@dataclass(frozen=True)
class DependencyProblem: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `index` | `int` | — | читання |  |
| `requirement` | `str` | — | читання |  |
| `message` | `str` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `ProfileSource`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.profiles` |
| Код | [profiles.py:98](../../../../../services/registry/src/jane_registry/profiles.py#L98) |

```python
class ProfileSource: ...
```

Loads profiles from the configured sources and caches them for ``refresh_seconds``.

#### Конструктор `ProfileSource.__init__`

```python
def __init__(
    self,
    sources: Sequence[str],
    limits: ProfileLimits,
    transport: httpx.AsyncBaseTransport | None = None,
    token: str | None = None,
) -> None: ...
```

Код: [profiles.py:101](../../../../../services/registry/src/jane_registry/profiles.py#L101).

#### Метод `ProfileSource.known`

```python
def known(self) -> list[str]: ...
```

Names of the profiles loaded so far (``/v1/info``).

Код: [profiles.py:118](../../../../../services/registry/src/jane_registry/profiles.py#L118).

#### Метод `ProfileSource.profiles`

```python
async def profiles(self) -> dict[str, RuntimeProfile]: ...
```

Код: [profiles.py:133](../../../../../services/registry/src/jane_registry/profiles.py#L133).

### Клас `RuntimeProfile`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_registry.profiles` |
| Код | [profiles.py:39](../../../../../services/registry/src/jane_registry/profiles.py#L39) |

```python
@dataclass(frozen=True)
class RuntimeProfile: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `name` | `str` | — | читання |  |
| `python` | `str` | — | читання |  |
| `libraries` | `Mapping[str, str]` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `RuntimeProfile.marker_environment`

```python
def marker_environment(self) -> dict[str, str]: ...
```

PEP 508 marker values of the sandbox (a Linux container), not of the registry host.

Код: [profiles.py:44](../../../../../services/registry/src/jane_registry/profiles.py#L44).

#### Метод `RuntimeProfile.version_of`

```python
def version_of(self, distribution: str) -> str | None: ...
```

Код: [profiles.py:56](../../../../../services/registry/src/jane_registry/profiles.py#L56).

## Функції

### Функція `check_dependencies`

```python
def check_dependencies(
    profile: RuntimeProfile,
    requirements: Sequence[str],
) -> list[DependencyProblem]: ...
```

Код: [profiles.py:152](../../../../../services/registry/src/jane_registry/profiles.py#L152).

### Функція `parse_profiles`

```python
def parse_profiles(doc: Any) -> dict[str, RuntimeProfile]: ...
```

Profiles from one source document (profile, list, ``runtime_profiles`` map or ``ServiceInfo``).

Винятки в коді функції: `ValueError`.

Код: [profiles.py:75](../../../../../services/registry/src/jane_registry/profiles.py#L75).
