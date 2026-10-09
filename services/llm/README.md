# LLM — шлюз і LLM-обробник

Сервіс `llm` (WP-10) — єдина точка звернення платформи до LLM:

- **шлюз** за [`contracts/openapi/llm.v1.yaml`](../../contracts/openapi/llm.v1.yaml): провайдери й моделі,
  псевдоніми моделей (`default`, `cheap`, `strong`), структуровані запити з валідацією виходу за JSON Schema,
  бюджети й ліміти частоти на рівнях platform → source → task, облік витрат;
- **LLM-обробник** за спільним протоколом [`handler.v1.yaml`](../../contracts/openapi/handler.v1.yaml)
  (`/v1/invocations`, `/v1/test-runs`, `/v1/connections`): виконує пакети типу `llm` (маніфест + промпти +
  схеми, коду немає). Приклад пакета — [`packages/jane.llm-event-extractor`](packages/jane.llm-event-extractor/).

Сервіс працює без оркестратора: усе потрібне приходить у запиті (пакет, вхідні дані, ліміти, scope).

## Незалежний запуск

Без Docker (з кореня репозиторію). Стан (бюджети, облік, провайдери, підключення, ключі ідемпотентності, job)
зберігається в PostgreSQL — у власній схемі сервісу (`JANE_LLM_DB_SCHEMA`, типово `llm`):

```
uv sync --all-packages
just up --project jane-wp10 postgres          # або будь-який PostgreSQL
# DSN — з `just env --project jane-wp10` (JANE_STACK_POSTGRES_DSN); пароль не комітьте
export JANE_LLM_DATABASE_URL=postgresql://...
uv run --package jane-llm python -m jane_llm  # http://127.0.0.1:8110
curl http://127.0.0.1:8110/v1/health
```

