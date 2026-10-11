# jane_web_collector.shared_hosts

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.shared_hosts.RENEWALS_PER_TTL](#jane_web_collectorshared_hostsrenewals_per_ttl)
- [jane_web_collector.shared_hosts.check_ttl](#jane_web_collectorshared_hostscheck_ttl)
- [jane_web_collector.shared_hosts.SharedHosts](#jane_web_collectorshared_hostssharedhosts)
- [jane_web_collector.shared_hosts.SharedHosts.__init__](#jane_web_collectorshared_hostssharedhosts__init__)
- [jane_web_collector.shared_hosts.SharedHosts.state](#jane_web_collectorshared_hostssharedhostsstate)
- [jane_web_collector.shared_hosts.SharedHosts.instance_id](#jane_web_collectorshared_hostssharedhostsinstance_id)
- [jane_web_collector.shared_hosts.SharedHosts.poll_s](#jane_web_collectorshared_hostssharedhostspoll_s)
- [jane_web_collector.shared_hosts.SharedHosts.ttl_s](#jane_web_collectorshared_hostssharedhoststtl_s)
- [jane_web_collector.shared_hosts.SharedHosts.start](#jane_web_collectorshared_hostssharedhostsstart)
- [jane_web_collector.shared_hosts.SharedHosts.release](#jane_web_collectorshared_hostssharedhostsrelease)
- [jane_web_collector.shared_hosts.SharedHosts.push_back](#jane_web_collectorshared_hostssharedhostspush_back)
- [jane_web_collector.shared_hosts.SharedHosts.leave](#jane_web_collectorshared_hostssharedhostsleave)
- [jane_web_collector.shared_hosts.SharedHosts.renew](#jane_web_collectorshared_hostssharedhostsrenew)
- [jane_web_collector.shared_hosts.SharedHosts.aclose](#jane_web_collectorshared_hostssharedhostsaclose)

## jane_web_collector.shared_hosts.RENEWALS_PER_TTL

**Константа.** Код: [services/web-collector/src/jane_web_collector/shared_hosts.py:51](../../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L51).

```python
RENEWALS_PER_TTL = 3
```

### Опис із вихідного коду

```text
Renewals within one ``shared_host_ttl_seconds``: a live row is renewed every ``ttl / 3``.
```

## jane_web_collector.shared_hosts.check_ttl

**Функція.** Код: [services/web-collector/src/jane_web_collector/shared_hosts.py:55](../../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L55).

```python
def check_ttl(ttl_s: float, busy_timeout_ms: int) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `ttl_s` | `float` | `—` | positional-or-keyword |
| `busy_timeout_ms` | `int` | `—` | positional-or-keyword |

Результат: `None`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Start-up rule: a renewal that waited one full SQLite lock wait must still come before the TTL runs out
(``ttl - ttl / 3 > busy timeout``); otherwise a live instance would lose its slot to another instance.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_shared_host_liveness.py:150](../../../../../../services/web-collector/tests/test_shared_host_liveness.py#L150).

```python
check_ttl(120, 10_000)
```

Контекст і передумови: [services/web-collector/tests/test_shared_host_liveness.py:152](../../../../../../services/web-collector/tests/test_shared_host_liveness.py#L152).

```python
check_ttl(3, 2_000)
```

## jane_web_collector.shared_hosts.SharedHosts

**Клас.** Код: [services/web-collector/src/jane_web_collector/shared_hosts.py:65](../../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L65).

```python
class SharedHosts:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.shared_hosts.md#jane_web_collectorshared_hostssharedhosts__init__) | Конструктор | ні |
| [state](jane_web_collector.shared_hosts.md#jane_web_collectorshared_hostssharedhostsstate) | Поле екземпляра | ні |
| [instance_id](jane_web_collector.shared_hosts.md#jane_web_collectorshared_hostssharedhostsinstance_id) | Поле екземпляра | ні |
| [poll_s](jane_web_collector.shared_hosts.md#jane_web_collectorshared_hostssharedhostspoll_s) | Поле екземпляра | ні |
| [ttl_s](jane_web_collector.shared_hosts.md#jane_web_collectorshared_hostssharedhoststtl_s) | Поле екземпляра | ні |
| [start](jane_web_collector.shared_hosts.md#jane_web_collectorshared_hostssharedhostsstart) | Метод | ні |
| [release](jane_web_collector.shared_hosts.md#jane_web_collectorshared_hostssharedhostsrelease) | Метод | ні |
| [push_back](jane_web_collector.shared_hosts.md#jane_web_collectorshared_hostssharedhostspush_back) | Метод | ні |
| [leave](jane_web_collector.shared_hosts.md#jane_web_collectorshared_hostssharedhostsleave) | Метод | ні |
| [renew](jane_web_collector.shared_hosts.md#jane_web_collectorshared_hostssharedhostsrenew) | Метод | ні |
| [aclose](jane_web_collector.shared_hosts.md#jane_web_collectorshared_hostssharedhostsaclose) | Метод | ні |

### Опис із вихідного коду

```text
Cross-instance part of the per-host limits, kept in the shared :class:`~.state.StateStore`.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_shared_host_liveness.py:65](../../../../../../services/web-collector/tests/test_shared_host_liveness.py#L65).

```python
yield (
            SharedHosts(a_store, "instance-a", poll_s=POLL, ttl_s=TTL),
            SharedHosts(b_store, "instance-b", poll_s=POLL, ttl_s=TTL),
        )
```

## jane_web_collector.shared_hosts.SharedHosts.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/shared_hosts.py:68](../../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L68).

```python
def __init__(self, state: StateStore, instance_id: str, *, poll_s: float, ttl_s: float) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `state` | `StateStore` | `—` | positional-or-keyword |
| `instance_id` | `str` | `—` | positional-or-keyword |
| `poll_s` | `float` | `—` | keyword-only |
| `ttl_s` | `float` | `—` | keyword-only |

Результат: `None`.

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_shared_host_liveness.py:65](../../../../../../services/web-collector/tests/test_shared_host_liveness.py#L65).

```python
yield (
            SharedHosts(a_store, "instance-a", poll_s=POLL, ttl_s=TTL),
            SharedHosts(b_store, "instance-b", poll_s=POLL, ttl_s=TTL),
        )
```

## jane_web_collector.shared_hosts.SharedHosts.state

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/shared_hosts.py:69](../../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L69).

```python
self.state = state
```

## jane_web_collector.shared_hosts.SharedHosts.instance_id

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/shared_hosts.py:70](../../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L70).

```python
self.instance_id = instance_id
```

## jane_web_collector.shared_hosts.SharedHosts.poll_s

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/shared_hosts.py:71](../../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L71).

```python
self.poll_s = poll_s
```

## jane_web_collector.shared_hosts.SharedHosts.ttl_s

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/shared_hosts.py:73](../../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L73).

```python
self.ttl_s = ttl_s
```

## jane_web_collector.shared_hosts.SharedHosts.start

**Метод.** Код: [services/web-collector/src/jane_web_collector/shared_hosts.py:81](../../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L81).

```python
async def start(self, host: str, *, interval: float, parallel: int) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |
| `interval` | `float` | `—` | keyword-only |
| `parallel` | `int` | `—` | keyword-only |

Результат: `str`.

Явні `raise` у тілі: `повторний raise`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
Register this instance's limits on ``host`` (its strictest ``interval`` and smallest ``parallel``), wait
in line until the request may start (a free slot of the platform, the interval since the previous start of
any instance, ``Retry-After``) and take the slot. Returns its token: give it back with :meth:`release`
when the request is over.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_shared_host_liveness.py:49](../../../../../../services/web-collector/tests/test_shared_host_liveness.py#L49).

```python
token = await shared.start(HOST, interval=interval, parallel=1)
```

## jane_web_collector.shared_hosts.SharedHosts.release

**Метод.** Код: [services/web-collector/src/jane_web_collector/shared_hosts.py:106](../../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L106).

```python
def release(self, host: str, token: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |
| `token` | `str` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Give back the slot (or the place in line) of ``token``.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_shared_host_liveness.py:58](../../../../../../services/web-collector/tests/test_shared_host_liveness.py#L58).

```python
shared.release(HOST, token)
```

## jane_web_collector.shared_hosts.SharedHosts.push_back

**Метод.** Код: [services/web-collector/src/jane_web_collector/shared_hosts.py:114](../../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L114).

```python
def push_back(self, host: str, seconds: float) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |
| `seconds` | `float` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
``Retry-After``: no instance starts a request to ``host`` before ``now + seconds``.
```

## jane_web_collector.shared_hosts.SharedHosts.leave

**Метод.** Код: [services/web-collector/src/jane_web_collector/shared_hosts.py:121](../../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L121).

```python
def leave(self, host: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
This instance no longer uses ``host``: its limits stop applying to the other instances.
```

## jane_web_collector.shared_hosts.SharedHosts.renew

**Метод.** Код: [services/web-collector/src/jane_web_collector/shared_hosts.py:142](../../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L142).

```python
def renew(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
One renewal of everything this instance holds (the renewal task calls it every ``ttl / 3``).
```

## jane_web_collector.shared_hosts.SharedHosts.aclose

**Метод.** Код: [services/web-collector/src/jane_web_collector/shared_hosts.py:151](../../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L151).

```python
async def aclose(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Stop renewing (service shutdown). Rows still held expire after ``ttl_s`` like those of a dead instance.
```
