# registry — репозиторій обробників Jane

Сервіс зберігання й розповсюдження пакетів обробників **усіх типів** (екстрактор, збереження, LLM,
перетворення) і **правил колекторів** (ТЗ §7, §13.2; рішення — [ADR-0002](../../docs/adr/0002-package-registry.md)).
Контракт — [`contracts/openapi/registry.v1.yaml`](../../contracts/openapi/registry.v1.yaml).

Що вміє:

- незмінні версії з дайджестом `sha256:` канонічного архіву (повтор версії — `409 version_exists`);
- валідація маніфесту за контрактною схемою, відповідність `kind ↔ entry`, наявність файлів, на які
  посилається маніфест, схеми сутностей, правила колектора (`collector-rules.schema.json`), обов'язкові
  тести для extractor/llm;
- залежності: `dependencies.python` — за описом профілю runtime (WP-06), `dependencies.packages` — лише
  наявні версії з тим самим дайджестом;
- відхилення секретів (`422 secret_detected`), походження (`provenance`), статуси версій з історією,
  звіти тестів, заборона автозмін пакета (`auto_changes_allowed=false` → LLM-версії `403 forbidden`);
- пошук (тип, текст, тег, тип сутності, медіатип, домен, форки пакета);
- форк (незалежна копія з `fork_of`), diff між версіями й від батька, стан відносно батька,
  **явне** перенесення змін батька новою версією (`upstream-ports`, трьохстороннє злиття, job);
- архів версії для автономного використання, CLI `export` / `verify` / `archive`.

Сам registry не залежить від інших сервісів Jane: лише власна БД PostgreSQL і blob-сховище (ADR-0009).

## Запуск

```text
# локально, без збереження між запусками (експерименти)
JANE_REGISTRY_DB=memory JANE_REGISTRY_BLOB=filesystem JANE_REGISTRY_BLOB_ROOT=./.registry-blobs \
  uv run --package jane-registry python -m jane_registry

# проти dev-стеку (PostgreSQL + MinIO): адреси й паролі — `just env --project <ім'я>`
just up --project jane-wp05 postgres minio
JANE_REGISTRY_DB_URL=postgresql://jane:<пароль>@127.0.0.1:<порт>/jane_registry \
JANE_REGISTRY_S3_ENDPOINT_URL=http://127.0.0.1:<порт minio> \
JANE_REGISTRY_S3_ACCESS_KEY=<ключ> JANE_REGISTRY_S3_SECRET_KEY=<секрет> \
JANE_REGISTRY_RUNTIME_PROFILES='["<шлях>/python-extractor-1.json"]' \
  uv run --package jane-registry python -m jane_registry
```

Базу `jane_registry` (окрема база й роль сервісу — [карта власності даних](../../contracts/docs/data-ownership.md))
створює оператор; таблиці й схема створюються сервісом під час старту (ідемпотентно, під advisory lock —
кілька екземплярів можуть стартувати одночасно). Бакет `jane-registry` створюється, якщо його немає
(`JANE_REGISTRY_S3_CREATE_BUCKET=true`).

Docker (контекст — корінь репозиторію; в образ копіюються контрактні схеми `contracts/schemas`):

```text
docker build -f services/registry/Dockerfile -t jane-registry .
docker run -d -p 127.0.0.1:8105:8000 --network <мережа стеку> \
  -e JANE_REGISTRY_DB_URL -e JANE_REGISTRY_S3_ENDPOINT_URL -e JANE_REGISTRY_S3_ACCESS_KEY \
  -e JANE_REGISTRY_S3_SECRET_KEY jane-registry
