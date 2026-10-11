# Dev-стек Jane

`infra/` описує локальний стек Docker Compose для розробки, інтеграційних тестів і ручної перевірки платформи: інфраструктурні сервіси (PostgreSQL, SQL Server, MongoDB, MinIO, S3-сумісне сховище), тестовий сайт, reverse proxy з адмінкою та сервіси Jane. Стек запускається командою `just up`, яка дає кожному checkout власний compose-проєкт, порти й згенеровані облікові дані.

Стек не є production-розгортанням: порти відкриваються лише на `127.0.0.1`, облікові дані зберігаються у файлі поза Git, образи збираються з поточного checkout.

## Зміст

- [Склад каталогу](#склад-каталогу)
- [Сервіси стеку](#сервіси-стеку)
- [Запуск і зупинка](#запуск-і-зупинка)
- [Ізоляція проєктів і порти](#ізоляція-проєктів-і-порти)
- [Облікові дані](#облікові-дані)
- [PostgreSQL: бази й ролі сервісів](#postgresql-бази-й-ролі-сервісів)
- [Proxy і адмінка](#proxy-і-адмінка)
- [Локальне доповнення compose.local.yaml](#локальне-доповнення-composelocalyaml)
- [Тести стеку](#тести-стеку)
- [Обмеження](#обмеження)

## Склад каталогу

```text
infra/
├── compose.yaml                  # опис стеку; параметризується змінними JANE_*
├── compose.local.example.yaml    # приклад локального з'єднання сервісів між собою
├── config/
│   └── storage-connections.json  # підключення Storage у dev-стеку (лише secret_refs)
├── postgres/
│   ├── provision.sh              # запускає provision.sql у контейнері pg-provision
│   └── provision.sql             # бази й LOGIN-ролі сервісів, відкликання прав PUBLIC
├── proxy/
│   ├── Caddyfile                 # єдина точка входу: адмінка, /api/<сервіс>/, /testsite/
│   ├── admin-config.json         # config.json адмінки (базовий шлях API, режим автентифікації)
│   └── empty/index.html          # заглушка, поки web/admin/dist не зібрано
└── tests/                        # інтеграційні тести самого стеку
```

## Сервіси стеку

Без аргументів `just up` запускає інфраструктуру: `postgres`, `sqlserver`, `mongodb`, `minio`, `s3`, `testsite`, `proxy`. Сервіси Jane мають compose-профілі з тією самою назвою й запускаються лише явно: `just up storage orchestrator`.

| Сервіс | Образ або збірка | Порт у контейнері | Змінна хост-порту | Том |
|---|---|---|---|---|
| `postgres` | `postgres:18` | 5432 | `JANE_PORT_POSTGRES` | `postgres-data` |
| `pg-provision` | `postgres:18`, одноразовий | — | — | — |
| `sqlserver` | `mcr.microsoft.com/mssql/server:2022-latest` | 1433 | `JANE_PORT_SQLSERVER` | `sqlserver-data` |
| `mongodb` | `mongo:8.0` | 27017 | `JANE_PORT_MONGODB` | `mongodb-data` |
| `minio` | `pgsty/minio`, закріплений дайджестом | 9000, 9001 | `JANE_PORT_MINIO`, `JANE_PORT_MINIO_CONSOLE` | `minio-data` |
| `s3` | `chrislusf/seaweedfs:4.47` | 8333 | `JANE_PORT_S3` | `s3-data` |
| `testsite` | збірка `tests/fixtures/testsite` | 8080 | `JANE_PORT_TESTSITE` | — |
| `proxy` | `caddy:2-alpine` | 8080 | `JANE_PORT_PROXY` | — |
| `storage` | збірка `services/storage/Dockerfile` | 8000 | `JANE_PORT_STORAGE` | `storage-data` |
| `handler-runtime` | збірка `services/handler-runtime/Dockerfile` | 8000 | `JANE_PORT_HANDLER_RUNTIME` | `storage-data` (лише читання) |
| `web-collector` | збірка `services/web-collector/Dockerfile` | 8101 | `JANE_PORT_WEB_COLLECTOR` | `web-collector-data` |
| `telegram-collector` | збірка `services/telegram-collector/Dockerfile` | 8102 | `JANE_PORT_TELEGRAM_COLLECTOR` | `telegram-collector-data` |
| `orchestrator` | збірка `services/orchestrator/Dockerfile` | 8000 | `JANE_PORT_ORCHESTRATOR` | — (база `jane_orchestrator`) |
| `registry` | збірка `services/registry/Dockerfile` | 8000 | `JANE_PORT_REGISTRY` | — (база `jane_registry`, бакет у MinIO) |
| `llm` | збірка `services/llm/Dockerfile` | 8110 | `JANE_PORT_LLM` | `storage-data` (лише читання) |
| `assistant` | збірка `services/assistant/Dockerfile` | 8000 | `JANE_PORT_ASSISTANT` | — (база `jane_assistant`) |

Пояснення до таблиці:

- **Залежності запуску.** Сервіси з базою PostgreSQL і `storage` чекають успішного завершення `pg-provision`; `registry` — ще й здорового `minio`; `assistant` — здорового `llm`; `proxy` — здорового `testsite`. Профіль `assistant` вмикає також `llm`.
- **Health-check.** Інфраструктурні сервіси перевіряються в `compose.yaml`; сервіси Jane — запитом `GET /v1/health` (у `compose.yaml` або `HEALTHCHECK` у Dockerfile). `just up` виконує `docker compose up --wait` і чекає стану `healthy`.
- **Образи.** Кожен образ можна замінити змінною `JANE_IMAGE_<СЕРВІС>`, наприклад `JANE_IMAGE_POSTGRES`, `JANE_IMAGE_MINIO`, `JANE_IMAGE_S3`, `JANE_IMAGE_PROXY`.
- **MinIO.** Upstream більше не публікує образи MinIO, тому типовим є сторонній community-образ `pgsty/minio`, закріплений дайджестом. Це ризик постачальника; іншу збірку MinIO задайте через `JANE_IMAGE_MINIO`.
- **Окреме S3-сумісне сховище.** Сервіс `s3` — шлюз SeaweedFS, а не MinIO. Адаптери Storage `s3` і `minio` перевіряються на двох незалежних реалізаціях протоколу S3.
- **Пісочниця Handler Runtime.** Сервіс монтує Docker-сокет (`JANE_DOCKER_SOCKET`, типово `/var/run/docker.sock`) і групу сокета (`JANE_DOCKER_GID`, типово `0`). Образ пісочниці `jane/python-extractor:1` збирається окремо командою `jane-handler-runtime build-image`; деталі — [Handler Runtime](../docs/components/handler-runtime/README.md).

## Запуск і зупинка

Команди виконуються з кореня репозиторію. Повна послідовність з адмінкою — у [README.md](../README.md#швидкий-старт).

```powershell
just up
just up storage orchestrator registry
just ps
just logs orchestrator
just env
```

- `just up [сервіси]` збирає образи (`--build`), запускає вказані сервіси з їхніми залежностями й чекає health-check (`--wait-timeout`, типово 600 с або `JANE_UP_WAIT_TIMEOUT`). Прапорець `--no-build` пропускає збірку.
- Якщо серед вибраних сервісів є `postgres`, але немає жодного сервісу з базою, `just up` окремо запускає `pg-provision` (`docker compose run --rm`), бо `up --wait` вважає завершений одноразовий контейнер помилкою.
- `just env` друкує адреси й облікові дані як рядки `JANE_STACK_<СЕРВІС>_<КЛЮЧ>=…`; `just env --format json` — як JSON.
- `just logs [сервіси] [--tail N]` показує останні рядки журналів (типово 200).

Зупинка стеку зі збереженням даних:

```powershell
just down
```

Команда нижче зупиняє стек і **видаляє всі його дані**: томи баз і сховищ, локально зібрані образи (`--rmi local`) та файл `.jane/stack-<проєкт>.json` зі згенерованими паролями й ключами.

```powershell
just down -v
```

## Ізоляція проєктів і порти

Кілька стеків можуть працювати на одному хості одночасно, якщо в кожного своя назва compose-проєкту.

- **Назва проєкту.** Типово `jane-<назва каталогу checkout>-<6 символів хешу шляху>`; змінна `JANE_COMPOSE_PROJECT` або аргумент `--project`/`-p` задають іншу. Назви контейнерів, мереж, томів і локально зібраних образів (наприклад `<проєкт>-testsite`) мають префікс проєкту.
- **Хост-порти.** Порожня змінна `JANE_PORT_<СЕРВІС>` означає, що порт вибирає Docker; `just up` читає вибрані порти через `docker compose port` і записує їх у файл стеку. Фіксований порт задається змінною середовища перед `just up`.
- **Адреса прив'язки.** `JANE_BIND`, типово `127.0.0.1`. Стек не відкриває порти назовні, якщо не змінити цю змінну.
- **Файл стеку.** `.jane/stack-<проєкт>.json` (каталог `.jane/` ігнорує Git) містить назву проєкту, облікові дані й адреси сервісів. Його читають `just env`, `just integration` (через `JANE_STACK_FILE`) і `jane_kit.devstack`.

Приклад запуску другого стеку з фіксованими портами PostgreSQL і Orchestrator (PowerShell):

```powershell
$env:JANE_PORT_POSTGRES = "19001"
$env:JANE_PORT_ORCHESTRATOR = "19010"
just up postgres orchestrator --project jane-second
just down -v --project jane-second
```

## Облікові дані

Перший `just up` для проєкту генерує випадкові облікові дані й зберігає їх у `.jane/stack-<проєкт>.json`; наступні запуски беруть їх звідти. У Git облікові дані не потрапляють.

| Призначення | Змінні |
|---|---|
| Суперкористувач PostgreSQL | `JANE_PG_USER` (`jane`), `JANE_PG_PASSWORD`, `JANE_PG_DB` (`jane`) |
| Ролі баз сервісів | `JANE_PG_<СЕРВІС>_PASSWORD` для `HANDLER_RUNTIME`, `ORCHESTRATOR`, `REGISTRY`, `LLM`, `ASSISTANT`, `STORAGE_RESULTS` |
| SQL Server | `JANE_MSSQL_SA_PASSWORD` (користувач `sa`) |
| MongoDB | `JANE_MONGO_USER` (`jane`), `JANE_MONGO_PASSWORD` |
| MinIO | `JANE_MINIO_ACCESS_KEY`, `JANE_MINIO_SECRET_KEY` |
| S3 (SeaweedFS) | `JANE_S3_ACCESS_KEY`, `JANE_S3_SECRET_KEY` |
| Ключі API | `JANE_API_KEY_<ІДЕНТИЧНІСТЬ>` і `JANE_API_KEY_<ІДЕНТИЧНІСТЬ>_SHA256` |

Сервіси Jane працюють у режимі `auth_mode=api_key`. Для кожної ідентичності — `admin`, `orchestrator`, `assistant`, `handler-runtime`, `storage`, `llm`, `web-collector`, `telegram-collector`, `registry` — генерується ключ `jk_…`. Сервіси отримують лише SHA-256 ключів і набір scopes для кожного викликача (`JANE_<СЕРВІС>_API_KEYS` у `compose.yaml`); власний ключ для звернення до сусідів сервіс отримує зі змінної середовища. Ключ оператора для адмінки та API через proxy — `JANE_STACK_AUTH_ADMIN_API_KEY` у виводі `just env`; `just up` його не друкує.

Модель автентифікації й scopes описано в [ADR-0006](../docs/adr/0006-authentication.md), секрети підключень — у [ADR-0007](../docs/adr/0007-secrets-and-connections.md) та [безпеці експлуатації](../docs/operations/security.md).

## PostgreSQL: бази й ролі сервісів

Один сервер PostgreSQL обслуговує кілька сервісів, але кожен має окрему базу й окрему роль. `pg-provision` виконує [provision.sql](postgres/provision.sql) під час кожного `just up`; повторний запуск оновлює паролі ролей і не видаляє даних.

| База | Роль-власник | Сервіс |
|---|---|---|
| `jane_orchestrator` | `jane_orchestrator` | Orchestrator |
| `jane_registry` | `jane_registry` | Registry (схема `jane_registry`) |
| `jane_llm` | `jane_llm` | LLM gateway |
| `jane_assistant` | `jane_assistant` | Assistant |
| `jane_handler_runtime` | `jane_handler_runtime` | Handler Runtime |
| `jane_storage_results` | `jane_storage_results` | Цільове сховище результатів Storage (підключення `results-pg`) |

- Ролі створюються з атрибутами `LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION`; кожна база належить своїй ролі.
- Права `CONNECT` і `TEMPORARY` для `PUBLIC` відкликано на всіх базах стеку, включно з `postgres`, `template1` і `jane`. Роль сервісу не може під'єднатися до чужої бази — це перевіряє `infra/tests/test_stack.py`.
- Таблиці в базах створюють самі сервіси під час старту; `provision.sql` створює лише бази й ролі. Як сервіси оновлюють схеми — [оновлення й міграції](../docs/operations/upgrades.md).
- `jane_storage_results` — не база стану Storage, а приклад цільового сховища користувача. Storage під'єднується до неї через підключення з `secret_refs` (`env:JANE_SECRET_DEV_PG_USER`, `env:JANE_SECRET_DEV_PG_PASSWORD`).

## Proxy і адмінка

`proxy` (Caddy) — єдина точка входу стеку на порту `JANE_PORT_PROXY`:

| Шлях | Куди веде |
|---|---|
| `/` | статичні файли адмінки з `web/admin/dist` (якщо каталог є) або заглушка `proxy/empty` |
| `/config.json` | `proxy/admin-config.json` або файл `JANE_ADMIN_CONFIG_PATH` |
| `/api/<сервіс>/…` | API сервісу без префікса; сервіси: `storage`, `handler-runtime`, `web-collector`, `telegram-collector`, `orchestrator`, `registry`, `llm`, `assistant` |
| `/testsite/…` | тестовий сайт із заголовком `X-Forwarded-Prefix: /testsite` |
| `/_proxy/health` | `200 ok` для health-check proxy |

Proxy додає заголовки `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`. Додаткові джерела для CSP задаються змінними `JANE_CSP_CONNECT_SRC` і `JANE_CSP_FORM_ACTION`. Невідомий шлях `/api/*` повертає `404`.

## Локальне доповнення compose.local.yaml

Базовий `compose.yaml` не з'єднує сервіси між собою: виконавців Orchestrator, адресу Registry для колекторів і Handler Runtime задають тести або локальне доповнення. Щоб отримати робочу систему, скопіюйте [compose.local.example.yaml](compose.local.example.yaml) у `infra/compose.local.yaml` (файл ігнорує Git). `just up`, `just down`, `just ps`, `just logs` додають його до кожного виклику compose. Приклад задає:

- виконавців Orchestrator (`JANE_ORCHESTRATOR_EXECUTORS`) для всіх сервісів;
- `JANE_*_REGISTRY_URL` для колекторів, Handler Runtime, LLM gateway і Assistant;
- збірку Web Collector з Playwright (`EXTRAS: --extra render`) і Telegram Collector з Telethon;
- більші ліміти Web Collector для реальних сайтів. Діє лише `JANE_WEB_COLLECTOR_LIMITS__TRANSFER__INLINE_MAX_BYTES`; змінні `JANE_WEB_COLLECTOR_JOBS__*` сервіс ігнорує, правильна форма — `JANE_WEB_COLLECTOR_LIMITS__JOBS__*` ([ліміти](../docs/operations/limits.md#ліміти-сервісу-файл-і-змінні-середовища)).

CI і наскрізні тести цього файлу не використовують.

## Тести стеку

```powershell
just up
just integration infra/tests
```

- `test_stack.py` — PostgreSQL, ізоляція ролей сервісів, SQL Server, MongoDB, обидва S3-сумісні сховища, тестовий сайт напряму й через proxy.
- `test_auth_config.py` — генератори ключів у `scripts/dev.py`, `deploy/profiles/stack.py` і `jane_kit.devstack` збігаються; сервіси стартують із ключами API; службові ключі сервісів приймаються їхніми сусідами.

## Обмеження

- `postgres:18` монтує том у `/var/lib/postgresql` (а не в `/var/lib/postgresql/data`, як старші образи).
- Docker-сокет у контейнері Handler Runtime дає сервісу керування Docker хоста. Це прийнятно для dev-стеку; для іншого середовища використовуйте окремий Docker/Podman-хост або rootless-рушій.
- `file://`-посилання на збережені RAW працюють лише в межах одного Docker-хоста зі спільним томом `storage-data`.
- Перевірено на Windows 11 з Docker Desktop. Linux-варіант використовується в CI (`ubuntu-24.04`, job `stack`).
