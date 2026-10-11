# Модуль `jane_web_collector.materials`

> Згенеровано `scripts/docs_reference.py` з [services/web-collector/src/jane_web_collector/materials.py](../../../../../services/web-collector/src/jane_web_collector/materials.py). Не редагуйте вручну.

Material documents (``material.schema.json``) and content delivery (inline / transit blob, ADR-0004).

Writing the ``ContentRef`` (inline or a transit blob with ``expires_at``) and the transit cleaner are jane-kit's shared :mod:`jane_kit.content` (R18); this module builds the Material around it.

## Зміст

- [Клас `TransitStore`](#клас-transitstore)
- [Функція `build_item_material`](#функція-build_item_material)
- [Функція `build_material`](#функція-build_material)
- [Функція `content_kind`](#функція-content_kind)
- [Функція `new_observation_id`](#функція-new_observation_id)
- [Функція `rfc3339`](#функція-rfc3339)

## Класи

### Клас `TransitStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_web_collector.materials` |
| Успадкування | `FileTransitStore` |
| Код | [materials.py:92](../../../../../services/web-collector/src/jane_web_collector/materials.py#L92) |

```python
class TransitStore(FileTransitStore): ...
```

Transit blobs of this collector (``<root>/web-collector/...``, ``file://`` URIs) - jane-kit's shared writer and cleaner (R18, ADR-0004).

#### Конструктор `TransitStore.__init__`

```python
def __init__(self, root: Path) -> None: ...
```

Код: [materials.py:96](../../../../../services/web-collector/src/jane_web_collector/materials.py#L96).

## Функції

### Функція `build_item_material`

```python
def build_item_material(
    body: bytes,
    *,
    media_type: str,
    url: str,
    canonical_url: str,
    fetched_at: datetime,
    observation_id: str,
    source_id: str | None,
    delivery: Delivery,
    collector_version: str,
    collection_id: str | None = None,
    rules_ref: Mapping[str, Any] | None = None,
    discovery: Mapping[str, Any] | None = None,
    edited_at: datetime | None = None,
) -> dict[str, Any]: ...
```

Material of content a strategy already has (``api_feed`` JSON item, ``DiscoveryContext.emit_material``).

The same document as for a fetched page, except that nothing was fetched at ``url``: no ``http`` and no ``locator.final_url``; ``fetched_at`` is when the API page with the item was fetched (its URL is ``discovery.parent_url``); ``edited_at`` is the item's ``lastmod``, if the strategy has one.

Код: [materials.py:182](../../../../../services/web-collector/src/jane_web_collector/materials.py#L182).

### Функція `build_material`

```python
def build_material(
    result: HttpResult,
    *,
    canonical_url: str,
    observation_id: str,
    source_id: str | None,
    delivery: Delivery,
    collector_version: str,
    collection_id: str | None = None,
    rules_ref: Mapping[str, Any] | None = None,
    discovery: Mapping[str, Any] | None = None,
    html_meta: Mapping[str, str] | None = None,
) -> dict[str, Any]: ...
```

Код: [materials.py:116](../../../../../services/web-collector/src/jane_web_collector/materials.py#L116).

### Функція `content_kind`

```python
def content_kind(media_type: str, url: str) -> str: ...
```

Код: [materials.py:77](../../../../../services/web-collector/src/jane_web_collector/materials.py#L77).

### Функція `new_observation_id`

```python
def new_observation_id() -> str: ...
```

``obs_`` + 12 hex of epoch ms + 4 hex counter + 8 hex random: sortable, monotonic within a process.

Код: [materials.py:58](../../../../../services/web-collector/src/jane_web_collector/materials.py#L58).

### Функція `rfc3339`

```python
def rfc3339(dt: datetime) -> str: ...
```

Код: [materials.py:50](../../../../../services/web-collector/src/jane_web_collector/materials.py#L50).

## Константи й змінні модуля

| Назва | Тип | Значення | Опис |
|---|---|---|---|
| `MaterialTooLarge` | — | `ContentTooLarge` | Content above ``transfer.inline_max_bytes`` and no blob store configured (``limit_exceeded``). |
