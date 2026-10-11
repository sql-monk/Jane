# Модуль `jane_telegram_collector.client`

> Згенеровано `scripts/docs_reference.py` з [services/telegram-collector/src/jane_telegram_collector/client.py](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py). Не редагуйте вручну.

Telegram client abstraction: the collector talks to Telegram only through :class:`TelegramClient`.

Implementations: :mod:`.recorded` (JSON recordings: tests, demos, replays), :mod:`.telethon_client` (MTProto via the optional ``telethon`` extra) or any ``<module>:<factory>`` (``JANE_TELEGRAM_COLLECTOR_CLIENT_BACKEND``).

Channel identifiers follow the Bot API convention (``-100<channel id>``), message ids are the channel's monotonic message ids, ``pts`` is the channel's update sequence (``updates.getChannelDifference``).

## Зміст

- [Клас `AccountUnauthorized`](#клас-accountunauthorized)
- [Клас `ChangeBatch`](#клас-changebatch)
- [Клас `ChannelInfo`](#клас-channelinfo)
- [Клас `ChannelUnavailable`](#клас-channelunavailable)
- [Клас `ClientFactory`](#клас-clientfactory)
- [Клас `ClientUnavailable`](#клас-clientunavailable)
- [Клас `FloodWait`](#клас-floodwait)
- [Клас `ResolvedAccount`](#клас-resolvedaccount)
- [Клас `TelegramClient`](#клас-telegramclient)
- [Клас `TelegramError`](#клас-telegramerror)
- [Клас `TgMedia`](#клас-tgmedia)
- [Клас `TgMessage`](#клас-tgmessage)
- [Функція `load_factory`](#функція-load_factory)

## Класи

### Клас `AccountUnauthorized`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_telegram_collector.client` |
| Успадкування | `TelegramError` |
| Код | [client.py:58](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L58) |

```python
class AccountUnauthorized(TelegramError): ...
```

The account session is missing, expired or rejected (the whole collection fails).

### Клас `ChangeBatch`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_telegram_collector.client` |
| Код | [client.py:100](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L100) |

```python
@dataclass(frozen=True)
class ChangeBatch: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `messages` | `Sequence[TgMessage]` | — | читання | New and edited messages after the requested ``pts`` (current state of each message). |
| `pts` | `int` | — | читання | ``pts`` to continue from. |
| `final` | `bool` | — | читання | No more changes after ``pts`` right now. |
| `too_long` | `bool` | `False` | читання | The difference is too long (Telegram ``channelDifferenceTooLong``): edits in the gap are unavailable. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `ChannelInfo`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_telegram_collector.client` |
| Код | [client.py:89](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L89) |

```python
@dataclass(frozen=True)
class ChannelInfo: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `channel_id` | `str` | — | читання |  |
| `username` | `str \| None` | — | читання |  |
| `title` | `str \| None` | — | читання |  |
| `top_message_id` | `int` | — | читання | Id of the newest message (0 for an empty channel). |
| `pts` | `int` | — | читання | Current update sequence of the channel. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `ChannelUnavailable`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_telegram_collector.client` |
| Успадкування | `TelegramError` |
| Код | [client.py:54](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L54) |

```python
class ChannelUnavailable(TelegramError): ...
```

The channel does not exist, is private or the account has no access (per-channel error).

### Клас `ClientFactory`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_telegram_collector.client` |
| Успадкування | `Protocol` |
| Код | [client.py:142](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L142) |

```python
class ClientFactory(Protocol): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `name` | `str` | — | читання й запис |  |

#### Метод `ClientFactory.open`

```python
async def open(self, account: ResolvedAccount, *, connect_timeout_s: float) -> TelegramClient: ...
```

Код: [client.py:145](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L145).

#### Метод `ClientFactory.requires_account`

```python
def requires_account(self) -> bool: ...
```

True if a ``telegram_account`` connection is mandatory for this backend.

Код: [client.py:147](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L147).

### Клас `ClientUnavailable`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_telegram_collector.client` |
| Успадкування | `TelegramError` |
| Код | [client.py:50](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L50) |

```python
class ClientUnavailable(TelegramError): ...
```

Transient failure (network, Telegram internal error): the call may be retried.

### Клас `FloodWait`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_telegram_collector.client` |
| Успадкування | `TelegramError` |
| Код | [client.py:42](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L42) |

```python
class FloodWait(TelegramError): ...
```

Telegram asks to wait ``seconds`` before the next call (FLOOD_WAIT_X).

#### Конструктор `FloodWait.__init__`

```python
def __init__(self, seconds: int) -> None: ...
```

Код: [client.py:45](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L45).

### Клас `ResolvedAccount`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_telegram_collector.client` |
| Код | [client.py:112](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L112) |

```python
@dataclass(frozen=True)
class ResolvedAccount: ...
```

A ``telegram_account`` connection with its secrets resolved in this service's environment.

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `connection_id` | `str \| None` | — | читання |  |
| `params` | `Mapping[str, object]` | — | читання |  |
| `secrets` | `Mapping[str, str]` | `field(repr=False, default_factory=dict)` | читання |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `TelegramClient`

| Властивість | Значення |
|---|---|
| Вид | протокол |
| Модуль | `jane_telegram_collector.client` |
| Успадкування | `Protocol` |
| Код | [client.py:120](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L120) |

```python
class TelegramClient(Protocol): ...
```

#### Метод `TelegramClient.resolve`

```python
async def resolve(
    self,
    *,
    username: str | None = None,
    channel_id: str | None = None,
) -> ChannelInfo: ...
```

Channel by ``username`` or ``channel_id``; :class:`ChannelUnavailable` if not accessible.

Код: [client.py:121](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L121).

#### Метод `TelegramClient.history`

```python
async def history(
    self,
    channel: ChannelInfo,
    *,
    after_id: int,
    limit: int,
    since: datetime | None = None,
) -> list[TgMessage]: ...
```

Up to ``limit`` messages with ``message_id > after_id`` (and ``date >= since``), oldest first.

Код: [client.py:125](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L125).

#### Метод `TelegramClient.get_message`

```python
async def get_message(self, channel: ChannelInfo, message_id: int) -> TgMessage | None: ...
```

Код: [client.py:131](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L131).

#### Метод `TelegramClient.changes`

```python
async def changes(self, channel: ChannelInfo, *, pts: int, limit: int) -> ChangeBatch: ...
```

Код: [client.py:133](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L133).

#### Метод `TelegramClient.download_media`

```python
async def download_media(
    self,
    channel: ChannelInfo,
    media: TgMedia,
    *,
    max_bytes: int,
) -> bytes: ...
```

Media bytes; more than ``max_bytes`` raises :class:`ValueError`.

Код: [client.py:135](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L135).

#### Метод `TelegramClient.close`

```python
async def close(self) -> None: ...
```

Код: [client.py:139](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L139).

### Клас `TelegramError`

| Властивість | Значення |
|---|---|
| Вид | виняток |
| Модуль | `jane_telegram_collector.client` |
| Успадкування | `Exception` |
| Код | [client.py:38](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L38) |

```python
class TelegramError(Exception): ...
```

Base class of client errors.

### Клас `TgMedia`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_telegram_collector.client` |
| Код | [client.py:63](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L63) |

```python
@dataclass(frozen=True)
class TgMedia: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `kind` | `str` | — | читання |  |
| `name` | `str` | — | читання |  |
| `media_type` | `str` | — | читання |  |
| `size_bytes` | `int \| None` | `None` | читання |  |
| `ref` | `str` | `''` | читання | Opaque reference for :meth:`TelegramClient.download_media`. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `TgMessage`

| Властивість | Значення |
|---|---|
| Вид | dataclass (незмінний) |
| Модуль | `jane_telegram_collector.client` |
| Код | [client.py:73](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L73) |

```python
@dataclass(frozen=True)
class TgMessage: ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `channel_id` | `str` | — | читання |  |
| `message_id` | `int` | — | читання |  |
| `date` | `datetime` | — | читання |  |
| `text` | `str` | `''` | читання |  |
| `edit_date` | `datetime \| None` | `None` | читання |  |
| `grouped_id` | `str \| None` | `None` | читання |  |
| `views` | `int \| None` | `None` | читання |  |
| `author` | `str \| None` | `None` | читання |  |
| `media` | `Sequence[TgMedia]` | `field(default_factory=tuple)` | читання |  |
| `service_action` | `str \| None` | `None` | читання | A service message of the channel (``MessageService``: channel created, message pinned, title or photo changed...): the action in snake case (``channel_create``, ``pin_message``); ``None`` for a post. |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

## Функції

### Функція `load_factory`

```python
def load_factory(settings: Settings) -> ClientFactory: ...
```

Винятки в коді функції: `ValueError`.

Код: [client.py:152](../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L152).
