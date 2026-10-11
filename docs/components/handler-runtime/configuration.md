# Handler Runtime: конфігурація

Handler Runtime налаштовується змінними середовища з префіксом `JANE_HANDLER_RUNTIME_` і лімітами, які можна задати файлом платформи, змінними або в запиті. Код налаштувань — [settings.py](../../../services/handler-runtime/src/jane_handler_runtime/settings.py).

## Зміст

- [Як задаються значення](#як-задаються-значення)
- [Процес і автентифікація](#процес-і-автентифікація)
- [Бекенд пісочниці](#бекенд-пісочниці)
- [Профілі й образи](#профілі-й-образи)
- [Пакети та вміст](#пакети-та-вміст)
- [Стан](#стан)
- [Ліміти](#ліміти)
- [Параметри CLI](#параметри-cli)
- [Як застосовуються зміни](#як-застосовуються-зміни)

## Як задаються значення

- Змінна середовища: `JANE_HANDLER_RUNTIME_<НАЗВА>` (регістр не важливий). Списки й словники — JSON, наприклад `JANE_HANDLER_RUNTIME_BLOB_ROOTS='["/data/raw"]'`.
- Помилка в значенні (тип, шаблон, недійсний хост у списку дозволених) зупиняє сервіс під час запуску.
- Секрети (`REGISTRY_TOKEN`, `STATE_DSN`) не потрапляють у журнали й `/v1/info`.

## Процес і автентифікація

Спільні параметри процесу описано в [конфігурації jane-kit](../jane-kit/configuration.md); тут — значення для Handler Runtime.

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_HANDLER_RUNTIME_HOST` | рядок | `127.0.0.1` | адреса прослуховування; в образі сервісу — `0.0.0.0` |
| `JANE_HANDLER_RUNTIME_PORT` | ціле | `8000` | порт HTTP |
| `JANE_HANDLER_RUNTIME_LOG_LEVEL` | рядок | `INFO` | рівень журналу |
| `JANE_HANDLER_RUNTIME_LOG_FORMAT` | `json`, `console` | `json` | формат журналу |
| `JANE_HANDLER_RUNTIME_METRICS_ENABLED` | булеве | `true` | `/metrics` |
| `JANE_HANDLER_RUNTIME_HEALTH_CHECK_TIMEOUT_MS` | ціле | `2000` | тайм-аут кожної перевірки `/v1/health` |
| `JANE_HANDLER_RUNTIME_INSTANCE_ID` | рядок | хост-PID-UUID | власник lease job і ключів у PostgreSQL |
| `JANE_HANDLER_RUNTIME_AUTH_MODE` | `none`, `api_key`, `jwt` | `none` | автентифікація; `none` — лише локально |
| `JANE_HANDLER_RUNTIME_API_KEYS` | JSON | `[]` | ключі для `api_key` з областями доступу |
| `JANE_HANDLER_RUNTIME_LIMITS_FILE` | шлях | — | файл лімітів платформи |

Області доступу операцій:

| Операція | Область |
|---|---|
| `POST /v1/invocations`, `GET /v1/invocations/{invocation_id}` | `handler:invoke` |
| `POST /v1/test-runs` | `handler:test` |
| `GET /v1/jobs/{job_id}`, `POST /v1/jobs/{job_id}/cancel` | `handler:invoke` або `handler:test` |
| `GET /v1/connections` | `handler:invoke` або `connections:write` |

У dev-стеку (`infra/compose.yaml`) сервіс працює з `api_key`: ключ `admin` має `handler:invoke`, `handler:test`, `connections:write`; `orchestrator` — `handler:invoke`, `connections:write`; `assistant` — `handler:invoke`, `handler:test`.

## Бекенд пісочниці

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_HANDLER_RUNTIME_SANDBOX_BACKEND` | `docker`, `subprocess` | `docker` | де виконується код пакета |
| `JANE_HANDLER_RUNTIME_ALLOW_UNSAFE_SUBPROCESS` | булеве | `false` | дозвіл бекенда `subprocess` |
| `JANE_HANDLER_RUNTIME_DOCKER_HOST` | рядок | `DOCKER_HOST` або типовий сокет | адреса Docker або Podman API |
| `JANE_HANDLER_RUNTIME_DOCKER_RUNTIME` | рядок | — | OCI runtime контейнерів, наприклад `runsc` |
| `JANE_HANDLER_RUNTIME_SANDBOX_USER` | `uid:gid` | `65534:65534` | користувач у контейнері, не root |
| `JANE_HANDLER_RUNTIME_SANDBOX_LABELS` | JSON-словник | `{}` | додаткові мітки контейнерів, наприклад для прибирання тестового стека |

**`docker`** — один свіжий контейнер на виклик: `network_mode=none`, read-only коренева ФС, `tmpfs` для `/tmp`, `cap_drop=ALL`, `no-new-privileges`, ліміти пам'яті без swap, CPU, кількості процесів. Деталі — [internals.md](internals.md#пісочниця-docker).

**`subprocess`** — раннер SDK як локальний процес поточного інтерпретатора. Мережа, файлова система й пам'ять **не обмежуються**, діє лише `wall_time_ms` і обрізання виводу. Використовуйте лише для довірених власних пакетів у розробці й тестах. Без `ALLOW_UNSAFE_SUBPROCESS=true` (у CLI — `--unsafe-no-sandbox`) кожен виклик повертає 503 `service_unavailable`, а health — `sandbox: down`. Пакети в цьому режимі бачать бібліотеки інтерпретатора сервісу, а не профілю.

## Профілі й образи

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_HANDLER_RUNTIME_PROFILE_IMAGES` | JSON-словник | `{"python-extractor@1": "jane/python-extractor:1"}` | образ для кожного профілю виконання |

Пакет обирає профіль у `dependencies.runtime_profile` (типово `python-extractor@1`). Якщо профілю немає в описі сервісу або в `PROFILE_IMAGES`, виклик відхиляється з 422 `dependency_not_allowed`. У продакшні закріплюйте образ дайджестом: `"python-extractor@1": "registry.example/jane/python-extractor@sha256:..."`.

## Пакети та вміст

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_HANDLER_RUNTIME_REGISTRY_URL` | URL | — | Registry для пакетів без `package_archive` |
| `JANE_HANDLER_RUNTIME_REGISTRY_TOKEN` | секрет | — | Bearer-токен для Registry |
| `JANE_HANDLER_RUNTIME_PACKAGE_CACHE_DIR` | шлях | тимчасовий каталог | кеш розпакованих пакетів за дайджестом |
| `JANE_HANDLER_RUNTIME_BLOB_ROOTS` | JSON-список шляхів | `[]` | каталоги, з яких дозволено читати `file://` |
| `JANE_HANDLER_RUNTIME_DOWNLOAD_HOST_ALLOWLIST` | JSON-список | `[]` | `host` або `host:port` для `download_url` |
| `JANE_HANDLER_RUNTIME_CONTRACTS_DIR` | шлях | пошук від коду вгору | каталог `contracts/` |

Тимчасовий кеш пакетів сервіс видаляє під час штатної зупинки. Каталог із `PACKAGE_CACHE_DIR` не видаляється: розпаковані пакети перевикористовуються після перезапуску. У dev-стеку `BLOB_ROOTS` містить каталоги RAW і транзитних blob сервісу Storage, змонтовані лише для читання.

## Стан

| Змінна | Тип | Типово | Вплив |
|---|---|---|---|
| `JANE_HANDLER_RUNTIME_STATE_DSN` | секрет, DSN PostgreSQL | — | спільний стан кількох екземплярів; без нього — пам'ять |
| `JANE_HANDLER_RUNTIME_STATE_SCHEMA` | `^[a-z_][a-z0-9_]{0,62}$` | `jane_handler_runtime` | схема таблиць стану (створюється, якщо її немає) |

Стан у пам'яті підходить лише для одного екземпляра й CLI: після перезапуску ключі ідемпотентності, job і результати зникають.

## Ліміти

Ліміти розв'язуються шарами, кожен наступний перекриває попередній:

1. типові значення з коду;
2. файл платформи `JANE_HANDLER_RUNTIME_LIMITS_FILE` — документ `PlatformLimits`, наприклад [профіль](../../../deploy/profiles/README.md) `deploy/profiles/<профіль>.json`; ліміти інших сервісів ігноруються, помилки в назвах зупиняють запуск;
3. змінні `JANE_HANDLER_RUNTIME_LIMITS__<ГРУПА>__<ПОЛЕ>`, наприклад `JANE_HANDLER_RUNTIME_LIMITS__SANDBOX__MEMORY_MB=256`;
4. `limits` у запиті `handler.v1` — лише групи `sandbox` і `timeouts`.

Значення вище жорсткої стелі (`hard_caps`) зменшуються до стелі: запит не може підняти ліміт понад неї. Стелі задаються у файлі платформи або змінними `JANE_HANDLER_RUNTIME_LIMITS__HARD_CAPS__<ГРУПА>__<ПОЛЕ>`; поле, задане так, замінює типову стелю сервісу. Ефективні типові значення й стелі показує `GET /v1/info` у полі `limits`, а журнал запуску — запис `configured limits`. Загальні правила успадкування — [конфігурація jane-kit](../jane-kit/configuration.md).

### Пісочниця

| Ліміт | Типово | Стеля | З запиту | Вплив |
|---|---|---|---|---|
| `sandbox.cpu_cores` | `1.0` | `4.0` | так | частка CPU контейнера |
| `sandbox.memory_mb` | `512` | `4096` | так | пам'ять без swap; перевищення — `resource_exceeded` |
| `sandbox.wall_time_ms` | `30000` | `600000` | так | час від старту контейнера; перевищення — `timeout` |
| `sandbox.max_output_bytes` | `4194304` | `67108864` | так | обсяг stdout і stderr; більший stdout — `resource_exceeded` |
| `sandbox.max_processes` | `16` | `256` | так | `pids_limit` контейнера |
| `sandbox.tmpfs_mb` | `64` | `1024` | так | розмір `/tmp`; `0` — без `tmpfs` |

`wall_time_ms` рахується від запуску контейнера, тому включає старт інтерпретатора. На Docker Desktop (Windows) простий виклик триває 2–6 с; із `wall_time_ms=3000` у перевірочному запуску тайм-аутом завершилися навіть успішні виклики. Не встановлюйте менше 10 000 мс на Docker Desktop.

### Тайм-аути, паралельність і job

| Ліміт | Типово | Стеля | З запиту | Вплив |
|---|---|---|---|---|
| `timeouts.invocation_timeout_ms` | `60000` | `900000` | так | загальний час виклику бекенда, разом із створенням контейнера |
| `timeouts.sync_response_max_ms` | `25000` | — | так | скільки `sync`-запит чекає до відповіді 202 |
| `timeouts.request_timeout_ms` | `30000` | — | ні | Registry і повне завантаження `download_url` |
| `concurrency.max_parallel_invocations` | `2` | — | ні | контейнерів одночасно в одному екземплярі |
| `jobs.max_concurrent_jobs` | `4` | — | ні | job одночасно; решта в `queued` |
| `jobs.max_queued_jobs` | `1000` | — | ні | понад це — 503 `service_unavailable` |
| `jobs.job_timeout_ms` | `3600000` | — | ні | граничний час job; перевищення — job `failed` |
| `jobs.job_retention_seconds` | `86400` | — | ні | скільки зберігаються завершені job |
| `jobs.queue_full_retry_after_seconds` | `1` | — | ні | `Retry-After` за повної черги |
| `idempotency.idempotency_ttl_seconds` | `86400` | — | ні | скільки пам'ятається ключ і результат у PostgreSQL |
| `idempotency.in_memory_max_entries` | `10000` | — | ні | ключів у пам'яті, старші витісняються |

Виклик проходить два обмеження: job чекає слота `jobs.max_concurrent_jobs`, а запуск контейнера — слота `concurrency.max_parallel_invocations`.

### Пакети й вхідні дані

| Ліміт | Типово | Вплив |
|---|---|---|
| `packages.max_archive_bytes` | `52428800` | розмір архіву пакета |
| `packages.max_unpacked_bytes` | `209715200` | сумарний розмір розпакованих файлів |
| `packages.max_files` | `5000` | кількість файлів в архіві |
| `packages.cache_max_entries` | `64` | розпакованих пакетів у кеші, найстаріші видаляються |
| `packages.max_input_bytes` | `67108864` | вміст одного вхідного матеріалу |
| `packages.max_stored_results` | `10000` | результатів для `GET /v1/invocations/{id}` у пам'яті |
| `packages.docker_api_timeout_ms` | `60000` | тайм-аут одного виклику Docker API |
| `packages.max_stderr_in_result_bytes` | `16000` | хвіст stderr у `diagnostics.logs_ref`; `0` — без нього |
| `packages.unavailable_retry_after_seconds` | `5` | `Retry-After` відповіді 503 за недоступного рушія |
| `packages.kill_grace_ms` | `2000` | запас для `timeout -s KILL` усередині контейнера |

### Спільний стан

| Ліміт | Типово | Вплив |
|---|---|---|
| `state.pool_max_size` | `10` | з'єднань із PostgreSQL |
| `state.connect_timeout_ms` | `10000` | тайм-аут підключення |
| `state.in_progress_lease_ms` | `900000` | через скільки інший екземпляр перебирає ключ ідемпотентності, що «завис» у виконанні |
| `state.job_lease_ms` | `30000` | job без продовження lease позначається `failed` під час читання |
| `state.heartbeat_interval_ms` | `5000` | як часто екземпляр продовжує свої lease |

## Параметри CLI

`run` і `test` беруть налаштування з тих самих змінних середовища; три параметри їх перекривають:

| Параметр | Що перекриває |
|---|---|
| `--backend docker` або `--backend subprocess` | `SANDBOX_BACKEND` |
| `--unsafe-no-sandbox` | `ALLOW_UNSAFE_SUBPROCESS=true` |
| `--image <тег>` | образ для всіх профілів |

Інші параметри `run`: `--media-type`, `--url`, `--source-id`, `--material` (файл — документ `Material` у JSON), `--params` (JSON-об'єкт або `@файл.json`), `--no-test-mode`, `-o`. Параметри `test`: `--case <назва>` (можна повторювати), `--json` (звіт `TestReport`), `-o`. `build-image` приймає `--profile` і `--tag`; без `--tag` бере тег із `PROFILE_IMAGES`.

## Як застосовуються зміни

| Що змінено | Коли діє |
|---|---|
| змінні середовища, файл лімітів | після перезапуску процесу |
| `limits` у запиті | для цього запиту |
| образ під тим самим тегом | з наступного виклику: контейнер створюється за тегом щоразу |
| профіль у `python-extractor-1.json` | після нового збирання образу й перезапуску сервісу |
