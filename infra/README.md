# Dev-стек (Docker Compose)

`infra/compose.yaml` — локальне оточення для розробки й інтеграційних тестів. Запуск — лише через
`just up`, який дбає про ізоляцію паралельних агентів (plan.md §3 п. 4).

```
just up                     # увесь стек, чекає health-checks
just up postgres minio      # лише потрібні сервіси
just up storage registry     # профілі застосунків; їхні залежності стартують автоматично
corepack pnpm --dir web/admin install --frozen-lockfile    # зібрати адмінку (web/admin/README.md)
corepack pnpm --dir web/admin build
just up proxy               # віддавати зібраний web/admin/dist через Caddy
just env                    # адреси й облікові дані (dotenv); just env --format json
just integration            # інтеграційні тести, зокрема infra/tests (smoke усього стеку)
just down -v                # зупинити й видалити томи, зібрані образи (<проєкт>-testsite) і файл стеку
```

## Сервіси

| Сервіс | Образ (типово) | Порт у контейнері | Health-check | Для кого |
|---|---|---|---|---|
| `postgres` | `postgres:18` | 5432 | `pg_isready` | оркестратор, адаптер PostgreSQL |
| `pg-provision` | `postgres:18` | — | успішне завершення SQL | окремі ролі й бази сервісів |
| `sqlserver` | `mcr.microsoft.com/mssql/server:2022-latest` (Developer) | 1433 | `sqlcmd SELECT 1` | адаптер SQL Server |
| `mongodb` | `mongo:8.0` | 27017 | `mongosh ping` | адаптер MongoDB |
| `minio` | `pgsty/minio:RELEASE.2026-08-04T00-00-00Z@sha256:b6bfe723…` (digest) | 9000 (API), 9001 (консоль) | `/minio/health/live` | адаптер MinIO, blob-сховище матеріалів |
| `s3` | `chrislusf/seaweedfs:4.47` (S3-шлюз) | 8333 | `/healthz` | адаптер S3 |
| `testsite` | збирається з `tests/fixtures/testsite`, тег `<проєкт>-testsite` | 8080 | `GET /robots.txt` | Web Collector і стратегії |
| `proxy` | `caddy:2-alpine` | 8080 | `/_proxy/health` | єдина точка входу (`/testsite/*`, далі — сервіси) |
| `storage`, `handler-runtime`, `orchestrator`, `registry`, `assistant` | збираються з `services/<name>/Dockerfile` | 8000 | `/v1/health` з образу / compose | профілі з іменами сервісів |
| `web-collector`, `telegram-collector`, `llm` | збираються з `services/<name>/Dockerfile` | 8101, 8102, 8110 | `/v1/health` з образу / compose | профілі з іменами сервісів |

## Параметризація та ізоляція

- **Ім'я проєкту.** `just up` бере `JANE_COMPOSE_PROJECT` або генерує `jane-<тека-checkout>-<хеш шляху>`,
  тож кожен worktree має власне ім'я. Контейнери, мережа й **томи** отримують цей префікс — `down -v` одного
  агента не зачіпає інших. Інше ім'я: `just up --project jane-wp07-pg`.
- **Порти.** Типово Docker сам обирає вільний порт хоста (`127.0.0.1::5432`), тож паралельні стеки не конфліктують.
  Фактичні порти записуються у `.jane/stack-<проєкт>.json` і виводяться `just up` / `just env`. Коли контейнер
  перестворюється (зміна конфігурації чи образу, повторний `just up` після `down`), Docker обирає новий порт —
  зокрема для `proxy`; `just up` друкує нові адреси. Фіксований порт:
  `JANE_PORT_POSTGRES=15432 just up` (також `JANE_PORT_SQLSERVER`, `_MONGODB`, `_MINIO`, `_MINIO_CONSOLE`,
  `_S3`, `_TESTSITE`, `_PROXY`).
- **Адреса.** `JANE_BIND` (типово `127.0.0.1`) — назовні хоста стек не відкривається.
- **Облікові дані.** Генеруються випадково під час першого `just up` для проєкту й зберігаються в
  `.jane/stack-<проєкт>.json` (у `.gitignore`); у репозиторії їх немає. `just down -v` видаляє файл.
