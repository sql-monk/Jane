# storage — обробник збереження Jane

Сервіс-виконавець пакетів типу `storage` (ТЗ §5, §11; plan.md WP-07/08). Колектори й екстрактори не пишуть у БД:
їхні результати (RAW-матеріали й сутності) зберігає цей сервіс через спільний протокол обробника. Сховище
обирається пакетом і підключенням етапу, тож заміна сховища не змінює коду колектора чи екстрактора (критерій 3).

- Запис: `contracts/openapi/handler.v1.yaml` (`POST /v1/invocations`, `/v1/test-runs`, `/v1/connections*`, `/v1/jobs/*`).
- Читання: `contracts/openapi/storage.v1.yaml` (`/v1/entities`, `/v1/entity-history`, `/v1/objects*`).
- Адаптер: `contracts/python/src/jane_contracts/storage_adapter.py`, сценарії — `contracts/docs/storage-adapter.md`.

## Семантика

| Вимога | Як реалізовано |
|---|---|
| Ідемпотентний запис за ключем доставки | Ключ доставки кожної частини виклику (`<delivery_key>#<n>` для n-ї сутності, `<delivery_key>` для першого RAW) зберігається адаптером **атомарно разом із даними** і безстроково; повтор повертає збережені підтвердження з `status: duplicate`, `duplicate: true` — між екземплярами й після рестарту |
| Нове спостереження — новий запис | Новий `observation_id`/`delivery_key` → новий запис історії й нова версія стану |
| Часткове оновлення | Змінюються лише поля з `fields`; відсутнє поле не чіпається |
| Явне очищення | Лише `cleared: [...]` (`null` у `fields` → 422) → поле зникає з `fields`, потрапляє в `cleared_fields` |
| Захист від запізнілих даних | Кожне поле пам'ятає порядок свого значення (`observed_at` → `sequence` → `observation_id`); старіше значення потрапляє лише в історію (`stale`, `partially_stale`) |
| Актуальний стан та історія | `EntitySnapshot` з `version` + `HistoryEvent` на кожне прийняте оновлення (включно із запізнілими) |
| Формати | RAW: `params.format.raw` → `entry.format.raw` → типова поведінка (ТЗ §5): вебсторінка HTML/XHTML — байт-у-байт у `.html`, будь-який інший RAW (Telegram, JSON API, стрічки) — JSON-документ Material із вбудованим вмістом (`.json`). Явні перевизначення: `original` (байти як є, розширення за медіатипом), `html` (лише для HTML), `json`. Сутності й інші результати — JSON; `format.entities: jsonl` (файловий адаптер — історія як JSON Lines) |
| Конкурентні записи | Адаптер робить compare-and-swap за `version`; ядро повторює при `CONFLICT` за `limits.retries` |
| Режим тестування | `context.test_mode: true` — валідація без виклику адаптера, `WriteAck.status = simulated` |

Злиття — чиста функція ядра (`jane_storage.merge`), адаптер дає лише атомарні примітиви, тому всі шість сховищ
поводяться однаково.

## Запуск

```text
uv sync --all-packages
JANE_STORAGE_CONNECTIONS_FILE=connections.json uv run --all-packages python -m jane_storage   # порт 8107
```

`--all-packages` потрібен, щоб встановились дистрибутиви адаптерів (вони — окремі пакети, див. «Адаптери»).
Docker (контекст — корінь репозиторію; образ містить ядро й усі `services/storage/adapters/*`):

```text
docker build -f services/storage/Dockerfile -t jane-storage .
docker run -p 8107:8000 -v jane-storage:/var/lib/jane/storage \
  -v ./connections.json:/cfg/connections.json:ro -e JANE_STORAGE_CONNECTIONS_FILE=/cfg/connections.json \
  -e JANE_STORAGE_CONNECTION_HOST_ALLOWLIST='["postgres:5432"]' \
  -e JANE_SECRET_RESULTS_PG_USER=... -e JANE_SECRET_RESULTS_PG_PASSWORD=... jane-storage
```

`connections.json` (секрети — лише посиланнями `env:`/`file:`, ADR-0006):

```json
{"connections": [
  {"connection_id": "raw-files", "kind": "filesystem", "params": {"base_path": "/var/lib/jane/storage"}},
  {"connection_id": "results-pg", "kind": "postgresql",
   "params": {"host": "postgres", "port": 5432, "database": "jane_results", "schema": "public", "sslmode": "prefer"},
   "secret_refs": {"username": "env:JANE_SECRET_RESULTS_PG_USER", "password": "env:JANE_SECRET_RESULTS_PG_PASSWORD"}}
]}
```

Підключення можна також задати `PUT /v1/connections/{id}` (так їх синхронізує оркестратор).

