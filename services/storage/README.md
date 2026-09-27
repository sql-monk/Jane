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
| Формати | RAW: `params.format.raw` → `entry.format.raw` → `original`; `original` зберігає вебсторінку як `text/html` з розширенням `.html`, `json` — Material із вмістом, `html` — лише для HTML. Сутності й інші результати — JSON; `format.entities: jsonl` (файловий адаптер — історія як JSON Lines) |
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
  -e RESULTS_PG_USER=... -e RESULTS_PG_PASSWORD=... jane-storage
```

`connections.json` (секрети — лише посиланнями `env:`/`file:`, ADR-0006):

```json
{"connections": [
  {"connection_id": "raw-files", "kind": "filesystem", "params": {"base_path": "/var/lib/jane/storage"}},
  {"connection_id": "results-pg", "kind": "postgresql",
   "params": {"host": "postgres", "port": 5432, "database": "jane_results", "schema": "public", "sslmode": "prefer"},
   "secret_refs": {"username": "env:RESULTS_PG_USER", "password": "env:RESULTS_PG_PASSWORD"}}
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
r = httpx.post("http://localhost:8107/v1/invocations", json=body,
               headers={"Idempotency-Key": body["delivery"]["delivery_key"]})
ack = r.json()["output"]["writes"][0]      # status: written | duplicate, object.locator.path = …/obs_….html
entities = httpx.get("http://localhost:8107/v1/entities",
                     params={"connection_id": "results-pg", "entity_type": "product"}).json()
```

Заміна сховища — лише в конфігурації етапу завдання (`handler.package_id` і `connections.target`), наприклад
`jane.storage-postgresql` + `results-pg` → `jane.storage-files` + `raw-files`; вхідні дані колектора й
екстрактора ті самі (тест `tests/test_adapter_swap.py` бере їх без змін із прикладів контрактів).

## Конфігурація й ліміти

Змінні середовища з префіксом `JANE_STORAGE_`; ліміти — `JANE_STORAGE_LIMITS__<група>__<поле>` або файл
`JANE_STORAGE_LIMITS_FILE` (форма `PlatformLimits`), стелі — `JANE_STORAGE_LIMITS__HARD_CAPS__…`. Ліміти з
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

Інші налаштування: `JANE_STORAGE_PORT` (8107), `JANE_STORAGE_CONNECTIONS_FILE`, `JANE_STORAGE_TRANSIT_CONNECTION_ID`
(підключення `s3`/`minio` для читання `s3://`-матеріалів), `JANE_STORAGE_PACKAGE_DIRS`, `JANE_CONTRACTS_DIR`
(валідація запитів за контрактами), `JANE_STORAGE_LOG_FORMAT`.

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

pytestmark = pytest.mark.integration          # якщо потрібен dev-стек

class MongoTarget(CompatTarget):
    kind = "mongodb"
    def connection(self): ...                 # ResolvedConnection до порожнього ізольованого простору (база/префікс на тест)
    def unavailable_connection(self): ...     # той самий kind, сховище недосяжне (C-16)
    async def cleanup(self): ...              # прибрати простір після тесту

class TestMongoCompat(AdapterCompatSuite):
    @pytest.fixture
    def compat_target(self):
        stack = load_stack()                  # jane_kit.devstack
        if stack is None: pytest.skip("dev stack is not running")
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
