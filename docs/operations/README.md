# Експлуатація Jane v1

Інструкції описують `main`: усі сервіси мають образи й профілі в `infra/compose.yaml`, Caddy віддає їх за
`/api/<сервіс>/*`, `just e2e` проганяє приймальні сценарії. Профілі лімітів
([`deploy/profiles/`](../../deploy/profiles/README.md)): `ci` (GitHub Actions `ubuntu-latest`) прийнято за живими
вимірюваннями job `limits` — CI [36921026070](https://github.com/sql-monk/Jane/actions/runs/36921026070) `pass`,
[36952287098](https://github.com/sql-monk/Jane/actions/runs/36952287098) `warn` без блокерів, останній на `main` —
[37811082079](https://github.com/sql-monk/Jane/actions/runs/37811082079) `pass`. `dev-laptop` і `single-node` —
кандидати, **не перевірено на реальному середовищі**: вимірювання `dev-laptop` виключено з обсягу
[рішенням людини 2026-10-08](../delivery/WP-14.md#рішення-людини-2026-10-08-і-стан-критерію-13)
([протокол](limits-validation.md)).

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
   Процес без налаштувань працює в `AUTH_MODE=none` (лише `127.0.0.1`); контейнер `just up` — в `api_key`:
   `GET /v1/info` і решта API потребують `Authorization: Bearer <ключ>` (адміністратора — з `just env`,
   `JANE_STACK_AUTH_ADMIN_API_KEY`), без токена відповідає лише `/v1/health` (і `/metrics`).
4. Ліміти сервісу — типові значення з README сервісу, `<ПРЕФІКС>_LIMITS__<ГРУПА>__<ПОЛЕ>` або
   `<ПРЕФІКС>_LIMITS_FILE`. Увесь профіль `deploy/profiles/<profile>.json` як `LIMITS_FILE` приймає **кожен**
   сервіс (storage, handler-runtime, registry, llm, assistant — з WP-01b): ліміти, яких сервіс не має,
   ігноруються з рядком журналу старту, опечатка — помилка старту (колектори поки ігнорують і опечатки,
   запит WP-01b до WP-02/WP-04); `GET /v1/info` → `limits.profile`.
   orchestrator бере файл лише для першого заповнення документа лімітів у БД. Змінні
   `<ПРЕФІКС>_LIMITS__<ГРУПА>__<ПОЛЕ>` перекривають файл. Тайм-аут виклику моделі llm — власний ліміт
   `provider.request_timeout_ms` (типово 120 000), профіль його не змінює; для повільної моделі —
   `JANE_LLM_LIMITS__PROVIDER__REQUEST_TIMEOUT_MS` (див. `deploy/profiles/README.md`). Асистент чекає виклик llm
   за `llm_call.request_timeout_ms` (типово 900 000) або бере режим `async`.

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

У робочому середовищі додатково: автентифікація (`AUTH_MODE=jwt` з IdP або `api_key` з окремими ключами й
scopes на кожного клієнта — див. «Автентифікація (ADR-0005)» нижче), TLS і reverse proxy (Caddy з
`/api/<сервіс>/*` і CSP — `infra/proxy/Caddyfile`), секрети лише через `secret_refs` з дозволеним префіксом,
окремі облікові записи БД (як `pg-provision`), закріплені образи.

## Автентифікація (ADR-0005)

**Що змінилося в M3.** До M3 перевірку токена мали лише orchestrator і registry (режим `api_key`); у
storage, handler-runtime, llm, web-collector, telegram-collector і assistant `AUTH_MODE=api_key` лише
показувався в `/v1/info` і **нічого не захищав**. Тепер усі 8 сервісів перевіряють токен і scope кожної
операції однаковим модулем `jane_kit.auth`, а dev-стек, e2e-стеки й стек профілів працюють у `api_key`.

Режими (`<PREFIX>AUTH_MODE` кожного сервісу; повний перелік змінних — [jane-kit](../../libs/jane-kit/README.md#автентифікація-adr-0005)):

- `none` — лише локальні тести: сервіс приймає всіх, пише попередження й відмовляється стартувати з `HOST`, що
  не є loopback (виняток — явне `AUTH_NONE_ALLOW_REMOTE=true` для ізольованої тестової мережі);
- `api_key` — ключі в конфігурації лише хешем (`API_KEYS` / `API_KEYS_FILE`: `sha256` або `secret_ref`
  `env:`/`file:`), scopes на кожен ключ; типовий режим dev-стеку;
- `jwt` — RS256/ES256 за JWKS IdP (`JWT_JWKS_URL`, `JWT_ISSUER`, `JWT_AUDIENCE`), scopes у claim `scope`;
  рекомендований для прод. Перевірено лише з локальним JWKS у тестах; з реальним IdP (Keycloak, Entra ID)
  — **не перевірено на реальному сервісі**.

Без токена працюють лише `/v1/health` і (типово) `/metrics`; `/v1/info` приймає будь-який дійсний токен.
Неповна конфігурація (`api_key` без ключів, `jwt` без JWKS/issuer/audience, нерозв'язне `secret_ref`) —
сервіс не стартує. Scopes операцій — `jane_kit.auth_scopes` (тест звіряє їх із контрактами) і README сервісів.

**Dev-стек.** `just up` генерує в ігнорований `.jane/stack-<project>.json` по ключу на кожну ідентичність
(`admin`, `orchestrator`, `assistant`, `handler-runtime`, `storage`, `llm`, `web-collector`,
`telegram-collector`, `registry`): `JANE_API_KEY_<ID>` — ключ, `JANE_API_KEY_<ID>_SHA256` — хеш, який
перевіряють сервіси (`infra/compose.yaml`; у git немає ні ключів, ні хешів). Ключ адміністратора показує
`just env` (`JANE_STACK_AUTH_ADMIN_API_KEY`); його вводять на сторінці входу адмінки, а для реального
e2e адмінки передають як `JANE_ADMIN_E2E_API_KEY`. Хто кого викликає власним ключем:

| Ідентичність | Приймають (scopes) |
|---|---|
| `admin` | усі сервіси, усі scopes своїх API |
| `orchestrator` | колектори (`collector:read`, `collector:run`, `connections:write`), handler-runtime і storage (`handler:invoke`, `connections:write`, storage ще `storage:read`), llm (`handler:invoke`, `connections:write`, `llm:admin`), registry (`registry:read`) |
| `assistant` | llm (`llm:invoke`), registry (`registry:read`, `registry:write`, `registry:approve`, `actor: llm`), колектори (`collector:read`, `collector:run`), handler-runtime (`handler:invoke`, `handler:test`), storage (`storage:read`), orchestrator (`orchestrator:read`, `orchestrator:write`) |
| `handler-runtime`, `storage`, `llm`, `web-collector`, `telegram-collector` | registry (`registry:read`) |
| `registry` | handler-runtime (без scopes: лише `GET /v1/info` для профілів runtime) |

Свій токен кожен сервіс бере із середовища: orchestrator — `SERVICE_TOKEN_REF` (або `token_ref` виконавця;
відкритий `token` у `EXECUTORS_FILE` застарів), assistant — `SERVICE_TOKEN_REF` чи окремий `*_TOKEN_REF`
для кожного сусіда, registry — `RUNTIME_PROFILES_TOKEN_REF`, handler-runtime/storage/llm — `REGISTRY_TOKEN`,
колектори — `REGISTRY_TOKEN_ENV`. Ключ іншого розгортання додають так само: згенерувати випадкове значення,
віддати його клієнту через секрет середовища, а в `API_KEYS` сервісу записати лише `sha256` і scopes.

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
   лімітів. Вимкніть розклади (`schedule.enabled: false` через `PUT /v1/tasks/{id}` або для всього
   оркестратора `JANE_ORCHESTRATOR_SCHEDULER_ENABLED=false`, разом із воркерами —
   `JANE_ORCHESTRATOR_RUN_WORKERS=false`; обидві змінні задаються в середовищі `just up` / `stack.py up`,
   типово `true`, команди — у [резервуванні](backup-restore.md#копіювання)) і дочекайтеся завершення або
   скасуйте активні запуски (`POST /v1/runs/{id}/cancel`).
2. Зробіть узгоджену копію за [резервуванням і відновленням](backup-restore.md) і перевірте її відновлення
   в ізольованому проєкті.
3. Міграції: orchestrator (`Database.migrate()`), registry (таблиці під advisory lock), handler-runtime,
   llm і assistant створюють/оновлюють **свої** схеми під час старту; колектори — власні SQLite-файли стану.
   Автоматичної сумісності довільного відкату це не гарантує.
4. Оновлюйте по одному сервісу: `just up --project <P> <сервіс>` (dev-стек; перебудовує образ і перестворює
   лише змінений контейнер) або та сама команда `stack.py up --project <P> --profile <профіль> [--telegram]`, що
   піднімала стек (коротший `--services` перезапише файл виконавців оркестратора). Без обгорток —
   `docker compose -f infra/compose.yaml -p <P> up -d --build --wait <сервіс>` зі змінними `env` з
   `.jane/stack-<P>.json`; накладку профілю — лише через `stack.py` (він задає ще `JANE_PROFILE_FILE`,
   `JANE_EXECUTORS_FILE` тощо). Перевіряйте health, журнали
   міграції, контрактні smoke-запити й `GET /v1/executors`. При помилці зупиніть нові записи; відкат коду
   після зміни схеми — лише за документованої сумісності, інакше разом із відновленням копії даних.
5. Пакети обробників незмінні: оновлення — нова версія в registry, активація через
   `POST /v1/tasks/{id}/stages/{stage}/activations` (версія `approved`), відкат — `kind: rollback`.
