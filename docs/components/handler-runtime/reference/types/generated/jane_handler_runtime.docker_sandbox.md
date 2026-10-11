# jane_handler_runtime.docker_sandbox

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_handler_runtime.docker_sandbox.SANDBOX_LABEL](#jane_handler_runtimedocker_sandboxsandbox_label)
- [jane_handler_runtime.docker_sandbox.DockerSandbox](#jane_handler_runtimedocker_sandboxdockersandbox)
- [jane_handler_runtime.docker_sandbox.DockerSandbox.name](#jane_handler_runtimedocker_sandboxdockersandboxname)
- [jane_handler_runtime.docker_sandbox.DockerSandbox.enforces_memory_limit](#jane_handler_runtimedocker_sandboxdockersandboxenforces_memory_limit)
- [jane_handler_runtime.docker_sandbox.DockerSandbox.__init__](#jane_handler_runtimedocker_sandboxdockersandbox__init__)
- [jane_handler_runtime.docker_sandbox.DockerSandbox.runtime](#jane_handler_runtimedocker_sandboxdockersandboxruntime)
- [jane_handler_runtime.docker_sandbox.DockerSandbox.user](#jane_handler_runtimedocker_sandboxdockersandboxuser)
- [jane_handler_runtime.docker_sandbox.DockerSandbox.kill_grace_ms](#jane_handler_runtimedocker_sandboxdockersandboxkill_grace_ms)
- [jane_handler_runtime.docker_sandbox.DockerSandbox.extra_labels](#jane_handler_runtimedocker_sandboxdockersandboxextra_labels)
- [jane_handler_runtime.docker_sandbox.DockerSandbox.api](#jane_handler_runtimedocker_sandboxdockersandboxapi)
- [jane_handler_runtime.docker_sandbox.DockerSandbox.ping](#jane_handler_runtimedocker_sandboxdockersandboxping)
- [jane_handler_runtime.docker_sandbox.DockerSandbox.has_image](#jane_handler_runtimedocker_sandboxdockersandboxhas_image)
- [jane_handler_runtime.docker_sandbox.DockerSandbox.run](#jane_handler_runtimedocker_sandboxdockersandboxrun)
- [jane_handler_runtime.docker_sandbox.DockerSandbox.kill](#jane_handler_runtimedocker_sandboxdockersandboxkill)
- [jane_handler_runtime.docker_sandbox.DockerSandbox.cleanup](#jane_handler_runtimedocker_sandboxdockersandboxcleanup)

## jane_handler_runtime.docker_sandbox.SANDBOX_LABEL

**Константа.** Код: [services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py:45](../../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L45).

```python
SANDBOX_LABEL = 'io.jane.handler-runtime.sandbox'
```

## jane_handler_runtime.docker_sandbox.DockerSandbox

**Клас.** Код: [services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py:60](../../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L60).

```python
class DockerSandbox:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_handler_runtime.docker_sandbox.md#jane_handler_runtimedocker_sandboxdockersandboxname) | Поле | ні |
| [enforces_memory_limit](jane_handler_runtime.docker_sandbox.md#jane_handler_runtimedocker_sandboxdockersandboxenforces_memory_limit) | Поле | ні |
| [__init__](jane_handler_runtime.docker_sandbox.md#jane_handler_runtimedocker_sandboxdockersandbox__init__) | Конструктор | ні |
| [runtime](jane_handler_runtime.docker_sandbox.md#jane_handler_runtimedocker_sandboxdockersandboxruntime) | Поле екземпляра | ні |
| [user](jane_handler_runtime.docker_sandbox.md#jane_handler_runtimedocker_sandboxdockersandboxuser) | Поле екземпляра | ні |
| [kill_grace_ms](jane_handler_runtime.docker_sandbox.md#jane_handler_runtimedocker_sandboxdockersandboxkill_grace_ms) | Поле екземпляра | ні |
| [extra_labels](jane_handler_runtime.docker_sandbox.md#jane_handler_runtimedocker_sandboxdockersandboxextra_labels) | Поле екземпляра | ні |
| [api](jane_handler_runtime.docker_sandbox.md#jane_handler_runtimedocker_sandboxdockersandboxapi) | Властивість | ні |
| [ping](jane_handler_runtime.docker_sandbox.md#jane_handler_runtimedocker_sandboxdockersandboxping) | Метод | ні |
| [has_image](jane_handler_runtime.docker_sandbox.md#jane_handler_runtimedocker_sandboxdockersandboxhas_image) | Метод | ні |
| [run](jane_handler_runtime.docker_sandbox.md#jane_handler_runtimedocker_sandboxdockersandboxrun) | Метод | ні |
| [kill](jane_handler_runtime.docker_sandbox.md#jane_handler_runtimedocker_sandboxdockersandboxkill) | Метод | ні |
| [cleanup](jane_handler_runtime.docker_sandbox.md#jane_handler_runtimedocker_sandboxdockersandboxcleanup) | Метод | ні |

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_classification.py:70](../../../../../../services/handler-runtime/tests/test_classification.py#L70).

```python
executor, prep = await prepared(subprocess_settings, DockerSandbox(), h)
```

Контекст і передумови: [services/handler-runtime/tests/test_classification.py:78](../../../../../../services/handler-runtime/tests/test_classification.py#L78).

```python
executor, prep = await prepared(subprocess_settings, DockerSandbox(), h)
```

## jane_handler_runtime.docker_sandbox.DockerSandbox.name

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py:61](../../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L61).

```python
name = 'docker'
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.docker_sandbox.DockerSandbox.enforces_memory_limit

**Поле.** Код: [services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py:62](../../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L62).

```python
enforces_memory_limit = True
```

Доступ: читання — так; запис — так.

## jane_handler_runtime.docker_sandbox.DockerSandbox.__init__

**Конструктор.** Код: [services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py:64](../../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L64).

```python
def __init__(self, *, base_url: str | None=None, runtime: str | None=None, user: str='65534:65534', api_timeout_s: float=60.0, kill_grace_ms: int=2000, extra_labels: Mapping[str, str] | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `base_url` | `str \| None` | `None` | keyword-only |
| `runtime` | `str \| None` | `None` | keyword-only |
| `user` | `str` | `'65534:65534'` | keyword-only |
| `api_timeout_s` | `float` | `60.0` | keyword-only |
| `kill_grace_ms` | `int` | `2000` | keyword-only |
| `extra_labels` | `Mapping[str, str] \| None` | `None` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_classification.py:70](../../../../../../services/handler-runtime/tests/test_classification.py#L70).

```python
executor, prep = await prepared(subprocess_settings, DockerSandbox(), h)
```

Контекст і передумови: [services/handler-runtime/tests/test_classification.py:78](../../../../../../services/handler-runtime/tests/test_classification.py#L78).

```python
executor, prep = await prepared(subprocess_settings, DockerSandbox(), h)
```

## jane_handler_runtime.docker_sandbox.DockerSandbox.runtime

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py:77](../../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L77).

```python
self.runtime = runtime
```

## jane_handler_runtime.docker_sandbox.DockerSandbox.user

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py:78](../../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L78).

```python
self.user = user
```

## jane_handler_runtime.docker_sandbox.DockerSandbox.kill_grace_ms

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py:79](../../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L79).

```python
self.kill_grace_ms = kill_grace_ms
```

## jane_handler_runtime.docker_sandbox.DockerSandbox.extra_labels

**Поле екземпляра.** Код: [services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py:80](../../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L80).

```python
self.extra_labels = dict(extra_labels or {})
```

## jane_handler_runtime.docker_sandbox.DockerSandbox.api

**Властивість.** Код: [services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py:87](../../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L87).

```python
def api(self) -> Any:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `Any`.

Доступ: читання — так; запис — ні.

Явні `raise` у тілі: `SandboxUnavailable`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_isolation.py:109](../../../../../../services/handler-runtime/tests/test_isolation.py#L109).

```python
api = engine.api
```

Контекст і передумови: [services/handler-runtime/tests/test_isolation.py:55](../../../../../../services/handler-runtime/tests/test_isolation.py#L55).

```python
leftovers = sandbox.api.containers(all=True, filters={"label": [f"{SESSION_LABEL}={SESSION}"]})
```

## jane_handler_runtime.docker_sandbox.DockerSandbox.ping

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py:100](../../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L100).

```python
def ping(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `SandboxUnavailable`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_isolation.py:39](../../../../../../services/handler-runtime/tests/test_isolation.py#L39).

```python
sandbox.ping()
```

## jane_handler_runtime.docker_sandbox.DockerSandbox.has_image

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py:106](../../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L106).

```python
def has_image(self, image: str) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `image` | `str` | `—` | positional-or-keyword |

Результат: `bool`.

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_isolation.py:42](../../../../../../services/handler-runtime/tests/test_isolation.py#L42).

```python
sandbox.has_image(IMAGE)
```

## jane_handler_runtime.docker_sandbox.DockerSandbox.run

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py:113](../../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L113).

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

Явні `raise` у тілі: `SandboxUnavailable`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_handler_runtime.docker_sandbox.DockerSandbox.kill

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py:224](../../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L224).

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
Stop the sandbox of an invocation (job cancel), on this engine, by label.

A run of this process is marked first, so its outcome says the runtime (not the OOM killer) sent the
SIGKILL. A container of another instance on a shared engine is killed too; that instance discards the
result of a cancelled job anyway.
```

## jane_handler_runtime.docker_sandbox.DockerSandbox.cleanup

**Метод.** Код: [services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py:241](../../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L241).

```python
def cleanup(self, label_selector: Mapping[str, str]) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `label_selector` | `Mapping[str, str]` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Remove sandbox containers matching labels (stale ones after a crash; tests).
```

### Приклади з тестів

Контекст і передумови: [services/handler-runtime/tests/test_isolation.py:54](../../../../../../services/handler-runtime/tests/test_isolation.py#L54).

```python
sandbox.cleanup({SESSION_LABEL: SESSION})
```
