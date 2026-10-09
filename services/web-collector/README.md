# Web Collector

Отримує вебсторінки та інші вебматеріали за правилами колектора й віддає їх як `Material` (ТЗ §3, §5, §6).
Автономний: працює без оркестратора, екстрактора, сервісу збереження й репозиторію (ТЗ §4, критерій 1).
Контракт: [`contracts/openapi/collector.v1.yaml`](../../contracts/openapi/collector.v1.yaml), правила —
[`collector-rules.schema.json`](../../contracts/schemas/collector-rules.schema.json), інтерфейс стратегій —
[`jane_contracts.discovery`](../../contracts/python/src/jane_contracts/discovery.py) і
[`contracts/docs/discovery-strategy.md`](../../contracts/docs/discovery-strategy.md).

Ядро (WP-02): завантаження, нормалізація URL, межі доменів і шляхів, `include`/`exclude`, `robots.txt` і явна
політика власника (`owner_policy`), черга з дедуплікацією та пріоритетами, глибина, повторні відвідування
(`revisit`, умовні запити), ліміти на хост, власне сховище стану й відновлення після kill, реєстр стратегій,
стратегії `seed_list` (явний перелік / головна сторінка) і `recursive`. Решту стратегій додає WP-03.

## Незалежний запуск

Без Docker (з кореня репозиторію):

```
uv sync --all-packages
uv run --package jane-web-collector python -m jane_web_collector
curl http://127.0.0.1:8101/v1/health
```

У Docker (контекст — корінь репозиторію; стан — у томі `/var/lib/jane-web-collector`):

```
docker build -f services/web-collector/Dockerfile -t jane-web-collector .
docker run --rm -p 8101:8101 -v jane-wc-state:/var/lib/jane-web-collector jane-web-collector
```

Правило конфігурації (перевіряється на старті, інакше сервіс не запускається):
`HEARTBEAT_INTERVAL_MS + STATE_BUSY_TIMEOUT_MS < LEASE_SECONDS × 1000` — живий власник завжди встигає продовжити
lease, навіть якщо один запис чекав на блокування весь busy timeout.

Кілька екземплярів: кожен процес має власний `JANE_WEB_COLLECTOR_PORT`. Екземпляри з **одним** каталогом стану на
одному вузлі ділять SQLite-файл: збір виконує той, хто тримає lease (`JANE_WEB_COLLECTOR_LEASE_SECONDS`), решта
віддає матеріали, стан і помилки з того самого сховища й підхоплює збір, якщо власник зник. Екземпляри з різними
каталогами — незалежні колектори. Якщо інший екземпляр тримає блокування `state.db` довше за
`STATE_BUSY_TIMEOUT_MS`, операція відповідає `503 service_unavailable` з `Retry-After` (описано в `collector.v1`);
повтор безпечний. Ліміти на хост екземпляри зі спільним каталогом узгоджують через те саме сховище (R15, див.
«Ліміти»). Job і ключі ідемпотентності — спільні сховища jane-kit (`jane_kit.stores.sqlite`, R17): job віддзеркалює
збір (пише лише власник lease збору, термінальний статус — лише за збором, job, скасований до старту, завершує й
збір), «захоплення» ключа має власника й оренду (`IDEMPOTENCY_LEASE_MS`); таблиці файла стану оновлюються на місці.
Політика `secret_refs` (`SECRET_ENV_PREFIX`, `SECRET_FILES_DIR`, читання файла через закріплені компоненти шляху),
схеми контракту й завантаження правил за `rules_ref`, запис транзитних blob і їх прибирання — теж спільні модулі
jane-kit (`secrets`, `rules`, `content`). Спільного сховища для кількох вузлів (PostgreSQL) у v1 немає — див. «Відомі
обмеження» у звіті WP-02.

## Тести

```
just test web-collector                 # unit + contract + сценарії проти testsite, ~2 хв
just test web-collector -m contract     # лише контрактні
```

Усі сценарії йдуть проти справжнього testsite (`jane_testsite`, WP-01) через HTTP; колектор не мокається.
Тест відновлення (`tests/test_resume_after_kill.py`) і тест автономності (`tests/test_autonomy.py`) запускають
сервіс окремим процесом (`python -m jane_web_collector`) і вбивають його жорстко (SIGKILL / TerminateProcess).
Мок сусіда — лише registry.v1 (`tests/test_rules_sources.py`), відповіді перевіряються за його контрактом.

