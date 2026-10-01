# Експлуатація Jane v1

Інструкції описують фактичний стан `main` після WP-01a: усі сервіси мають образи й профілі в
`infra/compose.yaml`, Caddy віддає їх за `/api/<сервіс>/*`, `just e2e` проганяє приймальні сценарії.
Перевірені середовища — `dev-laptop` (Windows 11 + Docker Desktop, ця машина) і `ci`
(GitHub Actions `ubuntu-latest`) — див. [рішення людини](../delivery/WP-14.md). `single-node` — кандидат,
**не перевірено на реальному середовищі**. Числа профілів ще не виміряні (фаза 2,
[протокол](limits-validation.md)).

## Три способи запуску

| Що потрібно | Команда | Що піднімається |
|---|---|---|
| Інфраструктура для розробки й інтеграційних тестів | `just up [сервіси]`, `just env`, `just down -v` | PostgreSQL (+ окремі БД/ролі сервісів), SQL Server, MongoDB, MinIO, SeaweedFS (S3), testsite, Caddy; застосунки — лише названі (`just up registry storage`) |
| Приймальні сценарії WP-13 | `just e2e -v` | власний проєкт `jane-e2e-*`, накладка `tests/e2e/compose.e2e.yaml`, прибирання після тестів |
| Увесь ланцюжок з профілем лімітів (приклади, вимірювання) | `uv run --all-packages python deploy/profiles/stack.py up --profile dev-laptop [--telegram] [--probe]` | testsite, registry, storage, handler-runtime (+ образ пісочниці), web-collector, orchestrator, за потреби telegram-collector і probe-site; `stack.py down` прибирає все |

Для паралельної роботи задавайте різні compose-проєкти: `just up --project <назва>`,
`stack.py up --project <назва>`. Порти обирає Docker (лише `127.0.0.1`), паролі генеруються у
`.jane/stack-<проєкт>.json` (у `.gitignore`); `just env --project <назва>` і `stack.py env --project <назва>`
показують адреси. Не копіюйте паролі у звіти. `just down -v` і `stack.py down` видаляють томи.

## Незалежний запуск компонента

Кожен сервіс працює без оркестратора (ТЗ §4) і описує запуск у своєму README:
[web-collector](../../services/web-collector/README.md), [telegram-collector](../../services/telegram-collector/README.md),
[handler-runtime](../../services/handler-runtime/README.md), [storage](../../services/storage/README.md),
[registry](../../services/registry/README.md), [llm](../../services/llm/README.md),
[assistant](../../services/assistant/README.md), [orchestrator](../../services/orchestrator/README.md).

1. `uv sync --all-packages`; для сервісу з власною БД — `just up postgres` (роль і БД створює `pg-provision`,
   DSN сервісу — `just env --format json` → `db-<сервіс>.db_dsn`).
