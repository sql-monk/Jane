# Registry: експлуатація

Сторінка описує запуск Registry з PostgreSQL і MinIO, моніторинг, оновлення, резервування, масштабування й типові проблеми. Команди dev-стеку виконано 2026-10-11 на Windows 11 з ревізії `48389a3` у compose-проєкті `jane-doc-registry`; на Linux не перевірялися.

## Зміст

- [Власність даних](#власність-даних)
- [Запуск із PostgreSQL і MinIO](#запуск-із-postgresql-і-minio)
- [Моніторинг](#моніторинг)
- [Оновлення й міграції](#оновлення-й-міграції)
- [Резервування й відновлення](#резервування-й-відновлення)
- [Масштабування](#масштабування)
- [Перевірка після змін](#перевірка-після-змін)
- [Типові проблеми](#типові-проблеми)
- [Зупинка й прибирання](#зупинка-й-прибирання)

## Власність даних

Registry — єдиний власник даних про пакети ([data-ownership.md](../../../contracts/docs/data-ownership.md)):

| Дані | Де | Хто ще має доступ |
|---|---|---|
| Пакети, версії, статуси, звіти тестів, ключі ідемпотентності, job | база PostgreSQL `jane_registry` (схема `JANE_REGISTRY_DB_SCHEMA`) | ніхто; інші сервіси — лише через `registry.v1` |
| Архіви версій | бакет `jane-registry`, ключі `sha256/<hex>` | ніхто; архіви віддає `GET …/archive` |

Роль бази `jane_registry` має права лише на свою базу. Оператор не редагує таблиці напряму: статуси змінюються через API, щоб вони потрапили в історію.

## Запуск із PostgreSQL і MinIO

У dev-стеку Registry запускається разом із залежностями (PostgreSQL, створення баз і ролей, MinIO):

```powershell
just up --project jane-doc-registry registry
```

Уривок виводу (порти на `127.0.0.1` обирає `just up`):

```text
 Container jane-doc-registry-registry-1 Healthy 

project: jane-doc-registry   (stack file: .jane/stack-jane-doc-registry.json)
  postgres   127.0.0.1:61034
  minio      http://127.0.0.1:61007
  registry   http://127.0.0.1:63986
  auth       api_key (admin key: `just env` -> JANE_STACK_AUTH_ADMIN_API_KEY)
```

Адресу Registry й ключ адміністратора показує `just env --project jane-doc-registry` (`JANE_STACK_REGISTRY_URL`, `JANE_STACK_AUTH_ADMIN_API_KEY`). У цьому стеку `/v1/info` показує робочі сховища:

```json
{"service":"registry","version":"0.1.0","api_versions":["v1"],"capabilities":{"handler_kinds":["extractor","storage","llm","transform","collector-rules"],"metadata_store":"postgres","blob_store":"s3","archive":{"format":"zip","compression":"stored","digest":"sha256"},"runtime_profiles":[],"upstream_ports":true},"auth_mode":"api_key","limits":{"defaults":{"transfer":{"job_retention_seconds":86400,"idempotency_ttl_seconds":86400,"max_request_body_bytes":31457280}}}}
```

`runtime_profiles: []` — базовий стек не задає джерел профілів, тому екстрактори в ньому відхиляються з `dependency_not_allowed` ([dependencies.md](dependencies.md#профілі-runtime)).

Поза dev-стеком образ збирається з кореня репозиторію (у сценарії вище його збирав `just up`; окремо команда не запускалася):

```powershell
docker build -f services/registry/Dockerfile -t jane-registry .
```

Образ слухає порт `8000`, працює від користувача без прав root і має `HEALTHCHECK` на `/v1/health`. Потрібні змінні — [configuration.md](configuration.md#приклади-конфігурацій). Базу й роль `jane_registry` створює оператор; таблиці Registry створює сам.

## Моніторинг

| Endpoint | Що показує |
|---|---|
| `GET /v1/health` | `200` і `status: ok`, якщо доступні сховище метаданих і blob-сховище; інакше `503` з `checks.<сховище>.status: down` і причиною |
| `GET /v1/info` | Версія, сховища, завантажені профілі runtime, режим автентифікації, контрактні ліміти |
| `GET /metrics` | Метрики Prometheus |

Відповідь health, коли MinIO зупинено:

```json
{"status":"down","checks":{"metadata_store":{"status":"ok"},"blob_store":{"status":"down","message":"timeout after 2.0s"}}}
```

Метрики:

| Метрика | Зміст |
|---|---|
| `jane_registry_publications_total{result}` | Спроби публікації: `published` або код помилки (`validation_failed`, `secret_detected`, `dependency_not_allowed`, `version_exists`, `forbidden`…) |
| `jane_http_requests_total`, `jane_http_request_duration_seconds`, `jane_http_requests_in_flight` | HTTP-запити за шаблоном маршруту й статусом (jane-kit) |
| `jane_service_info` | Статична інформація про сервіс |

Журнал — JSON-рядки в stdout (`JANE_REGISTRY_LOG_FORMAT=console` — читабельний формат). Кожен запит пише рядок `request` з `trace_id`, методом, шляхом, статусом і тривалістю. Події Registry:

| `msg` | Рівень | Коли |
|---|---|---|
| `registry started` | info | Старт; містить ефективні ліміти й назви сховищ |
| `version published` | info | Нова версія: `package_id`, `version`, `digest`, `created_by` |
| `package forked` | info | Створено форк |
| `secret detected in package` | warning | Публікацію відхилено; шляхи й рядки знахідок без значень |
| `runtime profile source failed` | warning | Джерело профілів не прочиталося |
| `jobs of stopped instances marked failed` | warning | На старті знайдено job упалих екземплярів |
| `lease renewal failed` | error | Не вдалося поновити оренди job чи ключів |
| `auth_mode=none: every caller has every scope - for local tests only` | warning | Сервіс запущено без автентифікації |

`trace_id` з журналу збігається з `trace_id` у тілі помилки problem+json — за ним відповідь клієнту зіставляється з записом журналу.

## Оновлення й міграції

- Схема БД створюється й оновлюється під час старту кожного екземпляра: ідемпотентний DDL (`CREATE … IF NOT EXISTS`, `ALTER … ADD COLUMN IF NOT EXISTS`) під advisory lock, застосована версія — у `registry_schema_version`. Окремої команди міграції немає.
- Поточна версія схеми — `1`. Відкату схеми немає; перед оновленням зробіть резервну копію.
- Кілька екземплярів можна оновлювати по черзі: незавершені job зупиненого екземпляра після спливу оренди стають `failed` з `retryable: true`, а незавершені запити з `Idempotency-Key` можна повторити на іншому екземплярі ([internals.md](internals.md#гарантії-й-паралельність)).
- Формат канонічного архіву — частина контракту: дайджести наявних версій не змінюються з оновленням Registry.

## Резервування й відновлення

Повна копія складається з двох частин: бази `jane_registry` і бакета `jane-registry`. Об'єкти бакета незмінні й адресуються дайджестом, тому порядок такий: спочатку база, потім бакет. Об'єкти, новіші за дамп бази, після відновлення просто не матимуть посилань; навпаки, бакет, скопійований раніше за базу, може не містити архівів версій із дампу.

1. Дамп бази (перевірено в контейнері PostgreSQL dev-стеку):

   ```powershell
   docker exec jane-doc-registry-postgres-1 pg_dump -U jane -d jane_registry -n jane_registry --format=custom -f /tmp/registry.dump
   ```

2. Копія бакета `jane-registry` — будь-яким інструментом копіювання S3 (наприклад `mc mirror` для MinIO). Цей крок не перевірявся.

Відновлення: створіть порожню базу, відновіть дамп, відновіть бакет і запустіть Registry з тими самими `JANE_REGISTRY_DB_SCHEMA` і `JANE_REGISTRY_BLOB_*`. Перевірка відновлення дампу в окрему базу:

```powershell
docker exec jane-doc-registry-postgres-1 createdb -U jane jane_registry_restore
docker exec jane-doc-registry-postgres-1 pg_restore -U jane -d jane_registry_restore --no-owner /tmp/registry.dump
docker exec jane-doc-registry-postgres-1 psql -U jane -d jane_registry_restore -c "select package_id, version, status from jane_registry.registry_versions order by package_id"
```

```text
         package_id          | version | status 
-----------------------------+---------+--------
 examples.testsite-web-rules | 1.0.0   | draft
(1 row)
```

Після відновлення цілісність архівів перевіряє сам Registry: кожне читання з blob-сховища звіряє байти з дайджестом. Вибірково перевірити версію можна `jane-registry export` і `jane-registry verify` ([Експорт і сумісність](../../reference/packages/export-and-compatibility.md)).

Видалення тимчасової бази й дампу після перевірки:

```powershell
docker exec jane-doc-registry-postgres-1 dropdb -U jane jane_registry_restore
docker exec jane-doc-registry-postgres-1 rm /tmp/registry.dump
```

У Git Bash перед командами `docker exec` з абсолютними шляхами контейнера задайте `MSYS_NO_PATHCONV=1`, інакше `/tmp/...` перетвориться на шлях Windows.

## Масштабування

- Екземпляри Registry без локального стану: усе спільне — у PostgreSQL і бакеті. Їх можна запускати скільки завгодно за балансувальником без прив'язки клієнта до екземпляра.
- Кожен екземпляр має власний LRU-кеш архівів (`packages.archive_cache_bytes`) і власний пул з'єднань (`db.pool_max_size`): сумарна кількість з'єднань до PostgreSQL — до `pool_max_size × кількість екземплярів`.
- Публікації одного пакета серіалізуються блокуванням рядка пакета; публікації різних пакетів ідуть паралельно.
- Job перенесення змін виконуються в екземплярі, що прийняв запит (до `jobs.max_concurrent_jobs` одночасно), а стан job видно з будь-якого екземпляра.
- Режим `memory` масштабуванню не підлягає: лише один процес.

## Перевірка після змін

Модульні й контрактні тести без зовнішніх сервісів:

```powershell
just test registry
```

```text
117 passed, 30 deselected in 46.60s
```

Ті самі API-тести на справжніх PostgreSQL і MinIO (стек з [розділу запуску](#запуск-із-postgresql-і-minio); тести створюють окрему базу, схеми й бакети та прибирають їх):

```powershell
just integration --project jane-doc-registry services/registry
```

```text
30 passed, 117 deselected in 467.00s (0:07:47)
```

## Типові проблеми

| Симптом | Причина | Що зробити |
|---|---|---|
| Старт: `ValueError: JANE_REGISTRY_DB_URL is required for db=postgres` | Не задано DSN | Задати `JANE_REGISTRY_DB_URL` або `JANE_REGISTRY_DB=memory` для дослідів |
| Старт: `ValueError: JANE_REGISTRY_BLOB_ROOT is required for blob=filesystem` | Режим `filesystem` без каталогу | Задати `JANE_REGISTRY_BLOB_ROOT` |
| Старт: `error connecting in 'pool-1'` і `Application startup failed` | PostgreSQL недоступна | Перевірити адресу, мережу, пароль ролі `jane_registry` |
| Старт: `FileNotFoundError: contracts/schemas/package-manifest.schema.json not found` | Немає контрактних схем | Задати `JANE_REGISTRY_CONTRACTS_DIR` |
| Старт: `LimitError: … unknown limit(s)` | Помилка в назві `JANE_REGISTRY_LIMITS__…` | Звірити назву з таблицею [лімітів](configuration.md#ліміти) |
| `422 validation_failed`, `Idempotency-Key header is required` | `POST` без ключа ідемпотентності | Додати заголовок `Idempotency-Key` |
| `422 dependency_not_allowed`, `known: none configured` | Не задано джерел профілів runtime | Задати `JANE_REGISTRY_RUNTIME_PROFILES` |
| `502 upstream_unavailable`, `runtime profiles cannot be loaded` | Джерело профілів недоступне або відхиляє токен | Перевірити Handler Runtime і `JANE_REGISTRY_RUNTIME_PROFILES_TOKEN_REF` |
| `403 forbidden`, `Automatic changes are forbidden for this package` | LLM-версія для пакета з `auto_changes_allowed: false` | Рішення людини: опублікувати версію самостійно або дозволити автоматичні зміни |
| `401` на всі запити | Немає або неправильний токен | Взяти ключ із `just env` або налаштувань `JANE_REGISTRY_API_KEYS` |
| `/v1/health` — `503`, запити — `500 internal_error` | Недоступне сховище метаданих або blob-сховище | За `checks` знайти сховище; після його повернення Registry відновлюється без перезапуску |
| Адреса dev-стеку перестала відповідати після `docker restart` | Порти dev-стеку обираються випадково й змінюються після перезапуску контейнера | Виконати `just up --project <проєкт> registry` ще раз: він оновлює адреси в `just env` |

## Зупинка й прибирання

Команда нижче зупиняє стек `jane-doc-registry` і **видаляє всі його дані**: томи PostgreSQL і MinIO (усі пакети й архіви), локально зібрані образи та файл стеку зі згенерованими паролями.

```powershell
just down -v --project jane-doc-registry
```

Щоб зупинити стек і зберегти дані, виконайте `just down --project jane-doc-registry` без `-v`.
