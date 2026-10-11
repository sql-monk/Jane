# jane_assistant.listing

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_assistant.listing.Position](#jane_assistantlistingposition)
- [jane_assistant.listing.CURSOR_TIME](#jane_assistantlistingcursor_time)
- [jane_assistant.listing.now_text](#jane_assistantlistingnow_text)
- [jane_assistant.listing.parse_time](#jane_assistantlistingparse_time)
- [jane_assistant.listing.encode_position](#jane_assistantlistingencode_position)
- [jane_assistant.listing.decode_position](#jane_assistantlistingdecode_position)

## jane_assistant.listing.Position

**Змінна.** Код: [services/assistant/src/jane_assistant/listing.py:20](../../../../../../services/assistant/src/jane_assistant/listing.py#L20).

```python
Position = tuple[datetime, str]
```

## jane_assistant.listing.CURSOR_TIME

**Константа.** Код: [services/assistant/src/jane_assistant/listing.py:21](../../../../../../services/assistant/src/jane_assistant/listing.py#L21).

```python
CURSOR_TIME = '%Y-%m-%dT%H:%M:%S.%fZ'
```

### Опис із вихідного коду

```text
The time of a cursor (UTC, microseconds) - also how sessions write their ``created_at``.
```

## jane_assistant.listing.now_text

**Функція.** Код: [services/assistant/src/jane_assistant/listing.py:27](../../../../../../services/assistant/src/jane_assistant/listing.py#L27).

```python
def now_text() -> str:
```

Результат: `str`.

## jane_assistant.listing.parse_time

**Функція.** Код: [services/assistant/src/jane_assistant/listing.py:31](../../../../../../services/assistant/src/jane_assistant/listing.py#L31).

```python
def parse_time(value: str) -> datetime:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `value` | `str` | `—` | positional-or-keyword |

Результат: `datetime`.

Явні `raise` у тілі: `ValueError`. Винятки викликаних залежностей описуються у ручному довіднику.

### Опис із вихідного коду

```text
A stored ``created_at`` (``...Z``, with or without microseconds) as an aware UTC time; ``ValueError`` else.
```

## jane_assistant.listing.encode_position

**Функція.** Код: [services/assistant/src/jane_assistant/listing.py:41](../../../../../../services/assistant/src/jane_assistant/listing.py#L41).

```python
def encode_position(position: Position) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `position` | `Position` | `—` | positional-or-keyword |

Результат: `str`.

## jane_assistant.listing.decode_position

**Функція.** Код: [services/assistant/src/jane_assistant/listing.py:45](../../../../../../services/assistant/src/jane_assistant/listing.py#L45).

```python
def decode_position(cursor: str | None) -> Position | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cursor` | `str \| None` | `—` | positional-or-keyword |

Результат: `Position | None`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.
