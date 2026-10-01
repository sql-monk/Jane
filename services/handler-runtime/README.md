# Handler Runtime

Виконує Python-пакети обробників (`kind: extractor` і `transform` з `entry.runtime: python`) за спільним
протоколом обробника в пісочниці ([ADR-0003](../../docs/adr/0003-python-sandbox.md)): **окремий контейнер на
кожен виклик**, мережа вимкнена, root FS лише для читання, ліміти часу/пам'яті/CPU/процесів, без секретів,
примусова зупинка при зависанні. Повертає `HandlerResult` з чотирма станами ТЗ §9.

Контракт: [`contracts/openapi/handler.v1.yaml`](../../contracts/openapi/handler.v1.yaml) (схеми
`handler-invocation`, `handler-result`, `package-manifest`). SDK для авторів екстракторів —
[`libs/extractor-sdk`](../../libs/extractor-sdk/README.md). Працює без оркестратора, репозиторію й сховищ.

## Як це працює

1. **Пакет**: `package_archive` (ContentRef: inline base64 zip, `file://` у дозволених теках або `download_url`)
   або репозиторій (`GET /v1/packages/{id}/versions/{v}/archive`, якщо задано `JANE_HANDLER_RUNTIME_REGISTRY_URL`).
   Перевіряються `handler.digest` (`sha256:` байтів архіву), `ContentRef.sha256`/`size_bytes`, `ETag` репозиторію;
   архів розпаковується з перевіркою шляхів (`..`, абсолютні, симлінки), кількості файлів і розміру; кеш — за дайджестом.
2. **Перевірки до запуску** (HTTP-помилки, виклик не відбувся): маніфест за схемою, `kind`/`entry`, `access.network`
   (дозволено лише `none`), профіль runtime і `dependencies.python` (422 `dependency_not_allowed`), `params` за
   `params_schema` (типові значення застосовуються), `input.accepts`/`media_types`, вміст входів (sha256, розмір).
3. **Пісочниця**: робоча тека (`request.json`, `package/…`, `inputs/<n>`) копіюється в анонімний том `/work`
   (власник root, права лише читання), запускається `python -I -m jane_extractor_sdk.runner /work` у образі профілю.
4. **Результат**: вихід раннера перевіряється — сутності мають бути оголошені в `output.entities`, `fields` — за
   схемою сутності пакета, без `null`, з ключем (`key` будується з `key_fields`, scope — `source.source_id` або
   `local`); додаються `observation`, `provenance`, `schema`; увесь запис — за `entity.schema.json`.

| Ситуація | Результат |
|---|---|
| екстрактор повернув `success` / `empty` / `unrecognized` | той самий `status` |
| виняток у коді, невалідний результат | `failed`, `failure.kind = execution_error` (traceback у `failure.details`) |
| поля не відповідають схемі, `null`, неоголошений тип | `failed`, `schema_mismatch`, `diagnostics.validation_errors` |
| перевищено `wall_time_ms` | контейнер убито (`docker kill`), `failed`, `timeout` |
| перевищено `memory_mb` (OOM) або `max_output_bytes` | `failed`, `resource_exceeded` |
| спроба мережі / запуску процесу (аудит-хук раннера) | `failed`, `sandbox_violation`, повідомлення `sandbox.network_blocked` |

Мережу блокує не хук, а сама пісочниця (`network_mode=none`: у контейнері лише `lo`); хук лише фіксує спробу для
діагностики. stdout/stderr коду (обрізані до `max_output_bytes`) — у `diagnostics.logs_ref` (inline).

## Профіль runtime `python-extractor@1`