Для демонстрації без БД: `JANE_LLM_STORE=memory` (стан у пам'яті процесу — лише один екземпляр і тести).

У Docker (контекст збірки — корінь репозиторію):

```
docker build -f services/llm/Dockerfile -t jane-llm .
docker run --rm -p 8110:8110 -e JANE_LLM_DATABASE_URL=postgresql://... \
  -e JANE_SECRET_ANTHROPIC_API_KEY=... -e JANE_LLM_SEED_FILE=/app/seed.yaml jane-llm
```

В образі провайдер `fake` **вимкнено** (`JANE_LLM_FAKE_PROVIDER_ENABLED=false`); для dev і тестів його вмикають
змінною середовища (типове значення поза образом — `true`).

**Кілька екземплярів:** запустіть кілька процесів/контейнерів з однаковими `JANE_LLM_DATABASE_URL` і
`JANE_LLM_DB_SCHEMA`. Бюджети, облік витрат, ліміти частоти, ключі ідемпотентності, результати викликів і
job — у спільному PostgreSQL, не в пам'яті процесу; перевірку бюджету й резервування виконує одна транзакція з
`SELECT … FOR UPDATE` на рядках лічильників (у єдиному порядку ключів), тож разом екземпляри не
проходять перевірку бюджету «повз» одне одного (`tests/test_multi_instance.py` — два справжні процеси).
Межа точності: перевіряється резерв (оцінка), а списується фактична вартість; якщо фактичний виклик
дорожчий за оцінку (див. «Бюджети»), витрати можуть перевищити ліміт на цю різницю для викликів, що вже
йшли одночасно, — наступні виклики тоді зупиняються. Схема створюється при старті (під advisory lock).

## Тести

```
just test llm                                              # unit + contract (memory store)
just up --project jane-wp10 postgres
just integration --project jane-wp10 services/llm          # ті самі сценарії на PostgreSQL + 2 процеси
just down -v --project jane-wp10
```

| Файл | Що перевіряє |
|---|---|
| `tests/test_budget.py` | **Перевищення бюджету зупиняє виклики**: 429 `budget_exhausted` без звернення до провайдера; бюджет платформи з конфігурації; бюджет запиту лише звужує (і з іншим періодом не підміняє збережений бюджет завдання чи платформи); `run` — окреме вікно на `run_id`, без `run_id` — на запит; `amount: 0` не пропускає жодного виклику (навіть безкоштовної моделі); повтор з тим самим `Idempotency-Key` не витрачає бюджет удруге; LLM-обробник повертає `failed/budget_exhausted` і не кешує його під ключем доставки |
| `tests/test_injection.py` | **Ін'єкція у вмісті не змінює поведінку** (див. нижче) |
| `tests/test_multi_instance.py` | два процеси сервісу з одним PostgreSQL: спільний бюджет під конкурентним навантаженням, спільний облік і ідемпотентність |
| `tests/test_contract.py` | усі операції `llm.v1` і `handler.v1` через `ContractClient` (запити й відповіді за схемами) |
| `tests/test_service.py` | повтори за схемою, 502 з вивільненням резерву, ліміти частоти й токенів, тести пакета через `/v1/test-runs`, простежуваність результату, seed-файл, публікація в registry (мок з контракту), завантаження пакета з registry з перевіркою дайджесту, адаптер Anthropic проти локального замінника API |
| `tests/test_units.py` | промпт і розмежувачі, фейкова модель, вікна бюджетів, розв'язання секретів, семантика резервувань |
| `tests/test_fake_provider.py` | затримка провайдера `fake`: `params.delay_ms`, `responses[].delay_ms` (зокрема скрипт лише із затримкою), межа `fake.max_delay_ms` з конфігурації, некоректні значення; синхронний `/v1/completions`, утримуваний затримкою, — 409 `idempotency_in_progress` на повтор, 422 на інше тіло, потім збережений результат і один виклик провайдера |
| `tests/test_content_policy.py` | політика ContentRef входів: `file:///proc/self/environ`, шлях поза `JANE_LLM_BLOB_ROOTS`, `..`, symlink назовні, хост поза `JANE_LLM_DOWNLOAD_HOST_ALLOWLIST`, редирект на інший хост, перевищення `gateway.max_data_part_bytes` — відмова без виклику провайдера; дозволені `file://` і `download_url` — успіх |

Фікстура `store_kind` проганяє кожен сценарій на `memory` і (з маркером `integration`) на PostgreSQL.

## Захист від ін'єкцій: як тест доводить його

Вміст джерел — дані, не інструкції (ТЗ §11):

1. **Канали.** Довірені `instructions` (від викликача чи пакета) і преамбула платформи йдуть лише в системний
   канал провайдера; недовірені `data` — лише в канал користувача, кожна частина між розмежувачами
   `<<<JANE-DATA <nonce> …>>>` / `<<<JANE-END <nonce>>>>`. Nonce — 128 випадкових біт на кожен запит, його
   оголошено в системному каналі. Шаблон входу пакета після підстановки вмісту теж іде як дані.
2. **Нейтралізація.** Будь-яке `<<<` у даних замінюється (`‹‹‹`), тож дані не можуть підробити розмежувач,
   навіть знаючи nonce.
3. **Підказка для повтору за схемою** теж іде в довірений канал, тому будується **лише зі схеми**
   (`schema_path` порушеного правила й ключове слово, напр. `schema #/additionalProperties: type`), без
   вказівників на вихід моделі: ключі виходу (`additionalProperties`, `patternProperties`) можуть містити
   текст із даних. Вказівники на вихід повертаються лише викликачеві у `validation_errors`.
4. **Вихід** перевіряється за схемою; шлюз не має інструментів і не виконує дій з відповіді; секретів у
   промптах немає.

**Чому тест змістовний.** Фейковий провайдер `fake` навмисно моделює **слухняну** модель
([`providers/fake.py`](src/jane_llm/providers/fake.py)): він, як модель, читає nonce із системного каналу,
вважає даними лише текст між *точними* розмежувачами з цим nonce, а все інше — інструкціями, і **виконує**
фразу `ignore previous instructions … {json}` в інструкціях (відповідає цим JSON). Тож:

| Випадок у `tests/test_injection.py` | Очікування | Що доводить |
|---|---|---|
| корисне навантаження в `instructions` (контроль) | фейк відповідає JSON атакувальника | фейк слухняний, навантаження дієве |
| наївний промпт — дані просто дописано в текст (контроль) | фейк захоплено | без розділення атака працює |
| підроблений розмежувач із *справжнім* nonce без нейтралізації (контроль) | фейк захоплено | нейтралізація `<<<` несуча |
| те саме навантаження **в даних через шлюз**: просто текстом, як «SYSTEM MESSAGE», з підробленим розмежувачем і вгаданим nonce, з підробленим розмежувачем і **злитим** nonce (тестова фабрика nonce) | відповідь така сама, як без навантаження (`product`) | шлюз тримає вміст у каналі даних |
| LLM-обробник: матеріал з ін'єкцією | ті самі сутності, що й для чистого матеріалу, без `HACKED` | захист діє й у ланцюжку |
| підказка повтору з вказівником на ключ виходу, що містить навантаження (контроль) | фейк захоплено | канал підказки — інструкційний |
| невалідний вихід з навантаженням у **ключах** (`additionalProperties`, `patternProperties`) → повтор через шлюз | у системному каналі другого виклику лише `schema #/additionalProperties…`; `valid: false`, без `hijacked` | підказка не переносить дані в інструкції |

Пакет `jane.llm-event-extractor` містить тест `prompt-injection-is-data` (очікується `empty`).

## Конфігурація

Змінні середовища з префіксом `JANE_LLM_`:

| Змінна | Типово | Опис |
|---|---|---|
| `JANE_LLM_HOST` / `JANE_LLM_PORT` | `127.0.0.1` (у контейнері `0.0.0.0`) / `8110` | адреса |
| `JANE_LLM_STORE` | `postgres` | `postgres` або `memory` (лише тести/демо) |
| `JANE_LLM_DATABASE_URL` | — | DSN PostgreSQL (обов'язковий для `postgres`) |
| `JANE_LLM_DB_SCHEMA` | `llm` | власна схема сервісу |
| `JANE_LLM_SEED_FILE` | — | YAML/JSON з провайдерами, псевдонімами, підключеннями, бюджетами (створюються лише відсутні), приклад — [`config/seed.example.yaml`](config/seed.example.yaml) |
| `JANE_LLM_FAKE_PROVIDER_ENABLED` | `true` (в образі `false`) | реєструвати провайдера `fake` і псевдонім `default` → `fake/fake-deterministic-1` (якщо `default` ще не задано) |
| `JANE_LLM_DB_POOL_MIN_SIZE` / `JANE_LLM_DB_POOL_MAX_SIZE` | `1` / `10` | пул з'єднань PostgreSQL на екземпляр |
| `JANE_LLM_SECRET_ENV_PREFIX` | `JANE_SECRET_` | `env:`-посилання підключень — лише на змінні з цим префіксом |
| `JANE_LLM_SECRET_FILES_DIR` | `/run/secrets` | `file:`-посилання — лише на файли в цьому каталозі |
| `JANE_LLM_PROVIDER_API_BASE_ALLOWLIST` | `["https://api.anthropic.com"]` | дозволені origin для `params.api_base` підключень (JSON-список) |
| `JANE_LLM_BLOB_ROOTS` | `[]` (вимкнено) | каталоги, з яких можна читати `file://` ContentRef (вміст матеріалу, `entities_ref`, `data_ref`, `package_archive`), JSON-список; порожньо — `file://` відхиляється (422) |
| `JANE_LLM_DOWNLOAD_HOST_ALLOWLIST` | `[]` (вимкнено) | `hostname` (будь-який порт) або `hostname:port`, куди може вести `download_url` ContentRef, JSON-список (IDN — у punycode `xn--…`); порожньо — завантаження відхиляються (422) |
| `JANE_LLM_PACKAGES_DIR` | вбудований `services/llm/packages` | локальні LLM-пакети (`<dir>/**/jane-package.json`) |
| `JANE_LLM_REGISTRY_URL` / `JANE_LLM_REGISTRY_TOKEN` | — | репозиторій обробників для пакетів за `handler` (архів `…/archive`); токен — власний ключ шлюзу (`registry:read`), лише з середовища, не журналюється |
| `JANE_LLM_LOG_LEVEL` / `JANE_LLM_LOG_FORMAT` | `INFO` / `json` | журнали |
| `JANE_LLM_AUTH_MODE` | `none` | `none` / `api_key` / `jwt` — див. «Автентифікація (ADR-0005)» |
| `JANE_LLM_LIMITS_FILE` | — | файл `PlatformLimits` (`defaults`, `hard_caps`), зокрема цілий профіль `deploy/profiles/<профіль>.json`: ліміти контракту, яких сервіс не має, ігноруються (перелік — у журналі старту), опечатка чи некоректне значення — помилка старту. Увага: `timeouts.connect_timeout_ms`, `timeouts.request_timeout_ms` і `retries` профілю діють і на виклики провайдерів (`provider.*` оголошені як ці поля контракту), тобто замінюють типові 120 с тайм-ауту запиту |
| `JANE_LLM_LIMITS__<ГРУПА>__<ПАРАМЕТР>` | — | перевизначення, напр. `JANE_LLM_LIMITS__LLM__BUDGET__AMOUNT=5` |
| `JANE_LLM_LIMITS__HARD_CAPS__…` | — | жорсткі стелі платформи |

**Провайдери й підключення.** Провайдер (`PUT /v1/providers/{id}`) має `kind` (`fake`, `anthropic`), моделі з
цінами й `connection_id`. Підключення (`PUT /v1/connections/{id}`, `kind: llm_provider`) містить лише несекретні
`params` і `secret_refs` (`env:VAR`, `file:/run/secrets/x`); значення розв'язує цей сервіс у своєму середовищі,
через API вони не проходять і в БД не зберігаються; `params`, схожі на секрети, відхиляються (`secret_detected`;
виняток — скрипти `params.responses` лише для `params.provider: fake`).
`POST /v1/connections/{id}/test` показує `secrets_resolved` без значень.

**Політика секретів (захист від витоку).** Підключення визначає, *куди* піде розв'язаний секрет, тому
(поки автентифікацію не реалізовано — тим паче) сервіс обмежує: `env:`-посилання — лише змінні з префіксом
`JANE_LLM_SECRET_ENV_PREFIX` (типово `JANE_SECRET_`, тобто не `PGPASSWORD`, не `JANE_LLM_DATABASE_URL`);
`file:` — лише всередині `JANE_LLM_SECRET_FILES_DIR` (після розв'язання шляху, без `..`); `vault:` вимкнено;
`params.api_base` — лише origin з `JANE_LLM_PROVIDER_API_BASE_ALLOWLIST` (типово офіційний хост Anthropic).
Порушення — 422 при `PUT /v1/connections` і в seed-файлі; підключення, збережене в обхід API, під час виклику
не отримує секретів і відхиляється (422). Тести: `test_connection_policy_rejects_exfiltration`.

**Політика ContentRef (WP-01h).** Вміст входів `POST /v1/invocations` і `package_archive` приходить у запиті, тож
сервіс читає його спільним `jane_kit.content.ContentReader`: `inline` (utf-8/base64); `blob` з `download_url` —
лише `http(s)` на хост із `JANE_LLM_DOWNLOAD_HOST_ALLOWLIST`, без редиректів, без проксі й `.netrc` із середовища,
лише незакодоване тіло, обрізання на `gateway.max_data_part_bytes` / `gateway.max_package_bytes` під час
завантаження, усе завантаження — у межах `gateway.content_fetch_timeout_ms`; `file://` — лише строго всередині
`JANE_LLM_BLOB_ROOTS` (шлях спершу розв'язується з `..` і symlink, читається саме розв'язаний файл, лише звичайний
файл); `s3://` без `download_url` — 422 (облікових даних сховища сервіс не має). Після читання перевіряються
`size_bytes` blob і `sha256`. Відмови: політика, невалідне посилання чи невідповідність `sha256` — 422
`validation_failed`; понад ліміт — 422 `limit_exceeded` (`details.path`); файла немає або `download_url` дав 404 —
404 `not_found`; мережа, тайм-аут, 5xx — 502 `upstream_unavailable` (повторюваний), редирект чи інший 4xx — 502
неповторюваний. `detail` не містить шляхів і вмісту; відхилений вміст до провайдера не потрапляє. Тести:
`tests/test_content_policy.py` (і `libs/jane-kit/tests/test_content.py`).

- **`anthropic`** — Anthropic Messages API (`POST {api_base}/v1/messages` через httpx; офіційний SDK 1.x тягне `httpx2`, що в спільному uv workspace перемикає `TestClient` усіх сервісів — тому не використано): `params.api_base` (необов'язково),
  `secret_refs.api_key`; структурований вихід — `output_config.format` (JSON Schema) для моделей з
  `supports_structured_output`. `temperature` запиту/пакета **не передається** (нові моделі Claude не приймають
параметрів семплювання; керування — промптом). Моделі й ціни за замовчуванням — з конфігурації (seed), приклад:
  `claude-opus-5` ($5/$25 за 1M токенів), `claude-haiku-4-5` ($1/$5). **Не перевірено на реальному сервісі**
  (ключа немає); форма запиту перевірена проти локального замінника API.
- **`fake`** — детермінований провайдер для тестів цього й інших WP. Відповідь: ін'єкція в інструкціях (див.
  вище) → перший збіг зі скриптів підключення (`params.responses: [{when_data_contains | when_data_matches,
  output | output_text | error: unavailable|rejected}]`) → мінімальне значення, що відповідає схемі →
  `fake:<sha256>`. Токени — `ceil(символи / 4)`. Ціни задаються в моделі провайдера (типово 0).
  **Затримка відповіді** (детерміноване вікно «виклик ще в польоті» для тестів, напр. R-04): `delay_ms`
  першого скрипту, що збігся й має `delay_ms` (скрипт лише з `delay_ms`, без відповіді, тільки задає затримку —
  відповідь шукається далі), інакше `params.delay_ms` підключення; ціле число мс ≥ 0, інше значення — помилка
  виклику (не `retryable`). Затримка обмежується `fake.max_delay_ms` (див. «Ліміти»), відбувається перед
  відповіддю (і перед скриптованою помилкою) і журналюється рядком `fake provider holds its answer` з
  `connection_id`, `delay_ms`. Приклад: `params: {provider: fake, delay_ms: 10000}` — кожен виклик через це
  підключення відповідає через 10 с; `responses: [{when_data_contains: "slow-marker", delay_ms: 10000}, …]` —
  лише запити з цим текстом у даних.

## Автентифікація (ADR-0005)

Режими й усі змінні (`AUTH_MODE`, `API_KEYS`, `API_KEYS_FILE`, `JWT_*`, `METRICS_PUBLIC`) спільні для всіх сервісів: [jane-kit, «Автентифікація»](../../libs/jane-kit/README.md#автентифікація-adr-0005) і [docs/operations](../../docs/operations/README.md#автентифікація-adr-0005). `/v1/health` (і `/metrics`, доки `METRICS_PUBLIC=true`) працюють без токена; `/v1/info` приймає будь-який дійсний токен; решта потребує токена (401 `unauthenticated`) і scope операції (403 `forbidden`). `AUTH_MODE=none` — лише для локальних тестів на loopback; за неповної конфігурації `api_key`/`jwt` сервіс не стартує. JWT з реальним IdP **не перевірено на реальному сервісі** (лише локальний JWKS у тестах jane-kit).

Scopes операцій (таблиця `merge(HANDLER, LLM)` з `jane_kit.auth_scopes`):

- llm.v1: `llm:invoke` — `POST /v1/completions`; `GET /v1/providers…` і `GET /v1/model-aliases` — `llm:invoke` або `llm:admin`; зміни провайдерів, псевдонімів і бюджетів, `GET /v1/budgets`, `GET /v1/usage` — `llm:admin` (оркестратор синхронізує бюджети з `llm:admin`); `/v1/jobs/*` — `llm:invoke`, `llm:admin`, `handler:invoke` або `handler:test`;
- handler.v1: `handler:invoke` — `POST /v1/invocations`, `GET /v1/invocations/{id}`; `handler:test` — `POST /v1/test-runs`; `/v1/jobs/*` — `handler:invoke` або `handler:test`; `GET /v1/connections…` — `connections:write` або `handler:invoke`; `PUT`/`DELETE /v1/connections/{id}` і `POST …/test` — `connections:write`.

Приклад для `api_key` (зберігається лише хеш ключа):

```text
JANE_LLM_AUTH_MODE=api_key
JANE_LLM_API_KEYS=[{"name": "assistant", "sha256": "<sha256 hex ключа>", "scopes": ["llm:invoke"]},
  {"name": "ops", "secret_ref": "file:/run/secrets/jane-ops-key", "scopes": ["llm:invoke"]}]
```

## Ліміти

Рівні: типові значення сервісу → платформа (файл, змінні середовища) → запит (автономний режим), `hard_caps`
обмежують результат. `GET /v1/info` → `limits` (поля з `limits.schema.json`).

| Параметр | Типово | Опис |
|---|---|---|
| `llm.budget` | 10 USD / day | бюджет платформи, якщо немає збереженого `PUT /v1/budgets/platform/platform` |
| `llm.max_requests_per_minute` | 60 | викликів провайдерів на хвилину для всієї платформи (усі екземпляри) |
| `llm.max_input_tokens_per_request` | 100000 | оцінка вхідних токенів понад це — 422 `limit_exceeded` |
| `llm.max_output_tokens_per_request` | 4096 | верхня межа `max_output_tokens` |
| `gateway.default_max_output_tokens` | 1024 | якщо ні запит, ні пакет не задали |
| `gateway.max_schema_retries` | 1 | типове й максимальне число повторів при виході не за схемою |
| `gateway.chars_per_token_estimate` | 2.0 | оцінка вхідних токенів (символи / значення) для резерву бюджету |
| `gateway.reservation_ttl_seconds` | 900 | резерв старший за це (екземпляр упав під час виклику) списується за оцінкою |
| `gateway.max_data_part_bytes` | 2000000 | найбільша частина даних (вміст матеріалу, `entities_ref`, `data_ref`) |
| `gateway.content_fetch_timeout_ms` | 30000 | тайм-аут усього завантаження blob за `download_url` (матеріали, архіви), включно з з'єднанням |
| `gateway.max_package_bytes` | 20000000 | архів пакета: стиснений розмір, відповідь registry і сума розпакованих файлів |
| `gateway.max_package_files` | 1000 | файлів в архіві пакета |
| `fake.max_delay_ms` | 30000 | верхня межа затримки провайдера `fake` (`params.delay_ms`, `responses[].delay_ms`); довша скорочується до неї, `0` вимикає затримки (`JANE_LLM_LIMITS__FAKE__MAX_DELAY_MS`) |
| пул PostgreSQL (`JANE_LLM_DB_POOL_MIN_SIZE` / `JANE_LLM_DB_POOL_MAX_SIZE`) | 1 / 10 | з'єднань на екземпляр (налаштування процесу, не `limits`) |
| `provider.connect_timeout_ms` / `provider.request_timeout_ms` | 5000 / 120000 | тайм-аути викликів провайдера (контракт `timeouts.*`) |
| `provider.retries.max_attempts` | 2 | спроби виклику провайдера (контракт `retries`) |
| `registry.connect_timeout_ms` / `request_timeout_ms` / `max_attempts` | 5000 / 30000 / 3 | виклики репозиторію обробників |
| `jobs.max_concurrent_jobs` / `max_queued_jobs` / `job_timeout_ms` | 4 / 1000 / 3600000 | асинхронні job (jane-kit) |
| `idempotency.idempotency_ttl_seconds` | 86400 | скільки пам'ятається `Idempotency-Key` (контракт `transfer.idempotency_ttl_seconds`) |

**Бюджети** (семантика зафіксована в контракті: `limits.schema.json` → `Budget`, `llm.v1` →
`CompletionRequest.limits`, `BudgetStatus`). Бюджет платформи — збережене визначення або `llm.budget`; бюджети
джерела й завдання — лише визначені через `PUT /v1/budgets/{scope_type}/{scope_id}` (оркестратор синхронізує сюди
`llm.budget` джерел і завдань). Scope запиту — `scope.source_id/task_id/run_id` (для обробника — з `context.trace`).

- **Бюджет запиту** (`limits.llm.budget`) — ще один бюджет **найконкретнішого рівня запиту**: `task`, якщо є
  `scope.task_id`, інакше `source`, інакше `platform`. Він лише звужує: збережені бюджети platform → source →
  task діють і далі. Та сама валюта й період, що й у збереженого бюджету цього рівня → спільний лічильник, діє
  менша сума; інший період → перевіряються обидва (до WP-15 бюджет запиту з іншим періодом підміняв збережений).
- **Лічильник** — `(рівень, валюта, вікно)`: `day`/`week`/`month` — календарний період UTC, `total` — одне вікно,
  `run` — окреме вікно на кожен `scope.run_id`; **без `run_id` вікном є сам запит** (усі його повтори за схемою),
  бюджет ніколи не пропускається (до WP-15 `run` без `run_id` пропускався).
- **Перевірка.** Перед **кожним** викликом провайдера резервується найгірша оцінка вартості (оцінка вхідних
  токенів + `max_output_tokens` за ціною моделі); виклик відбувається лише якщо для кожного застосовного бюджету
  `витрачено < ліміт` і `витрачено + зарезервовано + оцінка ≤ ліміт`, інакше 429 `budget_exhausted` (`details`:
  рівень, період, `spent`, `limit`, оцінка; `Retry-After` — до скидання календарного періоду, для `run`/`total`
  його немає) і провайдер не викликається. Тому **`amount: 0` — «LLM вимкнено»** для рівня: відхиляється навіть
  модель із нульовою ціною (так само перевіряє й асистент).
- **`exhausted`** (`BudgetStatus`) = `витрачено ≥ ліміт`: у цьому вікні не пройде жоден виклик, доки період не
  скинеться чи бюджет не збільшать. За `exhausted = false` виклик теж буде відхилено, якщо його оцінка не вміщується.
  `spent` — фактично списані витрати вікна (без резервів викликів, що ще йдуть); лічильник рахує виклики, на які
  цей бюджет діяв (визначення, створене посеред доби, не бачить раніших викликів цієї доби).

Після виклику резерв замінюється фактичною вартістю. Оцінка вхідних токенів — `символи / gateway.chars_per_token_estimate` (типово 2.0, з запасом до типових токенізаторів, зокрема для кирилиці), але
це не гарантія: фактична вартість може перевищити резерв, і тоді `витрачено` може стати більшим за ліміт на
цю різницю (для викликів, що йшли одночасно) — усі наступні виклики зупиняються. Для жорсткішої межі
зменшіть `chars_per_token_estimate`. Витрати `test_mode` рахуються в тому самому бюджеті й позначаються в обліку.
`max_requests_per_minute` застосовується до платформи, джерела, завдання (з визначень) і провайдера
(`Provider.limits`); `limits.llm.max_requests_per_minute` запиту звужує найконкретніший рівень.

## LLM-обробник

`POST /v1/invocations` (заголовок `Idempotency-Key` = `delivery.delivery_key`; якщо заголовка немає —
використовується `delivery_key`). Пакет: `package_archive` (inline base64 zip або `file://`/`download_url`) →
локальний каталог → registry; `handler.digest` перевіряється (`digest_mismatch`). Завантажені пакети
кешуються за дайджестом лише для того, щоб не завантажувати й не розпаковувати їх повторно: кеш не змінює
відповіді. Закешований пакет береться лише для посилання саме на його `package_id@version` (дайджест іншої
версії чи іншого пакета → той самий `digest_mismatch`/`not_found`, що й на холодному кеші), а `package_archive`
запиту читається й звіряється щоразу. Пакет, який був лише в `package_archive` якогось запиту, не відповідає на
посилання без архіву (кеш архівів і кеш знайдених у каталозі/registry пакетів окремі). Для кожного входу — один
структурований запит: інструкції пакета → системний канал, вхід (метадані й вміст матеріалу або заповнений
`input_template`) → дані. Вихід — `output.data`; для кожного `output.entities[]` маніфесту з типом `T` елементи
масиву `T + "s"` (або `T`) стають сутностями; ключові поля `message`/`material`/`material_id` беруться з
`material_id`; `observation` — з матеріалу; поля валідуються за схемою сутності. Повне правило відображення —
у контракті: [`contracts/docs/handler-packages.md`](../../contracts/docs/handler-packages.md) («Пакет `llm`: вихід
моделі → результат обробника»). Стани: `success`, `empty`,
`failed` (`schema_mismatch`, `budget_exhausted`, `invalid_params`). Повтор доставки — збережений результат із
`duplicate: true`; `failed/budget_exhausted` під ключем не зберігається (повторна доставка після збільшення
бюджету виконається). `POST /v1/test-runs` — тести маніфесту й `extra_cases` у `test_mode` (job → `TestReport`).

**Публікація пакета** (registry.v1, WP-05):

```
uv run --package jane-llm python -m jane_llm.packages digest services/llm/packages/jane.llm-event-extractor
uv run --package jane-llm python -m jane_llm.packages publish services/llm/packages/jane.llm-event-extractor --registry http://127.0.0.1:8105
```

## Приклад виклику зі стороннього застосунку

```python
import uuid
import httpx

with httpx.Client(base_url="http://127.0.0.1:8110") as client:
    r = client.post(
        "/v1/completions",
        headers={"Idempotency-Key": str(uuid.uuid4())},
        json={
            "model": "default",
            "instructions": "Classify the page type.",
            "data": [{"name": "page", "media_type": "text/html", "text": "<h1>Kettle A-100</h1>"}],
            "output_schema": {
                "type": "object",
                "required": ["page_type"],
                "properties": {"page_type": {"enum": ["product", "category", "article", "other"]}},
            },
            "scope": {"purpose": "other", "task_id": "my-task"},
        },
    )
    if r.status_code == 429:
        print(r.json()["code"])  # budget_exhausted | rate_limited
    else:
        result = r.json()
        print(result["valid"], result["output"], result["usage"]["cost"])
```

## Спостережуваність

- `GET /v1/health` (перевірка `store`), `GET /v1/info` (можливості: `handler_kinds`, `provider_kinds`, ліміти).
- `GET /metrics` — Prometheus: HTTP-метрики jane-kit, `jane_llm_requests_total{provider,model,outcome}`,
  `jane_llm_budget_rejections_total{scope_type}`.
- Журнали — JSON у stdout з `trace_id`, `request_id`, `job_id`; запис `completion` — провайдер, модель,
  токени, вартість, `test_mode`, тривалість (без вмісту даних і секретів).
- Помилки — `application/problem+json` (`budget_exhausted`, `rate_limited`, `upstream_unavailable`,
  `limit_exceeded`, `secret_detected`, `digest_mismatch`, …).
