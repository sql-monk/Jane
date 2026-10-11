# Модуль `jane_telegram_collector.recorded`

> Згенеровано `scripts/docs_reference.py` з [services/telegram-collector/src/jane_telegram_collector/recorded.py](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py). Не редагуйте вручну.

Recorded Telegram backend: channels replayed from JSON recordings (tests, demos, offline replays).

A recording ``<recordings_dir>/<username or channel_id>.json``::

    {
      "channel": {"channel_id": "-1001234567890", "username": "city_events_example", "title": "City events"},
      "required_secrets": ["session"],          # optional: the account must resolve these secret_refs
      "messages": [{"id": 1, "date": "2026-09-01T10:00:00Z", "text": "...", "edit_date": null,
                    "views": 10, "grouped_id": null, "author": null,
                    "media": [{"kind": "photo", "name": "p.jpg", "media_type": "image/jpeg", "data_base64": "..."}],
                    "service": null}],          # a service message: its action, e.g. "channel_create"
      "events": [{"pts": 1, "message": {...message as it was after this update...}}],
      "min_pts": 0,                             # updates before this pts are gone -> difference too long
      "faults": [{"method": "history", "flood_wait": 3, "count": 1},
                 {"method": "changes", "delay_ms": 500, "count": 1},
                 {"method": "resolve", "unavailable": true, "count": 1}]
    }

The file is re-read on every call, so another process (a test) may post and edit messages while the collector runs. Consumed faults are counted in ``<file>.faults.json`` next to the recording. :class:`Recording` writes the format (new message -> ``messages`` + event, edit -> updated message + event).

## Класи

### Клас `RecordedClient`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.recorded` |
| Код | [recorded.py:107](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L107) |

```python
class RecordedClient: ...
```

#### Конструктор `RecordedClient.__init__`

```python
def __init__(self, root: Path, account: ResolvedAccount) -> None: ...
```

Код: [recorded.py:108](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L108).

#### Метод `RecordedClient.resolve`

```python
async def resolve(
    self,
    *,
    username: str | None = None,
    channel_id: str | None = None,
) -> ChannelInfo: ...
```

Код: [recorded.py:195](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L195).

#### Метод `RecordedClient.history`

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

Код: [recorded.py:210](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L210).

#### Метод `RecordedClient.get_message`

```python
async def get_message(self, channel: ChannelInfo, message_id: int) -> TgMessage | None: ...
```

Код: [recorded.py:225](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L225).

#### Метод `RecordedClient.changes`

```python
async def changes(self, channel: ChannelInfo, *, pts: int, limit: int) -> ChangeBatch: ...
```

Код: [recorded.py:234](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L234).

#### Метод `RecordedClient.download_media`

```python
async def download_media(
    self,
    channel: ChannelInfo,
    media: TgMedia,
    *,
    max_bytes: int,
) -> bytes: ...
```

Винятки в коді методу: `ChannelUnavailable`, `ValueError`.

Код: [recorded.py:251](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L251).

#### Метод `RecordedClient.close`

```python
async def close(self) -> None: ...
```

Код: [recorded.py:263](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L263).

### Клас `RecordedClientFactory`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.recorded` |
| Код | [recorded.py:92](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L92) |

```python
class RecordedClientFactory: ...
```

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `name` | `'recorded'` |  |

#### Конструктор `RecordedClientFactory.__init__`

```python
def __init__(self, recordings_dir: Path | None) -> None: ...
```

Код: [recorded.py:95](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L95).

#### Метод `RecordedClientFactory.requires_account`

```python
def requires_account(self) -> bool: ...
```

Код: [recorded.py:98](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L98).

#### Метод `RecordedClientFactory.open`

```python
async def open(self, account: ResolvedAccount, *, connect_timeout_s: float) -> TelegramClient: ...
```

Винятки в коді методу: `ClientUnavailable`.

Код: [recorded.py:101](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L101).

### Клас `Recording`

| Властивість | Значення |
|---|---|
| Вид | dataclass |
| Модуль | `jane_telegram_collector.recorded` |
| Код | [recorded.py:268](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L268) |

```python
@dataclass
class Recording: ...
```

Writer of a recording file (for tests and hand-made demos).

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `path` | `Path` | — | читання й запис |  |
| `channel_id` | `str` | — | читання й запис |  |
| `username` | `str \| None` | `None` | читання й запис |  |
| `title` | `str \| None` | `None` | читання й запис |  |
| `data` | `dict[str, Any]` | `field(default_factory=dict)` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

#### Метод `Recording.create`

```python
@classmethod
def create(
    cls,
    root: Path,
    *,
    channel_id: str,
    username: str | None = None,
    title: str | None = None,
) -> Recording: ...
```

Код: [recorded.py:278](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L278).

#### Метод `Recording.save`

```python
def save(self) -> None: ...
```

Код: [recorded.py:294](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L294).

#### Метод `Recording.reload`

```python
def reload(self) -> None: ...
```

Код: [recorded.py:297](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L297).

#### Метод `Recording.post`

```python
def post(
    self,
    text: str,
    *,
    date: datetime | None = None,
    media: list[dict[str, Any]] | None = None,
    save: bool = True,
    **extra: Any,
) -> int: ...
```

Код: [recorded.py:304](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L304).

#### Метод `Recording.edit`

```python
def edit(
    self,
    message_id: int,
    text: str,
    *,
    edit_date: datetime | None = None,
    save: bool = True,
) -> None: ...
```

Винятки в коді методу: `KeyError`.

Код: [recorded.py:329](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L329).

#### Метод `Recording.redeliver`

```python
def redeliver(self, message_id: int) -> None: ...
```

Append an update carrying the current (unchanged) state of a message again.

Код: [recorded.py:343](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L343).

#### Метод `Recording.set`

```python
def set(self, key: str, value: Any) -> None: ...
```

Код: [recorded.py:349](../../../../../services/telegram-collector/src/jane_telegram_collector/recorded.py#L349).
