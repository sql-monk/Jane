# Assistant: конфігурація

Параметри Assistant: адреси й токени сусідів, стан, пошук, політика вмісту, моделі й ліміти. Джерело фактів — `services/assistant/src/jane_assistant/settings.py` і спільні налаштування `jane_kit.config.JaneSettings` ревізії `48389a3`.

## Зміст

- [Як задаються параметри](#як-задаються-параметри)
- [Параметри процесу](#параметри-процесу)
- [Сусіди й токени](#сусіди-й-токени)
- [Стан](#стан)
- [Пошук джерел](#пошук-джерел)
- [Вміст матеріалів](#вміст-матеріалів)
- [Моделі, генерація й активація](#моделі-генерація-й-активація)
- [Автентифікація](#автентифікація)
- [Ліміти](#ліміти)
- [Як застосовуються зміни](#як-застосовуються-зміни)

## Як задаються параметри

Усі змінні мають префікс `JANE_ASSISTANT_`. Списки — JSON-рядком (`JANE_ASSISTANT_BLOB_ROOTS='["/data/raw"]'`). Ліміти — `JANE_ASSISTANT_LIMITS__<ГРУПА>__<ПОЛЕ>`, файл платформних лімітів — `JANE_ASSISTANT_LIMITS_FILE`, ліміти конкретного запуску — поле `limits` запиту (контрактне `limits.llm`).

## Параметри процесу

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_ASSISTANT_HOST` | рядок | `127.0.0.1` | адреса прослуховування; в образі Docker — `0.0.0.0` |
| `JANE_ASSISTANT_PORT` | ціле | `8000` | порт HTTP |
| `JANE_ASSISTANT_LOG_LEVEL` | рядок | `INFO` | рівень журналу |
| `JANE_ASSISTANT_LOG_FORMAT` | `json`, `console` | `json` | формат журналу |
| `JANE_ASSISTANT_METRICS_ENABLED` | булеве | `true` | `/metrics` |
| `JANE_ASSISTANT_HEALTH_CHECK_TIMEOUT_MS` | ціле ≥ 1 | `2000` | тайм-аут перевірок `/v1/health` |
| `JANE_ASSISTANT_INSTANCE_ID` | рядок | `<hostname>-<pid>-<uuid>` | власник job і оренд |
| `JANE_ASSISTANT_LIMITS_FILE` | шлях | — | файл платформних лімітів |

У `servers` контракту `assistant.v1.yaml` вказано `http://localhost:8111`, а типовий порт у коді — `8000`; dev-стек публікує контейнерний порт `8000`.

## Сусіди й токени

| Змінна | Типово | Вплив |
|---|---|---|
| `JANE_ASSISTANT_LLM_URL` | — | LLM gateway |
| `JANE_ASSISTANT_REGISTRY_URL` | — | Registry |
| `JANE_ASSISTANT_COLLECTOR_WEB_URL` | — | Web Collector |
| `JANE_ASSISTANT_COLLECTOR_TELEGRAM_URL` | — | Telegram Collector |
| `JANE_ASSISTANT_HANDLER_RUNTIME_URL` | — | Handler Runtime |
| `JANE_ASSISTANT_ORCHESTRATOR_URL` | — | Orchestrator |
| `JANE_ASSISTANT_STORAGE_URL` | — | Storage |
| `JANE_ASSISTANT_SERVICE_TOKEN_REF` | — | власний bearer-токен Assistant для всіх сусідів без окремого посилання: `env:VAR` або `file:/шлях` |
| `JANE_ASSISTANT_LLM_TOKEN_REF`, `…_REGISTRY_TOKEN_REF`, `…_COLLECTOR_WEB_TOKEN_REF`, `…_COLLECTOR_TELEGRAM_TOKEN_REF`, `…_HANDLER_RUNTIME_TOKEN_REF`, `…_ORCHESTRATOR_TOKEN_REF`, `…_STORAGE_TOKEN_REF` | — | окремий токен для сусіда |
| `JANE_ASSISTANT_SERVICE_TOKEN_ENV` | — | застаріле: назва змінної з токеном; замість нього — `SERVICE_TOKEN_REF=env:<назва>` |

Порожня адреса — сусіда не налаштовано: операції, яким він потрібен, повертають `upstream_unavailable` ([dependencies.md](dependencies.md)). Посилання на токени розв'язуються один раз під час старту. У dev-стеку: `JANE_ASSISTANT_SERVICE_TOKEN_REF=env:JANE_SECRET_ASSISTANT_TOKEN`, а шлюз приймає цей ключ з дозволом `llm:invoke`.

## Стан

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_ASSISTANT_STATE_DSN` | секрет (DSN) | — | PostgreSQL для сесій, job і ключів ідемпотентності кількох екземплярів; без нього — стан у пам'яті одного процесу |
| `JANE_ASSISTANT_STATE_SCHEMA` | рядок `^[a-z_][a-z0-9_]{0,62}$` | `jane_assistant` | схема таблиць стану; створюється під час старту |

## Пошук джерел

| Змінна | Типово | Вплив |
|---|---|---|
| `JANE_ASSISTANT_SEARCH_PROVIDER` | `none` | `none`, `static` або `http_json` |
| `JANE_ASSISTANT_SEARCH_STATIC_FILE` | — | для `static`: JSON-список `[{"title", "url"?, "telegram_username"?, "description"?, "aliases"?}]`; без файла сервіс не стартує |
| `JANE_ASSISTANT_SEARCH_URL_TEMPLATE` | — | для `http_json`: URL з `{query}`; без нього сервіс не стартує |
| `JANE_ASSISTANT_SEARCH_ITEMS_PATH` | `results` | шлях до списку результатів у відповіді |
| `JANE_ASSISTANT_SEARCH_TITLE_FIELD` | `title` | поле назви |
| `JANE_ASSISTANT_SEARCH_URL_FIELD` | `url` | поле адреси |
| `JANE_ASSISTANT_SEARCH_DESCRIPTION_FIELD` | `description` | поле опису |

Приклад статичного каталогу (з процесного e2e-тесту):

```json
[{"title": "Shop Example", "url": "https://shop.example.test/", "aliases": ["kettles", "store"]}]
```

Кандидат обирається автоматично, лише якщо його впевненість не нижча за `onboarding.auto_select_confidence` і відрив від другого — не менший за `onboarding.auto_select_margin`; інакше сесія переходить у `needs_disambiguation`.

## Вміст матеріалів

| Змінна | Типово | Вплив |
|---|---|---|
| `JANE_ASSISTANT_BLOB_ROOTS` | `[]` | каталоги, з яких можна читати `file://` вміст матеріалів; порожньо — заборонено |
| `JANE_ASSISTANT_DOWNLOAD_HOST_ALLOWLIST` | `[]` | `hostname` або `hostname:port` для `download_url`; порожньо — заборонено; помилка формату зупиняє старт |
| `JANE_ASSISTANT_CONTRACTS_DIR` | — | каталог `contracts/schemas` для локальної перевірки; без значення шукається вгору від пакета або в `/app/contracts` |

Вміст `inline` читається завжди. Розміри й тайм-аути — група [`content`](#інші-групи).

## Моделі, генерація й активація

| Змінна | Типово | Вплив |
|---|---|---|
| `JANE_ASSISTANT_LLM_MODEL_CHEAP` | `cheap` | псевдонім LLM gateway для класифікації (вибірка, невідомі матеріали) |
| `JANE_ASSISTANT_LLM_MODEL_STRONG` | `strong` | псевдонім для аналізу, варіантів, генерації й вдосконалення коду |
| `JANE_ASSISTANT_LLM_COMPLETION_MODE` | `sync` | `sync` — один HTTP-запит з тайм-аутом `llm_call.request_timeout_ms`; `async` — 202 і опитування job шлюзу кожні `clients.job_poll_interval_ms` у межах `clients.job_wait_timeout_ms` |
| `JANE_ASSISTANT_GENERATED_CODE_ALLOWED_MODULES` | `re`, `html`, `json`, `math`, `datetime`, `decimal`, `string`, `unicodedata`, `itertools`, `functools`, `collections`, `typing`, `dataclasses` | модулі, які може імпортувати згенерований код; справжній бар'єр — пісочниця Handler Runtime |
| `JANE_ASSISTANT_ONBOARDING_ALLOW_ACTIVATION` | `true` | дозволити `activate: true` під час прийняття (лише коли всі екстрактори пройшли тести) |
| `JANE_ASSISTANT_DEFAULT_STORAGE_PACKAGE` | — | `package_id@version` пакета збереження, який додається в чернетку завдання після кожного екстрактора |
| `JANE_ASSISTANT_DEFAULT_STORAGE_CONNECTION` | — | `connection_id` цього етапу збереження |

## Автентифікація

Спільні параметри (`JANE_ASSISTANT_AUTH_MODE`, `JANE_ASSISTANT_API_KEYS`, `JANE_ASSISTANT_JWT_*`) — [безпека](../../architecture/security.md#автентифікація). Усі операції `assistant.v1`, зокрема списки й `/v1/jobs/*`, вимагають дозволу `assistant:use`; `/v1/health` — без ключа.

## Ліміти

Порядок: типові значення → `JANE_ASSISTANT_LIMITS_FILE` → `JANE_ASSISTANT_LIMITS__*` → `limits` запиту; `hard_caps` платформи застосовуються останніми. Загальні правила — [ліміти й профілі](../../operations/limits.md). Невалідні ліміти запиту — 422 одразу, до створення job.

### Група `llm` (контракт `limits.llm`)

| Поле | Типово | Вплив |
|---|---|---|
| `budget.amount` | `2.0` | бюджет одного запуску: сесії підключення, вдосконалення або аналізу невідомого матеріалу; `0` — жодного виклику моделі |
| `budget.currency` | `USD` | валюта |
| `budget.period` | `run` | з `run` шлюз рахує всі виклики запуску за `scope.run_id`; інші періоди звужують лічильник рівня запиту |
| `max_requests_per_minute` | `30` | передається шлюзу з кожним запитом |
| `max_input_tokens_per_request` | `16000` | дані підганяються під цей ліміт так, як рахує шлюз |
| `max_output_tokens_per_request` | `8000` | місце для відповіді моделі (код, схема, очікування) |
| `max_improvement_attempts` | `3` | спроб вдосконалення; `0` — одразу `unresolved` |
| `max_onboarding_samples` | `60` | найбільша вибірка, яку класифікує модель |
| `min_onboarding_confidence` | `0.8` | впевненість, за якої вибірка достатня |

Assistant також сам зупиняється, щойно витрати запуску досягли `budget.amount`.

### Група `onboarding`

| Поле | Типово | Вплив |
|---|---|---|
| `min_distinct_types` | `2` | не довіряти охопленню одного типу, поки збір триває |
| `sample_batch_size` | `10` | матеріалів в одному запиті класифікації |
| `max_sample_chars` | `6000` | текст одного матеріалу для класифікації |
| `max_example_chars` | `12000` | текст прикладу для аналізу й генерації |
| `min_examples_per_type`, `max_examples_per_type` | `2`, `3` | коли тип вважається розпізнаним; скільки прикладів типу йде в аналіз і генерацію |
| `max_negative_examples` | `1` | матеріали інших типів як випадки `empty` |
| `poll_page_factor` | `3` | матеріалів за одне опитування = `sample_batch_size × poll_page_factor` |
| `max_candidates` | `5` | кандидатів пошуку |
| `auto_select_confidence`, `auto_select_margin` | `0.8`, `0.2` | автоматичний вибір кандидата |
| `max_candidate_packages` | `5` | готових екстракторів, перевірених на кожен тип сутності |
| `bind_threshold` | `0.9` | частка пройдених зразків для прив'язки готового пакета як є |
| `fork_threshold` | `0.5` | частка, вище якої готовий пакет форкається й адаптується |
| `max_generation_attempts` | `2` | спроб згенерувати пакет, що проходить тести |
| `max_proposals` | `4` | варіантів правил збору |
| `fetch_ratio` | `3` | збір вибірки отримує до `max_onboarding_samples × fetch_ratio` матеріалів |
| `collection_poll_wait_ms` | `1000` | довге опитування матеріалів збору |
| `max_empty_polls` | `30` | порожніх опитувань незавершеного збору до відмови |
| `requests_overhead_ratio` | `0.05` | надбавка до оцінки кількості запитів варіанта |
| `max_link_patterns`, `link_pattern_examples`, `max_pages_listed`, `max_evidence_examples` | `20`, `2`, `20`, `5` | обсяг доказів (шаблони посилань, пагінація) для аналізу й варіантів |
| `max_risk_url_chars` | `200` | довжина URL у тексті ризику |

### Група `material`

Як велика HTML-сторінка показується моделі й зберігається як тестова фікстура.

| Поле | Типово | Вплив |
|---|---|---|
| `max_fixture_bytes` | `131072` | HTML більший за це скорочується: скрипти, стилі, SVG, коментарі, потім кінець `body`; JSON-LD зберігається |
| `head_share`, `structured_share`, `text_share` | `0.1`, `0.6`, `0.15` | частки дайджесту для тегів `head`, структурованих даних і видимого тексту; сума ≤ 1 |
| `max_list_items`, `max_string_chars`, `short_string_chars` | `3`, `1000`, `200` | скорочення структурованих даних у дайджесті |
| `max_head_tags`, `max_microdata_types`, `max_microdata_props` | `60`, `20`, `30` | обсяг тегів і мікроданих у дайджесті |

### Групи `improvement` і `unknown`

| Поле | Типово | Вплив |
|---|---|---|
| `improvement.max_sample_chars` | `6000` | текст зразка для моделі |
| `improvement.max_problem_samples` | `10` | проблемних прикладів у запуску |
| `improvement.max_successful_examples` | `5` | успішних прикладів для регресій |
| `improvement.max_file_chars` | `20000` | файл пакета, переданий моделі |
| `improvement.max_proposal_bytes` | `1048576` | розмір `proposal` для `proposal_only` |
| `unknown.max_sample_chars` | `6000` | текст невідомого матеріалу |
| `unknown.min_confidence` | `0.6` | нижче — порада `none` |

### Інші групи

| Група | Поля й типові значення | Вплив |
|---|---|---|
| `state` | `pool_max_size=10`, `connect_timeout_ms=10000`, `in_progress_lease_ms=900000`, `job_lease_ms=60000`, `heartbeat_interval_ms=15000`, `session_retention_seconds=2592000` | PostgreSQL-стан; `session_retention_seconds` — строк зберігання сесій, але видалення фактично не виконується ([internals.md](internals.md#власні-дані)) |
| `transfer` | `inline_max_bytes=262144` | найбільший архів чернетки, що передається Handler Runtime inline |
| `content` | `max_material_bytes=16777216`, `fetch_timeout_ms=30000`, `connect_timeout_ms=5000` | читання вмісту матеріалів |
| `search` | `request_timeout_ms=10000`, `connect_timeout_ms=5000` | провайдер `http_json` |
| `clients` | `connect_timeout_ms=5000`, `request_timeout_ms=30000`, `retries` (`max_attempts=4`, `initial_backoff_ms=200`, `max_backoff_ms=10000`, `backoff_multiplier=2.0`, `jitter=true`), `max_connections=20`, `job_poll_interval_ms=1000`, `job_wait_timeout_ms=3600000` | виклики сусідів і очікування їхніх job |
| `llm_call` | `request_timeout_ms=900000`, `chars_per_token=2.0`, `prompt_overhead_chars=2000`, `part_overhead_chars=150` | синхронний виклик шлюзу й підгонка даних під ліміт токенів; `chars_per_token` не має перевищувати `gateway.chars_per_token_estimate` шлюзу |
| `pages` | `default_page_size=50`, `max_page_size=500` | списки сесій і запусків вдосконалення |
| `jobs` | `max_concurrent_jobs=4`, `max_queued_jobs=1000`, `job_timeout_ms=3600000`, `job_retention_seconds=86400`, `queue_full_retry_after_seconds=1` | job Assistant |
| `idempotency` | `idempotency_ttl_seconds=86400`, `in_memory_max_entries=10000` | ключі `Idempotency-Key` |

Приклад ліміту запуску в запиті (з контракту): три спроби й 1 USD на запуск.

```json
{"limits": {"max_improvement_attempts": 3, "budget": {"amount": 1, "currency": "USD", "period": "run"}}}
```

## Як застосовуються зміни

| Що змінено | Як застосувати |
|---|---|
| Змінні `JANE_ASSISTANT_*`, файл лімітів, токени | перезапуск сервісу |
| Ліміти одного запуску | поле `limits` запиту; діє на весь запуск, зокрема продовження сесії іншим екземпляром |
| Псевдоніми моделей | у LLM gateway (`PUT /v1/model-aliases/...`), без перезапуску Assistant |