```

`/v1/health` перевіряє БД і blob-сховище (503, якщо недоступні — використовує `HEALTHCHECK` образу),
`/v1/info` — можливості й ліміти, `/metrics` — Prometheus (HTTP-метрики jane-kit і
`jane_registry_publications_total{result}`), журнали — JSON у stdout з `trace_id`.
Кілька екземплярів працюють на одній БД і одному бакеті: ключі ідемпотентності й job зберігаються в
PostgreSQL, публікації одного пакета серіалізуються блокуванням рядка пакета.

**Відновлення після падіння екземпляра.** Ключ `Idempotency-Key` запиту, що ще виконується, має lease
`recovery.in_progress_lease_ms` (типово 120 с): якщо екземпляр упав посеред запиту, після lease повтор із тим
самим ключем на будь-якому екземплярі виконується заново (до того — `409 idempotency_in_progress`, retryable).
Кожен незавершений job (`upstream_port`) має власника (екземпляр, унікальний на кожен запуск) і lease
`recovery.job_lease_ms` (60 с), який власник поновлює кожні `recovery.job_heartbeat_ms` (15 с). Job із
простроченим lease при читанні (і під час прибирання на старті) стає `failed` з
`service_unavailable` (`retryable: true`), `cancelling` → `cancelled`. Скасування з іншого екземпляра
перевіряється перед публікацією версії: скасований port нічого не публікує.

## Конфігурація

Змінні середовища з префіксом `JANE_REGISTRY_` (поля [`settings.py`](src/jane_registry/settings.py)).

| Змінна | Типово | Що |
|---|---|---|
| `PORT` / `HOST` | `8105` / `127.0.0.1` | адреса HTTP (в образі `0.0.0.0:8000`) |
| `DB` | `postgres` | `postgres` або `memory` (один процес, без збереження) |
| `DB_URL` | — | DSN власної БД `jane_registry` (секрет: лише середовище або secrets-файл) |
| `DB_SCHEMA` | `public` | схема таблиць |
| `BLOB` | `s3` | `s3` (MinIO/S3) або `filesystem` |
| `BLOB_BUCKET` / `BLOB_PREFIX` | `jane-registry` / `sha256/` | об'єкт архіву: `<bucket>/<prefix><hex дайджесту>` |
| `BLOB_ROOT` | — | для `filesystem`: тека, що грає роль бакета |
| `S3_ENDPOINT_URL`, `S3_REGION`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_CREATE_BUCKET` | —, `us-east-1`, —, —, `true` | підключення до MinIO/S3 |
| `RUNTIME_PROFILES` | `[]` | JSON-список файлів або URL з описом профілів runtime (див. нижче) |
| `CONTRACTS_DIR` | `contracts/` checkout або `/app/contracts` | де лежать контрактні схеми |
| `REQUIRE_TESTS` | `true` | extractor/llm мають щонайменше один тест `success` і один `empty`/`unrecognized` |
| `AUTH_MODE` | `none` | `none` / `api_key` / `jwt` — див. «Автентифікація (ADR-0005)» |
| `API_KEYS` / `API_KEYS_FILE` | — | для `api_key`: `[{"name", "sha256": "<hex ключа>" або "secret_ref": "env:…"\|"file:…", "scopes": [...], "actor": "human"\|"llm"\|"import"}]` (`actor` типово `human`; у `jwt` — claim `actor`) |
| `RUNTIME_PROFILES_TOKEN_REF` | — | `env:VAR` / `file:/path` власного токена registry для http(s)-джерел `RUNTIME_PROFILES` (`GET <runtime>/v1/info` потребує токена) |
| `LIMITS_FILE`, `LIMITS__<група>__<поле>` | — | ліміти (файл `PlatformLimits`, зокрема цілий профіль `deploy/profiles/<профіль>.json`, або змінні; див. «Ліміти й типові значення») |

Scopes (ADR-0005): `registry:read` — усі GET, зокрема `GET /v1/jobs/{id}`; `registry:write` — створення пакета,
публікація, PATCH, форк, звіти тестів, upstream-ports, `POST /v1/jobs/{id}/cancel`; `registry:approve` —
`POST …/status` і **дозвіл автозмін** (PATCH `auto_changes_allowed: false → true`; заборонити автозміни може
будь-хто з `registry:write`).

