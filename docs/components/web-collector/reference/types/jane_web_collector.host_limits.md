# Модуль `jane_web_collector.host_limits`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/host_limits.py](../../../../../services/web-collector/src/jane_web_collector/host_limits.py). Не редагуйте вручну.

Per-host politeness shared by every collection and one-shot fetch of one service process.

The :class:`~.engine.Engine` owns one :class:`HostLimiter`. Each user of it - a collection run or one ``POST /v1/fetches`` - opens a :class:`HostSession` with its own effective limits. The limiter keeps one schedule per host (``host[:port]`` of the URL), so the source sees one polite client however many collections and fetches use it at the same time:

* request starts to a host are at least ``interval`` apart, ``interval = max(1 / rate.requests_per_second_per_host, rate.min_delay_ms_per_host)`` and robots.txt ``Crawl-delay`` when ``rate.respect_crawl_delay``;
* at most ``concurrency.max_parallel_fetches_per_host`` requests to a host are in flight at once;
* sessions with different values: the strictest value of the sessions active on the host applies to every request to it (the largest interval, the smallest parallelism). A session becomes active on a host with its first request there and stays active until it is closed (the collection finished, failed, was cancelled or handed over; the fetch returned). A Crawl-delay seen by a session keeps counting until it is closed;
* ``Retry-After`` from the source delays every user of the host.

Nothing is reserved ahead of time: requests that hold a slot take their start turn one by one (in arrival order), sleep until the start the strictest interval allows and only then mark it as the host's last start. A request cancelled while it waits (for a slot or for its turn) leaves no trace in the schedule.

The state of a host is dropped once no session uses it, nothing is in flight or waiting and its last interval has passed: when a session closes and every ``collector.host_state_prune_interval_seconds``.

Instances that share the state store (one node, one ``STATE_DIR``) coordinate the same limits through it (:class:`~.shared_hosts.SharedHosts`, R15): a request holding a slot of the process also takes a slot of the platform and reserves its start in the shared schedule, so the host sees one polite client in total.

## Класи

### Клас `HostLimiter`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.host_limits` |
| Код | [host_limits.py:98](../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L98) |

```python
class HostLimiter: ...
```

Per-host limits of one service process (see the module docstring).

#### Конструктор `HostLimiter.__init__`

```python
def __init__(self, limits: ServiceLimits, shared: SharedHosts | None = None) -> None: ...
```

``limits`` are the service's own (platform) limits; only housekeeping is read from them, the per-host limits come with every session. ``shared``: coordination with the other instances that share the state store (``None``: this process only).

Код: [host_limits.py:101](../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L101).

#### Метод `HostLimiter.session`

```python
def session(self, limits: ServiceLimits) -> HostSession: ...
```

A new user of the limiter with its effective limits; close it when the work is done.

Код: [host_limits.py:110](../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L110).

#### Метод `HostLimiter.__len__`

```python
def __len__(self) -> int: ...
```

Number of hosts with state (diagnostics, tests).

Код: [host_limits.py:114](../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L114).

#### Метод `HostLimiter.stats`

```python
def stats(self, host: str) -> dict[str, Any] | None: ...
```

State of one host (diagnostics, tests): sessions active on it, requests in flight and waiting for a slot, the interval and parallelism in force; ``None`` when the host has no state.

Код: [host_limits.py:118](../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L118).

#### Метод `HostLimiter.prune`

```python
def prune(self, now: float | None = None) -> int: ...
```

Drop the state of hosts nobody uses any more; returns how many were dropped.

Код: [host_limits.py:142](../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L142).

#### Метод `HostLimiter.push_back`

```python
def push_back(self, host: str, seconds: float) -> None: ...
```

The source asked to slow down (``Retry-After``): no request to this host from anyone before that.

Код: [host_limits.py:151](../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L151).

### Клас `HostSession`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.host_limits` |
| Код | [host_limits.py:170](../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L170) |

```python
class HostSession: ...
```

One user of the shared :class:`HostLimiter` (a collection run or a one-shot fetch) with its own effective limits.

#### Конструктор `HostSession.__init__`

```python
def __init__(self, limiter: HostLimiter, limits: ServiceLimits) -> None: ...
```

Код: [host_limits.py:174](../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L174).

#### Метод `HostSession.interval`

```python
def interval(self, crawl_delay: float | None = None) -> float: ...
```

Minimum interval between request starts to one host that this session's limits ask for.

Код: [host_limits.py:179](../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L179).

#### Метод `HostSession.slot`

```python
@asynccontextmanager
async def slot(self, host: str, crawl_delay: float | None = None) -> AsyncIterator[None]: ...
```

Wait for a free per-host slot and for the next allowed start; the slot is held while the request is in flight. Cancellation interrupts any wait and frees everything taken.

Код: [host_limits.py:198](../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L198).

#### Метод `HostSession.push_back`

```python
def push_back(self, host: str, seconds: float) -> None: ...
```

Код: [host_limits.py:244](../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L244).

#### Метод `HostSession.close`

```python
def close(self) -> None: ...
```

Stop taking part in the limits of every host this session used (idempotent).

Код: [host_limits.py:247](../../../../../services/web-collector/src/jane_web_collector/host_limits.py#L247).
