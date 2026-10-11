# GET /v1/collections/{collection_id}/materials

> Згенеровано `scripts/docs_reference.py` з [collector.v1.yaml](../../../../contracts/openapi/collector.v1.yaml#L318). Не редагуйте вручну.

**Забрати матеріали після курсора (і підтвердити попередні)**

| Властивість | Значення |
|---|---|
| operationId | `listCollectionMaterials` |
| Метод і шлях | `GET /v1/collections/{collection_id}/materials` |
| Scope | `collector:read` |
| Ідемпотентність | — |
| Теги | collections |

`after` — курсор останнього обробленого матеріалу; усі матеріали до нього включно вважаються підтвердженими й більше не видаються. Без `after` — від першого непідтвердженого. `wait_ms` — long-poll: чекати нові матеріали до вказаного часу. `end_of_stream: true` — збір завершено й усі матеріали видано.

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `collection_id` | path | `string` | так | Дорівнює job_id, повернутому POST /v1/collections. |
| `after` | query | `string` | ні |  |
| `limit` | query | `integer` | ні | Розмір сторінки. Значення понад максимум сервісу обрізається до максимуму. |
| `wait_ms` | query | `integer` | ні | Long-poll до цього часу (обрізається до максимуму сервісу). |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Сторінка матеріалів. | `MaterialPage` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `410` | Збір видалено після `job_retention_seconds`. | `problem` |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `items` | array of `material` | так |  |
| `items[].material_id` | `string` | так | Стабільний ідентифікатор об'єкта в джерелі. Web: 'web:' + sha256(канонічний URL)[:32]; Telegram: 'tg:&lt;channel_id>:&lt;message_id>'. Однаковий для всіх спостережень того самого об'єкта.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `items[].observation_id` | `string` | так | Унікальний ідентифікатор цього отримання (ULID/UUIDv7 — монотонний у межах колектора).; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `items[].source` | `object` | так |  |
| `items[].source.source_id` | `string` | ні | Ідентифікатор джерела в оркестраторі; в автономному режимі може бути відсутній.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `items[].source.kind` | `string` | так | Тип джерела. Розширюється додаванням нових значень (клієнти мають терпіти невідомі значення).; шаблон `"^[a-z][a-z0-9_-]{1,31}$"` |
| `items[].source.name` | `string` | ні |  |
| `items[].locator` | `object` | так | Посилання на першоджерело. |
| `items[].locator.url` | `string` (uri) | ні | Запитаний URL. |
| `items[].locator.final_url` | `string` (uri) | ні | URL після переадресацій. |
| `items[].locator.canonical_url` | `string` (uri) | ні | Нормалізований URL, від якого обчислено material_id (web). |
| `items[].locator.telegram` | `object` | ні |  |
| `items[].fetched_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `items[].published_at` | `string` (date-time) | ні | Час публікації, якщо його надає джерело. |
| `items[].edited_at` | `string` (date-time) | ні | Час редагування, якщо його надає джерело. |
| `items[].format` | `object` | так |  |
| `items[].format.media_type` | `string` | так | Медіатип RFC 6838, наприклад 'text/html' або 'application/json'. Параметри (charset) передаються окремо.; шаблон `"^[a-z0-9!#$&^_.+-]+/[a-z0-9!#$&^_.+-]+$"` |
| `items[].format.charset` | `string` | ні |  |
| `items[].format.language` | `string` | ні | BCP 47, якщо відомо. |
| `items[].format.content_kind` | `string` | ні | Грубий вид вмісту для маршрутизації: page (HTML-сторінка), feed, sitemap, json, message (Telegram), file. |
| `items[].revision` | `object` | так | Версія вмісту. Однаковий content_sha256 у двох спостереженнях означає незмінений вміст. |
| `items[].revision.content_sha256` | `string` | так | шаблон `"^[a-f0-9]{64}$"` |
| `items[].revision.source_revision` | `string` | ні | Версія, яку надає джерело: ETag, Last-Modified, Telegram edit_date (або date неред. повідомлення) в epoch seconds. |
| `items[].revision.sequence` | `integer` | ні | Строго монотонний номер ревізії того самого material_id для порядку спостережень, якщо джерело дає основу для нього; кожна нова ревізія має більший sequence. Telegram: edit_date (або date неред. повідомлення) в epoch seconds × 1000 + порядковий номер ревізії з іншим текстом, яку колектор побачив у межах тієї самої секунди (0 — перша), тож кілька редагувань за секунду мають різні зростаючі значення (до 1.1 — просто epoch seconds; значення нового формату завжди більші за старі). Одноразовий POST /v1/fetches бере номер із ревізій, які колектор уже видав (у будь-якому state_key), і нічого не записує; строгу монотонність гарантують збори одного state_key. Web: відсутній.; мін. `0` |
| `items[].revision.is_edit` | `boolean` | ні | Джерело позначило матеріал як відредагований (Telegram edit). |
| `items[].content` | `InlineContent` \| `BlobContent` | так | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `items[].attachments` | array of `object` | ні | Додаткові файли (медіа Telegram, PDF за посиланням), кожен як ContentRef з описом. |
| `items[].attachments[].name` | `string` | так |  |
| `items[].attachments[].role` | `string` | ні |  |
| `items[].attachments[].content` | `InlineContent` \| `BlobContent` | так | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `items[].http` | `object` | ні |  |
| `items[].http.status` | `integer` | ні | мін. `100`; макс. `599` |
| `items[].http.headers` | `object` | ні | Підмножина заголовків відповіді (content-type, etag, last-modified, cache-control). Без Set-Cookie та інших чутливих. |
| `items[].http.redirects` | array of `string` (uri) | ні |  |
| `items[].discovery` | `object` | ні | Як матеріал було знайдено. |
| `items[].discovery.strategy` | `string` | ні |  |
| `items[].discovery.parent_url` | `string` (uri) | ні |  |
| `items[].discovery.depth` | `integer` | ні | мін. `0` |
| `items[].discovery.section` | `string` | ні | Ідентифікатор розділу з правил колектора (sections[].section_id), якщо URL йому відповідає. |
| `items[].discovery.priority` | `integer` | ні |  |
| `items[].collector` | `object` | так |  |
| `items[].collector.name` | `string` | так |  |
| `items[].collector.version` | `string` | так |  |
| `items[].collector.rules` | `package-ref` | ні | Версія правил колектора, за якими отримано матеріал. |
| `items[].collector.collection_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `items[].diagnostics` | array of `DiagnosticMessage` | ні |  |
| `items[].diagnostics[].level` | enum: `debug`, `info`, `warning`, `error` | так |  |
| `items[].diagnostics[].code` | `string` | ні | шаблон `"^[a-z][a-z0-9_.-]{0,127}$"` |
| `items[].diagnostics[].message` | `string` | так | макс. довжина `4000` |
| `items[].diagnostics[].pointer` | `string` | ні | JSON Pointer у вихідних даних (наприклад '/entities/3/fields/price'). |
| `items[].diagnostics[].material_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `items[].diagnostics[].selector` | `string` | ні | CSS/XPath/JSONPath, з яким пов'язано повідомлення (для екстракторів). |
| `items[].metadata` | `object` | ні | Додаткові метадані джерела (наприклад title, автор повідомлення, кількість переглядів). Відкритий об'єкт. Telegram: service_action — дія службового повідомлення каналу (channel_create, pin_message, chat_edit_title…); таке повідомлення зазвичай має порожній текст, тож завдання може відфільтрувати його умовою material.metadata.service_action not_exists. |
| `next_cursor` | `string \| null` | так | Курсор останнього елемента сторінки; передайте як after у наступному запиті.; макс. довжина `2048` |
| `end_of_stream` | `boolean` | так |  |
| `collection_status` | enum: `queued`, `running`, `cancelling`, `succeeded`, `failed`, `cancelled` | так |  |

Приклад `page`:

```json
{
  "items": [
    {
      "material_id": "web:9b1f0c1d2e3f40516273849a0b1c2d3e",
      "observation_id": "obs_01J9ZQ4A0000000000000001",
      "source": {
        "source_id": "shop-example",
        "kind": "web"
      },
      "locator": {
        "url": "https://shop.example.test/product/a-100",
        "canonical_url": "https://shop.example.test/product/a-100"
      },
      "fetched_at": "2026-09-27T10:00:05Z",
      "format": {
        "media_type": "text/html",
        "charset": "utf-8",
        "content_kind": "page"
      },
      "revision": {
        "content_sha256": "5d41402abc4b2a76b9719d911017c592ae2f1a7d9e6a3b8c4f5e6d7c8b9a0f1e"
      },
      "content": {
        "kind": "blob",
        "uri": "s3://jane-transit/web-collector/2026/09/27/obs_01J9ZQ4A0000000000000001.html",
        "media_type": "text/html",
        "size_bytes": 482113,
        "sha256": "5d41402abc4b2a76b9719d911017c592ae2f1a7d9e6a3b8c4f5e6d7c8b9a0f1e",
        "store": "transit",
        "expires_at": "2026-10-04T10:00:05Z"
      },
      "discovery": {
        "strategy": "sitemap",
        "depth": 0,
        "section": "products"
      },
      "collector": {
        "name": "web-collector",
        "version": "0.1.0"
      }
    }
  ],
  "next_cursor": "c_0000000000000599",
  "end_of_stream": false,
  "collection_status": "running"
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../contracts/docs/errors.md)): `401`, `404`, `410`, `503`.
