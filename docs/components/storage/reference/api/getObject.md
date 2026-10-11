# GET /v1/objects/{object_id}

> Згенеровано `scripts/docs_reference.py` з [storage.v1.yaml](../../../../../contracts/openapi/storage.v1.yaml#L265). Не редагуйте вручну.

**Метадані збереженого об'єкта і відновлений Material для повторної обробки**

| Властивість | Значення |
|---|---|
| operationId | `getObject` |
| Метод і шлях | `GET /v1/objects/{object_id}` |
| Scope | `storage:read` |
| Ідемпотентність | — |
| Теги | objects |

Для RAW — відновлений Material для повторної обробки. Вміст залежить від формату збереження (`format.raw` пакета, `contracts/docs/storage-adapter.md`, «Формати RAW»): `html` / `original` — постійне посилання адаптера на ті самі байти (`file://` чи `s3://`, `store: persistent`) або inline до `limits.transfer.inline_max_bytes`; `json` (документ Material із вбудованим вмістом) — початковий вміст, вийнятий із документа, inline до `limits.transfer.inline_max_bytes`. Більший за ліміт вміст без постійного посилання (`json`, а також адаптери без blob-URI: PostgreSQL, MongoDB, SQL Server) віддається транзитним blob самого storage (`store: transit`, `expires_at` = зараз + `limits.transfer.transit_ttl_seconds`, ADR-0004 §2), якщо в розгортанні налаштовано його транзитне сховище; без нього `material` відсутній (байти — `getObjectContent`).

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `object_id` | path | `string` | так |  |
| `connection_id` | query | `string` | так |  |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Об'єкт і, для RAW, Material із посиланням на вміст (або inline-вмістом). | `StoredObjectDetail` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `object` | `StoredObjectRef` | так | Посилання на збережений об'єкт (RAW або документ результатів), за яким його можна прочитати через storage API або повторно обробити. |
| `object.object_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `object.adapter` | `string` | так |  |
| `object.connection_id` | `string` | ні | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `object.locator` | `object` | ні | Адреса в термінах адаптера: path (files), table+id (SQL), collection+_id (MongoDB), bucket+key (S3/MinIO). |
| `object.media_type` | `string` | ні | Медіатип RFC 6838, наприклад 'text/html' або 'application/json'. Параметри (charset) передаються окремо.; шаблон `"^[a-z0-9!#$&^_.+-]+/[a-z0-9!#$&^_.+-]+$"` |
| `object.size_bytes` | `integer` | ні | мін. `0` |
| `object.sha256` | `string` | ні | шаблон `"^[a-f0-9]{64}$"` |
| `object.content` | `InlineContent` \| `BlobContent` | ні | Постійне посилання на вміст (store=persistent), якщо адаптер його надає. |
| `stored_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `material` | `material` | ні | Відновлений Material (лише для RAW і лише якщо його вміст можна віддати, див. опис операції). |
| `material.material_id` | `string` | так | Стабільний ідентифікатор об'єкта в джерелі. Web: 'web:' + sha256(канонічний URL)[:32]; Telegram: 'tg:&lt;channel_id>:&lt;message_id>'. Однаковий для всіх спостережень того самого об'єкта.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `material.observation_id` | `string` | так | Унікальний ідентифікатор цього отримання (ULID/UUIDv7 — монотонний у межах колектора).; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `material.source` | `object` | так |  |
| `material.source.source_id` | `string` | ні | Ідентифікатор джерела в оркестраторі; в автономному режимі може бути відсутній.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `material.source.kind` | `string` | так | Тип джерела. Розширюється додаванням нових значень (клієнти мають терпіти невідомі значення).; шаблон `"^[a-z][a-z0-9_-]{1,31}$"` |
| `material.source.name` | `string` | ні |  |
| `material.locator` | `object` | так | Посилання на першоджерело. |
| `material.locator.url` | `string` (uri) | ні | Запитаний URL. |
| `material.locator.final_url` | `string` (uri) | ні | URL після переадресацій. |
| `material.locator.canonical_url` | `string` (uri) | ні | Нормалізований URL, від якого обчислено material_id (web). |
| `material.locator.telegram` | `object` | ні |  |
| `material.fetched_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `material.published_at` | `string` (date-time) | ні | Час публікації, якщо його надає джерело. |
| `material.edited_at` | `string` (date-time) | ні | Час редагування, якщо його надає джерело. |
| `material.format` | `object` | так |  |
| `material.format.media_type` | `string` | так | Медіатип RFC 6838, наприклад 'text/html' або 'application/json'. Параметри (charset) передаються окремо.; шаблон `"^[a-z0-9!#$&^_.+-]+/[a-z0-9!#$&^_.+-]+$"` |
| `material.format.charset` | `string` | ні |  |
| `material.format.language` | `string` | ні | BCP 47, якщо відомо. |
| `material.format.content_kind` | `string` | ні | Грубий вид вмісту для маршрутизації: page (HTML-сторінка), feed, sitemap, json, message (Telegram), file. |
| `material.revision` | `object` | так | Версія вмісту. Однаковий content_sha256 у двох спостереженнях означає незмінений вміст. |
| `material.revision.content_sha256` | `string` | так | шаблон `"^[a-f0-9]{64}$"` |
| `material.revision.source_revision` | `string` | ні | Версія, яку надає джерело: ETag, Last-Modified, Telegram edit_date (або date неред. повідомлення) в epoch seconds. |
| `material.revision.sequence` | `integer` | ні | Строго монотонний номер ревізії того самого material_id для порядку спостережень, якщо джерело дає основу для нього; кожна нова ревізія має більший sequence. Telegram: edit_date (або date неред. повідомлення) в epoch seconds × 1000 + порядковий номер ревізії з іншим текстом, яку колектор побачив у межах тієї самої секунди (0 — перша), тож кілька редагувань за секунду мають різні зростаючі значення (до 1.1 — просто epoch seconds; значення нового формату завжди більші за старі). Одноразовий POST /v1/fetches бере номер із ревізій, які колектор уже видав (у будь-якому state_key), і нічого не записує; строгу монотонність гарантують збори одного state_key. Web: відсутній.; мін. `0` |
| `material.revision.is_edit` | `boolean` | ні | Джерело позначило матеріал як відредагований (Telegram edit). |
| `material.content` | `InlineContent` \| `BlobContent` | так | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `material.attachments` | array of `object` | ні | Додаткові файли (медіа Telegram, PDF за посиланням), кожен як ContentRef з описом. |
| `material.attachments[].name` | `string` | так |  |
| `material.attachments[].role` | `string` | ні |  |
| `material.attachments[].content` | `InlineContent` \| `BlobContent` | так | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `material.http` | `object` | ні |  |
| `material.http.status` | `integer` | ні | мін. `100`; макс. `599` |
| `material.http.headers` | `object` | ні | Підмножина заголовків відповіді (content-type, etag, last-modified, cache-control). Без Set-Cookie та інших чутливих. |
| `material.http.redirects` | array of `string` (uri) | ні |  |
| `material.discovery` | `object` | ні | Як матеріал було знайдено. |
| `material.discovery.strategy` | `string` | ні |  |
| `material.discovery.parent_url` | `string` (uri) | ні |  |
| `material.discovery.depth` | `integer` | ні | мін. `0` |
| `material.discovery.section` | `string` | ні | Ідентифікатор розділу з правил колектора (sections[].section_id), якщо URL йому відповідає. |
| `material.discovery.priority` | `integer` | ні |  |
| `material.collector` | `object` | так |  |
| `material.collector.name` | `string` | так |  |
| `material.collector.version` | `string` | так |  |
| `material.collector.rules` | `package-ref` | ні | Версія правил колектора, за якими отримано матеріал. |
| `material.collector.collection_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `material.diagnostics` | array of `DiagnosticMessage` | ні |  |
| `material.diagnostics[].level` | enum: `debug`, `info`, `warning`, `error` | так |  |
| `material.diagnostics[].code` | `string` | ні | шаблон `"^[a-z][a-z0-9_.-]{0,127}$"` |
| `material.diagnostics[].message` | `string` | так | макс. довжина `4000` |
| `material.diagnostics[].pointer` | `string` | ні | JSON Pointer у вихідних даних (наприклад '/entities/3/fields/price'). |
| `material.diagnostics[].material_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `material.diagnostics[].selector` | `string` | ні | CSS/XPath/JSONPath, з яким пов'язано повідомлення (для екстракторів). |
| `material.metadata` | `object` | ні | Додаткові метадані джерела (наприклад title, автор повідомлення, кількість переглядів). Відкритий об'єкт. Telegram: service_action — дія службового повідомлення каналу (channel_create, pin_message, chat_edit_title…); таке повідомлення зазвичай має порожній текст, тож завдання може відфільтрувати його умовою material.metadata.service_action not_exists. |

Приклад `raw`:

```json
{
  "object": {
    "object_id": "obj_01J9ZQ4C00000000000000D1",
    "adapter": "filesystem",
    "connection_id": "raw-files",
    "media_type": "text/html",
    "size_bytes": 151
  },
  "stored_at": "2026-09-27T10:00:07Z",
  "material": {
    "material_id": "web:9b1f0c1d2e3f40516273849a0b1c2d3e",
    "observation_id": "obs_01J9ZQ4A0000000000000001",
    "source": {
      "source_id": "shop-example",
      "kind": "web"
    },
    "locator": {
      "url": "https://shop.example.test/product/a-100"
    },
    "fetched_at": "2026-09-27T10:00:05Z",
    "format": {
      "media_type": "text/html"
    },
    "revision": {
      "content_sha256": "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"
    },
    "content": {
      "kind": "blob",
      "uri": "file:///var/lib/jane/raw/shop-example/2026/09/27/web_9b1f0c1d/obs_01J9ZQ4A0000000000000001.html",
      "media_type": "text/html",
      "size_bytes": 151,
      "sha256": "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae",
      "store": "persistent",
      "expires_at": null
    },
    "collector": {
      "name": "web-collector",
      "version": "0.1.0"
    }
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `404`.
