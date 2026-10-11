# jane_web_collector.materials

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_web_collector.materials.MaterialTooLarge](#jane_web_collectormaterialsmaterialtoolarge)
- [jane_web_collector.materials.rfc3339](#jane_web_collectormaterialsrfc3339)
- [jane_web_collector.materials.new_observation_id](#jane_web_collectormaterialsnew_observation_id)
- [jane_web_collector.materials.content_kind](#jane_web_collectormaterialscontent_kind)
- [jane_web_collector.materials.TransitStore](#jane_web_collectormaterialstransitstore)
- [jane_web_collector.materials.TransitStore.__init__](#jane_web_collectormaterialstransitstore__init__)
- [jane_web_collector.materials.build_material](#jane_web_collectormaterialsbuild_material)
- [jane_web_collector.materials.build_item_material](#jane_web_collectormaterialsbuild_item_material)

## jane_web_collector.materials.MaterialTooLarge

**Змінна.** Код: [services/web-collector/src/jane_web_collector/materials.py:46](../../../../../../services/web-collector/src/jane_web_collector/materials.py#L46).

```python
MaterialTooLarge = ContentTooLarge
```

### Опис із вихідного коду

```text
Content above ``transfer.inline_max_bytes`` and no blob store configured (``limit_exceeded``).
```

## jane_web_collector.materials.rfc3339

**Функція.** Код: [services/web-collector/src/jane_web_collector/materials.py:50](../../../../../../services/web-collector/src/jane_web_collector/materials.py#L50).

```python
def rfc3339(dt: datetime) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `dt` | `datetime` | `—` | positional-or-keyword |

Результат: `str`.

## jane_web_collector.materials.new_observation_id

**Функція.** Код: [services/web-collector/src/jane_web_collector/materials.py:58](../../../../../../services/web-collector/src/jane_web_collector/materials.py#L58).

```python
def new_observation_id() -> str:
```

Результат: `str`.

### Опис із вихідного коду

```text
``obs_`` + 12 hex of epoch ms + 4 hex counter + 8 hex random: sortable, monotonic within a process.
```

## jane_web_collector.materials.content_kind

**Функція.** Код: [services/web-collector/src/jane_web_collector/materials.py:77](../../../../../../services/web-collector/src/jane_web_collector/materials.py#L77).

```python
def content_kind(media_type: str, url: str) -> str:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `media_type` | `str` | `—` | positional-or-keyword |
| `url` | `str` | `—` | positional-or-keyword |

Результат: `str`.

## jane_web_collector.materials.TransitStore

**Клас.** Код: [services/web-collector/src/jane_web_collector/materials.py:92](../../../../../../services/web-collector/src/jane_web_collector/materials.py#L92).

```python
class TransitStore(FileTransitStore):
```

Базові типи / інтерфейси: `FileTransitStore`.

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [__init__](jane_web_collector.materials.md#jane_web_collectormaterialstransitstore__init__) | Конструктор | ні |
| [root](../../../../jane-kit/reference/types/generated/jane_kit.content.md#jane_kitcontentfiletransitstoreroot) | Поле екземпляра | так |
| [producer](../../../../jane-kit/reference/types/generated/jane_kit.content.md#jane_kitcontentfiletransitstoreproducer) | Поле екземпляра | так |
| [base](../../../../jane-kit/reference/types/generated/jane_kit.content.md#jane_kitcontentfiletransitstorebase) | Властивість | так |
| [put](../../../../jane-kit/reference/types/generated/jane_kit.content.md#jane_kitcontentfiletransitstoreput) | Метод | так |
| [cleanup](../../../../jane-kit/reference/types/generated/jane_kit.content.md#jane_kitcontentfiletransitstorecleanup) | Метод | так |

### Опис із вихідного коду

```text
Transit blobs of this collector (``<root>/web-collector/...``, ``file://`` URIs) - jane-kit's shared writer and
cleaner (R18, ADR-0004).
```

## jane_web_collector.materials.TransitStore.__init__

**Конструктор.** Код: [services/web-collector/src/jane_web_collector/materials.py:96](../../../../../../services/web-collector/src/jane_web_collector/materials.py#L96).

```python
def __init__(self, root: Path) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `root` | `Path` | `—` | positional-or-keyword |

Результат: `None`.

## jane_web_collector.materials.build_material

**Функція.** Код: [services/web-collector/src/jane_web_collector/materials.py:116](../../../../../../services/web-collector/src/jane_web_collector/materials.py#L116).

```python
def build_material(result: HttpResult, *, canonical_url: str, observation_id: str, source_id: str | None, delivery: Delivery, collector_version: str, collection_id: str | None=None, rules_ref: Mapping[str, Any] | None=None, discovery: Mapping[str, Any] | None=None, html_meta: Mapping[str, str] | None=None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `result` | `HttpResult` | `—` | positional-or-keyword |
| `canonical_url` | `str` | `—` | keyword-only |
| `observation_id` | `str` | `—` | keyword-only |
| `source_id` | `str \| None` | `—` | keyword-only |
| `delivery` | `Delivery` | `—` | keyword-only |
| `collector_version` | `str` | `—` | keyword-only |
| `collection_id` | `str \| None` | `None` | keyword-only |
| `rules_ref` | `Mapping[str, Any] \| None` | `None` | keyword-only |
| `discovery` | `Mapping[str, Any] \| None` | `None` | keyword-only |
| `html_meta` | `Mapping[str, str] \| None` | `None` | keyword-only |

Результат: `dict[str, Any]`.

## jane_web_collector.materials.build_item_material

**Функція.** Код: [services/web-collector/src/jane_web_collector/materials.py:182](../../../../../../services/web-collector/src/jane_web_collector/materials.py#L182).

```python
def build_item_material(body: bytes, *, media_type: str, url: str, canonical_url: str, fetched_at: datetime, observation_id: str, source_id: str | None, delivery: Delivery, collector_version: str, collection_id: str | None=None, rules_ref: Mapping[str, Any] | None=None, discovery: Mapping[str, Any] | None=None, edited_at: datetime | None=None) -> dict[str, Any]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `body` | `bytes` | `—` | positional-or-keyword |
| `media_type` | `str` | `—` | keyword-only |
| `url` | `str` | `—` | keyword-only |
| `canonical_url` | `str` | `—` | keyword-only |
| `fetched_at` | `datetime` | `—` | keyword-only |
| `observation_id` | `str` | `—` | keyword-only |
| `source_id` | `str \| None` | `—` | keyword-only |
| `delivery` | `Delivery` | `—` | keyword-only |
| `collector_version` | `str` | `—` | keyword-only |
| `collection_id` | `str \| None` | `None` | keyword-only |
| `rules_ref` | `Mapping[str, Any] \| None` | `None` | keyword-only |
| `discovery` | `Mapping[str, Any] \| None` | `None` | keyword-only |
| `edited_at` | `datetime \| None` | `None` | keyword-only |

Результат: `dict[str, Any]`.

### Опис із вихідного коду

```text
Material of content a strategy already has (``api_feed`` JSON item, ``DiscoveryContext.emit_material``).

The same document as for a fetched page, except that nothing was fetched at ``url``: no ``http`` and no
``locator.final_url``; ``fetched_at`` is when the API page with the item was fetched (its URL is
``discovery.parent_url``); ``edited_at`` is the item's ``lastmod``, if the strategy has one.
```