- **Власність PostgreSQL.** `pg-provision` створює й оновлює окремі LOGIN ролі й бази. Кожен сервіс
  отримує пароль тільки своєї ролі, не пароль суперкористувача `jane`. `PUBLIC` не має `CONNECT` до
  цих баз; `infra/tests/test_stack.py` перевіряє вхід кожною роллю у свою базу і відмову на чужі.
  На повторному `just up` паролі з файлу стеку зберігаються; provisioner ідемпотентний і не видаляє дані.

  | Сервіс / ціль | Роль і база | Змінна пароля в `.jane/stack-*.json` |
  |---|---|---|
  | handler-runtime | `jane_handler_runtime` | `JANE_PG_HANDLER_RUNTIME_PASSWORD` |
  | orchestrator | `jane_orchestrator` | `JANE_PG_ORCHESTRATOR_PASSWORD` |
  | registry | `jane_registry` | `JANE_PG_REGISTRY_PASSWORD` |
  | llm | `jane_llm` | `JANE_PG_LLM_PASSWORD` |
  | assistant | `jane_assistant` | `JANE_PG_ASSISTANT_PASSWORD` |
  | storage `results-pg` | `jane_storage_results` | `JANE_PG_STORAGE_RESULTS_PASSWORD` |

  `just env --format json` показує відповідні `db_dsn` для незалежного запуску сервісів. База `jane`
  залишається лише для адміністративного облікового запису dev-стеку; сервіси до неї не підключаються.
- **Образи.** `JANE_IMAGE_<СЕРВІС>` (наприклад `JANE_IMAGE_MINIO`) — замінити реєстр або версію. Образ testsite
  збирається з тегом `<проєкт>-testsite`, тож паралельні стеки не перезаписують образ одне одного.
- **SeaweedFS.** Розмір тому — `JANE_S3_VOLUME_SIZE_LIMIT_MB` (типово 64).
- **Застосунки.** Профілі вимкнені за замовчуванням, щоб `just up` не будував усі образи. `just up
  assistant` також піднімає `llm` і PostgreSQL; `registry` піднімає PostgreSQL і MinIO. Окремі бази
  створює `pg-provision` до запуску застосунку; приклад storage — `infra/config/storage-connections.json`.
  Його host-файл можна підмінити через `JANE_STORAGE_CONNECTIONS_FILE_HOST` (абсолютний шлях). Додаткові URL
  сусідів для assistant задавайте лише коли відповідні сервіси запущені. Для handler-runtime потрібен
  налаштований образ пісочниці (`JANE_HANDLER_RUNTIME_PROFILE_IMAGES`), якщо запускати екстрактори.
  Оркестратор бере `JANE_ORCHESTRATOR_SCHEDULER_ENABLED` і `JANE_ORCHESTRATOR_RUN_WORKERS` (типово `true`) із
  середовища `just up`: `false` — API без розкладів і воркерів на час резервування, відновлення чи оновлення
  ([backup-restore.md](../docs/operations/backup-restore.md)).
