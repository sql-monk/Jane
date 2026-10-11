# jane_telegram_collector.testing

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_telegram_collector.testing.Recording](#jane_telegram_collectortestingrecording)
- [jane_telegram_collector.testing.FAST_LIMITS](#jane_telegram_collectortestingfast_limits)
- [jane_telegram_collector.testing.REPO_ROOT](#jane_telegram_collectortestingrepo_root)
- [jane_telegram_collector.testing.CHANNEL_ID](#jane_telegram_collectortestingchannel_id)
- [jane_telegram_collector.testing.USERNAME](#jane_telegram_collectortestingusername)
- [jane_telegram_collector.testing.T0](#jane_telegram_collectortestingt0)
- [jane_telegram_collector.testing.make_channel](#jane_telegram_collectortestingmake_channel)
- [jane_telegram_collector.testing.make_settings](#jane_telegram_collectortestingmake_settings)
- [jane_telegram_collector.testing.telegram_rules](#jane_telegram_collectortestingtelegram_rules)
- [jane_telegram_collector.testing.start](#jane_telegram_collectortestingstart)
- [jane_telegram_collector.testing.wait_done](#jane_telegram_collectortestingwait_done)
- [jane_telegram_collector.testing.page](#jane_telegram_collectortestingpage)
- [jane_telegram_collector.testing.drain](#jane_telegram_collectortestingdrain)
- [jane_telegram_collector.testing.errors](#jane_telegram_collectortestingerrors)
- [jane_telegram_collector.testing.free_port](#jane_telegram_collectortestingfree_port)
- [jane_telegram_collector.testing.ServiceFactory](#jane_telegram_collectortestingservicefactory)
- [jane_telegram_collector.testing.ServiceProcess](#jane_telegram_collectortestingserviceprocess)
- [jane_telegram_collector.testing.ServiceProcess.__init__](#jane_telegram_collectortestingserviceprocess__init__)
- [jane_telegram_collector.testing.ServiceProcess.port](#jane_telegram_collectortestingserviceprocessport)
- [jane_telegram_collector.testing.ServiceProcess.state_dir](#jane_telegram_collectortestingserviceprocessstate_dir)
- [jane_telegram_collector.testing.ServiceProcess.env](#jane_telegram_collectortestingserviceprocessenv)
- [jane_telegram_collector.testing.ServiceProcess.proc](#jane_telegram_collectortestingserviceprocessproc)
- [jane_telegram_collector.testing.ServiceProcess.log_path](#jane_telegram_collectortestingserviceprocesslog_path)
- [jane_telegram_collector.testing.ServiceProcess.base](#jane_telegram_collectortestingserviceprocessbase)
- [jane_telegram_collector.testing.ServiceProcess.client](#jane_telegram_collectortestingserviceprocessclient)
- [jane_telegram_collector.testing.ServiceProcess.start](#jane_telegram_collectortestingserviceprocessstart)
- [jane_telegram_collector.testing.ServiceProcess.suspend](#jane_telegram_collectortestingserviceprocesssuspend)
- [jane_telegram_collector.testing.ServiceProcess.resume](#jane_telegram_collectortestingserviceprocessresume)
- [jane_telegram_collector.testing.ServiceProcess.kill](#jane_telegram_collectortestingserviceprocesskill)
- [jane_telegram_collector.testing.ServiceProcess.stop](#jane_telegram_collectortestingserviceprocessstop)
- [jane_telegram_collector.testing.ServiceProcess.log](#jane_telegram_collectortestingserviceprocesslog)
- [jane_telegram_collector.testing.ServiceProcess.environment](#jane_telegram_collectortestingserviceprocessenvironment)

## jane_telegram_collector.testing.Recording

**Повторний експорт.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:23](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L23).

```python
from jane_telegram_collector.recorded import Recording as Recording
```

Повторний експорт: [jane_telegram_collector.recorded.Recording](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecording).

## jane_telegram_collector.testing.FAST_LIMITS

**Константа.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:46](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L46).

```python
FAST_LIMITS: dict[str, Any] = {'rate': {'min_delay_ms_per_host': 0}, 'retries': {'max_attempts': 2, 'initial_backoff_ms': 0, 'max_backoff_ms': 0}}
```

### Опис із вихідного коду

```text
No pacing between calls to a recorded channel, one quick retry.
```

## jane_telegram_collector.testing.REPO_ROOT

**Константа.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:52](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L52).

```python
REPO_ROOT = Path(__file__).resolve().parents[4]
```

### Опис із вихідного коду

```text
Checkout root (``services/telegram-collector/src/jane_telegram_collector`` -> repository), for ``contracts/``.
```

## jane_telegram_collector.testing.CHANNEL_ID

**Константа.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:56](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L56).

```python
CHANNEL_ID = '-1001234567890'
```

## jane_telegram_collector.testing.USERNAME

**Константа.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:57](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L57).

```python
USERNAME = 'city_events_example'
```

## jane_telegram_collector.testing.T0

**Константа.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:58](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L58).

```python
T0 = datetime(2026, 9, 1, 10, 0, tzinfo=UTC)
```

## jane_telegram_collector.testing.make_channel

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:61](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L61).

```python
def make_channel(root: Path, count: int, *, username: str=USERNAME, channel_id: str=CHANNEL_ID) -> Recording:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `root` | `Path` | `—` | positional-or-keyword |
| `count` | `int` | `—` | positional-or-keyword |
| `username` | `str` | `USERNAME` | keyword-only |
| `channel_id` | `str` | `CHANNEL_ID` | keyword-only |

Результат: `Recording`.

### Опис із вихідного коду

```text
A recorded channel with ``count`` messages, one per minute from :data:`T0`.
```

### Приклади з тестів

Контекст і передумови: [services/telegram-collector/tests/conftest.py:56](../../../../../../services/telegram-collector/tests/conftest.py#L56).

```python
return make_channel(settings.recordings_dir, 25)
```

Контекст і передумови: [services/telegram-collector/tests/test_processes.py:92](../../../../../../services/telegram-collector/tests/test_processes.py#L92).

```python
make_channel(tmp_path / "recordings", 12)
```

## jane_telegram_collector.testing.make_settings

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:72](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L72).

```python
def make_settings(tmp: Path, **overrides: Any) -> Settings:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `tmp` | `Path` | `—` | positional-or-keyword |
| `overrides` | `Any` | `—` | var-keyword |

Результат: `Settings`.

### Опис із вихідного коду

```text
Settings for an in-process test app: state and recordings in ``tmp``.
```

### Приклади з тестів

Контекст і передумови: [services/telegram-collector/tests/conftest.py:44](../../../../../../services/telegram-collector/tests/conftest.py#L44).

```python
return make_settings(tmp_path)
```

Контекст і передумови: [services/telegram-collector/tests/test_limits_and_access.py:135](../../../../../../services/telegram-collector/tests/test_limits_and_access.py#L135).

```python
settings = make_settings(tmp_path)
```

## jane_telegram_collector.testing.telegram_rules

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:87](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L87).

```python
def telegram_rules(*channels: str, **overrides: Any) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `channels` | `str` | `—` | var-positional |
| `overrides` | `Any` | `—` | var-keyword |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
Rules for channels given as usernames or ``-100...`` ids.
```

### Приклади з тестів

Контекст і передумови: [services/telegram-collector/tests/test_collect.py:80](../../../../../../services/telegram-collector/tests/test_collect.py#L80).

```python
rules = telegram_rules(
        USERNAME, history={"since": (T0 + timedelta(minutes=20)).isoformat().replace("+00:00", "Z")}
    )
```

Контекст і передумови: [services/telegram-collector/tests/test_collect.py:85](../../../../../../services/telegram-collector/tests/test_collect.py#L85).

```python
rules = telegram_rules(USERNAME, history={"from_message_id": 23})
```

## jane_telegram_collector.testing.start

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:95](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L95).

```python
def start(client: httpx.Client, body: dict[str, Any], key: str | None=None) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `httpx.Client` | `—` | positional-or-keyword |
| `body` | `dict[str, Any]` | `—` | positional-or-keyword |
| `key` | `str \| None` | `None` | positional-or-keyword |

Результат: `str`.

### Приклади з тестів

Контекст і передумови: [services/telegram-collector/tests/test_collect.py:40](../../../../../../services/telegram-collector/tests/test_collect.py#L40).

```python
cid = start(client, body)
```

Контекст і передумови: [services/telegram-collector/tests/test_collect.py:165](../../../../../../services/telegram-collector/tests/test_collect.py#L165).

```python
cid = start(client, {"source_kind": "telegram", "rules": telegram_rules(USERNAME), "state_key": "s1"})
```

## jane_telegram_collector.testing.wait_done

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:102](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L102).

```python
def wait_done(client: httpx.Client, cid: str, timeout: float=60) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `httpx.Client` | `—` | positional-or-keyword |
| `cid` | `str` | `—` | positional-or-keyword |
| `timeout` | `float` | `60` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `AssertionError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [services/telegram-collector/tests/test_collect.py:166](../../../../../../services/telegram-collector/tests/test_collect.py#L166).

```python
wait_done(client, cid)
```

Контекст і передумови: [services/telegram-collector/tests/test_collect.py:297](../../../../../../services/telegram-collector/tests/test_collect.py#L297).

```python
wait_done(client, first.json()["job_id"])
```

## jane_telegram_collector.testing.page

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:113](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L113).

```python
def page(client: httpx.Client, cid: str, after: str | None=None, **params: Any) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `httpx.Client` | `—` | positional-or-keyword |
| `cid` | `str` | `—` | positional-or-keyword |
| `after` | `str \| None` | `None` | positional-or-keyword |
| `params` | `Any` | `—` | var-keyword |

Результат: `dict[str, Any]`.

### Приклади з тестів

Контекст і передумови: [services/telegram-collector/tests/test_collect.py:167](../../../../../../services/telegram-collector/tests/test_collect.py#L167).

```python
one = page(client, cid, limit=10)
```

Контекст і передумови: [services/telegram-collector/tests/test_collect.py:168](../../../../../../services/telegram-collector/tests/test_collect.py#L168).

```python
again = page(client, cid, limit=10)
```

## jane_telegram_collector.testing.drain

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:127](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L127).

```python
def drain(client: httpx.Client, cid: str, *, limit: int=50, timeout: float=60) -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `httpx.Client` | `—` | positional-or-keyword |
| `cid` | `str` | `—` | positional-or-keyword |
| `limit` | `int` | `50` | keyword-only |
| `timeout` | `float` | `60` | keyword-only |

Результат: `list[dict[str, Any]]`.

Явні `raise` у тілі: `AssertionError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Pull every material (acknowledging each page with ``after``) until ``end_of_stream``.
```

### Приклади з тестів

Контекст і передумови: [services/telegram-collector/tests/test_collect.py:41](../../../../../../services/telegram-collector/tests/test_collect.py#L41).

```python
items = drain(client, cid)
```

Контекст і передумови: [services/telegram-collector/tests/test_collect.py:216](../../../../../../services/telegram-collector/tests/test_collect.py#L216).

```python
items = drain(client, cid)
```

## jane_telegram_collector.testing.errors

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:143](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L143).

```python
def errors(client: httpx.Client, cid: str) -> list[dict[str, Any]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `client` | `httpx.Client` | `—` | positional-or-keyword |
| `cid` | `str` | `—` | positional-or-keyword |

Результат: `list[dict[str, Any]]`.

### Приклади з тестів

Контекст і передумови: [services/telegram-collector/tests/test_limits_and_access.py:70](../../../../../../services/telegram-collector/tests/test_limits_and_access.py#L70).

```python
errs = errors(client, cid)
```

Контекст і передумови: [services/telegram-collector/tests/test_limits_and_access.py:106](../../../../../../services/telegram-collector/tests/test_limits_and_access.py#L106).

```python
assert errors(client, cid)[0]["attempts"] == 2
```

## jane_telegram_collector.testing.free_port

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:155](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L155).

```python
def free_port() -> int:
```

Результат: `int`.

### Приклади з тестів

Контекст і передумови: [services/telegram-collector/tests/conftest.py:79](../../../../../../services/telegram-collector/tests/conftest.py#L79).

```python
port = free_port()
```

## jane_telegram_collector.testing.ServiceFactory

**Змінна.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:161](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L161).

```python
ServiceFactory = Callable[..., 'ServiceProcess']
```

### Опис із вихідного коду

```text
Type of the ``service_factory`` fixture: ``factory(state_dir=None, **env) -> ServiceProcess``.
```

## jane_telegram_collector.testing.ServiceProcess

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:166](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L166).

```python
class ServiceProcess:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [port](jane_telegram_collector.testing.md#jane_telegram_collectortestingserviceprocessport) | Поле | ні |
| [state_dir](jane_telegram_collector.testing.md#jane_telegram_collectortestingserviceprocessstate_dir) | Поле | ні |
| [env](jane_telegram_collector.testing.md#jane_telegram_collectortestingserviceprocessenv) | Поле | ні |
| [proc](jane_telegram_collector.testing.md#jane_telegram_collectortestingserviceprocessproc) | Поле | ні |
| [log_path](jane_telegram_collector.testing.md#jane_telegram_collectortestingserviceprocesslog_path) | Поле | ні |
| [base](jane_telegram_collector.testing.md#jane_telegram_collectortestingserviceprocessbase) | Властивість | ні |
| [client](jane_telegram_collector.testing.md#jane_telegram_collectortestingserviceprocessclient) | Метод | ні |
| [start](jane_telegram_collector.testing.md#jane_telegram_collectortestingserviceprocessstart) | Метод | ні |
| [suspend](jane_telegram_collector.testing.md#jane_telegram_collectortestingserviceprocesssuspend) | Метод | ні |
| [resume](jane_telegram_collector.testing.md#jane_telegram_collectortestingserviceprocessresume) | Метод | ні |
| [kill](jane_telegram_collector.testing.md#jane_telegram_collectortestingserviceprocesskill) | Метод | ні |
| [stop](jane_telegram_collector.testing.md#jane_telegram_collectortestingserviceprocessstop) | Метод | ні |
| [log](jane_telegram_collector.testing.md#jane_telegram_collectortestingserviceprocesslog) | Метод | ні |
| [environment](jane_telegram_collector.testing.md#jane_telegram_collectortestingserviceprocessenvironment) | Метод | ні |
| [__init__](jane_telegram_collector.testing.md#jane_telegram_collectortestingserviceprocess__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
The collector as a separate OS process (what a third-party application talks to).
```

## jane_telegram_collector.testing.ServiceProcess.__init__

**Конструктор dataclass.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:166](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L166).

```python
def __init__(self, port: int, state_dir: Path, env: dict[str, str], proc: subprocess.Popen[bytes] | None = None, log_path: Path | None = None) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `port` | `int` | `—` | positional-or-keyword |
| `state_dir` | `Path` | `—` | positional-or-keyword |
| `env` | `dict[str, str]` | `—` | positional-or-keyword |
| `proc` | `subprocess.Popen[bytes] \| None` | `None` | positional-or-keyword |
| `log_path` | `Path \| None` | `None` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.testing.ServiceProcess.port

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:169](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L169).

```python
port: int
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.testing.ServiceProcess.state_dir

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:170](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L170).

```python
state_dir: Path
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.testing.ServiceProcess.env

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:171](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L171).

```python
env: dict[str, str]
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.testing.ServiceProcess.proc

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:172](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L172).

```python
proc: subprocess.Popen[bytes] | None = None
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.testing.ServiceProcess.log_path

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:173](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L173).

```python
log_path: Path | None = None
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.testing.ServiceProcess.base

**Властивість.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:176](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L176).

```python
def base(self) -> str:
```

Декоратори: `property`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

Доступ: читання — так; запис — ні.

## jane_telegram_collector.testing.ServiceProcess.client

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:179](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L179).

```python
def client(self) -> httpx.Client:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `httpx.Client`.

## jane_telegram_collector.testing.ServiceProcess.start

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:182](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L182).

```python
def start(self, timeout: float=30) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `timeout` | `float` | `30` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `AssertionError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_telegram_collector.testing.ServiceProcess.suspend

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:215](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L215).

```python
def suspend(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Freeze the process tree (a stalled owner: alive, but not renewing its lease).
```

## jane_telegram_collector.testing.ServiceProcess.resume

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:221](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L221).

```python
def resume(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.testing.ServiceProcess.kill

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:226](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L226).

```python
def kill(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Hard kill of the whole process tree (on Windows a venv ``python.exe`` is a launcher with a child).
```

## jane_telegram_collector.testing.ServiceProcess.stop

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:237](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L237).

```python
def stop(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.testing.ServiceProcess.log

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:241](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L241).

```python
def log(self) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `str`.

## jane_telegram_collector.testing.ServiceProcess.environment

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/testing.py:245](../../../../../../services/telegram-collector/src/jane_telegram_collector/testing.py#L245).

```python
def environment(port: int, state_dir: Path, recordings_dir: Path, **overrides: str) -> dict[str, str]:
```

Декоратори: `staticmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `port` | `int` | `—` | positional-or-keyword |
| `state_dir` | `Path` | `—` | positional-or-keyword |
| `recordings_dir` | `Path` | `—` | positional-or-keyword |
| `overrides` | `str` | `—` | var-keyword |

Результат: `dict[str, str]`.

### Приклади з тестів

Контекст і передумови: [services/telegram-collector/tests/conftest.py:80](../../../../../../services/telegram-collector/tests/conftest.py#L80).

```python
env = ServiceProcess.environment(
            port,
            state_dir,
            tmp_path / "recordings",
            JANE_TELEGRAM_COLLECTOR_LEASE_SECONDS="3",
            JANE_TELEGRAM_COLLECTOR_HEARTBEAT_INTERVAL_MS="500",
            JANE_TELEGRAM_COLLECTOR_STATE_BUSY_TIMEOUT_MS="1000",
            **env_overrides,
        )
```
