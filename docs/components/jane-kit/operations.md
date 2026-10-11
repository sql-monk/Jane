# jane-kit: експлуатація

Що бібліотека дає для моніторингу сервісу, як оновлювати її та таблиці сховищ і як розпізнати типові проблеми. Окремого процесу бібліотека не має: усе нижче стосується сервісу, що її використовує.

## Зміст

- [Health](#health)
- [Метрики](#метрики)
- [Журнали](#журнали)
- [Оновлення бібліотеки](#оновлення-бібліотеки)
- [Міграції й прибирання таблиць](#міграції-й-прибирання-таблиць)
- [Масштабування](#масштабування)
- [Власність даних](#власність-даних)
- [Типові проблеми](#типові-проблеми)

## Health

`GET /v1/health` (без автентифікації) повертає `{"status": "ok" | "degraded" | "down", "checks": {...}}`. Статус — найгірший серед перевірок; `down` дає HTTP `503`, інші — `200`. Кожна перевірка обмежена `health_check_timeout_ms`; тайм-аут або виняток дає `down` для критичної перевірки й `degraded` — для некритичної. Перевірки додає сервіс через `app.state.health.add(...)`.

`GET /v1/info` (будь-який чинний токен) показує `service`, `version`, `api_versions`, `capabilities`, `auth_mode` і `limits` (`PlatformLimits` сервісу).

## Метрики

`GET /metrics` — формат Prometheus; без токена, якщо `metrics_public=true`. Вимикається `metrics_enabled=false`.

| Метрика | Тип | Мітки | Зміст |
|---|---|---|---|
| `jane_http_requests_total` | counter | `method`, `route`, `status` | Запити за шаблоном маршруту |
| `jane_http_request_duration_seconds` | histogram | `method`, `route` | Тривалість запиту |
| `jane_http_requests_in_flight` | gauge | — | Запити в обробці |
| `jane_service_info` | gauge | `service` | Завжди `1`; назва сервісу |

Запити до неіснуючих маршрутів мають `route="__unmatched__"`. Реєстр метрик окремий для кожного застосунку, тож два застосунки в одному процесі (тести) не змішують лічильники. Власні метрики сервісу мають той самий префікс `jane_`.

## Журнали

Кожен запис — один JSON-рядок у stdout (`log_format=json`):

| Поле | Зміст |
|---|---|
| `ts` | Час UTC з мілісекундами |
| `level` | `debug`, `info`, `warning`, `error`, `critical` |
| `logger` | Назва логера: `jane.access`, `jane.service`, `jane.auth`, логери сервісу |
| `msg` | Повідомлення |
| `service`, `instance` | `service_name` і `instance_id` |
| `trace_id`, `request_id` | Контекст запиту |
| інші | Поля `bind_context` (`job_id`, `source_id`…) і `extra=` виклику |
| `exc` | Трасування винятку |

Записи старту: `service starting` (версія, порт), режим автентифікації (`authentication enabled` з назвами ключів або попередження `auth_mode=none`), записи `platform limits profile applied partially` з `ignored` для лімітів спільного профілю, яких сервіс не має. Доступ: `jane.access` з `method`, `path`, `status`, `duration_ms` для кожного запиту, крім `/v1/health` і `/metrics`. Журнал uvicorn іде через той самий формат, його власний access-журнал вимкнено. Для читання в консолі — `log_format=console`.

## Оновлення бібліотеки

Бібліотека — член uv workspace, тож сервіси репозиторію завжди використовують її поточну версію з `libs/jane-kit`. Після зміни бібліотеки:

```powershell
uv sync --all-packages
just test jane-kit
just check
```

Образи сервісів копіюють `libs/` під час збирання (див. `Dockerfile` сервісу), тому для розгортання зміни потрібно перезібрати образи всіх сервісів. Публічні імена модулів перелічено в `__all__`; зміна їх сигнатур зачіпає всі сервіси — перевіряйте повним `just check`.

## Міграції й прибирання таблиць

- Таблиці сховищ створюються й оновлюються на старті сервісу (`migrate` для PostgreSQL, `migrate()` сховища для SQLite) — окремої команди міграції немає.
- Схема лише розширюється: нові стовпці додаються `ADD COLUMN IF NOT EXISTS`; старі розкладки читаються без перенесення даних.
- Завершені job видаляються після `job_retention_seconds` (під час створення нового job і в сховищі в пам'яті — під час доступу); прострочені ключі ідемпотентності — `gc` (PostgreSQL) або під час наступного захоплення того самого ключа.
- Резервування: таблиці — частина бази сервісу і резервуються разом із нею. Втрата таблиці job означає `404` для старих `job_id`; втрата таблиці ключів — повтор запиту з тим самим ключем виконується знову.

## Масштабування

- Кілька екземплярів одного сервісу потребують спільних сховищ (`jane_kit.stores`); сховища в пам'яті дають кожному екземпляру власний стан, і `GET /v1/jobs/{id}` на іншому екземплярі поверне `404`.
- `instance_id` унікальний для кожного старту, тож перезапуск у тому самому контейнері не «успадковує» оренд попереднього процесу.
- Паралельність у межах екземпляра — `JobLimits.max_concurrent_jobs`; понад `max_queued_jobs` — `503` з `Retry-After` (зворотний тиск).

## Власність даних

Бібліотека власних даних не має. Таблиці `idempotency` і `jobs` належать сервісу, у базі якого створені; інший сервіс читає їх лише через API (`GET /v1/jobs/{job_id}`). Загальна карта — [contracts/docs/data-ownership.md](../../../contracts/docs/data-ownership.md).

## Типові проблеми

| Симптом | Причина | Що зробити |
|---|---|---|
| Старт падає з `AuthConfigError: auth_mode=api_key needs at least one key` | Режим `api_key` без `API_KEYS` / `API_KEYS_FILE` | Задати ключі або `AUTH_MODE=none` для локальної роботи |
| `auth_mode=none is for local tests and listens on loopback only` | `HOST=0.0.0.0` з режимом `none` | Увімкнути `api_key` або `jwt` |
| `routes without a scope in the service's auth table` | Новий маршрут не внесено в `auth_scopes` | Додати рядок `"METHOD /path": "scope"` |
| `LimitError: ... unknown limit(s)` | Помилка в назві ліміту у файлі, змінній чи запиті | Звірити шлях із моделлю `Limits` сервісу |
| `LimitError: ... hard cap ... loosens` | Нижчий шар піднімає стелю | Стелю можна лише зменшувати |
| `ContractsNotFound: contracts/schemas not found` | У образі чи каталозі немає `contracts/` | Задати налаштування сервісу або `JANE_CONTRACTS_DIR` |
| Усі запити `503` у режимі `jwt` | JWKS недоступний і кешу ключів немає | Перевірити `jwt_jwks_url`; повтор — після `jwt_jwks_refresh_cooldown_seconds` |
| `409 idempotency_in_progress` довше за звичайне | Екземпляр, що захопив ключ, зупинився | Повторити після `in_progress_lease_ms` (типово 15 хв) — ключ перехопиться |
| `503 service_unavailable`, `job queue is full` | Досягнуто `max_concurrent_jobs + max_queued_jobs` | Повторити після `Retry-After` або збільшити ліміти |
| Job `failed` з `service_unavailable` і `job lease expired` | Екземпляр-власник зупинився під час виконання | Повторити запит (`retryable: true`) |
