# Модуль `jane_web_collector.shared_hosts`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/shared_hosts.py](../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py). Не редагуйте вручну.

Per-host politeness shared by the instances of the Web Collector that share one state store (R15).

:mod:`.host_limits` keeps the per-host schedule of one process; several instances on one node with one ``STATE_DIR`` (one SQLite file) would still reach a host N times as often. :class:`SharedHosts` extends the schedule of every host into the shared state store, so the host sees one polite client for the whole platform (all collections and one-shot fetches of all those instances):

* **who uses the host** (``host_users``): every instance registers the strictest interval and the smallest parallelism of its own sessions on the host, from its first request there until the host becomes idle in the instance;
* **parallelism** (``host_slots``): at most the smallest registered ``max_parallel_fetches_per_host`` requests of all instances are in flight;
* **fairness** (``host_waiters``): requests that wait queue in arrival order across the instances and start strictly in that order - a waiting request re-checks every ``collector.shared_host_poll_ms`` (the first one sleeps until the schedule allows its start) and takes a slot only when it is first in line, so a busy instance cannot starve another one, not even by arriving exactly when the first waiter's interval ends;
* **request starts** (``host_schedule``): a request takes its slot only when it may start at once - the largest registered interval after the previous start of any instance has passed, and so has ``Retry-After``; the first request in line sleeps until then **without** a slot. A slot is held only while the request is in flight;
* ``Retry-After`` from the source delays every instance (``host_schedule.not_before``).

**Liveness** (review 1 of WP-16): while an instance holds a registration, a slot or a place in line, a renewal task extends them every ``collector.shared_host_ttl_seconds / 3`` - also during a long download, a ``Retry-After`` of up to ``collector.max_retry_after_seconds`` or a ``Crawl-delay`` longer than the TTL. Only an instance that died stops renewing: its rows expire ``collector.shared_host_ttl_seconds`` after its last renewal and stop limiting the others. So the TTL does not have to exceed request durations or waits; it bounds how long a dead instance blocks a host. The start-up rule ``shared_host_ttl_seconds * 2/3 > STATE_BUSY_TIMEOUT_MS`` keeps a renewal that waited a full lock wait in time (:func:`check_ttl`).

Times are wall-clock (``time.time()``) because they are compared across processes. Instances with different state stores do not coordinate (separate collectors, v1 is single node: ADR-0007). A busy store (another process holding the SQLite lock longer than ``STATE_BUSY_TIMEOUT_MS``) never fails a request: the request waits and tries again; the per-process limits keep applying meanwhile.

## Класи

### Клас `SharedHosts`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.shared_hosts` |
| Код | [shared_hosts.py:65](../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L65) |

```python
class SharedHosts: ...
```

Cross-instance part of the per-host limits, kept in the shared :class:`~.state.StateStore`.

#### Конструктор `SharedHosts.__init__`

```python
def __init__(self, state: StateStore, instance_id: str, *, poll_s: float, ttl_s: float) -> None: ...
```

Код: [shared_hosts.py:68](../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L68).

#### Метод `SharedHosts.start`

```python
async def start(self, host: str, *, interval: float, parallel: int) -> str: ...
```

Register this instance's limits on ``host`` (its strictest ``interval`` and smallest ``parallel``), wait in line until the request may start (a free slot of the platform, the interval since the previous start of any instance, ``Retry-After``) and take the slot. Returns its token: give it back with :meth:`release` when the request is over.

Код: [shared_hosts.py:81](../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L81).

#### Метод `SharedHosts.release`

```python
def release(self, host: str, token: str) -> None: ...
```

Give back the slot (or the place in line) of ``token``.

Код: [shared_hosts.py:106](../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L106).

#### Метод `SharedHosts.push_back`

```python
def push_back(self, host: str, seconds: float) -> None: ...
```

``Retry-After``: no instance starts a request to ``host`` before ``now + seconds``.

Код: [shared_hosts.py:114](../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L114).

#### Метод `SharedHosts.leave`

```python
def leave(self, host: str) -> None: ...
```

This instance no longer uses ``host``: its limits stop applying to the other instances.

Код: [shared_hosts.py:121](../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L121).

#### Метод `SharedHosts.renew`

```python
def renew(self) -> None: ...
```

One renewal of everything this instance holds (the renewal task calls it every ``ttl / 3``).

Код: [shared_hosts.py:142](../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L142).

#### Метод `SharedHosts.aclose`

```python
async def aclose(self) -> None: ...
```

Stop renewing (service shutdown). Rows still held expire after ``ttl_s`` like those of a dead instance.

Код: [shared_hosts.py:151](../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L151).

## Функції

### Функція `check_ttl`

```python
def check_ttl(ttl_s: float, busy_timeout_ms: int) -> None: ...
```

Start-up rule: a renewal that waited one full SQLite lock wait must still come before the TTL runs out (``ttl - ttl / 3 > busy timeout``); otherwise a live instance would lose its slot to another instance.

Винятки в коді функції: `ValueError`.

Код: [shared_hosts.py:55](../../../../../services/web-collector/src/jane_web_collector/shared_hosts.py#L55).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `RENEWALS_PER_TTL` | — | `3` | Renewals within one ``shared_host_ttl_seconds``: a live row is renewed every ``ttl / 3``. |
