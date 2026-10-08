# Резервування та відновлення

Це процедура для репетиції в ізольованому стеку. Частину PostgreSQL відрепетирувано 2026-10-08 у dev-стеку на
БД оркестратора — копія, відновлення в новий проєкт через `just up` і через `stack.py`, старт без
планувальника й воркерів, повторне ввімкнення ([вивід](../delivery/M3/14d-docs.md)). Решту сховищ (архіви
registry у MinIO/S3, томи storage і колекторів, SQL Server, MongoDB) і робоче середовище **не перевірено**.
Власність даних розділена між сервісами. Копія лише PostgreSQL оркестратора не відновить
RAW, результати зберігання, пакети, курсори колекторів або транзитні blob.

## Що входить до узгодженої копії

Імена — як у dev-стеку (`infra/compose.yaml`, `pg-provision`); у вашому розгортанні вони можуть відрізнятися,
але розподіл власності той самий ([карта власності даних](../../contracts/docs/data-ownership.md)).

| Компонент | Дані | У dev-стеку |
|---|---|---|
| Orchestrator | джерела, завдання, запуски, черга, підключення (без секретів), аудит, ліміти | PostgreSQL БД `jane_orchestrator` (роль `jane_orchestrator`) |
| Registry | метадані, версії, статуси, звіти тестів + **архіви пакетів** (перевіряйте digest кожного) | БД `jane_registry` + бакет `jane-registry` у MinIO/S3 |
| Handler-runtime | ключі ідемпотентності, job, збережені результати викликів | БД `jane_handler_runtime` (схема `jane_handler_runtime`) |
| LLM | облік витрат, бюджети, конфігурація провайдерів; ключі — окремо в secret manager | БД `jane_llm` |
| Assistant | сесії онбордингу, job вдосконалення | БД `jane_assistant` |
| Storage | RAW-файли адаптера files і результати в цільових сховищах | том `storage-data` (`/var/lib/jane/storage`), БД `jane_storage_results`; SQL Server, MongoDB, MinIO, S3 — за підключеннями |
| Web/Telegram collectors | frontier, курсори, стан ідемпотентності (SQLite WAL) | томи `web-collector-data`, `telegram-collector-data` |
| Transit | тимчасові blob незавершених запусків; TTL — не backup | за `TRANSIT_DIR` колекторів, якщо задано |

Запишіть також Git SHA, версії образів/пакетів, схему розгортання, ідентифікатори сховищ,
політику секретів та контрольні суми архівів. Самі секрети зберігайте у захищеному backup
секретного сховища, окремо від репозиторію.

## Копіювання

1. Забороніть нові запуски, зупиніть планувальник і воркери, дочекайтеся завершення активних
   записів. Під час тестової репетиції можна зупинити всі застосунки після фіксації їхнього
   стану. Не використовуйте `just down -v`: цей варіант видаляє томи.

   Планувальник і воркери оркестратора вимикають змінні `JANE_ORCHESTRATOR_SCHEDULER_ENABLED` і
   `JANE_ORCHESTRATOR_RUN_WORKERS` (типово `true`): compose передає їх у контейнер із середовища команди,
   контейнер перестворюється, API лишається доступним. Окремі процеси `python -m jane_orchestrator worker`,
   якщо вони є, зупиніть теж.

   ```text
   # PowerShell
   $env:JANE_ORCHESTRATOR_SCHEDULER_ENABLED='false'; $env:JANE_ORCHESTRATOR_RUN_WORKERS='false'
   just up --project <P> orchestrator
   # bash
   JANE_ORCHESTRATOR_SCHEDULER_ENABLED=false JANE_ORCHESTRATOR_RUN_WORKERS=false just up --project <P> orchestrator

   docker compose -p <P> exec -T orchestrator printenv JANE_ORCHESTRATOR_SCHEDULER_ENABLED   # false
   just logs --project <P> orchestrator      # рядок "orchestrator started" закінчується "workers": 0}
   ```

   Для стеку `stack.py` задайте ті самі змінні й повторіть **ту саму** команду `stack.py up --project <P>
   --profile <профіль> [--telegram]`: коротший `--services` перезапише файл виконавців оркестратора.
   Увімкнення — та сама команда без змінних (PowerShell: `Remove-Item Env:JANE_ORCHESTRATOR_SCHEDULER_ENABLED,
   Env:JANE_ORCHESTRATOR_RUN_WORKERS`).
