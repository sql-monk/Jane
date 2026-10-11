# jane_handler_runtime.sandbox

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_handler_runtime.sandbox.INVOCATION_LABEL](#jane_handler_runtimesandboxinvocation_label)
- [jane_handler_runtime.sandbox.killed_by_sigkill](#jane_handler_runtimesandboxkilled_by_sigkill)
- [jane_handler_runtime.sandbox.SandboxUnavailable](#jane_handler_runtimesandboxsandboxunavailable)
- [jane_handler_runtime.sandbox.Bundle](#jane_handler_runtimesandboxbundle)
- [jane_handler_runtime.sandbox.Bundle.__init__](#jane_handler_runtimesandboxbundle__init__)
- [jane_handler_runtime.sandbox.Bundle.files](#jane_handler_runtimesandboxbundlefiles)
- [jane_handler_runtime.sandbox.Bundle.add](#jane_handler_runtimesandboxbundleadd)
- [jane_handler_runtime.sandbox.Bundle.tar](#jane_handler_runtimesandboxbundletar)
- [jane_handler_runtime.sandbox.Bundle.write_to](#jane_handler_runtimesandboxbundlewrite_to)
- [jane_handler_runtime.sandbox.SandboxOutcome](#jane_handler_runtimesandboxsandboxoutcome)
- [jane_handler_runtime.sandbox.SandboxOutcome.__init__](#jane_handler_runtimesandboxsandboxoutcome__init__)
- [jane_handler_runtime.sandbox.SandboxOutcome.exit_code](#jane_handler_runtimesandboxsandboxoutcomeexit_code)
- [jane_handler_runtime.sandbox.SandboxOutcome.stdout](#jane_handler_runtimesandboxsandboxoutcomestdout)
- [jane_handler_runtime.sandbox.SandboxOutcome.stderr](#jane_handler_runtimesandboxsandboxoutcomestderr)
- [jane_handler_runtime.sandbox.SandboxOutcome.duration_ms](#jane_handler_runtimesandboxsandboxoutcomeduration_ms)
- [jane_handler_runtime.sandbox.SandboxOutcome.timed_out](#jane_handler_runtimesandboxsandboxoutcometimed_out)
- [jane_handler_runtime.sandbox.SandboxOutcome.oom_killed](#jane_handler_runtimesandboxsandboxoutcomeoom_killed)
- [jane_handler_runtime.sandbox.SandboxOutcome.killed_by_runtime](#jane_handler_runtimesandboxsandboxoutcomekilled_by_runtime)
- [jane_handler_runtime.sandbox.SandboxOutcome.stdout_truncated](#jane_handler_runtimesandboxsandboxoutcomestdout_truncated)
- [jane_handler_runtime.sandbox.SandboxOutcome.stderr_truncated](#jane_handler_runtimesandboxsandboxoutcomestderr_truncated)
- [jane_handler_runtime.sandbox.SandboxOutcome.backend](#jane_handler_runtimesandboxsandboxoutcomebackend)
- [jane_handler_runtime.sandbox.SandboxOutcome.details](#jane_handler_runtimesandboxsandboxoutcomedetails)
- [jane_handler_runtime.sandbox.SandboxBackend](#jane_handler_runtimesandboxsandboxbackend)
- [jane_handler_runtime.sandbox.SandboxBackend.name](#jane_handler_runtimesandboxsandboxbackendname)
- [jane_handler_runtime.sandbox.SandboxBackend.enforces_memory_limit](#jane_handler_runtimesandboxsandboxbackendenforces_memory_limit)
- [jane_handler_runtime.sandbox.SandboxBackend.run](#jane_handler_runtimesandboxsandboxbackendrun)
- [jane_handler_runtime.sandbox.SandboxBackend.ping](#jane_handler_runtimesandboxsandboxbackendping)
- [jane_handler_runtime.sandbox.SandboxBackend.kill](#jane_handler_runtimesandboxsandboxbackendkill)
- [jane_handler_runtime.sandbox.read_limited](#jane_handler_runtimesandboxread_limited)
- [jane_handler_runtime.sandbox.SubprocessSandbox](#jane_handler_runtimesandboxsubprocesssandbox)
- [jane_handler_runtime.sandbox.SubprocessSandbox.name](#jane_handler_runtimesandboxsubprocesssandboxname)
- [jane_handler_runtime.sandbox.SubprocessSandbox.enforces_memory_limit](#jane_handler_runtimesandboxsubprocesssandboxenforces_memory_limit)
- [jane_handler_runtime.sandbox.SubprocessSandbox.__init__](#jane_handler_runtimesandboxsubprocesssandbox__init__)
- [jane_handler_runtime.sandbox.SubprocessSandbox.allowed](#jane_handler_runtimesandboxsubprocesssandboxallowed)
- [jane_handler_runtime.sandbox.SubprocessSandbox.kill_grace_ms](#jane_handler_runtimesandboxsubprocesssandboxkill_grace_ms)
- [jane_handler_runtime.sandbox.SubprocessSandbox.kill](#jane_handler_runtimesandboxsubprocesssandboxkill)
- [jane_handler_runtime.sandbox.SubprocessSandbox.ping](#jane_handler_runtimesandboxsubprocesssandboxping)
- [jane_handler_runtime.sandbox.SubprocessSandbox.run](#jane_handler_runtimesandboxsubprocesssandboxrun)

## jane_handler_runtime.sandbox.INVOCATION_LABEL

**Константа.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:39](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L39).

```python
INVOCATION_LABEL = 'io.jane.invocation-id'
```

### Опис із вихідного коду

```text
Label (and subprocess key) that identifies the sandbox of an invocation, used to stop it on cancel.
```

## jane_handler_runtime.sandbox.killed_by_sigkill

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:45](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L45).

```python
def killed_by_sigkill(exit_code: int | None) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `exit_code` | `int \| None` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
The sandbox process ended by SIGKILL: ``128 + 9`` (container / ``timeout`` as PID 1 report a child
killed by a signal this way) or ``-9`` (``Popen.returncode`` of a killed child on POSIX).
```

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_classification.py:63](../../../../../../services/handler-runtime/tests/test_classification.py#L63).

```python
assert sandbox.killed_by_sigkill(code) is expected
```

## jane_handler_runtime.sandbox.SandboxUnavailable

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:51](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L51).

```python
class SandboxUnavailable(RuntimeError):
```

Базові типи / інтерфейси: `RuntimeError`.

### Опис із вихідного коду

```text
The backend cannot run anything (no container engine, image missing, backend disabled).
```

## jane_handler_runtime.sandbox.Bundle

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:56](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L56).

```python
class Bundle:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [files](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxbundlefiles) | Поле | ні |
| [add](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxbundleadd) | Метод | ні |
| [tar](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxbundletar) | Метод | ні |
| [write_to](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxbundlewrite_to) | Метод | ні |
| [__init__](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxbundle__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Files of the runner workdir: package path -> bytes (``/`` separators).
```

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_units.py:88](../../../../../../services/handler-runtime/tests/test_units.py#L88).

```python
bundle = Bundle()
```

## jane_handler_runtime.sandbox.Bundle.__init__

**Конструктор dataclass.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:56](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L56).

```python
def __init__(self, files: dict[str, bytes] = <factory dict>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `files` | `dict[str, bytes]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_units.py:88](../../../../../../services/handler-runtime/tests/test_units.py#L88).

```python
bundle = Bundle()
```

## jane_handler_runtime.sandbox.Bundle.files

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:59](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L59).

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

## jane_handler_runtime.sandbox.Bundle.add

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:61](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L61).

```python
def add(self, name: str, data: bytes) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |
| `data` | `bytes` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_units.py:89](../../../../../../services/handler-runtime/tests/test_units.py#L89).

```python
bundle.add("package/src/a.py", b"x")
```

Контекст і передумови: [services/handler-runtime/tests/test_units.py:90](../../../../../../services/handler-runtime/tests/test_units.py#L90).

```python
bundle.add("request.json", b"{}")
```

## jane_handler_runtime.sandbox.Bundle.tar

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:66](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L66).

```python
def tar(self) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bytes`.

### Опис із вихідного коду

```text
Tar owned by root with read-only modes: the non-root sandbox user can read but not modify.
```

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_units.py:93](../../../../../../services/handler-runtime/tests/test_units.py#L93).

```python
bundle.tar()
```

## jane_handler_runtime.sandbox.Bundle.write_to

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:88](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L88).

```python
def write_to(self, root: Path) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `root` | `Path` | `—` | positional-or-keyword |

Результат: `None`.

## jane_handler_runtime.sandbox.SandboxOutcome

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:96](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L96).

```python
class SandboxOutcome:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [exit_code](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsandboxoutcomeexit_code) | Поле | ні |
| [stdout](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsandboxoutcomestdout) | Поле | ні |
| [stderr](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsandboxoutcomestderr) | Поле | ні |
| [duration_ms](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsandboxoutcomeduration_ms) | Поле | ні |
| [timed_out](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsandboxoutcometimed_out) | Поле | ні |
| [oom_killed](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsandboxoutcomeoom_killed) | Поле | ні |
| [killed_by_runtime](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsandboxoutcomekilled_by_runtime) | Поле | ні |
| [stdout_truncated](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsandboxoutcomestdout_truncated) | Поле | ні |
| [stderr_truncated](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsandboxoutcomestderr_truncated) | Поле | ні |
| [backend](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsandboxoutcomebackend) | Поле | ні |
| [details](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsandboxoutcomedetails) | Поле | ні |
| [__init__](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsandboxoutcome__init__) | Конструктор dataclass | ні |

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_classification.py:40](../../../../../../services/handler-runtime/tests/test_classification.py#L40).

```python
return SandboxOutcome(exit_code=exit_code, stdout=b"", stderr=b"", duration_ms=420, **kw)
```

## jane_handler_runtime.sandbox.SandboxOutcome.__init__

**Конструктор dataclass.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:96](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L96).

```python
def __init__(self, exit_code: int | None, stdout: bytes, stderr: bytes, duration_ms: int, timed_out: bool = False, oom_killed: bool = False, killed_by_runtime: bool = False, stdout_truncated: bool = False, stderr_truncated: bool = False, backend: str = '', details: dict[str, object] = <factory dict>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `exit_code` | `int \| None` | `—` | positional-or-keyword |
| `stdout` | `bytes` | `—` | positional-or-keyword |
| `stderr` | `bytes` | `—` | positional-or-keyword |
| `duration_ms` | `int` | `—` | positional-or-keyword |
| `timed_out` | `bool` | `False` | positional-or-keyword |
| `oom_killed` | `bool` | `False` | positional-or-keyword |
| `killed_by_runtime` | `bool` | `False` | positional-or-keyword |
| `stdout_truncated` | `bool` | `False` | positional-or-keyword |
| `stderr_truncated` | `bool` | `False` | positional-or-keyword |
| `backend` | `str` | `''` | positional-or-keyword |
| `details` | `dict[str, object]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_classification.py:40](../../../../../../services/handler-runtime/tests/test_classification.py#L40).

```python
return SandboxOutcome(exit_code=exit_code, stdout=b"", stderr=b"", duration_ms=420, **kw)
```

## jane_handler_runtime.sandbox.SandboxOutcome.exit_code

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:97](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L97).

```python
exit_code: int | None
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.sandbox.SandboxOutcome.stdout

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:98](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L98).

```python
stdout: bytes
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.sandbox.SandboxOutcome.stderr

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:99](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L99).

```python
stderr: bytes
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.sandbox.SandboxOutcome.duration_ms

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:100](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L100).

```python
duration_ms: int
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.sandbox.SandboxOutcome.timed_out

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:101](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L101).

```python
timed_out: bool = False
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.sandbox.SandboxOutcome.oom_killed

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:102](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L102).

```python
oom_killed: bool = False
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
The engine reported an OOM kill (container state). Not reliable on its own: it can be missing even
    when the kernel OOM killer stopped the process, see :attr:`SandboxBackend.enforces_memory_limit`.
```

## jane_handler_runtime.sandbox.SandboxOutcome.killed_by_runtime

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:105](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L105).

```python
killed_by_runtime: bool = False
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
The runtime itself force-stopped the sandbox for a reason other than wall time (job cancel).
```

## jane_handler_runtime.sandbox.SandboxOutcome.stdout_truncated

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:107](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L107).

```python
stdout_truncated: bool = False
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.sandbox.SandboxOutcome.stderr_truncated

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:108](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L108).

```python
stderr_truncated: bool = False
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.sandbox.SandboxOutcome.backend

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:109](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L109).

```python
backend: str = ''
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.sandbox.SandboxOutcome.details

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:110](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L110).

```python
details: dict[str, object] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_handler_runtime.sandbox.SandboxBackend

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:113](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L113).

```python
class SandboxBackend(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsandboxbackendname) | Поле | ні |
| [enforces_memory_limit](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsandboxbackendenforces_memory_limit) | Поле | ні |
| [run](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsandboxbackendrun) | Метод | ні |
| [ping](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsandboxbackendping) | Метод | ні |
| [kill](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsandboxbackendkill) | Метод | ні |

## jane_handler_runtime.sandbox.SandboxBackend.name

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:114](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L114).

```python
name: str
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.sandbox.SandboxBackend.enforces_memory_limit

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:115](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L115).

```python
enforces_memory_limit: bool
```

Доступ: читання — так; запис — так.

### Опис із вихідного коду

```text
``memory_mb`` is a kernel (cgroup) limit of the sandbox. Then the only SIGKILL the runtime did not send
    (no timeout, no cancel) is the OOM killer, and the executor classifies it as ``resource_exceeded`` even if
    the engine did not report ``OOMKilled``.
```

## jane_handler_runtime.sandbox.SandboxBackend.run

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:120](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L120).

```python
def run(self, image: str, bundle: Bundle, limits: SandboxLimits, labels: Mapping[str, str]) -> SandboxOutcome:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `image` | `str` | `—` | positional-or-keyword |
| `bundle` | `Bundle` | `—` | positional-or-keyword |
| `limits` | `SandboxLimits` | `—` | positional-or-keyword |
| `labels` | `Mapping[str, str]` | `—` | positional-or-keyword |

Результат: `SandboxOutcome`.

### Опис із вихідного коду

```text
Run the runner over ``bundle`` with ``limits``; blocks (call it in a worker thread).
```

## jane_handler_runtime.sandbox.SandboxBackend.ping

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:126](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L126).

```python
def ping(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Raise :class:`SandboxUnavailable` if runs are impossible.
```

## jane_handler_runtime.sandbox.SandboxBackend.kill

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:130](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L130).

```python
def kill(self, invocation_id: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `invocation_id` | `str` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Force-stop the sandbox(es) of ``invocation_id``; returns how many were stopped.
```

## jane_handler_runtime.sandbox.read_limited

**Функція.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:135](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L135).

```python
def read_limited(stream: io.BufferedIOBase | None, limit: int) -> tuple[bytes, bool]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `stream` | `io.BufferedIOBase \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `tuple[bytes, bool]`.

## jane_handler_runtime.sandbox.SubprocessSandbox

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:142](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L142).

```python
class SubprocessSandbox:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsubprocesssandboxname) | Поле | ні |
| [enforces_memory_limit](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsubprocesssandboxenforces_memory_limit) | Поле | ні |
| [__init__](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsubprocesssandbox__init__) | Конструктор | ні |
| [allowed](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsubprocesssandboxallowed) | Поле екземпляра | ні |
| [kill_grace_ms](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsubprocesssandboxkill_grace_ms) | Поле екземпляра | ні |
| [kill](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsubprocesssandboxkill) | Метод | ні |
| [ping](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsubprocesssandboxping) | Метод | ні |
| [run](jane_handler_runtime.sandbox.md#jane_handler_runtimesandboxsubprocesssandboxrun) | Метод | ні |

### Опис із вихідного коду

```text
Runs the runner as a local process. **No isolation** (no network block, no FS or memory limits):
only for trusted packages in local development and unit tests; refused unless explicitly allowed.

Without a memory limit a SIGKILL cannot be attributed to ``memory_mb``: it stays ``execution_error``.
```

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_classification.py:106](../../../../../../services/handler-runtime/tests/test_classification.py#L106).

```python
executor, prep = await prepared(subprocess_settings, SubprocessSandbox(allowed=True), h)
```

## jane_handler_runtime.sandbox.SubprocessSandbox.name

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:148](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L148).

```python
name = 'subprocess'
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.sandbox.SubprocessSandbox.enforces_memory_limit

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:149](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L149).

```python
enforces_memory_limit = False
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.sandbox.SubprocessSandbox.__init__

**Конструктор.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:151](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L151).

```python
def __init__(self, allowed: bool, kill_grace_ms: int=0) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `allowed` | `bool` | `—` | positional-or-keyword |
| `kill_grace_ms` | `int` | `0` | positional-or-keyword |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_classification.py:106](../../../../../../services/handler-runtime/tests/test_classification.py#L106).

```python
executor, prep = await prepared(subprocess_settings, SubprocessSandbox(allowed=True), h)
```

## jane_handler_runtime.sandbox.SubprocessSandbox.allowed

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:152](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L152).

```python
self.allowed = allowed
```

## jane_handler_runtime.sandbox.SubprocessSandbox.kill_grace_ms

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:153](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L153).

```python
self.kill_grace_ms = kill_grace_ms
```

## jane_handler_runtime.sandbox.SubprocessSandbox.kill

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:157](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L157).

```python
def kill(self, invocation_id: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `invocation_id` | `str` | `—` | positional-or-keyword |

Результат: `int`.

## jane_handler_runtime.sandbox.SubprocessSandbox.ping

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:165](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L165).

```python
def ping(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `SandboxUnavailable`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_handler_runtime.sandbox.SubprocessSandbox.run

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/sandbox.py:172](../../../../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py#L172).

```python
def run(self, image: str, bundle: Bundle, limits: SandboxLimits, labels: Mapping[str, str]) -> SandboxOutcome:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `image` | `str` | `—` | positional-or-keyword |
| `bundle` | `Bundle` | `—` | positional-or-keyword |
| `limits` | `SandboxLimits` | `—` | positional-or-keyword |
| `labels` | `Mapping[str, str]` | `—` | positional-or-keyword |

Результат: `SandboxOutcome`.
