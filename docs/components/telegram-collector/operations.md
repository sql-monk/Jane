# Telegram Collector: експлуатація

Моніторинг, оновлення, міграція стану, резервування й типові проблеми Telegram Collector. Експлуатація платформи загалом — у [docs/operations](../../operations/README.md).

## Зміст

- [Власність даних](#власність-даних)
- [Моніторинг](#моніторинг)
- [Запуск у Docker](#запуск-у-docker)
- [Оновлення й міграція стану](#оновлення-й-міграція-стану)
- [Резервування й відновлення](#резервування-й-відновлення)
- [Масштабування](#масштабування)
- [Типові проблеми](#типові-проблеми)

## Власність даних

| Дані | Де | Втрата означає |
|---|---|---|
| Збори, буфер матеріалів, помилки | `STATE_DIR/state.db` | непідтверджені матеріали й незавершені збори втрачено |
| Курсори каналів і видані ревізії (`tg_cursors`, `tg_seen`) | той самий файл | наступний `incremental` знову прочитає історію; редагування, зроблені до втрати, не відновляться |
| Підключення `telegram_account` | той самий файл | створити заново; секрети в ньому не зберігаються |
| Транзитні blob (медіа) | `TRANSIT_DIR` | посилання в матеріалах стануть недійсними |
| Записи каналів (`recorded`) | `RECORDINGS_DIR` | дані тестів і демонстрацій, не робочі |

Бізнес-результати колектор не зберігає — це етап обробника Storage.

## Моніторинг

- `GET /v1/health` перевіряє файл стану: `{"status":"ok","checks":{"state_store":{"status":"ok"}}}`. Docker-образ використовує його як `HEALTHCHECK`.
- `GET /v1/info` — `capabilities.client_backend` показує, який бекенд працює насправді.
- `GET /metrics` — спільні метрики HTTP `jane-kit` (`jane_http_requests_total`, `jane_http_request_duration_seconds`, `jane_http_requests_in_flight`, `jane_service_info`); власних метрик збору немає.
- `GET /v1/jobs/{id}` — `progress.counters` з лічильниками збору й `flood_waits`; результат завершеного job — підсумок каналів (`channels`) і `stopped_by`, якщо вичерпано бюджет.
- Журнал (JSON у stdout): `configured limits` з бекендом і шляхом стану, `telegram flood wait`, `state store busy`, повідомлення про відновлення зборів.

| Ознака | Що означає |
|---|---|
| збори `failed` з `rate_limited` | Telegram просить чекати довше за `telegram.max_flood_wait_seconds` |
| `failed` з `account_unauthorized` | сесію Telethon відкликано або вона недійсна |
| у `/errors` `channel difference too long` | збори запускаються рідше, ніж Telegram зберігає зміни каналу |
| `paused_by_backpressure: true` довго | отримувач не підтверджує матеріали |

## Запуск у Docker

```powershell
docker build -f services/telegram-collector/Dockerfile -t jane-telegram-collector .
```

З Telethon — `--build-arg EXTRAS="--extra telethon"`. В образі: користувач `jane` (uid 10001), порт 8102, `STATE_DIR=/var/lib/jane-telegram-collector` (том), `CONTRACTS_DIR=/app/contracts`. Для бекенда `recorded` змонтуйте каталог записів і задайте `JANE_TELEGRAM_COLLECTOR_RECORDINGS_DIR`. У dev-стеку — `just up telegram-collector`. Збірку образу для цієї сторінки окремо не перевіряли.

## Оновлення й міграція стану

- Формат файла стану має версію (`PRAGMA user_version`, зараз 1). Під час відкриття старіший файл мігрується автоматично в одній транзакції; файл новішої версії не відкривається (`StateFileTooNew`), тож відкат до старішої версії колектора після міграції неможливий без резервної копії.
- Колектори до WP-16 номера версії не читають: на мігрованому файлі вони сприйняли б `sequence` як секунди й перестали б видавати редагування. **Екземпляри зі спільним `STATE_DIR` оновлюйте разом.**
- Плавна зупинка звільняє оренду; після оновлення незавершені збори продовжуються з останнього виданого повідомлення.

## Резервування й відновлення

Резервна копія SQLite — на зупиненому сервісі або через API резервного копіювання SQLite:

```powershell
uv run python -c "import sqlite3; src = sqlite3.connect('.jane/telegram-collector/state.db'); dst = sqlite3.connect('tg-state-backup.db'); src.backup(dst); dst.close(); src.close()"
```

Відновлення — зупинити сервіс, замінити `state.db` копією, видалити поруч `state.db-wal` і `state.db-shm`, запустити. Повідомлення, видані після копії, буде видано знову з новими `observation_id` і тим самим `revision.sequence` — обробники мають сприймати їх як повторні спостереження. Команду копіювання перевірено на Windows на файлі стану з прикладу [quickstart.md](quickstart.md): копія містить `tg_seen` і `user_version = 1`. Відновлення з копії не перевірялося.

## Масштабування

- Кілька екземплярів на одному вузлі зі спільним `STATE_DIR`: збір виконує власник оренди, зупинений екземпляр підхоплюється іншим через `LEASE_SECONDS`.
- Кілька вузлів не підтримуються (SQLite на одному вузлі).
- Один обліковий запис Telegram для кількох екземплярів ділить ліміти Telegram (FloodWait); паузи `rate.min_delay_ms_per_host` діють лише в межах одного збору, а не між зборами чи екземплярами.

## Типові проблеми

| Симптом | Причина | Що робити |
|---|---|---|
| Збір `failed`: `recorded backend: JANE_TELEGRAM_COLLECTOR_RECORDINGS_DIR is not set` | каталог записів не задано | задати `RECORDINGS_DIR` |
| Канал у `/errors` як `not_found` | немає файла запису або доступу до каналу | перевірити ім'я файла (`<username>.json`) чи права облікового запису |
| `422`: `the telethon client needs a telegram_account connection` | немає підключення | створити підключення й указати `account_connection_id` |
| `422` під час `PUT /v1/connections` | секрет у `params`, недозволене посилання або хост поза `TELEGRAM_HOST_ALLOWLIST` | секрети — лише в `secret_refs` з префіксом `JANE_SECRET_` або в `SECRET_FILES_DIR` |
| `incremental` нічого не видає | курсор уже на верху каналу, або вимкнено `updates.*` | перевірити `GET /v1/states/{state_key}` і правила |
| `incremental` знову читає всю історію | курсор скинуто (`DELETE /v1/states`) або інший `state_key` | використовувати сталий `state_key` |
| Сервіс не стартує: `state file version ... is newer` | файл записав новіший колектор | оновити колектор або відновити копію |
| `503 service_unavailable`, `state store is busy` | інший процес тримає блокування SQLite | повторити після `Retry-After` |
