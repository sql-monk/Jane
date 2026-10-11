# Registry

Репозиторій пакетів обробників і правил колекторів Jane: незмінні версії з дайджестом, тести, походження, форки, diff, явне перенесення змін батька й експорт архівів. API — [registry.v1](../../contracts/openapi/registry.v1.yaml).

Повна документація модуля — [docs/components/registry](../../docs/components/registry/README.md); формат пакетів — [docs/reference/packages](../../docs/reference/packages/README.md).

## Швидкий запуск

Без зовнішніх сервісів (метадані в пам'яті, архіви в каталозі), з кореня репозиторію:

```powershell
$env:JANE_REGISTRY_DB = "memory"
$env:JANE_REGISTRY_BLOB = "filesystem"
$env:JANE_REGISTRY_BLOB_ROOT = ".jane/registry-quickstart"
uv run --package jane-registry python -m jane_registry
```

Сервіс слухає `http://127.0.0.1:8105`. Щоб публікувати екстрактори, задайте ще джерело профілів runtime `JANE_REGISTRY_RUNTIME_PROFILES`. Покрокова публікація пакета, форк, diff і експорт — [quickstart](../../docs/components/registry/quickstart.md); запуск із PostgreSQL і MinIO — [operations](../../docs/components/registry/operations.md).

## Тести

```powershell
just test registry
just up --project jane-wp05 registry
just integration --project jane-wp05 services/registry
just down -v --project jane-wp05
```

Остання команда видаляє стек `jane-wp05` разом із його даними.
