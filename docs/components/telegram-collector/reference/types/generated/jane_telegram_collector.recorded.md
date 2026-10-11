# jane_telegram_collector.recorded

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_telegram_collector.recorded.RecordedClientFactory](#jane_telegram_collectorrecordedrecordedclientfactory)
- [jane_telegram_collector.recorded.RecordedClientFactory.name](#jane_telegram_collectorrecordedrecordedclientfactoryname)
- [jane_telegram_collector.recorded.RecordedClientFactory.__init__](#jane_telegram_collectorrecordedrecordedclientfactory__init__)
- [jane_telegram_collector.recorded.RecordedClientFactory.recordings_dir](#jane_telegram_collectorrecordedrecordedclientfactoryrecordings_dir)
- [jane_telegram_collector.recorded.RecordedClientFactory.requires_account](#jane_telegram_collectorrecordedrecordedclientfactoryrequires_account)
- [jane_telegram_collector.recorded.RecordedClientFactory.open](#jane_telegram_collectorrecordedrecordedclientfactoryopen)
- [jane_telegram_collector.recorded.RecordedClient](#jane_telegram_collectorrecordedrecordedclient)
- [jane_telegram_collector.recorded.RecordedClient.__init__](#jane_telegram_collectorrecordedrecordedclient__init__)
- [jane_telegram_collector.recorded.RecordedClient.root](#jane_telegram_collectorrecordedrecordedclientroot)
- [jane_telegram_collector.recorded.RecordedClient.account](#jane_telegram_collectorrecordedrecordedclientaccount)
- [jane_telegram_collector.recorded.RecordedClient.resolve](#jane_telegram_collectorrecordedrecordedclientresolve)
- [jane_telegram_collector.recorded.RecordedClient.history](#jane_telegram_collectorrecordedrecordedclienthistory)
- [jane_telegram_collector.recorded.RecordedClient.get_message](#jane_telegram_collectorrecordedrecordedclientget_message)
- [jane_telegram_collector.recorded.RecordedClient.changes](#jane_telegram_collectorrecordedrecordedclientchanges)
- [jane_telegram_collector.recorded.RecordedClient.download_media](#jane_telegram_collectorrecordedrecordedclientdownload_media)
- [jane_telegram_collector.recorded.RecordedClient.close](#jane_telegram_collectorrecordedrecordedclientclose)
- [jane_telegram_collector.recorded.Recording](#jane_telegram_collectorrecordedrecording)
- [jane_telegram_collector.recorded.Recording.__init__](#jane_telegram_collectorrecordedrecording__init__)
- [jane_telegram_collector.recorded.Recording.path](#jane_telegram_collectorrecordedrecordingpath)
- [jane_telegram_collector.recorded.Recording.channel_id](#jane_telegram_collectorrecordedrecordingchannel_id)
- [jane_telegram_collector.recorded.Recording.username](#jane_telegram_collectorrecordedrecordingusername)
- [jane_telegram_collector.recorded.Recording.title](#jane_telegram_collectorrecordedrecordingtitle)
- [jane_telegram_collector.recorded.Recording.data](#jane_telegram_collectorrecordedrecordingdata)
- [jane_telegram_collector.recorded.Recording.create](#jane_telegram_collectorrecordedrecordingcreate)
- [jane_telegram_collector.recorded.Recording.save](#jane_telegram_collectorrecordedrecordingsave)
- [jane_telegram_collector.recorded.Recording.reload](#jane_telegram_collectorrecordedrecordingreload)
- [jane_telegram_collector.recorded.Recording.post](#jane_telegram_collectorrecordedrecordingpost)
- [jane_telegram_collector.recorded.Recording.edit](#jane_telegram_collectorrecordedrecordingedit)
- [jane_telegram_collector.recorded.Recording.redeliver](#jane_telegram_collectorrecordedrecordingredeliver)
- [jane_telegram_collector.recorded.Recording.set](#jane_telegram_collectorrecordedrecordingset)

## jane_telegram_collector.recorded.RecordedClientFactory

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:92](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L92).

```python
class RecordedClientFactory:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordedclientfactoryname) | Поле | ні |
| [__init__](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordedclientfactory__init__) | Конструктор | ні |
| [recordings_dir](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordedclientfactoryrecordings_dir) | Поле екземпляра | ні |
| [requires_account](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordedclientfactoryrequires_account) | Метод | ні |
| [open](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordedclientfactoryopen) | Метод | ні |

## jane_telegram_collector.recorded.RecordedClientFactory.name

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:93](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L93).

```python
name = 'recorded'
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.recorded.RecordedClientFactory.__init__

**Конструктор.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:95](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L95).

```python
def __init__(self, recordings_dir: Path | None) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `recordings_dir` | `Path \| None` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.recorded.RecordedClientFactory.recordings_dir

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:96](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L96).

```python
self.recordings_dir = recordings_dir
```

## jane_telegram_collector.recorded.RecordedClientFactory.requires_account

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:98](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L98).

```python
def requires_account(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_telegram_collector.recorded.RecordedClientFactory.open

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:101](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L101).

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

Явні `raise` у тілі: `ClientUnavailable`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_telegram_collector.recorded.RecordedClient

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:107](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L107).

```python
class RecordedClient:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordedclient__init__) | Конструктор | ні |
| [root](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordedclientroot) | Поле екземпляра | ні |
| [account](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordedclientaccount) | Поле екземпляра | ні |
| [resolve](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordedclientresolve) | Метод | ні |
| [history](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordedclienthistory) | Метод | ні |
| [get_message](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordedclientget_message) | Метод | ні |
| [changes](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordedclientchanges) | Метод | ні |
| [download_media](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordedclientdownload_media) | Метод | ні |
| [close](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordedclientclose) | Метод | ні |

## jane_telegram_collector.recorded.RecordedClient.__init__

**Конструктор.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:108](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L108).

```python
def __init__(self, root: Path, account: ResolvedAccount) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `root` | `Path` | `—` | positional-or-keyword |
| `account` | `ResolvedAccount` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.recorded.RecordedClient.root

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:109](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L109).

```python
self.root = root
```

## jane_telegram_collector.recorded.RecordedClient.account

**Поле екземпляра.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:110](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L110).

```python
self.account = account
```

## jane_telegram_collector.recorded.RecordedClient.resolve

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:195](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L195).

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

## jane_telegram_collector.recorded.RecordedClient.history

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:210](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L210).

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

## jane_telegram_collector.recorded.RecordedClient.get_message

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:225](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L225).

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

## jane_telegram_collector.recorded.RecordedClient.changes

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:234](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L234).

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

## jane_telegram_collector.recorded.RecordedClient.download_media

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:251](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L251).

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

Явні `raise` у тілі: `ChannelUnavailable`, `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_telegram_collector.recorded.RecordedClient.close

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:263](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L263).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.recorded.Recording

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:268](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L268).

```python
class Recording:
```

Декоратори: `dataclass`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [path](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordingpath) | Поле | ні |
| [channel_id](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordingchannel_id) | Поле | ні |
| [username](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordingusername) | Поле | ні |
| [title](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordingtitle) | Поле | ні |
| [data](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordingdata) | Поле | ні |
| [create](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordingcreate) | Метод | ні |
| [save](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordingsave) | Метод | ні |
| [reload](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordingreload) | Метод | ні |
| [post](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordingpost) | Метод | ні |
| [edit](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordingedit) | Метод | ні |
| [redeliver](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordingredeliver) | Метод | ні |
| [set](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecordingset) | Метод | ні |
| [__init__](jane_telegram_collector.recorded.md#jane_telegram_collectorrecordedrecording__init__) | Конструктор dataclass | ні |

### Опис із вихідного коду

```text
Writer of a recording file (for tests and hand-made demos).
```

## jane_telegram_collector.recorded.Recording.__init__

**Конструктор dataclass.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:268](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L268).

```python
def __init__(self, path: Path, channel_id: str, username: str | None = None, title: str | None = None, data: dict[str, Any] = <factory dict>) -> None:
```

Декоратори: `dataclass`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `path` | `Path` | `—` | positional-or-keyword |
| `channel_id` | `str` | `—` | positional-or-keyword |
| `username` | `str \| None` | `None` | positional-or-keyword |
| `title` | `str \| None` | `None` | positional-or-keyword |
| `data` | `dict[str, Any]` | `factory: dict` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.recorded.Recording.path

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:271](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L271).

```python
path: Path
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.recorded.Recording.channel_id

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:272](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L272).

```python
channel_id: str
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.recorded.Recording.username

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:273](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L273).

```python
username: str | None = None
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.recorded.Recording.title

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:274](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L274).

```python
title: str | None = None
```

Доступ: читання — так; запис — так.

## jane_telegram_collector.recorded.Recording.data

**Поле.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:275](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L275).

```python
data: dict[str, Any] = field(default_factory=dict)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default_factory": "dict"
}
```

## jane_telegram_collector.recorded.Recording.create

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:278](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L278).

```python
def create(cls, root: Path, *, channel_id: str, username: str | None=None, title: str | None=None) -> Recording:
```

Декоратори: `classmethod`.

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cls` | `не вказано` | `—` | positional-or-keyword |
| `root` | `Path` | `—` | positional-or-keyword |
| `channel_id` | `str` | `—` | keyword-only |
| `username` | `str \| None` | `None` | keyword-only |
| `title` | `str \| None` | `None` | keyword-only |

Результат: `Recording`.

## jane_telegram_collector.recorded.Recording.save

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:294](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L294).

```python
def save(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.recorded.Recording.reload

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:297](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L297).

```python
def reload(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.recorded.Recording.post

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:304](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L304).

```python
def post(self, text: str, *, date: datetime | None=None, media: list[dict[str, Any]] | None=None, save: bool=True, **extra: Any) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `text` | `str` | `—` | positional-or-keyword |
| `date` | `datetime \| None` | `None` | keyword-only |
| `media` | `list[dict[str, Any]] \| None` | `None` | keyword-only |
| `save` | `bool` | `True` | keyword-only |
| `extra` | `Any` | `—` | var-keyword |

Результат: `int`.

## jane_telegram_collector.recorded.Recording.edit

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:329](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L329).

```python
def edit(self, message_id: int, text: str, *, edit_date: datetime | None=None, save: bool=True) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `message_id` | `int` | `—` | positional-or-keyword |
| `text` | `str` | `—` | positional-or-keyword |
| `edit_date` | `datetime \| None` | `None` | keyword-only |
| `save` | `bool` | `True` | keyword-only |

Результат: `None`.

Явні `raise` у тілі: `KeyError`. Винятки викликаних залежностей описуються у ручному довіднику.

## jane_telegram_collector.recorded.Recording.redeliver

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:343](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L343).

```python
def redeliver(self, message_id: int) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `message_id` | `int` | `—` | positional-or-keyword |

Результат: `None`.

### Опис із вихідного коду

```text
Append an update carrying the current (unchanged) state of a message again.
```

## jane_telegram_collector.recorded.Recording.set

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/recorded.py:349](../../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L349).

```python
def set(self, key: str, value: Any) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `key` | `str` | `—` | positional-or-keyword |
| `value` | `Any` | `—` | positional-or-keyword |

Результат: `None`.
