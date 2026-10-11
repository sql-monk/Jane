# GET /v1/limits/platform

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L1297). Не редагуйте вручну.

**Ліміти рівня платформи (типові значення й жорсткі стелі)**

| Властивість | Значення |
|---|---|
| operationId | `getPlatformLimits` |
| Метод і шлях | `GET /v1/limits/platform` |
| Scope | `orchestrator:read`, `orchestrator:admin` |
| Ідемпотентність | — |
| Теги | limits |

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Ліміти платформи. | `PlatformLimits` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `profile` | `string` | ні | Ім'я профілю середовища, з якого взято значення (див. docs/adr/0007-target-environments.md). |
| `defaults` | `limits` | так | Модель лімітів з успадкуванням (ТЗ §13.1 п.5, критерій 13). Один і той самий об'єкт Limits задається на рівнях platform → source → task → stage; кожне поле необов'язкове. Ефективне значення: глибоке злиття за рівнями, нижчий рівень перекриває вищий; відсутнє поле успадковується (null заборонено — щоб 'скинути' до успадкованого, поле просто не передають). Після злиття кожне числове поле обмежується platform.hard_caps (min). Під час виконання значення додатково лише звужуються обмеженнями конкретного сайту чи сервісу (robots.txt Crawl-delay, Retry-After, Telegram flood-wait, ліміти провайдера LLM) — вони ніколи не послаблюються конфігурацією. Сервіс, що отримав limits у запиті (автономний режим), застосовує min(ліміти запиту, власні hard_caps). Типові значення — у сервісних конфігураціях і профілях WP-14; довідковий профіль — contracts/examples/schemas/limits/*.json. |
| `defaults.concurrency` | `object` | ні |  |
| `defaults.concurrency.max_parallel_fetches` | `integer` | ні | Одночасні завантаження одного збору колектора (на збір: кожен збір окремо, на будь-якому екземплярі; спільний для всіх зборів ліміт хоста — max_parallel_fetches_per_host).; мін. `1` |
| `defaults.concurrency.max_parallel_fetches_per_host` | `integer` | ні | Одночасні запити до одного хоста джерела (host[:port]) від усієї платформи: усіх зборів і одноразових запитів колектора разом, також усіх його екземплярів, що ділять сховище стану (один вузол, спільний каталог стану). Якщо активні на хості збори мають різні значення, діє найменше. Екземпляри з окремими сховищами стану — окремі колектори й між собою цей ліміт не узгоджують.; мін. `1` |
| `defaults.concurrency.max_parallel_invocations` | `integer` | ні | Одночасні виклики обробника (на екземпляр сервісу-виконавця або на етап).; мін. `1` |
| `defaults.concurrency.max_parallel_runs_per_task` | `integer` | ні | Скільки запусків одного завдання можуть іти одночасно.; мін. `1` |
| `defaults.concurrency.max_parallel_stage_items` | `integer` | ні | Скільки елементів один етап запуску обробляє одночасно.; мін. `1` |
| `defaults.rate` | `object` | ні |  |
| `defaults.rate.requests_per_second_per_host` | `number` | ні | Частота стартів запитів до одного хоста джерела; область дії — як у concurrency.max_parallel_fetches_per_host (уся платформа: усі збори, одноразові запити й екземпляри зі спільним сховищем стану). Інтервал між стартами = max(1 / requests_per_second_per_host, min_delay_ms_per_host, Crawl-delay за respect_crawl_delay); між активними на хості зборами діє найбільший інтервал. |
| `defaults.rate.min_delay_ms_per_host` | `integer` | ні | Мінімальний інтервал між стартами запитів до одного хоста джерела; область дії у Web Collector — як у requests_per_second_per_host. Telegram Collector (єдиний «хост» — API Telegram) застосовує його до викликів API одного збору.; мін. `0` |
| `defaults.rate.burst_per_host` | `integer` | ні | мін. `1` |
| `defaults.rate.respect_crawl_delay` | `boolean` | ні | Враховувати Crawl-delay з robots.txt (може лише збільшити затримку). |
| `defaults.crawl` | `object` | ні |  |
| `defaults.crawl.max_depth` | `integer` | ні | мін. `0` |
| `defaults.crawl.max_pages_per_run` | `integer` | ні | мін. `1` |
| `defaults.crawl.max_bytes_per_run` | `integer` | ні | мін. `1` |
| `defaults.crawl.max_material_bytes` | `integer` | ні | Більший матеріал обривається з діагностикою 'truncated' або відкидається (за налаштуванням колектора).; мін. `1` |
| `defaults.crawl.max_redirects` | `integer` | ні | мін. `0` |
| `defaults.crawl.max_links_per_page` | `integer` | ні | мін. `0` |
| `defaults.crawl.max_seed_urls` | `integer` | ні | Максимальна кількість URL у явному переліку (TaskInput.urls, CollectionRequest.urls, seed_list).; мін. `1` |
| `defaults.crawl.max_frontier_size` | `integer` | ні | Максимальна кількість URL у черзі обходу.; мін. `1` |
| `defaults.crawl.revisit_interval_seconds` | `integer` | ні | Мінімальний інтервал повторного відвідування того самого URL.; мін. `0` |
| `defaults.timeouts` | `object` | ні |  |
| `defaults.timeouts.connect_timeout_ms` | `integer` | ні | мін. `1` |
| `defaults.timeouts.request_timeout_ms` | `integer` | ні | мін. `1` |
| `defaults.timeouts.invocation_timeout_ms` | `integer` | ні | Тайм-аут одного виклику обробника (вкл. пісочницю).; мін. `1` |
| `defaults.timeouts.stage_timeout_ms` | `integer` | ні | мін. `1` |
| `defaults.timeouts.run_timeout_ms` | `integer` | ні | мін. `1` |
| `defaults.timeouts.sync_response_max_ms` | `integer` | ні | Якщо синхронна операція не встигає — сервіс повертає 202 + Job.; мін. `1` |
| `defaults.retries` | `RetryPolicy` | ні | Повтори застосовуються лише до помилок із retryable=true і лише разом з тим самим ключем ідемпотентності. |
| `defaults.retries.max_attempts` | `integer` | ні | Загальна кількість спроб, включно з першою.; мін. `1` |
| `defaults.retries.initial_backoff_ms` | `integer` | ні | мін. `0` |
| `defaults.retries.max_backoff_ms` | `integer` | ні | мін. `0` |
| `defaults.retries.backoff_multiplier` | `number` | ні | мін. `1` |
| `defaults.retries.jitter` | `boolean` | ні |  |
| `defaults.queue` | `object` | ні |  |
| `defaults.queue.max_queue_depth` | `integer` | ні | Максимальна кількість задач у черзі оркестратора для завдання; при переповненні збір пригальмовується (backpressure).; мін. `1` |
| `defaults.queue.max_inflight_materials` | `integer` | ні | Скільки матеріалів одного запуску можуть одночасно перебувати в обробці.; мін. `1` |
| `defaults.queue.max_unacked_materials` | `integer` | ні | Розмір буфера колектора: скільки отриманих, але ще не забраних споживачем матеріалів він тримає, перш ніж призупинити обхід.; мін. `1` |
| `defaults.sandbox` | `object` | ні |  |
| `defaults.sandbox.cpu_cores` | `number` | ні |  |
| `defaults.sandbox.memory_mb` | `integer` | ні | мін. `16` |
| `defaults.sandbox.wall_time_ms` | `integer` | ні | мін. `1` |
| `defaults.sandbox.max_output_bytes` | `integer` | ні | мін. `1` |
| `defaults.sandbox.max_processes` | `integer` | ні | мін. `1` |
| `defaults.sandbox.tmpfs_mb` | `integer` | ні | мін. `0` |
| `defaults.llm` | `object` | ні |  |
| `defaults.llm.max_requests_per_minute` | `integer` | ні | мін. `1` |
| `defaults.llm.max_input_tokens_per_request` | `integer` | ні | мін. `1` |
| `defaults.llm.max_output_tokens_per_request` | `integer` | ні | мін. `1` |
| `defaults.llm.budget` | `Budget` | ні | Бюджет витрат LLM на рівні (platform/source/task). Перевищення зупиняє нові виклики з кодом budget_exhausted. Семантика однакова для LLM-шлюзу й асистента: (1) виклик дозволено, лише якщо для кожного застосовного бюджету витрачено &lt; amount і витрачено + зарезервовано + найгірша оцінка вартості виклику ≤ amount; тому amount: 0 означає «LLM вимкнено» для рівня — відхиляється навіть модель із нульовою ціною; (2) витрати рахуються у вікні period: day/week/month — календарний період UTC, total — без скидання, run — окремо для кожного scope.run_id запиту LLM-шлюзу (асистент передає ідентифікатор свого запуску: сесії підключення чи job), а без run_id вікном є сам запит з усіма його повторами; бюджет ніколи не пропускається; (3) бюджет у limits запиту стосується найконкретнішого рівня запиту (task, якщо є task_id, інакше source, інакше platform) і лише звужує: збережені бюджети рівнів діють і далі; з тим самим period і currency лічильник спільний і діє менша сума, інакше перевіряються обидва. |
| `defaults.llm.max_improvement_attempts` | `integer` | ні | Скільки спроб вдосконалення екстрактора на одну групу проблем.; мін. `0` |
| `defaults.llm.max_onboarding_samples` | `integer` | ні | Верхня межа вибірки під час дослідження джерела (фактична кількість адаптивна).; мін. `1` |
| `defaults.llm.min_onboarding_confidence` | `number` | ні | Поріг достатньої впевненості вибірки під час дослідження джерела (ТЗ §8): асистент вибирає матеріали, доки оцінка впевненості не досягне порога; не досягнуто в межах бюджету й max_onboarding_samples — сесія insufficient_sample. Вищий поріг — більша вибірка й витрати, тому hard_caps обмежують його зверху. Типово 0.8.; макс. `1` |
| `defaults.transfer` | `object` | ні |  |
| `defaults.transfer.inline_max_bytes` | `integer` | ні | Вміст до цього розміру можна передавати inline; більший — лише blob.; мін. `0` |
| `defaults.transfer.max_request_body_bytes` | `integer` | ні | мін. `1` |
| `defaults.transfer.transit_ttl_seconds` | `integer` | ні | Час життя транзитних blob-об'єктів.; мін. `60` |
| `defaults.transfer.download_url_ttl_seconds` | `integer` | ні | мін. `1` |
| `defaults.transfer.job_retention_seconds` | `integer` | ні | мін. `60` |
| `defaults.transfer.idempotency_ttl_seconds` | `integer` | ні | Скільки сервіс пам'ятає Idempotency-Key для повтору відповіді.; мін. `60` |
| `defaults.telegram` | `object` | ні |  |
| `defaults.telegram.max_messages_per_run` | `integer` | ні | мін. `1` |
| `defaults.telegram.max_media_bytes` | `integer` | ні | мін. `0` |
| `defaults.telegram.max_flood_wait_seconds` | `integer` | ні | Якщо Telegram вимагає чекати довше — збір призупиняється з помилкою rate_limited замість блокування воркера.; мін. `0` |
| `hard_caps` | `limits` | ні | Модель лімітів з успадкуванням (ТЗ §13.1 п.5, критерій 13). Один і той самий об'єкт Limits задається на рівнях platform → source → task → stage; кожне поле необов'язкове. Ефективне значення: глибоке злиття за рівнями, нижчий рівень перекриває вищий; відсутнє поле успадковується (null заборонено — щоб 'скинути' до успадкованого, поле просто не передають). Після злиття кожне числове поле обмежується platform.hard_caps (min). Під час виконання значення додатково лише звужуються обмеженнями конкретного сайту чи сервісу (robots.txt Crawl-delay, Retry-After, Telegram flood-wait, ліміти провайдера LLM) — вони ніколи не послаблюються конфігурацією. Сервіс, що отримав limits у запиті (автономний режим), застосовує min(ліміти запиту, власні hard_caps). Типові значення — у сервісних конфігураціях і профілях WP-14; довідковий профіль — contracts/examples/schemas/limits/*.json. |
| `hard_caps.concurrency` | `object` | ні |  |
| `hard_caps.concurrency.max_parallel_fetches` | `integer` | ні | Одночасні завантаження одного збору колектора (на збір: кожен збір окремо, на будь-якому екземплярі; спільний для всіх зборів ліміт хоста — max_parallel_fetches_per_host).; мін. `1` |
| `hard_caps.concurrency.max_parallel_fetches_per_host` | `integer` | ні | Одночасні запити до одного хоста джерела (host[:port]) від усієї платформи: усіх зборів і одноразових запитів колектора разом, також усіх його екземплярів, що ділять сховище стану (один вузол, спільний каталог стану). Якщо активні на хості збори мають різні значення, діє найменше. Екземпляри з окремими сховищами стану — окремі колектори й між собою цей ліміт не узгоджують.; мін. `1` |
| `hard_caps.concurrency.max_parallel_invocations` | `integer` | ні | Одночасні виклики обробника (на екземпляр сервісу-виконавця або на етап).; мін. `1` |
| `hard_caps.concurrency.max_parallel_runs_per_task` | `integer` | ні | Скільки запусків одного завдання можуть іти одночасно.; мін. `1` |
| `hard_caps.concurrency.max_parallel_stage_items` | `integer` | ні | Скільки елементів один етап запуску обробляє одночасно.; мін. `1` |
| `hard_caps.rate` | `object` | ні |  |
| `hard_caps.rate.requests_per_second_per_host` | `number` | ні | Частота стартів запитів до одного хоста джерела; область дії — як у concurrency.max_parallel_fetches_per_host (уся платформа: усі збори, одноразові запити й екземпляри зі спільним сховищем стану). Інтервал між стартами = max(1 / requests_per_second_per_host, min_delay_ms_per_host, Crawl-delay за respect_crawl_delay); між активними на хості зборами діє найбільший інтервал. |
| `hard_caps.rate.min_delay_ms_per_host` | `integer` | ні | Мінімальний інтервал між стартами запитів до одного хоста джерела; область дії у Web Collector — як у requests_per_second_per_host. Telegram Collector (єдиний «хост» — API Telegram) застосовує його до викликів API одного збору.; мін. `0` |
| `hard_caps.rate.burst_per_host` | `integer` | ні | мін. `1` |
| `hard_caps.rate.respect_crawl_delay` | `boolean` | ні | Враховувати Crawl-delay з robots.txt (може лише збільшити затримку). |
| `hard_caps.crawl` | `object` | ні |  |
| `hard_caps.crawl.max_depth` | `integer` | ні | мін. `0` |
| `hard_caps.crawl.max_pages_per_run` | `integer` | ні | мін. `1` |
| `hard_caps.crawl.max_bytes_per_run` | `integer` | ні | мін. `1` |
| `hard_caps.crawl.max_material_bytes` | `integer` | ні | Більший матеріал обривається з діагностикою 'truncated' або відкидається (за налаштуванням колектора).; мін. `1` |
| `hard_caps.crawl.max_redirects` | `integer` | ні | мін. `0` |
| `hard_caps.crawl.max_links_per_page` | `integer` | ні | мін. `0` |
| `hard_caps.crawl.max_seed_urls` | `integer` | ні | Максимальна кількість URL у явному переліку (TaskInput.urls, CollectionRequest.urls, seed_list).; мін. `1` |
| `hard_caps.crawl.max_frontier_size` | `integer` | ні | Максимальна кількість URL у черзі обходу.; мін. `1` |
| `hard_caps.crawl.revisit_interval_seconds` | `integer` | ні | Мінімальний інтервал повторного відвідування того самого URL.; мін. `0` |
| `hard_caps.timeouts` | `object` | ні |  |
| `hard_caps.timeouts.connect_timeout_ms` | `integer` | ні | мін. `1` |
| `hard_caps.timeouts.request_timeout_ms` | `integer` | ні | мін. `1` |
| `hard_caps.timeouts.invocation_timeout_ms` | `integer` | ні | Тайм-аут одного виклику обробника (вкл. пісочницю).; мін. `1` |
| `hard_caps.timeouts.stage_timeout_ms` | `integer` | ні | мін. `1` |
| `hard_caps.timeouts.run_timeout_ms` | `integer` | ні | мін. `1` |
| `hard_caps.timeouts.sync_response_max_ms` | `integer` | ні | Якщо синхронна операція не встигає — сервіс повертає 202 + Job.; мін. `1` |
| `hard_caps.retries` | `RetryPolicy` | ні | Повтори застосовуються лише до помилок із retryable=true і лише разом з тим самим ключем ідемпотентності. |
| `hard_caps.retries.max_attempts` | `integer` | ні | Загальна кількість спроб, включно з першою.; мін. `1` |
| `hard_caps.retries.initial_backoff_ms` | `integer` | ні | мін. `0` |
| `hard_caps.retries.max_backoff_ms` | `integer` | ні | мін. `0` |
| `hard_caps.retries.backoff_multiplier` | `number` | ні | мін. `1` |
| `hard_caps.retries.jitter` | `boolean` | ні |  |
| `hard_caps.queue` | `object` | ні |  |
| `hard_caps.queue.max_queue_depth` | `integer` | ні | Максимальна кількість задач у черзі оркестратора для завдання; при переповненні збір пригальмовується (backpressure).; мін. `1` |
| `hard_caps.queue.max_inflight_materials` | `integer` | ні | Скільки матеріалів одного запуску можуть одночасно перебувати в обробці.; мін. `1` |
| `hard_caps.queue.max_unacked_materials` | `integer` | ні | Розмір буфера колектора: скільки отриманих, але ще не забраних споживачем матеріалів він тримає, перш ніж призупинити обхід.; мін. `1` |
| `hard_caps.sandbox` | `object` | ні |  |
| `hard_caps.sandbox.cpu_cores` | `number` | ні |  |
| `hard_caps.sandbox.memory_mb` | `integer` | ні | мін. `16` |
| `hard_caps.sandbox.wall_time_ms` | `integer` | ні | мін. `1` |
| `hard_caps.sandbox.max_output_bytes` | `integer` | ні | мін. `1` |
| `hard_caps.sandbox.max_processes` | `integer` | ні | мін. `1` |
| `hard_caps.sandbox.tmpfs_mb` | `integer` | ні | мін. `0` |
| `hard_caps.llm` | `object` | ні |  |
| `hard_caps.llm.max_requests_per_minute` | `integer` | ні | мін. `1` |
| `hard_caps.llm.max_input_tokens_per_request` | `integer` | ні | мін. `1` |
| `hard_caps.llm.max_output_tokens_per_request` | `integer` | ні | мін. `1` |
| `hard_caps.llm.budget` | `Budget` | ні | Бюджет витрат LLM на рівні (platform/source/task). Перевищення зупиняє нові виклики з кодом budget_exhausted. Семантика однакова для LLM-шлюзу й асистента: (1) виклик дозволено, лише якщо для кожного застосовного бюджету витрачено &lt; amount і витрачено + зарезервовано + найгірша оцінка вартості виклику ≤ amount; тому amount: 0 означає «LLM вимкнено» для рівня — відхиляється навіть модель із нульовою ціною; (2) витрати рахуються у вікні period: day/week/month — календарний період UTC, total — без скидання, run — окремо для кожного scope.run_id запиту LLM-шлюзу (асистент передає ідентифікатор свого запуску: сесії підключення чи job), а без run_id вікном є сам запит з усіма його повторами; бюджет ніколи не пропускається; (3) бюджет у limits запиту стосується найконкретнішого рівня запиту (task, якщо є task_id, інакше source, інакше platform) і лише звужує: збережені бюджети рівнів діють і далі; з тим самим period і currency лічильник спільний і діє менша сума, інакше перевіряються обидва. |
| `hard_caps.llm.max_improvement_attempts` | `integer` | ні | Скільки спроб вдосконалення екстрактора на одну групу проблем.; мін. `0` |
| `hard_caps.llm.max_onboarding_samples` | `integer` | ні | Верхня межа вибірки під час дослідження джерела (фактична кількість адаптивна).; мін. `1` |
| `hard_caps.llm.min_onboarding_confidence` | `number` | ні | Поріг достатньої впевненості вибірки під час дослідження джерела (ТЗ §8): асистент вибирає матеріали, доки оцінка впевненості не досягне порога; не досягнуто в межах бюджету й max_onboarding_samples — сесія insufficient_sample. Вищий поріг — більша вибірка й витрати, тому hard_caps обмежують його зверху. Типово 0.8.; макс. `1` |
| `hard_caps.transfer` | `object` | ні |  |
| `hard_caps.transfer.inline_max_bytes` | `integer` | ні | Вміст до цього розміру можна передавати inline; більший — лише blob.; мін. `0` |
| `hard_caps.transfer.max_request_body_bytes` | `integer` | ні | мін. `1` |
| `hard_caps.transfer.transit_ttl_seconds` | `integer` | ні | Час життя транзитних blob-об'єктів.; мін. `60` |
| `hard_caps.transfer.download_url_ttl_seconds` | `integer` | ні | мін. `1` |
| `hard_caps.transfer.job_retention_seconds` | `integer` | ні | мін. `60` |
| `hard_caps.transfer.idempotency_ttl_seconds` | `integer` | ні | Скільки сервіс пам'ятає Idempotency-Key для повтору відповіді.; мін. `60` |
| `hard_caps.telegram` | `object` | ні |  |
| `hard_caps.telegram.max_messages_per_run` | `integer` | ні | мін. `1` |
| `hard_caps.telegram.max_media_bytes` | `integer` | ні | мін. `0` |
| `hard_caps.telegram.max_flood_wait_seconds` | `integer` | ні | Якщо Telegram вимагає чекати довше — збір призупиняється з помилкою rate_limited замість блокування воркера.; мін. `0` |

Приклад `dev`:

```json
{
  "profile": "dev-laptop",
  "defaults": {
    "concurrency": {
      "max_parallel_fetches": 8,
      "max_parallel_fetches_per_host": 2,
      "max_parallel_invocations": 2,
      "max_parallel_runs_per_task": 1,
      "max_parallel_stage_items": 4
    },
    "rate": {
      "requests_per_second_per_host": 1,
      "min_delay_ms_per_host": 500,
      "burst_per_host": 2,
      "respect_crawl_delay": true
    },
    "crawl": {
      "max_depth": 5,
      "max_pages_per_run": 5000,
      "max_bytes_per_run": 2147483648,
      "max_material_bytes": 10485760,
      "max_redirects": 5,
      "max_links_per_page": 2000,
      "max_seed_urls": 100000,
      "max_frontier_size": 100000,
      "revisit_interval_seconds": 86400
    },
    "timeouts": {
      "connect_timeout_ms": 10000,
      "request_timeout_ms": 30000,
      "invocation_timeout_ms": 60000,
      "stage_timeout_ms": 3600000,
      "run_timeout_ms": 21600000,
      "sync_response_max_ms": 25000
    },
    "retries": {
      "max_attempts": 3,
      "initial_backoff_ms": 1000,
      "max_backoff_ms": 60000,
      "backoff_multiplier": 2,
      "jitter": true
    },
    "queue": {
      "max_queue_depth": 10000,
      "max_inflight_materials": 100,
      "max_unacked_materials": 500
    },
    "sandbox": {
      "cpu_cores": 1,
      "memory_mb": 512,
      "wall_time_ms": 30000,
      "max_output_bytes": 4194304,
      "max_processes": 16,
      "tmpfs_mb": 64
    },
    "llm": {
      "max_requests_per_minute": 20,
      "max_input_tokens_per_request": 32000,
      "max_output_tokens_per_request": 4096,
      "budget": {
        "amount": 5,
        "currency": "USD",
        "period": "day"
      },
      "max_improvement_attempts": 3,
      "max_onboarding_samples": 60
    },
    "transfer": {
      "inline_max_bytes": 262144,
      "max_request_body_bytes": 16777216,
      "transit_ttl_seconds": 604800,
      "download_url_ttl_seconds": 3600,
      "job_retention_seconds": 604800,
      "idempotency_ttl_seconds": 86400
    },
    "telegram": {
      "max_messages_per_run": 10000,
      "max_media_bytes": 20971520,
      "max_flood_wait_seconds": 600
    }
  },
  "hard_caps": {
    "concurrency": {
      "max_parallel_fetches": 16,
      "max_parallel_invocations": 4
    },
    "sandbox": {
      "memory_mb": 2048,
      "cpu_cores": 2,
      "wall_time_ms": 300000
    },
    "llm": {
      "max_output_tokens_per_request": 16000
    }
  }
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`.
