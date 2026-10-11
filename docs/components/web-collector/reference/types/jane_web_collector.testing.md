# Модуль `jane_web_collector.testing`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/testing.py](../../../../../services/web-collector/src/jane_web_collector/testing.py). Не редагуйте вручну.

Test helpers for the Web Collector API (this service's tests; usable by WP-03 and WP-13 too).

Only the standard library, httpx and the service itself: the testsite fixture lives in ``tests/conftest.py``. Clients may be ``httpx.Client`` or FastAPI ``TestClient`` (a subclass of it).

How long the helpers wait comes from the environment, so a loaded machine (a full ``just check``, parallel agents) can be given more time without touching the tests; a wait is an upper bound, never a pass condition:

* ``JANE_WEB_COLLECTOR_TEST_START_S`` (120): a service process answers ``/v1/health`` (:meth:`ServiceProcess.start`);
* ``JANE_WEB_COLLECTOR_TEST_WAIT_S`` (120): an awaited event happens - a collection finishes, the stream ends, a cancellation takes effect (:func:`wait_done`, :func:`drain`, :func:`wait_timeout_s` in tests).

## Зміст

- [Клас `ServiceProcess`](#клас-serviceprocess)
- [Клас `Site`](#клас-site)
- [Функція `drain`](#функція-drain)
- [Функція `errors`](#функція-errors)
- [Функція `free_port`](#функція-free_port)
- [Функція `make_settings`](#функція-make_settings)
- [Функція `start`](#функція-start)
- [Функція `start_timeout_s`](#функція-start_timeout_s)
- [Функція `wait_done`](#функція-wait_done)
- [Функція `wait_timeout_s`](#функція-wait_timeout_s)
- [Функція `web_rules`](#функція-web_rules)

## Класи

### Клас `ServiceProcess`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_web_collector.testing` |
| Код | [testing.py:209](../../../../../services/web-collector/src/jane_web_collector/testing.py#L209) |

```python
@dataclass
class ServiceProcess: ...
```

The collector as a separate OS process (what a third-party application talks to).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `port` | `int` | — | читання й запис |  |
| `state_dir` | `Path` | — | читання й запис |  |
| `env` | `dict[str, str]` | — | читання й запис |  |
| `proc` | `subprocess.Popen[bytes] \| None` | `None` | читання й запис |  |
| `log_path` | `Path \| None` | `None` | читання й запис |  |
| `base` | `str` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `ServiceProcess.client`

```python
def client(self) -> httpx.Client: ...
```

A client of this process for a test: request timeout :func:`wait_timeout_s`, and an idle pooled connection is dropped after ``CLIENT_KEEPALIVE_EXPIRY_S``, long before the service closes it. A client that keeps idle connections as long as the server (5 s in both httpx and uvicorn) may send a request on a connection the server is closing at that moment and get ``httpx.ReadError`` (WinError 10054 under load).

Код: [testing.py:222](../../../../../services/web-collector/src/jane_web_collector/testing.py#L222).

#### Метод `ServiceProcess.start`

```python
def start(self, timeout: float = START_TIMEOUT_S) -> None: ...
```

Start the process and wait for ``/v1/health`` (``timeout`` defaults to ``START_TIMEOUT_S``).

Винятки в коді методу: `AssertionError`.

Код: [testing.py:233](../../../../../services/web-collector/src/jane_web_collector/testing.py#L233).

#### Метод `ServiceProcess.kill`

```python
def kill(self) -> None: ...
```

Hard kill (SIGKILL on Linux, TerminateProcess on Windows): no graceful shutdown at all.

The whole process tree is killed: on Windows a venv's ``python.exe`` is a launcher whose child is the real interpreter (psutil, a dev dependency, is used when available).

Код: [testing.py:257](../../../../../services/web-collector/src/jane_web_collector/testing.py#L257).

#### Метод `ServiceProcess.stop`

```python
def stop(self) -> None: ...
```

Код: [testing.py:276](../../../../../services/web-collector/src/jane_web_collector/testing.py#L276).

#### Метод `ServiceProcess.environment`

```python
@staticmethod
def environment(port: int, state_dir: Path, **overrides: str) -> dict[str, str]: ...
```

Код: [testing.py:281](../../../../../services/web-collector/src/jane_web_collector/testing.py#L281).

### Клас `Site`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_web_collector.testing` |
| Код | [testing.py:113](../../../../../services/web-collector/src/jane_web_collector/testing.py#L113) |

```python
@dataclass
class Site: ...
```

A running test site: base URL plus a log of requested paths and User-Agents.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `base` | `str` | — | читання й запис |  |
| `requests` | `Counter[str]` | `field(default_factory=Counter)` | читання й запис |  |
| `user_agents` | `set[str]` | `field(default_factory=set)` | читання й запис |  |
| `lock` | `threading.Lock` | `field(default_factory=threading.Lock)` | читання й запис |  |
| `host` | `str` | — | читання (властивість) |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `Site.url`

```python
def url(self, path: str) -> str: ...
```

Код: [testing.py:125](../../../../../services/web-collector/src/jane_web_collector/testing.py#L125).

#### Метод `Site.canonical`

```python
def canonical(self, paths: set[str] | list[str]) -> set[str]: ...
```

Root-relative paths -> canonical URLs (same normalization as the default test rules).

Код: [testing.py:128](../../../../../services/web-collector/src/jane_web_collector/testing.py#L128).

#### Метод `Site.reset`

```python
def reset(self) -> None: ...
```

Код: [testing.py:133](../../../../../services/web-collector/src/jane_web_collector/testing.py#L133).

## Функції

### Функція `drain`

```python
def drain(
    client: httpx.Client,
    cid: str,
    *,
    limit: int = 50,
    timeout: float | None = None,
) -> list[dict[str, Any]]: ...
```

Pull every material (acknowledging each page with ``after``) until ``end_of_stream``.

Винятки в коді функції: `AssertionError`.

Код: [testing.py:167](../../../../../services/web-collector/src/jane_web_collector/testing.py#L167).

### Функція `errors`

```python
def errors(client: httpx.Client, cid: str) -> list[dict[str, Any]]: ...
```

Код: [testing.py:186](../../../../../services/web-collector/src/jane_web_collector/testing.py#L186).

### Функція `free_port`

```python
def free_port() -> int: ...
```

Код: [testing.py:198](../../../../../services/web-collector/src/jane_web_collector/testing.py#L198).

### Функція `make_settings`

```python
def make_settings(tmp: Path, **overrides: Any) -> Settings: ...
```

Settings for an in-process test app: state in ``tmp``, no WP-03 package unless given.

Код: [testing.py:98](../../../../../services/web-collector/src/jane_web_collector/testing.py#L98).

### Функція `start`

```python
def start(client: httpx.Client, body: dict[str, Any], key: str | None = None) -> str: ...
```

Код: [testing.py:150](../../../../../services/web-collector/src/jane_web_collector/testing.py#L150).

### Функція `start_timeout_s`

```python
def start_timeout_s() -> float: ...
```

How long a service process may take to become healthy (``JANE_WEB_COLLECTOR_TEST_START_S``).

Код: [testing.py:71](../../../../../services/web-collector/src/jane_web_collector/testing.py#L71).

### Функція `wait_done`

```python
def wait_done(client: httpx.Client, cid: str, timeout: float | None = None) -> dict[str, Any]: ...
```

Винятки в коді функції: `AssertionError`.

Код: [testing.py:156](../../../../../services/web-collector/src/jane_web_collector/testing.py#L156).

### Функція `wait_timeout_s`

```python
def wait_timeout_s() -> float: ...
```

Upper bound for an awaited event in a test (``JANE_WEB_COLLECTOR_TEST_WAIT_S``).

Код: [testing.py:76](../../../../../services/web-collector/src/jane_web_collector/testing.py#L76).

### Функція `web_rules`

```python
def web_rules(site: Site, **overrides: Any) -> dict[str, Any]: ...
```

Home page + recursion inside the site host, without the /calendar/ trap, without utm_* params.

Код: [testing.py:138](../../../../../services/web-collector/src/jane_web_collector/testing.py#L138).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `FAST_LIMITS` | `dict[str, Any]` | `{'rate': {'requests_per_second_per_host': 500, 'min_delay_ms_per_host': 0}, 'con` | Politeness limits for a local test site: fast, but still through the per-host limiter. |
| `REPO_ROOT` | — | `Path(__file__).resolve().parents[4]` | Checkout root (``services/web-collector/src/jane_web_collector`` -> repository), for ``contracts/``. |
| `START_TIMEOUT_S` | — | `start_timeout_s()` | Default of :meth:`ServiceProcess.start`, read once at import (a plain ``float`` default keeps subclasses that override ``start(timeout: float = ...)``, such as the WP-03 fixture, type-compatible). |
| `ServiceFactory` | — | `Callable[..., 'ServiceProcess']` | Type of the ``service_factory`` fixture: ``factory(state_dir=None, **env) -> ServiceProcess``. |
