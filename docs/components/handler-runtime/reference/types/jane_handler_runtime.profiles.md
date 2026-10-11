# Модуль `jane_handler_runtime.profiles`

> Згенеровано `scripts/docs_reference.py` з [services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py](../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py). Не редагуйте вручну.

Runtime profiles: which Python and libraries a sandbox image provides (``dependencies.runtime_profile``).

The machine-readable description (``python-extractor-1.json``) is the list the registry (WP-05) uses to check ``dependencies.python`` of a manifest (``dependency_not_allowed``); ``GET /v1/info`` publishes it in ``capabilities.runtime_profiles`` and the CLI prints it with ``jane-handler-runtime profile``.

## Зміст

- [Клас `DependencyProblem`](#клас-dependencyproblem)
- [Клас `RuntimeProfile`](#клас-runtimeprofile)
- [Функція `check_dependencies`](#функція-check_dependencies)
- [Функція `load_profiles`](#функція-load_profiles)

## Класи

### Клас `DependencyProblem`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_handler_runtime.profiles` |
| Код | [__init__.py:52](../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L52) |

```python
@dataclass(frozen=True)
class DependencyProblem: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `requirement` | `str` | — | читання |  |
| `message` | `str` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `RuntimeProfile`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_handler_runtime.profiles` |
| Код | [__init__.py:25](../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L25) |

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
| `document` | `Mapping[str, Any]` | — | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `RuntimeProfile.marker_environment`

```python
def marker_environment(self) -> dict[str, str]: ...
```

PEP 508 marker values of the sandbox (Linux container), not of the host running the runtime.

Код: [__init__.py:31](../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L31).

#### Метод `RuntimeProfile.version_of`

```python
def version_of(self, distribution: str) -> str | None: ...
```

Код: [__init__.py:43](../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L43).

## Функції

### Функція `check_dependencies`

```python
def check_dependencies(
    profile: RuntimeProfile,
    requirements: Sequence[str],
) -> list[DependencyProblem]: ...
```

PEP 508 requirements of a manifest vs the exact versions of the profile.

Код: [__init__.py:67](../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L67).

### Функція `load_profiles`

```python
@cache
def load_profiles() -> dict[str, RuntimeProfile]: ...
```

Код: [__init__.py:58](../../../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py#L58).
