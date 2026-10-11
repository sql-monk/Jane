# Модуль `jane_handler_runtime.sandbox`

> Згенеровано `scripts/docs_reference.py` з [services/handler-runtime/src/jane_handler_runtime/sandbox.py](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py). Не редагуйте вручну.

Sandbox backends (ADR-0003): ``SandboxBackend`` protocol, the workdir bundle, the ``subprocess`` backend.

A run gets a *bundle* - files for the runner's ``<workdir>`` (``request.json``, ``package/...``, ``inputs/<n>``) - and returns raw stdout/stderr and how the process ended. Interpreting the output is the executor's job, so every backend behaves the same way.

## Зміст

- [Клас `Bundle`](#клас-bundle)
- [Клас `SandboxBackend`](#клас-sandboxbackend)
- [Клас `SandboxOutcome`](#клас-sandboxoutcome)
- [Клас `SandboxUnavailable`](#клас-sandboxunavailable)
- [Клас `SubprocessSandbox`](#клас-subprocesssandbox)
- [Функція `killed_by_sigkill`](#функція-killed_by_sigkill)
- [Функція `read_limited`](#функція-read_limited)

## Класи

### Клас `Bundle`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_handler_runtime.sandbox` |
| Код | [sandbox.py:56](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L56) |

```python
@dataclass
class Bundle: ...
```

Files of the runner workdir: package path -> bytes (``/`` separators).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `files` | `dict[str, bytes]` | `field(default_factory=dict)` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `Bundle.add`

```python
def add(self, name: str, data: bytes) -> None: ...
```

Винятки в коді методу: `ValueError`.

Код: [sandbox.py:61](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L61).

#### Метод `Bundle.tar`

```python
def tar(self) -> bytes: ...
```

Tar owned by root with read-only modes: the non-root sandbox user can read but not modify.

Код: [sandbox.py:66](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L66).

#### Метод `Bundle.write_to`

```python
def write_to(self, root: Path) -> None: ...
```

Код: [sandbox.py:88](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L88).

### Клас `SandboxBackend`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_handler_runtime.sandbox` |
| Успадкування | `Protocol` |
| Код | [sandbox.py:113](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L113) |

```python
class SandboxBackend(Protocol): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `name` | `str` | — | читання й запис |  |
| `enforces_memory_limit` | `bool` | — | читання й запис | ``memory_mb`` is a kernel (cgroup) limit of the sandbox. Then the only SIGKILL the runtime did not send (no timeout, no cancel) is the OOM killer, and the executor classifies it as ``resource_exceeded`` even if the engine did not report ``OOMKilled``. |

#### Метод `SandboxBackend.run`

```python
def run(
    self,
    image: str,
    bundle: Bundle,
    limits: SandboxLimits,
    labels: Mapping[str, str],
) -> SandboxOutcome: ...
```

Run the runner over ``bundle`` with ``limits``; blocks (call it in a worker thread).

Код: [sandbox.py:120](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L120).

#### Метод `SandboxBackend.ping`

```python
def ping(self) -> None: ...
```

Raise :class:`SandboxUnavailable` if runs are impossible.

Код: [sandbox.py:126](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L126).

#### Метод `SandboxBackend.kill`

```python
def kill(self, invocation_id: str) -> int: ...
```

Force-stop the sandbox(es) of ``invocation_id``; returns how many were stopped.

Код: [sandbox.py:130](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L130).

### Клас `SandboxOutcome`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_handler_runtime.sandbox` |
| Код | [sandbox.py:96](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L96) |

```python
@dataclass
class SandboxOutcome: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `exit_code` | `int \| None` | — | читання й запис |  |
| `stdout` | `bytes` | — | читання й запис |  |
| `stderr` | `bytes` | — | читання й запис |  |
| `duration_ms` | `int` | — | читання й запис |  |
| `timed_out` | `bool` | `False` | читання й запис |  |
| `oom_killed` | `bool` | `False` | читання й запис | The engine reported an OOM kill (container state). Not reliable on its own: it can be missing even when the kernel OOM killer stopped the process, see :attr:`SandboxBackend.enforces_memory_limit`. |
| `killed_by_runtime` | `bool` | `False` | читання й запис | The runtime itself force-stopped the sandbox for a reason other than wall time (job cancel). |
| `stdout_truncated` | `bool` | `False` | читання й запис |  |
| `stderr_truncated` | `bool` | `False` | читання й запис |  |
| `backend` | `str` | `''` | читання й запис |  |
| `details` | `dict[str, object]` | `field(default_factory=dict)` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `SandboxUnavailable`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_handler_runtime.sandbox` |
| Успадкування | `RuntimeError` |
| Код | [sandbox.py:51](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L51) |

```python
class SandboxUnavailable(RuntimeError): ...
```

The backend cannot run anything (no container engine, image missing, backend disabled).

### Клас `SubprocessSandbox`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_handler_runtime.sandbox` |
| Код | [sandbox.py:142](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L142) |

```python
class SubprocessSandbox: ...
```

Runs the runner as a local process. **No isolation** (no network block, no FS or memory limits): only for trusted packages in local development and unit tests; refused unless explicitly allowed.

Without a memory limit a SIGKILL cannot be attributed to ``memory_mb``: it stays ``execution_error``.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `name` | `'subprocess'` |  |
| `enforces_memory_limit` | `False` |  |

#### Конструктор `SubprocessSandbox.__init__`

```python
def __init__(self, allowed: bool, kill_grace_ms: int = 0) -> None: ...
```

Код: [sandbox.py:151](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L151).

#### Метод `SubprocessSandbox.kill`

```python
def kill(self, invocation_id: str) -> int: ...
```

Код: [sandbox.py:157](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L157).

#### Метод `SubprocessSandbox.ping`

```python
def ping(self) -> None: ...
```

Винятки в коді методу: `SandboxUnavailable`.

Код: [sandbox.py:165](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L165).

#### Метод `SubprocessSandbox.run`

```python
def run(
    self,
    image: str,
    bundle: Bundle,
    limits: SandboxLimits,
    labels: Mapping[str, str],
) -> SandboxOutcome: ...
```

Код: [sandbox.py:172](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L172).

## Функції

### Функція `killed_by_sigkill`

```python
def killed_by_sigkill(exit_code: int | None) -> bool: ...
```

The sandbox process ended by SIGKILL: ``128 + 9`` (container / ``timeout`` as PID 1 report a child killed by a signal this way) or ``-9`` (``Popen.returncode`` of a killed child on POSIX).

Код: [sandbox.py:45](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L45).

### Функція `read_limited`

```python
def read_limited(stream: io.BufferedIOBase | None, limit: int) -> tuple[bytes, bool]: ...
```

Код: [sandbox.py:135](../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L135).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `INVOCATION_LABEL` | — | `'io.jane.invocation-id'` | Label (and subprocess key) that identifies the sandbox of an invocation, used to stop it on cancel. |
