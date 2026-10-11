# Handler Runtime: будова

Сторінка описує, як Handler Runtime перевіряє пакет, запускає пісочницю, класифікує результат і зберігає власний стан. Публічні типи й члени коду — [довідник типів](reference/types/README.md).

## Зміст

- [Компоненти](#компоненти)
- [Хід виклику](#хід-виклику)
- [Перевірки до запуску](#перевірки-до-запуску)
- [Пісочниця Docker](#пісочниця-docker)
- [Класифікація результату](#класифікація-результату)
- [Стани job](#стани-job)
- [Кеш пакетів](#кеш-пакетів)
- [Стан сервісу](#стан-сервісу)
- [Гарантії](#гарантії)

## Компоненти

![Компоненти Handler Runtime і зовнішні залежності](../../diagrams/handler-runtime/components.light.png#gh-light-mode-only)
![Компоненти Handler Runtime і зовнішні залежності](../../diagrams/handler-runtime/components.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/handler-runtime/components.light.png), [темне](../../diagrams/handler-runtime/components.dark.png); джерело — [components.drawio](../../diagrams/handler-runtime/components.drawio).

HTTP API і CLI використовують ті самі об'єкти, які збирає `build_runtime` у [runtime.py](../../../services/handler-runtime/src/jane_handler_runtime/runtime.py), тому CLI-прогін поводиться так само, як виклик сервісу.

| Модуль | Відповідальність |
|---|---|
| [app.py](../../../services/handler-runtime/src/jane_handler_runtime/app.py) | маршрути `handler.v1`, ідемпотентність, job, health і `/v1/info` |
| [cli.py](../../../services/handler-runtime/src/jane_handler_runtime/cli.py) | команди `run`, `test`, `profile`, `build-image`, `serve` |
| [executor.py](../../../services/handler-runtime/src/jane_handler_runtime/executor.py) | `Executor`: перевірки, підготовка робочого каталогу, запуск, класифікація |
| [packages.py](../../../services/handler-runtime/src/jane_handler_runtime/packages.py) | `PackageStore` (архів, Registry, кеш за дайджестом), `ContentFetcher` (`ContentRef`) |
| [sandbox.py](../../../services/handler-runtime/src/jane_handler_runtime/sandbox.py) | протокол `SandboxBackend`, `Bundle`, `SandboxOutcome`, бекенд `subprocess` |
| [docker_sandbox.py](../../../services/handler-runtime/src/jane_handler_runtime/docker_sandbox.py) | бекенд `docker`: контейнер на виклик через Engine API |
| [profiles](../../../services/handler-runtime/src/jane_handler_runtime/profiles/__init__.py) | опис профілів і перевірка PEP 508 залежностей |
| [testrun.py](../../../services/handler-runtime/src/jane_handler_runtime/testrun.py) | вибір тестів маніфесту, прогін, `TestReport` |
| [state.py](../../../services/handler-runtime/src/jane_handler_runtime/state.py) | стан у пам'яті або PostgreSQL |
| [schemas.py](../../../services/handler-runtime/src/jane_handler_runtime/schemas.py) | перевірка за схемами контрактів і пакета |
| [settings.py](../../../services/handler-runtime/src/jane_handler_runtime/settings.py) | налаштування й моделі лімітів |

## Хід виклику

![Послідовність виклику обробника: API, Executor, Docker Engine, раннер SDK](../../diagrams/handler-runtime/invocation-sequence.light.png#gh-light-mode-only)
![Послідовність виклику обробника: API, Executor, Docker Engine, раннер SDK](../../diagrams/handler-runtime/invocation-sequence.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/handler-runtime/invocation-sequence.light.png), [темне](../../diagrams/handler-runtime/invocation-sequence.dark.png); джерело — [invocation-sequence.drawio](../../diagrams/handler-runtime/invocation-sequence.drawio).

1. API перевіряє тіло за `handler-invocation.schema.json` і збіг `Idempotency-Key` з `delivery.delivery_key`, потім шукає ключ у сховищі ідемпотентності. Знайдений завершений ключ — відповідь зі сховища без нового запуску.
2. `Executor.prepare` виконує всі [перевірки до запуску](#перевірки-до-запуску). Помилка тут — HTTP-помилка, пісочниця не запускається, job не створюється.
3. API створює job `invocation` з міткою `invocation_id`. У режимі `sync` чекає його до `sync_response_max_ms`; не дочекався — 202 з job, виклик триває у фоні.
4. `Executor.run` чекає слота `max_parallel_invocations`, збирає робочий каталог (`request.json`, `package/…`, `inputs/<n>`) і передає бекенду. Увесь виклик бекенда обмежено `invocation_timeout_ms`.
5. Бекенд запускає раннер SDK; той викликає `extract` для кожного входу і пише один JSON-документ у stdout ([протокол раннера](../extractor-sdk/internals.md#протокол-раннера)).
6. `Executor.interpret` перетворює вихід на `HandlerResult` ([класифікація](#класифікація-результату)); результат зберігається для `GET /v1/invocations/{invocation_id}` і стає `Job.result`.

## Перевірки до запуску

| Перевірка | Помилка |
|---|---|
| пакет завантажено, дайджест збігається, архів безпечний (шляхи, символьні посилання, розміри, кількість файлів) | `validation_failed`, `digest_mismatch`, `not_found`, `upstream_unavailable` |
| маніфест відповідає `package-manifest.schema.json`, `package_id` і `version` збігаються з `handler` | `validation_failed` |
| `kind` — `extractor` або `transform`, `entry.runtime` — `python` | `validation_failed` |
| `access.network` — `none` | `validation_failed` |
| профіль є і має образ; `dependencies.python` задовольняють точні версії профілю | `dependency_not_allowed` |
| `params` після типових значень відповідають `params_schema` | `validation_failed` з `/params/...` |
| ліміти запиту дійсні | `validation_failed` |
| вид і тип кожного входу дозволені маніфестом, вміст прочитано й перевірено | `validation_failed`, `limit_exceeded`, `not_found` |

Залежності перевіряються як вимоги PEP 508 проти середовища Linux-контейнера профілю (`python_version` 3.12, `sys_platform` linux), а не хоста. URL-залежності заборонені.

## Пісочниця Docker

Кожен виклик — новий контейнер з образу профілю; жоден стан не переходить між викликами.

| Налаштування контейнера | Значення |
|---|---|
| мережа | `network_mode=none`, `network_disabled`: є лише `lo` |
| файлова система | коренева read-only; `/tmp` — `tmpfs` розміром `tmpfs_mb` з `noexec`; `/work` — анонімний том, файли власності root з правами лише на читання |
| користувач і права | `65534:65534`, `cap_drop=ALL`, `no-new-privileges`, `ipc_mode=none`, типовий seccomp |
| ресурси | `mem_limit` = `memswap_limit` = `memory_mb`, `nano_cpus` з `cpu_cores`, `pids_limit` = `max_processes` |
| середовище | лише `HOME=/tmp`, `PYTHONDONTWRITEBYTECODE`, `PYTHONUNBUFFERED` і змінні базового образу; секретів немає |
| команда | `timeout -s KILL <wall_time_ms + kill_grace_ms> python -I -m jane_extractor_sdk.runner /work` |
| мітки | `io.jane.handler-runtime.sandbox=1`, `io.jane.invocation-id`, `io.jane.package` і `SANDBOX_LABELS` |
| журнал рушія | `json-file` з обмеженим розміром; stdout і stderr читаються до `max_output_bytes` |

Runtime чекає завершення `wall_time_ms`; не дочекався — `kill` контейнера. Внутрішній `timeout -s KILL` спрацьовує на `kill_grace_ms` пізніше на випадок, якщо сам runtime зупинився. Після читання журналів контейнер видаляється разом з томом `/work`.

Перевірочний прогін тестового пакета `wp06.sandbox-probe` (Docker Desktop 29.8) показав: `uid` 65534, запис у `/` — `Read-only file system`, у `/work/package` і `/work` — `Permission denied`, у `/tmp` — дозволено, мережеві інтерфейси — лише `lo`. Інші результати прогону — [operations.md](operations.md#перевірка-ізоляції).

Бекенд `subprocess` запускає ту саму команду раннера поточним інтерпретатором у тимчасовому каталозі `jane-sbx-*` з мінімальним середовищем. Обмежень мережі, файлової системи, пам'яті й процесів немає.

## Класифікація результату

![Алгоритм класифікації результату пісочниці](../../diagrams/handler-runtime/result-classification.light.png#gh-light-mode-only)
![Алгоритм класифікації результату пісочниці](../../diagrams/handler-runtime/result-classification.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/handler-runtime/result-classification.light.png), [темне](../../diagrams/handler-runtime/result-classification.dark.png); джерело — [result-classification.drawio](../../diagrams/handler-runtime/result-classification.drawio).

Перевірки йдуть у порядку схеми; перша, що спрацювала, визначає `failure.kind`:

| `failure.kind` | Причина | `failure.details` |
|---|---|---|
| `timeout` | перевищено `wall_time_ms` або `invocation_timeout_ms` | `wall_time_ms`, ім'я контейнера |
| `resource_exceeded` | рушій повідомив OOM або процес убито SIGKILL, якого не надсилав runtime, під лімітом пам'яті; stdout довший за `max_output_bytes` | `memory_mb`, `exit_code`, `evidence` або `max_output_bytes` |
| `execution_error` | stdout не є JSON протоколу (раннер упав, процеси вичерпано); виняток під час `import` чи `extract` | `exit_code` або `stage`, `input`, `traceback` |
| `sandbox_violation` | аудит-хук раннера зафіксував спробу мережі чи запуску процесу | `violations`, перша помилка коду |
| `schema_mismatch` | сутність не оголошена в `output.entities`, поле `null`, поля не відповідають схемі, немає ключа, `data` не відповідає `data_schema`, недійсна діагностика | список у `diagnostics.validation_errors` |

`sandbox_violation` фіксується, навіть якщо код перехопив виняток: межею безпеки є контейнер, а аудит-хук лише пояснює, що сталося. `retryable` у всіх цих випадках — `false`: повтор того самого виклику дасть той самий результат.

Якщо помилок немає, статус визначається за статусами входів: є `unrecognized` — `unrecognized` (з `partial: true`, якщо є сутності); інакше є `success` — `success`; інакше `empty`. Для екстрактора `output.entities` присутній завжди, для `transform` — `output.data`.

Хвіст stderr (до `max_stderr_in_result_bytes`) додається в `diagnostics.logs_ref` як inline-текст; метрики `duration_ms`, `output_bytes`, `cpu_ms`, `peak_memory_mb` — у `diagnostics.metrics`.

## Стани job

![Стани job виклику й тест-прогону](../../diagrams/handler-runtime/job-states.light.png#gh-light-mode-only)
![Стани job виклику й тест-прогону](../../diagrams/handler-runtime/job-states.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/handler-runtime/job-states.light.png), [темне](../../diagrams/handler-runtime/job-states.dark.png); джерело — [job-states.drawio](../../diagrams/handler-runtime/job-states.drawio).

Job належить спільному механізму jane-kit. Особливість Handler Runtime — скасування: окрім зміни стану, сервіс зупиняє контейнер виклику за міткою `io.jane.invocation-id` на своєму рушії. Якщо скасування надійшло, поки пісочниця працювала в іншого екземпляра, той екземпляр після завершення перевіряє стан і не зберігає результат.

## Кеш пакетів

- Ключ кешу — дайджест архіву (`sha256:<hex>`); каталог — `<кеш>/<hex>`. Розпакування йде в тимчасовий каталог і атомарно перейменовується.
- У пам'яті — LRU на `packages.cache_max_entries` записів; витіснений запис видаляється з диска.
- Пакет із тим самим дайджестом не розпаковується вдруге; той самий пакет, отриманий з Registry і як архів, має один запис.
- Локальний каталог у CLI перетворюється на канонічний zip, тому має той самий дайджест, що й опублікована версія.

## Стан сервісу

Сервіс зберігає три види даних: ключі ідемпотентності, job і результати викликів. Бізнес-даних немає.

| Режим | Де | Межі |
|---|---|---|
| `memory` | словники в процесі | один екземпляр; ключів — `in_memory_max_entries`, результатів — `max_stored_results`; зникає після перезапуску |
| `postgresql` | схема `state_schema` у базі з `STATE_DSN` | кілька екземплярів; lease, перебирання ключів і job зниклого екземпляра |

![Таблиці стану Handler Runtime у PostgreSQL](../../diagrams/handler-runtime/state-er.light.png#gh-light-mode-only)
![Таблиці стану Handler Runtime у PostgreSQL](../../diagrams/handler-runtime/state-er.dark.png#gh-dark-mode-only)

Зображення для теми: [світле](../../diagrams/handler-runtime/state-er.light.png), [темне](../../diagrams/handler-runtime/state-er.dark.png); джерело — [state-er.drawio](../../diagrams/handler-runtime/state-er.drawio).

- `idempotency` і `jobs` — спільні сховища jane-kit (`PgIdempotencyStore`, `PgJobStore`): ключ має стан, відбиток тіла запиту, термін дії й lease власника; job — документ `Job` у `doc` з lease власника.
- `results` — власна таблиця сервісу: `HandlerResult` за `invocation_id`. Під час кожного запису видаляються результати, старші за `idempotency_ttl_seconds`.
- Таблиці створюються й оновлюються під час запуску в одній транзакції під advisory-lock, тому кілька екземплярів можуть стартувати одночасно.

Схему перевірено читанням коду (`state.py`, `jane_kit/stores/postgres.py`), не запуском із PostgreSQL.

## Гарантії

- **Ізоляція викликів.** Свіжий контейнер на кожен виклик, без мережі, з read-only файловою системою і без секретів; дані одного виклику недоступні іншому.
- **Відповідність контракту.** Сутності завжди перевіряються за схемами пакета й `entity.schema.json`; невідповідний вихід не повертається як `success`.
- **Відтворюваність.** Пакет виконується за дайджестом; залежності — лише точні версії профілю, без встановлення під час виконання.
- **Повторна доставка.** Той самий `delivery_key` у межах TTL не запускає пісочницю вдруге і повертає `duplicate: true`.
- **Без побічних ефектів.** Сервіс не пише сутності в сховища; `test_mode` для нього інформаційний і передається коду пакета.
