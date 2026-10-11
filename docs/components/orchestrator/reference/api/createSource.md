# POST /v1/sources

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L84). Не редагуйте вручну.

**Створити джерело**

| Властивість | Значення |
|---|---|
| operationId | `createSource` |
| Метод і шлях | `POST /v1/sources` |
| Scope | `orchestrator:write`, `orchestrator:admin` |
| Ідемпотентність | обов'язковий `Idempotency-Key` |
| Теги | sources |

## Параметри

| Назва | Де | Тип | Обов'язковий | Опис |
|---|---|---|---|---|
| `Idempotency-Key` | header | `string` | так | Ключ ідемпотентності (1–255 друкованих ASCII-символів; рекомендовано UUID або детермінований ключ доставки). Повтор із тим самим ключем і тим самим тілом повертає збережену відповідь (заголовок `Idempotency-Replayed: true`) без повторного ефекту. Той самий ключ з іншим тілом — 422 `idempotency_key_reused`. Запит ще виконується — 409 `idempotency_in_progress` (retryable). Сервіс пам'ятає ключ щонайменше `limits.transfer.idempotency_ttl_seconds`. |

## Тіло запиту

Тип вмісту `application/json`, схема `source`; обов'язкове: так.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `source_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `kind` | `string` | так | Тип джерела. Розширюється додаванням нових значень (клієнти мають терпіти невідомі значення).; шаблон `"^[a-z][a-z0-9_-]{1,31}$"` |
| `title` | `string` | так | мін. довжина `1`; макс. довжина `200` |
| `description` | `string` | ні | макс. довжина `4000` |
| `locator` | `object` | так |  |
| `locator.url` | `string` (uri) | ні |  |
| `locator.telegram_username` | `string` | ні |  |
| `locator.telegram_channel_id` | `string` | ні |  |
| `collector_rules` | `package-ref` | ні | Версія правил колектора за замовчуванням (пакет kind=collector-rules). Може бути відсутня до завершення підключення джерела. |
| `collector_rules.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `collector_rules.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `collector_rules.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
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
| `forward_unknown_to_llm` | `boolean` | ні | «Передавати в LLM невідомі сторінки» (ТЗ §8, критерій 11). За замовчуванням вимкнено: матеріал без відповідного обробника лише реєструється як невідомий.; типово `false` |
| `expected_entity_types` | array of `string` | ні | Очікувані типи даних джерела (наприклад product, price, event). Розширення пропонує асистент, приймає користувач. |
| `change_policy` | `object` | ні | Як активуються версії правил і екстракторів, створені LLM для цього джерела. |
| `change_policy.llm_versions` | enum: `manual_approval`, `auto_after_checks`, `forbidden` | ні | типово `"manual_approval"` |
| `connections` | `object` | ні | Логічне ім'я → connection_id (наприклад http-автентифікація сайту або обліковий запис Telegram). |
| `labels` | `Labels` | ні | Довільні мітки ключ-значення для фільтрації й пошуку. Не для секретів. |
| `created_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `updated_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |

Приклад `shop`:

```json
{
  "source_id": "shop-example",
  "kind": "web",
  "title": "Shop Example",
  "locator": {
    "url": "https://shop.example.test/"
  },
  "collector_rules": {
    "package_id": "shop-example.web-rules",
    "version": "1.0.0",
    "digest": "sha256:bd33d6b0fb860947abb60fbf898610d7ad28e279daf21106399995dcd911674a"
  },
  "limits": {
    "rate": {
      "requests_per_second_per_host": 2
    },
    "crawl": {
      "max_pages_per_run": 20000
    }
  },
  "forward_unknown_to_llm": false,
  "expected_entity_types": [
    "product"
  ],
  "change_policy": {
    "llm_versions": "manual_approval"
  },
  "labels": {
    "team": "catalog"
  }
}
```

Приклад `telegram`:

```json
{
  "source_id": "news-tg",
  "kind": "telegram",
  "title": "City events",
  "locator": {
    "telegram_username": "city_events_example"
  },
  "forward_unknown_to_llm": true,
  "expected_entity_types": [
    "event"
  ],
  "connections": {
    "account": "tg-main"
  }
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `201` | Джерело створено. | `source` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |
| `409` | Конфлікт стану (`conflict`, `version_exists`, `idempotency_in_progress`, `job_not_cancellable`, `upstream_conflict`). | `problem` |
| `422` | Семантична помилка (`validation_failed`, `idempotency_key_reused`, `limit_exceeded`, `secret_detected`, `schema_mismatch` тощо). | `problem` |

### Відповідь 201

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `source_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `kind` | `string` | так | Тип джерела. Розширюється додаванням нових значень (клієнти мають терпіти невідомі значення).; шаблон `"^[a-z][a-z0-9_-]{1,31}$"` |
| `title` | `string` | так | мін. довжина `1`; макс. довжина `200` |
| `description` | `string` | ні | макс. довжина `4000` |
| `locator` | `object` | так |  |
| `locator.url` | `string` (uri) | ні |  |
| `locator.telegram_username` | `string` | ні |  |
| `locator.telegram_channel_id` | `string` | ні |  |
| `collector_rules` | `package-ref` | ні | Версія правил колектора за замовчуванням (пакет kind=collector-rules). Може бути відсутня до завершення підключення джерела. |
| `collector_rules.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `collector_rules.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `collector_rules.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
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
| `forward_unknown_to_llm` | `boolean` | ні | «Передавати в LLM невідомі сторінки» (ТЗ §8, критерій 11). За замовчуванням вимкнено: матеріал без відповідного обробника лише реєструється як невідомий.; типово `false` |
| `expected_entity_types` | array of `string` | ні | Очікувані типи даних джерела (наприклад product, price, event). Розширення пропонує асистент, приймає користувач. |
| `change_policy` | `object` | ні | Як активуються версії правил і екстракторів, створені LLM для цього джерела. |
| `change_policy.llm_versions` | enum: `manual_approval`, `auto_after_checks`, `forbidden` | ні | типово `"manual_approval"` |
| `connections` | `object` | ні | Логічне ім'я → connection_id (наприклад http-автентифікація сайту або обліковий запис Telegram). |
| `labels` | `Labels` | ні | Довільні мітки ключ-значення для фільтрації й пошуку. Не для секретів. |
| `created_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `updated_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |

Приклад `shop`:

```json
{
  "source_id": "shop-example",
  "kind": "web",
  "title": "Shop Example",
  "locator": {
    "url": "https://shop.example.test/"
  },
  "collector_rules": {
    "package_id": "shop-example.web-rules",
    "version": "1.0.0",
    "digest": "sha256:bd33d6b0fb860947abb60fbf898610d7ad28e279daf21106399995dcd911674a"
  },
  "limits": {
    "rate": {
      "requests_per_second_per_host": 2
    },
    "crawl": {
      "max_pages_per_run": 20000
    }
  },
  "forward_unknown_to_llm": false,
  "expected_entity_types": [
    "product"
  ],
  "change_policy": {
    "llm_versions": "manual_approval"
  },
  "labels": {
    "team": "catalog"
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`, `409`, `422`.
