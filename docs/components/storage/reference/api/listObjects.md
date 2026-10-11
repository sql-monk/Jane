# GET /v1/objects

> Згенеровано `scripts/docs_reference.py` з [storage.v1.yaml](../../../../../contracts/openapi/storage.v1.yaml#L604). Не редагуйте вручну.

**Збережені об'єкти (RAW, документи результатів) — для перегляду й повторної обробки**

| Властивість | Значення |
|---|---|
| operationId | `listObjects` |
| Метод і шлях | `GET /v1/objects` |
| Scope | `storage:read` |
| Ідемпотентність | — |
| Теги | objects |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `connection_id` | query | `string` | так |  |
| `source_id` | query | `string` | ні |  |
| `material_id` | query | `string` | ні | Об'єкти одного матеріалу. Разом із `material_ids` значення об'єднуються. |
| `material_ids` | query | array of `string` | ні | Об'єкти будь-якого з кількох матеріалів (повторюваний параметр: `material_ids=a&material_ids=b`); значення об'єднуються з `material_id`. Інші фільтри діють для кожного значення. Порядок — за `material_id`, далі в порядку адаптера; `next_cursor` чинний лише для того самого запиту (інакше 422). Кількість значень обмежує конфігурація сервісу (storage: `objects.max_filter_material_ids`), більше — 422 `limit_exceeded`. |
| `since` | query | `string` (date-time) | ні |  |
| `until` | query | `string` (date-time) | ні |  |
| `cursor` | query | `string` | ні | Непрозорий курсор з `next_cursor` попередньої сторінки. |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка збережених об'єктів. | `object` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `StoredObject` | так |  |
| `items[].object` | `StoredObjectRef` | так | Посилання на збережений об'єкт (RAW або документ результатів), за яким його можна прочитати через storage API або повторно обробити. |
| `items[].object.object_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `items[].object.adapter` | `string` | так |  |
| `items[].object.connection_id` | `string` | ні | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `items[].object.locator` | `object` | ні | Адреса в термінах адаптера: path (files), table+id (SQL), collection+_id (MongoDB), bucket+key (S3/MinIO). |
| `items[].object.media_type` | `string` | ні | Медіатип RFC 6838, наприклад 'text/html' або 'application/json'. Параметри (charset) передаються окремо.; шаблон `"^[a-z0-9!#$&^_.+-]+/[a-z0-9!#$&^_.+-]+$"` |
| `items[].object.size_bytes` | `integer` | ні | мін. `0` |
| `items[].object.sha256` | `string` | ні | шаблон `"^[a-f0-9]{64}$"` |
| `items[].object.content` | `InlineContent` \| `BlobContent` | ні | Постійне посилання на вміст (store=persistent), якщо адаптер його надає. |
| `items[].material` | `object` | ні | Короткі метадані матеріалу, з якого збережено об'єкт. |
| `items[].material.material_id` | `string` | ні |  |
| `items[].material.observation_id` | `string` | ні |  |
| `items[].material.source_id` | `string` | ні |  |
| `items[].material.url` | `string` | ні |  |
| `items[].material.fetched_at` | `string` (date-time) | ні |  |
| `items[].stored_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `next_cursor` | `string \| null` | так | макс. довжина `2048` |

Приклад `raw`:

```json
{
  "items": [
    {
      "object": {
        "object_id": "obj_01J9ZQ4C00000000000000D1",
        "adapter": "filesystem",
        "connection_id": "raw-files",
        "locator": {
          "path": "raw/shop-example/2026/09/27/web_9b1f0c1d/obs_01J9ZQ4A0000000000000001.html"
        },
        "media_type": "text/html",
        "size_bytes": 151
      },
      "material": {
        "material_id": "web:9b1f0c1d2e3f40516273849a0b1c2d3e",
        "observation_id": "obs_01J9ZQ4A0000000000000001",
        "source_id": "shop-example",
        "url": "https://shop.example.test/product/a-100",
        "fetched_at": "2026-09-27T10:00:05Z"
      },
      "stored_at": "2026-09-27T10:00:07Z"
    }
  ],
  "next_cursor": null
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`, `422`.
