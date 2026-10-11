# Модуль `jane_registry.postgres`

> Згенеровано `scripts/docs_reference.py` з [services/registry/src/jane_registry/postgres.py](../../../../../services/registry/src/jane_registry/postgres.py). Не редагуйте вручну.

PostgreSQL store of the registry (ADR-0002 §1): own database ``jane_registry``, tables in ``db_schema``.

Idempotency keys and upstream-port jobs live in jane-kit's shared stores (``jane_kit.stores.postgres``, R17) on the tables ``registry_idempotency`` (one ``response`` column) and ``registry_jobs``, migrated together with the registry tables, so several registry instances share them. Publications of one package are serialised by ``SELECT ... FOR UPDATE`` on the package row; ``(package_id, version)`` is the primary key of a version, so a concurrent duplicate publish fails with ``version_exists``.

## Класи

### Клас `PostgresStore`

| Властивість | Значення |
|---|---|
| Вид | клас |
| Модуль | `jane_registry.postgres` |
| Код | [postgres.py:525](../../../../../services/registry/src/jane_registry/postgres.py#L525) |

```python
class PostgresStore: ...
```

Async facade (``MetadataStore``) over the synchronous store: every call runs in a worker thread.

psycopg's asyncio driver needs a selector event loop, which is not the default on Windows; the synchronous driver behaves the same on Windows and Linux.

**Атрибути класу**

| Назва | Значення | Опис |
|---|---|---|
| `name` | `'postgres'` |  |

#### Конструктор `PostgresStore.__init__`

```python
def __init__(self, dsn: str, schema: str, limits: DbLimits) -> None: ...
```

Код: [postgres.py:534](../../../../../services/registry/src/jane_registry/postgres.py#L534).

#### Метод `PostgresStore.open`

```python
async def open(self) -> None: ...
```

Код: [postgres.py:537](../../../../../services/registry/src/jane_registry/postgres.py#L537).

#### Метод `PostgresStore.close`

```python
async def close(self) -> None: ...
```

Код: [postgres.py:540](../../../../../services/registry/src/jane_registry/postgres.py#L540).

#### Метод `PostgresStore.check`

```python
async def check(self) -> bool: ...
```

Код: [postgres.py:543](../../../../../services/registry/src/jane_registry/postgres.py#L543).

#### Метод `PostgresStore.create_package`

```python
async def create_package(self, pkg: PackageRecord) -> PackageRecord: ...
```

Код: [postgres.py:546](../../../../../services/registry/src/jane_registry/postgres.py#L546).

#### Метод `PostgresStore.get_package`

```python
async def get_package(self, package_id: str) -> PackageRecord | None: ...
```

Код: [postgres.py:549](../../../../../services/registry/src/jane_registry/postgres.py#L549).

#### Метод `PostgresStore.update_package`

```python
async def update_package(
    self,
    package_id: str,
    changes: dict[str, Any],
    expected_revision: int | None,
) -> PackageRecord: ...
```

Код: [postgres.py:552](../../../../../services/registry/src/jane_registry/postgres.py#L552).

#### Метод `PostgresStore.list_packages`

```python
async def list_packages(
    self,
    flt: PackageFilter,
    after: str | None,
    limit: int,
) -> list[PackageRecord]: ...
```

Код: [postgres.py:557](../../../../../services/registry/src/jane_registry/postgres.py#L557).

#### Метод `PostgresStore.count_forks`

```python
async def count_forks(self, package_id: str) -> int: ...
```

Код: [postgres.py:560](../../../../../services/registry/src/jane_registry/postgres.py#L560).

#### Метод `PostgresStore.delete_package_if_empty`

```python
async def delete_package_if_empty(self, package_id: str) -> None: ...
```

Код: [postgres.py:563](../../../../../services/registry/src/jane_registry/postgres.py#L563).

#### Метод `PostgresStore.insert_version`

```python
async def insert_version(self, version: VersionRecord, max_versions: int) -> VersionRecord: ...
```

Код: [postgres.py:566](../../../../../services/registry/src/jane_registry/postgres.py#L566).

#### Метод `PostgresStore.get_version`

```python
async def get_version(self, package_id: str, version: str) -> VersionRecord | None: ...
```

Код: [postgres.py:569](../../../../../services/registry/src/jane_registry/postgres.py#L569).

#### Метод `PostgresStore.list_versions`

```python
async def list_versions(
    self,
    package_id: str,
    status: str | None,
    before_seq: int | None,
    limit: int,
) -> list[VersionRecord]: ...
```

Код: [postgres.py:572](../../../../../services/registry/src/jane_registry/postgres.py#L572).

#### Метод `PostgresStore.version_numbers`

```python
async def version_numbers(self, package_id: str) -> list[tuple[str, str]]: ...
```

Код: [postgres.py:577](../../../../../services/registry/src/jane_registry/postgres.py#L577).

#### Метод `PostgresStore.count_versions`

```python
async def count_versions(self, package_id: str) -> int: ...
```

Код: [postgres.py:580](../../../../../services/registry/src/jane_registry/postgres.py#L580).

#### Метод `PostgresStore.set_status`

```python
async def set_status(
    self,
    package_id: str,
    version: str,
    expected: str,
    entry: dict[str, Any],
) -> VersionRecord: ...
```

Код: [postgres.py:583](../../../../../services/registry/src/jane_registry/postgres.py#L583).

#### Метод `PostgresStore.add_test_report`

```python
async def add_test_report(
    self,
    package_id: str,
    version: str,
    record: dict[str, Any],
    test_status: str,
) -> VersionRecord: ...
```

Код: [postgres.py:588](../../../../../services/registry/src/jane_registry/postgres.py#L588).

## Функції

### Функція `postgres_idempotency_store`

```python
def postgres_idempotency_store(
    store: PostgresStore,
    in_progress_lease_s: float,
    owner: str,
) -> PgIdempotencyStore: ...
```

jane-kit ``PgIdempotencyStore`` on ``registry_idempotency`` (``response`` jsonb column).

Код: [postgres.py:594](../../../../../services/registry/src/jane_registry/postgres.py#L594).

### Функція `postgres_job_store`

```python
def postgres_job_store(
    store: PostgresStore,
    limits: JobLimits,
    owner: str,
    lease_s: float,
) -> PgJobStore: ...
```

jane-kit ``PgJobStore`` on ``registry_jobs``; finished jobs older than ``job_retention_seconds`` are purged.

Код: [postgres.py:609](../../../../../services/registry/src/jane_registry/postgres.py#L609).
