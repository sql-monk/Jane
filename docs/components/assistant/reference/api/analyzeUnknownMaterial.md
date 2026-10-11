# POST /v1/unknown-materials

> Згенеровано `scripts/docs_reference.py` з [assistant.v1.yaml](../../../../../contracts/openapi/assistant.v1.yaml#L416). Не редагуйте вручну.

**Проаналізувати невідомий матеріал (викликає оркестратор лише за увімкненим прапорцем)**

| Властивість | Значення |
|---|---|
| operationId | `analyzeUnknownMaterial` |
| Метод і шлях | `POST /v1/unknown-materials` |
| Scope | `assistant:use` |
| Ідемпотентність | обов'язковий `Idempotency-Key` |
| Теги | unknown |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `Idempotency-Key` | header | `string` | так | Ключ ідемпотентності (1–255 друкованих ASCII-символів; рекомендовано UUID або детермінований ключ доставки). Повтор із тим самим ключем і тим самим тілом повертає збережену відповідь (заголовок `Idempotency-Replayed: true`) без повторного ефекту. Той самий ключ з іншим тілом — 422 `idempotency_key_reused`. Запит ще виконується — 409 `idempotency_in_progress` (retryable). Сервіс пам'ятає ключ щонайменше `limits.transfer.idempotency_ttl_seconds`. |

## Тіло запиту

Тип вмісту `application/json`, схема `UnknownMaterialRequest`; обов'язкове: так.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `source_id` | `string` | так |  |
| `task_id` | `string` | ні |  |
| `forward_unknown_to_llm` | `boolean` | так | Ефективне значення прапорця на момент маршрутизації; false — асистент відмовляє (403). |
| `material` | `material` | так | Матеріал, отриманий колектором (ТЗ §5): вміст (RAW) і метадані. Кожне отримання — нове спостереження з новим observation_id (ТЗ §11); material_id стабільний для того самого об'єкта джерела; revision описує версію вмісту. Повторна технічна доставка того самого спостереження має той самий observation_id і не створює нових записів. |
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
| `limits` | `llm` | ні |  |
| `limits.max_requests_per_minute` | `integer` | ні | мін. `1` |
| `limits.max_input_tokens_per_request` | `integer` | ні | мін. `1` |
| `limits.max_output_tokens_per_request` | `integer` | ні | мін. `1` |
| `limits.budget` | `Budget` | ні | Бюджет витрат LLM на рівні (platform/source/task). Перевищення зупиняє нові виклики з кодом budget_exhausted. Семантика однакова для LLM-шлюзу й асистента: (1) виклик дозволено, лише якщо для кожного застосовного бюджету витрачено &lt; amount і витрачено + зарезервовано + найгірша оцінка вартості виклику ≤ amount; тому amount: 0 означає «LLM вимкнено» для рівня — відхиляється навіть модель із нульовою ціною; (2) витрати рахуються у вікні period: day/week/month — календарний період UTC, total — без скидання, run — окремо для кожного scope.run_id запиту LLM-шлюзу (асистент передає ідентифікатор свого запуску: сесії підключення чи job), а без run_id вікном є сам запит з усіма його повторами; бюджет ніколи не пропускається; (3) бюджет у limits запиту стосується найконкретнішого рівня запиту (task, якщо є task_id, інакше source, інакше platform) і лише звужує: збережені бюджети рівнів діють і далі; з тим самим period і currency лічильник спільний і діє менша сума, інакше перевіряються обидва. |
| `limits.budget.amount` | `number` | так | мін. `0` |
| `limits.budget.currency` | `string` | так | шаблон `"^[A-Z]{3}$"` |
| `limits.budget.period` | enum: `run`, `day`, `week`, `month`, `total` | так |  |
| `limits.max_improvement_attempts` | `integer` | ні | Скільки спроб вдосконалення екстрактора на одну групу проблем.; мін. `0` |
| `limits.max_onboarding_samples` | `integer` | ні | Верхня межа вибірки під час дослідження джерела (фактична кількість адаптивна).; мін. `1` |
| `limits.min_onboarding_confidence` | `number` | ні | Поріг достатньої впевненості вибірки під час дослідження джерела (ТЗ §8): асистент вибирає матеріали, доки оцінка впевненості не досягне порога; не досягнуто в межах бюджету й max_onboarding_samples — сесія insufficient_sample. Вищий поріг — більша вибірка й витрати, тому hard_caps обмежують його зверху. Типово 0.8.; макс. `1` |

Приклад `unknown`:

```json
{
  "source_id": "shop-example",
  "task_id": "shop-catalog",
  "forward_unknown_to_llm": true,
  "material": {
    "material_id": "web:0a1b2c3d4e5f60718293a4b5c6d7e8f9",
    "observation_id": "obs_01J9ZQ5A0000000000000007",
    "source": {
      "source_id": "shop-example",
      "kind": "web"
    },
    "locator": {
      "url": "https://shop.example.test/gift-cards"
    },
    "fetched_at": "2026-09-27T10:05:00Z",
    "format": {
      "media_type": "text/html"
    },
    "revision": {
      "content_sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    },
    "content": {
      "kind": "inline",
      "media_type": "text/html",
      "encoding": "utf-8",
      "data": "<html><h1>Gift cards</h1></html>"
    },
    "collector": {
      "name": "web-collector",
      "version": "0.1.0"
    }
  }
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `202` | Операцію прийнято до асинхронного виконання. | `job` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `403` | forward_unknown_to_llm не увімкнено — асистент не викликає LLM (`access_denied_by_policy`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |
| `429` | Перевищено частоту (`rate_limited`) або бюджет (`budget_exhausted`). | `problem` |

### Відповідь 202

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `job_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `kind` | `string` | так | Вид операції в межах сервісу, наприклад 'collection', 'invocation', 'test_run', 'run', 'onboarding', 'improvement', 'upstream_port'.; шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `status` | enum: `queued`, `running`, `cancelling`, `succeeded`, `failed`, `cancelled` | так |  |
| `created_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `updated_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `started_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `finished_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `progress` | `JobProgress` | ні |  |
| `progress.completed` | `integer` | ні | мін. `0` |
| `progress.total` | `integer \| null` | ні | Відома загальна кількість одиниць; null — невідома (наприклад під час рекурсивного обходу).; мін. `0` |
| `progress.unit` | `string` | ні |  |
| `progress.message` | `string` | ні |  |
| `progress.counters` | `object` | ні | Довільні лічильники, наприклад {"fetched": 10, "skipped_robots": 2}. |
| `progress.updated_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `result` | `object` | ні | Результат, коли status = succeeded. Форма залежить від 'kind' і описана в API відповідної операції. Великий результат передається як result_ref. |
| `result_ref` | `InlineContent` \| `BlobContent` | ні | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `error` | `problem` | ні | Причина, коли status = failed. Для cancelled причина — у cancellation. |
| `error.type` | `string` (uri-reference) | так | URI типу проблеми: 'urn:jane:problem:&lt;code>'. |
| `error.title` | `string` | так | Короткий людський опис типу проблеми. |
| `error.status` | `integer` | так | мін. `400`; макс. `599` |
| `error.detail` | `string` | ні | Пояснення конкретного випадку. Без секретів і без вмісту матеріалів. |
| `error.instance` | `string` (uri-reference) | ні |  |
| `error.code` | `string` | так | Стабільний машинний код у snake_case. Відомі коди — $defs/KnownErrorCode. Сервіс може додати власний код лише разом з оновленням каталогу в contracts/.; шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `error.retryable` | `boolean` | ні | true — ту саму операцію (з тим самим Idempotency-Key) можна безпечно повторити пізніше. |
| `error.retry_after_seconds` | `integer` | ні | Дублює заголовок Retry-After для клієнтів, які читають лише тіло.; мін. `0` |
| `error.errors` | array of `FieldError` | ні | Помилки окремих полів або параметрів (для validation_failed). |
| `error.errors[].pointer` | `string` | ні | JSON Pointer (RFC 6901) до поля тіла запиту, наприклад '/stages/2/handler/version'. |
| `error.errors[].parameter` | `string` | ні | Ім'я query/path/header параметра. |
| `error.errors[].code` | `string` | ні | шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `error.errors[].message` | `string` | так |  |
| `error.trace_id` | `string` | ні |  |
| `error.details` | `object` | ні | Додаткові структуровані дані, специфічні для коду (наприклад 'limit', 'actual' для limit_exceeded). |
| `cancellation` | `JobCancellation` | ні |  |
| `cancellation.requested_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `cancellation.requested_by` | `string` | ні |  |
| `cancellation.reason` | `string` | ні | макс. довжина `1000` |
| `idempotency_key` | `string` | ні | макс. довжина `255` |
| `links` | `object` | ні | Пов'язані ресурси: self, cancel, result, run, collection тощо. |
| `labels` | `Labels` | ні | Довільні мітки ключ-значення для фільтрації й пошуку. Не для секретів. |

Приклад `queued`:

```json
{
  "job_id": "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
  "kind": "collection",
  "status": "queued",
  "created_at": "2026-09-27T10:00:00Z",
  "links": {
    "self": "/v1/jobs/job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
    "cancel": "/v1/jobs/job_01J9ZQ3F8W2N4K7T5B6C1D0E9F/cancel"
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `403`, `422`, `429`.
- Операція асинхронна: `202` повертає job; стан, прогрес і результат — через `GET /v1/jobs/{job_id}`.
