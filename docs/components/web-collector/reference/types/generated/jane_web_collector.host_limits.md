# jane_web_collector.host_limits

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.host_limits.HostLimiter](#jane_web_collectorhost_limitshostlimiter)
- [jane_web_collector.host_limits.HostLimiter.__init__](#jane_web_collectorhost_limitshostlimiter__init__)
- [jane_web_collector.host_limits.HostLimiter.prune_interval](#jane_web_collectorhost_limitshostlimiterprune_interval)
- [jane_web_collector.host_limits.HostLimiter.shared](#jane_web_collectorhost_limitshostlimitershared)
- [jane_web_collector.host_limits.HostLimiter.session](#jane_web_collectorhost_limitshostlimitersession)
- [jane_web_collector.host_limits.HostLimiter.__len__](#jane_web_collectorhost_limitshostlimiter__len__)
- [jane_web_collector.host_limits.HostLimiter.stats](#jane_web_collectorhost_limitshostlimiterstats)
- [jane_web_collector.host_limits.HostLimiter.prune](#jane_web_collectorhost_limitshostlimiterprune)
- [jane_web_collector.host_limits.HostLimiter.push_back](#jane_web_collectorhost_limitshostlimiterpush_back)
- [jane_web_collector.host_limits.HostSession](#jane_web_collectorhost_limitshostsession)
- [jane_web_collector.host_limits.HostSession.__init__](#jane_web_collectorhost_limitshostsession__init__)
- [jane_web_collector.host_limits.HostSession.limiter](#jane_web_collectorhost_limitshostsessionlimiter)
- [jane_web_collector.host_limits.HostSession.limits](#jane_web_collectorhost_limitshostsessionlimits)
- [jane_web_collector.host_limits.HostSession.interval](#jane_web_collectorhost_limitshostsessioninterval)
- [jane_web_collector.host_limits.HostSession.slot](#jane_web_collectorhost_limitshostsessionslot)
- [jane_web_collector.host_limits.HostSession.push_back](#jane_web_collectorhost_limitshostsessionpush_back)
- [jane_web_collector.host_limits.HostSession.close](#jane_web_collectorhost_limitshostsessionclose)

## jane_web_collector.host_limits.HostLimiter

**Клас.** Код: [services/web-collector/src/jane_web_collector/host_limits.py:98](../../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L98).

```python
class HostLimiter:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.host_limits.md#jane_web_collectorhost_limitshostlimiter__init__) | Конструктор | ні |
| [prune_interval](jane_web_collector.host_limits.md#jane_web_collectorhost_limitshostlimiterprune_interval) | Поле екземпляра | ні |
| [shared](jane_web_collector.host_limits.md#jane_web_collectorhost_limitshostlimitershared) | Поле екземпляра | ні |
| [session](jane_web_collector.host_limits.md#jane_web_collectorhost_limitshostlimitersession) | Метод | ні |
| [__len__](jane_web_collector.host_limits.md#jane_web_collectorhost_limitshostlimiter__len__) | Метод | ні |
| [stats](jane_web_collector.host_limits.md#jane_web_collectorhost_limitshostlimiterstats) | Метод | ні |
| [prune](jane_web_collector.host_limits.md#jane_web_collectorhost_limitshostlimiterprune) | Метод | ні |
| [push_back](jane_web_collector.host_limits.md#jane_web_collectorhost_limitshostlimiterpush_back) | Метод | ні |

### Опис із вихідного коду

```text
Per-host limits of one service process (see the module docstring).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:118](../../../../../../services/web-collector/tests/test_connection_policy.py#L118).

```python
fetcher = Fetcher(
            client,
            limits,
            HostLimiter(limits).session(limits),
            user_agent="JaneBot",
            auth_headers={"Authorization": "Bearer safe-token"},
            connection_policy=policy,
        )
```

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:191](../../../../../../services/web-collector/tests/test_connection_policy.py#L191).

```python
fetcher = Fetcher(
            http_client,
            limits,
            HostLimiter(limits).session(limits),
            user_agent="JaneBot",
            auth_headers={"Authorization": "Bearer safe-token"},
            connection_policy=policy,
        )
```

## jane_web_collector.host_limits.HostLimiter.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/host_limits.py:101](../../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L101).

```python
def __init__(self, limits: ServiceLimits, shared: SharedHosts | None=None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |
| `shared` | `SharedHosts \| None` | `None` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
``limits`` are the service's own (platform) limits; only housekeeping is read from them, the
per-host limits come with every session. ``shared``: coordination with the other instances that share
the state store (``None``: this process only).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:118](../../../../../../services/web-collector/tests/test_connection_policy.py#L118).

```python
fetcher = Fetcher(
            client,
            limits,
            HostLimiter(limits).session(limits),
            user_agent="JaneBot",
            auth_headers={"Authorization": "Bearer safe-token"},
            connection_policy=policy,
        )
```

Контекст і передумови: [services/web-collector/tests/test_connection_policy.py:191](../../../../../../services/web-collector/tests/test_connection_policy.py#L191).

```python
fetcher = Fetcher(
            http_client,
            limits,
            HostLimiter(limits).session(limits),
            user_agent="JaneBot",
            auth_headers={"Authorization": "Bearer safe-token"},
            connection_policy=policy,
        )
```

## jane_web_collector.host_limits.HostLimiter.prune_interval

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/host_limits.py:105](../../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L105).

```python
self.prune_interval = float(limits.collector.host_state_prune_interval_seconds)
```

## jane_web_collector.host_limits.HostLimiter.shared

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/host_limits.py:106](../../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L106).

```python
self.shared = shared
```

## jane_web_collector.host_limits.HostLimiter.session

**Метод.** Код: [services/web-collector/src/jane_web_collector/host_limits.py:110](../../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L110).

```python
def session(self, limits: ServiceLimits) -> HostSession:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |

Результат: `HostSession`.

### Опис із вихідного коду

```text
A new user of the limiter with its effective limits; close it when the work is done.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_host_limiter.py:108](../../../../../../services/web-collector/tests/test_host_limiter.py#L108).

```python
slow = limiter.session(_limits(1.0, parallel=2))
```

Контекст і передумови: [services/web-collector/tests/test_host_limiter.py:130](../../../../../../services/web-collector/tests/test_host_limiter.py#L130).

```python
single = limiter.session(_limits(1000, parallel=1))
```

## jane_web_collector.host_limits.HostLimiter.__len__

**Метод.** Код: [services/web-collector/src/jane_web_collector/host_limits.py:114](../../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L114).

```python
def __len__(self) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Number of hosts with state (diagnostics, tests).
```

## jane_web_collector.host_limits.HostLimiter.stats

**Метод.** Код: [services/web-collector/src/jane_web_collector/host_limits.py:118](../../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L118).

```python
def stats(self, host: str) -> dict[str, Any] | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |

Результат: `dict[str, Any] | None`.

### Опис із вихідного коду

```text
State of one host (diagnostics, tests): sessions active on it, requests in flight and waiting for
a slot, the interval and parallelism in force; ``None`` when the host has no state.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_host_limiter.py:111](../../../../../../services/web-collector/tests/test_host_limiter.py#L111).

```python
stats = limiter.stats("c.test")
```

Контекст і передумови: [services/web-collector/tests/test_host_limiter.py:68](../../../../../../services/web-collector/tests/test_host_limiter.py#L68).

```python
assert limiter.stats("h.test") == {
        "sessions": 2,
        "in_flight": 0,
        "waiting": 0,
        "interval_s": pytest.approx(0.3),
        "parallel": 2,
        "last_start": pytest.approx(max(starts)),
    }
```

## jane_web_collector.host_limits.HostLimiter.prune

**Метод.** Код: [services/web-collector/src/jane_web_collector/host_limits.py:142](../../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L142).

```python
def prune(self, now: float | None=None) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `now` | `float \| None` | `None` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
Drop the state of hosts nobody uses any more; returns how many were dropped.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_host_limiter.py:192](../../../../../../services/web-collector/tests/test_host_limiter.py#L192).

```python
limiter.prune(time.monotonic() + 60)
```

Контекст і передумови: [services/web-collector/tests/test_host_limiter.py:189](../../../../../../services/web-collector/tests/test_host_limiter.py#L189).

```python
assert limiter.prune(time.monotonic() + 60) == 0
```

## jane_web_collector.host_limits.HostLimiter.push_back

**Метод.** Код: [services/web-collector/src/jane_web_collector/host_limits.py:151](../../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L151).

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
The source asked to slow down (``Retry-After``): no request to this host from anyone before that.
```

## jane_web_collector.host_limits.HostSession

**Клас.** Код: [services/web-collector/src/jane_web_collector/host_limits.py:170](../../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L170).

```python
class HostSession:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.host_limits.md#jane_web_collectorhost_limitshostsession__init__) | Конструктор | ні |
| [limiter](jane_web_collector.host_limits.md#jane_web_collectorhost_limitshostsessionlimiter) | Поле екземпляра | ні |
| [limits](jane_web_collector.host_limits.md#jane_web_collectorhost_limitshostsessionlimits) | Поле екземпляра | ні |
| [interval](jane_web_collector.host_limits.md#jane_web_collectorhost_limitshostsessioninterval) | Метод | ні |
| [slot](jane_web_collector.host_limits.md#jane_web_collectorhost_limitshostsessionslot) | Метод | ні |
| [push_back](jane_web_collector.host_limits.md#jane_web_collectorhost_limitshostsessionpush_back) | Метод | ні |
| [close](jane_web_collector.host_limits.md#jane_web_collectorhost_limitshostsessionclose) | Метод | ні |

### Опис із вихідного коду

```text
One user of the shared :class:`HostLimiter` (a collection run or a one-shot fetch) with its own
effective limits.
```

## jane_web_collector.host_limits.HostSession.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/host_limits.py:174](../../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L174).

```python
def __init__(self, limiter: HostLimiter, limits: ServiceLimits) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `limiter` | `HostLimiter` | `—` | positional-or-keyword |
| `limits` | `ServiceLimits` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.host_limits.HostSession.limiter

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/host_limits.py:175](../../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L175).

```python
self.limiter = limiter
```

## jane_web_collector.host_limits.HostSession.limits

**Поле екземпляра.** Код: [services/web-collector/src/jane_web_collector/host_limits.py:176](../../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L176).

```python
self.limits = limits
```

## jane_web_collector.host_limits.HostSession.interval

**Метод.** Код: [services/web-collector/src/jane_web_collector/host_limits.py:179](../../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L179).

```python
def interval(self, crawl_delay: float | None=None) -> float:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `crawl_delay` | `float \| None` | `None` | positional-or-keyword |

Результат: `float`.

### Опис із вихідного коду

```text
Minimum interval between request starts to one host that this session's limits ask for.
```

## jane_web_collector.host_limits.HostSession.slot

**Метод.** Код: [services/web-collector/src/jane_web_collector/host_limits.py:198](../../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L198).

```python
async def slot(self, host: str, crawl_delay: float | None=None) -> AsyncIterator[None]:
```

Декоратори: `asynccontextmanager`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `host` | `str` | `—` | positional-or-keyword |
| `crawl_delay` | `float \| None` | `None` | positional-or-keyword |

Результат: `AsyncIterator[None]`.

### Опис із вихідного коду

```text
Wait for a free per-host slot and for the next allowed start; the slot is held while the request
is in flight. Cancellation interrupts any wait and frees everything taken.
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_host_limiter.py:154](../../../../../../services/web-collector/tests/test_host_limiter.py#L154).

```python
session.slot(host)
```

Контекст і передумови: [services/web-collector/tests/test_host_limiter.py:34](../../../../../../services/web-collector/tests/test_host_limiter.py#L34).

```python
session.slot(host)
```

## jane_web_collector.host_limits.HostSession.push_back

**Метод.** Код: [services/web-collector/src/jane_web_collector/host_limits.py:244](../../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L244).

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

## jane_web_collector.host_limits.HostSession.close

**Метод.** Код: [services/web-collector/src/jane_web_collector/host_limits.py:247](../../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L247).

```python
def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Stop taking part in the limits of every host this session used (idempotent).
```

### Приклади з тестів

Контекст і передумови: [services/web-collector/tests/test_host_limiter.py:190](../../../../../../services/web-collector/tests/test_host_limiter.py#L190).

```python
session.close()
```

Контекст і передумови: [services/web-collector/tests/test_host_limiter.py:191](../../../../../../services/web-collector/tests/test_host_limiter.py#L191).

```python
session.close()
```
