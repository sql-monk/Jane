# Storage: інтеграція

Як викликати Storage зі стороннього застосунку, як він поєднується з іншими модулями Jane і як його замінити сумісною реалізацією. Повні описи операцій — у довідниках [storage.v1](reference/api/README.md) і [handler.v1](../../reference/api/handler/README.md).

## Зміст

- [Операції](#операції)
- [Самостійне використання](#самостійне-використання)
- [Записи сутностей](#записи-сутностей)
- [Читання результатів](#читання-результатів)
- [Помилки](#помилки)
- [Композиція в Jane](#композиція-в-jane)
- [Повторна обробка збереженого RAW](#повторна-обробка-збереженого-raw)
- [Заміна сумісною реалізацією](#заміна-сумісною-реалізацією)

## Операції

Запис — спільний контракт обробників `handler.v1` ([handler.v1.yaml](../../../contracts/openapi/handler.v1.yaml)):

| Операція | Scope | Призначення |
|---|---|---|
| `POST /v1/invocations` | `handler:invoke` | Записати входи виклику; `Idempotency-Key` = `delivery.delivery_key` |
| `GET /v1/invocations/{invocation_id}` | `handler:invoke` | Результат недавнього виклику (лише на тому самому екземплярі) |
| `POST /v1/test-runs` | `handler:test` | Тести пакета збереження в `test_mode`, асинхронно (`202` + job) |
| `GET`, `PUT`, `DELETE /v1/connections/{id}`, `GET /v1/connections` | `connections:write` (читання також `handler:invoke`) | Керовані підключення |
| `POST /v1/connections/{id}/test` | `connections:write` | Перевірка секретів і доступності сховища |
| `GET /v1/jobs/{job_id}`, `POST /v1/jobs/{job_id}/cancel` | `handler:invoke` або `handler:test` | Стан асинхронного виклику чи тесту |

Читання — `storage.v1` ([storage.v1.yaml](../../../contracts/openapi/storage.v1.yaml)), scope `storage:read`:

| Операція | Призначення |
|---|---|
| `GET /v1/entity-types` | Каталог типів, для яких у просторі підключення є сутності, з кількістю |
| `GET /v1/entities` | Поточний стан сутностей одного типу або однієї сутності за `key`; пошук підрядка `search` |
| `GET /v1/entity-history` | Історія оновлень однієї сутності |
| `GET /v1/objects` | Збережені RAW-об'єкти й документи з фільтрами |
| `GET /v1/objects/{object_id}` | Опис об'єкта й відновлений `Material` |
| `GET /v1/objects/{object_id}/content` | Байти об'єкта; підтримується `Range` |
| `GET /v1/storage-status` | Результат останньої перевірки сховища й статистика без звернення до сховища |

Перевірку доступності й статистику запускає `POST /v1/storage-status/checks` (scope `connections:write`, `202` + job). Також `GET /v1/health`, `GET /v1/info` (адаптери, пакети з digest, контрактні ліміти) і `/metrics`. Із `auth_mode=api_key` запит несе заголовок `Authorization: Bearer <ключ>`.

## Самостійне використання

Повний мінімальний сценарій із файловим адаптером — [швидкий старт](quickstart.md). Нижче — підключення з секретами на прикладі PostgreSQL. Перевірено 2026-10-11 на Windows з PostgreSQL 18 із `just up --project <назва> postgres` (порт бази `18210`); вивід — з цього запуску.

1. Задайте сервісу allowlist і секрети у змінних із префіксом `JANE_SECRET_`, потім запустіть його.

   PowerShell:

   ```powershell
   $env:JANE_STORAGE_CONNECTION_HOST_ALLOWLIST = '["127.0.0.1:18210"]'
   $env:JANE_SECRET_PG_USER = "jane_storage_results"
   $env:JANE_SECRET_PG_PASSWORD = "<пароль користувача бази>"
   uv run --all-packages python -m jane_storage
   ```

   Bash:

   ```bash
   export JANE_STORAGE_CONNECTION_HOST_ALLOWLIST='["127.0.0.1:18210"]'
   export JANE_SECRET_PG_USER=jane_storage_results
   export JANE_SECRET_PG_PASSWORD='<пароль користувача бази>'
   uv run --all-packages python -m jane_storage
   ```

   Пароль бази dev-стеку показує `just env` (змінна `JANE_PG_STORAGE_RESULTS_PASSWORD`).

2. Зареєструйте підключення — `secret_refs` містять лише посилання:

   ```json
   {
     "connection_id": "results-pg",
     "kind": "postgresql",
     "title": "Results in PostgreSQL",
     "params": {"host": "127.0.0.1", "port": 18210, "database": "jane_storage_results", "schema": "public", "sslmode": "disable"},
     "secret_refs": {"username": "env:JANE_SECRET_PG_USER", "password": "env:JANE_SECRET_PG_PASSWORD"}
   }
   ```

   ```bash
   curl -s -X PUT http://127.0.0.1:8107/v1/connections/results-pg -H 'Content-Type: application/json' --data-binary @connection-pg.json
   curl -s -X POST http://127.0.0.1:8107/v1/connections/results-pg/test
   ```

   Відповідь перевірки:

   ```json
   {"ok":true,"checked_at":"2026-10-11T10:05:46.408486Z","secrets_resolved":{"username":true,"password":true},"latency_ms":469}
   ```

3. Надішліть той самий виклик, що в швидкому старті, замінивши пакет на `jane.storage-postgresql`, а `connections.target` — на `results-pg`. Адаптер під час першого відкриття створює таблиці (`ensure_schema`), RAW потрапляє в `public.jane_objects`, сутність — у `public.jane_entities`. Уривок підтвердження RAW:

   ```json
   {
     "status": "written",
     "target": {"adapter": "postgresql", "connection_id": "results-pg"},
     "object": {
       "object_id": "obj_358c44b3866e4b33bd68301a1b96b90e",
       "adapter": "postgresql",
       "locator": {"table": "public.jane_objects", "id": "obj_358c44b3866e4b33bd68301a1b96b90e"},
       "media_type": "text/html",
       "size_bytes": 62,
       "sha256": "06f441ff0f8d8018b29669de7ef7675f11bffe23d07ff62ee8696aae8c922ba1"
     },
     "delivery_key": "pg-1"
   }
   ```

   `object_id` той самий, що у файловому адаптері: він залежить лише від ключа об'єкта.

4. Результати можна читати через `storage.v1` або напряму SQL у власній базі (це база користувача, а не внутрішня база Storage):

   ```sql
   SELECT canonical_key, fields->>'price' AS price, version
   FROM public.jane_entities
   WHERE entity_type = 'product';
   ```

   ```text
           canonical_key         | price | version
   ------------------------------+-------+---------
    shop-example|{"sku":"A-100"} | 1299  |       1
   ```

Таблиці й колонки — [адаптери: postgresql](adapters.md#postgresql).

### Синхронний і асинхронний виклик

Без поля `mode` Storage чекає результату до `timeouts.sync_response_max_ms` (типово 30 с) і повертає `200` з `HandlerResult`; довший виклик повертає `202` з job. З `"mode": "async"` відповідь — одразу `202` і `Location` на `GET /v1/jobs/{job_id}`; результат — у полі `result` завершеного job. Job живуть у пам'яті екземпляра, що його прийняв.

### Тести пакета

`POST /v1/test-runs` виконує тести з маніфесту пакета (`tests`) у `test_mode`: ядро перевіряє запит і повертає підтвердження `simulated`, не звертаючись до адаптера, тому підключення не потрібне.

```bash
curl -s -X POST http://127.0.0.1:8107/v1/test-runs -H 'Content-Type: application/json' -H 'Idempotency-Key: qs-test-1' -d '{"handler":{"package_id":"jane.storage-files","version":"1.0.0"}}'
```

Відповідь — `202` з `job_id`; завершений job (реальний запуск) містить `"passed": 2, "failed": 0` і випадки `raw-html-page`, `idempotent-redelivery` зі статусом `success`.

### Пакет із запиту

Пакет збереження, якого немає серед вбудованих (наприклад, форк із іншими форматами), передається архівом у полі `package_archive` (`ContentRef` канонічного ZIP) разом із `handler`. Storage перевіряє, що архів містить саме `package_id@version`, digest і межі `packages.*`; пакет збереження не може оголошувати залежностей (`422 dependency_not_allowed`). Без архіву пакет береться з вбудованих, потім із Registry, якщо задано `JANE_STORAGE_REGISTRY_URL`.

## Записи сутностей

`EntityRecord` ([entity.schema.json](../../../contracts/schemas/entity.schema.json)) описує одне спостереження сутності. Правила злиття однакові для всіх адаптерів:

- поле з `fields` встановлює значення; поле, якого немає ні в `fields`, ні в `cleared`, не змінюється — **пропуск не є видаленням**;
- поле з `cleared` видаляється з поточного стану й запам'ятовується в `cleared_fields`;
- `null` як значення заборонено (`422`): очищення — лише через `cleared`; поле не може бути одночасно в `fields` і `cleared`;
- поле змінюється, лише якщо спостереження **новіше** за останнє, що змінило саме це поле; інакше воно потрапляє в `stale_fields` і лише в історію.

Приклад часткового оновлення з явним очищенням (поле `title` лишиться, `price` зміниться, `discount` зникне):

```json
{
  "entity_type": "product",
  "key": {"scope": "shop-example", "natural": {"sku": "A-100"}},
  "fields": {"price": 1249},
  "cleared": ["discount"],
  "observation": {"observation_id": "obs_quickstart_0002", "observed_at": "2026-10-11T11:00:00Z"}
}
```

Перевірено після швидкого старту (файловий адаптер): підтвердження `written` з `applied_fields: ["discount", "price"]`, у стані `price: 1249`, `title` без змін, `cleared_fields: ["discount"]`, `version: 3`. Очищення поля, якого немає в стані, теж застосовується й запам'ятовує порядок.

Порядок спостережень: спершу `observed_at`, потім `sequence` (відсутній = `-1`), потім `observation_id`. `sequence` розрізняє версії з однаковим часом — наприклад, редагування повідомлення Telegram.

Статус підтвердження сутності (`WriteAck.status`):

| Статус | Коли |
|---|---|
| `written` | Застосовано всі поля запису |
| `partially_stale` | Частину полів застосовано, частина старіша |
| `stale` | Усі поля старіші; стан не змінився, але версія й історія зросли |
| `duplicate` | Цей `delivery_key` уже записано; повертається збережене підтвердження |
| `simulated` | `test_mode`: перевірка без запису |

Повторне спостереження з тим самим `observation_id` і `observed_at`, надіслане з **новим** `delivery_key`, — не дубль, а `stale`: на PostgreSQL такий повтор дав `stale` для сутності й `written` для RAW з тим самим `object_id`.

## Читання результатів

| Операція | Параметри | Примітки |
|---|---|---|
| `GET /v1/entity-types` | `connection_id`; `scope`, `cursor`, `limit` | Типи за назвою з точною кількістю `entity_count`; `search_supported` — чи доступний пошук |
| `GET /v1/entities` | `connection_id`, `entity_type` (обов'язкові); `key`, `scope`, `updated_since`, `search`, `cursor`, `limit` | З `key` — одна сутність або порожній список. `search` — буквальний підрядок без урахування регістру в ключі й полях, до пагінації. Порядок — власний для адаптера, не «новіші першими» |
| `GET /v1/entity-history` | `connection_id`, `entity_type`, `key`; `cursor`, `limit` | Новіші версії першими; `404`, якщо сутності немає |
| `GET /v1/objects` | `connection_id`; `source_id`, `material_id`, `material_ids` (до 200), `since`, `until`, `cursor`, `limit` | Кожен елемент — `object`, зведення `material`, `stored_at` |
| `GET /v1/objects/{object_id}` | `connection_id` | `object`, `stored_at` і відновлений `material` |
| `GET /v1/objects/{object_id}/content` | `connection_id`; заголовок `Range: bytes=…` | `200` або `206`; `416` для недосяжного діапазону |

Курсор непрозорий і дійсний лише для того самого запиту й адаптера. Послідовні сторінки не є транзакційним знімком при паралельних записах.

Каталог типів, пошук і статистику сутностей мають не всі адаптери:

| Можливість | `filesystem`, `postgresql`, `mongodb` | `sqlserver`, `s3`, `minio` |
|---|---|---|
| `GET /v1/entity-types` | так | `501 not_implemented` |
| `search` у `GET /v1/entities` | так | `501 not_implemented` |
| Статистика об'єктів і сутностей у перевірці сховища | так | `null` з причиною `adapter_statistics_not_supported` |

Як кожен адаптер рахує каталог і розмір (`size_basis`) — [адаптери](adapters.md). У прикладах Jane сутності читаються з `results-mongo`: кожен тип там — окрема колекція, а каталог показує, які типи вже мають сутності ([типи сутностей](../../reference/entity-types.md)).

API читання бачить простір імен, заданий `params` самого підключення: параметр етапу `prefix` / `schema` / `table_prefix` у читанні недоступний. Щоб читати простір етапу, зареєструйте окреме підключення з тими самими значеннями в `params`.

`material` в `GET /v1/objects/{object_id}` повертається, якщо об'єкт — RAW із метаданими `Material`:

| Як збережено | `material.content` |
|---|---|
| `html` / `original` у `filesystem` | Постійний blob `file:///…` на збережений файл |
| `html` / `original` у `s3`, `minio` | Постійний blob `s3://<бакет>/<ключ>` |
| `html` / `original` у БД, до `transfer.inline_max_bytes` | Inline |
| `json` (будь-який адаптер) | Початковий вміст із документа: inline або транзитний blob |
| Більше `inline_max_bytes` без постійного URI | Транзитний blob `file://` у `JANE_STORAGE_TRANSIT_DIR` (`store: transit`, `expires_at`); без цього каталогу `material` відсутній |

## Помилки

Помилки API — `application/problem+json` ([errors.md](../../../contracts/docs/errors.md)). Помилки сховища під час запису — не HTTP-помилки, а `HandlerResult` зі `status: failed`.

| Ситуація | Відповідь |
|---|---|
| Немає `Idempotency-Key` або він не дорівнює `delivery_key` | `422 validation_failed` |
| Той самий ключ з іншим тілом (без `context`) | `422 idempotency_key_reused` |
| Той самий ключ, виклик ще виконується | `409 idempotency_in_progress` |
| Невідомий пакет або підключення | `404 not_found` |
| `params` не за схемою пакета, вхід не того виду, хибний `EntityRecord`, тип підключення не той, що потрібен пакету | `422 validation_failed` |
| `digest` не збігся | `422 digest_mismatch` |
| Тіло більше `transfer.max_request_body_bytes` | `413 payload_too_large` |
| Registry недоступний | `502 upstream_unavailable` |
| Сховище недоступне, вичерпано повтори `CONFLICT` | `200`, `failure.kind = connection_error`, `retryable: true` |
| Інший `sha256` для того самого ключа об'єкта, пошкоджений документ | `200`, `failure.kind = execution_error`, `retryable: false` |
| Вміст більший за `objects.max_object_bytes` | `200`, `failure.kind = resource_exceeded` |
| `format.raw: html` для не-HTML матеріалу | `200`, `failure.kind = invalid_params` |
| `entities_ref` / `data_ref` не JSON або не за схемою | `200`, `failure.kind = schema_mismatch` |

Якщо збій стався після частини записів, `HandlerResult` містить `output.writes` уже виконаних і попередження `storage.partial`: повтор тим самим `delivery_key` пропустить їх як дублі.

## Композиція в Jane

- **Етап збереження.** Orchestrator викликає `POST /v1/invocations` з `delivery_key` елемента етапу як `Idempotency-Key` і записує результат разом з наступними елементами в одній транзакції. Після збою він повторює виклик тим самим ключем — Storage повертає збережені підтвердження з `duplicate: true` ([виконання завдань](../../architecture/task-execution.md)).
- **Ключі доставки частин.** З одного `delivery_key` виклику Storage утворює ключі частин: перший RAW — сам ключ, наступні — `<ключ>#raw1`, `#raw2`…; сутності — `<ключ>#0`, `#1`… наскрізно через усі входи; документи `writes: data` — `<ключ>#data0`…
- **Підключення.** Orchestrator зберігає реєстр підключень і надсилає їх виконавцям через `PUT /v1/connections/{id}`; секрети розв'язує лише Storage у своєму середовищі.
- **Розгалуження.** Один матеріал можна паралельно зберегти як RAW і передати екстрактору; сутності екстрактора приходять наступним етапом у `inputs[].entities` або за посиланням `entities_ref`.
- **Читання.** Assistant і Admin UI читають результати через `storage.v1`; власних даних Storage про завдання не має — [власність даних](../../architecture/data-ownership.md).

## Повторна обробка збереженого RAW

Orchestrator може запустити етапи заново для збереженого матеріалу: він читає `GET /v1/objects/{object_id}` і передає відновлений `Material` наступним етапам як є. Якщо повторюється сам етап збереження, Storage читає вміст за постійним URI:

- `file:///…` файлового адаптера — лише в межах `JANE_STORAGE_CONTENT_FILES_DIR` (у dev-стеку — корінь RAW-об'єктів власного тому `/var/lib/jane/storage/objects`; записи доставок, індекс і сутності поза ним недоступні);
- `s3://…` — через транзитне підключення `JANE_STORAGE_TRANSIT_CONNECTION_ID`;
- власні транзитні blob Storage читає завжди, якщо задано `JANE_STORAGE_TRANSIT_DIR`.

Без відповідного налаштування виклик повертає `HandlerResult.failed`.

## Заміна сумісною реалізацією

- **Інше сховище.** Змініть пакет етапу (наприклад, `jane.storage-postgresql` замість `jane.storage-mongodb`) і підключення. Колектор, екстрактор і формат `EntityRecord` не змінюються; семантика злиття та дедуплікації однакова, бо її виконує ядро. Типове розміщення в Jane — сутності в MongoDB, RAW у файлах ([ADR-0011](../../adr/0011-data-placement.md)).
- **Новий тип сховища.** Пакет адаптера за протоколом `StorageAdapter`, що проходить набір C-01…C-16, — [новий адаптер](new-adapter.md).
- **Інший сервіс збереження.** Сервіс, який реалізує `handler.v1` (`handler_kind: storage`) і `storage.v1`, замінює Storage для Orchestrator і Assistant. Обов'язкові властивості: ідемпотентність за `delivery_key` між перезапусками, порядок спостережень, часткові оновлення й `cleared`, підтвердження `WriteAck` за схемою. Контрактні тести — `just contract`; сценарії поведінки — набір сумісності.
