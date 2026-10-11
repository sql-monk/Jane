# jane_registry.postgres

Декларації публічного API з поточного вихідного коду. Ручні пояснення та приклади розміщуються в довіднику модуля.

## Зміст

- [jane_registry.postgres.PostgresStore](#jane_registrypostgrespostgresstore)
- [jane_registry.postgres.PostgresStore.name](#jane_registrypostgrespostgresstorename)
- [jane_registry.postgres.PostgresStore.__init__](#jane_registrypostgrespostgresstore__init__)
- [jane_registry.postgres.PostgresStore.sync](#jane_registrypostgrespostgresstoresync)
- [jane_registry.postgres.PostgresStore.open](#jane_registrypostgrespostgresstoreopen)
- [jane_registry.postgres.PostgresStore.close](#jane_registrypostgrespostgresstoreclose)
- [jane_registry.postgres.PostgresStore.check](#jane_registrypostgrespostgresstorecheck)
- [jane_registry.postgres.PostgresStore.create_package](#jane_registrypostgrespostgresstorecreate_package)
- [jane_registry.postgres.PostgresStore.get_package](#jane_registrypostgrespostgresstoreget_package)
- [jane_registry.postgres.PostgresStore.update_package](#jane_registrypostgrespostgresstoreupdate_package)
- [jane_registry.postgres.PostgresStore.list_packages](#jane_registrypostgrespostgresstorelist_packages)
- [jane_registry.postgres.PostgresStore.count_forks](#jane_registrypostgrespostgresstorecount_forks)
- [jane_registry.postgres.PostgresStore.delete_package_if_empty](#jane_registrypostgrespostgresstoredelete_package_if_empty)
- [jane_registry.postgres.PostgresStore.insert_version](#jane_registrypostgrespostgresstoreinsert_version)
- [jane_registry.postgres.PostgresStore.get_version](#jane_registrypostgrespostgresstoreget_version)
- [jane_registry.postgres.PostgresStore.list_versions](#jane_registrypostgrespostgresstorelist_versions)
- [jane_registry.postgres.PostgresStore.version_numbers](#jane_registrypostgrespostgresstoreversion_numbers)
- [jane_registry.postgres.PostgresStore.count_versions](#jane_registrypostgrespostgresstorecount_versions)
- [jane_registry.postgres.PostgresStore.set_status](#jane_registrypostgrespostgresstoreset_status)
- [jane_registry.postgres.PostgresStore.add_test_report](#jane_registrypostgrespostgresstoreadd_test_report)
- [jane_registry.postgres.postgres_idempotency_store](#jane_registrypostgrespostgres_idempotency_store)
- [jane_registry.postgres.postgres_job_store](#jane_registrypostgrespostgres_job_store)

## jane_registry.postgres.PostgresStore

**Клас.** Код: [services/registry/src/jane_registry/postgres.py:525](../../../../../../services/registry/src/jane_registry/postgres.py#L525).

```python
class PostgresStore:
```

### Публічні члени

| Член | Тип | Успадковано |
|---|---|---|
| [name](jane_registry.postgres.md#jane_registrypostgrespostgresstorename) | Поле | ні |
| [__init__](jane_registry.postgres.md#jane_registrypostgrespostgresstore__init__) | Конструктор | ні |
| [sync](jane_registry.postgres.md#jane_registrypostgrespostgresstoresync) | Поле екземпляра | ні |
| [open](jane_registry.postgres.md#jane_registrypostgrespostgresstoreopen) | Метод | ні |
| [close](jane_registry.postgres.md#jane_registrypostgrespostgresstoreclose) | Метод | ні |
| [check](jane_registry.postgres.md#jane_registrypostgrespostgresstorecheck) | Метод | ні |
| [create_package](jane_registry.postgres.md#jane_registrypostgrespostgresstorecreate_package) | Метод | ні |
| [get_package](jane_registry.postgres.md#jane_registrypostgrespostgresstoreget_package) | Метод | ні |
| [update_package](jane_registry.postgres.md#jane_registrypostgrespostgresstoreupdate_package) | Метод | ні |
| [list_packages](jane_registry.postgres.md#jane_registrypostgrespostgresstorelist_packages) | Метод | ні |
| [count_forks](jane_registry.postgres.md#jane_registrypostgrespostgresstorecount_forks) | Метод | ні |
| [delete_package_if_empty](jane_registry.postgres.md#jane_registrypostgrespostgresstoredelete_package_if_empty) | Метод | ні |
| [insert_version](jane_registry.postgres.md#jane_registrypostgrespostgresstoreinsert_version) | Метод | ні |
| [get_version](jane_registry.postgres.md#jane_registrypostgrespostgresstoreget_version) | Метод | ні |
| [list_versions](jane_registry.postgres.md#jane_registrypostgrespostgresstorelist_versions) | Метод | ні |
| [version_numbers](jane_registry.postgres.md#jane_registrypostgrespostgresstoreversion_numbers) | Метод | ні |
| [count_versions](jane_registry.postgres.md#jane_registrypostgrespostgresstorecount_versions) | Метод | ні |
| [set_status](jane_registry.postgres.md#jane_registrypostgrespostgresstoreset_status) | Метод | ні |
| [add_test_report](jane_registry.postgres.md#jane_registrypostgrespostgresstoreadd_test_report) | Метод | ні |

### Опис із вихідного коду

```text
Async facade (``MetadataStore``) over the synchronous store: every call runs in a worker thread.

psycopg's asyncio driver needs a selector event loop, which is not the default on Windows; the
synchronous driver behaves the same on Windows and Linux.
```

## jane_registry.postgres.PostgresStore.name

**Поле.** Код: [services/registry/src/jane_registry/postgres.py:532](../../../../../../services/registry/src/jane_registry/postgres.py#L532).

```python
name = 'postgres'
```

Доступ: читання — так; запис — так.

## jane_registry.postgres.PostgresStore.__init__

**Конструктор.** Код: [services/registry/src/jane_registry/postgres.py:534](../../../../../../services/registry/src/jane_registry/postgres.py#L534).

```python
def __init__(self, dsn: str, schema: str, limits: DbLimits) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `dsn` | `str` | `—` | positional-or-keyword |
| `schema` | `str` | `—` | positional-or-keyword |
| `limits` | `DbLimits` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.postgres.PostgresStore.sync

**Поле екземпляра.** Код: [services/registry/src/jane_registry/postgres.py:535](../../../../../../services/registry/src/jane_registry/postgres.py#L535).

```python
self.sync = _SyncStore(dsn, schema, limits)
```

## jane_registry.postgres.PostgresStore.open

**Метод.** Код: [services/registry/src/jane_registry/postgres.py:537](../../../../../../services/registry/src/jane_registry/postgres.py#L537).

```python
async def open(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.postgres.PostgresStore.close

**Метод.** Код: [services/registry/src/jane_registry/postgres.py:540](../../../../../../services/registry/src/jane_registry/postgres.py#L540).

```python
async def close(self) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.postgres.PostgresStore.check

**Метод.** Код: [services/registry/src/jane_registry/postgres.py:543](../../../../../../services/registry/src/jane_registry/postgres.py#L543).

```python
async def check(self) -> bool:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |

Результат: `bool`.

## jane_registry.postgres.PostgresStore.create_package

**Метод.** Код: [services/registry/src/jane_registry/postgres.py:546](../../../../../../services/registry/src/jane_registry/postgres.py#L546).

```python
async def create_package(self, pkg: PackageRecord) -> PackageRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `pkg` | `PackageRecord` | `—` | positional-or-keyword |

Результат: `PackageRecord`.

## jane_registry.postgres.PostgresStore.get_package

**Метод.** Код: [services/registry/src/jane_registry/postgres.py:549](../../../../../../services/registry/src/jane_registry/postgres.py#L549).

```python
async def get_package(self, package_id: str) -> PackageRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `PackageRecord | None`.

## jane_registry.postgres.PostgresStore.update_package

**Метод.** Код: [services/registry/src/jane_registry/postgres.py:552](../../../../../../services/registry/src/jane_registry/postgres.py#L552).

```python
async def update_package(self, package_id: str, changes: dict[str, Any], expected_revision: int | None) -> PackageRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `changes` | `dict[str, Any]` | `—` | positional-or-keyword |
| `expected_revision` | `int \| None` | `—` | positional-or-keyword |

Результат: `PackageRecord`.

## jane_registry.postgres.PostgresStore.list_packages

**Метод.** Код: [services/registry/src/jane_registry/postgres.py:557](../../../../../../services/registry/src/jane_registry/postgres.py#L557).

```python
async def list_packages(self, flt: PackageFilter, after: str | None, limit: int) -> list[PackageRecord]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `flt` | `PackageFilter` | `—` | positional-or-keyword |
| `after` | `str \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `list[PackageRecord]`.

## jane_registry.postgres.PostgresStore.count_forks

**Метод.** Код: [services/registry/src/jane_registry/postgres.py:560](../../../../../../services/registry/src/jane_registry/postgres.py#L560).

```python
async def count_forks(self, package_id: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `int`.

## jane_registry.postgres.PostgresStore.delete_package_if_empty

**Метод.** Код: [services/registry/src/jane_registry/postgres.py:563](../../../../../../services/registry/src/jane_registry/postgres.py#L563).

```python
async def delete_package_if_empty(self, package_id: str) -> None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `None`.

## jane_registry.postgres.PostgresStore.insert_version

**Метод.** Код: [services/registry/src/jane_registry/postgres.py:566](../../../../../../services/registry/src/jane_registry/postgres.py#L566).

```python
async def insert_version(self, version: VersionRecord, max_versions: int) -> VersionRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `version` | `VersionRecord` | `—` | positional-or-keyword |
| `max_versions` | `int` | `—` | positional-or-keyword |

Результат: `VersionRecord`.

## jane_registry.postgres.PostgresStore.get_version

**Метод.** Код: [services/registry/src/jane_registry/postgres.py:569](../../../../../../services/registry/src/jane_registry/postgres.py#L569).

```python
async def get_version(self, package_id: str, version: str) -> VersionRecord | None:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |

Результат: `VersionRecord | None`.

## jane_registry.postgres.PostgresStore.list_versions

**Метод.** Код: [services/registry/src/jane_registry/postgres.py:572](../../../../../../services/registry/src/jane_registry/postgres.py#L572).

```python
async def list_versions(self, package_id: str, status: str | None, before_seq: int | None, limit: int) -> list[VersionRecord]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `status` | `str \| None` | `—` | positional-or-keyword |
| `before_seq` | `int \| None` | `—` | positional-or-keyword |
| `limit` | `int` | `—` | positional-or-keyword |

Результат: `list[VersionRecord]`.

## jane_registry.postgres.PostgresStore.version_numbers

**Метод.** Код: [services/registry/src/jane_registry/postgres.py:577](../../../../../../services/registry/src/jane_registry/postgres.py#L577).

```python
async def version_numbers(self, package_id: str) -> list[tuple[str, str]]:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `list[tuple[str, str]]`.

## jane_registry.postgres.PostgresStore.count_versions

**Метод.** Код: [services/registry/src/jane_registry/postgres.py:580](../../../../../../services/registry/src/jane_registry/postgres.py#L580).

```python
async def count_versions(self, package_id: str) -> int:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |

Результат: `int`.

## jane_registry.postgres.PostgresStore.set_status

**Метод.** Код: [services/registry/src/jane_registry/postgres.py:583](../../../../../../services/registry/src/jane_registry/postgres.py#L583).

```python
async def set_status(self, package_id: str, version: str, expected: str, entry: dict[str, Any]) -> VersionRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |
| `expected` | `str` | `—` | positional-or-keyword |
| `entry` | `dict[str, Any]` | `—` | positional-or-keyword |

Результат: `VersionRecord`.

## jane_registry.postgres.PostgresStore.add_test_report

**Метод.** Код: [services/registry/src/jane_registry/postgres.py:588](../../../../../../services/registry/src/jane_registry/postgres.py#L588).

```python
async def add_test_report(self, package_id: str, version: str, record: dict[str, Any], test_status: str) -> VersionRecord:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `self` | `не вказано` | `—` | positional-or-keyword |
| `package_id` | `str` | `—` | positional-or-keyword |
| `version` | `str` | `—` | positional-or-keyword |
| `record` | `dict[str, Any]` | `—` | positional-or-keyword |
| `test_status` | `str` | `—` | positional-or-keyword |

Результат: `VersionRecord`.

## jane_registry.postgres.postgres_idempotency_store

**Функція.** Код: [services/registry/src/jane_registry/postgres.py:594](../../../../../../services/registry/src/jane_registry/postgres.py#L594).

```python
def postgres_idempotency_store(store: PostgresStore, in_progress_lease_s: float, owner: str) -> PgIdempotencyStore:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `store` | `PostgresStore` | `—` | positional-or-keyword |
| `in_progress_lease_s` | `float` | `—` | positional-or-keyword |
| `owner` | `str` | `—` | positional-or-keyword |

Результат: `PgIdempotencyStore`.

### Опис із вихідного коду

```text
jane-kit ``PgIdempotencyStore`` on ``registry_idempotency`` (``response`` jsonb column).
```

## jane_registry.postgres.postgres_job_store

**Функція.** Код: [services/registry/src/jane_registry/postgres.py:609](../../../../../../services/registry/src/jane_registry/postgres.py#L609).

```python
def postgres_job_store(store: PostgresStore, limits: JobLimits, owner: str, lease_s: float) -> PgJobStore:
```

### Параметри

| Ім’я | Тип | Типове значення | Спосіб передавання |
|---|---|---|---|
| `store` | `PostgresStore` | `—` | positional-or-keyword |
| `limits` | `JobLimits` | `—` | positional-or-keyword |
| `owner` | `str` | `—` | positional-or-keyword |
| `lease_s` | `float` | `—` | positional-or-keyword |

Результат: `PgJobStore`.

### Опис із вихідного коду

```text
jane-kit ``PgJobStore`` on ``registry_jobs``; finished jobs older than ``job_retention_seconds`` are purged.
```
