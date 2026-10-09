# Асистент джерел (assistant)

Сервіс WP-11. Підключає нове джерело за назвою чи посиланням (пошук, уточнення, адаптивна вибірка,
аналіз, варіанти збору, пошук/перевірка/форк/створення екстракторів), вдосконалює екстрактори на
проблемних прикладах (нова версія або форк, тести на всіх прив'язках, погодження чи автоактивація з
відкатом) і аналізує невідомі матеріали — лише за увімкненим прапорцем «Передавати в LLM невідомі
сторінки». Контракт: `contracts/openapi/assistant.v1.yaml` (конвенції — скіл `jane-contracts`).

Асистент не має власних даних-результатів: пакети живуть у registry, джерела й завдання — в оркестраторі.
Сусіди (усе — за їхніми контрактами):

| Сусід | Навіщо | Операції |
|---|---|---|
| llm (`llm.v1`) | класифікація, аналіз, варіанти, код | `createCompletion` |
| collector web/telegram (`collector.v1`) | вибірка, перевірка правил | `startCollection`, `listCollectionMaterials`, `getCollection`, `cancelJob`, `validateRules` |
| registry (`registry.v1`) | пошук, форк, публікація, статуси, звіти тестів | `listPackages`, `getPackage`, `downloadPackageArchive`, `createPackage`, `publishPackageVersion`, `forkPackage`, `recordTestResults`, `setPackageVersionStatus` |
| handler-runtime (`handler.v1`) | тести без запису (чернетки — inline-архівом) | `startTestRun` |
| orchestrator (`orchestrator.v1`) | прив'язки спільного пакета, активація/відкат, групи проблем, створення джерела й завдання | `listTasks?package_id=`, `getTask`, `activateStageVersion`, `updateProblemGroup`, `createSource`, `createTask`, `getSource` |
| storage (`storage.v1`) | вміст `material_ref` проблемних прикладів | `getObject`, `getObjectContent` |

Не налаштований сусід → job завершується `failed` з кодом `upstream_unavailable` (без здогадок).

## Як працює

**Підключення** (`POST /v1/onboarding-sessions` → 202 Job; `labels.session_id` і `links.session` — адреса сесії):

1. URL, `@channel` або `t.me/…` — беруться як є; назва йде в пошуковий провайдер. Явний лідер
   (`onboarding.auto_select_confidence` і відрив `auto_select_margin`) обирається сам, інакше
   `needs_disambiguation` → `POST …/candidate-selection`.
2. Адаптивна вибірка: звичайний збір колектора (sitemap + стрічки + рекурсія від входу; для Telegram —
   історія), з кожної порції беруться найменш представлені «форми» URL, їх класифікує дешева модель.
   Впевненість = `(1 − max(частка рідкісних типів серед класифікованих, ризик невідомого типу)) ×`
   середня впевненість моделі. Рідкісний тип має менше `min_examples_per_type` прикладів.
   Ризик для невибраних матеріалів оцінюється як мінімум їхньої частки в отриманому потоці та
   `1 − (1 − рівень_довіри)^(1 / кількість_класифікованих)`. Якщо спостережених типів менше за
   `min_distinct_types`, рівень довіри до відсутності нових типів посилюється. Це адаптивна
   статистична оцінка, а не гарантія повноти: невідомий тип із малою часткою може лишитися
   невибраним. Після першої порції асистент продовжує читати обмежений
   `fetch_ratio × max_onboarding_samples` потік, класифікує нові форми URL, а після завершення
   бере також матеріали з кінця вже відомих форм, щоб не покладатися лише на ранній порядок
   обходу. Додаткові порції вибираються лише до порога `min_confidence`; для 100 матеріалів не
   потрібно класифікувати всі 100. Достатність вимагає завершеного потоку й представлених у
   вибірці форм URL. Якщо потік не завершився до межі очікування, вичерпались вибірка чи бюджет —
   `insufficient_sample` з поясненням. Збір колектора після цього скасовується.
