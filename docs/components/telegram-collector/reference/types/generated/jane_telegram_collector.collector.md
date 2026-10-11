# jane_telegram_collector.collector

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_telegram_collector.collector.LeaseLost](#jane_telegram_collectorcollectorleaselost)
- [jane_telegram_collector.collector.new_stats](#jane_telegram_collectorcollectornew_stats)
- [jane_telegram_collector.collector.channel_key](#jane_telegram_collectorcollectorchannel_key)
- [jane_telegram_collector.collector.RunDeps](#jane_telegram_collectorcollectorrundeps)
- [jane_telegram_collector.collector.RunDeps.__init__](#jane_telegram_collectorcollectorrundeps__init__)
- [jane_telegram_collector.collector.RunDeps.state](#jane_telegram_collectorcollectorrundepsstate)
- [jane_telegram_collector.collector.RunDeps.factory](#jane_telegram_collectorcollectorrundepsfactory)
- [jane_telegram_collector.collector.RunDeps.resolve](#jane_telegram_collectorcollectorrundepsresolve)
- [jane_telegram_collector.collector.RunDeps.transit](#jane_telegram_collectorcollectorrundepstransit)
- [jane_telegram_collector.collector.RunDeps.instance_id](#jane_telegram_collectorcollectorrundepsinstance_id)
- [jane_telegram_collector.collector.RunDeps.lease_seconds](#jane_telegram_collectorcollectorrundepslease_seconds)
- [jane_telegram_collector.collector.RunDeps.heartbeat_seconds](#jane_telegram_collectorcollectorrundepsheartbeat_seconds)
- [jane_telegram_collector.collector.RunDeps.version](#jane_telegram_collectorcollectorrundepsversion)
- [jane_telegram_collector.collector.RunDeps.ack_events](#jane_telegram_collectorcollectorrundepsack_events)
- [jane_telegram_collector.collector.TelegramRun](#jane_telegram_collectorcollectortelegramrun)
- [jane_telegram_collector.collector.TelegramRun.__init__](#jane_telegram_collectorcollectortelegramrun__init__)
- [jane_telegram_collector.collector.TelegramRun.deps](#jane_telegram_collectorcollectortelegramrundeps)
- [jane_telegram_collector.collector.TelegramRun.state](#jane_telegram_collectorcollectortelegramrunstate)
- [jane_telegram_collector.collector.TelegramRun.account](#jane_telegram_collectorcollectortelegramrunaccount)
- [jane_telegram_collector.collector.TelegramRun.collection_id](#jane_telegram_collectorcollectortelegramruncollection_id)
- [jane_telegram_collector.collector.TelegramRun.state_key](#jane_telegram_collectorcollectortelegramrunstate_key)
- [jane_telegram_collector.collector.TelegramRun.request](#jane_telegram_collectorcollectortelegramrunrequest)
- [jane_telegram_collector.collector.TelegramRun.rules](#jane_telegram_collectorcollectortelegramrunrules)
- [jane_telegram_collector.collector.TelegramRun.rules_ref](#jane_telegram_collectorcollectortelegramrunrules_ref)
- [jane_telegram_collector.collector.TelegramRun.source_id](#jane_telegram_collectorcollectortelegramrunsource_id)
- [jane_telegram_collector.collector.TelegramRun.mode](#jane_telegram_collectorcollectortelegramrunmode)
- [jane_telegram_collector.collector.TelegramRun.stats](#jane_telegram_collectorcollectortelegramrunstats)
- [jane_telegram_collector.collector.TelegramRun.resolved](#jane_telegram_collectorcollectortelegramrunresolved)
- [jane_telegram_collector.collector.TelegramRun.limits](#jane_telegram_collectorcollectortelegramrunlimits)
- [jane_telegram_collector.collector.TelegramRun.delivery](#jane_telegram_collectorcollectortelegramrundelivery)
- [jane_telegram_collector.collector.TelegramRun.new_on](#jane_telegram_collectorcollectortelegramrunnew_on)
- [jane_telegram_collector.collector.TelegramRun.edits_on](#jane_telegram_collectorcollectortelegramrunedits_on)
- [jane_telegram_collector.collector.TelegramRun.media_on](#jane_telegram_collectorcollectortelegramrunmedia_on)
- [jane_telegram_collector.collector.TelegramRun.media_kinds](#jane_telegram_collectorcollectortelegramrunmedia_kinds)
- [jane_telegram_collector.collector.TelegramRun.fence](#jane_telegram_collectorcollectortelegramrunfence)
- [jane_telegram_collector.collector.TelegramRun.cancelled](#jane_telegram_collectorcollectortelegramruncancelled)
- [jane_telegram_collector.collector.TelegramRun.stop_reason](#jane_telegram_collectorcollectortelegramrunstop_reason)
- [jane_telegram_collector.collector.TelegramRun.flood_waits](#jane_telegram_collectorcollectortelegramrunflood_waits)
- [jane_telegram_collector.collector.TelegramRun.channels](#jane_telegram_collectorcollectortelegramrunchannels)
- [jane_telegram_collector.collector.TelegramRun.call](#jane_telegram_collectorcollectortelegramruncall)
- [jane_telegram_collector.collector.TelegramRun.execute](#jane_telegram_collectorcollectortelegramrunexecute)

## jane_telegram_collector.collector.LeaseLost

**Повторний експорт.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:69](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L69).

```python
from jane_telegram_collector.state import LeaseLost as LeaseLost
```

Повторний експорт: [jane_telegram_collector.state.LeaseLost](jane_telegram_collector.state.md#jane_telegram_collectorstateleaselost).

## jane_telegram_collector.collector.new_stats

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:95](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L95).

```python
def new_stats() -> dict[str, Any]:
```

Результат: `dict[str, Any]`.

## jane_telegram_collector.collector.channel_key

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:99](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L99).

```python
def channel_key(spec: Mapping[str, Any]) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `spec` | `Mapping[str, Any]` | `—` | positional-or-keyword |

Результат: `str`.

## jane_telegram_collector.collector.RunDeps

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:125](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L125).

```python
class RunDeps:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [state](jane_telegram_collector.collector.md#jane_telegram_collectorcollectorrundepsstate) | Поле | ні |
| [factory](jane_telegram_collector.collector.md#jane_telegram_collectorcollectorrundepsfactory) | Поле | ні |
| [resolve](jane_telegram_collector.collector.md#jane_telegram_collectorcollectorrundepsresolve) | Поле | ні |
| [transit](jane_telegram_collector.collector.md#jane_telegram_collectorcollectorrundepstransit) | Поле | ні |
| [instance_id](jane_telegram_collector.collector.md#jane_telegram_collectorcollectorrundepsinstance_id) | Поле | ні |
| [lease_seconds](jane_telegram_collector.collector.md#jane_telegram_collectorcollectorrundepslease_seconds) | Поле | ні |
| [heartbeat_seconds](jane_telegram_collector.collector.md#jane_telegram_collectorcollectorrundepsheartbeat_seconds) | Поле | ні |
| [version](jane_telegram_collector.collector.md#jane_telegram_collectorcollectorrundepsversion) | Поле | ні |
| [ack_events](jane_telegram_collector.collector.md#jane_telegram_collectorcollectorrundepsack_events) | Поле | ні |
| [__init__](jane_telegram_collector.collector.md#jane_telegram_collectorcollectorrundeps__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Service-level dependencies shared by all runs.
```

## jane_telegram_collector.collector.RunDeps.__init__

**Конструктор dataclass.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:125](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L125).

```python
def __init__(self, state: StateStore, factory: ClientFactory, resolve: Callable[..., ResolvedLimits[ServiceLimits]], transit: TransitStore | None, instance_id: str, lease_seconds: float, heartbeat_seconds: float, version: str, ack_events: dict[str, asyncio.Event] = <factory dict>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `state` | `StateStore` | `—` | positional-or-keyword |
| `factory` | `ClientFactory` | `—` | positional-or-keyword |
| `resolve` | `Callable[..., ResolvedLimits[ServiceLimits]]` | `—` | positional-or-keyword |
| `transit` | `TransitStore \| None` | `—` | positional-or-keyword |
| `instance_id` | `str` | `—` | positional-or-keyword |
| `lease_seconds` | `float` | `—` | positional-or-keyword |
| `heartbeat_seconds` | `float` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |
| `ack_events` | `dict[str, asyncio.Event]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.collector.RunDeps.state

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:128](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L128).

```python
state: StateStore
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.collector.RunDeps.factory

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:129](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L129).

```python
factory: ClientFactory
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.collector.RunDeps.resolve

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:130](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L130).

```python
resolve: Callable[..., ResolvedLimits[ServiceLimits]]
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.collector.RunDeps.transit

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:131](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L131).

```python
transit: TransitStore | None
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.collector.RunDeps.instance_id

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:132](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L132).

```python
instance_id: str
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.collector.RunDeps.lease_seconds

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:133](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L133).

```python
lease_seconds: float
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.collector.RunDeps.heartbeat_seconds

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:134](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L134).

```python
heartbeat_seconds: float
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.collector.RunDeps.version

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:135](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L135).

```python
version: str
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.collector.RunDeps.ack_events

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:136](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L136).

```python
ack_events: dict[str, asyncio.Event] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_telegram_collector.collector.TelegramRun

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:139](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L139).

```python
class TelegramRun:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrun__init__) | Конструктор | ні |
| [deps](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrundeps) | Поле екземпляра | ні |
| [state](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunstate) | Поле екземпляра | ні |
| [account](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunaccount) | Поле екземпляра | ні |
| [collection_id](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramruncollection_id) | Поле екземпляра | ні |
| [state_key](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunstate_key) | Поле екземпляра | ні |
| [request](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunrequest) | Поле екземпляра | ні |
| [rules](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunrules) | Поле екземпляра | ні |
| [rules_ref](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunrules_ref) | Поле екземпляра | ні |
| [source_id](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunsource_id) | Поле екземпляра | ні |
| [mode](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunmode) | Поле екземпляра | ні |
| [stats](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunstats) | Поле екземпляра | ні |
| [resolved](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunresolved) | Поле екземпляра | ні |
| [limits](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunlimits) | Поле екземпляра | ні |
| [delivery](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrundelivery) | Поле екземпляра | ні |
| [new_on](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunnew_on) | Поле екземпляра | ні |
| [edits_on](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunedits_on) | Поле екземпляра | ні |
| [media_on](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunmedia_on) | Поле екземпляра | ні |
| [media_kinds](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunmedia_kinds) | Поле екземпляра | ні |
| [fence](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunfence) | Поле екземпляра | ні |
| [cancelled](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramruncancelled) | Поле екземпляра | ні |
| [stop_reason](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunstop_reason) | Поле екземпляра | ні |
| [flood_waits](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunflood_waits) | Поле екземпляра | ні |
| [channels](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunchannels) | Поле екземпляра | ні |
| [call](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramruncall) | Метод | ні |
| [execute](jane_telegram_collector.collector.md#jane_telegram_collectorcollectortelegramrunexecute) | Метод | ні |

## jane_telegram_collector.collector.TelegramRun.__init__

**Конструктор.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:140](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L140).

```python
def __init__(self, deps: RunDeps, record: Mapping[str, Any], account: ResolvedAccount) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `deps` | `RunDeps` | `—` | positional-or-keyword |
| `record` | `Mapping[str, Any]` | `—` | positional-or-keyword |
| `account` | `ResolvedAccount` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.collector.TelegramRun.deps

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:141](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L141).

```python
self.deps = deps
```

## jane_telegram_collector.collector.TelegramRun.state

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:142](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L142).

```python
self.state = deps.state
```

## jane_telegram_collector.collector.TelegramRun.account

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:143](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L143).

```python
self.account = account
```

## jane_telegram_collector.collector.TelegramRun.collection_id

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:144](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L144).

```python
self.collection_id: str = record['collection_id']
```

## jane_telegram_collector.collector.TelegramRun.state_key

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:145](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L145).

```python
self.state_key: str = record['state_key']
```

## jane_telegram_collector.collector.TelegramRun.request

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:146](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L146).

```python
self.request: dict[str, Any] = record['request']
```

## jane_telegram_collector.collector.TelegramRun.rules

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:147](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L147).

```python
self.rules: dict[str, Any] = record['rules']
```

## jane_telegram_collector.collector.TelegramRun.rules_ref

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:148](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L148).

```python
self.rules_ref: dict[str, Any] | None = record.get('rules_ref')
```

## jane_telegram_collector.collector.TelegramRun.source_id

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:149](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L149).

```python
self.source_id: str | None = self.request.get('source_id')
```

## jane_telegram_collector.collector.TelegramRun.mode

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:150](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L150).

```python
self.mode: str = self.request.get('mode', 'full')
```

## jane_telegram_collector.collector.TelegramRun.stats

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:151](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L151).

```python
self.stats: dict[str, Any] = {**new_stats(), **(record.get('stats') or {})}
```

## jane_telegram_collector.collector.TelegramRun.resolved

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:152](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L152).

```python
self.resolved = deps.resolve(self.rules.get('limits'), self.request.get('limits'))
```

## jane_telegram_collector.collector.TelegramRun.limits

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:153](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L153).

```python
self.limits: ServiceLimits = self.resolved.limits
```

## jane_telegram_collector.collector.TelegramRun.delivery

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:154](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L154).

```python
self.delivery = Delivery(mode=self.request.get('content_delivery', 'auto'), inline_max_bytes=self.limits.transfer.inline_max_bytes, transit_ttl_seconds=self.limits.transfer.transit_ttl_seconds, store=deps.transit)
```

## jane_telegram_collector.collector.TelegramRun.new_on

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:161](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L161).

```python
self.new_on = bool(updates.get('new_messages', True))
```

## jane_telegram_collector.collector.TelegramRun.edits_on

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:162](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L162).

```python
self.edits_on = bool(updates.get('edits', True))
```

## jane_telegram_collector.collector.TelegramRun.media_on

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:164](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L164).

```python
self.media_on = bool(media.get('download', False))
```

## jane_telegram_collector.collector.TelegramRun.media_kinds

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:165](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L165).

```python
self.media_kinds = set(media.get('kinds') or ())
```

## jane_telegram_collector.collector.TelegramRun.fence

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:166](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L166).

```python
self.fence = (self.collection_id, deps.instance_id)
```

## jane_telegram_collector.collector.TelegramRun.cancelled

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:167](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L167).

```python
self.cancelled = False
```

## jane_telegram_collector.collector.TelegramRun.stop_reason

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:168](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L168).

```python
self.stop_reason: str | None = None
```

## jane_telegram_collector.collector.TelegramRun.flood_waits

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:169](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L169).

```python
self.flood_waits = 0
```

## jane_telegram_collector.collector.TelegramRun.channels

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:170](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L170).

```python
self.channels: dict[str, Any] = {}
```

## jane_telegram_collector.collector.TelegramRun.call

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:192](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L192).

```python
async def call(self, what: str, fn: Callable[[], Awaitable[T]]) -> T:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `what` | `str` | `—` | positional-or-keyword |
| `fn` | `Callable[[], Awaitable[T]]` | `—` | positional-or-keyword |

Результат: `T`.

Явні `raise` у тілі: `RateLimitedStop`, `TransientFailure`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
One Telegram API call: pacing, per-call timeout, retries of transient errors, flood-wait.
```

## jane_telegram_collector.collector.TelegramRun.execute

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/collector.py:308](../../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L308).

```python
async def execute(self, job: JobContext | None=None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `job` | `JobContext \| None` | `None` | positional-or-keyword |

Результат: `dict[str, Any]`.

Явні `raise` у тілі: `RuntimeError`, `self._stop_exc`, `повторний raise`. Винятки викликаних залежностей описуються у ручному довіднику.
