# Профілі лімітів

`deploy/profiles/` містить початкові профілі лімітів Jane для цільових середовищ, засоби їх перевірки та окремий стек, у якому один профіль застосовано до всіх сервісів. Профіль — це документ `PlatformLimits` зі схеми [limits.schema.json](../../contracts/schemas/common/limits.schema.json): назва, типові значення й жорсткі стелі (`hard_caps`). Він змінює ліміти виконання без зміни коду (ТЗ §12, критерій 13).

Як сервіси успадковують ліміти й як змінювати їх у роботі — [ліміти й профілі](../../docs/operations/limits.md). Сценарії вимірювань — [перевірка профілів](../../docs/operations/limits-validation.md).

## Зміст

- [Склад каталогу](#склад-каталогу)
- [Профілі](#профілі)
- [Перевірка схеми: check.py](#перевірка-схеми-checkpy)
- [Стек з профілем: stack.py](#стек-з-профілем-stackpy)
- [Як профіль доходить до сервісів](#як-профіль-доходить-до-сервісів)
- [Вимірювання профілю](#вимірювання-профілю)
- [Тести](#тести)

## Склад каталогу

```text
deploy/profiles/
├── dev-laptop.json          # профіль PlatformLimits для ноутбука розробника
├── ci.json                  # профіль для runner CI (ubuntu-24.04)
├── single-node.json         # профіль для одного сервера
├── check.py                 # перевірка трьох профілів за схемою limits.schema.json
├── stack.py                 # ізольований стек Jane з одним профілем для всіх сервісів
├── compose.stack.yaml       # compose-доповнення до infra/compose.yaml для stack.py
├── thresholds.json          # пороги прийнятності вимірювань для dev-laptop і ci
├── harness/
│   ├── limits_harness.py    # вимірювання профілю: сценарії L1–L8
│   ├── metrics.py           # обчислення метрик із сирих журналів
│   ├── probe_site.py        # інструментований HTTP-сайт для вимірювань
│   └── packages/            # тестовий пакет пісочниці harness.sandbox-probe
└── tests/                   # офлайн-тести профілів і harness
```

## Профілі

Усі три профілі задають значення для кожної групи контракту: `concurrency`, `rate`, `crawl`, `timeouts`, `retries`, `queue`, `sandbox`, `llm`, `transfer`, `telegram`. Нижче — значення, якими вони відрізняються.

| Ліміт | `dev-laptop` | `ci` | `single-node` |
|---|---|---|---|
| `concurrency.max_parallel_fetches` | 8 | 4 | 32 |
| `concurrency.max_parallel_fetches_per_host` | 2 | 2 | 4 |
| `concurrency.max_parallel_invocations` | 2 | 2 | 8 |
| `concurrency.max_parallel_runs_per_task` | 1 | 1 | 2 |
| `concurrency.max_parallel_stage_items` | 4 | 2 | 16 |
| `rate.requests_per_second_per_host` | 1 | 50 | 1 |
| `rate.min_delay_ms_per_host` | 500 | 0 | 500 |
| `rate.burst_per_host` | 2 | 10 | 2 |
| `timeouts.invocation_timeout_ms` | 90000 | 60000 | 60000 |
| `queue.max_queue_depth` | 10000 | 10000 | 100000 |
| `queue.max_inflight_materials` | 100 | 100 | 500 |
| `queue.max_unacked_materials` | 500 | 500 | 2000 |
| `sandbox.wall_time_ms` | 60000 | 30000 | 30000 |
| `llm.budget.amount` (USD) | 5 | 0.01 | 5 |

Жорсткі стелі (`hard_caps`):

| Профіль | Стелі |
|---|---|
| `dev-laptop` | `concurrency.max_parallel_fetches` 16, `concurrency.max_parallel_invocations` 4, `sandbox.memory_mb` 2048, `sandbox.cpu_cores` 2, `sandbox.wall_time_ms` 300000, `llm.max_output_tokens_per_request` 16000 |
| `ci` | `sandbox.memory_mb` 1024, `sandbox.cpu_cores` 1, `sandbox.wall_time_ms` 60000 |
| `single-node` | `concurrency.max_parallel_fetches` 128, `concurrency.max_parallel_invocations` 16, `sandbox.memory_mb` 4096, `sandbox.cpu_cores` 4, `sandbox.wall_time_ms` 600000 |

- `ci` має високу частоту запитів до одного хоста (`rate.requests_per_second_per_host` 50), бо в CI джерелом є лише контрольований тестовий сайт. Для реальних сайтів так не налаштовуйте: `dev-laptop` і `single-node` обмежують 1 запит/с і 500 мс між запитами.
- Бюджет LLM `ci` (0,01 USD) розрахований на детермінований провайдер `fake`, який нічого не коштує.
- Вимірювальне приймання (harness L1–L8) виконано для профілю `ci` — [перевірка профілів](../../docs/operations/limits-validation.md#результати-приймання).

## Перевірка схеми: check.py

`check.py` перевіряє три профілі за `$defs/PlatformLimits` зі схеми лімітів і звіряє поле `profile` з назвою файлу.

```powershell
uv run --all-packages python deploy/profiles/check.py
```

Вивід запуску 2026-10-11, ревізія `48389a3`, Windows 11:

```text
deploy\profiles\dev-laptop.json: schema valid
deploy\profiles\ci.json: schema valid
deploy\profiles\single-node.json: schema valid
```

## Стек з профілем: stack.py

`stack.py` піднімає ізольований стек на базі `infra/compose.yaml` і доповнення `compose.stack.yaml`, у якому профіль змонтовано як файл лімітів кожного сервісу. Типовий набір сервісів — ланцюжок прикладів каталогу й перевірки цін: `testsite`, `registry`, `storage`, `handler-runtime`, `web-collector`, `orchestrator` (з їхніми залежностями PostgreSQL і MinIO).

| Команда | Дія |
|---|---|
| `up [--profile P] [--project N] [--services …] [--telegram] [--probe] [--wait-timeout S]` | збирає образ пісочниці й сервіси, запускає стек, чекає health-check (типово 900 с), друкує адреси |
| `env [--project N]` | адреси сервісів без секретів |
| `down [--project N]` | видаляє контейнери, томи, локальні образи, контейнери пісочниці й файли стеку |
| `leftovers [--project N]` | друкує залишки проєкту (контейнери, пісочниці, томи, мережі, образи, файли); код виходу 1, якщо щось лишилося |

```powershell
uv run --all-packages python deploy/profiles/stack.py up --profile ci --project jane-profile-ci
uv run --all-packages python deploy/profiles/stack.py env --project jane-profile-ci
```

Команда нижче **видаляє всі дані стеку** `jane-profile-ci`: контейнери, томи, образи `<проєкт>-*` і образ пісочниці, контейнери з міткою `io.jane.stack=<проєкт>`, файли `.jane/stack-<проєкт>.json`, `.jane/executors-<проєкт>.json` і копію записів Telegram.

```powershell
uv run --all-packages python deploy/profiles/stack.py down --project jane-profile-ci
```

Параметри й поведінка:

- **Профіль** — `--profile`, типово `dev-laptop`; допустимі `dev-laptop`, `ci`, `single-node`.
- **Проєкт** — `--project`, або `JANE_STACK_PROJECT`, або `jane-stack-<6 символів хешу шляху checkout>`. Порти вибирає Docker на `127.0.0.1`.
- **Облікові дані й ключі API** генеруються так само, як у `just up`, і зберігаються у `.jane/stack-<проєкт>.json`; `just env --project <проєкт>` читає цей файл.
- **Виконавці Orchestrator** записуються в `.jane/executors-<проєкт>.json` лише для запущених сервісів.
- **Пісочниця** — образ `<проєкт>-python-extractor:1` збирається командою `jane-handler-runtime build-image`, якщо його немає. Групу Docker-сокета `stack.py` визначає пробним контейнером, якщо не задано `JANE_DOCKER_GID`.
- **Telegram** — `--telegram` додає Telegram Collector з бекендом `recorded` (записи `examples/telegram/recordings`). Реальний бекенд — `JANE_TELEGRAM_BACKEND=telethon` і `JANE_TELEGRAM_EXTRAS=--extra telethon`; секрети облікового запису беруться з середовища оператора (`JANE_SECRET_TG_API_HASH`, `JANE_SECRET_TG_SESSION`). Реальний бекенд тут не перевірявся.
- **Тайм-аут LLM** — `JANE_LLM_PROVIDER_REQUEST_TIMEOUT_MS` (типово 120000) задає `provider.request_timeout_ms` LLM gateway; `timeouts.request_timeout_ms` профілю на виклик моделі не впливає.
- **Режим без планувальника** — `JANE_ORCHESTRATOR_SCHEDULER_ENABLED=false` і `JANE_ORCHESTRATOR_RUN_WORKERS=false` у середовищі `stack.py up` запускають Orchestrator лише з API (для резервування й відновлення).

## Як профіль доходить до сервісів

`compose.stack.yaml` монтує `deploy/profiles/<профіль>.json` у кожен сервіс Jane як `/cfg/limits/platform.json` і задає `JANE_<СЕРВІС>_LIMITS_FILE`.

- **Orchestrator** під час першого старту записує профіль як документ лімітів платформи у свою базу. Пізніші зміни файлу на вже ініціалізовану базу не впливають; змінюйте ліміти через `PUT /v1/limits/platform`. Ефективні ліміти етапу Orchestrator передає виконавцям у кожному виклику.
- **Колектори, Storage, Handler Runtime, Registry, LLM gateway, Assistant** беруть із профілю ліміти, які вони моделюють, як власні ліміти рівня платформи; решту груп ігнорують і пишуть їх у журнал під час старту. `GET /v1/info` показує `limits.profile`.
- Шлях, якого немає ні в контракті, ні в моделі сервісу (наприклад, помилка в назві), — помилка конфігурації: сервіс не стартує.

Докладно про рівні, стелі й походження значень — [ліміти й профілі](../../docs/operations/limits.md).

## Вимірювання профілю

`harness/limits_harness.py` вимірює стек із профілем проти порогів `thresholds.json`: темп запитів до хоста, паралельність, повтори, backpressure, пісочниця, ресурси й наскрізний сценарій. Профілі вимірювання — `dev-laptop` і `ci`.

```powershell
uv run --all-packages python deploy/profiles/harness/limits_harness.py plan --profile ci
```

Уривок виводу запуску 2026-10-11, ревізія `48389a3`:

```text
{
  "profile": "ci",
  "repeat": 1,
  ...
  "estimated_minutes_per_repetition": 6.8,
  "stack_start_minutes": "3-10 (image builds; faster when cached)"
}
```

Запуск вимірювань, оцінка результатів і отримані докази — [перевірка профілів](../../docs/operations/limits-validation.md).

## Тести

`deploy/profiles/tests/` — офлайн-тести (без Docker) профілів, `stack.py` і обчислення метрик harness. Їх запускає `just unit` окремою сесією pytest разом з `examples/`; типи перевіряє `just types`.
