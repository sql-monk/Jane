# jane-kit: будова

Як бібліотека обробляє запит, як змінюється стан job, як працюють ідемпотентність і спільні сховища та які гарантії вони дають. Код — [libs/jane-kit/src/jane_kit](../../../libs/jane-kit/src/jane_kit/).

## Зміст

- [Конвеєр запиту](#конвеєр-запиту)
- [Стани job](#стани-job)
- [Алгоритм ідемпотентності](#алгоритм-ідемпотентності)
- [Сховища стану](#сховища-стану)
- [Злиття лімітів](#злиття-лімітів)
- [Повтори клієнта](#повтори-клієнта)
- [Гарантії](#гарантії)

## Конвеєр запиту

![Конвеєр запиту в застосунку create_app](../../diagrams/jane-kit/request-pipeline.light.png#gh-light-mode-only)
![Конвеєр запиту в застосунку create_app](../../diagrams/jane-kit/request-pipeline.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/jane-kit/request-pipeline.light.png), [темне](../../diagrams/jane-kit/request-pipeline.dark.png); джерело — [request-pipeline.drawio](../../diagrams/jane-kit/request-pipeline.drawio).

`create_app` додає шари в такому порядку (від зовнішнього до внутрішнього):

1. **Контекст запиту** (`service.py`): `trace_id` з `traceparent` або новий, `X-Request-ID` із заголовка або новий; обидва прив'язуються до журналів на весь запит. Після відповіді — заголовок `X-Request-ID` і запис `jane.access` (крім `/v1/health` і `/metrics`).
2. **Метрики** (`metrics.py`): `jane_http_requests_in_flight`, лічильник і гістограма за шаблоном маршруту (`/v1/jobs/{job_id}`, а не конкретний id).
3. **Автентифікація** (`AuthMiddleware`): крім відкритих шляхів, розбирає `Authorization: Bearer`, кладе `Principal` у `request.state`. Помилка — одразу `401` Problem, далі запит не йде.
4. **Маршрутизація FastAPI** і залежність усього застосунку `authorize`: scope операції з таблиці сервісу; немає потрібного — `403`, немає рядка в таблиці — `403` і запис `error` у журнал.
5. **Обробник** сервісу. `JaneError` перетворюється на Problem; помилки валідації — `422`/`400`; необроблений виняток — `500 internal_error`.

## Стани job

![Стани job і переходи між ними](../../diagrams/jane-kit/job-states.light.png#gh-light-mode-only)
![Стани job і переходи між ними](../../diagrams/jane-kit/job-states.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/jane-kit/job-states.light.png), [темне](../../diagrams/jane-kit/job-states.dark.png); джерело — [job-states.drawio](../../diagrams/jane-kit/job-states.drawio).

`JobRunner.submit` створює job у стані `queued` і запускає asyncio-задачу. Задача чекає слот (`max_concurrent_jobs`), переводить job у `running`, виконує корутину з тайм-аутом `job_timeout_ms` і записує кінцевий стан:

| Подія | Новий стан |
|---|---|
| Корутина повернула результат | `succeeded`, `result` |
| `JaneError` у корутині | `failed`, `error` — Problem цієї помилки |
| Інший виняток | `failed`, `internal_error` і запис у журнал |
| Перевищено `job_timeout_ms` | `failed`, код `timeout` |
| `POST /v1/jobs/{id}/cancel` для `queued` або `running` | `cancelling`, задача переривається на найближчому `await` → `cancelled` |
| Скасування кінцевого job | Без змін, відповідь `200` (для живого — `202`) |
| Власник перестав поновлювати оренду (спільні сховища) | `failed` з `service_unavailable`, `retryable: true`; якщо вже `cancelling` — `cancelled` |
| Черга заповнена (`max_concurrent_jobs + max_queued_jobs`) | Job не створюється, `503 service_unavailable` з `Retry-After` |

Правила запису однакові для всіх сховищ (`decide_save`):

- кінцевий job (`succeeded`, `failed`, `cancelled`) більше не змінюється;
- скасування може записати будь-який екземпляр; решту змін — лише власник job і лише поки його оренда жива (fencing);
- скасування, записане першим, зберігається: прогрес лишає `cancelling`, пізніший успіх чи помилка старого знімка закінчують job як `cancelled`.

## Алгоритм ідемпотентності

1. Перевірити формат ключа: 1–255 друкованих ASCII-символів, інакше `422`.
2. Обчислити відбиток: SHA-256 методу, шляху й тіла запиту.
3. `store.begin(key, fingerprint, ttl)` атомарно захоплює ключ. Якщо запис уже є: інший відбиток — `422 idempotency_key_reused`; стан `in_progress` — `409 idempotency_in_progress`; `completed` — повернути збережену відповідь із `Idempotency-Replayed: true`.
4. Виконати обробник. Успіх — `store.complete(key, response)`; виняток — `store.release(key)` і виняток далі.

У спільних сховищах захоплення має власника (`instance_id`), токен і оренду `in_progress_lease_ms`, яку поновлює `heartbeat`. Ключ, термін якого (`idempotency_ttl_seconds`) минув, видаляється й захоплюється знову. Захоплення зупиненого екземпляра (оренда минула) перехоплює запит із **тим самим** відбитком; `complete` і `release` перевіряють токен, тож запит, у якого захоплення перехопили, не перезапише новий результат.

## Сховища стану

Таблиці створюються в базі сервісу, що використовує сховище; назву таблиці (і схему PostgreSQL) задає сервіс. Дані різних сервісів не змішуються: код спільний, бази — ні.

Таблиця ключів ідемпотентності (`PgIdempotencyStore`, `SqliteIdempotencyStore`, типова назва `idempotency`):

| Стовпець | PostgreSQL | SQLite | Зміст |
|---|---|---|---|
| `key` | `text` PK | `TEXT` PK | `Idempotency-Key` |
| `fingerprint` | `text` | `TEXT` | Відбиток запиту |
| `state` | `text` | `TEXT` | `in_progress` або `completed` |
| `expires_at` | `timestamptz` | `REAL` (epoch) | Кінець терміну ключа; за ним індекс у PostgreSQL |
| `lease_until`, `owner`, `token` | `timestamptz`, `text`, `text` | `REAL`, `TEXT`, `TEXT` | Оренда захоплення |
| відповідь | `status_code`, `body`, `headers` (`layout="split"`) або `response jsonb` (`layout="json"`) | `response TEXT` | Збережена відповідь |

Таблиця job (`PgJobStore`, `SqliteJobStore`, типова назва `jobs`):

| Стовпець | PostgreSQL | SQLite | Зміст |
|---|---|---|---|
| `job_id` | `text` PK | `TEXT` PK | Ідентифікатор |
| документ (`doc_column`, типово `doc`) | `jsonb` | `TEXT` (JSON) | Повний документ `Job` контракту |
| `owner`, `lease_until` | `text`, `timestamptz` | `TEXT`, `REAL` | Власник і оренда |
| `finished_at` | `timestamptz` | `REAL` | Час завершення; за ним видаляються старі job |
| `updated_at` | `timestamptz` | — | Останній запис |

`SqliteWorkJobStore` має лише `job_id` і документ (`body`): власник і стан беруться з «робочого рядка» сервісу (протокол `WorkRows`), а job лише віддзеркалює його — job ніколи не виглядає завершеним, поки робота не завершена.

Міграції: `migrate(tx, lock, *stores)` (PostgreSQL) виконує `CREATE TABLE IF NOT EXISTS` і `ADD COLUMN IF NOT EXISTS` в одній транзакції під `pg_advisory_xact_lock`, тому кілька екземплярів можуть стартувати одночасно. `SqliteIdempotencyStore.migrate()` і `SqliteJobStore.migrate()` додають відсутні стовпці всередині транзакції `BEGIN IMMEDIATE`. Старі розкладки стовпців (`layout="json"`, інша назва стовпця документа) читаються без копіювання даних.

Фонові дії, які сервіс викликає з `heartbeat_loop` кожні `heartbeat_interval_ms`:

| Метод | Що робить |
|---|---|
| `PgIdempotencyStore.heartbeat` | Поновлює оренди захоплень цього процесу |
| `PgIdempotencyStore.gc` | Видаляє до `gc_batch` (500) прострочених ключів |
| `PgJobStore.heartbeat` | Поновлює оренди job, які виконує цей процес |
| `PgJobStore.sweep` | Завершує job усіх власників з минулою орендою (`orphaned`) |
| `PgJobStore.release_owned` | Під час плавної зупинки завершує незавершені job цього власника як `cancelled` |

Невдалий такт записується в журнал і повторюється на наступному; оренда розрахована на кілька пропущених тактів. psycopg використовується синхронно в робочих потоках (`asyncio.to_thread`), бо асинхронний драйвер потребує selector event loop, якого немає типово на Windows.

## Злиття лімітів

`resolve_limits` перетворює кожен шар на плоскі шляхи (`jobs.max_concurrent_jobs`), для спільного шару платформи відображає шляхи контракту на поля моделі, відкидає `null`, перевіряє невідомі шляхи, накопичує найтісніші `hard_caps` (послаблення — помилка), зливає значення за порядком шарів, валідує модель і знижує значення до стель. Опис правил і схема — [конфігурація](configuration.md#ліміти).

## Повтори клієнта

`ServiceClient.request` повторює запит, лише якщо метод безпечний (`GET`, `HEAD`, `OPTIONS`, `PUT`, `DELETE`) або є `Idempotency-Key`, і лише для помилки з'єднання чи читання, статусу `429`/`502`/`503`/`504` або Problem з `retryable: true`. Пауза: `initial_backoff_ms × backoff_multiplier^спроба` плюс випадкова добавка до половини (`jitter`), не більше `max_backoff_ms`; заголовок `Retry-After` має пріоритет (теж обмежений `max_backoff_ms`). Усього спроб — `max_attempts`.

## Гарантії

- Відповідь з ідемпотентним ключем повторюється без нового побічного ефекту протягом `idempotency_ttl_seconds`.
- Job спільного сховища не лишається вічно `running`: після втрати оренди його завершує читання, перелік або `sweep`.
- Запис застарілого виконавця не перезаписує job нового власника і не скасовує записане скасування.
- Невідома або неповна конфігурація автентифікації й лімітів зупиняє старт, а не послаблює перевірки.
- Значення секретів не потрапляють у журнали, Problem і повідомлення про помилки конфігурації.