Скільки тести чекають, задається змінними середовища (`jane_web_collector.testing`; це лише верхня межа
очікування, не умова проходження — на завантаженій машині її можна збільшити):

| Змінна | Типово | Що обмежує |
|---|---|---|
| `JANE_WEB_COLLECTOR_TEST_START_S` | 120 с | старт процесу колектора до `/v1/health` (`ServiceProcess.start`) |
| `JANE_WEB_COLLECTOR_TEST_WAIT_S` | 120 с | очікувану подію: кінець збору (`wait_done`), кінець потоку (`drain`), скасування, прогрес |

Тести, яким потрібна незавершена колекція (409 на `DELETE /v1/states/…`, скасування, перехоплення після kill),
утримують її через backpressure (`limits.queue.max_unacked_materials`), а не розраховують на повільний обхід.

## Конфігурація

Змінні середовища з префіксом `JANE_WEB_COLLECTOR_`:

| Змінна | Типово | Опис |
|---|---|---|
| `HOST` / `PORT` | `127.0.0.1` / `8101` (у контейнері `0.0.0.0`) | адреса прослуховування |
| `STATE_DIR` | `.jane/web-collector` (контейнер: `/var/lib/jane-web-collector`) | власне сховище стану (`state.db`, SQLite WAL) |
| `TRANSIT_DIR` | — | транзитне blob-сховище (`file://`) для великих матеріалів; без нього — лише inline |
| `RULES_DIR` | — | локальні пакети правил: `<package_id>/<version>/jane-package.json` + `rules.json` або архів `<package_id>-<version>.zip` |
| `REGISTRY_URL` | — | registry.v1 для `rules_ref` (після `RULES_DIR`) |
| `REGISTRY_TOKEN_ENV` | — | **ім'я** змінної середовища з bearer-токеном до registry (не значення) |
| `SECRET_ENV_PREFIX` | `JANE_SECRET_` | `secret_refs` типу `env:` читаються лише з цим префіксом; порожній вимикає `env:` |
| `SECRET_FILES_DIR` | `/run/secrets` | `secret_refs` типу `file:` читаються лише з цього каталогу після розв'язання `..` і symlink; порожній вимикає `file:` |
| `CONNECTION_ORIGIN_ALLOWLIST` | `[]` | JSON-масив точних HTTP(S) origin (`scheme://host[:port]`), яким дозволено надсилати облікові дані підключень; порожній список забороняє всі |
| `EGRESS_DENY_LINK_LOCAL` | `true` | не з'єднуватися з link-local адресами: `169.254.0.0/16` (метадані хмари `169.254.169.254`), `fe80::/10`, `fd00:ec2::254`; див. «Політика вихідних адрес» |
| `EGRESS_DENY_PRIVATE` | `false` | також не з'єднуватися з loopback, приватними й іншими не публічними адресами; типово вимкнено, бо testsite dev/e2e — у приватній мережі Docker |
| `CONTRACTS_DIR` | `JANE_CONTRACTS_DIR` або `contracts/` checkout | JSON Schema контрактів для валідації запитів і правил |
| `DISCOVERY_PATH` | `services/web-collector/strategies/discovery` | пакет стратегій WP-03 |
| `USER_AGENT` | `JaneBot/0.1 (+https://github.com/jane)` | типовий User-Agent; перше слово — токен для `robots.txt` |
| `LEASE_SECONDS` | `30` | lease збору; після нього інший екземпляр підхоплює збір |
| `HEARTBEAT_INTERVAL_MS` | `5000` | як часто власник продовжує lease (окрема задача, працює й під час seeds і повільних запитів) і перевіряє скасування |
| `STATE_BUSY_TIMEOUT_MS` | `10000` | скільки запис чекає на блокування SQLite іншим процесом |
| `IDEMPOTENCY_LEASE_MS` | `900000` | оренда «захоплення» `Idempotency-Key`: живий екземпляр поновлює свої в циклі відновлення, ключ убитого можна захопити після неї (а не після всього `transfer.idempotency_ttl_seconds`) |
| `LOG_LEVEL` / `LOG_FORMAT` | `INFO` / `json` | журнали |
| `METRICS_ENABLED` | `true` | `/metrics` |
| `AUTH_MODE` | `none` | `none` / `api_key` / `jwt` — див. «Автентифікація (ADR-0005)» |
| `LIMITS_FILE` | — | `PlatformLimits` (`profile`, `defaults`, `hard_caps`; TOML/JSON/YAML), напр. цілий `deploy/profiles/<профіль>.json`. Спільний шар jane-kit (R20): ліміти контракту, яких колектор не має (`sandbox`, `llm`, `telegram`…), ігноруються й перелічуються в стартовому журналі (`platform limits profile applied partially`); шлях, невідомий і контракту, і моделі (опечатка), — помилка старту |
| `LIMITS__<ГРУПА>__<ПАРАМЕТР>` / `LIMITS__HARD_CAPS__…` | — | перевизначення шляхами моделі (як у всіх сервісах), напр. `JANE_WEB_COLLECTOR_LIMITS__CRAWL__MAX_DEPTH=3`, `..._LIMITS__JOBS__JOB_RETENTION_SECONDS=600`; невідомий шлях — помилка старту |

