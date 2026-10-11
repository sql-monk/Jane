# POST /v1/task-validations

> Згенеровано `scripts/docs_reference.py` з [orchestrator.v1.yaml](../../../../../contracts/openapi/orchestrator.v1.yaml#L403). Не редагуйте вручну.

**Перевірити конфігурацію завдання без збереження (DAG, версії, прив'язки, ліміти)**

| Властивість | Значення |
|---|---|
| operationId | `validateTask` |
| Метод і шлях | `POST /v1/task-validations` |
| Scope | `orchestrator:read`, `orchestrator:admin` |
| Ідемпотентність | не потрібна: pure validation without side effects |
| Теги | tasks |

## Тіло запиту

Тип вмісту `application/json`, схема `task-config`; обов'язкове: так.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `task_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `title` | `string` | так | мін. довжина `1`; макс. довжина `200` |
| `description` | `string` | ні | макс. довжина `4000` |
| `enabled` | `boolean` | ні | типово `true` |
| `input` | `TaskInput` | так |  |
| `input.source_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `input.urls` | array of `string` (uri) | ні | Явний перелік матеріалів. Якщо задано — колектор отримує лише ці URL (стратегія seed_list без рекурсії) у межах scope джерела. Типово для завдань перевірки цін. Кількість обмежує limits.crawl.max_seed_urls (ефективне значення; перевищення — limit_exceeded), а не схема. |
| `input.stored_materials` | `object` | ні | Повторна обробка збережених RAW (ТЗ §10): фільтр збережених об'єктів замість нового збору. Завжди лише RAW джерела завдання (Material.source.source_id). Фільтри поєднуються через AND. material_ids обирає всі збережені спостереження цих матеріалів у часовому вікні since/until; точний вибір — object_ids (конкретні збережені RAW) або observation_ids (конкретні спостереження). |
| `input.stored_materials.storage_connection_id` | `string` | ні | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `input.stored_materials.since` | `string` (date-time) | ні | Час збереження (stored_at) не раніше. |
| `input.stored_materials.until` | `string` (date-time) | ні | Час збереження (stored_at) раніше за це значення. |
| `input.stored_materials.material_ids` | array of `string` | ні | Усі збережені спостереження цих матеріалів (у межах since/until). |
| `input.stored_materials.object_ids` | array of `string` | ні | Точний вибір: саме ці збережені RAW (StoredObjectRef.object_id у підключенні storage_connection_id), у заданому порядку; кожен читається через storage.v1 GET /v1/objects/{object_id}. Відсутній об'єкт завершує запуск помилкою not_found; RAW іншого джерела чи без відновлюваного Material пропускається. Кількість обмежує конфігурація оркестратора (більше — 422 limit_exceeded). |
| `input.stored_materials.observation_ids` | array of `string` | ні | Точний вибір спостережень (Material.observation_id): лише RAW цих спостережень серед відібраних іншими фільтрами. Кілька збережених копій одного спостереження не вгадуються (одна копія обробляється, посилання на RAW не записується). Кількість обмежує конфігурація оркестратора. |
| `stages` | array of `Stage` | так | мін. елементів `1` |
| `stages[].stage_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `stages[].kind` | enum: `collect`, `handler` | так |  |
| `stages[].title` | `string` | ні | макс. довжина `200` |
| `stages[].collector` | `CollectorStage` | ні | Лише для kind=collect. |
| `stages[].collector.collector` | `string` | так |  |
| `stages[].collector.rules` | `package-ref` | ні | Версія правил; відсутня — правила джерела. |
| `stages[].collector.mode` | enum: `full`, `incremental` | ні | incremental — продовжити від збереженого курсора/стану колектора (Telegram — нові повідомлення й редагування; web — повторне відвідування).; типово `"full"` |
| `stages[].handler` | `package-ref` | ні | Лише для kind=handler: точна версія пакета. |
| `stages[].handler.package_id` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `stages[].handler.version` | `string` | так | Точна версія Semantic Versioning 2.0.0. Діапазони версій у посиланнях на пакети заборонені.; шаблон `"^(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)\\.(0\|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?$"` |
| `stages[].handler.digest` | `string` | ні | Дайджест вмісту: 'sha256:' і 64 шістнадцяткові символи в нижньому регістрі.; шаблон `"^sha256:[a-f0-9]{64}$"` |
| `stages[].params` | `object` | ні | Параметри пакета (валідуються за params_schema маніфесту). |
| `stages[].connections` | `object` | ні | Логічне ім'я з required_connections пакета → connection_id. |
| `stages[].inputs` | array of `StageInput` | ні | Вхідні ребра DAG. Кілька ребер — етап отримує елементи з кількох етапів. Відсутні для kind=collect. |
| `stages[].inputs[].from` | `string` | так | Ідентифікатор, який обирає користувач (source_id, task_id, package_id, connection_id). Нижній регістр, цифри, '.', '_', '-'.; шаблон `"^[a-z0-9](?:[a-z0-9._-]{0,98}[a-z0-9])?$"` |
| `stages[].inputs[].select` | enum: `output`, `input_material`, `problems`, `unmatched_materials` | ні | Що брати з етапу-джерела і в якій формі (HandlerInvocation.inputs): output — вихід: collect — MaterialInput; extractor/transform із сутностями — EntitiesInput (entities або entities_ref, from_invocation_id, material вхідного елемента); llm/transform із даними — DataInput (data або data_ref, from_invocation_id); етап збереження — DataInput з data = WritesData ({writes: [WriteAck…]}, handler-invocation.schema.json) і from_invocation_id; input_material — вхідний матеріал етапу-джерела як MaterialInput (наприклад зберегти RAW лише успішно розібраних); problems — елементи зі статусом unrecognized або failed: MaterialInput вхідного матеріалу (якщо він був) і DataInput з data = ProblemData ({problem: {stage_id, status, invocation_id, handler, unrecognized?, failure?, diagnostics?}}) і from_invocation_id; unmatched_materials — матеріали collect-етапу, яким не відповідає жодна прив'язка, як MaterialInput (доставляються лише за ефективного forward_unknown_to_llm=true, інакше лише реєструються).; типово `"output"` |
| `stages[].inputs[].when` | `object` \| `object` \| `object` \| `Predicate` | ні | Умова переходу. Поля: material.* (метадані Material, напр. material.format.media_type, material.discovery.section, material.locator.url), result.status, result.failure.kind, result.entities_count, entity.entity_type, entity.fields.&lt;name>. |
| `stages[].bindings` | array of `Binding` | ні | Прив'язки екстрактора (ТЗ §7): до яких матеріалів застосовувати етап. Матеріал потрапляє на етап, якщо відповідає хоча б одній прив'язці. Етап без bindings отримує всі елементи своїх входів. Матеріал, що не відповідає жодній прив'язці жодного етапу з bindings, вважається невідомим (select=unmatched_materials). |
| `stages[].bindings[].source_ids` | array of `string` | ні | Порожньо — джерело завдання. |
| `stages[].bindings[].sections` | array of `string` | ні | section_id з правил колектора. |
| `stages[].bindings[].url_patterns` | array of `UrlPattern` | ні |  |
| `stages[].bindings[].media_types` | array of `string` | ні |  |
| `stages[].bindings[].content_kinds` | array of `string` | ні |  |
| `stages[].limits` | `limits` | ні | Ліміти рівня stage. |
| `stages[].limits.concurrency` | `object` | ні |  |
| `stages[].limits.rate` | `object` | ні |  |
| `stages[].limits.crawl` | `object` | ні |  |
| `stages[].limits.timeouts` | `object` | ні |  |
| `stages[].limits.retries` | `RetryPolicy` | ні | Повтори застосовуються лише до помилок із retryable=true і лише разом з тим самим ключем ідемпотентності. |
| `stages[].limits.queue` | `object` | ні |  |
| `stages[].limits.sandbox` | `object` | ні |  |
| `stages[].limits.llm` | `object` | ні |  |
| `stages[].limits.transfer` | `object` | ні |  |
| `stages[].limits.telegram` | `object` | ні |  |
| `stages[].retries` | `RetryPolicy` | ні | Повтори застосовуються лише до помилок із retryable=true і лише разом з тим самим ключем ідемпотентності. |
| `stages[].retries.max_attempts` | `integer` | ні | Загальна кількість спроб, включно з першою.; мін. `1` |
| `stages[].retries.initial_backoff_ms` | `integer` | ні | мін. `0` |
| `stages[].retries.max_backoff_ms` | `integer` | ні | мін. `0` |
| `stages[].retries.backoff_multiplier` | `number` | ні | мін. `1` |
| `stages[].retries.jitter` | `boolean` | ні |  |
| `stages[].on_failure` | enum: `continue`, `fail_run` | ні | Що робити, коли елемент на етапі остаточно failed після повторів: continue — записати проблему й продовжити інші елементи; fail_run — завершити запуск помилкою.; типово `"continue"` |
| `schedule` | `Schedule` | ні |  |
| `schedule.type` | enum: `manual`, `once`, `cron`, `interval` | так |  |
| `schedule.at` | `string` (date-time) | ні | Для once. |
| `schedule.cron` | `string` | ні | П'ять полів cron (хв год день міс день_тижня) для type=cron.; шаблон `"^\\S+( \\S+){4}$"` |
| `schedule.interval_seconds` | `integer` | ні | Для type=interval.; мін. `1` |
| `schedule.timezone` | `string` | ні | IANA, наприклад Europe/Kyiv.; типово `"UTC"` |
| `schedule.start_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `schedule.end_at` | `string` (date-time) | ні | Момент часу RFC 3339 з часовою зоною; сервіси повертають UTC із суфіксом 'Z'. |
| `schedule.enabled` | `boolean` | ні | типово `true` |
| `schedule.overlap` | enum: `skip`, `queue`, `allow` | ні | Що робити, якщо попередній запуск ще триває (allow обмежується limits.concurrency.max_parallel_runs_per_task).; типово `"skip"` |
| `retries` | `RetryPolicy` | ні | Повтори етапів за замовчуванням (перекриває limits.retries). |
| `retries.max_attempts` | `integer` | ні | Загальна кількість спроб, включно з першою.; мін. `1` |
| `retries.initial_backoff_ms` | `integer` | ні | мін. `0` |
| `retries.max_backoff_ms` | `integer` | ні | мін. `0` |
| `retries.backoff_multiplier` | `number` | ні | мін. `1` |
| `retries.jitter` | `boolean` | ні |  |
| `limits` | `limits` | ні | Ліміти рівня task. |
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
| `forward_unknown_to_llm` | `boolean` | ні | «Передавати в LLM невідомі сторінки» на рівні завдання. Відсутнє — успадковується від джерела (за замовчуванням false). |
| `labels` | `Labels` | ні | Довільні мітки ключ-значення для фільтрації й пошуку. Не для секретів. |

Приклад `catalog`:

```json
{
  "task_id": "shop-catalog",
  "title": "Повний збір каталогу Shop Example",
  "input": {
    "source_id": "shop-example"
  },
  "stages": [
    {
      "stage_id": "collect",
      "kind": "collect",
      "collector": {
        "collector": "web",
        "rules": {
          "package_id": "shop-example.web-rules",
          "version": "1.0.0",
          "digest": "sha256:bd33d6b0fb860947abb60fbf898610d7ad28e279daf21106399995dcd911674a"
        },
        "mode": "full"
      }
    },
    {
      "stage_id": "store-raw",
      "kind": "handler",
      "handler": {
        "package_id": "jane.storage-files",
        "version": "1.0.0",
        "digest": "sha256:b2d691abc92053497acfe8f61d6cd32488b126a4aeb6e080c63d966ecd096a94"
      },
      "connections": {
        "target": "raw-files"
      },
      "inputs": [
        {
          "from": "collect"
        }
      ]
    },
    {
      "stage_id": "extract-products",
      "kind": "handler",
      "handler": {
        "package_id": "shop-example.product-extractor",
        "version": "1.2.0",
        "digest": "sha256:4f6440c6a17b54edef02166e12a3bffd2364cbf790484d1f076b5d2e5ef78a35"
      },
      "inputs": [
        {
          "from": "collect",
          "when": {
            "field": "material.format.media_type",
            "op": "eq",
            "value": "text/html"
          }
        }
      ],
      "bindings": [
        {
          "sections": [
            "products"
          ]
        },
        {
          "url_patterns": [
            {
              "value": "shop.example.test/p/**"
            }
          ]
        }
      ],
      "limits": {
        "sandbox": {
          "memory_mb": 512,
          "wall_time_ms": 20000
        }
      }
    },
    {
      "stage_id": "store-products",
      "kind": "handler",
      "handler": {
        "package_id": "jane.storage-postgresql",
        "version": "1.0.0",
        "digest": "sha256:8751adf49b3d26c9a59f6ecc83f52feccc0edade6db1a98c1a0155b0380a045b"
      },
      "connections": {
        "target": "results-pg"
      },
      "inputs": [
        {
          "from": "extract-products",
          "select": "output",
          "when": {
            "field": "result.status",
            "op": "in",
            "value": [
              "success",
              "unrecognized"
            ]
          }
        }
      ]
    },
    {
      "stage_id": "analyze-problems",
      "kind": "handler",
      "handler": {
        "package_id": "jane.llm-page-triage",
        "version": "1.0.0",
        "digest": "sha256:4041159bcbdce2491ed21066225c584e70c2d5ad8783ba979f3df4adad98d77b"
      },
      "inputs": [
        {
          "from": "extract-products",
          "select": "problems"
        }
      ],
      "on_failure": "continue"
    },
    {
      "stage_id": "unknown-pages",
      "kind": "handler",
      "handler": {
        "package_id": "jane.llm-page-triage",
        "version": "1.0.0",
        "digest": "sha256:4041159bcbdce2491ed21066225c584e70c2d5ad8783ba979f3df4adad98d77b"
      },
      "inputs": [
        {
          "from": "collect",
          "select": "unmatched_materials"
        }
      ]
    }
  ],
  "schedule": {
    "type": "cron",
    "cron": "0 2 * * 0",
    "timezone": "Europe/Kyiv",
    "overlap": "skip"
  },
  "retries": {
    "max_attempts": 5,
    "initial_backoff_ms": 1000,
    "max_backoff_ms": 60000,
    "backoff_multiplier": 2,
    "jitter": true
  },
  "limits": {
    "crawl": {
      "max_depth": 5
    },
    "queue": {
      "max_inflight_materials": 200
    }
  },
  "forward_unknown_to_llm": false,
  "labels": {
    "kind": "catalog"
  }
}
```

## Відповіді

| Код | Опис | Схема |
|---|---|---|
| `200` | Результат перевірки (невалідна конфігурація — теж 200 з valid=false). | `TaskValidation` |
| `401` | Немає або недійсний токен (`unauthenticated`). | `problem` |

### Відповідь 200

Тип вмісту `application/json`.

| Поле | Тип | Обов'язкове | Опис |
|---|---|---|---|
| `valid` | `boolean` | так |  |
| `errors` | array of `FieldError` | так |  |
| `errors[].pointer` | `string` | ні | JSON Pointer (RFC 6901) до поля тіла запиту, наприклад '/stages/2/handler/version'. |
| `errors[].parameter` | `string` | ні | Ім'я query/path/header параметра. |
| `errors[].code` | `string` | ні | шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `errors[].message` | `string` | так |  |
| `warnings` | array of `FieldError` | ні |  |
| `warnings[].pointer` | `string` | ні | JSON Pointer (RFC 6901) до поля тіла запиту, наприклад '/stages/2/handler/version'. |
| `warnings[].parameter` | `string` | ні | Ім'я query/path/header параметра. |
| `warnings[].code` | `string` | ні | шаблон `"^[a-z][a-z0-9_]{1,63}$"` |
| `warnings[].message` | `string` | так |  |
| `effective_forward_unknown_to_llm` | `boolean` | ні |  |

Приклад `warnings`:

```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    {
      "pointer": "/stages/5",
      "code": "unknown_flag_off",
      "message": "stage 'unknown-pages' consumes unmatched_materials but forward_unknown_to_llm is false; materials will only be registered"
    }
  ],
  "effective_forward_unknown_to_llm": false
}
```

## Примітки

- Помилки повертаються як `application/problem+json` ([модель помилок](../../../../../contracts/docs/errors.md)): `401`.