`actor` ключа визначає походження того, що створює клієнт: ключ асистента з `actor: "llm"` може публікувати лише
версії з `provenance.created_by: llm` (інакше `403`), тож заборона автозмін не обходиться підміною походження;
upstream-port записує `provenance.created_by` = `actor` того, хто його запустив (`requested_by` = ім'я ключа).
У `auth_mode=none` усі клієнти — `human`.

### Автентифікація (ADR-0005)

Режими й усі змінні (`AUTH_MODE`, `API_KEYS`, `API_KEYS_FILE`, `JWT_*`, `METRICS_PUBLIC`) спільні для всіх сервісів: [jane-kit, «Автентифікація»](../../libs/jane-kit/README.md#автентифікація-adr-0005) і [docs/operations](../../docs/operations/README.md#автентифікація-adr-0005). `/v1/health` (і `/metrics`, доки `METRICS_PUBLIC=true`) працюють без токена; `/v1/info` приймає будь-який дійсний токен; решта потребує токена (401 `unauthenticated`) і scope операції (403 `forbidden`). `AUTH_MODE=none` — лише для локальних тестів на loopback; за неповної конфігурації `api_key`/`jwt` сервіс не стартує. JWT з реальним IdP **не перевірено на реальному сервісі** (лише локальний JWKS у тестах jane-kit).

Scopes операцій (таблиця `REGISTRY` з `jane_kit.auth_scopes`, по суті та сама, що в абзаці «Scopes» вище):

- невідомий `actor` у ключі — сервіс не стартує, у JWT — 403;
- **увага, `jwt`:** `actor` береться з claim `actor` токена, а якщо claim немає — клієнт вважається `human`, як і
  ключ без поля `actor`. Сервісний JWT асистента без claim `actor: llm` **обходить** обмеження для `llm` (може
  публікувати версії з `provenance.created_by: human` і не підпадає під заборону автозмін через походження). У
  режимі `jwt` налаштуйте в IdP для клієнта асистента claim `actor` зі значенням `llm` (mapper/optional claim) або
  видайте асистенту ключ `api_key` з `"actor": "llm"`; код registry цього не перевіряє; `GET /v1/jobs/{id}` — `registry:read`, `POST /v1/jobs/{id}/cancel` — `registry:write`.

Приклад для `api_key` (зберігається лише хеш ключа):

```text
JANE_REGISTRY_AUTH_MODE=api_key
JANE_REGISTRY_API_KEYS=[{"name": "assistant", "sha256": "<sha256 hex ключа>", "scopes": ["registry:read", "registry:write", "registry:approve"], "actor": "llm"},
  {"name": "ops", "secret_ref": "file:/run/secrets/jane-ops-key", "scopes": ["registry:read", "registry:write", "registry:approve"]}]
```

### Профілі runtime

`dependencies.python` екстрактора перевіряється проти профілю `dependencies.runtime_profile`
(ADR-0002 §4) тими самими правилами, що й у handler-runtime (WP-06): вимога PEP 508, без прямих URL;
вимога з маркером, хибним для пісочниці (Linux, Python профілю), пропускається; інакше бібліотека має
бути в профілі, а її точна версія — задовольняти специфікатор. Профілі **не зашиті**: джерела —
`JANE_REGISTRY_RUNTIME_PROFILES` (файли або URL; документ профілю, їх список, `{"runtime_profiles": {...}}`
або `ServiceInfo` — тобто можна вказати `http://<handler-runtime>/v1/info`). Прочитані профілі
кешуються на `profiles.refresh_seconds`; якщо джерело недоступне й профілю немає — `502 upstream_unavailable`
(retryable); невідомий профіль — `422 dependency_not_allowed`.

## Ліміти й типові значення

Усі — з конфігурації (`JANE_REGISTRY_LIMITS__PACKAGES__MAX_FILES=500` тощо), `/v1/info` показує поля,
що є в контракті лімітів. `JANE_REGISTRY_LIMITS_FILE` може бути цілим профілем платформи
(`deploy/profiles/<профіль>.json`): з нього registry бере `transfer.max_request_body_bytes`,
`transfer.job_retention_seconds` і `transfer.idempotency_ttl_seconds`, решта лімітів контракту ігнорується й
перелічується в журналі старту; опечатка чи некоректне значення — помилка старту (див. README jane-kit).

| Параметр | Типово | Що |
|---|---|---|
| `packages.max_archive_bytes` | 20 MiB | розмір архіву (завантаженого чи канонічного) |
| `packages.max_unpacked_bytes` | 50 MiB | сума розмірів файлів пакета |
| `packages.max_files` | 2000 | файлів у пакеті |
| `packages.max_versions_per_package` | 1000 | версій одного пакета (`422 limit_exceeded`) |
| `packages.archive_cache_bytes` | 64 MiB | LRU архівів у пам'яті екземпляра |
| `requests.max_request_body_bytes` (= `transfer.max_request_body_bytes`) | 30 MiB | тіло запиту (`413 payload_too_large`) |
| `secrets.max_scan_bytes_per_file` / `scan_time_budget_ms` / `max_findings_per_file` / `min_entropy_token_length` / `entropy_threshold` | 2 MiB / 20000 / 20 / 32 / 4.3 | сканування секретів (завеликий файл або перевищення часу — `limit_exceeded`) |
| `recovery.in_progress_lease_ms` / `job_lease_ms` / `job_heartbeat_ms` | 120000 / 60000 / 15000 | відновлення після падіння екземпляра |
| `diff.max_context_lines` / `max_diff_file_bytes` / `max_merge_file_bytes` | 50 / 1 MiB / 1 MiB | diff і злиття |
| `profiles.fetch_timeout_ms` / `refresh_seconds` | 5000 / 300 | читання профілів runtime |
| `db.pool_min_size` / `pool_max_size` / `connect_timeout_ms` / `statement_timeout_ms` | 1 / 10 / 5000 / 30000 | PostgreSQL |
| `blob.connect_timeout_ms` / `read_timeout_ms` / `max_attempts` | 5000 / 60000 / 3 | MinIO/S3 |
| `jobs.*`, `idempotency.*`, `pages.*` | як у jane-kit | job (upstream-ports), `Idempotency-Key`, сторінки |

## Канонічний архів і дайджест

Єдиний алгоритм для registry, storage (WP-07) і SDK (WP-06) — [`archive.py`](src/jane_registry/archive.py):

1. один запис на **звичайний файл**, без записів тек і симлінків;
2. імена — шляхи пакета (`PackagePath`: ASCII `[A-Za-z0-9._/-]`, `/`, без `..` і початкового `/`), унікальні,
   **відсортовані за зростанням байтів**;
3. метод **0 (stored, без стиснення)** — байти не залежать від збірки zlib;
4. час `1980-01-01 00:00:00`, `external_attr = 0o100644 << 16`, `create_system = 3` (Unix), без extra-полів,
   коментарів і шифрування (Python `zipfile`: локальні заголовки + центральний каталог);
5. `digest = "sha256:" + sha256(байти архіву)`.

Завантажений zip може бути зібраний будь-як (deflate, теки, інший час): registry розпаковує його з
лімітами й перепаковує канонічно, тому дайджест залежить лише від шляхів і вмісту файлів. Для JSON-публікації
`jane-package.json` формується з `manifest` так: UTF-8, відступ 2 пробіли, порядок ключів як у запиті,
не-ASCII без екранування, `\n` у кінці (`json.dumps(m, ensure_ascii=False, indent=2) + "\n"`). Так само
registry записує маніфест форку й версії upstream-port. `GET …/archive` віддає рівно ці байти, `ETag` =
`"sha256:…"`; споживач перевіряє `sha256(тіло) == ETag == digest`. Незмінність алгоритму закріплює тест
`test_canonical_archive_golden_digest`.

Локально: `uv run --package jane-registry jane-registry archive <тека пакета> --out pkg.zip` друкує дайджест,
який видасть registry для того самого вмісту (кеші `__pycache__`, `.pyc`, `.git` тощо не пакуються).

## Публікація й перевірки

`POST /v1/packages/{id}/versions` — `application/zip` (у корені `jane-package.json`) або `application/json`
`{manifest, files}` (`jane-package.json` у `files` заборонено — його формує registry). Порядок перевірок:

| Крок | Помилка |
|---|---|
| пакет існує | `404 not_found` |
| розмір тіла / архіву / файлів | `413 payload_too_large`, `422 limit_exceeded` (`details.path`) |
| zip і шляхи (траверс, симлінки, дублікати, шифрування) | `422 validation_failed` |
| маніфест за схемою; `package_id`/`kind` = пакет; `fork_of` лише від registry і без змін; `kind ↔ entry`; файли з маніфесту; модуль `src/<module>.py`; JSON Schema сутностей (і `key_fields` у `required`); правила колектора за схемою; тести | `422 validation_failed` (`errors[].pointer`: `/manifest/...` або `/files/<шлях>`) |
| `provenance.created_by = llm` і `auto_changes_allowed = false` | `403 forbidden` |
| версія вже є | `409 version_exists` |
| секрети | `422 secret_detected` (`errors[].code`: `aws_access_key`, `private_key`, `secret_file`, `high_entropy_string`…; значення не повертається) |
| профіль runtime і `dependencies.python`; `dependencies.packages` | `422 dependency_not_allowed`; `422 validation_failed` |

Нова версія — `status: draft`, `test_status: unknown`, `created_by` з маніфесту, `published_by` — хто публікував.
Ідентичний вміст зберігається один раз (content-addressed). Секрети шукаються за:
- іменами файлів (`.env`, `*.pem`, `id_rsa`, `.netrc`…);
- відомими форматами: приватні ключі PEM (зокрема розірвані й екрановані), AWS, GitHub, GitLab, Slack
  (токени й webhook), Google, SendGrid, Stripe, Hugging Face, `sk-…` (OpenAI/Anthropic), ключі й SAS
  Azure Storage, токени Telegram-ботів, JWT, паролі в URL;
- значеннями після `Bearer`/`Basic`/`token` (`Authorization: Bearer …`);
- присвоєннями секретоподібним іменам (`password`, `secret`, `token`, `api_key`/`api.key`, `client_secret`,
  `sessionid`, `cookie`…): у лапках — у будь-якому файлі; без лапок (`password: …` YAML, `password = …`
  INI/.properties/.env) — у конфігураційних файлах; `Password=…;`/`Pwd=…;` у рядках підключення — усюди;
  заповнювачі (`${VAR}`, `<…>`, `changeme`, імена змінних середовища) не вважаються секретами;
- високоентропійними рядками в коді/конфігурації (не в HTML-входах тестів).

Файли з BOM UTF-16 або з байтами NUL додатково декодуються (UTF-16 LE/BE, Latin-1), тож NUL-префікс чи UTF-16
не ховають секрет. Файл, більший за `secrets.max_scan_bytes_per_file`, не приймається неперевіреним:
`422 limit_exceeded` (`details.path = secrets.max_scan_bytes_per_file`). Шляхи з сегментом `.` і шляхи, що
відрізняються лише регістром літер, відхиляються (`422 validation_failed`: `invalid_path`, `duplicate_path`).

**Статуси:** `draft → approved | rejected | deprecated | yanked`; `approved → deprecated | yanked`;
`deprecated → approved | yanked`; `rejected`, `yanked` — кінцеві. Інший перехід — `409 conflict`. Кожна
зміна пишеться в `status_history` (хто, коли, причина). `latest_version` — найбільша SemVer серед версій
не в `rejected`/`yanked`; `yanked` архів лишається доступним. Активація в етапах — справа оркестратора.

**Звіти тестів:** `POST …/test-results` (`TestReport` з handler-result.schema; `report.package` має
збігатися з версією, `digest` — з дайджестом, інакше `422`). `test_status` = `failed`, якщо `failed > 0`,
`passed`, якщо `passed > 0`.

## Форк, diff, перенесення змін

- `POST /v1/packages/{id}/forks` — новий пакет із копією файлів версії; у маніфесті registry змінює лише
  `package_id`, `version` (`initial_version` або `from_version`), `fork_of` (батько, версія, дайджест) і
  `provenance` (`based_on` = батько). Форк — окремий архів і окремий дайджест; батько не має посилань на форк,
  тож **жодна зміна батька (нові версії, статуси, налаштування) не змінює форк** (тест
  `test_parent_update_does_not_change_fork`). `auto_changes_allowed` форку типово `false`.
- `GET /v1/packages/{id}/diff?from=&to=` — `from`/`to`: версія цього пакета або `parent:<версія>`; без `from` —
  попередня версія (для першої версії форку — вихідна версія батька). `manifest_changes` (JSON Pointer) і
  файли (`added|removed|modified|unchanged`, unified diff для тексту, `binary` для решти; `jane-package.json`
  описано лише в `manifest_changes`).
- `GET /v1/packages/{id}/upstream` — `last_ported_version`, `parent_latest_version`, `newer_parent_versions`
  (без `rejected`/`yanked`); не форк — `409 conflict`.
- `POST /v1/packages/{id}/upstream-ports` — **лише явна команда**; `202` + job `upstream_port`. Трьохстороннє
  злиття: база — версія батька, востаннє перенесена в `base_version` форку, «їхні» — `parent_version`,
  «наші» — `base_version` (типово остання). Маніфест зливається як JSON (ключі `package_id`, `version`,
  `fork_of`, `provenance` — від форку), текстові файли — порядково. Конфлікт — job `failed` з кодом
  `upstream_conflict` і `error.details.conflicts[] = {path, reason, pointer?}`; нічого не застосовується.
  Успіх — нова версія форку (`draft`) з `provenance.upstream_port = {parent_version, requested_by}`.

## Автономне використання й експорт

```text
uv run --package jane-registry jane-registry export shop.product-extractor@1.2.0 --registry http://localhost:8105 --out ./export
uv run --package jane-registry jane-registry verify ./export/shop.product-extractor-1.2.0.zip
```

`export` завантажує архів версії та, рекурсивно, `dependencies.packages`, перевіряє `ETag` і `digest`,
пише архіви й індекс `jane-export.json` (межа замикання залежностей — `--max-packages`, типово 100).
`verify` бере ліміти з тієї самої конфігурації, що й сервіс (`JANE_REGISTRY_LIMITS__PACKAGES__*`,
`__SECRETS__*`), і працює **без registry**: дайджест (з індексу або
`--digest`), канонічна форма, маніфест за контрактною схемою (якщо доступна тека `contracts/`), наявність
файлів, секрети. Експортований архів виконує handler-runtime (`jane-handler-runtime test <zip>` або
`HandlerInvocation.package_archive`). Тест `test_exported_package_runs_without_registry` зупиняє сервер
після експорту, перевіряє архів і запускає екстрактор з архіву в ізольованому інтерпретаторі (`python -I`).

## Виклик зі стороннього застосунку

```python
import httpx

with httpx.Client(base_url="http://localhost:8105", headers={"Authorization": "Bearer <ключ>"}) as c:
    c.post(
        "/v1/packages",
        json={"package_id": "acme.rules", "kind": "collector-rules", "title": "ACME"},
        headers={"Idempotency-Key": "create-acme.rules"},
    )
    with open("acme-rules.zip", "rb") as f:
        v = c.post(
            "/v1/packages/acme.rules/versions",
            content=f.read(),
            headers={"Content-Type": "application/zip", "Idempotency-Key": "acme.rules@1.0.0"},
        ).json()
    archive = c.get(f"/v1/packages/acme.rules/versions/{v['version']}/archive")
    assert archive.headers["etag"].strip('"') == v["digest"]
```

```text
curl -X POST http://localhost:8105/v1/packages -H "Content-Type: application/json" \
  -H "Idempotency-Key: create-1" -d '{"package_id":"shop.rules","kind":"collector-rules","title":"Shop rules"}'
curl "http://localhost:8105/v1/packages?kind=extractor&entity_type=product&domain=shop.example.test"
```

## Тести

```text
just test registry                                   # unit + contract (memory-бекенд, без сервісів)
just up --project jane-wp05 postgres minio
just integration --project jane-wp05 services/registry   # ті самі API-тести на PostgreSQL + MinIO
just down -v --project jane-wp05
```

API-тести параметризовано бекендом (`memory` / `real`): `real` створює окрему базу
`jane_registry_test_<hex>` на сесію, окрему схему на тест і окремий бакет і прибирає їх.
`test_contract.py` викликає кожну операцію `registry.v1` і перевіряє відповіді за контрактом.

## Відомі обмеження

- Прогін тестів пакета при публікації через handler-runtime не робиться: звіти приходять через
  `POST …/test-results` (ADR-0002 §8 — опційно).
- Архіви без посилань (після невдалої вставки версії) лишаються в blob-сховищі; вони content-addressed і
  нешкідливі, прибирання — окремою операцією (не реалізовано).
- `memory`-бекенд — лише для одного процесу й тестів.
