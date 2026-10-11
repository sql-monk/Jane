# Web Collector: налаштування

Параметри процесу задаються змінними середовища з префіксом `JANE_WEB_COLLECTOR_`; ліміти — шарами від платформи до окремої стратегії. Джерело фактів — `services/web-collector/src/jane_web_collector/settings.py` і `libs/jane-kit` (ревізія `48389a3`).

## Зміст

- [Застосування змін](#застосування-змін)
- [Процес і API](#процес-і-api)
- [Стан, правила й доставка](#стан-правила-й-доставка)
- [Безпека й підключення](#безпека-й-підключення)
- [Рендеринг](#рендеринг)
- [Оренда й кілька екземплярів](#оренда-й-кілька-екземплярів)
- [Ліміти](#ліміти)
- [Успадкування лімітів](#успадкування-лімітів)

## Застосування змін

| Що змінюється | Як застосувати |
|---|---|
| Змінні середовища, файл лімітів платформи | перезапуск процесу |
| `rules.limits` (рівень джерела) | у правилах наступного запиту |
| `limits` запиту `POST /v1/collections` чи `POST /v1/fetches` | у цьому запиті |
| `strategies[].limits` | лише для URL цієї стратегії в наступному зборі |

Ефективні ліміти збору повертаються в `effective_limits` (`GET /v1/collections/{id}`), типові — у `limits` відповіді `GET /v1/info`; повний набір разом зі службовими лімітами — у журналі старту (`configured limits`).

## Процес і API

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_WEB_COLLECTOR_HOST` | рядок | `127.0.0.1` | адреса прослуховування; в образі — `0.0.0.0` |
| `JANE_WEB_COLLECTOR_PORT` | ціле | `8101` | порт HTTP API |
| `JANE_WEB_COLLECTOR_INSTANCE_ID` | рядок | `<hostname>-<pid>-<uuid>` | ідентифікатор екземпляра для оренди зборів; має бути унікальним для кожного запуску |
| `JANE_WEB_COLLECTOR_LOG_LEVEL` | рядок | `INFO` | рівень журналу |
| `JANE_WEB_COLLECTOR_LOG_FORMAT` | `json`, `console` | `json` | формат журналу |
| `JANE_WEB_COLLECTOR_METRICS_ENABLED` | bool | `true` | ендпойнт `/metrics` |
| `JANE_WEB_COLLECTOR_HEALTH_CHECK_TIMEOUT_MS` | ціле ≥ 1 | `2000` | межа часу кожної перевірки `/v1/health` |
| `JANE_WEB_COLLECTOR_AUTH_MODE` | `none`, `api_key`, `jwt` | `none` | автентифікація викликів |
| `JANE_WEB_COLLECTOR_API_KEYS` | JSON-список | `[]` | ключі для `api_key`: `name`, `scopes`, `sha256` або `secret_ref` |
| `JANE_WEB_COLLECTOR_API_KEYS_FILE` | шлях | — | ті самі ключі з файла JSON або YAML |
| `JANE_WEB_COLLECTOR_AUTH_NONE_ALLOW_REMOTE` | bool | `false` | дозволити `auth_mode=none` на не-loopback адресі |
| `JANE_WEB_COLLECTOR_METRICS_PUBLIC` | bool | `true` | `/metrics` без токена |

Решта параметрів `jwt` (`JWT_JWKS_URL`, `JWT_ISSUER`, `JWT_AUDIENCE` тощо з тим самим префіксом) — спільні для сервісів, описані в [jane-kit](../../../libs/jane-kit/README.md). Права операцій: `collector:run` — запуск отримання й зборів, скасування job, скидання стану; `collector:read` — читання зборів, матеріалів, помилок, стану; `connections:write` — керування підключеннями.

У `auth_mode=none` з адресою, відмінною від loopback, сервіс не стартує без `AUTH_NONE_ALLOW_REMOTE=true`.

## Стан, правила й доставка

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_WEB_COLLECTOR_STATE_DIR` | шлях | `.jane/web-collector` | каталог файла `state.db`; спільний для екземплярів одного вузла |
| `JANE_WEB_COLLECTOR_TRANSIT_DIR` | шлях | не задано | транзитні blob для великих матеріалів; без нього доставка лише inline |
| `JANE_WEB_COLLECTOR_RULES_DIR` | шлях | не задано | локальні пакети правил для `rules_ref` (`<package_id>/<version>/`) |
| `JANE_WEB_COLLECTOR_REGISTRY_URL` | URL | не задано | Registry для `rules_ref`; перевіряється після `RULES_DIR` |
| `JANE_WEB_COLLECTOR_REGISTRY_TOKEN_ENV` | рядок | не задано | **ім'я** змінної з токеном для Registry (не саме значення) |
| `JANE_WEB_COLLECTOR_CONTRACTS_DIR` | шлях | `JANE_CONTRACTS_DIR` або `contracts/` checkout | JSON Schema для перевірки запитів і правил |
| `JANE_WEB_COLLECTOR_DISCOVERY_PATH` | шлях | `services/web-collector/strategies/discovery` | пакет стратегій пошуку |
| `JANE_WEB_COLLECTOR_USER_AGENT` | рядок | `JaneBot/0.1 (+https://github.com/jane)` | типовий User-Agent; перше слово — токен для `robots.txt`; `rules.fetch.user_agent` перевизначає |

## Безпека й підключення

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_WEB_COLLECTOR_SECRET_ENV_PREFIX` | рядок | `JANE_SECRET_` | посилання `env:` підключень лише на змінні з цим префіксом; порожньо — `env:` вимкнено |
| `JANE_WEB_COLLECTOR_SECRET_FILES_DIR` | шлях | `/run/secrets` | посилання `file:` лише всередині каталогу; порожньо — `file:` вимкнено |
| `JANE_WEB_COLLECTOR_CONNECTION_ORIGIN_ALLOWLIST` | JSON-список | `[]` | точні origin (`https://site.example`), яким дозволено передавати облікові дані підключення; порожньо — нікому |
| `JANE_WEB_COLLECTOR_EGRESS_DENY_LINK_LOCAL` | bool | `true` | заборонити з'єднання з link-local (`169.254.0.0/16`, метадані хмари, `fe80::/10`) |
| `JANE_WEB_COLLECTOR_EGRESS_DENY_PRIVATE` | bool | `false` | заборонити також loopback, RFC 1918 та інші непублічні адреси |

Політика вихідних адрес перевіряє кожну адресу після DNS-розв'язання для кожного з'єднання, включно з кроками переадресації, `robots.txt` і запитами стратегій. `EGRESS_DENY_PRIVATE` типово вимкнено, бо тестовий сайт dev-стеку працює в приватній мережі Docker; вмикайте його, якщо джерела — лише публічні сайти. Відмова — `access_denied_by_policy`.

Керовані підключення `kind=http` (`PUT /v1/connections/{id}`, схема — [connection.schema.json](../../../contracts/schemas/common/connection.schema.json)) застосовуються так:

| `params.auth_scheme` | Потрібні `secret_refs` | Заголовок |
|---|---|---|
| `bearer` | `token` | `Authorization: Bearer <token>` |
| `basic` | `username`, `password` | `Authorization: Basic ...` |
| `header` | `value`, плюс `params.header_name` | `<header_name>: <value>` |

Облікові дані надсилаються лише на хост початкового URL і лише якщо його origin є в `CONNECTION_ORIGIN_ALLOWLIST`. У правилах (`fetch.headers`) дозволено лише `Accept`, `Accept-Language` і `Cache-Control`; інші заголовки дають `secret_detected`.

## Рендеринг

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_WEB_COLLECTOR_RENDER_ENABLED` | bool | `true` | виконувати `fetch.render_js`; вимкнено або немає Chromium — URL отримують `not_implemented` |
| `JANE_WEB_COLLECTOR_RENDER_WAIT_UNTIL` | `domcontentloaded`, `load`, `networkidle` | `networkidle` | чого чекати перед зняттям DOM |
| `JANE_WEB_COLLECTOR_RENDER_BLOCK_RESOURCE_TYPES` | JSON-список | `["image", "media", "font"]` | типи ресурсів, які браузер не завантажує |
| `JANE_WEB_COLLECTOR_RENDER_BROWSER_EXECUTABLE` | шлях | браузер Playwright | інший виконуваний файл Chromium |
| `JANE_WEB_COLLECTOR_RENDER_DENY_PRIVATE` | bool | `true` | скрипти сторінки звертаються до непублічних адрес лише на власному хості сторінки та в `scope.allowed_domains` |

## Оренда й кілька екземплярів

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_WEB_COLLECTOR_LEASE_SECONDS` | ціле ≥ 2 | `30` | без поновлення оренди довше за цей час збір переходить до іншого екземпляра |
| `JANE_WEB_COLLECTOR_HEARTBEAT_INTERVAL_MS` | ціле ≥ 50 | `5000` | як часто власник поновлює оренду й перевіряє скасування |
| `JANE_WEB_COLLECTOR_STATE_BUSY_TIMEOUT_MS` | ціле ≥ 1 | `10000` | скільки запис чекає блокування SQLite, яке тримає інший процес |
| `JANE_WEB_COLLECTOR_IDEMPOTENCY_LEASE_MS` | ціле ≥ 1000 | `900000` | після цього часу заявку `Idempotency-Key` зупиненого екземпляра може перехопити інший |

Правила старту: `HEARTBEAT_INTERVAL_MS + STATE_BUSY_TIMEOUT_MS < LEASE_SECONDS × 1000` і `collector.shared_host_ttl_seconds × 2/3 > STATE_BUSY_TIMEOUT_MS / 1000`; інакше сервіс не стартує.

## Ліміти

Групи й назви полів відповідають [limits.schema.json](../../../contracts/schemas/common/limits.schema.json); група `collector` — службові ліміти цього сервісу, яких немає в контракті.

| Ліміт | Типово | Призначення |
|---|---|---|
| `concurrency.max_parallel_fetches` | 4 | паралельні завантаження одного збору |
| `concurrency.max_parallel_fetches_per_host` | 2 | паралельні запити до хоста (спільно для всіх зборів і екземплярів) |
| `rate.requests_per_second_per_host` | 1.0 | частота стартів запитів до хоста |
| `rate.min_delay_ms_per_host` | 500 | мінімальний інтервал між стартами |
| `rate.respect_crawl_delay` | `true` | враховувати `Crawl-delay` з `robots.txt` |
| `crawl.max_depth` | 5 | глибина від початкових URL |
| `crawl.max_pages_per_run` | 5000 | бюджет запитів збору |
| `crawl.max_bytes_per_run` | 2 ГіБ | бюджет байтів збору |
| `crawl.max_material_bytes` | 10 МіБ | тіло понад ліміт обрізається (`truncated`) |
| `crawl.max_redirects` | 5 | довжина ланцюжка переадресацій |
| `crawl.max_links_per_page` | 2000 | посилань зі сторінки до стратегій |
| `crawl.max_seed_urls` | 100 000 | початкових URL у запиті й `seed_list` |
| `crawl.max_frontier_size` | 100 000 | URL у черзі збору |
| `crawl.revisit_interval_seconds` | 86 400 | інтервал для `revisit.mode: interval` |
| `timeouts.connect_timeout_ms` | 10 000 | з'єднання |
| `timeouts.request_timeout_ms` | 30 000 | запит |
| `retries.max_attempts` | 3 | спроби запиту з повторюваним збоєм (429, 500, 502, 503, 504, мережа) |
| `retries.initial_backoff_ms`, `max_backoff_ms` | 1000, 60 000 | межі паузи між спробами |
| `retries.backoff_multiplier`, `jitter` | 2.0, `true` | зростання паузи й випадковий розкид |
| `queue.max_unacked_materials` | 500 | непідтверджених матеріалів у буфері; далі збір чекає (backpressure) |
| `transfer.inline_max_bytes` | 262 144 | більший матеріал іде транзитним blob |
| `transfer.transit_ttl_seconds` | 604 800 | термін життя транзитного blob |
| `transfer.job_retention_seconds` | 86 400 | скільки зберігаються завершені збори; потім `410` |
| `transfer.idempotency_ttl_seconds` | 86 400 | скільки пам'ятається `Idempotency-Key` |
| `collector.max_wait_ms` | 30 000 | верхня межа `wait_ms` у `/materials` |
| `collector.long_poll_interval_ms` | 100 | як часто довге опитування перевіряє буфер |
| `collector.backpressure_poll_ms` | 1000 | як часто збір на паузі перевіряє буфер |
| `collector.robots_cache_ttl_seconds` | 3600 | кеш `robots.txt` |
| `collector.robots_max_bytes` | 512 000 | більший `robots.txt` обрізається |
| `collector.max_retry_after_seconds` | 300 | довше очікування (`Retry-After`, `Crawl-delay`) — `rate_limited` |
| `collector.gc_interval_seconds` | 3600 | прибирання прострочених зборів і транзитних файлів |
| `collector.host_state_prune_interval_seconds` | 60 | прибирання стану неактивних хостів |
| `collector.shared_host_limits` | `true` | узгоджувати ліміти хоста з іншими екземплярами через `state.db` |
| `collector.shared_host_poll_ms` | 100 | як часто запит перевіряє чергу хоста |
| `collector.shared_host_ttl_seconds` | 120 | скільки записи зупиненого екземпляра обмежують інших |
| `collector.render_timeout_ms` | 30 000 | завантаження сторінки в браузері |
| `collector.render_extra_wait_ms` | 0 | додаткова пауза після умови очікування |
| `collector.render_max_pages` | 2 | сторінок у браузері одночасно на процес |
| `collector.render_max_transfer_bytes` | 50 МіБ | байтів, які браузер завантажує для однієї сторінки |
| `collector.render_launch_timeout_ms`, `render_close_timeout_ms` | 30 000, 30 000 | старт і закриття браузера |
| `jobs.max_concurrent_jobs` | 4 | зборів, що виконуються одночасно в екземплярі |
| `jobs.max_queued_jobs` | 1000 | понад це — `503 service_unavailable` |
| `jobs.job_timeout_ms` | 3 600 000 | межа часу збору; перевищення — `failed`, код `timeout` |
| `page.default_page_size`, `max_page_size` | 50, 500 | розмір сторінок `/materials`, `/errors`, `/v1/connections` |

Інтервал між стартами запитів до хоста — найбільше з `1 / requests_per_second_per_host`, `min_delay_ms_per_host` і `Crawl-delay`. Якщо хостом одночасно користуються збори з різними лімітами, діє найсуворіше значення.

## Успадкування лімітів

Порядок шарів (кожен наступний перевизначає попередній):

1. типові значення сервісу (таблиця вище);
2. файл профілю платформи `JANE_WEB_COLLECTOR_LIMITS_FILE` (формат `PlatformLimits`, наприклад [deploy/profiles/single-node.json](../../../deploy/profiles/single-node.json); ліміти інших сервісів ігноруються, невідомий шлях — помилка старту);
3. змінні `JANE_WEB_COLLECTOR_LIMITS__<ГРУПА>__<ПОЛЕ>`, наприклад `JANE_WEB_COLLECTOR_LIMITS__CRAWL__MAX_DEPTH=3`; `JANE_WEB_COLLECTOR_LIMITS__HARD_CAPS__<ГРУПА>__<ПОЛЕ>` задає жорстку межу;
4. `rules.limits` — рівень джерела;
5. `limits` запиту;
6. `strategies[].limits` — лише для URL цієї стратегії.

Жорсткі межі (`hard_caps`) обмежують результат будь-якого шару. Перевірено: з `..._LIMITS__HARD_CAPS__CRAWL__MAX_PAGES_PER_RUN=100` запит із `crawl.max_pages_per_run: 500` отримує ефективне значення 100. Неприпустимі ліміти запиту чи правил — `422 validation_failed` з текстом `invalid limits: ...`.
