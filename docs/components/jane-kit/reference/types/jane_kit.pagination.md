# Модуль `jane_kit.pagination`

> Згенеровано `scripts/docs_reference.py` з [libs/jane-kit/src/jane_kit/pagination.py](../../../../../libs/jane-kit/src/jane_kit/pagination.py). Не редагуйте вручну.

Cursor pagination per WP-00 conventions: ``?limit=&cursor=`` -> ``{"items": [...], "next_cursor": ... | null}``.

``limit`` above the service maximum is clamped (not rejected); there is no offset/page. Cursors are opaque to clients: :func:`encode_cursor` wraps any JSON-serialisable position (e.g. the last sort key) in URL-safe base64.

## Зміст

- [Клас `Page`](#клас-page)
- [Клас `PageLimits`](#клас-pagelimits)
- [Функція `clamp_limit`](#функція-clamp_limit)
- [Функція `decode_cursor`](#функція-decode_cursor)
- [Функція `encode_cursor`](#функція-encode_cursor)

## Класи

### Клас `Page`

| Властивість | Значення |
|---|---|
| Вид | модель Pydantic |
| Модуль | `jane_kit.pagination` |
| Успадкування | `BaseModel` |
| Код | [pagination.py:28](../../../../../libs/jane-kit/src/jane_kit/pagination.py#L28) |

```python
class Page(BaseModel): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `items` | `list[T]` | — | читання й запис |  |
| `next_cursor` | `str \| None` | `None` | читання й запис |  |

Поля без типового значення — обов'язкові аргументи конструктора; решта — необов'язкові іменовані.

### Клас `PageLimits`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_kit.pagination` |
| Успадкування | `Limits` |
| Код | [pagination.py:23](../../../../../libs/jane-kit/src/jane_kit/pagination.py#L23) |

```python
class PageLimits(Limits): ...
```

**Поля й властивості**

| Член | Тип | Типове значення | Доступ | Опис |
|---|---|---|---|---|
| `default_page_size` | `int` | `Field(default=50, ge=1)` | читання й запис |  |
| `max_page_size` | `int` | `Field(default=500, ge=1)` | читання й запис |  |

## Функції

### Функція `clamp_limit`

```python
def clamp_limit(requested: int | None, limits: PageLimits | None = None) -> int: ...
```

Код: [pagination.py:33](../../../../../libs/jane-kit/src/jane_kit/pagination.py#L33).

### Функція `decode_cursor`

```python
def decode_cursor(cursor: str) -> Any: ...
```

Винятки в коді функції: `ValidationFailed`.

Код: [pagination.py:45](../../../../../libs/jane-kit/src/jane_kit/pagination.py#L45).

### Функція `encode_cursor`

```python
def encode_cursor(position: Any) -> str: ...
```

Код: [pagination.py:40](../../../../../libs/jane-kit/src/jane_kit/pagination.py#L40).
