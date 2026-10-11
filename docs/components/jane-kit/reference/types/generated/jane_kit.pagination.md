# jane_kit.pagination

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_kit.pagination.PageLimits](#jane_kitpaginationpagelimits)
- [jane_kit.pagination.PageLimits.default_page_size](#jane_kitpaginationpagelimitsdefault_page_size)
- [jane_kit.pagination.PageLimits.max_page_size](#jane_kitpaginationpagelimitsmax_page_size)
- [jane_kit.pagination.Page](#jane_kitpaginationpage)
- [jane_kit.pagination.Page.items](#jane_kitpaginationpageitems)
- [jane_kit.pagination.Page.next_cursor](#jane_kitpaginationpagenext_cursor)
- [jane_kit.pagination.clamp_limit](#jane_kitpaginationclamp_limit)
- [jane_kit.pagination.encode_cursor](#jane_kitpaginationencode_cursor)
- [jane_kit.pagination.decode_cursor](#jane_kitpaginationdecode_cursor)

## jane_kit.pagination.PageLimits

**Клас.** Код: [libs/jane-kit/src/jane_kit/pagination.py:23](../../../../../../libs/jane-kit/src/jane_kit/pagination.py#L23).

```python
class PageLimits(Limits):
```

Базові типи / інтерфейси: `Limits`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [default_page_size](jane_kit.pagination.md#jane_kitpaginationpagelimitsdefault_page_size) | Поле | ні |
| [max_page_size](jane_kit.pagination.md#jane_kitpaginationpagelimitsmax_page_size) | Поле | ні |
| [model_config](jane_kit.config.md#jane_kitconfiglimitsmodel_config) | Поле | так |

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_tracing_pagination.py:35](../../../../../../libs/jane-kit/tests/test_tracing_pagination.py#L35).

```python
limits = PageLimits(default_page_size=50, max_page_size=100)
```

## jane_kit.pagination.PageLimits.default_page_size

**Поле.** Код: [libs/jane-kit/src/jane_kit/pagination.py:24](../../../../../../libs/jane-kit/src/jane_kit/pagination.py#L24).

```python
default_page_size: int = Field(default=50, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "50",
  "ge": "1"
}
```

## jane_kit.pagination.PageLimits.max_page_size

**Поле.** Код: [libs/jane-kit/src/jane_kit/pagination.py:25](../../../../../../libs/jane-kit/src/jane_kit/pagination.py#L25).

```python
max_page_size: int = Field(default=500, ge=1)
```

Доступ: читання — так; запис — так.

Обмеження й метадані декларації:

```json
{
  "default": "500",
  "ge": "1"
}
```

## jane_kit.pagination.Page

**Клас.** Код: [libs/jane-kit/src/jane_kit/pagination.py:28](../../../../../../libs/jane-kit/src/jane_kit/pagination.py#L28).

```python
class Page(BaseModel):
```

Базові типи / інтерфейси: `BaseModel`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [items](jane_kit.pagination.md#jane_kitpaginationpageitems) | Поле | ні |
| [next_cursor](jane_kit.pagination.md#jane_kitpaginationpagenext_cursor) | Поле | ні |

## jane_kit.pagination.Page.items

**Поле.** Код: [libs/jane-kit/src/jane_kit/pagination.py:29](../../../../../../libs/jane-kit/src/jane_kit/pagination.py#L29).

```python
items: list[T]
```

Доступ: читання — так; запис — так.

## jane_kit.pagination.Page.next_cursor

**Поле.** Код: [libs/jane-kit/src/jane_kit/pagination.py:30](../../../../../../libs/jane-kit/src/jane_kit/pagination.py#L30).

```python
next_cursor: str | None = None
```

Доступ: читання — так; запис — так.

## jane_kit.pagination.clamp_limit

**Функція.** Код: [libs/jane-kit/src/jane_kit/pagination.py:33](../../../../../../libs/jane-kit/src/jane_kit/pagination.py#L33).

```python
def clamp_limit(requested: int | None, limits: PageLimits | None=None) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `requested` | `int \| None` | `—` | positional-or-keyword |
| `limits` | `PageLimits \| None` | `None` | positional-or-keyword |

Результат: `int`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_tracing_pagination.py:36](../../../../../../libs/jane-kit/tests/test_tracing_pagination.py#L36).

```python
assert clamp_limit(None, limits) == 50
```

Контекст і передумови: [libs/jane-kit/tests/test_tracing_pagination.py:37](../../../../../../libs/jane-kit/tests/test_tracing_pagination.py#L37).

```python
assert clamp_limit(1000, limits) == 100
```

## jane_kit.pagination.encode_cursor

**Функція.** Код: [libs/jane-kit/src/jane_kit/pagination.py:40](../../../../../../libs/jane-kit/src/jane_kit/pagination.py#L40).

```python
def encode_cursor(position: Any) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `position` | `Any` | `—` | positional-or-keyword |

Результат: `str`.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_tracing_pagination.py:42](../../../../../../libs/jane-kit/tests/test_tracing_pagination.py#L42).

```python
cursor = encode_cursor({"after": "mat_01", "ts": 3})
```

Контекст і передумови: [services/assistant/tests/test_lists.py:170](../../../../../../services/assistant/tests/test_lists.py#L170).

```python
r = w.client.get(path, params={"cursor": encode_cursor(cursor)})
```

## jane_kit.pagination.decode_cursor

**Функція.** Код: [libs/jane-kit/src/jane_kit/pagination.py:45](../../../../../../libs/jane-kit/src/jane_kit/pagination.py#L45).

```python
def decode_cursor(cursor: str) -> Any:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `cursor` | `str` | `—` | positional-or-keyword |

Результат: `Any`.

Явні `raise` у тілі: `ValidationFailed`. Винятки викликаних залежностей описуються у ручному довіднику.

### Приклади з тестів

Контекст і передумови: [libs/jane-kit/tests/test_tracing_pagination.py:43](../../../../../../libs/jane-kit/tests/test_tracing_pagination.py#L43).

```python
assert decode_cursor(cursor) == {"after": "mat_01", "ts": 3}
```

Контекст і передумови: [libs/jane-kit/tests/test_tracing_pagination.py:45](../../../../../../libs/jane-kit/tests/test_tracing_pagination.py#L45).

```python
decode_cursor("%%%not-base64")
```
