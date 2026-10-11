# LLM gateway: експлуатація

Запуск із PostgreSQL, моніторинг, журнали, оновлення й міграції, резервування, масштабування та типові проблеми LLM gateway. Команди перевірено 2026-10-11 на Windows 11 з Docker Desktop 29.8, ревізія `48389a3`; на Linux не перевірялися.

## Зміст

- [Запуск із PostgreSQL](#запуск-із-postgresql)
- [Моніторинг](#моніторинг)
- [Журнали](#журнали)
- [Оновлення й міграції](#оновлення-й-міграції)
- [Резервування й відновлення](#резервування-й-відновлення)
- [Масштабування](#масштабування)
- [Власність даних](#власність-даних)
- [Тести](#тести)
- [Типові проблеми](#типові-проблеми)

## Запуск із PostgreSQL

### Без Docker для сервісу

Потрібна база PostgreSQL з правом створювати схему. Пароль передавайте через `PGPASSWORD`, а не в DSN у файлах.

PowerShell:

```powershell
$env:JANE_LLM_DATABASE_URL = "postgresql://jane_llm@127.0.0.1:5432/jane_llm"
$env:PGPASSWORD = "<пароль>"
uv run --package jane-llm python -m jane_llm
```

Bash:

```bash
JANE_LLM_DATABASE_URL=postgresql://jane_llm@127.0.0.1:5432/jane_llm PGPASSWORD='<пароль>' uv run --package jane-llm python -m jane_llm
```

Цей варіант у документації не виконувався; той самий код сховища перевірено в dev-стеку нижче.

### У dev-стеку

`just up` збирає образ, створює окрему базу `jane_llm` з власним користувачем і запускає сервіс з `JANE_LLM_STORE=postgres`, `auth_mode=api_key` і провайдером `fake`. Профіль `assistant` також піднімає LLM gateway.

```powershell
just up --project jane-doc-llm llm
```

Уривок виводу перевірочного запуску (`llm assistant`, порти задано змінними `JANE_PORT_*`; без них порти обирає Docker):

```text
project: jane-doc-llm   (stack file: .jane/stack-jane-doc-llm.json)
  postgres   127.0.0.1:18540
  llm        http://127.0.0.1:18541
  assistant  http://127.0.0.1:18542
  auth       api_key (admin key: `just env` -> JANE_STACK_AUTH_ADMIN_API_KEY)
  db-llm     postgresql://127.0.0.1:18540/jane_llm
```

Без ключа захищені операції повертають 401; `GET /v1/health` відповідає без ключа. Ключ адміністратора — `just env --project jane-doc-llm`.

Таблиці, які сервіс створив під час старту:

```powershell
docker exec jane-doc-llm-postgres-1 psql -U jane -d jane_llm -c '\dt llm.*'
```

```text
              List of tables
 Schema |     Name     | Type  |  Owner   
--------+--------------+-------+----------
 llm    | config       | table | jane_llm
 llm    | counters     | table | jane_llm
 llm    | idempotency  | table | jane_llm
 llm    | invocations  | table | jane_llm
 llm    | jobs         | table | jane_llm
 llm    | reservations | table | jane_llm
 llm    | usage        | table | jane_llm
(7 rows)
```

Прибирання: команда нижче зупиняє стек і **видаляє всі його дані** — томи баз, локально зібрані образи й файл `.jane/stack-jane-doc-llm.json` зі згенерованими паролями.

```powershell
just down -v --project jane-doc-llm
```

## Моніторинг

| Точка | Що показує |
|---|---|
| `GET /v1/health` | `ok` або `down` (HTTP 503); перевірка `store` — доступність сховища |
| `GET /v1/info` | версія, `capabilities` (`provider_kinds`, `store`), режим автентифікації, ефективні контрактні ліміти |
| `GET /metrics` | метрики Prometheus |
| `GET /v1/budgets` | стан кожного бюджету: витрачено, ліміт, `exhausted`, час скидання |
| `GET /v1/usage` | витрати за днями, моделями, метою, рівнями |

Метрики шлюзу (крім загальних `jane_http_*`):

| Метрика | Мітки | Зміст |
|---|---|---|
| `jane_llm_requests_total` | `provider`, `model`, `outcome` | виклики провайдера; `outcome`: `ok`, `invalid_output`, `error` |
| `jane_llm_budget_rejections_total` | `scope_type` | виклики, зупинені бюджетом |

Що спостерігати: зростання `outcome="error"` — проблеми провайдера; зростання `jane_llm_budget_rejections_total` — вичерпані бюджети; `exhausted: true` у `GET /v1/budgets` — рівень, на якому зупинено виклики. Загальний моніторинг платформи — [моніторинг](../../operations/monitoring.md).

## Журнали

Журнал — JSON (`JANE_LLM_LOG_FORMAT=json`) або текст (`console`). Ключові записи:

| Повідомлення | Рівень | Поля |
|---|---|---|
| `configured limits` | INFO | ефективні ліміти з походженням кожного значення, `store` |
| `store=memory: budgets and usage are per process…` | WARNING | режим `memory` |
| `completion` | INFO | `completion_id`, `provider`, `model`, `purpose`, `valid`, `input_tokens`, `output_tokens`, `cost`, `test_mode`, `duration_ms` |
| `anthropic rejected the request` | WARNING | HTTP-статус і тип помилки провайдера, без вмісту запиту |
| `jobs of stopped instances ended` | WARNING | job, завершені після зупинки іншого екземпляра |
| `fake provider holds its answer` | INFO | затримка сценарію `fake` |

Інструкції, дані, відповіді моделі й значення секретів у журнал не пишуться.

## Оновлення й міграції

- Схема бази створюється й доповнюється під час старту (`CREATE … IF NOT EXISTS`) під advisory-блокуванням, тож кілька екземплярів, що стартують одночасно, не заважають один одному. Окремої команди міграції немає.
- Оновлення: зупиніть екземпляр, розгорніть нову версію, запустіть. Нові екземпляри можна піднімати поруч зі старими лише в межах однієї версії схеми; сумісність різних версій у змішаному кластері не перевірялася.
- Конфігурацію (провайдерів, псевдоніми, бюджети, підключення) seed-файл не оновлює — змінюйте її через API.
- Нові ціни провайдера: `PUT /v1/providers/{provider_id}` з оновленими `models[].pricing`; уже записані витрати не перераховуються.

Загальний порядок оновлення платформи — [оновлення](../../operations/upgrades.md).

## Резервування й відновлення

Дані сервісу — лише його схема (`llm`) у власній базі. Резервна копія — `pg_dump` цієї схеми; відновлення — у порожню базу до старту сервісу. Що втрачається без копії: конфігурація провайдерів і бюджетів (відновлюється seed-файлом і API), журнал витрат і лічильники (відновити неможливо — бюджети поточних вікон почнуться з нуля), ключі ідемпотентності (повтор старого запиту виконається знову). Процедуру для платформи — [резервування й відновлення](../../operations/backup-restore.md). У цій документації резервування схеми `llm` не виконувалося.

## Масштабування

- **Кілька екземплярів** — лише з `JANE_LLM_STORE=postgres` і спільною базою: бюджети, частота, ключі ідемпотентності й job спільні, перевірка бюджету атомарна. Це перевіряють інтеграційні тести `services/llm/tests/test_multi_instance.py`.
- **`memory`** — один процес; кілька таких екземплярів мають окремі бюджети, тож разом можуть перевищити ліміт.
- **Пропускна здатність** обмежена частотою провайдера (`max_requests_per_minute` провайдера й рівнів) і `jobs.max_concurrent_jobs` для асинхронних операцій. Пул з'єднань (`JANE_LLM_DB_POOL_MAX_SIZE`) узгоджуйте з навантаженням.

Загальні правила — [масштабування](../../operations/scaling.md).

## Власність даних

LLM gateway володіє своєю базою `jane_llm` (dev-стек) і схемою `JANE_LLM_DB_SCHEMA`. Інші модулі читають ці дані лише через API: бюджети й облік — `llm.v1`, результати викликів — `GET /v1/invocations/{id}`. Сутності, витягнуті LLM-пакетами, шлюз не зберігає: їх записує етап Storage. Карта платформи — [власність даних](../../architecture/data-ownership.md).

## Тести

| Команда | Що перевіряє | Результат 2026-10-11 |
|---|---|---|
| `just test llm` | unit і контрактні тести без зовнішніх сервісів | 99 passed, 51 deselected |
| `just integration --project jane-doc-llm services/llm` | PostgreSQL, кілька екземплярів, сервіс у стеку | 51 passed |

Інтеграційним тестам потрібен запущений стек проєкту (`just up --project jane-doc-llm postgres` або з сервісом `llm`).

## Типові проблеми

| Симптом | Причина | Що зробити |
|---|---|---|
| Сервіс не стартує: `JANE_LLM_DATABASE_URL is required` | режим `postgres` без DSN | задайте DSN або `JANE_LLM_STORE=memory` |
| 404 `model alias 'cheap' is not configured` | псевдонім не створено (типово є лише `default`) | `PUT /v1/model-aliases/cheap` |
| 422 `model … has no pricing` | у моделі провайдера немає `pricing` | додайте ціни в `PUT /v1/providers/{id}` |
| 429 `budget_exhausted` | вичерпано бюджет рівня з `details.scope_type`/`scope_id` | дочекайтеся `period_resets_at` або збільште бюджет |
| 429 `budget_exhausted` при `spent = 0` | `amount: 0` або оцінка резерву більша за залишок | збільште бюджет або зменште `max_output_tokens` чи дані |
| 422 `limit_exceeded` | оцінка входу більша за `max_input_tokens_per_request` чи контекст моделі | зменште дані або підніміть ліміт |
| 502 `upstream_unavailable`, `retryable: false` | провайдер відхилив запит (ключ, модель, формат) | журнал `anthropic rejected the request`; `POST /v1/connections/{id}/test` |
| `secrets_resolved: {"api_key": false}` | змінна без префікса `JANE_SECRET_`, файл поза `JANE_LLM_SECRET_FILES_DIR` або `api_base` не в дозволеному списку | виправте посилання чи політику |
| 422 `secret_detected` на `PUT /v1/connections` | ключ чи значення в `params` схоже на секрет | перенесіть його в `secret_refs` |
| Відповідь 200 з `"valid": false` | вихід моделі не відповідає схемі після всіх спроб | спростіть схему, збільште `max_output_tokens` (`finish_reason: length`) |
| Результат обробника `empty` з `fake` | без сценарію `fake` повертає мінімальну відповідь | налаштуйте сценарій або реальний провайдер |