2. Процесом: `uv run --package jane-<сервіс> python -m jane_<сервіс>`; або контейнером: `just up <сервіс>`
   (профіль compose = ім'я сервісу, залежності стартують автоматично).
3. Перевірте `GET /v1/health`, `GET /v1/info` (можливості, ліміти й стелі), `GET /metrics`. Через Caddy ті самі
   шляхи доступні як `http://<proxy>/api/<сервіс>/v1/...` (незапущений сервіс → 502, невідомий → 404).
4. Ліміти сервісу — типові значення з README сервісу, `<ПРЕФІКС>_LIMITS__<ГРУПА>__<ПОЛЕ>` або
   `<ПРЕФІКС>_LIMITS_FILE`. Увесь профіль `deploy/profiles/<profile>.json` як `LIMITS_FILE` приймає **кожен**
   сервіс (storage, handler-runtime, registry, llm, assistant — з WP-01b): ліміти, яких сервіс не має,
   ігноруються з рядком журналу старту, опечатка — помилка старту (колектори поки ігнорують і опечатки,
   запит WP-01b до WP-02/WP-04); `GET /v1/info` → `limits.profile`.
   orchestrator бере файл лише для першого заповнення документа лімітів у БД. Змінні
   `<ПРЕФІКС>_LIMITS__<ГРУПА>__<ПОЛЕ>` перекривають файл. Для llm профіль задає й тайм-аут виклику провайдера
   (`provider.request_timeout_ms` = `timeouts.request_timeout_ms` профілю, 30 с): для реальної моделі перекрийте
   `JANE_LLM_LIMITS__PROVIDER__REQUEST_TIMEOUT_MS` (стек профілю — 120 000, див. `deploy/profiles/README.md`).

## Спільний запуск (ланцюжок)

Готова конфігурація — [`deploy/profiles/compose.stack.yaml`](../../deploy/profiles/compose.stack.yaml) поверх
`infra/compose.yaml`; `stack.py` задає змінні. Що вона з'єднує і що треба повторити в іншому розгортанні:

1. **Registry** — власна БД `jane_registry` і бакет MinIO/S3; `JANE_REGISTRY_RUNTIME_PROFILES` вказує на
   `http://handler-runtime:8000/v1/info` (перевірка `dependencies.python`).
2. **Handler-runtime** — `JANE_HANDLER_RUNTIME_REGISTRY_URL` (архіви за дайджестом),
   `JANE_HANDLER_RUNTIME_PROFILE_IMAGES` (образ профілю `python-extractor@1`, у проді — за дайджестом),
   доступ до Docker API для пісочниць (`/var/run/docker.sock`, група сокета в контейнері).
3. **Колектори** — `JANE_WEB_COLLECTOR_REGISTRY_URL` / `JANE_TELEGRAM_COLLECTOR_REGISTRY_URL` для `rules_ref`.
4. **Storage** — підключення `raw-files` (filesystem) і `results-pg` (PostgreSQL, `secret_refs` на
   `env:JANE_SECRET_*`); те саме оркестратор тримає як джерело правди й синхронізує (`PUT /v1/connections/{id}`).
5. **Orchestrator** — `JANE_ORCHESTRATOR_EXECUTORS_FILE`: колектори (`capabilities.collector`), storage
   (`packages: ["jane.storage-*"]`) і `storage_read`, handler-runtime (`default`, `handler_kinds`), registry.
   `stack.py` генерує цей файл лише для запущених сервісів. `JANE_ORCHESTRATOR_LIMITS_FILE` — профіль для
   **першого** заповнення лімітів платформи в БД.
6. Після старту: health усіх сервісів, `GET /v1/executors` оркестратора, `GET /v1/limits/platform` (поле
   `profile`), один малий контрольований запуск. Робочий приклад усього цього —
   [`examples/`](../../examples/README.md) (`jane_examples.py demo`).

У робочому середовищі додатково: автентифікація (`AUTH_MODE=api_key`, окремі ключі й scopes), TLS і
reverse proxy (Caddy з `/api/<сервіс>/*` і CSP — `infra/proxy/Caddyfile`), секрети лише через
`secret_refs` з дозволеним префіксом, окремі облікові записи БД (як `pg-provision`), закріплені образи.

## Зміна лімітів без зміни коду

1. Прочитайте `GET /v1/limits/platform`, збережіть `ETag`, передайте новий документ `PUT /v1/limits/platform`
   з `If-Match` (право `orchestrator:admin`). Для джерела чи завдання — поле `limits` у
   `PUT /v1/sources/{id}` / `PUT /v1/tasks/{id}` (теж з ETag).
2. Перевірте `GET /v1/limits/effective?source_id=&task_id=&stage_id=` — значення й походження
   (`platform` / `source` / `task` / `stage` / `hard_cap`).
3. Нові значення діють для **нових** запусків (запуск фіксує ефективні ліміти на старті). Обмеження сайту
   (`robots.txt` Crawl-delay, `Retry-After`), flood-wait Telegram і ліміти провайдера LLM лише звужують.

Перевірено сценарієм WP-13 S-M2-09 (`tests/e2e/test_m2_limits.py`: `crawl.max_pages_per_run` platform → task)
і прикладом WP-14 (`verify`: частота з рівня `source`, `max_pages_per_run` з рівня `task`). Темп запитів
вимірює фаза 2.

## Оновлення, міграції та відкат

1. Зафіксуйте ревізії коду, образів, контрактів, пакетів і дайджестів активних етапів, `ETag` платформних
   лімітів. Вимкніть розклади (`schedule.enabled: false` через `PUT /v1/tasks/{id}` або
   `JANE_ORCHESTRATOR_SCHEDULER_ENABLED=false`) і дочекайтеся завершення або скасуйте активні запуски
   (`POST /v1/runs/{id}/cancel`).
2. Зробіть узгоджену копію за [резервуванням і відновленням](backup-restore.md) і перевірте її відновлення
   в ізольованому проєкті.
3. Міграції: orchestrator (`Database.migrate()`), registry (таблиці під advisory lock), handler-runtime,
   llm і assistant створюють/оновлюють **свої** схеми під час старту; колектори — власні SQLite-файли стану.
   Автоматичної сумісності довільного відкату це не гарантує.
4. Оновлюйте по одному сервісу (`docker compose ... up -d --build <сервіс>`), перевіряючи health, журнали
   міграції, контрактні smoke-запити й `GET /v1/executors`. При помилці зупиніть нові записи; відкат коду
   після зміни схеми — лише за документованої сумісності, інакше разом із відновленням копії даних.
5. Пакети обробників незмінні: оновлення — нова версія в registry, активація через
   `POST /v1/tasks/{id}/stages/{stage}/activations` (версія `approved`), відкат — `kind: rollback`.
