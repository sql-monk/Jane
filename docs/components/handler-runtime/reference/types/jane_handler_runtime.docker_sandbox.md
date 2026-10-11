# Модуль `jane_handler_runtime.docker_sandbox`

> Згенеровано `scripts/docs_reference.py` з [services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py](../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py). Не редагуйте вручну.

Docker/Podman backend (ADR-0003): one fresh container per invocation through the Engine API.

Container settings - every number comes from ``limits.sandbox``:

* ``network_mode=none`` (no interfaces but loopback), no host volumes, no secrets in the environment;
* read-only root FS, ``tmpfs`` ``/tmp`` (``tmpfs_mb``), non-root user, ``cap_drop=ALL``, ``no-new-privileges``, default seccomp, optional OCI runtime (``runsc``);
* ``memory_mb`` (swap disabled: ``memswap == memory``), ``cpu_cores`` (``nano_cpus``), ``max_processes`` (``pids_limit``);
* the workdir (package + request + inputs) is copied into an anonymous volume ``/work`` before start, owned by root with read-only modes; the volume is removed together with the container;
* ``wall_time_ms``: the runtime kills the container when it is exceeded (``failed``/``timeout``), and inside the container ``timeout -s KILL`` fires ``kill_grace_ms`` later as a safety net if the runtime itself died;
* stdout/stderr are read up to ``max_output_bytes``;
* OOM: ``State.OOMKilled`` is only a hint - the engine may not have it set yet when the container is inspected right after exit (the OOM event races the exit event), and the cgroup OOM killer usually stops the Python child, so PID 1 (``timeout``) exits with ``128 + 9``. The outcome therefore also carries the exit code and whether the runtime killed the container itself (cancel); the executor classifies an unexplained SIGKILL as ``resource_exceeded`` (``enforces_memory_limit``).

## Класи

### Клас `DockerSandbox`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_handler_runtime.docker_sandbox` |
| Код | [docker_sandbox.py:60](../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L60) |

```python
class DockerSandbox: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `api` | `Any` | — | читання (властивість) |  |

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `name` | `'docker'` |  |
| `enforces_memory_limit` | `True` |  |

#### Конструктор `DockerSandbox.__init__`

```python
def __init__(
    self,
    *,
    base_url: str | None = None,
    runtime: str | None = None,
    user: str = '65534:65534',
    api_timeout_s: float = 60.0,
    kill_grace_ms: int = 2000,
    extra_labels: Mapping[str, str] | None = None,
) -> None: ...
```

Код: [docker_sandbox.py:64](../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L64).

#### Метод `DockerSandbox.ping`

```python
def ping(self) -> None: ...
```

Винятки в коді методу: `SandboxUnavailable`.

Код: [docker_sandbox.py:100](../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L100).

#### Метод `DockerSandbox.has_image`

```python
def has_image(self, image: str) -> bool: ...
```

Код: [docker_sandbox.py:106](../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L106).

#### Метод `DockerSandbox.run`

```python
def run(
    self,
    image: str,
    bundle: Bundle,
    limits: SandboxLimits,
    labels: Mapping[str, str],
) -> SandboxOutcome: ...
```

Винятки в коді методу: `SandboxUnavailable`.

Код: [docker_sandbox.py:113](../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L113).

#### Метод `DockerSandbox.kill`

```python
def kill(self, invocation_id: str) -> int: ...
```

Stop the sandbox of an invocation (job cancel), on this engine, by label.

A run of this process is marked first, so its outcome says the runtime (not the OOM killer) sent the SIGKILL. A container of another instance on a shared engine is killed too; that instance discards the result of a cancelled job anyway.

Код: [docker_sandbox.py:224](../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L224).

#### Метод `DockerSandbox.cleanup`

```python
def cleanup(self, label_selector: Mapping[str, str]) -> int: ...
```

Remove sandbox containers matching labels (stale ones after a crash; tests).

Код: [docker_sandbox.py:241](../../../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py#L241).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `SANDBOX_LABEL` | — | `'io.jane.handler-runtime.sandbox'` |  |
