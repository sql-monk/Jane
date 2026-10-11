# POST /v1/fetches

> Згенеровано `scripts/docs_reference.py` з [collector.v1.yaml](../../../../contracts/openapi/collector.v1.yaml#L58). Не редагуйте вручну.

**Синхронно отримати один матеріал**

| Властивість | Значення |
|---|---|
| operationId | `fetchMaterial` |
| Метод і шлях | `POST /v1/fetches` |
| Scope | `collector:run` |
| Ідемпотентність | не потрібна: read-only for Jane state; every call is a new observation by design |
| Теги | fetch |

Коротка операція: один URL або одне повідомлення. Перевіряє scope й robots, якщо передано правила. Кожен виклик — нове спостереження (новий `observation_id`), тому ключ ідемпотентності не потрібен. Якщо джерело підтвердило, що матеріалу немає (сайт відповів HTTP 404 або 410; повідомлення Telegram не існує чи видалене), — `404 not_found`; інші помилки джерела — `502 source_unavailable`.

## Тіло запиту

Тип вмісту `application/json`, схема `FetchRequest`; обов'язкове: так.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `source_kind` | `string` | так | Тип джерела. Розширюється додаванням нових значень (клієнти мають терпіти невідомі значення).; шаблон `"^[a-z][a-z0-9_-]{1,31}$"` |
| `source_id` | `string` | ні | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `url` | `string` (uri) | ні |  |
| `telegram` | `object` | ні |  |
| `telegram.channel_username` | `string` | ні |  |
| `telegram.channel_id` | `string` | ні |  |
| `telegram.message_id` | `integer` | так |  |
| `rules` | `WebRules` \| `TelegramRules` | ні | Правила колектора (ТЗ §6, §13.1 п.1): версіонуються як пакет kind=collector-rules або передаються колектору inline/з локального файла в автономному режимі. Web: комбінація стратегій пошуку в спільних межах обходу; Telegram: канали, історія, редагування. Числові обмеження — лише через limits (успадкування platform → source → task). |
| `rules_ref` | `package-ref` | ні | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `rules_ref.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `rules_ref.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `rules_ref.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `content_delivery` | enum: `auto`, `inline`, `blob` | ні | auto — inline до limits.transfer.inline_max_bytes, інакше blob.; типово `"auto"` |
| `limits` | `limits` | ні | Модель лімітів з успадкуванням (ТЗ §13.1 п.5, критерій 13). Один і той самий об'єкт Limits задається на рівнях platform → source → task → stage; кожне поле необов'язкове. Ефективне значення: глибоке злиття за рівнями, нижчий рівень перекриває вищий; відсутнє поле успадковується (null заборонено — щоб 'скинути' до успадкованого, поле просто не передають). Після злиття кожне числове поле обмежується platform.hard_caps (min). Під час виконання значення додатково лише звужуються обмеженнями конкретного сайту чи сервісу (robots.txt Crawl-delay, Retry-After, Telegram flood-wait, ліміти провайдера LLM) — вони ніколи не послаблюються конфігурацією. Сервіс, що отримав limits у запиті (автономний режим), застосовує min(ліміти запиту, власні hard_caps). Типові значення — у сервісних конфігураціях і профілях WP-14; довідковий профіль — contracts/examples/schemas/limits/*.json. |
| `limits.concurrency` | `object` | ні |  |
| `limits.concurrency.max_parallel_fetches` | `integer` | ні | Одночасні завантаження одного збору колектора (на збір: кожен збір окремо, на будь-якому екземплярі; спільний для всіх зборів ліміт хоста — max_parallel_fetches_per_host).; мін. `1` |
| `limits.concurrency.max_parallel_fetches_per_host` | `integer` | ні | Одночасні запити до одного хоста джерела (host[:port]) від усієї платформи: усіх зборів і одноразових запитів колектора разом, також усіх його екземплярів, що ділять сховище стану (один вузол, спільний каталог стану). Якщо активні на хості збори мають різні значення, діє найменше. Екземпляри з окремими сховищами стану — окремі колектори й між собою цей ліміт не узгоджують.; мін. `1` |
| `limits.concurrency.max_parallel_invocations` | `integer` | ні | Одночасні виклики обробника (на екземпляр сервісу-виконавця або на етап).; мін. `1` |
| `limits.concurrency.max_parallel_runs_per_task` | `integer` | ні | Скільки запусків одного завдання можуть іти одночасно.; мін. `1` |
| `limits.concurrency.max_parallel_stage_items` | `integer` | ні | Скільки елементів один етап запуску обробляє одночасно.; мін. `1` |
| `limits.rate` | `object` | ні |  |
| `limits.rate.requests_per_second_per_host` | `number` | ні | Частота стартів запитів до одного хоста джерела; область дії — як у concurrency.max_parallel_fetches_per_host (уся платформа: усі збори, одноразові запити й екземпляри зі спільним сховищем стану). Інтервал між стартами = max(1 / requests_per_second_per_host, min_delay_ms_per_host, Crawl-delay за respect_crawl_delay); між активними на хості зборами діє найбільший інтервал. |
| `limits.rate.min_delay_ms_per_host` | `integer` | ні | Мінімальний інтервал між стартами запитів до одного хоста джерела; область дії у Web Collector — як у requests_per_second_per_host. Telegram Collector (єдиний «хост» — API Telegram) застосовує його до викликів API одного збору.; мін. `0` |
| `limits.rate.burst_per_host` | `integer` | ні | мін. `1` |
| `limits.rate.respect_crawl_delay` | `boolean` | ні | Враховувати Crawl-delay з robots.txt (може лише збільшити затримку). |
| `limits.crawl` | `object` | ні |  |
| `limits.crawl.max_depth` | `integer` | ні | мін. `0` |
| `limits.crawl.max_pages_per_run` | `integer` | ні | мін. `1` |
| `limits.crawl.max_bytes_per_run` | `integer` | ні | мін. `1` |
| `limits.crawl.max_material_bytes` | `integer` | ні | Більший матеріал обривається з діагностикою 'truncated' або відкидається (за налаштуванням колектора).; мін. `1` |
| `limits.crawl.max_redirects` | `integer` | ні | мін. `0` |
| `limits.crawl.max_links_per_page` | `integer` | ні | мін. `0` |
| `limits.crawl.max_seed_urls` | `integer` | ні | Максимальна кількість URL у явному переліку (TaskInput.urls, CollectionRequest.urls, seed_list).; мін. `1` |
| `limits.crawl.max_frontier_size` | `integer` | ні | Максимальна кількість URL у черзі обходу.; мін. `1` |
| `limits.crawl.revisit_interval_seconds` | `integer` | ні | Мінімальний інтервал повторного відвідування того самого URL.; мін. `0` |
| `limits.timeouts` | `object` | ні |  |
| `limits.timeouts.connect_timeout_ms` | `integer` | ні | мін. `1` |
| `limits.timeouts.request_timeout_ms` | `integer` | ні | мін. `1` |
| `limits.timeouts.invocation_timeout_ms` | `integer` | ні | Тайм-аут одного виклику обробника (вкл. пісочницю).; мін. `1` |
| `limits.timeouts.stage_timeout_ms` | `integer` | ні | мін. `1` |
| `limits.timeouts.run_timeout_ms` | `integer` | ні | мін. `1` |
| `limits.timeouts.sync_response_max_ms` | `integer` | ні | Якщо синхронна операція не встигає — сервіс повертає 202 + Job.; мін. `1` |
| `limits.retries` | `RetryPolicy` | ні | Повтори застосовуються лише до помилок із retryable=true і лише разом з тим самим ключем ідемпотентності. |
| `limits.retries.max_attempts` | `integer` | ні | Загальна кількість спроб, включно з першою.; мін. `1` |
| `limits.retries.initial_backoff_ms` | `integer` | ні | мін. `0` |
| `limits.retries.max_backoff_ms` | `integer` | ні | мін. `0` |
| `limits.retries.backoff_multiplier` | `number` | ні | мін. `1` |
| `limits.retries.jitter` | `boolean` | ні |  |
| `limits.queue` | `object` | ні |  |
| `limits.queue.max_queue_depth` | `integer` | ні | Максимальна кількість задач у черзі оркестратора для завдання; при переповненні збір пригальмовується (backpressure).; мін. `1` |
| `limits.queue.max_inflight_materials` | `integer` | ні | Скільки матеріалів одного запуску можуть одночасно перебувати в обробці.; мін. `1` |
| `limits.queue.max_unacked_materials` | `integer` | ні | Розмір буфера колектора: скільки отриманих, але ще не забраних споживачем матеріалів він тримає, перш ніж призупинити обхід.; мін. `1` |
| `limits.sandbox` | `object` | ні |  |
| `limits.sandbox.cpu_cores` | `number` | ні |  |
| `limits.sandbox.memory_mb` | `integer` | ні | мін. `16` |
| `limits.sandbox.wall_time_ms` | `integer` | ні | мін. `1` |
| `limits.sandbox.max_output_bytes` | `integer` | ні | мін. `1` |
| `limits.sandbox.max_processes` | `integer` | ні | мін. `1` |
| `limits.sandbox.tmpfs_mb` | `integer` | ні | мін. `0` |
| `limits.llm` | `object` | ні |  |
| `limits.llm.max_requests_per_minute` | `integer` | ні | мін. `1` |
| `limits.llm.max_input_tokens_per_request` | `integer` | ні | мін. `1` |
| `limits.llm.max_output_tokens_per_request` | `integer` | ні | мін. `1` |
| `limits.llm.budget` | `Budget` | ні | Бюджет витрат LLM на рівні (platform/source/task). Перевищення зупиняє нові виклики з кодом budget_exhausted. Семантика однакова для LLM-шлюзу й асистента: (1) виклик дозволено, лише якщо для кожного застосовного бюджету витрачено &lt; amount і витрачено + зарезервовано + найгірша оцінка вартості виклику ≤ amount; тому amount: 0 означає «LLM вимкнено» для рівня — відхиляється навіть модель із нульовою ціною; (2) витрати рахуються у вікні period: day/week/month — календарний період UTC, total — без скидання, run — окремо для кожного scope.run_id запиту LLM-шлюзу (асистент передає ідентифікатор свого запуску: сесії підключення чи job), а без run_id вікном є сам запит з усіма його повторами; бюджет ніколи не пропускається; (3) бюджет у limits запиту стосується найконкретнішого рівня запиту (task, якщо є task_id, інакше source, інакше platform) і лише звужує: збережені бюджети рівнів діють і далі; з тим самим period і currency лічильник спільний і діє менша сума, інакше перевіряються обидва. |
| `limits.llm.max_improvement_attempts` | `integer` | ні | Скільки спроб вдосконалення екстрактора на одну групу проблем.; мін. `0` |
| `limits.llm.max_onboarding_samples` | `integer` | ні | Верхня межа вибірки під час дослідження джерела (фактична кількість адаптивна).; мін. `1` |
| `limits.llm.min_onboarding_confidence` | `number` | ні | Поріг достатньої впевненості вибірки під час дослідження джерела (ТЗ §8): асистент вибирає матеріали, доки оцінка впевненості не досягне порога; не досягнуто в межах бюджету й max_onboarding_samples — сесія insufficient_sample. Вищий поріг — більша вибірка й витрати, тому hard_caps обмежують його зверху. Типово 0.8.; макс. `1` |
| `limits.transfer` | `object` | ні |  |
| `limits.transfer.inline_max_bytes` | `integer` | ні | Вміст до цього розміру можна передавати inline; більший — лише blob.; мін. `0` |
| `limits.transfer.max_request_body_bytes` | `integer` | ні | мін. `1` |
| `limits.transfer.transit_ttl_seconds` | `integer` | ні | Час життя транзитних blob-об'єктів.; мін. `60` |
| `limits.transfer.download_url_ttl_seconds` | `integer` | ні | мін. `1` |
| `limits.transfer.job_retention_seconds` | `integer` | ні | мін. `60` |
| `limits.transfer.idempotency_ttl_seconds` | `integer` | ні | Скільки сервіс пам'ятає Idempotency-Key для повтору відповіді.; мін. `60` |
| `limits.telegram` | `object` | ні |  |
| `limits.telegram.max_messages_per_run` | `integer` | ні | мін. `1` |
| `limits.telegram.max_media_bytes` | `integer` | ні | мін. `0` |
| `limits.telegram.max_flood_wait_seconds` | `integer` | ні | Якщо Telegram вимагає чекати довше — збір призупиняється з помилкою rate_limited замість блокування воркера.; мін. `0` |

Приклад `web`:

```json
{
  "source_kind": "web",
  "source_id": "shop-example",
  "url": "https://shop.example.test/product/a-100",
  "rules_ref": {
    "package_id": "shop-example.web-rules",
    "version": "1.0.0"
  },
  "content_delivery": "auto"
}
```

Приклад `telegram`:

```json
{
  "source_kind": "telegram",
  "telegram": {
    "channel_username": "city_events_example",
    "message_id": 4521
  }
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Матеріал із метаданими. | `material` |
| `400` | Некоректний синтаксис запиту (`bad_request`). | `problem` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `403` | Заборонено robots.txt або політикою доступу (`access_denied_by_policy`). | `problem` |
| `404` | Джерело підтвердило, що матеріалу немає (`not_found`, `retryable: false`): web — сайт відповів HTTP 404 або 410 (`details.http_status`); Telegram — повідомлення не існує або видалене (`details.reason: message_not_found`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |
| `429` | Перевищено частоту (`rate_limited`) або бюджет (`budget_exhausted`). | `problem` |
| `502` | Джерело недоступне або повернуло помилку (`source_unavailable`). Web: `details.http_status` — статус відповіді сайту (крім 404/410, див. 404) або останньої спроби після повторів. Telegram: `details.reason` — `channel_unavailable` (канал не знайдено, приватний чи без доступу) або `account_unauthorized` (сесію відхилено); для них `retryable: false`, бо повтор нічого не змінить. | `problem` |
| `500` | Непередбачена помилка сервісу (`internal_error`, retryable). | `problem` |
| `501` | Правила просять `fetch.render_js`, але в цьому колекторі немає headless-браузера (рендеринг вимкнено, Playwright чи Chromium не встановлено або браузер не стартує; `not_implemented`, `retryable: false`). Причина — у `detail`; те саме видно в `GET /v1/info` → `capabilities.render_js`. | `problem` |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | `problem` |
| `504` | `fetch.render_js`: DOM сторінки не вдалося отримати з браузера за `collector.render_timeout_ms` (`timeout`, `retryable: true`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `material_id` | `string` | так | Стабільний ідентифікатор об'єкта в джерелі. Web: 'web:' + sha256(канонічний URL)[:32]; Telegram: 'tg:&lt;channel_id>:&lt;message_id>'. Однаковий для всіх спостережень того самого об'єкта.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `observation_id` | `string` | так | Унікальний ідентифікатор цього отримання (ULID/UUIDv7 — монотонний у межах колектора).; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `source` | `object` | так |  |
| `source.source_id` | `string` | ні | Ідентифікатор джерела в оркестраторі; в автономному режимі може бути відсутній.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `source.kind` | `string` | так | Тип джерела. Розширюється додаванням нових значень (клієнти мають терпіти невідомі значення).; шаблон `"^[a-z][a-z0-9_-]{1,31}$"` |
| `source.name` | `string` | ні |  |
| `locator` | `object` | так | Посилання на першоджерело. |
| `locator.url` | `string` (uri) | ні | Запитаний URL. |
| `locator.final_url` | `string` (uri) | ні | URL після переадресацій. |
| `locator.canonical_url` | `string` (uri) | ні | Нормалізований URL, від якого обчислено material_id (web). |
| `locator.telegram` | `object` | ні |  |
| `locator.telegram.channel_id` | `string` | так |  |
| `locator.telegram.channel_username` | `string` | ні |  |
| `locator.telegram.message_id` | `integer` | так |  |
| `locator.telegram.grouped_id` | `string` | ні | Ідентифікатор альбому, якщо повідомлення в групі. |
| `fetched_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `published_at` | `string` (date-time) | ні | Час публікації, якщо його надає джерело. |
| `edited_at` | `string` (date-time) | ні | Час редагування, якщо його надає джерело. |
| `format` | `object` | так |  |
| `format.media_type` | `string` | так | Медіатип RFC 6838, наприклад 'text/html' або 'application/json'. Параметри (charset) передаються окремо.; шаблон `"^[a-z0-9!#$&^_.+-]+/[a-z0-9!#$&^_.+-]+$"` |
| `format.charset` | `string` | ні |  |
| `format.language` | `string` | ні | BCP 47, якщо відомо. |
| `format.content_kind` | `string` | ні | Грубий вид вмісту для маршрутизації: page (HTML-сторінка), feed, sitemap, json, message (Telegram), file. |
| `revision` | `object` | так | Версія вмісту. Однаковий content_sha256 у двох спостереженнях означає незмінений вміст. |
| `revision.content_sha256` | `string` | так | шаблон `"^[a-f0-9]{64}$"` |
| `revision.source_revision` | `string` | ні | Версія, яку надає джерело: ETag, Last-Modified, Telegram edit_date (або date неред. повідомлення) в epoch seconds. |
| `revision.sequence` | `integer` | ні | Строго монотонний номер ревізії того самого material_id для порядку спостережень, якщо джерело дає основу для нього; кожна нова ревізія має більший sequence. Telegram: edit_date (або date неред. повідомлення) в epoch seconds × 1000 + порядковий номер ревізії з іншим текстом, яку колектор побачив у межах тієї самої секунди (0 — перша), тож кілька редагувань за секунду мають різні зростаючі значення (до 1.1 — просто epoch seconds; значення нового формату завжди більші за старі). Одноразовий POST /v1/fetches бере номер із ревізій, які колектор уже видав (у будь-якому state_key), і нічого не записує; строгу монотонність гарантують збори одного state_key. Web: відсутній.; мін. `0` |
| `revision.is_edit` | `boolean` | ні | Джерело позначило матеріал як відредагований (Telegram edit). |
| `content` | `InlineContent` \| `BlobContent` | так | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `attachments` | array of `object` | ні | Додаткові файли (медіа Telegram, PDF за посиланням), кожен як ContentRef з описом. |
| `attachments[].name` | `string` | так |  |
| `attachments[].role` | `string` | ні |  |
| `attachments[].content` | `InlineContent` \| `BlobContent` | так | Вміст матеріалу або великого результату: або вбудований (kind=inline, до limits.transfer.inline_max_bytes), або посилання на blob-сховище (kind=blob). Кожен споживач зобов'язаний підтримувати обидва варіанти. Див. docs/adr/0004-large-materials.md. |
| `http` | `object` | ні |  |
| `http.status` | `integer` | ні | мін. `100`; макс. `599` |
| `http.headers` | `object` | ні | Підмножина заголовків відповіді (content-type, etag, last-modified, cache-control). Без Set-Cookie та інших чутливих. |
| `http.redirects` | array of `string` (uri) | ні |  |
| `discovery` | `object` | ні | Як матеріал було знайдено. |
| `discovery.strategy` | `string` | ні |  |
| `discovery.parent_url` | `string` (uri) | ні |  |
| `discovery.depth` | `integer` | ні | мін. `0` |
| `discovery.section` | `string` | ні | Ідентифікатор розділу з правил колектора (sections[].section_id), якщо URL йому відповідає. |
| `discovery.priority` | `integer` | ні |  |
| `collector` | `object` | так |  |
| `collector.name` | `string` | так |  |
| `collector.version` | `string` | так |  |
| `collector.rules` | `package-ref` | ні | Версія правил колектора, за якими отримано матеріал. |
| `collector.rules.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `collector.rules.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `collector.rules.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `collector.collection_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `diagnostics` | array of `DiagnosticMessage` | ні |  |
| `diagnostics[].level` | enum: `debug`, `info`, `warning`, `error` | так |  |
| `diagnostics[].code` | `string` | ні | шаблон `"^[a-z][a-z0-9_.-]{0,127}$"` |
| `diagnostics[].message` | `string` | так | макс. довжина `4000` |
| `diagnostics[].pointer` | `string` | ні | JSON Pointer у вихідних даних (наприклад '/entities/3/fields/price'). |
| `diagnostics[].material_id` | `string` | ні | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `diagnostics[].selector` | `string` | ні | CSS/XPath/JSONPath, з яким пов'язано повідомлення (для екстракторів). |
| `metadata` | `object` | ні | Додаткові метадані джерела (наприклад title, автор повідомлення, кількість переглядів). Відкритий об'єкт. Telegram: service_action — дія службового повідомлення каналу (channel_create, pin_message, chat_edit_title…); таке повідомлення зазвичай має порожній текст, тож завдання може відфільтрувати його умовою material.metadata.service_action not_exists. |

Приклад `web`:

```json
{
  "material_id": "web:3704326c60776c53169680099e2eed31",
  "observation_id": "obs_01J9ZQ4A0000000000000001",
  "source": {
    "source_id": "shop-example",
    "kind": "web",
    "name": "Shop Example"
  },
  "locator": {
    "url": "https://shop.example.test/product/a-100",
    "final_url": "https://shop.example.test/product/a-100",
    "canonical_url": "https://shop.example.test/product/a-100"
  },
  "fetched_at": "2026-09-27T10:00:05Z",
  "format": {
    "media_type": "text/html",
    "charset": "utf-8",
    "language": "uk",
    "content_kind": "page"
  },
  "revision": {
    "content_sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07",
    "source_revision": "\"etag-a100-v3\""
  },
  "content": {
    "kind": "inline",
    "media_type": "text/html",
    "encoding": "utf-8",
    "data": "<html><head><title>Kettle A-100</title></head><body><h1>Kettle A-100</h1><span class=\"price\">1299.00 UAH</span><span class=\"stock\">in stock</span></body></html>",
    "size_bytes": 160,
    "sha256": "e33249025b65cfa300d506c2c201202d7e96d0115ec85a33681f71370e7d4c07"
  },
  "http": {
    "status": 200,
    "headers": {
      "content-type": "text/html; charset=utf-8",
      "etag": "\"etag-a100-v3\""
    }
  },
  "discovery": {
    "strategy": "sitemap",
    "depth": 0,
    "section": "products",
    "priority": 10
  },
  "collector": {
    "name": "web-collector",
    "version": "0.1.0",
    "rules": {
      "package_id": "shop-example.web-rules",
      "version": "1.0.0",
      "digest": "sha256:bd33d6b0fb860947abb60fbf898610d7ad28e279daf21106399995dcd911674a"
    },
    "collection_id": "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F"
  },
  "metadata": {
    "title": "Kettle A-100"
  }
}
```

Приклад `blob`:

```json
{
  "material_id": "web:3704326c60776c53169680099e2eed31",
  "observation_id": "obs_01J9ZQ4A0000000000000003",
  "source": {
    "source_id": "shop-example",
    "kind": "web",
    "name": "Shop Example"
  },
  "locator": {
    "url": "https://shop.example.test/product/a-100",
    "final_url": "https://shop.example.test/product/a-100",
    "canonical_url": "https://shop.example.test/product/a-100"
  },
  "fetched_at": "2026-09-27T10:00:05Z",
  "format": {
    "media_type": "text/html",
    "charset": "utf-8",
    "language": "uk",
    "content_kind": "page"
  },
  "revision": {
    "content_sha256": "265a5a56e9b12039179290438ba92ce1acdeae16e6d51075973c6210fb1247c6"
  },
  "content": {
    "kind": "blob",
    "uri": "s3://jane-transit/web-collector/2026/09/27/obs_01J9ZQ4A0000000000000003.html",
    "download_url": "http://minio.localhost:9000/jane-transit/web-collector/2026/09/27/obs_01J9ZQ4A0000000000000003.html?X-Amz-Signature=redacted",
    "download_url_expires_at": "2026-09-27T11:00:05Z",
    "media_type": "text/html",
    "charset": "utf-8",
    "size_bytes": 1843201,
    "sha256": "265a5a56e9b12039179290438ba92ce1acdeae16e6d51075973c6210fb1247c6",
    "store": "transit",
    "expires_at": "2026-10-04T10:00:05Z"
  },
  "http": {
    "status": 200,
    "headers": {
      "content-type": "text/html; charset=utf-8",
      "etag": "\"etag-a100-v3\""
    }
  },
  "discovery": {
    "strategy": "sitemap",
    "depth": 0,
    "section": "products",
    "priority": 10
  },
  "collector": {
    "name": "web-collector",
    "version": "0.1.0",
    "rules": {
      "package_id": "shop-example.web-rules",
      "version": "1.0.0",
      "digest": "sha256:bd33d6b0fb860947abb60fbf898610d7ad28e279daf21106399995dcd911674a"
    },
    "collection_id": "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F"
  },
  "metadata": {
    "title": "Kettle A-100"
  }
}
```

Приклад `telegram`:

```json
{
  "material_id": "tg:-1001234567890:4521",
  "observation_id": "obs_01J9ZT0C0000000000000004",
  "source": {
    "source_id": "news-tg",
    "kind": "telegram",
    "name": "City events"
  },
  "locator": {
    "telegram": {
      "channel_id": "-1001234567890",
      "channel_username": "city_events_example",
      "message_id": 4521
    }
  },
  "fetched_at": "2026-09-27T12:30:00Z",
  "published_at": "2026-09-27T09:00:00Z",
  "edited_at": "2026-09-27T12:10:00Z",
  "format": {
    "media_type": "text/plain",
    "charset": "utf-8",
    "language": "uk",
    "content_kind": "message"
  },
  "revision": {
    "content_sha256": "39f16d19ae01f13cceb68b1822579074b18f9bb848a8c4bf5288c088daad8a5d",
    "source_revision": "1790503800",
    "sequence": 1790503800000,
    "is_edit": true
  },
  "content": {
    "kind": "inline",
    "media_type": "text/plain",
    "encoding": "utf-8",
    "data": "Концерт 12 жовтня о 19:00, Філармонія. Вхід вільний.",
    "size_bytes": 87,
    "sha256": "39f16d19ae01f13cceb68b1822579074b18f9bb848a8c4bf5288c088daad8a5d"
  },
  "discovery": {
    "strategy": "telegram_updates"
  },
  "collector": {
    "name": "telegram-collector",
    "version": "0.1.0"
  },
  "metadata": {
    "views": 1520
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../contracts/docs/errors.md)): `400`, `401`, `403`, `404`, `422`, `429`, `502`, `500`, `501`, `503`, `504`.