Кілька екземплярів: стан запису — у сховищі (записи доставок, CAS за версією, для файлів — файли-блокування), тож
екземпляри над одним сховищем не дублюють записів. У пам'яті екземпляра лише кеш ключів ідемпотентності (відхилення
повторного ключа з іншим тілом), результати `GET /v1/invocations/{id}` і підключення, додані через `PUT`.

## Приклад виклику зі стороннього застосунку

```python
import httpx

material = {...}  # Material від колектора (contracts/schemas/material.schema.json)
body = {
    "handler": {"package_id": "jane.storage-files", "version": "1.0.0"},
    "connections": {"target": "raw-files"},
    "inputs": [{"kind": "material", "material": material}],
    "delivery": {"delivery_key": "my-app:obs_01J9ZQ4A0000000000000001"},
}
r = httpx.post(
    "http://localhost:8107/v1/invocations",
    json=body,
    headers={"Idempotency-Key": body["delivery"]["delivery_key"]},
)
ack = r.json()["output"]["writes"][0]  # status: written | duplicate, object.locator.path = …/obs_….html
entities = httpx.get(
    "http://localhost:8107/v1/entities", params={"connection_id": "results-pg", "entity_type": "product"}
).json()
```

Заміна сховища — лише в конфігурації етапу завдання (`handler.package_id` і `connections.target`), наприклад
`jane.storage-postgresql` + `results-pg` → `jane.storage-files` + `raw-files`; вхідні дані колектора й
екстрактора ті самі (тест `tests/test_adapter_swap.py` бере їх без змін із прикладів контрактів).

## Конфігурація й ліміти

Змінні середовища з префіксом `JANE_STORAGE_`; ліміти — `JANE_STORAGE_LIMITS__<група>__<поле>` або файл
`JANE_STORAGE_LIMITS_FILE` (форма `PlatformLimits`; можна дати цілий профіль `deploy/profiles/<профіль>.json` —
ліміти контракту, яких storage не має, ігноруються й перелічуються в журналі старту, опечатка чи некоректне
значення — помилка старту; див. README jane-kit), стелі — `JANE_STORAGE_LIMITS__HARD_CAPS__…`. Ліміти з
`HandlerInvocation.limits` (`retries`, `timeouts.sync_response_max_ms`, `timeouts.request_timeout_ms`) діють у межах
стель. Типові значення:

| Параметр | Типово | Призначення |
|---|---|---|
| `retries.max_attempts` / `initial_backoff_ms` / `max_backoff_ms` / `backoff_multiplier` / `jitter` | 4 / 200 / 10000 / 2.0 / true | повтори ядра при `CONFLICT` |
| `timeouts.sync_response_max_ms` | 30000 | довше — `202` + Job |
| `timeouts.request_timeout_ms` | 30000 | читання blob (`download_url`, `s3://`) |
| `transfer.max_request_body_bytes` | 16777216 | більше тіло — `413` |
| `transfer.inline_max_bytes` | 1048576 | до цього розміру `GET /v1/objects/{id}` віддає вміст inline (якщо в адаптера немає URI) |
| `transfer.idempotency_ttl_seconds` | 86400 | кеш ключів ідемпотентності в пам'яті (стійка дедуплікація — у сховищі, безстроково) |
| `objects.max_object_bytes` | 104857600 | найбільший RAW/документ |
| `adapters.lock_timeout_ms` / `lock_stale_ms` / `lock_poll_ms` / `replace_retry_ms` | 30000 / 120000 / 10 / 5000 | файловий адаптер |
| `adapters.pool_min_size` / `pool_max_size` / `connect_timeout_ms` / `command_timeout_ms` | 1 / 10 / 10000 / 30000 | PostgreSQL |
| `pages.default_page_size` / `max_page_size` | 50 / 500 | пагінація читального API |
| `invocations.max_results_in_memory` | 10000 | `GET /v1/invocations/{id}` |
| `jobs.max_concurrent_jobs` / `max_queued_jobs` / `job_timeout_ms` | 4 / 1000 / 3600000 | виконання викликів |
| `packages.max_archive_bytes` / `max_unpacked_bytes` / `max_files` | 20971520 / 52428800 / 2000 | межі для архівів у запиті та registry |
| `packages.cache_max_entries` | 128 | перевірені пакети registry в пам'яті одного екземпляра |
| `packages.registry_connect_timeout_ms` / `registry_request_timeout_ms` | 5000 / 30000 | встановлення з'єднання / повне завантаження архіву |

