# Безпека експлуатації

Сторінка зводить налаштування безпеки, які оператор задає для платформи: автентифікацію й scopes, ключі сервісів, секрети підключень, allowlist-и мережевих звернень і пісочницю. Рішення й альтернативи — [ADR-0006](../adr/0006-authentication.md), [ADR-0007](../adr/0007-secrets-and-connections.md), [ADR-0004](../adr/0004-python-sandbox.md).

## Зміст

- [Автентифікація](#автентифікація)
- [Scopes](#scopes)
- [Ключі сервісів для сусідів](#ключі-сервісів-для-сусідів)
- [Секрети й підключення](#секрети-й-підключення)
- [Allowlist-и мережевих звернень](#allowlist-и-мережевих-звернень)
- [Пісочниця й вміст джерел](#пісочниця-й-вміст-джерел)
- [Контрольний список](#контрольний-список)

## Автентифікація

Усі сервіси приймають токен у заголовку `Authorization: Bearer <токен>`. Режим задає `JANE_<СЕРВІС>_AUTH_MODE`:

| Режим | Призначення | Поведінка |
|---|---|---|
| `none` | лише локальні тести | усі запити від `anonymous` з усіма scopes; попередження в журналі; сервіс не стартує на не-loopback адресі без `JANE_<СЕРВІС>_AUTH_NONE_ALLOW_REMOTE=true` |
| `api_key` | dev-стек | статичні ключі з `JANE_<СЕРВІС>_API_KEYS` (JSON) або `…_API_KEYS_FILE` (JSON/YAML): `{"name", "scopes", "sha256"}` або `{"name", "scopes", "secret_ref"}` |
| `jwt` | рекомендований для інших середовищ | токени RS*/PS*/ES* з ключами з `…_JWT_JWKS_URL`; обов'язкові `iss`, `aud`, `exp`; scopes з claim `scope` |

- Типовий режим у коді — `none`; dev-стек задає `api_key` усім сервісам.
- Неповна конфігурація зупиняє старт (fail closed): `api_key` без ключів, `jwt` без JWKS URL, issuer або audience, нерозв'язне `secret_ref`, маршрут без scope у таблиці сервісу.
- `alg=none` і HMAC-алгоритми в режимі `jwt` не приймаються. Режим `jwt` у dev-стеку не перевірявся.
- Ключі `api_key` зберігаються лише як SHA-256; у журнал старту потрапляють тільки назви ключів (`authentication enabled`).
- Без токена доступні `GET /v1/health` і, типово, `GET /metrics` (`JANE_<СЕРВІС>_METRICS_PUBLIC=false` закриває метрики). Відсутній або недійсний токен — `401 unauthenticated`, бракує scope — `403 forbidden`.

## Scopes

Scope має вигляд `<сервіс>:<дія>`. Таблиці «маршрут → scope» визначено в `libs/jane-kit/src/jane_kit/auth_scopes.py`, у контрактах — розширенням `x-jane-scope` кожної операції.

| Сервіс | Scopes |
|---|---|
| Колектори | `collector:read`, `collector:run`, `connections:write` |
| Handler Runtime | `handler:invoke`, `handler:test`, `connections:write` |
| Storage | як Handler Runtime + `storage:read` |
| LLM gateway | як Handler Runtime + `llm:invoke`, `llm:admin` (бюджети й облік витрат) |
| Registry | `registry:read`, `registry:write`, `registry:approve` (зміна статусу версії) |
| Orchestrator | `orchestrator:read`, `orchestrator:write`, `orchestrator:admin` (підключення, ліміти платформи; включає read і write) |
| Assistant | `assistant:use` |

Розподіл scopes між викликачами в dev-стеку видно в `JANE_<СЕРВІС>_API_KEYS` у `infra/compose.yaml`. Ключ `admin` має повний набір для оператора; ключ `assistant` у Registry має `registry:approve` з атрибутом `actor: llm` — Assistant може затверджувати створені LLM версії, якщо політика пакета це дозволяє ([ADR-0010](../adr/0010-llm-in-assistant.md)).

## Ключі сервісів для сусідів

Сервіс звертається до сусідів зі своїм ключем, який отримує з середовища:

| Сервіс | Параметр |
|---|---|
| Orchestrator | `token_ref` кожного виконавця або спільний `JANE_ORCHESTRATOR_SERVICE_TOKEN_REF` (`env:…` / `file:…`) |
| Assistant | `JANE_ASSISTANT_SERVICE_TOKEN_REF` і за потреби окремі `…_<СУСІД>_TOKEN_REF` |
| Registry | `JANE_REGISTRY_RUNTIME_PROFILES_TOKEN_REF` (запит профілів Handler Runtime) |
| Handler Runtime, Storage, LLM gateway | `JANE_<СЕРВІС>_REGISTRY_TOKEN` |
| Колектори | `JANE_<СЕРВІС>_REGISTRY_TOKEN_ENV` — **назва** змінної, у якій лежить токен |

У dev-стеку `just up` генерує ключ кожної ідентичності й передає сервісу значення, а сусідам — лише його хеш — [облікові дані стеку](../../infra/README.md#облікові-дані).

## Секрети й підключення

Підключення (до сховища, провайдера LLM, HTTP-джерела, облікового запису Telegram) містить несекретні `params` і `secret_refs` — посилання на секрети. Значення секретів не проходять через API й не зберігаються в базах.

- **Види посилань:** `env:ІМ'Я` і `file:/шлях`. `vault:` відхиляється: у цій збірці постачальника немає.
- **Обмеження для підключень** (Storage, LLM gateway, колектори): змінна `env:` має починатися з `JANE_SECRET_` (`JANE_<СЕРВІС>_SECRET_ENV_PREFIX`); файл `file:` має бути всередині `/run/secrets` (`JANE_<СЕРВІС>_SECRET_FILES_DIR`) після розв'язання `..` і символьних посилань. Порушення — `422` з кодом `secret_ref_not_allowed`.
- **Реєстр підключень** — `PUT/DELETE /v1/connections/{connection_id}` в Orchestrator (scope `orchestrator:admin`). Значення, схожі на секрети, у `params` відхиляються (`secret_detected`). Orchestrator розсилає визначення виконавцям (`PUT /v1/connections/{id}`, scope `connections:write`); виконавець, що не підтримує керованих підключень, відповідає `501` і вилучається з розсилки.
- **Розв'язання** секретів відбувається лише у виконавця, у його середовищі. `POST …/test` підключення показує, чи секрети розв'язалися, не розкриваючи значень.
- **Файл підключень Storage** — `JANE_STORAGE_CONNECTIONS_FILE` (`infra/config/storage-connections.json` у dev-стеку), формат `{"connections": [...]}`, лише з `secret_refs`.
- **Пакети обробників** секретів не містять: Registry сканує файли пакета й відхиляє публікацію з `secret_detected`. Маніфест містить лише `required_connections` (логічна назва й вид).
- **Ключі провайдерів LLM** у dev-стеку лежать у `.jane/secrets` (ігнорується Git), змонтованому в LLM gateway як `/run/secrets`; підключення посилається на файл (`file:/run/secrets/<ім'я>`). Значення людина кладе у файл сама.

## Allowlist-и мережевих звернень

Типово сервіси не звертаються за довільними адресами: кожен вид звернень дозволяється явно.

| Параметр | Сервіс | Типово | Що дозволяє |
|---|---|---|---|
| `JANE_STORAGE_CONNECTION_HOST_ALLOWLIST` | Storage | порожній — підключення з мережевою адресою відхиляються | `host:port` цільових сховищ |
| `JANE_<СЕРВІС>_DOWNLOAD_HOST_ALLOWLIST` | Storage, Handler Runtime, LLM gateway, Assistant | порожній — завантаження вимкнено | хости `download_url` у `ContentRef`; редиректи не виконуються |
| `JANE_<СЕРВІС>_BLOB_ROOTS` | Handler Runtime, LLM gateway, Assistant | порожній — `file://` вимкнено | каталоги, з яких можна читати `file://`-blob |
| `JANE_STORAGE_CONTENT_FILES_DIR` | Storage | не задано | каталог RAW для читання `file://` |
| `JANE_LLM_PROVIDER_API_BASE_ALLOWLIST` | LLM gateway | `["https://api.anthropic.com"]` | адреси API провайдерів |
| `JANE_TELEGRAM_COLLECTOR_TELEGRAM_HOST_ALLOWLIST` | Telegram Collector | порожній | хости в мережевих параметрах підключення (`server`, `proxy_host` …) |
| `JANE_WEB_COLLECTOR_CONNECTION_ORIGIN_ALLOWLIST` | Web Collector | порожній — облікові дані HTTP-підключень не надсилаються | точні origin для підключень з автентифікацією |
| `JANE_WEB_COLLECTOR_EGRESS_DENY_LINK_LOCAL` | Web Collector | `true` | блокує link-local і адреси метаданих хмари після DNS і на кожному редиректі |
| `JANE_WEB_COLLECTOR_EGRESS_DENY_PRIVATE` | Web Collector | `false` | `true` блокує приватні мережі |

`ContentRef` перевіряється після читання: розмір і SHA-256 мають збігатися з оголошеними. `s3://`-посилання без `download_url` відхиляються.

Обмеження: типово Web Collector **може** звертатися до приватних мереж (`EGRESS_DENY_PRIVATE=false`) — у середовищі, де сервіс бачить внутрішню мережу, увімкніть цей параметр. Правила `robots.txt` колектор поважає типово (`robots.mode: respect` у правилах); режим `owner_policy` вимагає `confirmed_owner: true` і обґрунтування в правилах джерела.

## Пісочниця й вміст джерел

- Код екстракторів виконується в окремому контейнері на кожен виклик: без мережі, з файловою системою лише для читання, non-root користувачем `65534:65534`, з лімітами CPU, пам'яті, процесів і часу — [Handler Runtime](../components/handler-runtime/operations.md). Бекенд `subprocess` без ізоляції не запускається без `JANE_HANDLER_RUNTIME_ALLOW_UNSAFE_SUBPROCESS=true`.
- Handler Runtime у dev-стеку має доступ до Docker-сокета хоста. Поза розробкою використовуйте окремий рушій або rootless Podman і обмежте доступ до сокета.
- Вміст сторінок і повідомлень для LLM — дані, а не інструкції: LLM gateway відокремлює інструкції від даних розмежувачами з випадковим nonce, Assistant перевіряє згенеровані правила й код перед застосуванням — [ADR-0010](../adr/0010-llm-in-assistant.md).

## Контрольний список

- [ ] Усі сервіси в режимі `api_key` або `jwt`; `auth_mode=none` ніде, крім локальних тестів.
- [ ] Кожен викликач має власний ключ із мінімальними scopes.
- [ ] `/metrics` недоступний ззовні або `METRICS_PUBLIC=false`.
- [ ] Секрети — лише через `secret_refs` з `JANE_SECRET_*` або файлів у `/run/secrets`; `.jane/` і `.jane/secrets` не потрапляють у Git і копії з доступом сторонніх.
- [ ] Allowlist-и порожні, крім явно потрібних адрес; для Web Collector у внутрішній мережі — `EGRESS_DENY_PRIVATE=true`.
- [ ] Порти слухають лише `127.0.0.1` (`JANE_BIND`) або доступ до них обмежено мережею.
- [ ] Образ пісочниці закріплено дайджестом.
