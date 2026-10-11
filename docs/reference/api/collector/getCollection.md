# GET /v1/collections/{collection_id}

> Згенеровано `scripts/docs_reference.py` з [collector.v1.yaml](../../../../contracts/openapi/collector.v1.yaml#L294). Не редагуйте вручну.

**Стан і статистика збору**

| Властивість | Значення |
|---|---|
| operationId | `getCollection` |
| Метод і шлях | `GET /v1/collections/{collection_id}` |
| Scope | `collector:read` |
| Ідемпотентність | — |
| Теги | collections |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `collection_id` | path | `string` | так | Дорівнює job_id, повернутому POST /v1/collections. |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Стан збору. | `Collection` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `404` | Ресурс не знайдено (`not_found`). | `problem` |
| `503` | Сервіс або його залежність тимчасово недоступні (`service_unavailable`, `upstream_unavailable`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `collection_id` | `string` | так | Непрозорий ідентифікатор, згенерований сервісом-власником (наприклад 'mat_01J9Z...'). Клієнти не розбирають його структуру.; шаблон `"^[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"` |
| `status` | enum: `queued`, `running`, `cancelling`, `succeeded`, `failed`, `cancelled` | так |  |
| `paused_by_backpressure` | `boolean` | ні |  |
| `source_kind` | `string` | так | Тип джерела. Розширюється додаванням нових значень (клієнти мають терпіти невідомі значення).; шаблон `"^[a-z][a-z0-9_-]{1,31}$"` |
| `source_id` | `string` | ні | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `rules` | `package-ref` | ні | Посилання на конкретну незмінну версію пакета в репозиторії обробників. Діапазони версій і 'latest' заборонені: етап завдання завжди фіксує точну версію. digest — дайджест архіву версії; якщо заданий, виконавець зобов'язаний перевірити збіг (digest_mismatch). |
| `rules.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `rules.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `rules.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `mode` | enum: `full`, `incremental` | ні |  |
| `state_key` | `string` | ні |  |
| `created_at` | `string` (date-time) | так | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `finished_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `stats` | `CollectionStats` | так |  |
| `stats.discovered` | `integer` | ні | мін. `0` |
| `stats.fetched` | `integer` | ні | мін. `0` |
| `stats.emitted` | `integer` | ні | мін. `0` |
| `stats.acknowledged` | `integer` | ні | мін. `0` |
| `stats.unacked` | `integer` | ні | мін. `0` |
| `stats.duplicates` | `integer` | ні | мін. `0` |
| `stats.skipped_out_of_scope` | `integer` | ні | мін. `0` |
| `stats.skipped_robots` | `integer` | ні | мін. `0` |
| `stats.not_modified` | `integer` | ні | мін. `0` |
| `stats.errors` | `integer` | ні | мін. `0` |
| `stats.frontier_size` | `integer` | ні | мін. `0` |
| `stats.bytes_fetched` | `integer` | ні | мін. `0` |
| `stats.by_strategy` | `object` | ні |  |
| `effective_limits` | `limits` | ні | Модель лімітів з успадкуванням (ТЗ §13.1 п.5, критерій 13). Один і той самий об'єкт Limits задається на рівнях platform → source → task → stage; кожне поле необов'язкове. Ефективне значення: глибоке злиття за рівнями, нижчий рівень перекриває вищий; відсутнє поле успадковується (null заборонено — щоб 'скинути' до успадкованого, поле просто не передають). Після злиття кожне числове поле обмежується platform.hard_caps (min). Під час виконання значення додатково лише звужуються обмеженнями конкретного сайту чи сервісу (robots.txt Crawl-delay, Retry-After, Telegram flood-wait, ліміти провайдера LLM) — вони ніколи не послаблюються конфігурацією. Сервіс, що отримав limits у запиті (автономний режим), застосовує min(ліміти запиту, власні hard_caps). Типові значення — у сервісних конфігураціях і профілях WP-14; довідковий профіль — contracts/examples/schemas/limits/*.json. |
| `effective_limits.concurrency` | `object` | ні |  |
| `effective_limits.concurrency.max_parallel_fetches` | `integer` | ні | Одночасні завантаження одного збору колектора (на збір: кожен збір окремо, на будь-якому екземплярі; спільний для всіх зборів ліміт хоста — max_parallel_fetches_per_host).; мін. `1` |
| `effective_limits.concurrency.max_parallel_fetches_per_host` | `integer` | ні | Одночасні запити до одного хоста джерела (host[:port]) від усієї платформи: усіх зборів і одноразових запитів колектора разом, також усіх його екземплярів, що ділять сховище стану (один вузол, спільний каталог стану). Якщо активні на хості збори мають різні значення, діє найменше. Екземпляри з окремими сховищами стану — окремі колектори й між собою цей ліміт не узгоджують.; мін. `1` |
| `effective_limits.concurrency.max_parallel_invocations` | `integer` | ні | Одночасні виклики обробника (на екземпляр сервісу-виконавця або на етап).; мін. `1` |
| `effective_limits.concurrency.max_parallel_runs_per_task` | `integer` | ні | Скільки запусків одного завдання можуть іти одночасно.; мін. `1` |
| `effective_limits.concurrency.max_parallel_stage_items` | `integer` | ні | Скільки елементів один етап запуску обробляє одночасно.; мін. `1` |
| `effective_limits.rate` | `object` | ні |  |
| `effective_limits.rate.requests_per_second_per_host` | `number` | ні | Частота стартів запитів до одного хоста джерела; область дії — як у concurrency.max_parallel_fetches_per_host (уся платформа: усі збори, одноразові запити й екземпляри зі спільним сховищем стану). Інтервал між стартами = max(1 / requests_per_second_per_host, min_delay_ms_per_host, Crawl-delay за respect_crawl_delay); між активними на хості зборами діє найбільший інтервал. |
| `effective_limits.rate.min_delay_ms_per_host` | `integer` | ні | Мінімальний інтервал між стартами запитів до одного хоста джерела; область дії у Web Collector — як у requests_per_second_per_host. Telegram Collector (єдиний «хост» — API Telegram) застосовує його до викликів API одного збору.; мін. `0` |
| `effective_limits.rate.burst_per_host` | `integer` | ні | мін. `1` |
| `effective_limits.rate.respect_crawl_delay` | `boolean` | ні | Враховувати Crawl-delay з robots.txt (може лише збільшити затримку). |
| `effective_limits.crawl` | `object` | ні |  |
| `effective_limits.crawl.max_depth` | `integer` | ні | мін. `0` |
| `effective_limits.crawl.max_pages_per_run` | `integer` | ні | мін. `1` |
| `effective_limits.crawl.max_bytes_per_run` | `integer` | ні | мін. `1` |
| `effective_limits.crawl.max_material_bytes` | `integer` | ні | Більший матеріал обривається з діагностикою 'truncated' або відкидається (за налаштуванням колектора).; мін. `1` |
| `effective_limits.crawl.max_redirects` | `integer` | ні | мін. `0` |
| `effective_limits.crawl.max_links_per_page` | `integer` | ні | мін. `0` |
| `effective_limits.crawl.max_seed_urls` | `integer` | ні | Максимальна кількість URL у явному переліку (TaskInput.urls, CollectionRequest.urls, seed_list).; мін. `1` |
| `effective_limits.crawl.max_frontier_size` | `integer` | ні | Максимальна кількість URL у черзі обходу.; мін. `1` |
| `effective_limits.crawl.revisit_interval_seconds` | `integer` | ні | Мінімальний інтервал повторного відвідування того самого URL.; мін. `0` |
| `effective_limits.timeouts` | `object` | ні |  |
| `effective_limits.timeouts.connect_timeout_ms` | `integer` | ні | мін. `1` |
| `effective_limits.timeouts.request_timeout_ms` | `integer` | ні | мін. `1` |
| `effective_limits.timeouts.invocation_timeout_ms` | `integer` | ні | Тайм-аут одного виклику обробника (вкл. пісочницю).; мін. `1` |
| `effective_limits.timeouts.stage_timeout_ms` | `integer` | ні | мін. `1` |
| `effective_limits.timeouts.run_timeout_ms` | `integer` | ні | мін. `1` |
| `effective_limits.timeouts.sync_response_max_ms` | `integer` | ні | Якщо синхронна операція не встигає — сервіс повертає 202 + Job.; мін. `1` |
| `effective_limits.retries` | `RetryPolicy` | ні | Повтори застосовуються лише до помилок із retryable=true і лише разом з тим самим ключем ідемпотентності. |
| `effective_limits.retries.max_attempts` | `integer` | ні | Загальна кількість спроб, включно з першою.; мін. `1` |
| `effective_limits.retries.initial_backoff_ms` | `integer` | ні | мін. `0` |
| `effective_limits.retries.max_backoff_ms` | `integer` | ні | мін. `0` |
| `effective_limits.retries.backoff_multiplier` | `number` | ні | мін. `1` |
| `effective_limits.retries.jitter` | `boolean` | ні |  |
| `effective_limits.queue` | `object` | ні |  |
| `effective_limits.queue.max_queue_depth` | `integer` | ні | Максимальна кількість задач у черзі оркестратора для завдання; при переповненні збір пригальмовується (backpressure).; мін. `1` |
| `effective_limits.queue.max_inflight_materials` | `integer` | ні | Скільки матеріалів одного запуску можуть одночасно перебувати в обробці.; мін. `1` |
| `effective_limits.queue.max_unacked_materials` | `integer` | ні | Розмір буфера колектора: скільки отриманих, але ще не забраних споживачем матеріалів він тримає, перш ніж призупинити обхід.; мін. `1` |
| `effective_limits.sandbox` | `object` | ні |  |
| `effective_limits.sandbox.cpu_cores` | `number` | ні |  |
| `effective_limits.sandbox.memory_mb` | `integer` | ні | мін. `16` |
| `effective_limits.sandbox.wall_time_ms` | `integer` | ні | мін. `1` |
| `effective_limits.sandbox.max_output_bytes` | `integer` | ні | мін. `1` |
| `effective_limits.sandbox.max_processes` | `integer` | ні | мін. `1` |
| `effective_limits.sandbox.tmpfs_mb` | `integer` | ні | мін. `0` |
| `effective_limits.llm` | `object` | ні |  |
| `effective_limits.llm.max_requests_per_minute` | `integer` | ні | мін. `1` |
| `effective_limits.llm.max_input_tokens_per_request` | `integer` | ні | мін. `1` |
| `effective_limits.llm.max_output_tokens_per_request` | `integer` | ні | мін. `1` |
| `effective_limits.llm.budget` | `Budget` | ні | Бюджет витрат LLM на рівні (platform/source/task). Перевищення зупиняє нові виклики з кодом budget_exhausted. Семантика однакова для LLM-шлюзу й асистента: (1) виклик дозволено, лише якщо для кожного застосовного бюджету витрачено &lt; amount і витрачено + зарезервовано + найгірша оцінка вартості виклику ≤ amount; тому amount: 0 означає «LLM вимкнено» для рівня — відхиляється навіть модель із нульовою ціною; (2) витрати рахуються у вікні period: day/week/month — календарний період UTC, total — без скидання, run — окремо для кожного scope.run_id запиту LLM-шлюзу (асистент передає ідентифікатор свого запуску: сесії підключення чи job), а без run_id вікном є сам запит з усіма його повторами; бюджет ніколи не пропускається; (3) бюджет у limits запиту стосується найконкретнішого рівня запиту (task, якщо є task_id, інакше source, інакше platform) і лише звужує: збережені бюджети рівнів діють і далі; з тим самим period і currency лічильник спільний і діє менша сума, інакше перевіряються обидва. |
| `effective_limits.llm.max_improvement_attempts` | `integer` | ні | Скільки спроб вдосконалення екстрактора на одну групу проблем.; мін. `0` |
| `effective_limits.llm.max_onboarding_samples` | `integer` | ні | Верхня межа вибірки під час дослідження джерела (фактична кількість адаптивна).; мін. `1` |
| `effective_limits.llm.min_onboarding_confidence` | `number` | ні | Поріг достатньої впевненості вибірки під час дослідження джерела (ТЗ §8): асистент вибирає матеріали, доки оцінка впевненості не досягне порога; не досягнуто в межах бюджету й max_onboarding_samples — сесія insufficient_sample. Вищий поріг — більша вибірка й витрати, тому hard_caps обмежують його зверху. Типово 0.8.; макс. `1` |
| `effective_limits.transfer` | `object` | ні |  |
| `effective_limits.transfer.inline_max_bytes` | `integer` | ні | Вміст до цього розміру можна передавати inline; більший — лише blob.; мін. `0` |
| `effective_limits.transfer.max_request_body_bytes` | `integer` | ні | мін. `1` |
| `effective_limits.transfer.transit_ttl_seconds` | `integer` | ні | Час життя транзитних blob-об'єктів.; мін. `60` |
| `effective_limits.transfer.download_url_ttl_seconds` | `integer` | ні | мін. `1` |
| `effective_limits.transfer.job_retention_seconds` | `integer` | ні | мін. `60` |
| `effective_limits.transfer.idempotency_ttl_seconds` | `integer` | ні | Скільки сервіс пам'ятає Idempotency-Key для повтору відповіді.; мін. `60` |
| `effective_limits.telegram` | `object` | ні |  |
| `effective_limits.telegram.max_messages_per_run` | `integer` | ні | мін. `1` |
| `effective_limits.telegram.max_media_bytes` | `integer` | ні | мін. `0` |
| `effective_limits.telegram.max_flood_wait_seconds` | `integer` | ні | Якщо Telegram вимагає чекати довше — збір призупиняється з помилкою rate_limited замість блокування воркера.; мін. `0` |

Приклад `running`:

```json
{
  "collection_id": "job_01J9ZQ3F8W2N4K7T5B6C1D0E9F",
  "status": "running",
  "paused_by_backpressure": true,
  "source_kind": "web",
  "source_id": "shop-example",
  "rules": {
    "package_id": "shop-example.web-rules",
    "version": "1.0.0"
  },
  "mode": "full",
  "state_key": "shop-example",
  "created_at": "2026-09-27T10:00:00Z",
  "stats": {
    "discovered": 1840,
    "fetched": 620,
    "emitted": 598,
    "acknowledged": 98,
    "unacked": 500,
    "duplicates": 211,
    "skipped_out_of_scope": 305,
    "skipped_robots": 4,
    "not_modified": 0,
    "errors": 2,
    "frontier_size": 1220,
    "bytes_fetched": 48211002,
    "by_strategy": {
      "sitemap": 1500,
      "recursive": 290,
      "listing": 50
    }
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../contracts/docs/errors.md)): `401`, `404`, `503`.
