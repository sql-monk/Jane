# jane_telegram_collector.client

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_telegram_collector.client.TelegramError](#jane_telegram_collectorclienttelegramerror)
- [jane_telegram_collector.client.FloodWait](#jane_telegram_collectorclientfloodwait)
- [jane_telegram_collector.client.FloodWait.__init__](#jane_telegram_collectorclientfloodwait__init__)
- [jane_telegram_collector.client.FloodWait.seconds](#jane_telegram_collectorclientfloodwaitseconds)
- [jane_telegram_collector.client.ClientUnavailable](#jane_telegram_collectorclientclientunavailable)
- [jane_telegram_collector.client.ChannelUnavailable](#jane_telegram_collectorclientchannelunavailable)
- [jane_telegram_collector.client.AccountUnauthorized](#jane_telegram_collectorclientaccountunauthorized)
- [jane_telegram_collector.client.TgMedia](#jane_telegram_collectorclienttgmedia)
- [jane_telegram_collector.client.TgMedia.__init__](#jane_telegram_collectorclienttgmedia__init__)
- [jane_telegram_collector.client.TgMedia.kind](#jane_telegram_collectorclienttgmediakind)
- [jane_telegram_collector.client.TgMedia.name](#jane_telegram_collectorclienttgmedianame)
- [jane_telegram_collector.client.TgMedia.media_type](#jane_telegram_collectorclienttgmediamedia_type)
- [jane_telegram_collector.client.TgMedia.size_bytes](#jane_telegram_collectorclienttgmediasize_bytes)
- [jane_telegram_collector.client.TgMedia.ref](#jane_telegram_collectorclienttgmediaref)
- [jane_telegram_collector.client.TgMessage](#jane_telegram_collectorclienttgmessage)
- [jane_telegram_collector.client.TgMessage.__init__](#jane_telegram_collectorclienttgmessage__init__)
- [jane_telegram_collector.client.TgMessage.channel_id](#jane_telegram_collectorclienttgmessagechannel_id)
- [jane_telegram_collector.client.TgMessage.message_id](#jane_telegram_collectorclienttgmessagemessage_id)
- [jane_telegram_collector.client.TgMessage.date](#jane_telegram_collectorclienttgmessagedate)
- [jane_telegram_collector.client.TgMessage.text](#jane_telegram_collectorclienttgmessagetext)
- [jane_telegram_collector.client.TgMessage.edit_date](#jane_telegram_collectorclienttgmessageedit_date)
- [jane_telegram_collector.client.TgMessage.grouped_id](#jane_telegram_collectorclienttgmessagegrouped_id)
- [jane_telegram_collector.client.TgMessage.views](#jane_telegram_collectorclienttgmessageviews)
- [jane_telegram_collector.client.TgMessage.author](#jane_telegram_collectorclienttgmessageauthor)
- [jane_telegram_collector.client.TgMessage.media](#jane_telegram_collectorclienttgmessagemedia)
- [jane_telegram_collector.client.TgMessage.service_action](#jane_telegram_collectorclienttgmessageservice_action)
- [jane_telegram_collector.client.ChannelInfo](#jane_telegram_collectorclientchannelinfo)
- [jane_telegram_collector.client.ChannelInfo.__init__](#jane_telegram_collectorclientchannelinfo__init__)
- [jane_telegram_collector.client.ChannelInfo.channel_id](#jane_telegram_collectorclientchannelinfochannel_id)
- [jane_telegram_collector.client.ChannelInfo.username](#jane_telegram_collectorclientchannelinfousername)
- [jane_telegram_collector.client.ChannelInfo.title](#jane_telegram_collectorclientchannelinfotitle)
- [jane_telegram_collector.client.ChannelInfo.top_message_id](#jane_telegram_collectorclientchannelinfotop_message_id)
- [jane_telegram_collector.client.ChannelInfo.pts](#jane_telegram_collectorclientchannelinfopts)
- [jane_telegram_collector.client.ChangeBatch](#jane_telegram_collectorclientchangebatch)
- [jane_telegram_collector.client.ChangeBatch.__init__](#jane_telegram_collectorclientchangebatch__init__)
- [jane_telegram_collector.client.ChangeBatch.messages](#jane_telegram_collectorclientchangebatchmessages)
- [jane_telegram_collector.client.ChangeBatch.pts](#jane_telegram_collectorclientchangebatchpts)
- [jane_telegram_collector.client.ChangeBatch.final](#jane_telegram_collectorclientchangebatchfinal)
- [jane_telegram_collector.client.ChangeBatch.too_long](#jane_telegram_collectorclientchangebatchtoo_long)
- [jane_telegram_collector.client.ResolvedAccount](#jane_telegram_collectorclientresolvedaccount)
- [jane_telegram_collector.client.ResolvedAccount.__init__](#jane_telegram_collectorclientresolvedaccount__init__)
- [jane_telegram_collector.client.ResolvedAccount.connection_id](#jane_telegram_collectorclientresolvedaccountconnection_id)
- [jane_telegram_collector.client.ResolvedAccount.params](#jane_telegram_collectorclientresolvedaccountparams)
- [jane_telegram_collector.client.ResolvedAccount.secrets](#jane_telegram_collectorclientresolvedaccountsecrets)
- [jane_telegram_collector.client.TelegramClient](#jane_telegram_collectorclienttelegramclient)
- [jane_telegram_collector.client.TelegramClient.resolve](#jane_telegram_collectorclienttelegramclientresolve)
- [jane_telegram_collector.client.TelegramClient.history](#jane_telegram_collectorclienttelegramclienthistory)
- [jane_telegram_collector.client.TelegramClient.get_message](#jane_telegram_collectorclienttelegramclientget_message)
- [jane_telegram_collector.client.TelegramClient.changes](#jane_telegram_collectorclienttelegramclientchanges)
- [jane_telegram_collector.client.TelegramClient.download_media](#jane_telegram_collectorclienttelegramclientdownload_media)
- [jane_telegram_collector.client.TelegramClient.close](#jane_telegram_collectorclienttelegramclientclose)
- [jane_telegram_collector.client.ClientFactory](#jane_telegram_collectorclientclientfactory)
- [jane_telegram_collector.client.ClientFactory.name](#jane_telegram_collectorclientclientfactoryname)
- [jane_telegram_collector.client.ClientFactory.open](#jane_telegram_collectorclientclientfactoryopen)
- [jane_telegram_collector.client.ClientFactory.requires_account](#jane_telegram_collectorclientclientfactoryrequires_account)
- [jane_telegram_collector.client.load_factory](#jane_telegram_collectorclientload_factory)

## jane_telegram_collector.client.TelegramError

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:38](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L38).

```python
class TelegramError(Exception):
```

Базові типи / інтерфейси: `Exception`.

### Опис із вихідного коду

```text
Base class of client errors.
```

## jane_telegram_collector.client.FloodWait

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:42](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L42).

```python
class FloodWait(TelegramError):
```

Базові типи / інтерфейси: `TelegramError`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_telegram_collector.client.md#jane_telegram_collectorclientfloodwait__init__) | Конструктор | ні |
| [seconds](jane_telegram_collector.client.md#jane_telegram_collectorclientfloodwaitseconds) | Поле екземпляра | ні |

### Опис із вихідного коду

```text
Telegram asks to wait ``seconds`` before the next call (FLOOD_WAIT_X).
```

## jane_telegram_collector.client.FloodWait.__init__

**Конструктор.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:45](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L45).

```python
def __init__(self, seconds: int) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `seconds` | `int` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.client.FloodWait.seconds

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:47](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L47).

```python
self.seconds = seconds
```

## jane_telegram_collector.client.ClientUnavailable

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:50](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L50).

```python
class ClientUnavailable(TelegramError):
```

Базові типи / інтерфейси: `TelegramError`.

### Опис із вихідного коду

```text
Transient failure (network, Telegram internal error): the call may be retried.
```

## jane_telegram_collector.client.ChannelUnavailable

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:54](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L54).

```python
class ChannelUnavailable(TelegramError):
```

Базові типи / інтерфейси: `TelegramError`.

### Опис із вихідного коду

```text
The channel does not exist, is private or the account has no access (per-channel error).
```

## jane_telegram_collector.client.AccountUnauthorized

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:58](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L58).

```python
class AccountUnauthorized(TelegramError):
```

Базові типи / інтерфейси: `TelegramError`.

### Опис із вихідного коду

```text
The account session is missing, expired or rejected (the whole collection fails).
```

## jane_telegram_collector.client.TgMedia

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:63](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L63).

```python
class TgMedia:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [kind](jane_telegram_collector.client.md#jane_telegram_collectorclienttgmediakind) | Поле | ні |
| [name](jane_telegram_collector.client.md#jane_telegram_collectorclienttgmedianame) | Поле | ні |
| [media_type](jane_telegram_collector.client.md#jane_telegram_collectorclienttgmediamedia_type) | Поле | ні |
| [size_bytes](jane_telegram_collector.client.md#jane_telegram_collectorclienttgmediasize_bytes) | Поле | ні |
| [ref](jane_telegram_collector.client.md#jane_telegram_collectorclienttgmediaref) | Поле | ні |
| [__init__](jane_telegram_collector.client.md#jane_telegram_collectorclienttgmedia__init__) | Конструктор dataclass | ні |

## jane_telegram_collector.client.TgMedia.__init__

**Конструктор dataclass.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:63](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L63).

```python
def __init__(self, kind: str, name: str, media_type: str, size_bytes: int | None = None, ref: str = '') -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `kind` | `str` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |
| `media_type` | `str` | `—` | positional-or-keyword |
| `size_bytes` | `int \| None` | `None` | positional-or-keyword |
| `ref` | `str` | `''` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.client.TgMedia.kind

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:64](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L64).

```python
kind: str
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.client.TgMedia.name

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:65](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L65).

```python
name: str
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.client.TgMedia.media_type

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:66](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L66).

```python
media_type: str
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.client.TgMedia.size_bytes

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:67](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L67).

```python
size_bytes: int | None = None
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.client.TgMedia.ref

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:68](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L68).

```python
ref: str = ''
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
Opaque reference for :meth:`TelegramClient.download_media`.
```

## jane_telegram_collector.client.TgMessage

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:73](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L73).

```python
class TgMessage:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [channel_id](jane_telegram_collector.client.md#jane_telegram_collectorclienttgmessagechannel_id) | Поле | ні |
| [message_id](jane_telegram_collector.client.md#jane_telegram_collectorclienttgmessagemessage_id) | Поле | ні |
| [date](jane_telegram_collector.client.md#jane_telegram_collectorclienttgmessagedate) | Поле | ні |
| [text](jane_telegram_collector.client.md#jane_telegram_collectorclienttgmessagetext) | Поле | ні |
| [edit_date](jane_telegram_collector.client.md#jane_telegram_collectorclienttgmessageedit_date) | Поле | ні |
| [grouped_id](jane_telegram_collector.client.md#jane_telegram_collectorclienttgmessagegrouped_id) | Поле | ні |
| [views](jane_telegram_collector.client.md#jane_telegram_collectorclienttgmessageviews) | Поле | ні |
| [author](jane_telegram_collector.client.md#jane_telegram_collectorclienttgmessageauthor) | Поле | ні |
| [media](jane_telegram_collector.client.md#jane_telegram_collectorclienttgmessagemedia) | Поле | ні |
| [service_action](jane_telegram_collector.client.md#jane_telegram_collectorclienttgmessageservice_action) | Поле | ні |
| [__init__](jane_telegram_collector.client.md#jane_telegram_collectorclienttgmessage__init__) | Конструктор dataclass | ні |

## jane_telegram_collector.client.TgMessage.__init__

**Конструктор dataclass.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:73](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L73).

```python
def __init__(self, channel_id: str, message_id: int, date: datetime, text: str = '', edit_date: datetime | None = None, grouped_id: str | None = None, views: int | None = None, author: str | None = None, media: Sequence[TgMedia] = <factory tuple>, service_action: str | None = None) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `channel_id` | `str` | `—` | positional-or-keyword |
| `message_id` | `int` | `—` | positional-or-keyword |
| `date` | `datetime` | `—` | positional-or-keyword |
| `text` | `str` | `''` | positional-or-keyword |
| `edit_date` | `datetime \| None` | `None` | positional-or-keyword |
| `grouped_id` | `str \| None` | `None` | positional-or-keyword |
| `views` | `int \| None` | `None` | positional-or-keyword |
| `author` | `str \| None` | `None` | positional-or-keyword |
| `media` | `Sequence[TgMedia]` | `factory: tuple` | positional-or-keyword |
| `service_action` | `str \| None` | `None` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.client.TgMessage.channel_id

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:74](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L74).

```python
channel_id: str
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.client.TgMessage.message_id

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:75](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L75).

```python
message_id: int
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.client.TgMessage.date

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:76](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L76).

```python
date: datetime
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.client.TgMessage.text

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:77](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L77).

```python
text: str = ''
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.client.TgMessage.edit_date

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:78](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L78).

```python
edit_date: datetime | None = None
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.client.TgMessage.grouped_id

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:79](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L79).

```python
grouped_id: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.client.TgMessage.views

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:80](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L80).

```python
views: int | None = None
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.client.TgMessage.author

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:81](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L81).

```python
author: str | None = None
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.client.TgMessage.media

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:82](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L82).

```python
media: Sequence[TgMedia] = field(default_factory=tuple)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "default_factory": "tuple"
}
```

## jane_telegram_collector.client.TgMessage.service_action

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:83](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L83).

```python
service_action: str | None = None
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
A service message of the channel (``MessageService``: channel created, message pinned, title or photo
    changed...): the action in snake case (``channel_create``, ``pin_message``); ``None`` for a post.
```

## jane_telegram_collector.client.ChannelInfo

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:89](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L89).

```python
class ChannelInfo:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [channel_id](jane_telegram_collector.client.md#jane_telegram_collectorclientchannelinfochannel_id) | Поле | ні |
| [username](jane_telegram_collector.client.md#jane_telegram_collectorclientchannelinfousername) | Поле | ні |
| [title](jane_telegram_collector.client.md#jane_telegram_collectorclientchannelinfotitle) | Поле | ні |
| [top_message_id](jane_telegram_collector.client.md#jane_telegram_collectorclientchannelinfotop_message_id) | Поле | ні |
| [pts](jane_telegram_collector.client.md#jane_telegram_collectorclientchannelinfopts) | Поле | ні |
| [__init__](jane_telegram_collector.client.md#jane_telegram_collectorclientchannelinfo__init__) | Конструктор dataclass | ні |

## jane_telegram_collector.client.ChannelInfo.__init__

**Конструктор dataclass.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:89](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L89).

```python
def __init__(self, channel_id: str, username: str | None, title: str | None, top_message_id: int, pts: int) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `channel_id` | `str` | `—` | positional-or-keyword |
| `username` | `str \| None` | `—` | positional-or-keyword |
| `title` | `str \| None` | `—` | positional-or-keyword |
| `top_message_id` | `int` | `—` | positional-or-keyword |
| `pts` | `int` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.client.ChannelInfo.channel_id

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:90](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L90).

```python
channel_id: str
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.client.ChannelInfo.username

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:91](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L91).

```python
username: str | None
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.client.ChannelInfo.title

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:92](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L92).

```python
title: str | None
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.client.ChannelInfo.top_message_id

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:93](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L93).

```python
top_message_id: int
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
Id of the newest message (0 for an empty channel).
```

## jane_telegram_collector.client.ChannelInfo.pts

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:95](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L95).

```python
pts: int
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
Current update sequence of the channel.
```

## jane_telegram_collector.client.ChangeBatch

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:100](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L100).

```python
class ChangeBatch:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [messages](jane_telegram_collector.client.md#jane_telegram_collectorclientchangebatchmessages) | Поле | ні |
| [pts](jane_telegram_collector.client.md#jane_telegram_collectorclientchangebatchpts) | Поле | ні |
| [final](jane_telegram_collector.client.md#jane_telegram_collectorclientchangebatchfinal) | Поле | ні |
| [too_long](jane_telegram_collector.client.md#jane_telegram_collectorclientchangebatchtoo_long) | Поле | ні |
| [__init__](jane_telegram_collector.client.md#jane_telegram_collectorclientchangebatch__init__) | Конструктор dataclass | ні |

## jane_telegram_collector.client.ChangeBatch.__init__

**Конструктор dataclass.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:100](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L100).

```python
def __init__(self, messages: Sequence[TgMessage], pts: int, final: bool, too_long: bool = False) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `messages` | `Sequence[TgMessage]` | `—` | positional-or-keyword |
| `pts` | `int` | `—` | positional-or-keyword |
| `final` | `bool` | `—` | positional-or-keyword |
| `too_long` | `bool` | `False` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.client.ChangeBatch.messages

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:101](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L101).

```python
messages: Sequence[TgMessage]
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
New and edited messages after the requested ``pts`` (current state of each message).
```

## jane_telegram_collector.client.ChangeBatch.pts

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:103](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L103).

```python
pts: int
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
``pts`` to continue from.
```

## jane_telegram_collector.client.ChangeBatch.final

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:105](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L105).

```python
final: bool
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
No more changes after ``pts`` right now.
```

## jane_telegram_collector.client.ChangeBatch.too_long

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:107](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L107).

```python
too_long: bool = False
```

Доступ: читання — так; запис — ні.

### Опис із вихідного коду

```text
The difference is too long (Telegram ``channelDifferenceTooLong``): edits in the gap are unavailable.
```

## jane_telegram_collector.client.ResolvedAccount

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:112](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L112).

```python
class ResolvedAccount:
```

Декоратори: `dataclass(frozen=True)`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [connection_id](jane_telegram_collector.client.md#jane_telegram_collectorclientresolvedaccountconnection_id) | Поле | ні |
| [params](jane_telegram_collector.client.md#jane_telegram_collectorclientresolvedaccountparams) | Поле | ні |
| [secrets](jane_telegram_collector.client.md#jane_telegram_collectorclientresolvedaccountsecrets) | Поле | ні |
| [__init__](jane_telegram_collector.client.md#jane_telegram_collectorclientresolvedaccount__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
A ``telegram_account`` connection with its secrets resolved in this service's environment.
```

## jane_telegram_collector.client.ResolvedAccount.__init__

**Конструктор dataclass.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:112](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L112).

```python
def __init__(self, connection_id: str | None, params: Mapping[str, object], secrets: Mapping[str, str] = <factory dict>) -> None:
```

Декоратори: `dataclass(frozen=True)`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `connection_id` | `str \| None` | `—` | positional-or-keyword |
| `params` | `Mapping[str, object]` | `—` | positional-or-keyword |
| `secrets` | `Mapping[str, str]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.client.ResolvedAccount.connection_id

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:115](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L115).

```python
connection_id: str | None
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.client.ResolvedAccount.params

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:116](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L116).

```python
params: Mapping[str, object]
```

Доступ: читання — так; запис — ні.

## jane_telegram_collector.client.ResolvedAccount.secrets

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:117](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L117).

```python
secrets: Mapping[str, str] = field(repr=False, default_factory=dict)
```

Доступ: читання — так; запис — ні.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict",
  "repr": "False"
}
```

## jane_telegram_collector.client.TelegramClient

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:120](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L120).

```python
class TelegramClient(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [resolve](jane_telegram_collector.client.md#jane_telegram_collectorclienttelegramclientresolve) | Метод | ні |
| [history](jane_telegram_collector.client.md#jane_telegram_collectorclienttelegramclienthistory) | Метод | ні |
| [get_message](jane_telegram_collector.client.md#jane_telegram_collectorclienttelegramclientget_message) | Метод | ні |
| [changes](jane_telegram_collector.client.md#jane_telegram_collectorclienttelegramclientchanges) | Метод | ні |
| [download_media](jane_telegram_collector.client.md#jane_telegram_collectorclienttelegramclientdownload_media) | Метод | ні |
| [close](jane_telegram_collector.client.md#jane_telegram_collectorclienttelegramclientclose) | Метод | ні |

## jane_telegram_collector.client.TelegramClient.resolve

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:121](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L121).

```python
async def resolve(self, *, username: str | None=None, channel_id: str | None=None) -> ChannelInfo:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `username` | `str \| None` | `None` | keyword-only |
| `channel_id` | `str \| None` | `None` | keyword-only |

Результат: `ChannelInfo`.

### Опис із вихідного коду

```text
Channel by ``username`` or ``channel_id``; :class:`ChannelUnavailable` if not accessible.
```

## jane_telegram_collector.client.TelegramClient.history

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:125](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L125).

```python
async def history(self, channel: ChannelInfo, *, after_id: int, limit: int, since: datetime | None=None) -> list[TgMessage]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `channel` | `ChannelInfo` | `—` | positional-or-keyword |
| `after_id` | `int` | `—` | keyword-only |
| `limit` | `int` | `—` | keyword-only |
| `since` | `datetime \| None` | `None` | keyword-only |

Результат: `list[TgMessage]`.

### Опис із вихідного коду

```text
Up to ``limit`` messages with ``message_id > after_id`` (and ``date >= since``), oldest first.
```

## jane_telegram_collector.client.TelegramClient.get_message

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:131](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L131).

```python
async def get_message(self, channel: ChannelInfo, message_id: int) -> TgMessage | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `channel` | `ChannelInfo` | `—` | positional-or-keyword |
| `message_id` | `int` | `—` | positional-or-keyword |

Результат: `TgMessage | None`.

## jane_telegram_collector.client.TelegramClient.changes

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:133](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L133).

```python
async def changes(self, channel: ChannelInfo, *, pts: int, limit: int) -> ChangeBatch:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `channel` | `ChannelInfo` | `—` | positional-or-keyword |
| `pts` | `int` | `—` | keyword-only |
| `limit` | `int` | `—` | keyword-only |

Результат: `ChangeBatch`.

## jane_telegram_collector.client.TelegramClient.download_media

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:135](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L135).

```python
async def download_media(self, channel: ChannelInfo, media: TgMedia, *, max_bytes: int) -> bytes:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `channel` | `ChannelInfo` | `—` | positional-or-keyword |
| `media` | `TgMedia` | `—` | positional-or-keyword |
| `max_bytes` | `int` | `—` | keyword-only |

Результат: `bytes`.

### Опис із вихідного коду

```text
Media bytes; more than ``max_bytes`` raises :class:`ValueError`.
```

## jane_telegram_collector.client.TelegramClient.close

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:139](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L139).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.client.ClientFactory

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:142](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L142).

```python
class ClientFactory(Protocol):
```

Базові типи / інтерфейси: `Protocol`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_telegram_collector.client.md#jane_telegram_collectorclientclientfactoryname) | Поле | ні |
| [open](jane_telegram_collector.client.md#jane_telegram_collectorclientclientfactoryopen) | Метод | ні |
| [requires_account](jane_telegram_collector.client.md#jane_telegram_collectorclientclientfactoryrequires_account) | Метод | ні |

## jane_telegram_collector.client.ClientFactory.name

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:143](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L143).

```python
name: str
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.client.ClientFactory.open

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:145](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L145).

```python
async def open(self, account: ResolvedAccount, *, connect_timeout_s: float) -> TelegramClient:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `account` | `ResolvedAccount` | `—` | positional-or-keyword |
| `connect_timeout_s` | `float` | `—` | keyword-only |

Результат: `TelegramClient`.

## jane_telegram_collector.client.ClientFactory.requires_account

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:147](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L147).

```python
def requires_account(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

### Опис із вихідного коду

```text
True if a ``telegram_account`` connection is mandatory for this backend.
```

## jane_telegram_collector.client.load_factory

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/client.py:152](../../../../../../services/telegram-collector/src/jane_telegram_collector/client.py#L152).

```python
def load_factory(settings: Settings) -> ClientFactory:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `settings` | `Settings` | `—` | positional-or-keyword |

Результат: `ClientFactory`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.