3. Аналіз: типи матеріалів, сутності, поля, способи обходу (лише реальні стратегії, без `llm_explore` — ADR-0010).
4. Для кожного очікуваного типу сутності: пошук екстракторів у registry (за доменом і загалом), прогін
   на зразках через handler-runtime; частка успіхів ≥ `bind_threshold` → прив'язка, ≥ `fork_threshold`
   → форк з адаптацією, інакше генерація нового пакета (маніфест будує асистент, модель дає код, схему
   й очікування; код перевіряється статично, пакет — тестами `success` + `empty|unrecognized`).
5. Кілька варіантів правил з оцінкою охоплення (`estimated_materials`), вартості
   (`requests_per_run_estimate`, `llm_setup_cost`, `llm_cost_per_run`) і ризиків. Кожен варіант проходить
   захист (див. нижче), JSON Schema і `validateRules` колектора.
6. `POST …/proposals/{id}/acceptance` → 202: публікація правил і пакетів (`draft`), звіти тестів, чернетки
   Source і TaskConfig. `activate: true` (або `auto_activation` у запиті — тоді рекомендований варіант
   приймається сам) і всі тести зелені → версії погоджуються, джерело й завдання створюються в оркестраторі.

**Вдосконалення** (`POST /v1/improvement-runs` → 202; `Job.result` = `ImprovementResult`):
групування проблем за джерелом і характером (сигнатура `unrecognized`, вид збою, коди діагностики) →
модель отримує групи, код, схеми, діагностику, успішні приклади → кандидат проходить старі тести, нові
тести з проблемних прикладів (`origin: problem_sample`), регресії на успішних прикладах і тести з
параметрами кожної прив'язки (`listTasks?package_id=` + `getTask`). Ламає прив'язки інших джерел або
несумісно змінює схему спільного пакета → форк для цього джерела (`policy.allow_fork`), інакше
`unresolved`. `auto_changes_allowed = false` → `proposal_only`, нічого не публікується.
`policy.approval = auto_after_checks` → погодження й `auto_activate` на всіх цільових прив'язках; якщо
оркестратор відмовив на одній — уже активовані відкочуються (`kind: rollback`). Стан групи проблем
(`in_progress` → `resolved` / `unresolved` з поясненням) оновлюється в оркестраторі — так невирішене видно
в адмінці. Нові типи сутностей лише пропонуються (`suggested_entity_types`).

**Невідомі матеріали** (`POST /v1/unknown-materials`): `forward_unknown_to_llm = false` → 403
`access_denied_by_policy` без жодного виклику LLM; інакше класифікація й пропозиція
(`new_extractor`, `extend_rules`, `expand_entity_types`, `none`).

**Вміст джерел — дані, не інструкції.** Інструкції моделі — сталі тексти (`prompts.py`); вміст сторінок,
код і діагностика — лише в `data`. Вихід моделі не довіряється: правила обмежуються хостами джерела
(плюс домени, які дозволив *користувач* у `crawl_hints`), `robots` завжди `respect`, без `llm_explore` і
лімітів у правилах; код без заборонених імпортів і викликів; маніфест за схемою. Відхилене видно в
`risks` варіанту.

## Незалежний запуск

Без Docker (з кореня репозиторію):

```
uv sync --all-packages
JANE_ASSISTANT_LLM_URL=http://127.0.0.1:8110 JANE_ASSISTANT_REGISTRY_URL=http://127.0.0.1:8105 \
JANE_ASSISTANT_COLLECTOR_WEB_URL=http://127.0.0.1:8101 JANE_ASSISTANT_HANDLER_RUNTIME_URL=http://127.0.0.1:8106 \
uv run --package jane-assistant python -m jane_assistant
curl http://127.0.0.1:8000/v1/health
```

Проти моків сусідів із контрактів: `uv run contracts/tools/mock.py <api> --port <порт>` для кожного сусіда.

У Docker (контекст збірки — корінь репозиторію; образ містить `contracts/schemas` для локальної валідації):

