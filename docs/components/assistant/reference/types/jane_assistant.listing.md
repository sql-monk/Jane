# Модуль `jane_assistant.listing`

> Згенеровано `scripts/docs_reference.py` з [services/assistant/src/jane_assistant/listing.py](../../../../../services/assistant/src/jane_assistant/listing.py). Не редагуйте вручну.

Positions and cursors of the list operations (``listOnboardingSessions``, ``listImprovementRuns``).

A list is ordered newest first by ``(created_at, id)``; a cursor is the opaque form of the position of the last item of a page (``jane_kit.pagination.encode_cursor``). Its time is always written and read in one fixed UTC format with microseconds, so the position compares the same way in memory and in PostgreSQL (``timestamptz``); anything else - garbage, a naive time, another format, an id that is no service id - is ``validation_failed`` (422), never a server error.

## Зміст

- [Функція `decode_position`](#функція-decode_position)
- [Функція `encode_position`](#функція-encode_position)
- [Функція `now_text`](#функція-now_text)
- [Функція `parse_time`](#функція-parse_time)

## Функції

### Функція `decode_position`

```python
def decode_position(cursor: str | None) -> Position | None: ...
```

Винятки в коді функції: `ValidationFailed`.

Код: [listing.py:45](../../../../../services/assistant/src/jane_assistant/listing.py#L45).

### Функція `encode_position`

```python
def encode_position(position: Position) -> str: ...
```

Код: [listing.py:41](../../../../../services/assistant/src/jane_assistant/listing.py#L41).

### Функція `now_text`

```python
def now_text() -> str: ...
```

Код: [listing.py:27](../../../../../services/assistant/src/jane_assistant/listing.py#L27).

### Функція `parse_time`

```python
def parse_time(value: str) -> datetime: ...
```

A stored ``created_at`` (``...Z``, with or without microseconds) as an aware UTC time; ``ValueError`` else.

Винятки в коді функції: `ValueError`.

Код: [listing.py:31](../../../../../services/assistant/src/jane_assistant/listing.py#L31).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `CURSOR_TIME` | — | `'%Y-%m-%dT%H:%M:%S.%fZ'` | The time of a cursor (UTC, microseconds) - also how sessions write their ``created_at``. |
| `Position` | — | `tuple[datetime, str]` |  |
