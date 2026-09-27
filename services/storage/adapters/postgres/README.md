# jane-storage-postgres — адаптер PostgreSQL

Адаптер `postgresql` сервісу storage (WP-07), asyncpg. Реєстрація — entry points `jane.storage.adapters` →
`postgresql`, `jane.storage.packages` → `jane.storage-postgresql` ([механізм](../../README.md#адаптери)).

## Підключення

```json
{"connection_id": "results-pg", "kind": "postgresql",
 "params": {"host": "postgres", "port": 5432, "database": "jane_results", "schema": "public", "sslmode": "prefer"},
 "secret_refs": {"username": "env:RESULTS_PG_USER", "password": "env:RESULTS_PG_PASSWORD"}}
```

Параметри етапу: `table_prefix` (типово `jane_`), `schema` (перекриває `params.schema`), `format.raw`.

## Таблиці

| Таблиця | Вміст |
|---|---|
| `<prefix>entities` | актуальний стан: PK `(entity_type, canonical_key)`, `fields`/`field_orders`/`cleared_fields` jsonb, `version` |
| `<prefix>entity_history` | кожне прийняте оновлення (також запізніле): PK `(entity_type, canonical_key, version)` |
| `<prefix>deliveries` | `delivery_key` PK + підтвердження (jsonb), безстроково |
| `<prefix>objects` | RAW/документи: `content` bytea, медіатип, sha256, метадані Material |

`commit_entity` — одна транзакція: `INSERT … ON CONFLICT DO NOTHING` у `deliveries` (не вставлено → `DUPLICATE`),
CAS стану (`UPDATE … WHERE version = $expected` або `INSERT … ON CONFLICT DO NOTHING` для нової сутності; нічого не
змінено → `CONFLICT`) і вставка історії. `ensure_schema` ідемпотентний і серіалізований advisory-lock-ом.

## Ліміти

| Параметр | Типово | Де задається |
|---|---|---|
| `pool_min_size` / `pool_max_size` | 1 / 10 | `params` підключення або `JANE_STORAGE_LIMITS__ADAPTERS__POOL_*` |
| `connect_timeout_ms` / `command_timeout_ms` | 10000 / 30000 | те саме (`…__CONNECT_TIMEOUT_MS`, `…__COMMAND_TIMEOUT_MS`) |

## Тести

`just up --project jane-wp07 postgres` → `just integration --project jane-wp07 services/storage` (набір сумісності
C-01…C-16 — `tests/test_compat.py`, кожен тест у власній схемі, яку видаляє після себе).