## Автентифікація (ADR-0005)

Режими й усі змінні (`AUTH_MODE`, `API_KEYS`, `API_KEYS_FILE`, `JWT_*`, `METRICS_PUBLIC`) спільні для всіх сервісів: [jane-kit, «Автентифікація»](../../libs/jane-kit/README.md#автентифікація-adr-0005) і [docs/operations](../../docs/operations/README.md#автентифікація-adr-0005). `/v1/health` (і `/metrics`, доки `METRICS_PUBLIC=true`) працюють без токена; `/v1/info` приймає будь-який дійсний токен; решта потребує токена (401 `unauthenticated`) і scope операції (403 `forbidden`). `AUTH_MODE=none` — лише для локальних тестів на loopback; за неповної конфігурації `api_key`/`jwt` сервіс не стартує. JWT з реальним IdP **не перевірено на реальному сервісі** (лише локальний JWKS у тестах jane-kit).

Scopes операцій (таблиця `COLLECTOR` з `jane_kit.auth_scopes`):

- `collector:run` — `POST /v1/fetches`, `POST /v1/collections`, `DELETE /v1/states/{key}`, `POST /v1/jobs/{id}/cancel`; `collector:read` — `GET /v1/collections/{id}`, `…/materials`, `…/errors`, `GET /v1/states/{key}`, `GET /v1/jobs/{id}`; `POST /v1/rules/validations` — `collector:read` або `collector:run`; `GET /v1/connections…` — `connections:write` або `collector:read`; зміна й перевірка підключень — `connections:write`.

Власний токен колектора до registry — у змінній, яку називає `REGISTRY_TOKEN_ENV`; у dev-стеку `JANE_SECRET_WEB_COLLECTOR_TOKEN` (ключ ідентичності `web-collector`).

Приклад для `api_key` (зберігається лише хеш ключа):

```text
JANE_WEB_COLLECTOR_AUTH_MODE=api_key
JANE_WEB_COLLECTOR_API_KEYS=[{"name": "orchestrator", "sha256": "<sha256 hex ключа>", "scopes": ["collector:read", "collector:run", "connections:write"]},
  {"name": "ops", "secret_ref": "file:/run/secrets/jane-ops-key", "scopes": ["collector:read", "collector:run", "connections:write"]}]
```

## Ліміти

Рівні: типові значення сервісу → платформа (файл, потім змінні) → джерело (`rules.limits`) → запит
(`CollectionRequest.limits`, `FetchRequest.limits`) → стратегія (`strategies[].limits`, діє для URL цієї стратегії,
зокрема `crawl.max_depth`). `hard_caps` обмежують результат (`min`); `robots.txt` Crawl-delay і `Retry-After` лише
звужують. Ефективні ліміти збору — у `GET /v1/collections/{id}` → `effective_limits`; налаштовані —
у `GET /v1/info` → `limits`.

**Ліміти на хост спільні для платформи.** `concurrency.max_parallel_fetches_per_host`, `rate.requests_per_second_per_host`,
`rate.min_delay_ms_per_host`, `Crawl-delay` і `Retry-After` діють на хост (`host[:port]` URL) для **всіх** зборів і
одноразових `POST /v1/fetches` разом — у процесі (WP-02c) і між **екземплярами**, що ділять каталог стану (R15):
два збори одного сайту, хоч в одному процесі, хоч у двох репліках, разом роблять не більше запитів, ніж дозволяє
ліміт, а не вдвічі більше. Так `limits.schema.json` визначає область дії лімітів «на хост» (рівень platform).

- Правило для різних значень: діє **найсуворіше** значення серед активних на хості користувачів — найбільший
  інтервал між стартами запитів і найменша паралельність. Збір активний на хості від свого першого запиту до нього
  до завершення (успіх, помилка, скасування, передача lease іншому екземпляру); `POST /v1/fetches` — на час
  виклику. Отже повільний збір (наприклад, `rules.limits.rate` джерела з 0,2 rps) сповільнює до свого темпу й
  інші збори та fetch того самого хоста, поки він працює; після його завершення решта повертається до своїх значень.
  Синхронний `POST /v1/fetches` чекає на свою чергу до хоста без окремої межі (`collector.max_retry_after_seconds`
  обмежує лише `Retry-After` і `Crawl-delay`): поруч із повільним збором того самого хоста відповідь може йти
  кілька його інтервалів — клієнту потрібен відповідний тайм-аут.
- Інтервал користувача = `max(1 / requests_per_second_per_host, min_delay_ms_per_host)`, а за
  `respect_crawl_delay` — і `Crawl-delay` з `robots.txt` (побачений одного разу, діє до завершення збору).
- `Retry-After` від джерела затримує всіх користувачів хоста (не лише збір, що отримав 429/503).
- `POST /v1/fetches` бере ліміти на хост з власних ефективних лімітів (платформа → `rules.limits` → `limits`
  запиту), як і збір (до WP-02c темп і паралельність на хост для fetch бралися лише з платформних значень).
- Очікування слоту чи черги на хост не блокує скасування: запит, скасований під час очікування, нічого не
  резервує в розкладі хоста. Стан хоста, яким ніхто не користується, прибирається
  (`collector.host_state_prune_interval_seconds` і під час завершення збору).
- **Між екземплярами** (R15, [`shared_hosts.py`](src/jane_web_collector/shared_hosts.py)): у спільному `state.db`
  кожен екземпляр реєструє на хості свої найсуворіші значення (`host_users`); запит, що пройшов інтервал свого
  процесу, стає в чергу хоста (FIFO між екземплярами, `host_waiters`) і бере слот платформи (`host_slots`, не більше
  найменшого зареєстрованого `max_parallel_fetches_per_host`) лише тоді, коли може стартувати одразу: минув
  найбільший зареєстрований інтервал від попереднього старту будь-якого екземпляра і `Retry-After` (`host_schedule`).
  Перший у черзі чекає старту **без** слота, тож слот тримається лише на час запиту. Живий екземпляр поновлює свої
  реєстрації, слоти й місця в черзі кожні `shared_host_ttl_seconds / 3` — також під час довгого завантаження,
  `Retry-After` до `collector.max_retry_after_seconds` чи `Crawl-delay`, довшого за TTL; лише вбитий екземпляр
  перестає їх поновлювати, і вони спливають через `collector.shared_host_ttl_seconds` (рев'ю 1). Зайняте сховище
  не валить запит — він чекає й пробує знову. Екземпляри з **різними** каталогами стану — окремі колектори, вони ліміти не узгоджують (спільного сховища
  між вузлами у v1 немає, ADR-0007). Вимкнути узгодження — `collector.shared_host_limits=false`.

| Параметр | Типово | Опис |
|---|---|---|
| `concurrency.max_parallel_fetches` | 4 | одночасні завантаження одного збору |
| `concurrency.max_parallel_fetches_per_host` | 2 | одночасні запити до одного хоста (усі збори й fetch усіх екземплярів зі спільним сховищем разом) |
| `rate.requests_per_second_per_host` | 1 | частота запитів до хоста (так само) |
| `rate.min_delay_ms_per_host` | 500 | мінімальний інтервал між стартами запитів до хоста (так само) |
| `rate.respect_crawl_delay` | true | враховувати `Crawl-delay` |
| `crawl.max_depth` | 5 | глибина від seeds |
| `crawl.max_pages_per_run` | 5000 | запитів за збір |
| `crawl.max_bytes_per_run` | 2 GiB | байтів за збір |
| `crawl.max_material_bytes` | 10 MiB | більший вміст обрізається з діагностикою `truncated` |
| `crawl.max_redirects` | 5 | переадресацій на URL |
| `crawl.max_links_per_page` | 2000 | кандидатів зі сторінки (на стратегію) |
| `crawl.max_seed_urls` | 100000 | явних URL у запиті й `seed_list` |
| `crawl.max_frontier_size` | 100000 | URL у черзі |
| `crawl.revisit_interval_seconds` | 86400 | для `revisit.mode=interval` |
| `timeouts.connect_timeout_ms` / `request_timeout_ms` | 10000 / 30000 | тайм-аути HTTP |
| `retries.*` | 3 спроби, 1000–60000 мс, ×2, jitter | повтори на 429/5xx/мережі |
| `queue.max_unacked_materials` | 500 | буфер непідтверджених матеріалів; понад — пауза (backpressure) |
| `transfer.inline_max_bytes` | 262144 | більше — blob (або `limit_exceeded` без blob-сховища) |
| `transfer.transit_ttl_seconds` | 604800 | час життя транзитних файлів |
| `jobs.job_retention_seconds` (у контракті, файлі й запиті — `transfer.job_retention_seconds`) | 86400 | після цього збір видаляється (далі 410) |
| `idempotency.idempotency_ttl_seconds` (у контракті — `transfer.idempotency_ttl_seconds`) | 86400 | пам'ять `Idempotency-Key` |
| `jobs.max_concurrent_jobs` / `max_queued_jobs` | 4 / 1000 | зборів одночасно / у черзі на екземпляр |
| `jobs.job_timeout_ms` | 3600000 | максимальна тривалість збору |
| `page.default_page_size` / `max_page_size` | 50 / 500 | сторінки `/materials`, `/errors`, `/connections` |
| `collector.max_wait_ms` | 30000 | стеля long-poll `wait_ms` |
| `collector.robots_cache_ttl_seconds` / `robots_max_bytes` | 3600 / 512000 | кеш і розмір `robots.txt` |
| `collector.max_retry_after_seconds` | 300 | довше очікування (Retry-After, Crawl-delay) → `rate_limited` |
| `collector.backpressure_poll_ms` | 1000 | як часто перевіряється буфер під час паузи backpressure |
| `collector.long_poll_interval_ms` | 100 | як часто `/materials?wait_ms=` шукає нові матеріали |
| `collector.gc_interval_seconds` | 3600 | прибирання прострочених зборів і транзитних файлів (не рідше `job_retention_seconds / 10`) |
| `collector.host_state_prune_interval_seconds` | 60 | як часто спільний лімітер хостів прибирає стан хостів, якими ніхто не користується |
| `collector.shared_host_limits` | true | узгоджувати ліміти на хост з іншими екземплярами через спільне сховище стану (R15) |
| `collector.shared_host_poll_ms` | 100 | як часто запит, що чекає слоту хоста, зайнятого іншими екземплярами, перевіряє його знову |
| `collector.shared_host_ttl_seconds` | 120 | скільки реєстрація, слот і місце в черзі вбитого екземпляра ще обмежують інших; живий екземпляр поновлює їх кожні TTL/3, тож TTL не мусить перевищувати запити чи очікування. Правило старту: `TTL × 2/3 > STATE_BUSY_TIMEOUT_MS`, інакше сервіс не стартує |

## Поведінка

- **Межі**: кожен кандидат нормалізується (`normalization`) і перевіряється за `scope` (схеми, домени,
  піддомени, `path_prefixes`, `include`, `exclude` — виключення мають пріоритет); кожен крок переадресації
  перевіряється знову. `mailto:`, `tel:`, `javascript:` відкидаються. Адреси призначення після DNS — за
  [політикою вихідних адрес](#політика-вихідних-адрес).
- **robots.txt**: RFC 9309 (групи за токеном, `*`/`$`, найдовший збіг, 4xx → дозволено, 5xx/мережа → заборонено),
  кешується на збір. `robots.mode=owner_policy` (з `confirmed_owner` і обґрунтуванням у правилах) — явна політика
  для власного ресурсу: `robots.txt` не читається.
- **Дедуплікація й цикли**: ключ черги — канонічний URL; переадресація на вже відомий URL не завантажується вдруге;
  `<link rel=canonical>` (якщо `dedup.use_link_rel_canonical`) теж зводить дублікати. `dedup.key=canonical_url_and_content`
  видає матеріал лише за зміни вмісту відносно попереднього спостереження.
- **Пріоритет** = перший збіг `priorities` + `priority` стратегії + `priority` кандидата; `sections` → `discovery.section`.
- **Повторні відвідування** (історія URL у просторі `state_key`): `mode=full` — усе завантажується наново (нові
  спостереження); `mode=incremental` + `revisit.mode=never` — відомі успішні URL не завантажуються (їхні збережені
  посилання продовжують обхід), `interval` — лише старші за `revisit_interval_seconds`, `if_changed` — умовні
  запити (ETag / If-Modified-Since), 304 не видається. URL, що минулого разу впали (4xx/5xx), пробуються знову.
  `lastmod` кандидата (sitemap з `use_lastmod_for_revisit`, стрічка, `api_feed` з `lastmod_path`), пізніший за
  попереднє завантаження URL, змушує завантажити його попри `never`/`interval` (лічильник `revisited_by_lastmod`);
  старіший чи відсутній `lastmod` нічого не забороняє (R23). Навігаційні документи стратегій і сторінки списків
  `listing` (хук `RefreshingStrategy`) читаються повністю в кожному зборі — без пропуску й без умовного запиту
  (лічильник `refreshed`), тож нові елементи відомих категорій знаходяться в `incremental`.
- **Тайм-аути** `timeouts.connect_timeout_ms` / `request_timeout_ms` застосовуються до кожного запиту з ефективних
  лімітів збору (з урахуванням `rules.limits`, `limits` запиту і `limits` стратегії), а не з платформних типових.
- **Видача**: `GET /v1/collections/{id}/materials?after=<cursor>` підтверджує все до курсора включно
  (курсор, якого сервіс не видавав, — 422);
  непідтверджене видається повторно з тим самим `observation_id`. Коли непідтверджених ≥ `max_unacked_materials`,
  обхід стає на паузу (`paused_by_backpressure: true`). Паралельні HTTP-запити можуть уже завершуватися,
  але запис матеріалу чекає на вільне місце: непідтверджених у буфері не буває більше за ліміт.
- **Відновлення**: кожна сторінка фіксується однією транзакцією (нові URL, статус, матеріал, історія, стан стратегій,
  статистика) і перевіряє, що цей прогін досі тримає lease (fencing): прогін, у якого lease перехопили (процес
«завис» довше за lease), не може записати нічого й зупиняється, а його Job не перезаписує Job нового власника.
Після kill новий процес (або інший екземпляр після lease) повертає незавершені URL у чергу й продовжує; перед
завершенням `inflight`, що лишились від чужого прогону, теж повертаються в чергу — `succeeded` неможливий, поки є
`pending`/`inflight`;
  повторно завантажуються лише URL, що були в польоті.
- **`llm_explore`**: валідна за схемою, але колектор її не виконує (ADR-0010): `supported: false`, збір — `validation_failed`.
- **Підключення** (`/v1/connections`, лише `kind=http`): `params.auth_scheme` = `bearer` (`secret_refs.token`),
  `basic` (`username`, `password`) або `header` (`params.header_name`, `secret_refs.value`); секрети — лише дозволені
  `env:`/`file:` у середовищі колектора, у `params` відхиляються (`secret_detected`). Для автентифікованого збору
  оператор задає `JANE_WEB_COLLECTOR_CONNECTION_ORIGIN_ALLOWLIST='["https://shop.example.test"]'`.
  Облікові дані не йдуть на інший origin або при переході з HTTPS на HTTP. `rules.fetch.headers` приймає лише
  `Accept`, `Accept-Language` і `Cache-Control`; для `X-Client-Key` та інших облікових заголовків використовується
  кероване підключення (`auth_scheme=header`) з дозволеним origin. Значення секрету з керівними символами або
  поза видимим ASCII відхиляється до HTTP-запиту; повідомлення про транспортні помилки не містять значень
  заголовків.

## Політика вихідних адрес

Захист від SSRF: `POST /v1/fetches` чи збір не можуть стати проксі до сервісу метаданих хмари або внутрішніх
сервісів. Кожне TCP-з'єднання HTTP-клієнта колектора ([`egress.py`](src/jane_web_collector/egress.py)):

1. ім'я хоста розв'язується один раз (`getaddrinfo`);
2. перевіряється **кожна** отримана адреса — одна заборонена адреса забороняє хост;
3. з'єднання відкривається саме з перевіреною адресою (TLS і далі перевіряє ім'я хоста), тож відповідь DNS, що
   змінилась між перевіркою і з'єднанням (DNS rebinding), політику не обходить.

Перевірка стоїть на рівні з'єднання, тому діє для першого запиту, **кожного кроку переадресації** (крок спершу
проходить `scope` і `robots.txt`, потім — політику адрес), `robots.txt`, sitemap і запитів стратегій.

| Налаштування | Типово | Що забороняє |
|---|---|---|
| `JANE_WEB_COLLECTOR_EGRESS_DENY_LINK_LOCAL` | `true` | `169.254.0.0/16`, `fe80::/10`, `fd00:ec2::254` (метадані AWS IPv6) |
| `JANE_WEB_COLLECTOR_EGRESS_DENY_PRIVATE` | `false` | усе, що не є глобально маршрутизованим: loopback, RFC 1918, `fc00::/7`, CGNAT `100.64.0.0/10`, `0.0.0.0/8`, документаційні й зарезервовані діапазони, multicast |

IPv4, вкладена в IPv6 (`::ffff:a.b.c.d`, NAT64 `64:ff9b::/96`, 6to4 `2002::/16`), перевіряється як та IPv4.
У продуктивному розгортанні, де джерела — лише публічні сайти, увімкніть `EGRESS_DENY_PRIVATE=true`; у dev/e2e
він вимкнений, бо testsite і сервіси Jane — у приватній мережі Docker.

Відмова — `access_denied_by_policy` (не повторюється): `POST /v1/fetches` → `403` problem, у тексті адреса й
`egress policy`; у зборі — помилка URL у `GET /v1/collections/{id}/errors` (`code: access_denied_by_policy`), матеріал
не видається, збір продовжується з рештою URL. Без `robots.mode=owner_policy` заборонена адреса зазвичай відсіюється
ще раніше: її `robots.txt` теж не завантажується, і за RFC 9309 недоступний `robots.txt` означає заборону.

## Підключення стратегій (WP-03)

Реєстр (`jane_web_collector.discovery.Registry`) збирає стратегії з трьох джерел; повторне `type_name` — помилка:

1. вбудовані: `seed_list`, `recursive`;
2. **пакет WP-03** — каталог `services/web-collector/strategies/discovery/` (інший — `JANE_WEB_COLLECTOR_DISCOVERY_PATH`).
   Ядро імпортує його як пакет `jane_web_collector_discovery` (відносні імпорти всередині працюють) і реєструє
   `STRATEGIES: list[type[DiscoveryStrategy]]` з `__init__.py`. Помилка імпорту не валить сервіс: вона видна в
   журналі й у `/v1/info` → `capabilities.strategy_load_errors`. Docker-образ копіює каталог у `/app/strategies`;
3. entry points групи `jane.web_collector.strategies` (клас або список класів) — для пакетів, встановлених поруч.

Що дає ядро стратегії (`StrategyContext`, реалізує `DiscoveryContext`):

- `ctx.fetch(url, kind=..., conditional=True, method="GET", body=None)` — через ті самі scope, robots, політику
  адрес, ліміти на хост (спільні з усіма зборами, fetch і екземплярами зі спільним сховищем), повтори,
  переадресації, розмір і бюджет збору; тайм-аути — з `limits` стратегії (повна таблиця — в
  [`discovery-strategy.md`](../../contracts/docs/discovery-strategy.md), R03). Повертає `FetchedResource` з будь-яким
  кінцевим статусом, крім 304 (зокрема 4xx — корисно для `url_template`); `None` — 304, URL уже отримано в цьому
  процесі для збору або вже виданий матеріал, переадресація на відомий URL, збій після повторів (помилка — в
  `/errors`); `FetchRejected` — `out_of_scope`, `access_denied_by_policy` (robots, політика адрес),
  `limit_exceeded` (бюджет), `rate_limited` (джерело просить чекати довше за `collector.max_retry_after_seconds`
  або 429 після повторів). `method="POST"` з JSON `body` — лише для `kind="navigation"` (сторінки API, R22).
  Ресурс, отриманий через `ctx.fetch`, передається в `on_fetched` усіх **інших** стратегій. Навігаційні документи
  після рестарту можна отримати знову (стан — у `snapshot()`).
- `await ctx.emit_material(DiscoveredMaterial(...))` — вміст, який стратегія вже має (елемент JSON API), стає
  Material за правилами сторінки: scope, глибина, один матеріал на канонічний URL у зборі, `revisit`/`dedup`,
  backpressure (R22).
- `on_fetched` викликається для кожної HTTP-відповіді з тілом, хай який статус (2xx, 4xx, 5xx без повторів;
  `resource.strategy_id` — хто запропонував URL), але не для 304, пропущених `revisit`, дублікатів і збоїв.
  Кандидати з `on_fetched` отримують `depth = resource.depth + 1`.
- Необов'язковий хук `refresh_on_revisit(url) -> bool` (`RefreshingStrategy`): сторінка, з якої стратегія бере нові
  матеріали, читається повністю в кожному зборі (так робить `listing`, R23).
- `ctx.extract_links(resource, LinkSelector(...))` — css / xpath / rel через lxml (залежності `lxml`, `cssselect`
  уже є); `ctx.normalize`, `ctx.in_scope`, `ctx.section_for`, `ctx.limits` (ефективні, з `limits` стратегії),
  `ctx.is_cancelled()`.
- `snapshot()` зберігається після кожної сторінки разом із чергою; `restore()` — при відновленні. Непорожні
  знімки також видно в `GET /v1/states/{state_key}` → `cursors`.

Тести WP-03 можуть узяти пакет так само, як ядро: `load_discovery_package(path)` з
`jane_web_collector.discovery`, і допоміжні засоби `jane_web_collector.testing` (`web_rules`, `start`, `drain`,
`FAST_LIMITS`, `make_settings`). Приклад плагіна — `tests/test_registry.py`. Нові залежності для стратегій
додаються в `pyproject.toml` сервісу — це область WP-02 (запит через координатора).

## Приклад виклику зі стороннього застосунку

```python
import httpx

rules = {
    "collector": "web",
    "scope": {"allowed_domains": ["shop.example.test"], "exclude": [{"value": "*/calendar/**"}]},
    "strategies": [{"type": "seed_list", "urls": ["https://shop.example.test/"]}, {"type": "recursive"}],
    "normalization": {"strip_query_params": ["utm_*"]},
}
with httpx.Client(base_url="http://127.0.0.1:8101") as api:
    job = api.post(
        "/v1/collections",
        json={"source_kind": "web", "source_id": "shop", "rules": rules},
        headers={"Idempotency-Key": "shop-crawl-1"},
    ).json()
    after = None
    while True:
        page = api.get(
            f"/v1/collections/{job['job_id']}/materials",
            params={"wait_ms": 5000, **({"after": after} if after else {})},
        ).json()
        for material in page["items"]:
            print(material["locator"]["canonical_url"], material["content"]["kind"])
        after = page["next_cursor"] or after  # наступний запит підтверджує оброблене
        if page["end_of_stream"]:
            break
```

Одна сторінка синхронно: `POST /v1/fetches {"source_kind": "web", "url": "https://shop.example.test/about"}`.
Сторінка, якої на сайті немає (HTTP 404 або 410), — `404 not_found` з `details.http_status` (`retryable: false`), як
`not_found` у `/errors` збору; інші помилки сайту — `502 source_unavailable` з `details.http_status`.

## Спостережуваність

- `GET /v1/health` (перевірка `state_store`), `GET /v1/info` (стратегії, джерела правил, ліміти).
- `GET /metrics` — Prometheus (`jane_http_requests_total`, `jane_http_request_duration_seconds`).
- Журнали — JSON у stdout із `trace_id`, `job_id`; прогрес збору — `GET /v1/jobs/{id}` → `progress.counters`
  (зокрема `skipped_depth`, `dropped_frontier_full`, `dropped_by_budget`).
