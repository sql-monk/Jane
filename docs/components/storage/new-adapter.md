# Storage: новий адаптер

Як додати сховище до Storage: пакет адаптера за протоколом `StorageAdapter`, пакет збереження `jane.storage-*` і набір сумісності C-01…C-16. Нормативні джерела — протокол [storage_adapter.py](../../../contracts/python/src/jane_contracts/storage_adapter.py) і сценарії [storage-adapter.md](../../../contracts/docs/storage-adapter.md); ця сторінка не повторює їх, а показує порядок роботи.

## Зміст

- [Що робить адаптер](#що-робить-адаптер)
- [Структура пакета](#структура-пакета)
- [Реєстрація](#реєстрація)
- [Реалізація протоколу](#реалізація-протоколу)
- [Пакет збереження](#пакет-збереження)
- [Мережеві адреси й секрети](#мережеві-адреси-й-секрети)
- [Набір сумісності](#набір-сумісності)
- [Перевірка перед використанням](#перевірка-перед-використанням)

## Що робить адаптер

Адаптер дає ядру надійні примітиви й не знає семантики злиття ([поділ ядро — адаптер](internals.md#поділ-ядро--адаптер)). Дві обов'язкові гарантії:

1. `commit_entity` атомарний: унікальність ключа доставки, CAS за `version` знімка й додавання події історії вдаються або не вдаються разом.
2. `put_object` ідемпотентний за `object_key`: той самий SHA-256 — наявний запис; інший — `AdapterError(retryable=False)`.

Кожен адаптер зберігає і RAW, і сутності з історією: `capabilities` має дорівнювати `{"objects", "entities", "history"}`, інакше сервіс не стартує.

## Структура пакета

Новий адаптер — окремий пакет у `services/storage/adapters/<назва>/` (каталог потрапляє в uv workspace і в образ Storage автоматично):

```text
services/storage/adapters/<назва>/
├── pyproject.toml                  # пакет jane-storage-<назва>, драйвер, entry points
├── README.md
├── src/jane_storage_<назва>/
│   ├── __init__.py                 # клас адаптера і package_dir()
│   ├── py.typed
│   └── package/                    # пакет збереження jane.storage-<назва>
│       ├── jane-package.json
│       ├── schemas/params.schema.json
│       └── tests/…                 # входи тестів маніфесту
└── tests/
    └── test_compat.py              # набір сумісності C-01…C-16
```

Зразки — наявні адаптери в [services/storage/adapters](../../../services/storage/adapters/); найпростіший — `files`.

## Реєстрація

Ядро не імпортує адаптери напряму: достатньо встановити пакет. У `pyproject.toml` адаптера:

```toml
[project]
name = "jane-storage-example"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["jane-storage", "jane-contracts", "<драйвер сховища>"]

[project.entry-points."jane.storage.adapters"]
example = "jane_storage_example:ExampleAdapter"      # ім'я = ExampleAdapter.kind = Connection.kind

[project.entry-points."jane.storage.packages"]
"jane.storage-example" = "jane_storage_example:package_dir"

[tool.uv.sources]
jane-storage = { path = "../..", editable = true }
```

Залежність `jane-storage` задається шляхом, а не `workspace = true`: uv не вважає проєкт, вкладений в інший член workspace, членом workspace під час його збирання.

## Реалізація протоколу

Скелет класу (не повна реалізація; сигнатури — з протоколу):

```python
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, ClassVar

from jane_contracts.storage_adapter import (
    AdapterError, CommitResult, DeliveryRecord, EntitySnapshot, HistoryEvent, ObjectRecord, RawObject,
    ResolvedConnection,
)


def package_dir() -> Path:
    return Path(__file__).parent / "package"


class ExampleAdapter:
    kind: ClassVar[str] = "example"
    capabilities: ClassVar[frozenset[str]] = frozenset({"objects", "entities", "history"})

    async def open(self, connection: ResolvedConnection, options: Mapping[str, Any]) -> None: ...
    async def close(self) -> None: ...
    async def health(self) -> bool: ...
    async def ensure_schema(self, entity_types: Sequence[str]) -> None: ...
    async def put_object(self, obj: RawObject) -> ObjectRecord: ...
    async def get_object(self, object_id: str) -> ObjectRecord | None: ...
    async def read_object_content(self, object_id: str) -> bytes: ...
    async def list_objects(self, *, source_id=None, material_id=None, since=None, until=None,
                           cursor=None, limit: int): ...
    async def read_entity(self, entity_type: str, canonical_key: str) -> EntitySnapshot | None: ...
    async def commit_entity(self, *, new: EntitySnapshot, expected_version: int | None,
                            event: HistoryEvent) -> CommitResult: ...
    async def list_entities(self, entity_type: str, *, scope=None, updated_since=None, cursor=None,
                            limit: int): ...
    async def list_history(self, entity_type: str, canonical_key: str, *, cursor=None, limit: int): ...
    async def get_delivery(self, delivery_key: str) -> DeliveryRecord | None: ...
    async def record_delivery(self, record: DeliveryRecord) -> bool: ...
```

Правила, які перевіряє набір сумісності або ядро:

| Тема | Правило |
|---|---|
| Конфігурація | `open` отримує вже розв'язані секрети в `connection.secrets` і опції в `options`; адаптер не читає змінних середовища й сховищ секретів |
| Опції | Безпечні типові значення в коді; `options` (група `adapters.*` сервісу і простір етапу `prefix` / `schema` / `table_prefix`, `entities_format`) перекривають `params` підключення |
| `ensure_schema` | Ідемпотентний і безпечний для паралельного виклику з кількох екземплярів |
| `object_id` | `jane_storage.keys.object_id_for(object_key)` — однаковий у всіх адаптерах |
| `commit_entity` | `DUPLICATE`, якщо ключ доставки вже записано; `CONFLICT`, якщо версія не `expected_version` (`None` — сутності не має бути); інакше записати знімок і подію, повернути `COMMITTED` |
| `DeliveryRecord.acks` | Однаковий документ для всіх адаптерів: для сутності — `jane_storage.codec.entity_ack(new, event)`; для об'єкта ядро передає документ саме |
| `get_delivery` | Повертає лише завершену доставку; незавершену після збою коміт виконує знову |
| `record_delivery` | Вставка, якщо ключа немає; `False` — ключ уже є |
| Списки | Курсор непрозорий; повний обхід без пропусків і дублів; `list_history` — новіші версії першими |
| Помилки | Лише `AdapterError`; `retryable=True` — недоступність, тайм-аут, конкуренція; `False` — автентифікація, хибні параметри, пошкоджені дані |
| Серіалізація | `jane_storage.codec`: `snapshot_to_json`, `event_to_json`, `delivery_to_json`, `object_record_to_json` і зворотні функції |
| `content_uri(rec)` | Необов'язковий: постійний URI вмісту (`file:///`, `s3://`), який читачі отримають у `ContentRef` |

Як атомарність досягнуто в наявних сховищах (транзакція, CAS одного документа з `pending`, умовні записи) — [адаптери](adapters.md).

## Пакет збереження

Пакет — маніфест без коду. Мінімальні поля `jane-package.json` (формат — [handler-packages.md](../../../contracts/docs/handler-packages.md), схема — [package-manifest.schema.json](../../../contracts/schemas/package-manifest.schema.json)):

```json
{
  "schema_version": "1",
  "package_id": "jane.storage-example",
  "version": "1.0.0",
  "kind": "storage",
  "title": "Example storage",
  "entry": {
    "executor": "storage",
    "adapter": "example",
    "writes": "raw_and_entities",
    "format": {"entities": "json"},
    "history": true
  },
  "input": {"accepts": ["material", "entities"]},
  "params_schema": "schemas/params.schema.json",
  "required_connections": [{"name": "target", "kind": "example", "purpose": "куди писати"}],
  "tests": [
    {"name": "idempotent-redelivery", "input": {"entities": "tests/redelivery/entities.json"}, "expected_status": "success"}
  ]
}
```

Обмеження ядра: `kind: storage`, `entry.executor: storage`, `entry.history` лише `true`, без `dependencies`; `params_schema` — коректна JSON Schema 2020-12. Повні зразки — маніфести наявних адаптерів, наприклад [jane.storage-files](../../../services/storage/adapters/files/src/jane_storage_files/package/jane-package.json). Тести маніфесту виконує `POST /v1/test-runs`.

## Мережеві адреси й секрети

Ядро перевіряє мережеві адреси підключення за allowlist до розв'язання секретів ([політика](configuration.md#політика-секретів-і-хостів)). Для адаптера, невідомого ядру, перевіряються лише параметри із загальними іменами (`host`, `hosts`, `hostname`, `server`, `address`, `endpoint`, `endpoint_url`, `url`, `uri`, `dsn`, `connection_string`, `base_url`, `api_base`). Тому:

- задавайте адреси сховища лише в цих параметрах;
- якщо адаптер має типову адресу (наприклад, `localhost`) або виводить хост інакше, додайте правило для свого `kind` у `KIND_ADDRESSES` ядра ([policy.py](../../../services/storage/src/jane_storage/policy.py)), інакше типова адреса пройде без перевірки;
- імена секретів (`username`, `password`, `access_key`…) опишіть у README адаптера; значення приходять лише через `secret_refs`.

## Набір сумісності

Набір — модуль `jane_storage.compat` (extra `compat` пакета `jane-storage`): базовий клас pytest `AdapterCompatSuite` запускає справжній адаптер (знайдений за entry point) разом зі справжнім ядром. Пакет адаптера дає лише ціль `CompatTarget`:

```python
import pytest

from jane_contracts.storage_adapter import ResolvedConnection
from jane_storage.compat import AdapterCompatSuite, CompatTarget


class ExampleTarget(CompatTarget):
    kind = "example"

    def connection(self) -> ResolvedConnection:
        """Підключення до порожнього ізольованого простору доступного сховища (те саме на кожен виклик)."""
        ...

    def unavailable_connection(self) -> ResolvedConnection:
        """Підключення того самого типу до недоступного сховища (C-16)."""
        ...


class TestExampleCompat(AdapterCompatSuite):
    @pytest.fixture
    def compat_target(self) -> CompatTarget:
        return ExampleTarget()
```

Необов'язкові методи `CompatTarget`: `options()` (базові опції `open`, наприклад `prefix`), `cleanup()` (видалити простір після тесту), `native_object_path`, `native_entity_document`, `native_history_documents` (перевірка рідного формату в C-12, C-13); атрибут `entity_formats` — підтримувані `entities_format`. Кожен тест має отримувати власний простір: схему, префікс, бакет.

Сценарії C-01…C-16 обов'язкові всі; пропускати сценарії сутностей чи історії не можна. Тести, яким потрібне зовнішнє сховище, позначте `pytestmark = pytest.mark.integration` і беріть адреси з dev-стеку (`jane_kit.devstack.load_stack()`), як у [test_compat.py PostgreSQL](../../../services/storage/adapters/postgres/tests/test_compat.py). Якщо сховища немає в dev-стеку, його сервіс додається в [infra/compose.yaml](../../../infra/compose.yaml) з унікальними портами й томами.

Запуск:

```powershell
just test storage
just integration --project <проєкт> services/storage/adapters/<назва>
```

Перша команда запускає тести без зовнішніх сервісів (усі пакети в `services/storage`), друга — інтеграційні тести адаптера з dev-стеком, піднятим `just up --project <проєкт> <сервіс>`.

## Перевірка перед використанням

1. `uv sync --all-packages`, потім `uv run --all-packages jane-storage-packages list` показує новий пакет із digest.
2. Під час старту журнал `storage ready` перелічує новий `kind` в `adapters`; `GET /v1/info` — у `capabilities.adapters`.
3. `PUT /v1/connections/{id}` з новим `kind` і `POST /v1/connections/{id}/test` повертають `ok: true`.
4. `POST /v1/test-runs` для пакета `jane.storage-<назва>` проходить усі тести маніфесту.
5. `just check` — lint, типи, unit і контрактні тести без помилок.