2. Скопіюйте кожну БД PostgreSQL (`pg_dump --format=custom`) обліковим записом її сервісу (роль = ім'я БД,
   таблиця вище) і перевірте архів `pg_restore --list`. У dev-стеку клієнт PostgreSQL на хості не
   потрібен: команди виконуються в контейнері `postgres`, а його локальний сокет у dev-стеку пароля не
   вимагає. Тека `backup/` має існувати; у Git Bash додайте `MSYS_NO_PATHCONV=1`, інакше `/tmp/...`
   стане шляхом Windows.

   ```text
   docker compose -p <P> exec -T postgres pg_dump -U jane_orchestrator -d jane_orchestrator --format=custom --file=/tmp/jane_orchestrator.dump
   docker compose -p <P> exec -T postgres pg_restore --list /tmp/jane_orchestrator.dump
   docker compose -p <P> cp postgres:/tmp/jane_orchestrator.dump backup/jane_orchestrator.dump
   docker compose -p <P> exec -T postgres rm /tmp/jane_orchestrator.dump
   ```

   Те саме для `jane_registry`, `jane_handler_runtime`, `jane_llm`, `jane_assistant`, `jane_storage_results`.
   З хоста чи в іншому розгортанні — `pg_dump --format=custom --dbname=<адреса> --username=<роль>
   --file=<archive.dump>` клієнтом PostgreSQL версії не нижчої за сервер (18). Адреса й облікові дані dev-стеку:
   - `just up`: `just env --project <P> --format json` → `db-<сервіс>` (`db-orchestrator`, `db-registry`,
     `db-handler-runtime`, `db-llm`, `db-assistant`, `db-storage-results`): `endpoint` (без пароля),
     `db_user`, `db_password`; `db_dsn` містить пароль;
   - `stack.py`: файл `.jane/stack-<P>.json` записів `db-*` не має — пароль ролі в
     `env.JANE_PG_<СЕРВІС>_PASSWORD`, порт — `docker compose -p <P> port postgres 5432`, адреса —
     `postgresql://127.0.0.1:<порт>/jane_<сервіс>`.

   Не вставляйте пароль у командний рядок, що журналюється: використайте `.pgpass` або змінну процесу
   `PGPASSWORD`.
3. Для SQL Server/MongoDB/об'єктного сховища застосуйте засіб backup відповідної системи та
   його перевірку цілісності. Для файлів стану й RAW зробіть копію після зупинки записів;
   SQLite не копіюйте як довільний відкритий файл. Архіви registry та blob зберігайте разом
   із метаданими, щоб посилання не стали битими.
4. Запишіть manifest: час зупинки записів, перелік БД/томів, розміри, checksum, завершені
   команди й права доступу. Перенесіть копію в окреме місце з обмеженим доступом.

## Відновлення та перевірка

1. Підніміть **новий ізольований** проєкт з порожніми сховищами й тими самими сумісними версіями —
   спершу **лише PostgreSQL**: `just up --project <NEW> postgres` (`pg-provision` створює порожні БД і ролі
   сервісів із новими паролями). Застосунки ще не запускайте: під час старту кожен створює свою схему, і
   `pg_restore` у непорожню БД дасть конфлікти. Переконайтеся, що ім'я compose-проєкту та шляхи томів не
   належать чинному стеку.
2. Відновіть кожну БД її роллю (`--no-owner`: об'єкти належатимуть ролі, якою відновлюєте):

   ```text
   docker compose -p <NEW> cp backup/jane_orchestrator.dump postgres:/tmp/jane_orchestrator.dump
   docker compose -p <NEW> exec -T postgres pg_restore -U jane_orchestrator -d jane_orchestrator --no-owner --exit-on-error /tmp/jane_orchestrator.dump
   docker compose -p <NEW> exec -T postgres rm /tmp/jane_orchestrator.dump
   ```

   З хоста — `pg_restore --dbname=<адреса нового проєкту> --username=<роль> --no-owner --exit-on-error
   <archive.dump>`. Відновіть решту сховищ їхніми штатними засобами. Не використовуйте
   `--clean` проти чинної БД. Поверніть secret refs із захищеного джерела; перевірте доступ
   сервісів до пакетів і blob, а також контрольні суми.
3. Запускайте застосунки без планувальника/воркерів: змінні з кроку 1 копіювання і `just up --project <NEW>
   orchestrator [інші сервіси]` або `stack.py up --project <NEW> --profile <профіль> […]`. `stack.py` бере
   паролі з файлу стеку, створеного `just up` (ті самі ключі), тож ролі збігаються з відновленими БД;
   `LIMITS_FILE` профілю не перезапише відновлені ліміти платформи (він лише заповнює порожню БД).
   Перевірте health, кількість джерел, завдань, підключень, активних пакетів, `GET /v1/limits/platform`
   (значення й `ETag` як до копії) і доступність тестових RAW. Потім увімкніть воркери (та сама команда без
   змінних) та проведіть один контрольований повтор доставки/відновлення. Порівняйте результати, кількість
   матеріалів і відсутність дублів; перевірте, що прострочені транзитні посилання не
   залишилися в незавершених роботах.
4. Лише після успішної репетиції затверджуйте час відновлення й дозволяйте робоче
   розгортання. Повної репетиції (усі сховища, робочі обсяги даних, час відновлення) ще не було.
