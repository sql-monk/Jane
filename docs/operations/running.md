# Запуск і зупинка

Сторінка описує, як запускати й зупиняти платформу в dev-стеку, як запускати окремі сервіси та як перевести Orchestrator у режим без планувальника й воркерів для обслуговування. Перший запуск з адмінкою — [README.md](../../README.md#швидкий-старт); будова стеку — [infra/README.md](../../infra/README.md).

## Зміст

- [Передумови](#передумови)
- [Запуск стеку](#запуск-стеку)
- [Перевірка після запуску](#перевірка-після-запуску)
- [Зупинка](#зупинка)
- [Orchestrator без планувальника й воркерів](#orchestrator-без-планувальника-й-воркерів)
- [Окремий процес воркерів Orchestrator](#окремий-процес-воркерів-orchestrator)
- [Сервіс без Docker](#сервіс-без-docker)

## Передумови

- uv, just, Docker із Compose v2; встановлення — [README.md](../../README.md#передумови).
- Команди виконуються з кореня репозиторію.
- Для Handler Runtime потрібен образ пісочниці (`jane-handler-runtime build-image`) і доступ до Docker-сокета — [Handler Runtime](../components/handler-runtime/operations.md).

## Запуск стеку

1. Запустіть потрібні сервіси. Інфраструктура (PostgreSQL, MinIO тощо) стартує як залежність:

   ```powershell
   just up orchestrator registry storage
   ```

2. Щоб сервіси знали адреси одне одного (виконавці Orchestrator, Registry для колекторів), скопіюйте `infra/compose.local.example.yaml` в `infra/compose.local.yaml` перед `just up` — [локальне доповнення](../../infra/README.md#локальне-доповнення-composelocalyaml).

3. Для стеку з одним профілем лімітів на всі сервіси використовуйте `deploy/profiles/stack.py` — [профілі](../../deploy/profiles/README.md#стек-з-профілем-stackpy).

Назва проєкту й порти типово унікальні для checkout. Фіксовані порти задаються змінними `JANE_PORT_<СЕРВІС>` і мають бути в середовищі **кожного** `just up` цього проєкту: інакше Docker вибере інший порт під час перестворення контейнера.

## Перевірка після запуску

```powershell
just ps
just env
```

Очікуваний результат: у стовпці `STATUS` кожного контейнера — `(healthy)`, у `just env` — адреси сервісів. Перевірка одного сервісу:

```powershell
curl.exe -s http://127.0.0.1:19010/v1/health
```

```json
{"status":"ok","checks":{"database":{"status":"ok"}}}
```

Вивід отримано 2026-10-11 на стеку `jane-doc-ops` з Orchestrator на порту 19010. Значення `status` і HTTP-коди — [моніторинг](monitoring.md#health).

## Зупинка

Зупинка зі збереженням даних (контейнери й мережа видаляються, томи й файл стеку лишаються):

```powershell
just down
```

Наступний `just up` для того ж проєкту бере облікові дані з `.jane/stack-<проєкт>.json` і під'єднується до тих самих томів.

Команда нижче **видаляє всі дані стеку**: томи баз і сховищ, локально зібрані образи й файл `.jane/stack-<проєкт>.json` із паролями та ключами API.

```powershell
just down -v
```

Для іншого проєкту додайте `--project <назва>`. Команди `just down` зачіпають лише контейнери, мережі й томи цього compose-проєкту.

## Orchestrator без планувальника й воркерів

Для резервування, відновлення або оновлення Orchestrator можна запустити лише з API: розклади не запускають нових запусків, воркери не беруть елементи черги.

| Змінна | Типово | Дія при `false` |
|---|---|---|
| `JANE_ORCHESTRATOR_SCHEDULER_ENABLED` | `true` | воркери не створюють запусків за розкладом |
| `JANE_ORCHESTRATOR_RUN_WORKERS` | `true` | процес API не запускає потоків воркерів |

`infra/compose.yaml` і `deploy/profiles/compose.stack.yaml` передають ці змінні з середовища викликача. PowerShell:

```powershell
$env:JANE_ORCHESTRATOR_SCHEDULER_ENABLED = "false"
$env:JANE_ORCHESTRATOR_RUN_WORKERS = "false"
just up orchestrator --no-build
```

Bash:

```bash
JANE_ORCHESTRATOR_SCHEDULER_ENABLED=false JANE_ORCHESTRATOR_RUN_WORKERS=false just up orchestrator --no-build
```

Compose перестворює контейнер із новими змінними. Перевірка:

```powershell
docker inspect <проєкт>-orchestrator-1 --format "{{range .Config.Env}}{{println .}}{{end}}"
```

У виводі мають бути `JANE_ORCHESTRATOR_SCHEDULER_ENABLED=false` і `JANE_ORCHESTRATOR_RUN_WORKERS=false` (перевірено 2026-10-11 на стеку `jane-doc-ops`). Щоб повернути звичайний режим, приберіть змінні із середовища й повторіть `just up orchestrator --no-build`.

Обмеження: API продовжує приймати запити, зокрема створення запусків вручну; вони чекатимуть у черзі, доки не запрацюють воркери. Якщо працюють окремі процеси воркерів (наступний розділ), їх треба зупинити окремо.

## Окремий процес воркерів Orchestrator

`python -m jane_orchestrator worker` запускає лише воркери без HTTP: `JANE_ORCHESTRATOR_LIMITS__ENGINE__WORKERS` потоків (типово 2, щонайменше 1). Кілька таких процесів ділять чергу в PostgreSQL. API-процес тоді запускають із `JANE_ORCHESTRATOR_RUN_WORKERS=false`. У `infra/compose.yaml` окремого сервісу воркерів немає; цей режим описано за кодом (`services/orchestrator/src/jane_orchestrator/__main__.py`) і в dev-стеку не перевірявся.

## Сервіс без Docker

Кожен сервіс запускається як `python -m jane_<сервіс>`, наприклад:

```powershell
uv run --package jane-web-collector python -m jane_web_collector
```

Без змінної `JANE_<СЕРВІС>_AUTH_MODE` сервіс працює в режимі `none` і слухає лише `127.0.0.1` — лише для локальної роботи. Залежності й параметри кожного сервісу — `quickstart.md` і `configuration.md` у комплекті модуля, наприклад [Web Collector](../components/web-collector/quickstart.md).