```
docker build -f services/assistant/Dockerfile -t jane-assistant .
docker run --rm -p 8000:8000 -e JANE_ASSISTANT_LLM_URL=http://llm:8000 jane-assistant
```

### Кілька екземплярів

Задайте `JANE_ASSISTANT_STATE_DSN` (PostgreSQL, власна схема `JANE_ASSISTANT_STATE_SCHEMA`, типово
`jane_assistant`; таблиці створюються самі) і унікальний `JANE_ASSISTANT_INSTANCE_ID` кожному екземпляру
(типово — `hostname-pid`). Тоді сесії підключення, job і ключі ідемпотентності спільні
(`state.py`: `PostgresState`):

- будь-який екземпляр читає й продовжує сесію чи job іншого (`selectCandidate`, `acceptProposal`, `GET /v1/jobs`);
  повтор `Idempotency-Key` на іншому екземплярі повертає збережену відповідь;
- переходи стану сесії з API — з оптимістичною версією (`UPDATE … WHERE version = …`): з двох одночасних
  виборів кандидата чи прийнять виграє один, інший отримує 409;
- job належить екземпляру, що його виконує, і тримає оренду (`limits.state.job_lease_ms`), яку той поновлює
  кожні `heartbeat_interval_ms`. Екземпляр убито → після закінчення оренди будь-який інший позначає job
  `failed` (`service_unavailable`, «instance … stopped …»), сесію — теж; завершений job більше не змінюється.
  Типовий `instance_id` створюється заново для кожного запуску процесу, навіть якщо hostname і PID повторилися;
  явно заданий `JANE_ASSISTANT_INSTANCE_ID` має бути унікальним для кожного одночасного екземпляра.
  Штатна зупинка → job `cancelled` з `cancellation.reason` «instance … shut down», сесія — `cancelled` з причиною;
- `/v1/health` перевіряє `state`, `/v1/info` → `capabilities.state` = `postgresql`.

Без `STATE_DSN` стан у пам'яті (`InMemoryState`) — лише для одиночного запуску й тестів; після рестарту
сесії й job зникають.

## Тести

```
just test assistant                  # unit + наскрізні сценарії + контрактні (одна команда)
just test assistant -m contract      # лише контрактні
just up --project jane-wp11 postgres # спільний стан: кілька екземплярів на одній БД
JANE_STACK_FILE=.jane/stack-jane-wp11.json just test assistant -m integration   # або JANE_WP11_STATE_DSN=<dsn>
just down -v --project jane-wp11
```

`tests/test_state.py` (інтеграційні): сесію з A продовжує B, повтор ключа на B, одночасний вибір на двох
екземплярах, штатний рестарт (job `cancelled` з причиною), «убитий» екземпляр (job `failed` іншим екземпляром).

Сценарії (`tests/test_onboarding.py`, `test_improvement.py`, `test_unknown.py`) запускають справжній
застосунок асистента; сусіди — фейки, прив'язані до контрактів (`tests/assistant_fakes`): кожен запит
асистента перевіряється за схемою запиту сусіда, кожна відповідь фейка — за схемою відповіді; порушення
валять тест. Фейкова LLM детермінована (диспетчеризація за `output_schema.title`), може «піддатись
ін'єкції», щоб перевірити захист. Тести пакетів справді виконуються (мінімальний замінник runtime).