Образ: [`sandbox/python-extractor-1/Dockerfile`](sandbox/python-extractor-1/Dockerfile) (база
`python:3.12.12-slim-bookworm`), точні версії — [`requirements.txt`](sandbox/python-extractor-1/requirements.txt),
машиночитний опис — [`src/jane_handler_runtime/profiles/python-extractor-1.json`](src/jane_handler_runtime/profiles/python-extractor-1.json)
(його ж віддають `GET /v1/info` → `capabilities.runtime_profiles` і `jane-handler-runtime profile --json`).
Встановлення пакетів під час виконання немає. Цей перелік має використовувати репозиторій (WP-05) для
перевірки `dependencies.python` (`dependency_not_allowed`): вимога PEP 508 задоволена, якщо бібліотека є в
профілі й її версія входить у специфікатор; маркери оцінюються для Linux/CPython 3.12; URL-вимоги заборонені.

| Бібліотека | Версія | | Бібліотека | Версія |
|---|---|---|---|---|
| beautifulsoup4 | 4.15.0 | | python-dateutil | 2.9.0.post0 |
| cssselect | 1.5.0 | | regex | 2026.9.10 |
| html5lib | 1.1 | | selectolax | 0.3.34 |
| jmespath | 1.1.0 | | six | 1.17.0 |
| jsonpath-ng | 1.8.0 | | soupsieve | 2.10 |
| lxml | 6.1.3 | | typing-extensions | 4.16.0 |
| parsel | 1.12.0 | | w3lib | 2.4.1 |
| jane-extractor-sdk | 0.1.0 | | webencodings | 0.6.1 |

Плюс стандартна бібліотека Python 3.12. Збірка образу (контекст — лише потрібні файли, не весь репозиторій):

```
uv run --package jane-handler-runtime jane-handler-runtime build-image            # тег jane/python-extractor:1
uv run --package jane-handler-runtime jane-handler-runtime build-image --tag my/python-extractor:1
```

У проді закріплюйте образ за дайджестом: `JANE_HANDLER_RUNTIME_PROFILE_IMAGES='{"python-extractor@1":"registry/…@sha256:…"}'`.

## CLI: пакет на локальному файлі без інших сервісів

```
uv sync --all-packages
uv run --package jane-handler-runtime jane-handler-runtime build-image
uv run --package jane-handler-runtime jane-handler-runtime test libs/extractor-sdk/examples/testsite-product-extractor
uv run --package jane-handler-runtime jane-handler-runtime run libs/extractor-sdk/examples/testsite-product-extractor page.html --media-type text/html --url https://shop.test/product/x --params '{"include_url": false}'
uv run --package jane-handler-runtime jane-handler-runtime profile
```

`run` друкує `HandlerResult` (код виходу 0 — `success`/`empty`, 1 — `unrecognized`/`failed`, 2 — виклик
неможливий: невалідний пакет, параметри, немає пісочниці); `test` друкує таблицю (або `--json` — `TestReport`),
код 0 — усі тести пройшли. `--image` — інший образ, `--backend subprocess --unsafe-no-sandbox` — **без ізоляції**,
лише для власного довіреного коду. Поза checkout репозиторію задайте `JANE_HANDLER_RUNTIME_CONTRACTS_DIR`
(теки `contracts/schemas` і `contracts/openapi`).

## Незалежний запуск сервісу

Потрібен контейнерний рушій (Docker Engine / Docker Desktop з Linux-контейнерами / Podman з Docker API).

```
uv run --package jane-handler-runtime jane-handler-runtime serve        # 127.0.0.1:8000
curl http://127.0.0.1:8000/v1/health                                     # checks.sandbox = ok, якщо рушій доступний
```

У Docker (контекст — корінь репозиторію). Сервісу потрібен доступ до Docker API; у проді — через socket-proxy
з мінімальними правами або rootless Podman / окремий вузол (ADR-0003):

```
docker build -f services/handler-runtime/Dockerfile -t jane-handler-runtime .
docker run -d -p 8106:8000 -v /var/run/docker.sock:/var/run/docker.sock --group-add <gid сокета> \
  -e 'JANE_HANDLER_RUNTIME_PROFILE_IMAGES={"python-extractor@1":"jane/python-extractor:1"}' jane-handler-runtime
```

Робоча тека передається в пісочницю через Docker API (`put_archive`), не через bind-mount, тож сервіс однаково
працює з локальним, віддаленим (`DOCKER_HOST`) чи контейнеризованим рушієм.

