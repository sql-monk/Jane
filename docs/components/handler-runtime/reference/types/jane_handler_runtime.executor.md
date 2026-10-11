# Модуль `jane_handler_runtime.executor`

> Згенеровано `scripts/docs_reference.py` з [services/handler-runtime/src/jane_handler_runtime/executor.py](../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py). Не редагуйте вручну.

Executing a ``HandlerInvocation``: prepare (package, dependencies, params, inputs, limits), run in the sandbox, turn the runner output into a ``HandlerResult`` with the four states of TZ §9.

``prepare`` raises :class:`JaneError` (HTTP errors: the call did not happen); once the sandbox ran, every problem is a ``HandlerResult`` with ``status: failed`` and ``failure.kind``.

## Зміст

- [Клас `Executor`](#клас-executor)
- [Клас `PreparedInvocation`](#клас-preparedinvocation)
- [Функція `new_invocation_id`](#функція-new_invocation_id)
- [Функція `now_rfc3339`](#функція-now_rfc3339)

## Класи

### Клас `Executor`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_handler_runtime.executor` |
| Код | [executor.py:75](../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L75) |

```python
class Executor: ...
```

#### Конструктор `Executor.__init__`

```python
def __init__(
    self,
    settings: Settings,
    store: PackageStore,
    fetcher: ContentFetcher,
    backend: SandboxBackend,
    schemas: ContractSchemas,
) -> None: ...
```

Код: [executor.py:76](../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L76).

#### Метод `Executor.check_package`

```python
def check_package(self, package: LoadedPackage) -> str: ...
```

Kind, entry, access and dependencies; returns the sandbox image of the runtime profile.

Винятки в коді методу: `ValidationFailed`, `JaneError`.

Код: [executor.py:94](../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L94).

#### Метод `Executor.check_params`

```python
def check_params(
    self,
    package: LoadedPackage,
    params: Mapping[str, Any] | None,
) -> dict[str, Any]: ...
```

Винятки в коді методу: `ValidationFailed`.

Код: [executor.py:141](../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L141).

#### Метод `Executor.check_input`

```python
def check_input(self, package: LoadedPackage, index: int, item: Mapping[str, Any]) -> None: ...
```

Винятки в коді методу: `ValidationFailed`.

Код: [executor.py:154](../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L154).

#### Метод `Executor.prepare`

```python
async def prepare(
    self,
    invocation: Mapping[str, Any],
    *,
    package: LoadedPackage | None = None,
    test_mode: bool | None = None,
) -> PreparedInvocation: ...
```

Validate everything that must be right before the sandbox starts.

Винятки в коді методу: `ValidationFailed`.

Код: [executor.py:199](../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L199).

#### Метод `Executor.bundle`

```python
def bundle(self, prep: PreparedInvocation) -> Bundle: ...
```

Код: [executor.py:241](../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L241).

#### Метод `Executor.labels`

```python
def labels(self, prep: PreparedInvocation) -> dict[str, str]: ...
```

Код: [executor.py:263](../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L263).

#### Метод `Executor.run`

```python
async def run(self, prep: PreparedInvocation) -> dict[str, Any]: ...
```

Винятки в коді методу: `ServiceUnavailable`.

Код: [executor.py:269](../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L269).

#### Метод `Executor.interpret`

```python
def interpret(
    self,
    prep: PreparedInvocation,
    outcome: SandboxOutcome,
    started_at: str,
) -> dict[str, Any]: ...
```

Винятки в коді методу: `ValueError`.

Код: [executor.py:328](../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L328).

### Клас `PreparedInvocation`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_handler_runtime.executor` |
| Код | [executor.py:55](../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L55) |

```python
@dataclass
class PreparedInvocation: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `invocation_id` | `str` | — | читання й запис |  |
| `package` | `LoadedPackage` | — | читання й запис |  |
| `params` | `dict[str, Any]` | — | читання й запис |  |
| `inputs` | `list[dict[str, Any]]` | — | читання й запис |  |
| `contents` | `list[bytes \| None]` | — | читання й запис |  |
| `limits` | `ServiceLimits` | — | читання й запис |  |
| `image` | `str` | — | читання й запис |  |
| `test_mode` | `bool` | `False` | читання й запис |  |
| `delivery_key` | `str \| None` | `None` | читання й запис |  |
| `context` | `dict[str, Any]` | `field(default_factory=dict)` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `new_invocation_id`

```python
def new_invocation_id() -> str: ...
```

Код: [executor.py:50](../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L50).

### Функція `now_rfc3339`

```python
def now_rfc3339() -> str: ...
```

Код: [executor.py:46](../../../../../services/handler-runtime/src/jane_handler_runtime/executor.py#L46).
