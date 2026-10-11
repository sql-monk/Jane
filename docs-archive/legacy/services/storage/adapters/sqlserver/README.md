# jane-storage-sqlserver — адаптер SQL Server

Адаптер `sqlserver` сервісу storage (WP-08), драйвер pymssql (FreeTDS у wheel-пакетах для Windows і Linux — ODBC-драйвер
ставити не треба). Реєстрація — entry points `jane.storage.adapters` → `sqlserver`, `jane.storage.packages` →
`jane.storage-sqlserver` ([механізм](../../README.md#адаптери)).

## Підключення

```json
{"connection_id": "results-mssql", "kind": "sqlserver",
 "params": {"host": "sqlserver", "port": 1433, "database": "jane_results", "schema": "dbo"},
 "secret_refs": {"username": "env:RESULTS_MSSQL_USER", "password": "env:RESULTS_MSSQL_PASSWORD"}}
```

Параметри: `host`, `port`, `database` (обов'язковий), `schema` (типово `dbo`), `encryption` (FreeTDS: `off` / `request` /
`require`), `tds_version` (`7.4`). Параметри етапу `table_prefix` (типово `jane_`) і `schema` перекривають підключення.
Потрібні права: `CREATE TABLE` / `CREATE SCHEMA` на першому запуску (`ensure_schema`), далі — читання й запис у таблиці.

## Таблиці

| Таблиця | Вміст |
|---|---|
| `<prefix>entities` | PK `(entity_type, key_hash)`, `doc` = `EntitySnapshot` JSON (nvarchar(max)), `version`, `updated_at`, `scope_hash` (індекс) |
| `<prefix>entity_history` | PK `(entity_type, key_hash, version)`, `doc` = `HistoryEvent` JSON |
| `<prefix>deliveries` | PK `delivery_hash`, `delivery_key`, `doc` = `DeliveryRecord` JSON — безстроково |
| `<prefix>objects` | PK `object_id`, `content` varbinary(max), `meta` = `ObjectRecord` JSON, індекси за `stored_at` і `material_hash` |

Ключі (канонічний, доставки, об'єкта) не мають обмеження довжини, а ключ індексу SQL Server — 900/1700 байтів, тому
індекси будуються за sha256 (`key_hash`, `delivery_hash`, `scope_hash`, `material_hash`, `source_hash`). Час — рядок
RFC 3339 UTC фіксованої ширини (`jane_storage.codec.format_ts`): сортується хронологічно й зберігає мікросекунди на
будь-якій версії TDS. Хеш-колонки — `Latin1_General_100_BIN2`.

`commit_entity` — один T-SQL-пакет в одній транзакції (`XACT_ABORT ON`): вставка доставки (дубль ключа →
`DUPLICATE`), CAS знімка (`UPDATE … WHERE version = @expected` або `INSERT` для нової сутності; нічого не змінено або
дубль → `CONFLICT`), вставка історії — усе або нічого. Жертва взаємоблокування (1205) → `CONFLICT` (нічого не
записано, ядро повторить). Перевірки «чи є» з `HOLDLOCK` навмисно немає: вона дає відомі взаємоблокування
діапазонних блокувань при паралельних вставках. `ensure_schema` ідемпотентний і серіалізований `sp_getapplock`.

## Ліміти

| Параметр | Типово | Де задається |
|---|---|---|
| `pool_min_size` / `pool_max_size` | 1 / 10 | `params` підключення або `JANE_STORAGE_LIMITS__ADAPTERS__POOL_*` (власний пул з'єднань, кожен виклик — у потоці) |
| `connect_timeout_ms` / `command_timeout_ms` | 10000 / 30000 | те саме (`login_timeout` / `timeout` pymssql, округлені до секунд) |
| `lock_timeout_ms` | 30000 | те саме — очікування `sp_getapplock` у `ensure_schema` |

## Тести

```text
just up --project jane-wp08 sqlserver
just integration --project jane-wp08 services/storage/adapters/sqlserver   # C-01…C-16
just down -v --project jane-wp08
```

Тести ділять базу `jane_compat` (створюється за потреби), кожен — власна схема, яку видаляє після себе.
`tests/test_sqlserver_config.py` (без сервісів) входить у `just check`.