- **Автентифікація (ADR-0005).** Застосунки стартують у `AUTH_MODE=api_key`. `just up` генерує ключ для кожної
  ідентичності (`JANE_API_KEY_<ID>`, зокрема `ADMIN`) і його SHA-256 (`JANE_API_KEY_<ID>_SHA256`) у
  `.jane/stack-<проєкт>.json`; сервіси отримують лише хеші з scopes кожного клієнта, а власний ключ для викликів
  сусідів — із середовища. Ключ адміністратора для адмінки: `just env` → `JANE_STACK_AUTH_ADMIN_API_KEY`.
  Матриця «хто кого викликає» — [docs/operations](../docs/operations/README.md#автентифікація-adr-0005);
  `infra/tests/test_auth_config.py` перевіряє її без стеку.
- **Ключі зовнішніх провайдерів (ADR-0006).** `llm` бачить `.jane/secrets/` checkout (або `JANE_SECRETS_DIR`)
  лише для читання як `/run/secrets`: один файл — один секрет, у базі лише посилання `file:/run/secrets/<файл>`.
  `.jane/` поза Git. Реальний Anthropic — `scripts/llm_anthropic.py` ([services/llm](../services/llm/README.md)).
- **Статика адмінки.** `just up` підмонтовує `web/admin/dist`, якщо тека вже існує; інакше Caddy показує
  службову сторінку з `infra/proxy/empty`. Зібрати `dist` — `corepack pnpm --dir web/admin build` (вище);
  `just web` — повна перевірка адмінки (install, lint, typecheck, test, build), як job `web` у CI. Прямий
  `docker compose` приймає `JANE_ADMIN_DIST_PATH`.
  `/config.json` береться з `infra/proxy/admin-config.json`; для іншого середовища задайте
  `JANE_ADMIN_CONFIG_PATH` до власного JSON-файлу. Після зміни файлу образ адмінки перебудовувати не треба.
- **Тести.** `jane_kit.devstack.load_stack()` повертає адреси й облікові дані (або `None`, якщо стек не
  запущено — тоді інтеграційні тести пропускаються). Береться стек **цього** checkout (типове ім'я проєкту);
  `just integration --project <ім'я>` задає інший (через `JANE_STACK_FILE`).

Прямий запуск без just: задати змінні `JANE_PG_PASSWORD`, `JANE_MSSQL_SA_PASSWORD`,
`JANE_MONGO_PASSWORD`, `JANE_MINIO_SECRET_KEY`, `JANE_S3_SECRET_KEY`, усі шість
`JANE_PG_*_PASSWORD` із таблиці вище і для застосунків — `JANE_API_KEY_<ID>` та `JANE_API_KEY_<ID>_SHA256`
(генерує `jane_kit.devstack.new_api_keys()`). Спершу `docker compose -f infra/compose.yaml -p <унікальне-ім'я>
up -d --wait postgres`, потім `docker compose -f infra/compose.yaml -p <те саме ім'я> run --rm
--no-deps pg-provision`, далі `up -d --wait <сервіс>`. Для звичайної роботи `just up` робить це сам.

## Чому SeaweedFS як S3-замінник

Адаптери `s3` і `minio` (WP-08) мають перевірятися на **різних** реалізаціях S3 API, інакше тест «S3 на
сумісному замінникові» (ТЗ §12, критерій 12) фактично повторює тест MinIO.

- **SeaweedFS** — незалежна реалізація (Apache-2.0), S3-шлюз з автентифікацією SigV4 за ключами з
  конфігурації, легкий образ, стартує за секунди, без облікового запису чи ліцензійного ключа. Обрано.
- LocalStack — емулює весь AWS, важкий для одного S3; за оголошеною політикою LocalStack нові версії образу
  вимагають токен облікового запису (не перевірялося в цьому WP).
- Zenko CloudServer, Garage, adobe/s3mock — робочі альтернативи; SeaweedFS має ширше покриття API
  (multipart, versioning, presigned URL) і активну підтримку.

Обмеження: SeaweedFS не реалізує весь S3 API (наприклад, частину політик бакетів і Object Lock) — адаптер S3
має обмежуватися операціями, спільними для AWS S3, MinIO і SeaweedFS. Перевірка на реальному AWS S3 — «не
перевірено на реальному сервісі», доки немає тестового доступу.

## Чому `pgsty/minio`

Upstream MinIO припинив публікацію образів у Docker Hub і `quay.io` (станом на 2026-09 обидва недоступні без
авторизації). `pgsty/minio` — збірка того самого сервера MinIO (AGPLv3) спільнотою Pigsty. Якщо у вашому
середовищі є доступ до іншого образу MinIO, задайте `JANE_IMAGE_MINIO`.

**Ризик постачальника.** Це сторонній образ, не від MinIO, Inc.: його можуть змінити, перестати оновлювати
або видалити, і ми не контролюємо ланцюжок збірки. Тому образ закріплено за digest
(`sha256:b6bfe7239bfc83fb90d31612d9704d86039dd714f7904b3f1ad68f211e602372`) — підміна тегу не змінить того, що
запускається. Образ використовується лише в локальному dev-стеку й CI (не в робочому середовищі), без
секретів поза згенерованими для стеку. Оновлення — свідомо: новий тег і digest у `infra/compose.yaml`,
перевірка `just up` + `just integration`. Якщо образ зникне — `JANE_IMAGE_MINIO` на інший образ сервера MinIO
(наприклад, власну збірку з вихідного коду).

## Reverse proxy

Caddy (`infra/proxy/Caddyfile`): `/_proxy/health`, `/testsite/*` (з `X-Forwarded-Prefix`),
`/api/<service>/*` для всіх сервісів і статика адмінки. Префікс `/api/<service>` видаляється перед
передаванням запиту сервісу. CSP, `nosniff` і `Referrer-Policy` встановлюються для відповідей proxy.
Для OIDC додайте довірене джерело до `JANE_CSP_CONNECT_SRC` і `JANE_CSP_FORM_ACTION` (типово порожні).
Незапущений профіль поверне 502 на своєму API-маршруті; невідомий API-маршрут — 404.