`tests/test_llm_budget.py` — бюджет і довгі виклики LLM проти **справжнього** шлюзу `jane_llm` (fake-провайдер,
пам'ять): бюджет `run` рахується за `scope.run_id` через кілька сесій одного запуску, `amount: 0` зупиняє і асистента,
і шлюз, режим `async` чекає job шлюзу; виклик, довший за `clients.request_timeout_ms`, завершується в межах
`llm_call.request_timeout_ms` (контрактний фейк шлюзу на uvicorn, справжній HTTP).

Скільки тести чекають, задається змінними середовища (це лише верхня межа очікування, не умова проходження;
на завантаженій машині її можна збільшити): `JANE_ASSISTANT_TEST_START_S` (типово 120 с) — старт процесу
асистента й фейкових серверів у `tests/test_process_e2e.py`, `JANE_ASSISTANT_TEST_WAIT_S` (типово 120 с) —
завершення job.

## Конфігурація

**Політика вмісту матеріалів (ContentRef, WP-01h).** Матеріал приходить у запиті (`/v1/unknown-materials`,
`problem_samples`/`successful_examples` вдосконалення) або від колектора (вибірка онбордингу), тож його вміст
читається спільним `jane_kit.content.ContentReader`: `inline` (utf-8/base64); `download_url` — лише `http(s)` на хост
із `JANE_ASSISTANT_DOWNLOAD_HOST_ALLOWLIST`, без редиректів, без проксі й `.netrc` із середовища, лише незакодоване
тіло, обрізання на `content.max_material_bytes`, усе завантаження — у межах `content.fetch_timeout_ms`; `file://` —
лише строго всередині `JANE_ASSISTANT_BLOB_ROOTS` (шлях спершу розв'язується з `..` і symlink, читається саме
розв'язаний звичайний файл); `s3://` без `download_url` — 422. Перевіряються `size_bytes` blob і `sha256`. Відмова
завершує job помилкою (`validation_failed` / `limit_exceeded` — 422, `not_found` — 404, `upstream_unavailable` — 502)
без шляхів і вмісту в `detail`, до LLM нічого не йде. Застосунок ставить свій читач для кожного запиту
(`content.MaterialContentScope`), тож його успадковують і job, які запит запускає; поза застосунком
`material_bytes` читає лише inline. Збережений RAW зі storage асистент і так отримує inline (`/v1/objects/{id}/content`).
Тести: `tests/test_content_policy.py`, `test_improvement.py::test_problem_sample_content_follows_the_content_policy`.

Змінні середовища з префіксом `JANE_ASSISTANT_`:

| Змінна | Типово | Опис |
|---|---|---|
| `HOST` / `PORT` | `127.0.0.1` / `8000` (у контейнері `0.0.0.0`) | адреса прослуховування |
| `LOG_LEVEL` / `LOG_FORMAT` | `INFO` / `json` | журнали (JSON у stdout) |
| `METRICS_ENABLED` | `true` | `/metrics` (Prometheus) |
| `HEALTH_CHECK_TIMEOUT_MS` | `2000` | тайм-аут перевірок `/v1/health` |
| `AUTH_MODE` | `none` | `none` / `api_key` / `jwt` — див. «Автентифікація (ADR-0005)» |
| `LLM_URL`, `REGISTRY_URL`, `COLLECTOR_WEB_URL`, `COLLECTOR_TELEGRAM_URL`, `HANDLER_RUNTIME_URL`, `ORCHESTRATOR_URL`, `STORAGE_URL` | — | адреси сусідів |
| `SERVICE_TOKEN_REF` | — | `env:VAR` / `file:/path` власного токена асистента для всіх сусідів (ADR-0005 §5) |
| `LLM_TOKEN_REF`, `REGISTRY_TOKEN_REF`, `COLLECTOR_WEB_TOKEN_REF`, `COLLECTOR_TELEGRAM_TOKEN_REF`, `HANDLER_RUNTIME_TOKEN_REF`, `ORCHESTRATOR_TOKEN_REF`, `STORAGE_TOKEN_REF` | — | окремий токен конкретного сусіда (перекриває `SERVICE_TOKEN_REF`); нерозв'язне посилання — сервіс не стартує |
| `SERVICE_TOKEN_ENV` | — | застаріле: **ім'я** змінної з токеном для всіх сусідів; замість нього `SERVICE_TOKEN_REF=env:<ім'я>` |
| `SEARCH_PROVIDER` | `none` | `none`, `static`, `http_json` |
| `SEARCH_STATIC_FILE` | — | JSON `[{"title","url"?,"telegram_username"?,"description"?,"aliases"?}]` |
| `SEARCH_URL_TEMPLATE`, `SEARCH_ITEMS_PATH`, `SEARCH_TITLE_FIELD`, `SEARCH_URL_FIELD`, `SEARCH_DESCRIPTION_FIELD` | —, `results`, `title`, `url`, `description` | HTTP-пошук з JSON-відповіддю (тайм-аути — `limits.search`) |
| `BLOB_ROOTS` | `[]` (вимкнено) | каталоги, з яких можна читати `file://` вміст матеріалів (JSON-список); порожньо — `file://` відхиляється (422) |
| `DOWNLOAD_HOST_ALLOWLIST` | `[]` (вимкнено) | `hostname` (будь-який порт) або `hostname:port`, куди може вести `download_url` вмісту матеріалу (JSON-список; IDN — у punycode `xn--…`); порожньо — завантаження відхиляються (422) |
| `LLM_MODEL_CHEAP` / `LLM_MODEL_STRONG` | `cheap` / `strong` | псевдоніми моделей шлюзу |
| `LLM_COMPLETION_MODE` | `sync` | як чекати виклик моделі: `sync` — один HTTP-запит із власним тайм-аутом `llm_call.request_timeout_ms`; `async` — 202 + job шлюзу, опитування кожні `clients.job_poll_interval_ms` у межах `clients.job_wait_timeout_ms` (без довгого з'єднання) |
| `CONTRACTS_DIR` | пошук угору / `/app/contracts` | де `contracts/schemas` для локальної валідації |
| `GENERATED_CODE_ALLOWED_MODULES` | `re, html, json, math, datetime, decimal, string, unicodedata, itertools, functools, collections, typing, dataclasses` | політика імпортів згенерованого коду (JSON-список) |
| `ONBOARDING_ALLOW_ACTIVATION` | `true` | чи може прийняття з `activate: true` створювати джерело й завдання |
| `DEFAULT_STORAGE_PACKAGE` / `DEFAULT_STORAGE_CONNECTION` | — | `package_id@version` і `connection_id` етапу збереження в чернетці завдання |
| `STATE_DSN` | — | PostgreSQL для спільного стану кількох екземплярів (секрет; без нього — пам'ять, один екземпляр) |
| `STATE_SCHEMA` | `jane_assistant` | схема таблиць стану |
| `INSTANCE_ID` | `hostname-pid` | власник job і оренд (унікальний для кожного екземпляра) |
| `LIMITS_FILE` | — | файл `PlatformLimits` (TOML/JSON/YAML), зокрема цілий профіль `deploy/profiles/<профіль>.json`: ліміти контракту, яких асистент не має, ігноруються (перелік — у журналі старту), опечатка чи некоректне значення — помилка старту; `timeouts.connect_timeout_ms` / `request_timeout_ms` і `retries` профілю діють на виклики сусідів (`clients.*`), окрім тайм-ауту виклику моделі (`llm_call.request_timeout_ms`, власний ліміт асистента) |
| `LIMITS__<ГРУПА>__<ПАРАМЕТР>` / `LIMITS__HARD_CAPS__…` | — | перевизначення й жорсткі стелі |

## Автентифікація (ADR-0005)

Режими й усі змінні (`AUTH_MODE`, `API_KEYS`, `API_KEYS_FILE`, `JWT_*`, `METRICS_PUBLIC`) спільні для всіх сервісів: [jane-kit, «Автентифікація»](../../libs/jane-kit/README.md#автентифікація-adr-0005) і [docs/operations](../../docs/operations/README.md#автентифікація-adr-0005). `/v1/health` (і `/metrics`, доки `METRICS_PUBLIC=true`) працюють без токена; `/v1/info` приймає будь-який дійсний токен; решта потребує токена (401 `unauthenticated`) і scope операції (403 `forbidden`). `AUTH_MODE=none` — лише для локальних тестів на loopback; за неповної конфігурації `api_key`/`jwt` сервіс не стартує. JWT з реальним IdP **не перевірено на реальному сервісі** (лише локальний JWKS у тестах jane-kit).

Scopes операцій (таблиця `ASSISTANT` з `jane_kit.auth_scopes`):

- `assistant:use` — усі операції (`/v1/onboarding-sessions…`, `/v1/improvement-runs`, `/v1/unknown-materials`, `/v1/jobs/*`).

Сусідів асистент викликає власним токеном (`SERVICE_TOKEN_REF` або окремі `*_TOKEN_REF`), а не токеном користувача. Потрібні scopes ключа асистента: llm — `llm:invoke`; registry — `registry:read`, `registry:write`, `registry:approve` і `actor: llm`; колектори — `collector:read`, `collector:run`; handler-runtime — `handler:test`; storage — `storage:read`; orchestrator — `orchestrator:read`, `orchestrator:write`.

Приклад для `api_key` (зберігається лише хеш ключа):

```text
JANE_ASSISTANT_AUTH_MODE=api_key
JANE_ASSISTANT_API_KEYS=[{"name": "admin", "sha256": "<sha256 hex ключа>", "scopes": ["assistant:use"]},
  {"name": "ops", "secret_ref": "file:/run/secrets/jane-ops-key", "scopes": ["assistant:use"]}]
```

## Ліміти

Рівні: типові значення → платформа (файл, потім змінні середовища) → запит (`limits` у тілі —
контрактний `limits.llm`); `hard_caps` обмежують результат. `GET /v1/info` → `limits` показує контрактні
поля (`llm.*`, `transfer.*`, `timeouts.*`, `retries`); решта — внутрішні.

| Параметр | Типово | Опис |
|---|---|---|
| `llm.budget` | 2 USD / `run` | семантика контракту (`Budget`, однакова з LLM-шлюзом): `run` — один запуск асистента (сесія підключення — від пошуку до прийняття, хоч би скільки job і екземплярів її продовжували; job вдосконалення; job невідомого матеріалу). Кожен виклик несе весь бюджет і `scope.run_id` запуску — шлюз сам рахує витрати запуску атомарно для всіх екземплярів; інші періоди звужують спільний лічильник найконкретнішого рівня запиту (`source` для вдосконалення з `source_id`, інакше `platform`). Асистент зупиняється сам, щойно витрати запуску ≥ `amount`; **`amount: 0` — жодного виклику LLM** (так само відмовляє шлюз, навіть для безкоштовної моделі) |
| `llm.max_onboarding_samples` | 60 | верхня межа класифікованих матеріалів (фактично — адаптивно менше) |
| `llm.max_improvement_attempts` | 3 | спроби моделі на один запуск вдосконалення (0 → одразу `unresolved`) |
| `llm.max_input_tokens_per_request` / `max_output_tokens_per_request` | 16000 / 4000 | дані обрізаються (~4 символи на токен) |
| `llm.max_requests_per_minute` | 30 | передається шлюзу |
| `onboarding.min_confidence` | 0.8 | поріг достатньої впевненості вибірки |
| `onboarding.min_distinct_types` | 2 | нижче цієї кількості спостережених типів оцінка ризику невідомого типу суворіша; однотипне джерело може стати достатнім за більшої вибірки |
| `onboarding.sample_batch_size` | 10 | матеріалів на один запит класифікації |
| `onboarding.fetch_ratio` | 3 | збір вибірки може отримати до `max_onboarding_samples × fetch_ratio` матеріалів |
| `onboarding.min_examples_per_type` / `max_examples_per_type` | 2 / 3 | коли тип «розрізнено» / скільки прикладів у аналіз і тести |
| `onboarding.max_sample_chars` | 6000 | текст одного матеріалу для моделі |
| `onboarding.max_candidates`, `auto_select_confidence`, `auto_select_margin` | 5, 0.8, 0.2 | пошук і автовибір кандидата |
| `onboarding.max_candidate_packages`, `bind_threshold`, `fork_threshold` | 5, 0.9, 0.5 | підбір готових екстракторів |
| `onboarding.max_generation_attempts` | 2 | спроби згенерувати пакет, що проходить тести |
| `onboarding.max_proposals` | 4 | варіантів збору |
| `onboarding.collection_poll_wait_ms`, `max_empty_polls` | 1000, 30 | long-poll матеріалів вибірки |
| `onboarding.poll_page_factor` | 3 | матеріалів за одне опитування = `sample_batch_size × poll_page_factor` (запас для вибору різноманітних) |
| `onboarding.max_negative_examples` | 1 | матеріалів інших типів як `empty`-випадки для тестів екстрактора |
| `state.job_lease_ms` / `heartbeat_interval_ms` | 60000 / 15000 | оренда job і як часто екземпляр її поновлює |
| `state.in_progress_lease_ms` | 900000 | коли незавершений `Idempotency-Key` убитого екземпляра можна перехопити |
| `state.session_retention_seconds` | 2592000 | сесії без змін довше — видаляються |
| `state.pool_max_size` / `connect_timeout_ms` | 10 / 10000 | з'єднання з PostgreSQL |
| `onboarding.requests_overhead_ratio` | 0.05 | запас запитів понад оцінку матеріалів |
| `improvement.max_problem_samples`, `max_successful_examples`, `max_sample_chars`, `max_file_chars` | 10, 5, 6000, 20000 | обсяг даних для моделі |
| `unknown.min_confidence`, `max_sample_chars` | 0.6, 6000 | нижче — пропозиція `none` |
| `transfer.inline_max_bytes` | 262144 | чернетка пакета до runtime inline; більша — `payload_too_large` |
| `content.max_material_bytes` | 16777216 | найбільший вміст одного матеріалу (inline, `file://`, `download_url`); більший — `limit_exceeded` |
| `content.fetch_timeout_ms` / `connect_timeout_ms` | 30000 / 5000 | усе завантаження за `download_url` / встановлення з'єднання |
| `search.request_timeout_ms` / `connect_timeout_ms` | 10000 / 5000 | виклики пошукового провайдера `http_json` |
| `clients.*` (тайм-аути, повтори, опитування job) | див. jane-kit (30000 мс запит, 4 спроби) | виклики сусідів; це контрактні `timeouts.*` / `retries`, тож профіль платформи задає їх для коротких службових викликів |
| `llm_call.request_timeout_ms` | 900000 | тайм-аут одного синхронного виклику LLM-шлюзу (власний ліміт: виклик моделі довший за службові). Має покривати найгірший випадок шлюзу: (повтори за схемою + 1) × спроби провайдера × тайм-аут провайдера — з типовими значеннями llm 2 × 2 × 120 с = 8 хв, зі спробами профілю 3 — 12 хв; 15 хв — і `gateway.reservation_ttl_seconds` шлюзу. З'єднання й повтори — з `clients.*` |
| `jobs.*`, `idempotency.*` | див. jane-kit | job і ключі ідемпотентності |

## Приклад виклику зі стороннього застосунку

```python
import time

import httpx

with httpx.Client(base_url="http://127.0.0.1:8000") as client:
    job = client.post(
        "/v1/onboarding-sessions",
        json={"query": "https://shop.example.test/", "expected_entity_types": ["product"]},
        headers={"Idempotency-Key": "onboard-shop-1"},
    ).json()
    session_id = job["labels"]["session_id"]
    while client.get(f"/v1/jobs/{job['job_id']}").json()["status"] not in {
        "succeeded",
        "failed",
        "cancelled",
    }:
        time.sleep(1)
    session = client.get(f"/v1/onboarding-sessions/{session_id}").json()
    best = next(p for p in session.get("proposals", []) if p["recommended"])
    accept = client.post(
        f"/v1/onboarding-sessions/{session_id}/proposals/{best['proposal_id']}/acceptance",
        json={"activate": False, "source_id": "shop-example"},
        headers={"Idempotency-Key": "accept-shop-1"},
    ).json()
    print(accept["job_id"])  # Job.result = AcceptanceResult (опубліковані версії, звіти тестів, чернетки)
```
