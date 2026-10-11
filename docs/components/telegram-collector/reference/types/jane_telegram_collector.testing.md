# Модуль `jane_telegram_collector.testing`

> Згенеровано `scripts/docs_reference.py` з [services/telegram-collector/src/jane_telegram_collector/testing.py](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py). Не редагуйте вручну.

Test helpers for the Telegram Collector API (this service's tests; usable by WP-13 too).

Only the standard library, httpx and the service itself. Clients may be ``httpx.Client`` or FastAPI ``TestClient`` (a subclass of it). Channels are recordings (:class:`~jane_telegram_collector.recorded.Recording`).

## Зміст

- [Клас `ServiceProcess`](#клас-serviceprocess)
- [Функція `drain`](#функція-drain)
- [Функція `errors`](#функція-errors)
- [Функція `free_port`](#функція-free_port)
- [Функція `make_channel`](#функція-make_channel)
- [Функція `make_settings`](#функція-make_settings)
- [Функція `page`](#функція-page)
- [Функція `start`](#функція-start)
- [Функція `telegram_rules`](#функція-telegram_rules)
- [Функція `wait_done`](#функція-wait_done)

## Класи

### Клас `ServiceProcess`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_telegram_collector.testing` |
| Код | [testing.py:166](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L166) |

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

Код: [testing.py:179](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L179).

#### Метод `ServiceProcess.start`

```python
def start(self, timeout: float = 30) -> None: ...
```

Винятки в коді методу: `AssertionError`.

Код: [testing.py:182](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L182).

#### Метод `ServiceProcess.suspend`

```python
def suspend(self) -> None: ...
```

Freeze the process tree (a stalled owner: alive, but not renewing its lease).

Код: [testing.py:215](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L215).

#### Метод `ServiceProcess.resume`

```python
def resume(self) -> None: ...
```

Код: [testing.py:221](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L221).

#### Метод `ServiceProcess.kill`

```python
def kill(self) -> None: ...
```

Hard kill of the whole process tree (on Windows a venv ``python.exe`` is a launcher with a child).

Код: [testing.py:226](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L226).

#### Метод `ServiceProcess.stop`

```python
def stop(self) -> None: ...
```

Код: [testing.py:237](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L237).

#### Метод `ServiceProcess.log`

```python
def log(self) -> str: ...
```

Код: [testing.py:241](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L241).

#### Метод `ServiceProcess.environment`

```python
@staticmethod
def environment(
    port: int,
    state_dir: Path,
    recordings_dir: Path,
    **overrides: str,
) -> dict[str, str]: ...
```

Код: [testing.py:245](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L245).

## Функції

### Функція `drain`

```python
def drain(
    client: httpx.Client,
    cid: str,
    *,
    limit: int = 50,
    timeout: float = 60,
) -> list[dict[str, Any]]: ...
```

Pull every material (acknowledging each page with ``after``) until ``end_of_stream``.

Винятки в коді функції: `AssertionError`.

Код: [testing.py:127](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L127).

### Функція `errors`

```python
def errors(client: httpx.Client, cid: str) -> list[dict[str, Any]]: ...
```

Код: [testing.py:143](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L143).

### Функція `free_port`

```python
def free_port() -> int: ...
```

Код: [testing.py:155](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L155).

### Функція `make_channel`

```python
def make_channel(
    root: Path,
    count: int,
    *,
    username: str = USERNAME,
    channel_id: str = CHANNEL_ID,
) -> Recording: ...
```

A recorded channel with ``count`` messages, one per minute from :data:`T0`.

Код: [testing.py:61](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L61).

### Функція `make_settings`

```python
def make_settings(tmp: Path, **overrides: Any) -> Settings: ...
```

Settings for an in-process test app: state and recordings in ``tmp``.

Код: [testing.py:72](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L72).

### Функція `page`

```python
def page(
    client: httpx.Client,
    cid: str,
    after: str | None = None,
    **params: Any,
) -> dict[str, Any]: ...
```

Код: [testing.py:113](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L113).

### Функція `start`

```python
def start(client: httpx.Client, body: dict[str, Any], key: str | None = None) -> str: ...
```

Код: [testing.py:95](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L95).

### Функція `telegram_rules`

```python
def telegram_rules(*channels: str, **overrides: Any) -> dict[str, Any]: ...
```

Rules for channels given as usernames or ``-100...`` ids.

Код: [testing.py:87](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L87).

### Функція `wait_done`

```python
def wait_done(client: httpx.Client, cid: str, timeout: float = 60) -> dict[str, Any]: ...
```

Винятки в коді функції: `AssertionError`.

Код: [testing.py:102](../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L102).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `CHANNEL_ID` | — | `'-1001234567890'` |  |
| `FAST_LIMITS` | `dict[str, Any]` | `{'rate': {'min_delay_ms_per_host': 0}, 'retries': {'max_attempts': 2, 'initial_b` | No pacing between calls to a recorded channel, one quick retry. |
| `REPO_ROOT` | — | `Path(__file__).resolve().parents[4]` | Checkout root (``services/telegram-collector/src/jane_telegram_collector`` -> repository), for ``contracts/``. |
| `T0` | — | `datetime(2026, 9, 1, 10, 0, tzinfo=UTC)` |  |
| `USERNAME` | — | `'city_events_example'` |  |
| `ServiceFactory` | — | `Callable[..., 'ServiceProcess']` | Type of the ``service_factory`` fixture: ``factory(state_dir=None, **env) -> ServiceProcess``. |

## Реекспорт

| Назва | Визначено в |
|---|---|
| `Recording` | [`jane_telegram_collector.recorded`](jane_telegram_collector.recorded.md) |
