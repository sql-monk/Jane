# Handler Runtime: експлуатація

Сторінка описує спостереження за Handler Runtime, оновлення образів і сервісу, роботу кількох екземплярів, власність даних і типові проблеми.

## Зміст

- [Моніторинг](#моніторинг)
- [Перевірка ізоляції](#перевірка-ізоляції)
- [Оновлення](#оновлення)
- [Міграції, резервування й відновлення](#міграції-резервування-й-відновлення)
- [Масштабування](#масштабування)
- [Власність даних](#власність-даних)
- [Типові проблеми](#типові-проблеми)

## Моніторинг

### Health

`GET /v1/health` має дві критичні перевірки, кожна обмежена `HEALTH_CHECK_TIMEOUT_MS`:

| Перевірка | Що перевіряє | `down`, коли |
|---|---|---|
| `sandbox` | `ping` контейнерного рушія; для `subprocess` — дозвіл бекенда | рушій недоступний або `subprocess` не дозволено |
| `state` | з'єднання з PostgreSQL; для пам'яті — завжди `ok` | база недоступна |

Будь-яка перевірка `down` — HTTP 503 і `"status": "down"`. Наявність образу профілю health не перевіряє: відсутній образ проявиться лише на першому виклику (503).

`GET /v1/info` показує версію, бекенд пісочниці, профілі з бібліотеками, джерела пакетів, режим стану й ефективні ліміти.

### Метрики

`/metrics` у форматі Prometheus — стандартні HTTP-метрики jane-kit: `jane_http_requests_total{method,route,status}`, `jane_http_request_duration_seconds`, `jane_http_requests_in_flight`, `jane_service_info`. Власних метрик пісочниці (тривалість, статуси `HandlerResult`) сервіс не публікує: використовуйте журнал `invocation finished` і `diagnostics.metrics` у результатах. Уривок `/metrics` після кількох викликів:

```text
jane_http_requests_total{method="POST",route="/v1/invocations",status="200"} 3.0
jane_http_requests_total{method="GET",route="/v1/invocations/{invocation_id}",status="200"} 1.0
jane_http_requests_total{method="POST",route="/v1/invocations",status="202"} 1.0
jane_http_requests_total{method="POST",route="/v1/invocations",status="422"} 2.0
```

### Журнали

Журнал — JSON (типово) або текст (`LOG_FORMAT=console`), у кожному записі `service` і `instance`. Записи сервісу:

| Повідомлення | Коли | Поля |
|---|---|---|
| `configured limits` | старт | ефективні ліміти й їхнє походження, `backend`, `images`, `state` |
| `invocation finished` | кожен виклик пісочниці | `invocation_id`, `package`, `status`, `failure`, `duration_ms`, `backend` |
| `job cancelled` | скасування | `job_id`, `invocation_id`, `killed` |
| `could not remove sandbox container` | контейнер не видалено | `container`, `error` |
| `state heartbeat failed` | не вдалося продовжити lease у PostgreSQL | виняток |

Вихід коду пакета (`print`, журнали Python) у журнал сервісу не потрапляє: його хвіст — у `diagnostics.logs_ref` результату.

## Перевірка ізоляції

Автоматичні тести ізоляції (`services/handler-runtime/tests/test_isolation.py`) працюють лише на Linux і запускаються в CI:

```powershell
just isolation
```

Перевірочний прогін на Windows 11 і Docker Desktop 29.8 (ревізія `c59d26d`) — тестовий пакет `wp06.sandbox-probe` з режимами в `params`, `memory_mb=64`, `wall_time_ms=15000`; `page.html` — будь-яка HTML-сторінка:

```powershell
$env:JANE_HANDLER_RUNTIME_LIMITS__SANDBOX__WALL_TIME_MS = "15000"
$env:JANE_HANDLER_RUNTIME_LIMITS__SANDBOX__MEMORY_MB = "64"
uv run --package jane-handler-runtime jane-handler-runtime run services/handler-runtime/tests/packages/probe page.html --params '{"mode":"hang"}' -o hang.json
```

| Режим пакета | `status` | `failure.kind` | Подробиці з результату |
|---|---|---|---|
| `hang` — нескінченний цикл | `failed` | `timeout` | контейнер убито, `duration_ms` 17812 |
| `memory` — 200 МБ при ліміті 64 | `failed` | `resource_exceeded` | `exit_code` 137, `evidence: oom_killed` |
| `network` — з'єднання з `1.1.1.1:443` | `failed` | `sandbox_violation` | `Network is unreachable`, події `socket.getaddrinfo`, `socket.connect` |
| `raise` — виняток | `failed` | `execution_error` | `RuntimeError: probe failure`, `stage: extract` |
| `bad_entity` — поле `null` | `failed` | `schema_mismatch` | `null is not allowed; omit the field or list it in 'cleared'` |
| `environment` — огляд середовища | `success` | — | `uid` 65534, лише `lo`, запис дозволено тільки в `/tmp` |

Той самий прогін із `wall_time_ms=3000` завершив тайм-аутом усі шість випадків, зокрема ті, що встигли вивести результат: на Docker Desktop старт контейнера й Python забирає 2–6 с ([configuration.md](configuration.md#пісочниця)).

## Оновлення

| Що оновлюється | Дії |
|---|---|
| образ профілю (виправлення бібліотеки, базового образу) | змініть `requirements.txt` і `python-extractor-1.json` разом, `jane-handler-runtime build-image`, опублікуйте образ; нові виклики беруть образ за тегом без перезапуску |
| SDK | SDK копіюється в образ під час збирання — новий образ, як вище; протокол раннера має версію (`PROTOCOL_VERSION = 1`) і має збігатися в runtime і образі |
| сервіс | новий образ сервісу (`services/handler-runtime/Dockerfile`), перезапуск; міграції стану — автоматично |
| ліміти | файл платформи або змінні, перезапуск |

Зміна набору бібліотек чи їхніх версій змінює поведінку вже опублікованих пакетів. Несумісні зміни оформлюйте новим профілем (`python-extractor@2`) з окремим образом, а не перезбиранням `@1`. У продакшні закріплюйте образ дайджестом у `PROFILE_IMAGES`.

## Міграції, резервування й відновлення

- **Міграції.** Під час запуску сервіс створює схему й таблиці (`idempotency`, `jobs`, `results`) або додає колонки в наявні — під advisory-lock, безпечно для одночасного старту кількох екземплярів. Окремої команди міграції немає.
- **Резервування.** Стан тимчасовий: ключі й результати живуть `idempotency_ttl_seconds`, job — `job_retention_seconds`. Резервувати його не обов'язково. Втрата стану означає, що повторна доставка в межах TTL знову запустить пісочницю; бізнес-даних сервіс не має, тому дублів записів це не створює.
- **Збій екземпляра.** Job зниклого екземпляра, який перестав продовжувати lease (`state.job_lease_ms`), позначається `failed` під час читання; викликач вирішує, чи повторювати етап (Orchestrator має власні правила повторів). Ключ ідемпотентності в стані «виконується» інший екземпляр перебирає через `state.in_progress_lease_ms`.
- **Залишки після аварійної зупинки.** Контейнери пісочниці, які не встигли видалитися, мають мітку `io.jane.handler-runtime.sandbox=1`; тимчасовий кеш пакетів — каталог `jane-packages-*` у тимчасовій теці. Перед видаленням контейнерів переконайтеся, що сервіс зупинено, бо команда знищує й виклики, що виконуються:

  ```powershell
  docker ps -a --filter label=io.jane.handler-runtime.sandbox=1 --format "{{.Names}} {{.Status}} {{.CreatedAt}}"
  ```

  Щоб відібрати контейнери одного стека, задайте йому власну мітку через `SANDBOX_LABELS` і фільтруйте за нею.

## Масштабування

- **Кілька екземплярів** — лише зі спільним `STATE_DSN`; без нього повторна доставка на інший екземпляр знову виконає пакет, а `GET /v1/jobs/{job_id}` не знайде job іншого екземпляра.
- **Паралельність** — `concurrency.max_parallel_invocations` контейнерів на екземпляр; пам'ять вузла має вміщати `max_parallel_invocations × memory_mb` плюс сам сервіс.
- **Рушій** — екземпляри можуть ділити один рушій; скасування зупиняє контейнер виклику за міткою незалежно від того, який екземпляр його створив.
- **Кеш пакетів** — локальний для кожного екземпляра; спільний каталог `PACKAGE_CACHE_DIR` між екземплярами не потрібен.

Профілі лімітів платформи для різних середовищ — [deploy/profiles](../../../deploy/profiles/README.md).

## Власність даних

| Дані | Власник | Де |
|---|---|---|
| ключі ідемпотентності, job, результати викликів | Handler Runtime | пам'ять або схема `jane_handler_runtime` |
| кеш розпакованих пакетів | Handler Runtime | `PACKAGE_CACHE_DIR` або тимчасовий каталог |
| пакети й версії | Registry | читаються через `registry.v1` |
| RAW і сутності | Storage | RAW читається лише через `BLOB_ROOTS` або `download_url` |

Інші сервіси не читають таблиці Handler Runtime, а він — чужі таблиці. Загальна карта — [власність даних](../../architecture/data-ownership.md).

## Типові проблеми

| Симптом | Причина | Що зробити |
|---|---|---|
| 503 `sandbox image '…' not found` | образу профілю немає на рушії | `jane-handler-runtime build-image` або `docker pull` образу з `PROFILE_IMAGES` |
| 503 `container engine is not reachable`, health `sandbox: down` | Docker не запущено, немає доступу до сокета | запустіть рушій; у контейнері — змонтуйте сокет і додайте групу (`JANE_DOCKER_GID`) |
| 503 `subprocess backend is disabled` | `SANDBOX_BACKEND=subprocess` без дозволу | `ALLOW_UNSAFE_SUBPROCESS=true` або `--unsafe-no-sandbox` — лише для довірених пакетів |
| усі виклики `failed: timeout`, хоча код швидкий | `wall_time_ms` менший за час старту контейнера | збільште `sandbox.wall_time_ms` (на Docker Desktop — від 10 000) |
| `failed: resource_exceeded` з `evidence: sigkill` | процес убито під лімітом пам'яті | збільште `sandbox.memory_mb` у запиті чи конфігурації в межах стелі |
| `failed: execution_error` з `exit_code`, без `stage` | раннер не вивів результат: вичерпано `max_processes`, аварія інтерпретатора | перегляньте `diagnostics.logs_ref`; перевірте, чи пакет не створює процеси |
| `failed: sandbox_violation` | код пакета звертається до мережі чи запускає процеси | приберіть мережу з пакета: дані мають надходити у вхідних даних |
| 422 `dependency_not_allowed` | бібліотеки немає в профілі або версія не підходить | використовуйте бібліотеки з `jane-handler-runtime profile` |
| 422 `validation_failed`: `file:// content is disabled` | `BLOB_ROOTS` порожній | додайте каталог у `BLOB_ROOTS` або передайте вміст inline |
| 409 `idempotency_in_progress` | той самий ключ ще виконується | повторіть пізніше з тим самим ключем |
| попередження `Duplicate Operation ID cancelJob` під час старту | сервіс замінює типове скасування job власним | не впливає на роботу |
