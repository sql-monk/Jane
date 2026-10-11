# Модуль `jane_telegram_collector.collector`

> Згенеровано `scripts/docs_reference.py` з [services/telegram-collector/src/jane_telegram_collector/collector.py](../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py). Не редагуйте вручну.

Collection run: one :class:`TelegramRun` per collection (history, new messages, edits, cursors).

Per channel the run keeps a *progress* record (``channel_progress``, per collection) and the persistent *cursor* (``tg_cursors``, per ``state_key``):

* ``mode=full`` (or no cursor yet): read the history (``history.since`` / ``from_message_id``) oldest first; every message is a new observation. The channel ``pts`` at the start is remembered, so the next incremental run also sees the edits made while the history was read.
* ``mode=incremental`` with a cursor: ``getChannelDifference`` from the cursor's ``pts`` gives new and edited messages. If Telegram answers "difference too long", new messages are read from the history after ``last_message_id`` and an error entry says that edits in the gap are unavailable.

An edit is emitted as a new observation of the same ``material_id`` with a strictly larger ``revision.sequence`` (``edit_date`` x 1000 + the revision number within that second, also for several edits in one second) and ``is_edit: true``. A repeated delivery of a revision already emitted for the ``state_key`` (same ``edit_date`` and text; e.g. an update replayed after a restart) is not emitted again (``stats.duplicates``).

``stats.by_strategy`` / ``discovery.strategy``: ``telegram_history`` for messages read from the channel history (full mode, the first incremental run without a cursor, and an incremental run that finishes a history read a previous collection stopped, e.g. at ``telegram.max_messages_per_run``, before the cursor got a ``pts``); ``telegram_updates`` for new and edited messages from ``getChannelDifference`` and for new messages read after "difference too long" in place of the lost updates.

Every emitted message is committed in one lease-fenced transaction with the run progress, the cursor, the seen revision and the stats, so a killed instance's successor continues exactly after the last emitted message. Flood-waits up to ``telegram.max_flood_wait_seconds`` are waited out; longer ones stop the run with ``rate_limited`` (progress kept, the next collection continues from the cursor).

## Зміст

- [Клас `RunDeps`](#клас-rundeps)
- [Клас `TelegramRun`](#клас-telegramrun)
- [Функція `channel_key`](#функція-channel_key)
- [Функція `new_stats`](#функція-new_stats)

## Класи

### Клас `RunDeps`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_telegram_collector.collector` |
| Код | [collector.py:125](../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L125) |

```python
@dataclass
class RunDeps: ...
```

Service-level dependencies shared by all runs.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `state` | `StateStore` | — | читання й запис |  |
| `factory` | `ClientFactory` | — | читання й запис |  |
| `resolve` | `Callable[..., ResolvedLimits[ServiceLimits]]` | — | читання й запис |  |
| `transit` | `TransitStore \| None` | — | читання й запис |  |
| `instance_id` | `str` | — | читання й запис |  |
| `lease_seconds` | `float` | — | читання й запис |  |
| `heartbeat_seconds` | `float` | — | читання й запис |  |
| `version` | `str` | — | читання й запис |  |
| `ack_events` | `dict[str, asyncio.Event]` | `field(default_factory=dict)` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `TelegramRun`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.collector` |
| Код | [collector.py:139](../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L139) |

```python
class TelegramRun: ...
```

#### Конструктор `TelegramRun.__init__`

```python
def __init__(self, deps: RunDeps, record: Mapping[str, Any], account: ResolvedAccount) -> None: ...
```

Код: [collector.py:140](../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L140).

#### Метод `TelegramRun.call`

```python
async def call(self, what: str, fn: Callable[[], Awaitable[T]]) -> T: ...
```

One Telegram API call: pacing, per-call timeout, retries of transient errors, flood-wait.

Винятки в коді методу: `RateLimitedStop`, `TransientFailure`.

Код: [collector.py:192](../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L192).

#### Метод `TelegramRun.execute`

```python
async def execute(self, job: JobContext | None = None) -> dict[str, Any]: ...
```

Винятки в коді методу: `RuntimeError`.

Код: [collector.py:308](../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L308).

## Функції

### Функція `channel_key`

```python
def channel_key(spec: Mapping[str, Any]) -> str: ...
```

Код: [collector.py:99](../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L99).

### Функція `new_stats`

```python
def new_stats() -> dict[str, Any]: ...
```

Код: [collector.py:95](../../../../../services/telegram-collector/src/jane_telegram_collector/collector.py#L95).

## Реекспорт

| Назва | Визначено в |
|---|---|
| `LeaseLost` | [`jane_telegram_collector.state`](jane_telegram_collector.state.md) |
