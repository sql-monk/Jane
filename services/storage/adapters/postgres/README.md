# Адаптер Storage: postgresql

Адаптер `postgresql` (пакет `jane-storage-postgres`, пакет збереження `jane.storage-postgresql`, драйвер asyncpg): таблиці `<prefix>entities`, `<prefix>entity_history`, `<prefix>deliveries`, `<prefix>objects`; коміт сутності — одна транзакція. Секрети: `username`, `password`.

Параметри підключення, структура даних і обмеження — [адаптери Storage: postgresql](../../../../docs/components/storage/adapters.md#postgresql). Загальна документація модуля — [docs/components/storage](../../../../docs/components/storage/README.md).

## Тести

Набір сумісності C-01…C-16 потребує сервісу dev-стеку:

```powershell
just up --project <проєкт> postgres
just integration --project <проєкт> services/storage/adapters/postgres
```

Команда нижче зупиняє стек і видаляє його томи з усіма даними:

```powershell
just down -v --project <проєкт>
```
