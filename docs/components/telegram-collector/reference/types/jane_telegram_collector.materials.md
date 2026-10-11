# Модуль `jane_telegram_collector.materials`

> Згенеровано `scripts/docs_reference.py` з [services/telegram-collector/src/jane_telegram_collector/materials.py](../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py). Не редагуйте вручну.

Material documents for Telegram messages (``material.schema.json``) and content delivery (ADR-0004).

* ``material_id`` = ``tg:<channel_id>:<message_id>`` — the same for every observation of the message;
* ``observation_id`` — new for every read from Telegram (history, update, edit, one-shot fetch);
* ``revision.sequence`` = ``edit_date`` (or ``date`` for an unedited message) in epoch seconds x :data:`SEQUENCE_SCALE` + the number of the revision the collector saw within that second (0 for the first): strictly larger for every new revision, also for several edits within one second (R04, ``material.schema.json``); ``revision.source_revision`` keeps ``edit_date`` in epoch seconds as Telegram gives it; ``revision.is_edit`` = Telegram marked the message as edited, ``revision.content_sha256`` = sha256 of the text;
* a service message of the channel (channel created, message pinned...) is a material too, with its action in ``metadata.service_action`` (R30);
* content: the message text (``text/plain``, UTF-8) inline, or a transit blob (``file://``) if asked or larger than ``transfer.inline_max_bytes``; downloaded media go to ``attachments`` the same way. The ``ContentRef`` writer and the transit cleaner are jane-kit's shared :mod:`jane_kit.content` (R18).

## Зміст

- [Клас `Delivery`](#клас-delivery)
- [Клас `TransitStore`](#клас-transitstore)
- [Функція `build_material`](#функція-build_material)
- [Функція `message_sequence`](#функція-message_sequence)
- [Функція `message_sha`](#функція-message_sha)
- [Функція `new_observation_id`](#функція-new_observation_id)
- [Функція `revision_sequence`](#функція-revision_sequence)
- [Функція `rfc3339`](#функція-rfc3339)

## Класи

### Клас `Delivery`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.materials` |
| Успадкування | `ContentWriter` |
| Код | [materials.py:115](../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L115) |

```python
class Delivery(ContentWriter): ...
```

Content delivery of the collector (``content_delivery`` auto | inline | blob, ADR-0004).

#### Метод `Delivery.content_ref`

```python
def content_ref(
    self,
    body: bytes,
    media_type: str,
    name: str,
    now: datetime,
    *,
    text: bool,
) -> dict[str, Any]: ...
```

Код: [materials.py:118](../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L118).

### Клас `TransitStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_telegram_collector.materials` |
| Успадкування | `FileTransitStore` |
| Код | [materials.py:107](../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L107) |

```python
class TransitStore(FileTransitStore): ...
```

Transit blobs of this collector (``<root>/telegram-collector/...``, ``file://`` URIs) - jane-kit's shared writer and cleaner (R18, ADR-0004).

#### Конструктор `TransitStore.__init__`

```python
def __init__(self, root: Path) -> None: ...
```

Код: [materials.py:111](../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L111).

## Функції

### Функція `build_material`

```python
def build_material(
    msg: TgMessage,
    channel: ChannelInfo,
    *,
    observation_id: str,
    delivery: Delivery,
    collector_version: str,
    source_id: str | None = None,
    strategy: str | None = None,
    rules_ref: Mapping[str, Any] | None = None,
    collection_id: str | None = None,
    attachments: Sequence[tuple[TgMedia, dict[str, Any]]] = (),
    diagnostics: Sequence[Mapping[str, Any]] = (),
    now: datetime | None = None,
    sequence: int | None = None,
) -> dict[str, Any]: ...
```

``sequence``: the revision number computed against the state (:func:`revision_sequence`); without it the first number of the ``edit_date`` second.

Код: [materials.py:133](../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L133).

### Функція `message_sequence`

```python
def message_sequence(msg: TgMessage) -> int: ...
```

``revision.sequence`` of the first revision with this ``edit_date`` second.

Код: [materials.py:80](../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L80).

### Функція `message_sha`

```python
def message_sha(msg: TgMessage) -> str: ...
```

Код: [materials.py:103](../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L103).

### Функція `new_observation_id`

```python
def new_observation_id() -> str: ...
```

``obs_`` + 12 hex of epoch ms + 4 hex counter + 8 hex random: sortable, monotonic within a process.

Код: [materials.py:53](../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L53).

### Функція `revision_sequence`

```python
def revision_sequence(msg: TgMessage, sha: str, seen: tuple[int, str] | None) -> int: ...
```

``revision.sequence`` of ``msg`` given the last revision seen for the message (``sequence``, text sha256).

Another text within the second of the seen revision gets the next number, so every new revision has a strictly larger sequence (Telegram's ``edit_date`` has only second precision); the same text keeps the seen sequence (a repeated delivery); an older ``edit_date`` gives a smaller sequence (the caller skips it).

Код: [materials.py:85](../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L85).

### Функція `rfc3339`

```python
def rfc3339(dt: datetime) -> str: ...
```

Код: [materials.py:45](../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L45).

## Реекспорт

| Назва | Визначено в |
|---|---|
| `ContentTooLarge` | `jane_kit.content` |