### Кілька екземплярів

Кожен виклик — окремий контейнер, тож екземпляри незалежні у виконанні. Спільний стан — ключі ідемпотентності
(`Idempotency-Key` = `delivery_key`), job і результати `GET /v1/invocations/{id}` — зберігається у **власній БД
сервісу** (PostgreSQL, схема `jane_handler_runtime`, `contracts/docs/data-ownership.md`):

```
JANE_HANDLER_RUNTIME_STATE_DSN=postgresql://user:pass@host:5432/jane_handler_runtime   # з середовища, не в коді
JANE_HANDLER_RUNTIME_STATE_SCHEMA=jane_handler_runtime                                   # типово; таблиці створюються самі
```

Тоді повтор доставки на будь-якому екземплярі (і після рестарту) повертає збережений результат (`duplicate: true`,
`Idempotency-Replayed: true`) без повторного запуску пісочниці; job і результати читаються з будь-якого
екземпляра; виклик, що ще виконується на іншому екземплярі, — 409 `idempotency_in_progress` (`retryable: true`);
незавершене «захоплення» ключа впалим екземпляром звільняється через `state.in_progress_lease_ms`. Ключі
пам'ятаються `transfer.idempotency_ttl_seconds`, job — `transfer.job_retention_seconds`.

Без `STATE_DSN` стан у пам'яті процесу (`InMemory*` jane-kit) — **лише для одного автономного екземпляра й CLI**:
після рестарту ключі втрачаються, між екземплярами не видно. `GET /v1/info` → `capabilities.state`
(`memory` | `postgresql`), `GET /v1/health` → `checks.state`.

`POST /v1/jobs/{id}/cancel` з будь-якого екземпляра переводить job у `cancelling` і вбиває контейнер пісочниці
за міткою `io.jane.invocation-id` (на тому ж рушії); екземпляр-власник завершує job як `cancelled`.

## API

| Операція | Поведінка |
|---|---|
| `POST /v1/invocations` | `Idempotency-Key` обов'язковий і дорівнює `delivery.delivery_key`. `mode: sync` — 200 з `HandlerResult` або 202 + Job, якщо не вклалося в `timeouts.sync_response_max_ms`; `mode: async` — 202 + Job. Повтор із тим самим ключем і тілом — збережений результат з `duplicate: true` і `Idempotency-Replayed: true`, без повторного запуску; інше тіло — 422 `idempotency_key_reused` |
| `GET /v1/invocations/{id}` | збережений результат (у межах `packages.max_stored_results`) |
| `POST /v1/test-runs` | 202 + Job; `Job.result` — `TestReport`. Тести маніфесту (`all` / `none` / імена) + `extra_cases`, кожен випадок — окремий запуск у `test_mode` (жодного запису: runtime нічого не зберігає) |
| `GET /v1/jobs/{id}` | jane-kit (зі спільного сховища, якщо задано `STATE_DSN`) |
| `POST /v1/jobs/{id}/cancel` | 202 — скасування прийнято, контейнер пісочниці вбито; 200 — job уже завершено |
| `GET /v1/connections` | 200 `{"items": [], "next_cursor": null}` — виконавець без підключень (`capabilities.connections: false`) |
| `PUT /v1/connections/{id}` | 501 `not_implemented` (екстрактори не отримують облікових даних) |
| `GET`/`DELETE /v1/connections/{id}`, `POST …/test` | 404 `not_found` |
| `GET /v1/health`, `/v1/info`, `/metrics` | `checks.sandbox` — пінг рушія, `checks.state` — сховище стану; `capabilities` — типи, профілі, backend, state |

## Тести

```
just test handler-runtime                                   # unit + contract (backend subprocess, без Docker)
uv run pytest services/handler-runtime -m isolation         # ізоляція на справжньому Docker (Windows/Linux)
just isolation                                              # те саме в CI (Linux)
just up --project jane-wp06-state postgres                  # кілька екземплярів на спільному PostgreSQL:
just integration --project jane-wp06-state services/handler-runtime
just down -v --project jane-wp06-state
```

