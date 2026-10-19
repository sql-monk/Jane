# Резервування й відновлення

Кожен сервіс Jane володіє своїм сховищем, тому резервна копія платформи — це набір копій окремих баз і томів за [власністю даних](README.md#власність-даних). Сторінка описує, що копіювати, як зробити узгоджену копію в dev-стеку і як відновити стек після втрати томів. Процедуру перевірено 2026-10-11 на стеку `jane-doc-ops` (Windows 11, PowerShell 7, ревізія `48389a3`); команди для MongoDB — 2026-10-12 на окремому контейнері `mongo:8.0` ([MongoDB](#mongodb-сутності-з-пакетів)).

## Зміст

- [Що резервувати](#що-резервувати)
- [Узгодженість копії](#узгодженість-копії)
- [Резервування](#резервування)
- [Відновлення](#відновлення)
- [MongoDB: сутності з пакетів](#mongodb-сутності-з-пакетів)
- [Перевірка після відновлення](#перевірка-після-відновлення)
- [Обмеження](#обмеження)

## Що резервувати

| Дані | Власник | Сховище в dev-стеку | Спосіб |
|---|---|---|---|
| Джерела, завдання, запуски, черга, підключення, ліміти, аудит | Orchestrator | база `jane_orchestrator` | `pg_dump` |
| Метадані пакетів, версій, звітів тестів | Registry | база `jane_registry` | `pg_dump` |
| Архіви версій пакетів | Registry | бакет `jane-registry` у томі `minio-data` | архів тому при зупиненому MinIO |
| Бюджети, облік витрат LLM, провайдери, псевдоніми | LLM gateway | база `jane_llm` | `pg_dump` |
| Сесії підключення джерел | Assistant | база `jane_assistant` | `pg_dump` |
| Кеш ідемпотентності, job, результати викликів | Handler Runtime | база `jane_handler_runtime` | `pg_dump` (за потреби) |
| Стан обходу, буфер, курсори | Web Collector, Telegram Collector | томи `web-collector-data`, `telegram-collector-data` | архів тому при зупиненому сервісі |
| Сутності прикладів та їхня історія | користувач (пише Storage) | MongoDB, база `jane_results` (підключення `results-mongo`) | `mongodump` — [MongoDB](#mongodb-сутності-з-пакетів) |
| Новини й дописи (`article`, `post`, `news_article`, `news_event`) та їхня історія | користувач (пише Storage) | PostgreSQL, база `jane_storage_results`, схема `news` (підключення `results-news`, [ADR-0012](../adr/0012-news-relational-postgresql.md)) | `pg_dump` бази `jane_storage_results` |
| RAW-сторінки | користувач (пише Storage) | том `storage-data` (підключення `raw-files`) | архів тому при зупиненому Storage |
| Сутності в PostgreSQL та інших цільових сховищах | користувач (пише Storage) | база `jane_storage_results` (підключення `results-pg`), сховища користувача | `pg_dump` або засоби сховища |
| Облікові дані стеку | оператор | `.jane/stack-<проєкт>.json` | копія файлу в захищеному місці |

Пояснення:

- **Що можна не копіювати.** Кеш ідемпотентності й job Handler Runtime, транзитні blob (`transit`) мають обмежений строк життя; після їх втрати незавершені виклики виконуються повторно. Втрата стану колектора означає, що наступний збір почнеться з початку.
- **Облікові дані.** Файл стеку містить паролі ролей PostgreSQL, кореневого користувача MongoDB, ключі MinIO та ключі API. MinIO зберігає свою конфігурацію в тому самому томі, тому відновлений том `minio-data` треба запускати з тими самими обліковими даними. Зберігайте файл окремо від даних і так само захищено, як секрети.
- **Секрети підключень** у базах не зберігаються — лише `secret_refs`. Значення (`.jane/secrets`, змінні середовища) резервуються окремо засобами, якими їх видано.

## Узгодженість копії

- Перед копіюванням зупиніть нові запуски: Orchestrator без планувальника й воркерів — [запуск](running.md#orchestrator-без-планувальника-й-воркерів).
- `pg_dump` дає узгоджений знімок однієї бази. Бази різних сервісів копіюються в різні моменти; посилання між ними (наприклад завдання → версія пакета) лишаються дійсними, бо версії пакетів незмінні.
- Томи з файлами (MinIO, SQLite колекторів, файли Storage) копіюйте при зупиненому сервісі-власнику.
- `mongodump` без реплікасету не дає знімка всієї бази: колекції копіюються в різні моменти. Тому MongoDB копіюйте, коли Storage не пише.

![Процес резервування й відновлення](../diagrams/operations/backup-restore.light.png#gh-light-mode-only)
![Процес резервування й відновлення](../diagrams/operations/backup-restore.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../diagrams/operations/backup-restore.light.png), [темне](../diagrams/operations/backup-restore.dark.png); джерело — [backup-restore.drawio](../diagrams/operations/backup-restore.drawio).

## Резервування

Приклад для проєкту `jane-doc-ops` із сервісами `orchestrator`, `registry`, `storage`. Контейнери мають назви `<проєкт>-<сервіс>-1`, томи — `<проєкт>_<том>`. Команди нижче — PowerShell; їх перевірено.

1. Переведіть Orchestrator у режим без планувальника й воркерів (зберігайте в середовищі й фіксовані порти, якщо вони задані):

   ```powershell
   $env:JANE_ORCHESTRATOR_SCHEDULER_ENABLED = "false"
   $env:JANE_ORCHESTRATOR_RUN_WORKERS = "false"
   just up orchestrator --no-build --project jane-doc-ops
   ```

2. Створіть каталог копії й зніміть логічні копії баз. `pg_dump` виконується в контейнері PostgreSQL від імені суперкористувача стеку (`jane`), файл копіюється на хост:

   ```powershell
   $b = "$PWD\backup"
   New-Item -ItemType Directory -Force $b
   foreach ($db in "jane_orchestrator", "jane_registry") {
       docker exec jane-doc-ops-postgres-1 pg_dump -U jane -Fc -f /tmp/$db.dump $db
       docker cp jane-doc-ops-postgres-1:/tmp/$db.dump "$b\$db.dump"
   }
   ```

   Додайте до списку `jane_llm`, `jane_assistant`, `jane_handler_runtime`, `jane_storage_results`, якщо ці сервіси працюють.

3. Скопіюйте том MinIO при зупинених MinIO і Registry. Архів створює тимчасовий контейнер з образом `postgres:18`, який уже є в стеку:

   ```powershell
   docker stop jane-doc-ops-registry-1 jane-doc-ops-minio-1
   docker run --rm -v jane-doc-ops_minio-data:/data:ro -v "${b}:/backup" postgres:18 tar -C /data -czf /backup/minio-data.tgz .
   docker start jane-doc-ops-minio-1 jane-doc-ops-registry-1
   ```

   Так само копіюються томи `web-collector-data`, `telegram-collector-data`, `storage-data` — при зупиненому сервісі-власнику.

4. Скопіюйте файл `.jane/stack-jane-doc-ops.json` у захищене місце.

5. Поверніть звичайний режим Orchestrator (приберіть змінні з кроку 1 і повторіть `just up orchestrator --no-build`).

Результат перевірочного запуску (розміри файлів у байтах):

```text
jane_orchestrator.dump  34252
jane_registry.dump      27584
minio-data.tgz          10450
```

Bash: у кроках 2–3 ті самі команди `docker`; каталог копії — `b="$PWD/backup"`, том для архіву — `-v "$b:/backup"`. У Git Bash на Windows перед `docker run` з bind-шляхом задайте `MSYS_NO_PATHCONV=1`. Варіант для Bash не перевірявся.

## Відновлення

Сценарій: томи PostgreSQL і MinIO втрачено, файл стеку з обліковими даними збережено. Перевірочний запуск імітував втрату так:

```powershell
just down --project jane-doc-ops
docker volume rm jane-doc-ops_postgres-data jane-doc-ops_minio-data
```

Друга команда **безповоротно видаляє** бази й архіви пакетів цього проєкту — виконуйте її лише на тестовому стеку.

1. Запустіть інфраструктуру. `just up` створить порожні томи, а провізіонер — бази й ролі сервісів із паролями з файлу стеку:

   ```powershell
   just up postgres minio --no-build --project jane-doc-ops
   ```

2. Відновіть том MinIO при зупиненому MinIO:

   ```powershell
   docker stop jane-doc-ops-minio-1
   docker run --rm -v jane-doc-ops_minio-data:/data -v "${b}:/backup:ro" postgres:18 tar -C /data -xzf /backup/minio-data.tgz
   docker start jane-doc-ops-minio-1
   ```

3. Відновіть бази. Дамп містить власника об'єктів (роль сервісу), яку вже створив провізіонер:

   ```powershell
   foreach ($db in "jane_orchestrator", "jane_registry") {
       docker cp "$b\$db.dump" jane-doc-ops-postgres-1:/tmp/$db.dump
       docker exec jane-doc-ops-postgres-1 pg_restore -U jane -d $db --clean --if-exists --exit-on-error /tmp/$db.dump
   }
   ```

   Очікуваний результат — код виходу 0 для кожної бази.

4. Запустіть сервіси:

   ```powershell
   just up orchestrator registry storage --no-build --project jane-doc-ops
   ```

   Сервіси бачать актуальну схему й міграцій не виконують.

## MongoDB: сутності з пакетів

Сутності прикладів, крім новин і дописів, лежать у базі `jane_results` контейнера `mongodb`, кожен тип — в окремій колекції ([типи сутностей](../reference/entity-types.md)). Новини, зібрані до 2026-10-19, теж лишаються в цій базі. Копія логічна: `mongodump` виконується в контейнері стеку від імені кореневого користувача. Ім'я й пароль контейнер уже має в змінних `MONGO_INITDB_ROOT_USERNAME` і `MONGO_INITDB_ROOT_PASSWORD`, тож пароль не потрапляє в командний рядок хоста. Одинарні лапки не дають оболонці хоста підставити ці змінні.

Перевірено 2026-10-12 на окремому контейнері `mongo:8.0` (mongodump 100.18.0) з тестовими колекціями в розкладці адаптера: `product_book`, `product_book.history`, `product_food`, `_deliveries`. Сценарій перевірки: копія, видалення контейнера з томом, новий контейнер із тим самим паролем, відновлення. Назва контейнера в командах — за схемою стеку `<проєкт>-mongodb-1`.

Резервування — коли Storage не пише (Orchestrator без планувальника й воркерів, крок 1 [резервування](#резервування)); каталог `$b` — з кроку 2:

```powershell
docker exec jane-doc-ops-mongodb-1 sh -c 'mongodump --quiet --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin --db jane_results --gzip --archive=/tmp/jane_results.archive.gz'
docker cp jane-doc-ops-mongodb-1:/tmp/jane_results.archive.gz "$b\jane_results.archive.gz"
```

Очікуваний результат — код виходу 0 і файл `jane_results.archive.gz` у каталозі копії.

Відновлення після втрати тому `mongodb-data`:

1. Запустіть MongoDB. На порожньому томі контейнер створює кореневого користувача з паролем із файлу стеку:

   ```powershell
   just up mongodb --no-build --project jane-doc-ops
   ```

2. Скопіюйте архів у контейнер і відновіть базу. `--drop` спершу видаляє колекції з тими самими іменами:

   ```powershell
   docker cp "$b\jane_results.archive.gz" jane-doc-ops-mongodb-1:/tmp/jane_results.archive.gz
   docker exec jane-doc-ops-mongodb-1 sh -c 'mongorestore --quiet --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin --nsInclude "jane_results.*" --drop --gzip --archive=/tmp/jane_results.archive.gz'
   ```

3. Перевірте колекції — кількість документів та індексів кожної:

   ```powershell
   docker exec jane-doc-ops-mongodb-1 sh -c 'mongosh --quiet --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin jane_results --eval "db.getCollectionNames().sort().forEach(n => print(n, db.getCollection(n).countDocuments(), db.getCollection(n).getIndexes().length))"'
   ```

   Вивід перевірочного запуску на тестових колекціях (колекція, документи, індекси):

   ```text
   _deliveries 1 1
   product_book 2 2
   product_book.history 1 2
   product_food 1 1
   ```

`mongorestore` відновлює індекси з копії. Індекси, яких бракує, адаптер створює сам під час першого запису типу ([адаптери: mongodb](../components/storage/adapters.md#mongodb)). Bash: ті самі команди, каталог копії — `$b/jane_results.archive.gz`; у Git Bash на Windows задайте `MSYS_NO_PATHCONV=1`.

## Перевірка після відновлення

- `just ps --project jane-doc-ops` — усі контейнери `(healthy)`.
- `GET /v1/health` кожного сервісу — `"status":"ok"`.
- Дані, створені до копії, доступні через API.

У перевірочному запуску до копії було створено джерело `ops-backup-marker` в Orchestrator і опубліковано шість пакетів `jane.storage-*` у Registry (`jane-storage-packages publish`). Після відновлення перевірочний скрипт викликав ці ендпоінти з ключем адміністратора стеку й `GET /v1/health` Orchestrator; його вивід:

```text
GET /v1/sources/ops-backup-marker -> 200 ops-backup-marker
GET registry /v1/packages -> 200 ['jane.storage-files', 'jane.storage-minio', 'jane.storage-mongodb', 'jane.storage-postgresql', 'jane.storage-s3', 'jane.storage-sqlserver']
GET archive jane.storage-files@1.0.0 -> 200 sha256:b87649411631a78b58f4e44e304dab362526e21861705a2e04f8a8a6d6aec12f
{"status":"ok","checks":{"database":{"status":"ok"}}}
```

SHA-256 завантаженого архіву збігся з дайджестом, з яким пакет було опубліковано, — архів відновлено з тому MinIO без змін.

## Обмеження

- Перевірено лише Orchestrator, Registry (PostgreSQL + MinIO) і порожній Storage. Бази LLM gateway, Assistant, Handler Runtime і томи колекторів відновлюються тим самим способом, але окремо не перевірялися.
- Відновлення в стек із **новими** обліковими даними (інший файл стеку) не перевірялося; для MinIO воно потребує тих самих root-облікових даних.
- Копіювання на рівні тому PostgreSQL (`/var/lib/postgresql` при зупиненому сервері) можливе, але не перевірялося; логічні копії дозволяють відновити бази окремо, за власниками.
- Резервування цільових сховищ користувача поза dev-стеком (SQL Server, S3, власні MongoDB і PostgreSQL) виконується їхніми засобами й тут не описується.
- Команди MongoDB перевірено на окремому контейнері, а не на стеку `jane-doc-ops`. Запуск `just up mongodb` для відновлення й варіант для Bash не перевірялися.
