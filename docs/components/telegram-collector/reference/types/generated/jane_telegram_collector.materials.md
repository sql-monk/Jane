# jane_telegram_collector.materials

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_telegram_collector.materials.ContentTooLarge](#jane_telegram_collectormaterialscontenttoolarge)
- [jane_telegram_collector.materials.rfc3339](#jane_telegram_collectormaterialsrfc3339)
- [jane_telegram_collector.materials.new_observation_id](#jane_telegram_collectormaterialsnew_observation_id)
- [jane_telegram_collector.materials.message_sequence](#jane_telegram_collectormaterialsmessage_sequence)
- [jane_telegram_collector.materials.revision_sequence](#jane_telegram_collectormaterialsrevision_sequence)
- [jane_telegram_collector.materials.message_sha](#jane_telegram_collectormaterialsmessage_sha)
- [jane_telegram_collector.materials.TransitStore](#jane_telegram_collectormaterialstransitstore)
- [jane_telegram_collector.materials.TransitStore.__init__](#jane_telegram_collectormaterialstransitstore__init__)
- [jane_telegram_collector.materials.Delivery](#jane_telegram_collectormaterialsdelivery)
- [jane_telegram_collector.materials.Delivery.content_ref](#jane_telegram_collectormaterialsdeliverycontent_ref)
- [jane_telegram_collector.materials.build_material](#jane_telegram_collectormaterialsbuild_material)

## jane_telegram_collector.materials.ContentTooLarge

**Повторний експорт.** Код: [services/telegram-collector/src/jane_telegram_collector/materials.py:28](../../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L28).

```python
from jane_kit.content import ContentTooLarge as ContentTooLarge
```

Повторний експорт: [jane_kit.content.ContentTooLarge](../../../../jane-kit/reference/types/generated/jane_kit.content.md#jane_kitcontentcontenttoolarge).

## jane_telegram_collector.materials.rfc3339

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/materials.py:45](../../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L45).

```python
def rfc3339(dt: datetime) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `dt` | `datetime` | `—` | positional-or-keyword |

Результат: `str`.

## jane_telegram_collector.materials.new_observation_id

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/materials.py:53](../../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L53).

```python
def new_observation_id() -> str:
```

Результат: `str`.

### Опис із вихідного коду

```text
``obs_`` + 12 hex of epoch ms + 4 hex counter + 8 hex random: sortable, monotonic within a process.
```

## jane_telegram_collector.materials.message_sequence

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/materials.py:80](../../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L80).

```python
def message_sequence(msg: TgMessage) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `msg` | `TgMessage` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
``revision.sequence`` of the first revision with this ``edit_date`` second.
```

## jane_telegram_collector.materials.revision_sequence

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/materials.py:85](../../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L85).

```python
def revision_sequence(msg: TgMessage, sha: str, seen: tuple[int, str] | None) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `msg` | `TgMessage` | `—` | positional-or-keyword |
| `sha` | `str` | `—` | positional-or-keyword |
| `seen` | `tuple[int, str] \| None` | `—` | positional-or-keyword |

Результат: `int`.

### Опис із вихідного коду

```text
``revision.sequence`` of ``msg`` given the last revision seen for the message (``sequence``, text sha256).

Another text within the second of the seen revision gets the next number, so every new revision has a
strictly larger sequence (Telegram's ``edit_date`` has only second precision); the same text keeps the seen
sequence (a repeated delivery); an older ``edit_date`` gives a smaller sequence (the caller skips it).
```

## jane_telegram_collector.materials.message_sha

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/materials.py:103](../../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L103).

```python
def message_sha(msg: TgMessage) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `msg` | `TgMessage` | `—` | positional-or-keyword |

Результат: `str`.

## jane_telegram_collector.materials.TransitStore

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/materials.py:107](../../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L107).

```python
class TransitStore(FileTransitStore):
```

Базові типи / інтерфейси: `FileTransitStore`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_telegram_collector.materials.md#jane_telegram_collectormaterialstransitstore__init__) | Конструктор | ні |
| [root](../../../../jane-kit/reference/types/generated/jane_kit.content.md#jane_kitcontentfiletransitstoreroot) | Поле екземпляра | так |
| [producer](../../../../jane-kit/reference/types/generated/jane_kit.content.md#jane_kitcontentfiletransitstoreproducer) | Поле екземпляра | так |
| [base](../../../../jane-kit/reference/types/generated/jane_kit.content.md#jane_kitcontentfiletransitstorebase) | Властивість | так |
| [put](../../../../jane-kit/reference/types/generated/jane_kit.content.md#jane_kitcontentfiletransitstoreput) | Метод | так |
| [cleanup](../../../../jane-kit/reference/types/generated/jane_kit.content.md#jane_kitcontentfiletransitstorecleanup) | Метод | так |

### Опис із вихідного коду

```text
Transit blobs of this collector (``<root>/telegram-collector/...``, ``file://`` URIs) - jane-kit's shared writer
and cleaner (R18, ADR-0004).
```

## jane_telegram_collector.materials.TransitStore.__init__

**Конструктор.** Код: [services/telegram-collector/src/jane_telegram_collector/materials.py:111](../../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L111).

```python
def __init__(self, root: Path) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `root` | `Path` | `—` | positional-or-keyword |

Результат: `None`.

## jane_telegram_collector.materials.Delivery

**Клас.** Код: [services/telegram-collector/src/jane_telegram_collector/materials.py:115](../../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L115).

```python
class Delivery(ContentWriter):
```

Базові типи / інтерфейси: `ContentWriter`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [content_ref](jane_telegram_collector.materials.md#jane_telegram_collectormaterialsdeliverycontent_ref) | Метод | ні |
| [mode](../../../../jane-kit/reference/types/generated/jane_kit.content.md#jane_kitcontentcontentwritermode) | Поле | так |
| [inline_max_bytes](../../../../jane-kit/reference/types/generated/jane_kit.content.md#jane_kitcontentcontentwriterinline_max_bytes) | Поле | так |
| [transit_ttl_seconds](../../../../jane-kit/reference/types/generated/jane_kit.content.md#jane_kitcontentcontentwritertransit_ttl_seconds) | Поле | так |
| [store](../../../../jane-kit/reference/types/generated/jane_kit.content.md#jane_kitcontentcontentwriterstore) | Поле | так |
| [ref](../../../../jane-kit/reference/types/generated/jane_kit.content.md#jane_kitcontentcontentwriterref) | Метод | так |
| [blob](../../../../jane-kit/reference/types/generated/jane_kit.content.md#jane_kitcontentcontentwriterblob) | Метод | так |

### Опис із вихідного коду

```text
Content delivery of the collector (``content_delivery`` auto | inline | blob, ADR-0004).
```

## jane_telegram_collector.materials.Delivery.content_ref

**Метод.** Код: [services/telegram-collector/src/jane_telegram_collector/materials.py:118](../../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L118).

```python
def content_ref(self, body: bytes, media_type: str, name: str, now: datetime, *, text: bool) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `body` | `bytes` | `—` | positional-or-keyword |
| `media_type` | `str` | `—` | positional-or-keyword |
| `name` | `str` | `—` | positional-or-keyword |
| `now` | `datetime` | `—` | positional-or-keyword |
| `text` | `bool` | `—` | keyword-only |

Результат: `dict[str, Any]`.

## jane_telegram_collector.materials.build_material

**Функція.** Код: [services/telegram-collector/src/jane_telegram_collector/materials.py:133](../../../../../../services/telegram-collector/src/jane_telegram_collector/materials.py#L133).

```python
def build_material(msg: TgMessage, channel: ChannelInfo, *, observation_id: str, delivery: Delivery, collector_version: str, source_id: str | None=None, strategy: str | None=None, rules_ref: Mapping[str, Any] | None=None, collection_id: str | None=None, attachments: Sequence[tuple[TgMedia, dict[str, Any]]]=(), diagnostics: Sequence[Mapping[str, Any]]=(), now: datetime | None=None, sequence: int | None=None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `msg` | `TgMessage` | `—` | positional-or-keyword |
| `channel` | `ChannelInfo` | `—` | positional-or-keyword |
| `observation_id` | `str` | `—` | keyword-only |
| `delivery` | `Delivery` | `—` | keyword-only |
| `collector_version` | `str` | `—` | keyword-only |
| `source_id` | `str \| None` | `None` | keyword-only |
| `strategy` | `str \| None` | `None` | keyword-only |
| `rules_ref` | `Mapping[str, Any] \| None` | `None` | keyword-only |
| `collection_id` | `str \| None` | `None` | keyword-only |
| `attachments` | `Sequence[tuple[TgMedia, dict[str, Any]]]` | `()` | keyword-only |
| `diagnostics` | `Sequence[Mapping[str, Any]]` | `()` | keyword-only |
| `now` | `datetime \| None` | `None` | keyword-only |
| `sequence` | `int \| None` | `None` | keyword-only |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
``sequence``: the revision number computed against the state (:func:`revision_sequence`); without it the
first number of the ``edit_date`` second.
```