`tests/test_state.py` (`integration`): два екземпляри на спільній схемі — повтор на іншому дає `duplicate: true`
і той самий `invocation_id` без другого запуску пісочниці; job/invocation читаються з іншого екземпляра й після
«рестарту» (новий застосунок); виконання на іншому екземплярі — 409; скасування з іншого екземпляра.

Тести ізоляції (`tests/test_isolation.py`, без моків пісочниці): зависання вбивається за `wall_time_ms`;
сервер, досяжний зі звичайного контейнера, недосяжний з пісочниці (ENETUNREACH, лише `lo`); OOM за `memory_mb`;
FS лише для читання, користувач 65534, відсутність змінних `JANE_*`; тести прикладного пакета через CLI;
версії бібліотек в образі = профіль. Образ тестів — `JANE_WP06_SANDBOX_IMAGE` (типово
`jane-wp06/python-extractor:1-test`, збирається автоматично); контейнери мають мітку сесії й прибираються.

## Конфігурація

Змінні з префіксом `JANE_HANDLER_RUNTIME_` (плюс загальні `HOST`, `PORT`, `LOG_LEVEL`, `LOG_FORMAT`,
`METRICS_ENABLED`, `HEALTH_CHECK_TIMEOUT_MS`, `AUTH_MODE`, `LIMITS_FILE` з шаблону):

