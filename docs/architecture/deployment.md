# Розгортання

Як Jane розгортається зараз: dev-стек на Docker Compose, способи його запуску, профілі лімітів і масштабування сервісів. Експлуатація платформи — [operations](../operations/README.md); покрокові запуски — [початок роботи](../getting-started/README.md).

## Зміст

- [Dev-стек](#dev-стек)
- [Способи запуску](#способи-запуску)
- [Ізоляція паралельних стеків](#ізоляція-паралельних-стеків)
- [Профілі лімітів](#профілі-лімітів)
- [Масштабування](#масштабування)
- [Промислове розгортання](#промислове-розгортання)

## Dev-стек

![Dev-стек: контейнери, бази, томи й proxy](../diagrams/platform/dev-stack.light.png#gh-light-mode-only)
![Dev-стек: контейнери, бази, томи й proxy](../diagrams/platform/dev-stack.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../diagrams/platform/dev-stack.light.png), [темне](../diagrams/platform/dev-stack.dark.png); джерело — [dev-stack.drawio](../diagrams/platform/dev-stack.drawio).

Склад — [infra/compose.yaml](../../infra/compose.yaml):

| Контейнер | Образ або збірка | Порт у контейнері | Том |
|---|---|---|---|
| `postgres` | `postgres:18` | 5432 | `postgres-data` |
| `pg-provision` | `postgres:18`, разовий | — | — |
| `minio` | `pgsty/minio` за дайджестом | 9000, консоль 9001 | `minio-data` |
| `s3` | `chrislusf/seaweedfs:4.47` | 8333 | `s3-data` |
| `sqlserver` | `mcr.microsoft.com/mssql/server:2022-latest` | 1433 | `sqlserver-data` |
| `mongodb` | `mongo:8.0` | 27017 | `mongodb-data` |
| `testsite` | збірка `tests/fixtures/testsite` | 8080 | — |
| `proxy` | `caddy:2-alpine` | 8080 | — |
| `storage` | збірка `services/storage` | 8000 | `storage-data` |
| `handler-runtime` | збірка `services/handler-runtime` | 8000 | `storage-data` лише для читання, сокет Docker |
| `web-collector` | збірка `services/web-collector` | 8101 | `web-collector-data` |
| `telegram-collector` | збірка `services/telegram-collector` | 8102 | `telegram-collector-data` |
| `orchestrator` | збірка `services/orchestrator` | 8000 | — |
| `registry` | збірка `services/registry` | 8000 | — |
| `llm` | збірка `services/llm` | 8110 | `storage-data` лише для читання, `.jane/secrets` |
| `assistant` | збірка `services/assistant` | 8000 | — |

- **Інфраструктура** (`postgres`, `sqlserver`, `mongodb`, `minio`, `s3`, `testsite`, `proxy`) стартує типовою командою `just up` без аргументів. Сервіси застосунку вмикаються явно за назвою (compose-профілі): `just up storage assistant`.
- **`pg-provision`** створює в `postgres` окрему роль і базу для кожного сервісу ([infra/postgres](../../infra/postgres/)).
- **Образи** замінюються змінними `JANE_IMAGE_<СЕРВІС>`.
- **Порти на хості** — `JANE_PORT_<СЕРВІС>`; порожнє значення — Docker обирає вільний порт. Адреса публікації — `JANE_BIND` (типово `127.0.0.1`).
- **Облікові дані** генерує `just up` у файл `.jane/stack-<проєкт>.json` поза Git: паролі баз, MinIO, S3, SQL Server, MongoDB і ключі API.
- **Типові порти сервісів поза контейнером** (`python -m jane_<сервіс>`): Web Collector 8101, Telegram Collector 8102, Registry 8105, Storage 8107, Orchestrator 8109, LLM gateway 8110, Handler Runtime і Assistant 8000; адреса — `127.0.0.1`.

## Способи запуску

| Спосіб | Команда | Що додає до `infra/compose.yaml` | Для чого |
|---|---|---|---|
| Інфраструктура або окремі сервіси | `just up [сервіси]` | нічого | розробка модуля, інтеграційні тести |
| Робоча локальна система | `just up …` з файлом `infra/compose.local.yaml` | зв'язування з `infra/compose.local.example.yaml`: виконавці Orchestrator, адреси Registry, профілі Handler Runtime | Admin UI з реальними даними, реальні сайти й Telegram |
| Ланцюжок із профілем лімітів | `uv run --all-packages python deploy/profiles/stack.py up --project <p>` | [deploy/profiles/compose.stack.yaml](../../deploy/profiles/compose.stack.yaml): профіль лімітів усім сервісам, виконавці, образ пісочниці, записи Telegram | приклади, вимірювання профілів |
| Наскрізні тести | `just e2e` | `tests/e2e/compose.e2e.yaml`; стек створює й прибирає фікстура | приймальні сценарії |

Без зв'язування Orchestrator не має виконавців, а Registry не приймає версій екстракторів — [платформа з Admin UI](../getting-started/platform.md#звязування-сервісів).

## Ізоляція паралельних стеків

На одному хості можна тримати кілька стеків: кожен має унікальну назву compose-проєкту (`--project`; типово `jane-<каталог>-<хеш шляху>` для `just up` і `jane-stack-<хеш>` для `stack.py`). Від назви залежать імена контейнерів, мережі, томів і локально зібраних образів. `just down -v --project <p>` видаляє томи, локальні образи й файл стеку; `stack.py down` додатково видаляє контейнери пісочниць цього стеку, образ пісочниці й перевіряє, що залишків немає.

## Профілі лімітів

Профіль — файл `deploy/profiles/<профіль>.json` із полями `profile`, `defaults` і `hard_caps` (схема `PlatformLimits` у [limits.schema.json](../../contracts/schemas/common/limits.schema.json)).

| Профіль | Пісочниця: пам'ять / CPU / час | `max_parallel_invocations` | `max_parallel_fetches` |
|---|---|---|---|
| `dev-laptop` | 2048 МБ / 2 / 300 с | 2 | 8 |
| `ci` | 1024 МБ / 1 / 60 с | 2 | 4 |
| `single-node` | 4096 МБ / 4 / 600 с | 8 | 32 |

У колонці «Пісочниця» — верхні межі (`hard_caps`). Сервіс отримує профіль файлом `JANE_<СЕРВІС>_LIMITS_FILE` і бере з нього лише ліміти, які моделює; решту пропускає й записує в журнал. Orchestrator під час першого старту засіває з файла ліміти платформи у своїй БД; далі вони змінюються через `PUT /v1/limits/platform`, а ефективні значення для джерела, завдання й етапу показує `GET /v1/limits/effective`. Окреме значення сервісу задає змінна `JANE_<СЕРВІС>_LIMITS__<ГРУПА>__<ПОЛЕ>`.

## Масштабування

- **Orchestrator** — кілька екземплярів або окремі процеси воркерів (`python -m jane_orchestrator worker`) з однією БД; черга елементів і розклад захоплюються через `FOR UPDATE SKIP LOCKED` — [відновлення після збою](task-execution.md#відновлення-після-збою).
- **Web Collector** — кілька екземплярів узгоджують ліміти хоста через спільний каталог стану.
- **Handler Runtime, Assistant** — кілька екземплярів потребують PostgreSQL (`STATE_DSN`); без нього стан у пам'яті.
- **Storage, Registry, LLM gateway** — стан у зовнішніх сховищах; паралельний запис тієї самої сутності Storage розв'язує порівнянням версій і внутрішніми повторами.
- **Посилання `file://`** на RAW і транзитні blob працюють лише на одному вузлі зі спільним томом `storage-data`; між вузлами потрібне об'єктне сховище.

Масштабування кількома екземплярами в цій документації не перевірялося; сценарії з репліками є серед наскрізних тестів (`tests/e2e/test_r06_*`, `tests/e2e/test_shared_host_replicas.py`).

## Промислове розгортання

Готових маніфестів промислового розгортання (Kubernetes, Helm, окремих compose-файлів для сервера) у репозиторії немає. Кожен сервіс має `Dockerfile` і запускається з налаштуваннями зі змінних середовища; для розгортання поза dev-стеком потрібно задати режим автентифікації, сховища стану, адреси сусідів, виконавців Orchestrator і профіль лімітів — див. `configuration.md` і `operations.md` модулів у [каталозі](../components/README.md).
