# Web Collector: експлуатація

Моніторинг, оновлення, резервування, відновлення й масштабування Web Collector, а також типові проблеми. Експлуатація платформи загалом — у [docs/operations](../../operations/README.md).

## Зміст

- [Власність даних](#власність-даних)
- [Моніторинг](#моніторинг)
- [Запуск у Docker](#запуск-у-docker)
- [Оновлення й міграції](#оновлення-й-міграції)
- [Резервування й відновлення](#резервування-й-відновлення)
- [Масштабування](#масштабування)
- [Типові проблеми](#типові-проблеми)

## Власність даних

| Дані | Де | Власник | Втрата означає |
|---|---|---|---|
| Збори, черга, буфер матеріалів, помилки | `STATE_DIR/state.db` | Web Collector | непідтверджені матеріали й незавершені збори втрачено; їх можна зібрати знову |
| Історія URL за `state_key` | той самий файл | Web Collector | наступний `incremental` завантажить усе, як `full` |
| Підключення `kind=http` | той самий файл | Web Collector | підключення треба створити знову (секрети в них не зберігаються) |
| Транзитні blob | `TRANSIT_DIR` | Web Collector | посилання `file://` у матеріалах стануть недійсними |
| Бізнес-результати | — | обробники Storage | колектор їх не зберігає |

## Моніторинг

**Стан.** `GET /v1/health` перевіряє доступність файла стану:

```json
{"status":"ok","checks":{"state_store":{"status":"ok"}}}
```

Docker-образ використовує цей ендпойнт як `HEALTHCHECK`.

**Метрики.** `GET /metrics` (Prometheus) — спільні метрики HTTP `jane-kit`: `jane_http_requests_total{method,route,status}`, `jane_http_request_duration_seconds`, `jane_http_requests_in_flight`, `jane_service_info`. Власних метрик збору немає; прогрес збору видно в `GET /v1/jobs/{id}` (`progress.counters`, оновлюється з кожним heartbeat) і в `stats` збору.

**Що відстежувати:**

| Ознака | Де | Що означає |
|---|---|---|
| `paused_by_backpressure: true` довго | `GET /v1/collections/{id}` | отримувач не підтверджує матеріали |
| `stats.errors` зростає | там само, `/errors` | сайт недоступний або змінився |
| `stats.skipped_out_of_scope` великий | там само | межі в правилах відрізають потрібне |
| `stopped_by` у результаті job | `GET /v1/jobs/{id}` | вичерпано `crawl.max_pages_per_run` або `crawl.max_bytes_per_run` |
| `503 service_unavailable` | журнал, відповіді API | файл стану зайнятий іншим процесом |
| `strategy_load_errors` | `GET /v1/info` | пакет стратегій не завантажився |

**Журнали** — JSON у stdout (`JANE_WEB_COLLECTOR_LOG_FORMAT=console` для читання людиною). Корисні повідомлення: `configured limits` (ефективні ліміти й список стратегій на старті), `outbound address policy`, `javascript rendering`, `resuming collection`, `lease lost, another instance continues`, `state store busy`, `collections expired`.

## Запуск у Docker

Образ збирається з кореня репозиторію:

```powershell
docker build -f services/web-collector/Dockerfile -t jane-web-collector .
```

В образі: користувач `jane` (uid 10001), порт 8101, `STATE_DIR=/var/lib/jane-web-collector` (том), `CONTRACTS_DIR=/app/contracts`, `DISCOVERY_PATH=/app/strategies/discovery`, `HOST=0.0.0.0`. Варіант із рендерингом — [dependencies.md](dependencies.md#рендеринг-javascript). У складі dev-стеку сервіс піднімає `just up web-collector`. Збірку образу для цієї сторінки окремо не перевіряли.

## Оновлення й міграції

- Схема `state.db` створюється командами `CREATE TABLE IF NOT EXISTS` під час старту; окремих міграцій і номера версії формату у Web Collector немає. Нові таблиці додаються автоматично, зміни наявних колонок потребуватимуть міграції в коді.
- Оновлення: зупинити екземпляри (плавна зупинка звільняє оренду, збори лишаються відновлюваними), замінити образ або код, запустити — незавершені збори продовжаться з останньої транзакції.
- Екземпляри зі спільним `STATE_DIR` оновлюйте разом.
- Перед оновленням зробіть копію `state.db` (нижче).

## Резервування й відновлення

Копію файла SQLite в режимі WAL робіть на зупиненому сервісі або через резервне копіювання SQLite, а не простим копіюванням під навантаженням:

```powershell
uv run python -c "import sqlite3; src = sqlite3.connect('.jane/web-collector/state.db'); dst = sqlite3.connect('state-backup.db'); src.backup(dst); dst.close(); src.close()"
```

Відновлення — зупинити сервіс, замінити `state.db` копією й видалити поруч `state.db-wal` і `state.db-shm`, запустити. Збори, незавершені в момент копії, продовжаться; матеріали, видані після копії, буде видано повторно з новими `observation_id` — отримувач має бути готовий до повторних спостережень. Команду копіювання перевірено на Windows на файлі зі станом прикладів; відновлення з копії не перевірялося.

Резервувати транзитні blob зазвичай не потрібно: вони тимчасові (`transfer.transit_ttl_seconds`).

## Масштабування

- **Кілька екземплярів на одному вузлі** зі спільним `STATE_DIR`: будь-який екземпляр приймає запити й читає матеріали; збір виконує той, хто тримає оренду; ліміти хоста спільні; зупинений екземпляр підхоплюється іншим через `LEASE_SECONDS`. У кожного запуску має бути унікальний `INSTANCE_ID` (типове значення це забезпечує).
- **Кілька вузлів** не підтримуються: файл SQLite не можна ділити між вузлами через мережеву файлову систему. Окремі колектори з окремими `STATE_DIR` не узгоджують ліміти хоста — розподіляйте між ними різні сайти.
- **У межах екземпляра**: `jobs.max_concurrent_jobs` зборів одночасно, `concurrency.max_parallel_fetches` запитів на збір, `collector.render_max_pages` сторінок у браузері.

## Типові проблеми

| Симптом | Причина | Що робити |
|---|---|---|
| `422`, `Idempotency-Key header is required` | заголовок не передано | додати `Idempotency-Key` до `POST /v1/collections` |
| `422 idempotency_key_reused` | той самий ключ з іншим тілом | новий ключ для нового запиту |
| `409 conflict` на старті збору | `state_key` уже використовує інший збір | дочекатися або скасувати попередній |
| Збір `succeeded`, але матеріалів мало, `skipped_out_of_scope` великий | URL стрічки, sitemap чи API поза `path_prefixes` | додати шляхи навігаційних документів у `scope` |
| Помилки `access_denied_by_policy` на всі URL хоста | `robots.txt` відповідає 5xx або забороняє | перевірити `robots.txt`; для власного ресурсу — `owner_policy` |
| Помилки `access_denied_by_policy` на внутрішні адреси | `EGRESS_DENY_PRIVATE=true` або link-local | змінити політику, якщо джерело справді внутрішнє |
| `not_implemented` для `render_js` | немає Playwright або Chromium | `uv run playwright install chromium` або образ з extra `render` |
| `paused_by_backpressure` не знімається | матеріали не підтверджуються | читати `/materials` з `after` |
| `410` на `GET /v1/collections/{id}` | збір прострочено (`job_retention_seconds`) | дані збору видалено, запустити новий |
| Сервіс не стартує: `heartbeat_interval_ms + state_busy_timeout_ms must be less than ...` | несумісні параметри оренди | див. [правила старту](configuration.md#оренда-й-кілька-екземплярів) |
| `503 service_unavailable`, `state store is busy` | інший процес довго тримає блокування SQLite | повторити після `Retry-After`; перевірити кількість екземплярів |
