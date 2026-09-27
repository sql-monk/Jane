# jane-storage-mongodb — адаптер MongoDB

Адаптер `mongodb` сервісу storage (WP-08), нативний asyncio-клієнт PyMongo (`AsyncMongoClient`). Реєстрація — entry
points `jane.storage.adapters` → `mongodb`, `jane.storage.packages` → `jane.storage-mongodb`
([механізм](../../README.md#адаптери)).

## Підключення

```json
{"connection_id": "results-mongo", "kind": "mongodb",
 "params": {"host": "mongodb", "port": 27017, "database": "jane_results", "auth_source": "admin"},
 "secret_refs": {"username": "env:RESULTS_MONGO_USER", "password": "env:RESULTS_MONGO_PASSWORD"}}
```

Параметри: `host`, `port`, `database` (типово `jane`), `auth_source` (`admin`), `tls`, `replica_set`,
`direct_connection`, `chunk_bytes`, `prefix` (префікс колекцій, типово `jane_`; параметр етапу `prefix` його перекриває).

## Колекції

| Колекція | Вміст |
|---|---|
| `<prefix>entities` | `_id = <entity_type>\|<sha256(canonical_key)>`, документ `EntitySnapshot` (+ `pending`) |
| `<prefix>entity_history` | подія історії на кожну версію, унікальний індекс `(entity_type, key_hash, version)` |
| `<prefix>deliveries` | `_id = sha256(delivery_key)`, `DeliveryRecord` — безстроково |
| `<prefix>objects` | `_id = object_id`, `ObjectRecord` (точка коміту об'єкта) |
| `<prefix>object_chunks` | байти RAW частинами по `chunk_bytes` (документ BSON ≤ 16 МіБ) |

## Атомарність без транзакцій

Багатодокументні транзакції MongoDB потребують набору реплік; адаптер їх не використовує, тож працює і з окремим
`mongod` (як у dev-стеку). `commit_entity` спирається на атомарність одного документа:

1. ключ є в `deliveries` або в `pending` збереженого знімка → `DUPLICATE`;
2. CAS знімка: `replace_one({_id, version: expected})` або `insert_one` для нової сутності (дубль `_id` →
   `CONFLICT`). Документ-заміна містить подію історії й підтвердження доставки в `pending` — це **єдина точка
   коміту**: стан, версія, подія й ключ доставки з'являються разом;
3. перенесення: вставити подію історії й запис доставки, потім `$unset: pending`. Збій тут нічого не втрачає:
   `get_delivery` знаходить ключ у `pending` (індекс), читачі історії й наступний коміт спершу переносять `pending`
   (усі кроки ідемпотентні). Тест — `tests/test_recovery.py`.

RAW: частини з `_id = <object_id>:<sha256>:<n>` (ідемпотентний upsert), потім `insert_one` документа об'єкта; якщо
конкурентний запис того самого ключа з іншим вмістом переміг — власні частини видаляються, `AdapterError(retryable=False)`.

## Ліміти

| Параметр | Типово | Де задається |
|---|---|---|
| `pool_min_size` / `pool_max_size` | 0 / 10 | `params` підключення або `JANE_STORAGE_LIMITS__ADAPTERS__POOL_*` |
| `connect_timeout_ms` / `command_timeout_ms` | 10000 / 30000 | те саме (`serverSelectionTimeoutMS`, `connectTimeoutMS` / `socketTimeoutMS`) |
| `chunk_bytes` | 4194304 | `params` підключення (1…15 МіБ) |

## Тести

```text
just up --project jane-wp08 mongodb
just integration --project jane-wp08 services/storage/adapters/mongodb   # C-01…C-16 + відновлення
just down -v --project jane-wp08
```

Кожен тест — власна база, яку видаляє після себе. `tests/test_mongo_config.py` (без сервісів) входить у `just check`.