| Змінна | Типово | Опис |
|---|---|---|
| `SANDBOX_BACKEND` | `docker` | `docker` або `subprocess` (без ізоляції) |
| `ALLOW_UNSAFE_SUBPROCESS` | `false` | без `true` backend `subprocess` відмовляє (503) |
| `DOCKER_HOST` | — | адреса Docker/Podman API (інакше `DOCKER_HOST` середовища / стандартний сокет чи named pipe) |
| `DOCKER_RUNTIME` | — | OCI runtime пісочниці, напр. `runsc` (gVisor) |
| `SANDBOX_USER` | `65534:65534` | користувач у контейнері (не root) |
| `SANDBOX_LABELS` | `{}` | додаткові мітки контейнерів (JSON) |
| `PROFILE_IMAGES` | `{"python-extractor@1": "jane/python-extractor:1"}` | профіль → образ (JSON) |
| `REGISTRY_URL` / `REGISTRY_TOKEN` | — | репозиторій пакетів і bearer-токен (лише з середовища) |
| `PACKAGE_CACHE_DIR` | тимчасова тека | кеш перевірених пакетів за дайджестом |
| `BLOB_ROOTS` | `[]` | теки, з яких дозволено читати `file://` (JSON-масив); порожньо — `file://` заборонено |
| `STATE_DSN` | — (стан у пам'яті) | PostgreSQL для спільного стану кількох екземплярів (секрет — лише з середовища) |
| `STATE_SCHEMA` | `jane_handler_runtime` | схема таблиць стану |
| `CONTRACTS_DIR` | пошук угору від пакета (`JANE_CONTRACTS_DIR`) | `contracts/` зі схемами; в образі — `/app/contracts` |

## Ліміти

Рівні: типові значення → стелі сервісу (`DEFAULT_HARD_CAPS`) → файл платформи (`LIMITS_FILE`, форма
`PlatformLimits`; можна дати цілий профіль `deploy/profiles/<профіль>.json` — ліміти контракту, яких runtime не
має, ігноруються й перелічуються в журналі старту, опечатка чи некоректне значення — помилка старту; див. README
jane-kit) → `JANE_HANDLER_RUNTIME_LIMITS__<ГРУПА>__<ПАРАМЕТР>` → `limits` запиту (групи `sandbox`,
`timeouts`; решта груп ігнорується). Застосовується `min(запит, hard_caps)`; стеля платформи для поля замінює
стелю сервісу. `GET /v1/info` → `limits` показує типові значення й стелі (лише поля контракту).

| Параметр | Типово | Стеля сервісу | Опис |
|---|---|---|---|
| `sandbox.cpu_cores` | 1.0 | 4.0 | `nano_cpus` контейнера |
| `sandbox.memory_mb` | 512 | 4096 | пам'ять (swap вимкнено: memswap = memory) |
| `sandbox.wall_time_ms` | 30000 | 600000 | після — `docker kill`, `failed`/`timeout` |
| `sandbox.max_output_bytes` | 4194304 | 67108864 | stdout (результат) і stderr (журнал) |
| `sandbox.max_processes` | 16 | 256 | `pids_limit` |
| `sandbox.tmpfs_mb` | 64 | 1024 | `/tmp` (tmpfs, `noexec`); 0 — без `/tmp` |
| `timeouts.invocation_timeout_ms` | 60000 | 900000 | весь виклик пісочниці |
| `timeouts.sync_response_max_ms` | 25000 | — | далі sync-виклик стає 202 + Job |
| `timeouts.request_timeout_ms` | 30000 | — | репозиторій і `download_url` |
| `concurrency.max_parallel_invocations` | 2 | — | одночасні пісочниці в екземплярі |
| `packages.max_archive_bytes` | 52428800 | — | розмір zip пакета |
| `packages.max_unpacked_bytes` | 209715200 | — | розмір після розпакування |
| `packages.max_files` | 5000 | — | файлів в архіві |
| `packages.cache_max_entries` | 64 | — | пакетів у кеші |
| `packages.max_input_bytes` | 67108864 | — | вміст одного матеріалу |
| `packages.max_stored_results` | 10000 | — | результати для `GET /v1/invocations/{id}` |
| `packages.docker_api_timeout_ms` | 60000 | — | виклики Docker API |
| `packages.kill_grace_ms` | 2000 | — | `timeout -s KILL` у контейнері спрацьовує через `wall_time_ms` + це (якщо сам runtime упав) |
| `packages.max_stderr_in_result_bytes` | 16000 | — | хвіст stderr у `diagnostics.logs_ref` (0 — не додавати) |
| `packages.unavailable_retry_after_seconds` | 5 | — | `Retry-After` відповіді 503, коли рушій недоступний |
| `state.pool_max_size` | 10 | — | з'єднань до PostgreSQL стану на екземпляр |
| `state.connect_timeout_ms` | 10000 | — | підключення до PostgreSQL стану |
| `state.in_progress_lease_ms` | 900000 | — | після цього «захоплення» ключа впалим екземпляром можна перехопити |
| `jobs.*`, `idempotency.*` | як у jane-kit | — | див. `libs/jane-kit/README.md` |

## Приклад виклику зі стороннього застосунку

```python
import base64, hashlib, httpx
from pathlib import Path
from jane_extractor_sdk.package import build_archive, material_from_file

archive = build_archive(Path("my-package"))
body = {
    "handler": {
        "package_id": "testsite.product-extractor",
        "version": "1.0.0",
        "digest": "sha256:" + hashlib.sha256(archive).hexdigest(),
    },
    "package_archive": {
        "kind": "inline",
        "media_type": "application/zip",
        "encoding": "base64",
        "data": base64.b64encode(archive).decode(),
    },
    "inputs": [
        {"kind": "material", "material": material_from_file(Path("page.html"), media_type="text/html")}
    ],
    "delivery": {"delivery_key": "my-app-0001"},
}
r = httpx.post(
    "http://127.0.0.1:8106/v1/invocations", json=body, headers={"Idempotency-Key": "my-app-0001"}, timeout=60
)
print(r.json()["status"], r.json()["output"])
```

## Спостережуваність

- Журнали — JSON із `trace_id`, `invocation_id`, пакетом, статусом, `failure`, тривалістю, backend.
- `GET /metrics` — HTTP-метрики jane-kit; `diagnostics.metrics` кожного результату — `duration_ms`, `cpu_ms`,
  `peak_memory_mb` (cgroup контейнера), `output_bytes`.