Інші налаштування: `JANE_STORAGE_PORT` (8107), `JANE_STORAGE_CONNECTIONS_FILE`, `JANE_STORAGE_TRANSIT_CONNECTION_ID`
(підключення `s3`/`minio` для читання `s3://`-матеріалів), `JANE_STORAGE_PACKAGE_DIRS`, `JANE_CONTRACTS_DIR`
(валідація запитів за контрактами), `JANE_STORAGE_LOG_FORMAT`.

### Пакети з registry (ADR-0009 §4)

Пакет `handler` (`package_id`, точна `version`, необов'язковий `digest`) береться в такому порядку:

1. `package_archive` запиту;
2. вбудований каталог (пакети встановлених адаптерів і `JANE_STORAGE_PACKAGE_DIRS`) — він авторитетний для
   свого `package_id@version`: інший `digest` → `422 digest_mismatch` без звернення до registry;
3. registry (`GET /v1/packages/{id}/versions/{v}/archive`, `registry.v1`), якщо задано
   `JANE_STORAGE_REGISTRY_URL`.

| Змінна | Типово | Дія |
|---|---|---|
| `JANE_STORAGE_REGISTRY_URL` | порожньо | `http(s)://host[:port][/шлях]` registry; без userinfo, query, fragment (помилка старту). Порожньо — registry немає, невідомий пакет → `404 not_found` |
| `JANE_STORAGE_REGISTRY_TOKEN` | порожньо | Bearer-токен лише для цієї адреси; не журналюється; не має префікса `JANE_SECRET_`, тож `secret_refs` підключень на нього не посилаються |

Перевірки архіву з registry (і `package_archive`): `ETag` = `sha256:` байтів; канонічний дайджест (той самий
алгоритм, що в registry) = `handler.digest`, якщо задано; маніфест — саме `package_id@version` запиту,
`kind: storage`, `entry.executor: storage`, без `dependencies`, адаптер встановлено; zip без небезпечних шляхів,
дублікатів і symlink, у межах `packages.*`. Адреса й токен — конфігурація оператора, не запиту; перенаправлення
не виконуються, проксі із середовища не використовується (тому allowlist хостів не потрібен).
Перевірені пакети кешуються за дайджестом у пам'яті екземпляра (`packages.cache_max_entries`); влучання в кеш
перевіряється на `package_id@version` так само, як завантаження: дайджест іншої версії → `digest_mismatch`
і з холодним, і з теплим кешем. Одночасні виклики однієї версії ділять одне завантаження. Помилки:
`404 not_found` (немає у registry), `502 upstream_unavailable` (немає відповіді, тайм-аут, 5xx/429 —
`retryable: true`; 401/403, перенаправлення — `retryable: false`), `422` (`digest_mismatch`,
`validation_failed`, `dependency_not_allowed`, `limit_exceeded`). `POST /v1/test-runs` бере пакет так само.

### Політика секретів і вмісту

| Змінна | Типово | Дія |
|---|---|---|
| `JANE_STORAGE_SECRET_ENV_PREFIX` | `JANE_SECRET_` | `secret_refs` типу `env:` можуть називати лише змінні з цим префіксом; порожнє значення вимикає `env:` |
| `JANE_STORAGE_SECRET_FILES_DIR` | `/run/secrets` | `secret_refs` типу `file:` можуть читати лише файли цього каталогу після розв'язання `..` і symlink; порожнє значення вимикає `file:` |
| `JANE_STORAGE_CONNECTION_HOST_ALLOWLIST` | `[]` | JSON-список дозволених `hostname` або `hostname:port` для мережевих адрес підключень; порожній список забороняє всі такі підключення |
| `JANE_STORAGE_CONTENT_FILES_DIR` | не задано | `ContentRef` з `file:///…` читається лише з цього каталогу після розв'язання symlink; без змінної локальні blob заборонені |
| `JANE_STORAGE_DOWNLOAD_HOST_ALLOWLIST` | `[]` | JSON-список дозволених `hostname` або `hostname:port` для `ContentRef.download_url`; порожній список забороняє HTTP-завантаження |

Для `download_url` дозволені лише HTTP(S) URL без userinfo; порт звіряється з allowlist (типово 80/443).
HTTP-перенаправлення не виконуються. Змінні HTTP-проксі середовища для цих завантажень не застосовуються.
Каталог `JANE_STORAGE_CONTENT_FILES_DIR` має бути окремим спільним транзитним томом, доступним виробнику
`ContentRef` і storage за однаковим шляхом. Не спрямовуйте його на `/`, `/run/secrets` або каталог конфігурації.
Якщо виробник використовує `s3://` з налаштованим `JANE_STORAGE_TRANSIT_CONNECTION_ID`, цей каталог не потрібний.
Невідповідні адреси чи файли відхиляються до читання вмісту.
Для підключень `s3`/`minio` з власним `params.endpoint` політика вимагає
`params.addressing_style: path` (`minio` використовує `path` типово). Значення `auto` або `virtual`
може спрямувати запит із секретами до `<bucket>.<endpoint host>`, якого немає в allowlist.
Без власного S3 endpoint allowlist також звіряється з фактичним host, який формує botocore для
`bucket`/`region`/`addressing_style`. Наприклад, `us-east-1` з `auto` і bucket `outside` використовує
`outside.s3.amazonaws.com:443`, а з `path` — `s3.amazonaws.com:443`; запис
`s3.us-east-1.amazonaws.com:443` не дозволяє жоден із цих host. Перевірка формує запит без мережевого
виклику та враховує також AWS endpoint, заданий через середовище процесу.

## Адаптери

Кожен адаптер — окремий uv-пакет `services/storage/adapters/<name>/` з дистрибутивом `jane-storage-<name>`
(ця назва потрібна Dockerfile). Ядро знаходить адаптери й пакети збереження через entry points:

```toml
[project]
name = "jane-storage-mongodb"
dependencies = ["jane-storage", "jane-contracts", "pymongo>=4.10"]

[project.entry-points."jane.storage.adapters"]
mongodb = "jane_storage_mongodb:MongoAdapter"            # ім'я == Adapter.kind == Connection.kind

[project.entry-points."jane.storage.packages"]
"jane.storage-mongodb" = "jane_storage_mongodb:package_dir"  # () -> Path каталогу з jane-package.json

[tool.uv.sources]
jane-storage = { path = "../..", editable = true }        # саме path: uv не вважає вкладений проєкт членом workspace під час збирання
jane-contracts = { path = "../../../../contracts/python", editable = true }
```

- Клас реалізує `jane_contracts.storage_adapter.StorageAdapter`; `capabilities = {"objects", "entities", "history"}`
  (реєстр відхиляє інше). Спільні JSON-документи (`EntitySnapshot`, `HistoryEvent`, `DeliveryRecord`, `ObjectRecord`) і
  `entity_ack` — `jane_storage.codec`; `object_id` — `jane_storage.keys.object_id_for`. `commit_entity` має записати
  `DeliveryRecord(acks=[entity_ack(new, event)])` атомарно зі знімком і подією історії.
- Пакет збереження адаптера (`package/jane-package.json`, `schemas/params.schema.json`, `tests/…`) лежить у дистрибутиві
  адаптера; сервіс бачить його без репозиторію.
- Параметри етапу `prefix`, `table_prefix`, `schema` і ліміти `adapters.*` передаються в `open(connection, options)`;
  `options["entities_format"]` — формат сутностей.
- Нічого в ядрі чи Dockerfile міняти не треба: `uv lock`, і адаптер з'являється в `/v1/info`.

### Набір сумісності C-01…C-16

`jane_storage.compat.AdapterCompatSuite` — pytest-клас із 17 тестами (реєстрація + C-01…C-16). Адаптер підключає його так
(приклади — `adapters/files/tests/test_compat.py`, `adapters/postgres/tests/test_compat.py`):

```python
import pytest
from jane_storage.compat import AdapterCompatSuite, CompatTarget

pytestmark = pytest.mark.integration  # якщо потрібен dev-стек


class MongoTarget(CompatTarget):
    kind = "mongodb"

    def connection(self): ...  # ResolvedConnection до порожнього ізольованого простору (база/префікс на тест)
    def unavailable_connection(self): ...  # той самий kind, сховище недосяжне (C-16)
    async def cleanup(self): ...  # прибрати простір після тесту


class TestMongoCompat(AdapterCompatSuite):
    @pytest.fixture
    def compat_target(self):
        stack = load_stack()  # jane_kit.devstack
        if stack is None:
            pytest.skip("dev stack is not running")
        return MongoTarget(stack)
```

Набір запускає справжній адаптер (через entry point) разом зі справжнім ядром і обробником; хуки `native_*` —
необов'язкові перевірки нативного формату (файловий адаптер перевіряє `.html` і JSON/JSONL на диску).

## Тести

```text
just test storage                                   # unit + contract: ядро, HTTP, files-адаптер (C-01…C-16)
just up --project jane-wp07 postgres
just integration --project jane-wp07 services/storage   # PostgreSQL: C-01…C-16, заміна сховища
just down -v --project jane-wp07
```

## Публікація пакетів збереження

```text
uv run --all-packages jane-storage-packages list                        # пакети й дайджести
uv run --all-packages jane-storage-packages publish --registry http://localhost:8105
```

`publish` робить `POST /v1/packages` (409 — уже є) і `POST /v1/packages/{id}/versions` з `PublishRequest`
(registry.v1). Поки репозиторій (WP-05) не готовий, публікацію перевірено на моку з контракту
(`tests/test_packages.py`).
